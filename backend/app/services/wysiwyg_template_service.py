"""
WYSIWYG Template Editor Service with versioning and preview
WYSIWYG sablon szerkesztő szolgáltatás verziókezeléssel és előnézettel
"""
import os
import uuid
import json
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from io import BytesIO
import weasyprint
from PIL import Image, ImageDraw, ImageFont
import base64
from jinja2 import Template, Environment, BaseLoader, meta

from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from ..core.database import get_db
from ..models.template_versioning import (
    DocumentTemplateVersion, DocumentTemplateChangeLog, DocumentTemplateField, 
    DocumentPreviewSession, TemplateChangeType, TemplateStatus
)
from ..models.documents import DocumentTemplate, DocumentType
from ..models.auth import User


class WYSIWYGTemplateService:
    """
    WYSIWYG template editor service with full versioning support
    WYSIWYG sablon szerkesztő szolgáltatás teljes verziókezelés támogatással
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.preview_base_url = "https://garagereg.local/api/documents/preview"
        self.storage_path = "/var/garagereg/template_previews"
    
    def create_template_version(
        self,
        template_id: int,
        user_id: int,
        html_content: str,
        css_styles: Optional[str] = None,
        editor_content: Optional[Dict[str, Any]] = None,
        version_type: str = "minor",
        version_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DocumentTemplateVersion:
        """
        Create new template version with WYSIWYG content
        Új sablon verzió létrehozása WYSIWYG tartalommal
        """
        template = self.db.query(DocumentTemplate).filter(DocumentTemplate.id == template_id).first()
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        # Get current version for incrementing
        current_version = self.db.query(DocumentTemplateVersion).filter(
            DocumentTemplateVersion.template_id == template_id,
            DocumentTemplateVersion.is_current == True
        ).first()
        
        # Generate new version number
        if current_version:
            new_version_number = self._increment_version(current_version.version_number, version_type)
            # Set current version as not current
            current_version.is_current = False
        else:
            new_version_number = "1.0"
        
        # Extract template fields from HTML content
        template_fields = self._extract_template_fields(html_content)
        
        # Create new version
        new_version = DocumentTemplateVersion(
            template_id=template_id,
            organization_id=template.organization_id,
            version_number=new_version_number,
            version_name=version_name,
            html_template=html_content,
            css_styles=css_styles,
            editor_content=editor_content,
            title=metadata.get('title', template.name) if metadata else template.name,
            description=metadata.get('description') if metadata else None,
            page_size=metadata.get('page_size', 'A4') if metadata else 'A4',
            orientation=metadata.get('orientation', 'portrait') if metadata else 'portrait',
            margins=metadata.get('margins') if metadata else None,
            include_qr_code=metadata.get('include_qr_code', True) if metadata else True,
            qr_code_position=metadata.get('qr_code_position', 'top_right') if metadata else 'top_right',
            qr_code_size=metadata.get('qr_code_size', 100) if metadata else 100,
            include_logo=metadata.get('include_logo', True) if metadata else True,
            logo_position=metadata.get('logo_position', 'top_left') if metadata else 'top_left',
            required_fields=json.dumps(template_fields['required']) if template_fields else None,
            optional_fields=json.dumps(template_fields['optional']) if template_fields else None,
            sample_data=metadata.get('sample_data') if metadata else None,
            status=TemplateStatus.DRAFT,
            is_current=True,
            created_by_id=user_id
        )
        
        self.db.add(new_version)
        self.db.flush()  # Get the ID
        
        # Update template current version reference
        template.current_version_id = new_version.id
        template.updated_at = datetime.now(timezone.utc)
        
        # Log the change
        self._log_template_change(
            template_id=template_id,
            version_id=new_version.id,
            change_type=TemplateChangeType.CREATED,
            change_summary=f"Created new version {new_version_number}",
            user_id=user_id,
            new_data={
                'version_number': new_version_number,
                'html_length': len(html_content),
                'css_length': len(css_styles) if css_styles else 0,
                'field_count': len(template_fields['required']) + len(template_fields['optional']) if template_fields else 0
            }
        )
        
        self.db.commit()
        
        # Generate preview asynchronously
        self._generate_version_preview(new_version.id)
        
        return new_version
    
    def update_template_version(
        self,
        version_id: int,
        user_id: int,
        html_content: Optional[str] = None,
        css_styles: Optional[str] = None,
        editor_content: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DocumentTemplateVersion:
        """
        Update existing template version
        Meglévő sablon verzió frissítése
        """
        version = self.db.query(DocumentTemplateVersion).filter(
            DocumentTemplateVersion.id == version_id
        ).first()
        
        if not version:
            raise ValueError(f"Template version not found: {version_id}")
        
        if version.status == TemplateStatus.PUBLISHED:
            raise ValueError("Cannot modify published version. Create new version instead.")
        
        # Store old data for change tracking
        old_data = {
            'html_template': version.html_template,
            'css_styles': version.css_styles,
            'editor_content': version.editor_content,
            'title': version.title,
            'description': version.description
        }
        
        # Update fields
        changes = []
        if html_content is not None and html_content != version.html_template:
            version.html_template = html_content
            changes.append('HTML template')
            
            # Re-extract fields
            template_fields = self._extract_template_fields(html_content)
            version.required_fields = json.dumps(template_fields['required'])
            version.optional_fields = json.dumps(template_fields['optional'])
        
        if css_styles is not None and css_styles != version.css_styles:
            version.css_styles = css_styles
            changes.append('CSS styles')
        
        if editor_content is not None:
            version.editor_content = editor_content
            changes.append('Editor content')
        
        if metadata:
            for key, value in metadata.items():
                if hasattr(version, key) and getattr(version, key) != value:
                    setattr(version, key, value)
                    changes.append(key)
        
        version.updated_at = datetime.now(timezone.utc)
        
        # Log changes
        if changes:
            self._log_template_change(
                template_id=version.template_id,
                version_id=version.id,
                change_type=TemplateChangeType.UPDATED,
                change_summary=f"Updated {', '.join(changes)}",
                user_id=user_id,
                old_data=old_data,
                new_data={
                    'html_template': version.html_template,
                    'css_styles': version.css_styles,
                    'title': version.title,
                    'changes': changes
                }
            )
        
        self.db.commit()
        
        # Regenerate preview
        self._generate_version_preview(version.id)
        
        return version
    
    def publish_template_version(
        self,
        version_id: int,
        user_id: int,
        approval_notes: Optional[str] = None
    ) -> DocumentTemplateVersion:
        """
        Publish template version (make it active)
        Sablon verzió publikálása (aktívvá tétel)
        """
        version = self.db.query(DocumentTemplateVersion).filter(
            DocumentTemplateVersion.id == version_id
        ).first()
        
        if not version:
            raise ValueError(f"Template version not found: {version_id}")
        
        # Unpublish other versions of same template
        self.db.query(DocumentTemplateVersion).filter(
            DocumentTemplateVersion.template_id == version.template_id,
            DocumentTemplateVersion.status == TemplateStatus.PUBLISHED
        ).update({'status': TemplateStatus.ARCHIVED})
        
        # Publish this version
        version.status = TemplateStatus.PUBLISHED
        version.published_at = datetime.now(timezone.utc)
        version.published_by_id = user_id
        version.is_current = True
        
        # Update template reference
        template = version.template
        template.current_version_id = version.id
        template.updated_at = datetime.now(timezone.utc)
        
        # Log the change
        self._log_template_change(
            template_id=version.template_id,
            version_id=version.id,
            change_type=TemplateChangeType.PUBLISHED,
            change_summary=f"Published version {version.version_number}",
            user_id=user_id,
            new_data={
                'published_at': version.published_at.isoformat(),
                'approval_notes': approval_notes
            }
        )
        
        self.db.commit()
        
        return version
    
    def create_preview_session(
        self,
        version_id: int,
        user_id: int,
        sample_data: Optional[Dict[str, Any]] = None,
        preview_options: Optional[Dict[str, Any]] = None
    ) -> DocumentPreviewSession:
        """
        Create preview session for template version
        Előnézeti munkamenet létrehozása sablon verzióhoz
        """
        version = self.db.query(DocumentTemplateVersion).filter(
            DocumentTemplateVersion.id == version_id
        ).first()
        
        if not version:
            raise ValueError(f"Template version not found: {version_id}")
        
        # Generate session token
        session_token = str(uuid.uuid4())
        
        # Use sample data or generate default data
        if not sample_data:
            sample_data = self._generate_sample_data(version)
        
        # Create preview session
        session = DocumentPreviewSession(
            session_token=session_token,
            template_id=version.template_id,
            version_id=version.id,
            organization_id=version.organization_id,
            created_by_id=user_id,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),  # 24 hour expiry
            preview_data=sample_data,
            preview_options=preview_options or {},
            generation_status='pending'
        )
        
        self.db.add(session)
        self.db.commit()
        
        # Generate preview asynchronously
        self._generate_session_preview(session.id)
        
        return session
    
    def get_template_versions(
        self,
        template_id: int,
        include_drafts: bool = True,
        limit: int = 50
    ) -> List[DocumentTemplateVersion]:
        """
        Get template version history
        Sablon verzió történet lekérése
        """
        query = self.db.query(DocumentTemplateVersion).filter(
            DocumentTemplateVersion.template_id == template_id
        )
        
        if not include_drafts:
            query = query.filter(
                DocumentTemplateVersion.status != TemplateStatus.DRAFT
            )
        
        return query.order_by(desc(DocumentTemplateVersion.created_at)).limit(limit).all()
    
    def get_template_changelog(
        self,
        template_id: int,
        limit: int = 100
    ) -> List[DocumentTemplateChangeLog]:
        """
        Get template change history
        Sablon változás történet lekérése
        """
        return self.db.query(DocumentTemplateChangeLog).filter(
            DocumentTemplateChangeLog.template_id == template_id
        ).order_by(desc(DocumentTemplateChangeLog.change_timestamp)).limit(limit).all()
    
    def compare_template_versions(
        self,
        version_id_1: int,
        version_id_2: int
    ) -> Dict[str, Any]:
        """
        Compare two template versions
        Két sablon verzió összehasonlítása
        """
        version1 = self.db.query(DocumentTemplateVersion).filter(
            DocumentTemplateVersion.id == version_id_1
        ).first()
        
        version2 = self.db.query(DocumentTemplateVersion).filter(
            DocumentTemplateVersion.id == version_id_2
        ).first()
        
        if not version1 or not version2:
            raise ValueError("One or both versions not found")
        
        # Generate HTML diff
        html_diff = self._generate_html_diff(version1.html_template, version2.html_template)
        
        # Generate CSS diff
        css_diff = self._generate_css_diff(
            version1.css_styles or "", 
            version2.css_styles or ""
        )
        
        # Compare metadata
        metadata_changes = {}
        fields = ['title', 'description', 'page_size', 'orientation', 'include_qr_code', 
                 'qr_code_position', 'include_logo', 'logo_position']
        
        for field in fields:
            val1 = getattr(version1, field)
            val2 = getattr(version2, field)
            if val1 != val2:
                metadata_changes[field] = {'from': val1, 'to': val2}
        
        return {
            'version_1': {
                'id': version1.id,
                'version_number': version1.version_number,
                'created_at': version1.created_at.isoformat(),
                'status': version1.status.value
            },
            'version_2': {
                'id': version2.id,
                'version_number': version2.version_number,
                'created_at': version2.created_at.isoformat(),
                'status': version2.status.value
            },
            'html_diff': html_diff,
            'css_diff': css_diff,
            'metadata_changes': metadata_changes
        }
    
    def _extract_template_fields(self, html_content: str) -> Dict[str, List[str]]:
        """
        Extract Jinja2 variables from HTML template
        Jinja2 változók kinyerése HTML sablonból
        """
        try:
            env = Environment()
            ast = env.parse(html_content)
            variables = meta.find_undeclared_variables(ast)
            
            # Categorize fields (this is a simple heuristic)
            required_fields = []
            optional_fields = []
            
            common_required = ['document_number', 'date', 'title', 'organization']
            
            for var in variables:
                if any(req in var.lower() for req in common_required):
                    required_fields.append(var)
                else:
                    optional_fields.append(var)
            
            return {
                'required': sorted(required_fields),
                'optional': sorted(optional_fields)
            }
            
        except Exception as e:
            # Fallback to regex extraction
            import re
            variables = re.findall(r'\{\{\s*([^}]+)\s*\}\}', html_content)
            return {
                'required': [],
                'optional': list(set(variables))
            }
    
    def _increment_version(self, current_version: str, version_type: str) -> str:
        """Generate next version number"""
        try:
            parts = current_version.split('.')
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
            
            if version_type == "major":
                return f"{major + 1}.0"
            else:  # minor
                return f"{major}.{minor + 1}"
        except:
            return "1.0"
    
    def _log_template_change(
        self,
        template_id: int,
        version_id: Optional[int],
        change_type: TemplateChangeType,
        change_summary: str,
        user_id: int,
        old_data: Optional[Dict[str, Any]] = None,
        new_data: Optional[Dict[str, Any]] = None
    ):
        """Log template change"""
        change_log = DocumentTemplateChangeLog(
            template_id=template_id,
            version_id=version_id,
            organization_id=1,  # TODO: Get from context
            change_type=change_type,
            change_summary=change_summary,
            change_details={
                'user_agent': 'GarageReg-Admin/1.0',  # TODO: Get from request
                'timestamp': datetime.now(timezone.utc).isoformat()
            },
            changed_by_id=user_id,
            old_data=old_data,
            new_data=new_data
        )
        
        self.db.add(change_log)
    
    def _generate_sample_data(self, version: DocumentTemplateVersion) -> Dict[str, Any]:
        """Generate sample data for preview"""
        sample_data = {
            'document_number': 'DOC-20251002-001',
            'generation': {
                'date': datetime.now(timezone.utc),
                'document_number': 'DOC-20251002-001',
                'generated_by': 'Admin User'
            },
            'organization': {
                'name': 'GarageReg Demo Kft.',
                'address': '1234 Budapest, Demo utca 1.',
                'tax_number': '12345678-1-23',
                'registration_number': 'Cg.01-09-123456'
            },
            'gate': {
                'id': 'GATE-001',
                'name': 'Főbejárat Kapu',
                'location': 'Budapest, Fő utca 1.',
                'type': 'Automatikus tolókapu'
            },
            'inspector': {
                'name': 'Teszt Ellenőr',
                'display_name': 'Teszt Ellenőr',
                'license_number': 'ELL-123456'
            },
            'inspection': {
                'id': 1,
                'type': 'Éves biztonsági ellenőrzés',
                'date': datetime.now(timezone.utc).date(),
                'result': 'Megfelelő'
            }
        }
        
        # Add sample data from version if available
        if version.sample_data:
            sample_data.update(version.sample_data)
        
        return sample_data
    
    def _generate_version_preview(self, version_id: int):
        """Generate preview files for template version (async task)"""
        try:
            version = self.db.query(DocumentTemplateVersion).filter(
                DocumentTemplateVersion.id == version_id
            ).first()
            
            if not version:
                return
            
            # Generate sample data
            sample_data = self._generate_sample_data(version)
            
            # Render HTML
            from jinja2 import Template
            template = Template(version.html_template)
            rendered_html = template.render(**sample_data)
            
            # Generate PDF
            css_content = version.css_styles or ""
            html_doc = weasyprint.HTML(string=rendered_html)
            pdf_bytes = html_doc.write_pdf()
            
            # Save files
            preview_dir = os.path.join(self.storage_path, str(version.template_id), str(version.id))
            os.makedirs(preview_dir, exist_ok=True)
            
            # Save HTML preview
            html_path = os.path.join(preview_dir, 'preview.html')
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(rendered_html)
            
            # Save PDF preview
            pdf_path = os.path.join(preview_dir, 'preview.pdf')
            with open(pdf_path, 'wb') as f:
                f.write(pdf_bytes)
            
            # Generate preview image (first page of PDF)
            image_path = os.path.join(preview_dir, 'preview.png')
            self._pdf_to_image(pdf_bytes, image_path)
            
            # Update version with paths
            version.preview_pdf_path = pdf_path
            version.preview_image_url = f"{self.preview_base_url}/{version.template_id}/{version.id}/preview.png"
            
            self.db.commit()
            
        except Exception as e:
            print(f"Error generating preview for version {version_id}: {e}")
    
    def _generate_session_preview(self, session_id: int):
        """Generate preview files for preview session"""
        try:
            session = self.db.query(DocumentPreviewSession).filter(
                DocumentPreviewSession.id == session_id
            ).first()
            
            if not session:
                return
            
            session.generation_status = 'generating'
            self.db.commit()
            
            version = session.version
            if not version:
                session.generation_status = 'failed'
                session.error_message = 'Template version not found'
                self.db.commit()
                return
            
            # Use session preview data
            preview_data = session.preview_data or self._generate_sample_data(version)
            
            # Render HTML
            from jinja2 import Template
            template = Template(version.html_template)
            rendered_html = template.render(**preview_data)
            
            # Generate PDF
            html_doc = weasyprint.HTML(string=rendered_html)
            pdf_bytes = html_doc.write_pdf()
            
            # Save files
            preview_dir = os.path.join(self.storage_path, 'sessions', session.session_token)
            os.makedirs(preview_dir, exist_ok=True)
            
            html_path = os.path.join(preview_dir, 'preview.html')
            pdf_path = os.path.join(preview_dir, 'preview.pdf')
            image_path = os.path.join(preview_dir, 'preview.png')
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(rendered_html)
            
            with open(pdf_path, 'wb') as f:
                f.write(pdf_bytes)
            
            self._pdf_to_image(pdf_bytes, image_path)
            
            # Update session
            session.html_preview_path = html_path
            session.pdf_preview_path = pdf_path
            session.preview_image_path = image_path
            session.generation_status = 'ready'
            
            self.db.commit()
            
        except Exception as e:
            session.generation_status = 'failed'
            session.error_message = str(e)
            self.db.commit()
    
    def _pdf_to_image(self, pdf_bytes: bytes, output_path: str):
        """Convert PDF first page to PNG image"""
        try:
            from pdf2image import convert_from_bytes
            
            pages = convert_from_bytes(pdf_bytes, first_page=1, last_page=1, dpi=150)
            if pages:
                pages[0].save(output_path, 'PNG')
        except ImportError:
            # Fallback: create placeholder image
            img = Image.new('RGB', (595, 842), color='white')  # A4 size at 72 DPI
            draw = ImageDraw.Draw(img)
            draw.text((50, 50), 'Preview Image\n(PDF2Image not available)', fill='black')
            img.save(output_path, 'PNG')
        except Exception as e:
            # Create error placeholder
            img = Image.new('RGB', (595, 842), color='white')
            draw = ImageDraw.Draw(img)
            draw.text((50, 50), f'Preview Error:\n{str(e)}', fill='red')
            img.save(output_path, 'PNG')
    
    def _generate_html_diff(self, html1: str, html2: str) -> List[Dict[str, Any]]:
        """Generate HTML difference"""
        try:
            import difflib
            
            lines1 = html1.splitlines()
            lines2 = html2.splitlines()
            
            diff = list(difflib.unified_diff(lines1, lines2, lineterm=''))
            
            return [{'type': 'unified', 'content': diff}]
        except:
            return [{'type': 'error', 'content': 'Diff generation failed'}]
    
    def _generate_css_diff(self, css1: str, css2: str) -> List[Dict[str, Any]]:
        """Generate CSS difference"""
        try:
            import difflib
            
            lines1 = css1.splitlines()
            lines2 = css2.splitlines()
            
            diff = list(difflib.unified_diff(lines1, lines2, lineterm=''))
            
            return [{'type': 'unified', 'content': diff}]
        except:
            return [{'type': 'error', 'content': 'CSS diff generation failed'}]