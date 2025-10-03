"""
Document generation service for creating operational logs, maintenance protocols, and work sheets.

Dokumentum generálási szolgáltatás üzemeltetési naplók, karbantartási jegyzőkönyvek és munkalapok létrehozásához.
"""

import os
import uuid
import qrcode
import hashlib
from io import BytesIO, StringIO
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
from jinja2 import Template, Environment, BaseLoader
import weasyprint
from PIL import Image, ImageDraw, ImageFont
import base64

from sqlalchemy.orm import Session
from app.models.documents import (
    Document, DocumentTemplate, DocumentSignature, 
    DocumentType, DocumentStatus, SignatureType
)
from app.models.auth import User
from app.models.organization import Gate
from app.models.inspections import Inspection
from app.models.tickets import WorkOrder, Ticket
from app.core.config import settings


class DocumentGenerationService:
    """
    Service for generating PDF documents from HTML templates.
    
    Szolgáltatás PDF dokumentumok generálásához HTML sablonokból.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.base_url = getattr(settings, 'BASE_URL', 'https://garagereg.app')
        
    def generate_operational_log(
        self,
        gate_id: int,
        user_id: int,
        date_from: datetime,
        date_to: datetime,
        template_name: Optional[str] = None,
        custom_data: Optional[Dict[str, Any]] = None
    ) -> Document:
        """
        Generate operational log (üzemeltetési napló) for a gate.
        
        Üzemeltetési napló generálása egy kapuhoz.
        """
        
        # Get gate and related data
        gate = self.db.query(Gate).filter(Gate.id == gate_id).first()
        if not gate:
            raise ValueError(f"Gate not found: {gate_id}")
        
        # Get template
        template = self._get_template(DocumentType.OPERATIONAL_LOG, template_name)
        
        # Prepare template data
        template_data = {
            'gate': {
                'id': gate.id,
                'name': gate.name,
                'display_name': gate.display_name,
                'gate_code': gate.gate_code,
                'gate_type': gate.gate_type,
                'manufacturer': gate.manufacturer,
                'model': gate.model,
                'serial_number': gate.serial_number,
                'installation_date': gate.installation_date,
                'status': gate.status
            },
            'period': {
                'from': date_from,
                'to': date_to,
                'days': (date_to - date_from).days + 1
            },
            'generation': {
                'date': datetime.utcnow(),
                'user_id': user_id,
                'document_number': self._generate_document_number('OL')
            },
            'operations': self._get_gate_operations(gate_id, date_from, date_to),
            'incidents': self._get_gate_incidents(gate_id, date_from, date_to),
            'maintenance_summary': self._get_maintenance_summary(gate_id, date_from, date_to),
            'usage_statistics': self._get_usage_statistics(gate_id, date_from, date_to)
        }
        
        # Add custom data
        if custom_data:
            template_data.update(custom_data)
        
        # Generate document
        return self._generate_document(
            document_type=DocumentType.OPERATIONAL_LOG,
            template=template,
            template_data=template_data,
            user_id=user_id,
            entity_type='gate',
            entity_id=gate_id,
            title=f"Üzemeltetési napló - {gate.display_name or gate.name}"
        )
    
    def generate_maintenance_protocol(
        self,
        work_order_id: int,
        user_id: int,
        template_name: Optional[str] = None,
        custom_data: Optional[Dict[str, Any]] = None
    ) -> Document:
        """
        Generate maintenance protocol (karbantartási jegyzőkönyv) for a work order.
        
        Karbantartási jegyzőkönyv generálása egy munkarendeléshez.
        """
        
        # Get work order and related data
        work_order = self.db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not work_order:
            raise ValueError(f"Work order not found: {work_order_id}")
        
        # Get template
        template = self._get_template(DocumentType.MAINTENANCE_PROTOCOL, template_name)
        
        # Prepare template data
        template_data = {
            'work_order': {
                'id': work_order.id,
                'work_order_number': work_order.work_order_number,
                'title': work_order.title,
                'description': work_order.description,
                'work_type': work_order.work_type,
                'work_category': work_order.work_category,
                'status': work_order.status,
                'priority': work_order.priority,
                'scheduled_start': work_order.scheduled_start,
                'scheduled_end': work_order.scheduled_end,
                'actual_start': work_order.actual_start,
                'actual_end': work_order.actual_end,
                'estimated_duration_hours': work_order.estimated_duration_hours,
                'actual_duration_hours': work_order.actual_duration_hours,
                'progress_percentage': work_order.progress_percentage,
                'work_performed': work_order.work_performed,
                'issues_encountered': work_order.issues_encountered,
                'quality_check_passed': work_order.quality_check_passed,
                'quality_notes': work_order.quality_notes
            },
            'gate': self._get_gate_data(work_order.gate_id) if work_order.gate_id else None,
            'technician': self._get_user_data(work_order.assigned_technician_id) if work_order.assigned_technician_id else None,
            'parts_used': self._get_parts_used(work_order_id),
            'time_logs': self._get_time_logs(work_order_id),
            'costs': self._get_work_order_costs(work_order_id),
            'generation': {
                'date': datetime.utcnow(),
                'user_id': user_id,
                'document_number': self._generate_document_number('MP')
            },
            'compliance': {
                'standards': ['EN 13241-1', 'EN 12453', 'EN 12604'],
                'safety_requirements': work_order.safety_requirements
            }
        }
        
        # Add custom data
        if custom_data:
            template_data.update(custom_data)
        
        # Generate document
        return self._generate_document(
            document_type=DocumentType.MAINTENANCE_PROTOCOL,
            template=template,
            template_data=template_data,
            user_id=user_id,
            entity_type='work_order',
            entity_id=work_order_id,
            title=f"Karbantartási jegyzőkönyv - {work_order.work_order_number}"
        )
    
    def generate_work_sheet(
        self,
        inspection_id: int,
        user_id: int,
        template_name: Optional[str] = None,
        custom_data: Optional[Dict[str, Any]] = None
    ) -> Document:
        """
        Generate work sheet (munkalap) for an inspection.
        
        Munkalap generálása egy ellenőrzéshez.
        """
        
        # Get inspection and related data
        inspection = self.db.query(Inspection).filter(Inspection.id == inspection_id).first()
        if not inspection:
            raise ValueError(f"Inspection not found: {inspection_id}")
        
        # Get template
        template = self._get_template(DocumentType.WORK_SHEET, template_name)
        
        # Prepare template data
        template_data = {
            'inspection': {
                'id': inspection.id,
                'inspection_number': inspection.inspection_number,
                'inspection_type': inspection.inspection_type,
                'status': inspection.status,
                'priority': inspection.priority,
                'scheduled_date': inspection.scheduled_date,
                'started_at': inspection.started_at,
                'completed_at': inspection.completed_at,
                'estimated_duration': inspection.estimated_duration_minutes,
                'actual_duration': inspection.actual_duration_minutes,
                'weather_conditions': inspection.weather_conditions,
                'notes': inspection.notes,
                'findings': inspection.findings,
                'recommendations': inspection.recommendations
            },
            'gate': self._get_gate_data(inspection.gate_id) if inspection.gate_id else None,
            'inspector': self._get_user_data(inspection.assigned_inspector_id) if inspection.assigned_inspector_id else None,
            'checklist_items': self._get_inspection_items(inspection_id),
            'measurements': self._get_inspection_measurements(inspection_id),
            'photos': self._get_inspection_photos(inspection_id),
            'generation': {
                'date': datetime.utcnow(),
                'user_id': user_id,
                'document_number': self._generate_document_number('WS')
            },
            'compliance': {
                'standards': ['EN 13241-1', 'EN 12453', 'EN 12604'],
                'checklist_template': inspection.checklist_template_id
            }
        }
        
        # Add custom data
        if custom_data:
            template_data.update(custom_data)
        
        # Generate document
        return self._generate_document(
            document_type=DocumentType.WORK_SHEET,
            template=template,
            template_data=template_data,
            user_id=user_id,
            entity_type='inspection',
            entity_id=inspection_id,
            title=f"Munkalap - {inspection.inspection_number}"
        )
    
    def add_digital_signature(
        self,
        document_id: int,
        signer_id: int,
        signature_type: SignatureType = SignatureType.BASIC_STAMP,
        signature_data: Optional[Dict[str, Any]] = None
    ) -> DocumentSignature:
        """
        Add digital signature to a document.
        
        Digitális aláírás hozzáadása dokumentumhoz.
        """
        
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document not found: {document_id}")
        
        signer = self.db.query(User).filter(User.id == signer_id).first()
        if not signer:
            raise ValueError(f"Signer not found: {signer_id}")
        
        # Create signature record
        signature = DocumentSignature(
            document_id=document_id,
            signature_type=signature_type.value,
            signer_id=signer_id,
            signed_at=datetime.utcnow(),
            verification_status='signed',
            org_id=document.org_id
        )
        
        if signature_data:
            signature.signature_hash = self._generate_signature_hash(document, signature_data)
            signature.certificate_info = signature_data.get('certificate_info')
        
        # Update document
        document.signature_type = signature_type.value
        document.signature_data = signature_data
        document.signed_at = datetime.utcnow()
        document.signed_by_id = signer_id
        
        # Generate signed PDF if needed
        if signature_type == SignatureType.BASIC_STAMP:
            self._apply_signature_stamp(document, signer)
        elif signature_type == SignatureType.ETSI_PADES_B:
            # For demo purposes, just mark as signed
            document.signature_file_path = document.storage_key.replace('.pdf', '_signed.pdf')
        
        self.db.add(signature)
        self.db.commit()
        
        return signature
    
    def _generate_document(
        self,
        document_type: DocumentType,
        template: DocumentTemplate,
        template_data: Dict[str, Any],
        user_id: int,
        entity_type: str,
        entity_id: int,
        title: str
    ) -> Document:
        """Generate document from template and data."""
        
        # Generate QR code
        qr_data = self._generate_qr_data(template_data['generation']['document_number'])
        qr_image_path = self._generate_qr_code(qr_data)
        
        # Add QR code to template data
        template_data['qr_code'] = {
            'data': qr_data,
            'image_path': qr_image_path,
            'url': f"{self.base_url}/documents/verify/{template_data['generation']['document_number']}"
        }
        
        # Render HTML
        html_content = self._render_template(template, template_data)
        
        # Generate PDF
        pdf_content = self._generate_pdf(html_content, template)
        
        # Calculate file hash
        file_hash = hashlib.sha256(pdf_content).hexdigest()
        
        # Generate storage key
        filename = f"{template_data['generation']['document_number']}.pdf"
        storage_key = Document.generate_storage_key(
            org_id=template.org_id,
            entity_type=entity_type,
            filename=filename
        )
        
        # Create document record
        document = Document(
            entity_type=entity_type,
            entity_id=entity_id,
            filename=filename,
            original_filename=filename,
            title=title,
            content_type='application/pdf',
            file_size=len(pdf_content),
            file_hash=file_hash,
            storage_key=storage_key,
            category=document_type.value,
            document_number=template_data['generation']['document_number'],
            document_type=document_type.value,
            template_name=template.name,
            template_data=template_data,
            html_content=html_content,
            qr_code_data=qr_data,
            qr_code_image_path=qr_image_path,
            uploaded_by=user_id,
            generated_by_id=user_id,
            processing_status='generated',
            org_id=template.org_id
        )
        
        self.db.add(document)
        self.db.commit()
        
        # Store PDF file (in real implementation, upload to S3)
        self._store_pdf_file(document, pdf_content)
        
        return document
    
    def _get_template(self, document_type: DocumentType, template_name: Optional[str] = None) -> DocumentTemplate:
        """Get template for document type."""
        query = self.db.query(DocumentTemplate).filter(
            DocumentTemplate.document_type == document_type.value,
            DocumentTemplate.is_active == True
        )
        
        if template_name:
            template = query.filter(DocumentTemplate.name == template_name).first()
        else:
            template = query.filter(DocumentTemplate.is_default == True).first()
            if not template:
                template = query.first()
        
        if not template:
            raise ValueError(f"No template found for document type: {document_type}")
        
        return template
    
    def _generate_document_number(self, prefix: str) -> str:
        """Generate unique document number."""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        random_suffix = uuid.uuid4().hex[:6].upper()
        return f"{prefix}-{timestamp}-{random_suffix}"
    
    def _generate_qr_data(self, document_number: str) -> str:
        """Generate QR code data for document verification."""
        return f"{self.base_url}/documents/verify/{document_number}"
    
    def _generate_qr_code(self, qr_data: str) -> str:
        """Generate QR code image and return path."""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for embedding in HTML
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{qr_base64}"
    
    def _render_template(self, template: DocumentTemplate, data: Dict[str, Any]) -> str:
        """Render Jinja2 template with data."""
        jinja_template = Template(template.html_template)
        return jinja_template.render(**data)
    
    def _generate_pdf(self, html_content: str, template: DocumentTemplate) -> bytes:
        """Generate PDF from HTML content."""
        
        # Prepare CSS
        css_content = template.css_styles or ""
        
        # Create WeasyPrint HTML document
        html_doc = weasyprint.HTML(string=html_content)
        
        # Generate PDF
        pdf_bytes = html_doc.write_pdf()
        
        return pdf_bytes
    
    def _store_pdf_file(self, document: Document, pdf_content: bytes):
        """Store PDF file (placeholder for S3 upload)."""
        # In real implementation, upload to S3
        # For demo, we just update the storage path
        document.pdf_file_path = f"s3://{getattr(settings, 'S3_BUCKET', 'garagereg-docs')}/{document.storage_key}"
        self.db.commit()
    
    def _apply_signature_stamp(self, document: Document, signer: User):
        """Apply basic signature stamp to document."""
        # For demo, just update the signature file path
        document.signature_file_path = document.storage_key.replace('.pdf', '_signed.pdf')
        self.db.commit()
    
    def _generate_signature_hash(self, document: Document, signature_data: Dict[str, Any]) -> str:
        """Generate signature hash for integrity."""
        content = f"{document.file_hash}_{document.document_number}_{signature_data}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    # Helper methods for data retrieval
    def _get_gate_data(self, gate_id: int) -> Optional[Dict[str, Any]]:
        """Get gate data for template."""
        if not gate_id:
            return None
            
        gate = self.db.query(Gate).filter(Gate.id == gate_id).first()
        if not gate:
            return None
            
        return {
            'id': gate.id,
            'name': gate.name,
            'display_name': gate.display_name,
            'gate_code': gate.gate_code,
            'gate_type': gate.gate_type,
            'manufacturer': gate.manufacturer,
            'model': gate.model,
            'serial_number': gate.serial_number,
            'installation_date': gate.installation_date,
            'status': gate.status
        }
    
    def _get_user_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user data for template."""
        if not user_id:
            return None
            
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
            
        return {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'display_name': user.display_name,
            'email': user.email,
            'job_title': user.job_title,
            'department': user.department
        }
    
    def _get_gate_operations(self, gate_id: int, date_from: datetime, date_to: datetime) -> List[Dict[str, Any]]:
        """Get gate operations for operational log."""
        # Placeholder - in real implementation, query gate operation logs
        return [
            {
                'timestamp': datetime.utcnow(),
                'operation': 'OPEN',
                'duration_seconds': 15,
                'status': 'SUCCESS'
            }
        ]
    
    def _get_gate_incidents(self, gate_id: int, date_from: datetime, date_to: datetime) -> List[Dict[str, Any]]:
        """Get gate incidents for operational log.""" 
        # Placeholder - in real implementation, query incidents/tickets
        return []
    
    def _get_maintenance_summary(self, gate_id: int, date_from: datetime, date_to: datetime) -> Dict[str, Any]:
        """Get maintenance summary for operational log."""
        return {
            'scheduled_maintenance': 2,
            'emergency_repairs': 0,
            'total_downtime_hours': 1.5
        }
    
    def _get_usage_statistics(self, gate_id: int, date_from: datetime, date_to: datetime) -> Dict[str, Any]:
        """Get usage statistics for operational log."""
        return {
            'total_operations': 1250,
            'average_daily_operations': 50,
            'peak_hour': '08:00',
            'peak_operations': 75
        }
    
    def _get_parts_used(self, work_order_id: int) -> List[Dict[str, Any]]:
        """Get parts used in work order."""
        # Placeholder - query part_usages table
        return []
    
    def _get_time_logs(self, work_order_id: int) -> List[Dict[str, Any]]:
        """Get time logs for work order."""
        # Placeholder - query work_order_time_logs table  
        return []
    
    def _get_work_order_costs(self, work_order_id: int) -> Dict[str, Any]:
        """Get work order cost breakdown."""
        return {
            'labor_cost': 0.0,
            'parts_cost': 0.0,
            'total_cost': 0.0
        }
    
    def _get_inspection_items(self, inspection_id: int) -> List[Dict[str, Any]]:
        """Get inspection checklist items."""
        # Placeholder - query inspection_items table
        return []
    
    def _get_inspection_measurements(self, inspection_id: int) -> List[Dict[str, Any]]:
        """Get inspection measurements."""
        # Placeholder - query measurements table
        return []
    
    def _get_inspection_photos(self, inspection_id: int) -> List[Dict[str, Any]]:
        """Get inspection photos."""
        # Placeholder - query inspection_photos table
        return []