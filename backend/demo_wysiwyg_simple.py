"""
Simplified WYSIWYG Template Demo without PDF dependencies
Egyszerűsített WYSIWYG sablon demó PDF függőségek nélkül
"""
import asyncio
import json
import sys
import os
from datetime import datetime, timezone

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy.orm import Session
from app.database import engine, get_db
from app.models.auth import User
from app.models.organization import Organization
from app.models.documents import DocumentTemplate, DocumentType
from app.models.template_versioning import (
    DocumentTemplateVersion, DocumentTemplateChangeLog, 
    DocumentTemplateField, DocumentPreviewSession,
    TemplateChangeType, TemplateStatus
)


class SimpleWYSIWYGService:
    """
    Simplified WYSIWYG service for demo without external dependencies
    Egyszerűsített WYSIWYG szolgáltatás demóhoz külső függőségek nélkül
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_template_version(
        self,
        template_id: int,
        user_id: int,
        html_content: str,
        css_styles: str = None,
        editor_content: dict = None,
        version_type: str = "minor",
        version_name: str = None,
        metadata: dict = None
    ) -> DocumentTemplateVersion:
        """Create new template version"""
        
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
            current_version.is_current = False
        else:
            new_version_number = "1.0"
        
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
            include_qr_code=metadata.get('include_qr_code', True) if metadata else True,
            qr_code_position=metadata.get('qr_code_position', 'top_right') if metadata else 'top_right',
            status=TemplateStatus.DRAFT,
            is_current=True,
            created_by_id=user_id
        )
        
        self.db.add(new_version)
        self.db.flush()
        
        # Update template current version reference
        template.current_version_id = new_version.id
        template.updated_at = datetime.now(timezone.utc)
        
        # Log the change
        self._log_template_change(
            template_id=template_id,
            version_id=new_version.id,
            change_type=TemplateChangeType.CREATED,
            change_summary=f"Created new version {new_version_number}",
            user_id=user_id
        )
        
        self.db.commit()
        return new_version
    
    def publish_template_version(
        self,
        version_id: int,
        user_id: int,
        approval_notes: str = None
    ) -> DocumentTemplateVersion:
        """Publish template version"""
        
        version = self.db.query(DocumentTemplateVersion).filter(
            DocumentTemplateVersion.id == version_id
        ).first()
        
        if not version:
            raise ValueError(f"Template version not found: {version_id}")
        
        # Unpublish other versions
        self.db.query(DocumentTemplateVersion).filter(
            DocumentTemplateVersion.template_id == version.template_id,
            DocumentTemplateVersion.status == TemplateStatus.PUBLISHED
        ).update({'status': TemplateStatus.ARCHIVED})
        
        # Publish this version
        version.status = TemplateStatus.PUBLISHED
        version.published_at = datetime.now(timezone.utc)
        version.published_by_id = user_id
        version.is_current = True
        
        # Log the change
        self._log_template_change(
            template_id=version.template_id,
            version_id=version.id,
            change_type=TemplateChangeType.PUBLISHED,
            change_summary=f"Published version {version.version_number}",
            user_id=user_id
        )
        
        self.db.commit()
        return version
    
    def get_template_versions(self, template_id: int):
        """Get template version history"""
        return self.db.query(DocumentTemplateVersion).filter(
            DocumentTemplateVersion.template_id == template_id
        ).order_by(DocumentTemplateVersion.created_at.desc()).all()
    
    def get_template_changelog(self, template_id: int):
        """Get template change history"""
        return self.db.query(DocumentTemplateChangeLog).filter(
            DocumentTemplateChangeLog.template_id == template_id
        ).order_by(DocumentTemplateChangeLog.change_timestamp.desc()).all()
    
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
        version_id: int,
        change_type: TemplateChangeType,
        change_summary: str,
        user_id: int
    ):
        """Log template change"""
        change_log = DocumentTemplateChangeLog(
            template_id=template_id,
            version_id=version_id,
            organization_id=1,
            change_type=change_type,
            change_summary=change_summary,
            changed_by_id=user_id
        )
        
        self.db.add(change_log)


async def create_simple_wysiwyg_demo():
    """
    Create simplified WYSIWYG templates demo
    Egyszerűsített WYSIWYG sablonok demó létrehozása
    """
    print("🎨 Creating Simplified WYSIWYG Template Editor Demo...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Get or create organization
        org = db.query(Organization).filter(Organization.name == "GarageReg Demo Kft.").first()
        if not org:
            org = Organization(
                name="GarageReg Demo Kft.",
                display_name="GarageReg Demo Kft.",
                email="admin@garagereg.demo",
                tax_number="12345678-1-23",
                registration_number="Cg.01-09-123456",
                is_active=True
            )
            db.add(org)
            db.flush()
        
        # Get or create admin user
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            from app.core.security import hash_password
            admin_user = User(
                username="admin",
                email="admin@garagereg.demo",
                first_name="Admin",
                last_name="User",
                display_name="Admin User",
                password_hash=hash_password("admin123"),
                is_active=True,
                is_superuser=True,
                organization_id=org.id,
                org_id=org.id,
                timezone="Europe/Budapest",
                language="hu",
                theme="light"
            )
            db.add(admin_user)
            db.flush()
        
        # Get or create document type
        doc_type = db.query(DocumentType).filter(DocumentType.code == "GATE_INSPECTION").first()
        if not doc_type:
            doc_type = DocumentType(
                code="GATE_INSPECTION",
                name="Kapu Ellenőrzési Jegyzőkönyv",
                organization_id=org.id,
                org_id=org.id
            )
            db.add(doc_type)
            db.flush()
        
        # Create base template
        base_template = db.query(DocumentTemplate).filter(
            DocumentTemplate.name == "WYSIWYG Demo Sablon"
        ).first()
        
        if not base_template:
            base_template = DocumentTemplate(
                name="WYSIWYG Demo Sablon",
                document_type_id=doc_type.id,
                organization_id=org.id,
                org_id=org.id,
                html_template="<p>Placeholder template</p>",
                created_by_id=admin_user.id
            )
            db.add(base_template)
            db.flush()
        
        db.commit()
        
        # Initialize simplified service
        wysiwyg_service = SimpleWYSIWYGService(db)
        
        print(f"✅ Base template created: {base_template.name} (ID: {base_template.id})")
        
        # Create version 1.0 - Basic template
        print("\n📝 Creating Version 1.0 - Basic WYSIWYG Template...")
        
        html_v1 = """
<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{document_title}}</title>
</head>
<body>
    <header class="document-header">
        <div class="logo-section">
            <img src="{{organization.logo_url}}" alt="{{organization.name}}" class="company-logo" />
        </div>
        <div class="title-section">
            <h1>Kapu Ellenőrzési Jegyzőkönyv</h1>
            <p class="document-info">
                <span class="doc-number"><strong>Dokumentum száma:</strong> {{document_number}}</span>
                <span class="doc-date"><strong>Dátum:</strong> {{generation.date}}</span>
            </p>
        </div>
    </header>
    
    <main class="document-content">
        <section class="organization-info">
            <h2>Szervezet adatai</h2>
            <div class="info-grid">
                <div class="info-item">
                    <label>Szervezet neve:</label>
                    <span>{{organization.name}}</span>
                </div>
                <div class="info-item">
                    <label>Cím:</label>
                    <span>{{organization.address}}</span>
                </div>
                <div class="info-item">
                    <label>Adószám:</label>
                    <span>{{organization.tax_number}}</span>
                </div>
                <div class="info-item">
                    <label>Cégjegyzékszám:</label>
                    <span>{{organization.registration_number}}</span>
                </div>
            </div>
        </section>
        
        <section class="gate-info">
            <h2>Kapu adatai</h2>
            <div class="info-grid">
                <div class="info-item">
                    <label>Kapu azonosító:</label>
                    <span class="highlight">{{gate.id}}</span>
                </div>
                <div class="info-item">
                    <label>Kapu neve:</label>
                    <span>{{gate.name}}</span>
                </div>
                <div class="info-item">
                    <label>Helyszín:</label>
                    <span>{{gate.location}}</span>
                </div>
                <div class="info-item">
                    <label>Kapu típusa:</label>
                    <span>{{gate.type}}</span>
                </div>
            </div>
        </section>
        
        <section class="inspection-info">
            <h2>Ellenőrzés adatai</h2>
            <div class="info-grid">
                <div class="info-item">
                    <label>Ellenőr neve:</label>
                    <span>{{inspector.name}}</span>
                </div>
                <div class="info-item">
                    <label>Engedély száma:</label>
                    <span>{{inspector.license_number}}</span>
                </div>
                <div class="info-item">
                    <label>Ellenőrzés típusa:</label>
                    <span>{{inspection.type}}</span>
                </div>
                <div class="info-item">
                    <label>Ellenőrzés dátuma:</label>
                    <span>{{inspection.date}}</span>
                </div>
            </div>
            
            <div class="result-section">
                <h3>Ellenőrzés eredménye</h3>
                <div class="result-badge result-{{inspection.result|lower|replace(' ', '-')}}">
                    {{inspection.result}}
                </div>
                <p class="result-notes">{{inspection.notes|default('Nincsenek további megjegyzések.')}}</p>
            </div>
        </section>
    </main>
    
    <footer class="document-footer">
        <div class="footer-content">
            <div class="generation-info">
                <p><strong>Dokumentum generálva:</strong> {{generation.date}}</p>
                <p><strong>Generálta:</strong> {{generation.generated_by}}</p>
                <p><strong>Rendszer:</strong> GarageReg WYSIWYG Demo</p>
            </div>
            <div class="qr-section">
                <div class="qr-code">QR</div>
                <small>Dokumentum azonosító</small>
            </div>
        </div>
    </footer>
</body>
</html>
        """
        
        css_v1 = """
/* WYSIWYG Template Styles - Demo Version 1.0 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #2c3e50;
    background-color: #ffffff;
    margin: 20px;
}

/* Header Styles */
.document-header {
    display: flex;
    align-items: center;
    padding: 20px;
    border-bottom: 3px solid #3498db;
    margin-bottom: 30px;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.logo-section {
    margin-right: 30px;
}

.company-logo {
    max-height: 60px;
    max-width: 120px;
}

.title-section {
    flex: 1;
}

.title-section h1 {
    font-size: 28px;
    color: #2c3e50;
    margin-bottom: 10px;
    font-weight: 600;
}

.document-info {
    display: flex;
    gap: 30px;
    font-size: 14px;
    color: #5a6c7d;
}

/* Content Sections */
.document-content {
    padding: 0;
}

section {
    margin-bottom: 40px;
    padding: 25px;
    background: #f8f9fa;
    border-radius: 8px;
    border-left: 4px solid #3498db;
}

section h2 {
    font-size: 22px;
    color: #2c3e50;
    margin-bottom: 20px;
    font-weight: 600;
}

section h3 {
    font-size: 18px;
    color: #34495e;
    margin-bottom: 15px;
    font-weight: 600;
}

/* Info Grid */
.info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 15px;
    margin-bottom: 20px;
}

.info-item {
    display: flex;
    flex-direction: column;
    padding: 15px;
    background: white;
    border-radius: 6px;
    border: 1px solid #dee2e6;
}

.info-item label {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    color: #6c757d;
    margin-bottom: 5px;
    letter-spacing: 0.5px;
}

.info-item span {
    font-size: 16px;
    color: #2c3e50;
    font-weight: 500;
}

.highlight {
    background-color: #fff3cd;
    padding: 6px 10px;
    border-radius: 4px;
    border: 1px solid #ffeaa7;
    color: #856404 !important;
    font-weight: 700 !important;
}

/* Result Section */
.result-section {
    margin-top: 25px;
    padding: 20px;
    background: white;
    border-radius: 8px;
    border: 1px solid #dee2e6;
}

.result-badge {
    display: inline-block;
    padding: 10px 20px;
    border-radius: 25px;
    font-size: 18px;
    font-weight: 700;
    text-transform: uppercase;
    text-align: center;
    margin: 10px 0;
}

.result-megfelelő {
    background-color: #d4edda;
    color: #155724;
    border: 2px solid #c3e6cb;
}

.result-nem-megfelelő {
    background-color: #f8d7da;
    color: #721c24;
    border: 2px solid #f5c6cb;
}

.result-feltételesen-megfelelő {
    background-color: #fff3cd;
    color: #856404;
    border: 2px solid #ffeaa7;
}

.result-notes {
    margin-top: 15px;
    font-style: italic;
    color: #5a6c7d;
    line-height: 1.5;
}

/* Section Colors */
.organization-info {
    border-left-color: #e74c3c;
}

.gate-info {
    border-left-color: #27ae60;
}

.inspection-info {
    border-left-color: #f39c12;
}

/* Footer */
.document-footer {
    margin-top: 50px;
    padding: 25px;
    background: #2c3e50;
    color: white;
    border-radius: 8px;
}

.footer-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.generation-info p {
    margin-bottom: 5px;
    font-size: 14px;
}

.qr-section {
    text-align: center;
}

.qr-code {
    width: 60px;
    height: 60px;
    background: white;
    color: #2c3e50;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 18px;
    margin-bottom: 5px;
}

.qr-section small {
    font-size: 12px;
    opacity: 0.8;
}

/* Print Styles */
@media print {
    body {
        margin: 0;
        background: white;
    }
    
    .document-header {
        background: white !important;
        border-bottom: 2px solid #3498db;
    }
    
    section {
        background: white !important;
        border: 1px solid #dee2e6;
        break-inside: avoid;
    }
    
    .document-footer {
        background: #f8f9fa !important;
        color: #2c3e50 !important;
        border: 1px solid #dee2e6;
    }
}

/* Responsive Design */
@media (max-width: 768px) {
    .document-header {
        flex-direction: column;
        text-align: center;
    }
    
    .logo-section {
        margin-right: 0;
        margin-bottom: 20px;
    }
    
    .document-info {
        flex-direction: column;
        gap: 10px;
    }
    
    .info-grid {
        grid-template-columns: 1fr;
    }
    
    .footer-content {
        flex-direction: column;
        gap: 20px;
        text-align: center;
    }
}
        """
        
        editor_content_v1 = {
            "content": html_v1,
            "wysiwyg_mode": True,
            "editor": "tinymce",
            "plugins": ["lists", "table", "link", "code", "preview"],
            "last_edit": datetime.now(timezone.utc).isoformat(),
            "demo_version": True
        }
        
        metadata_v1 = {
            "title": "WYSIWYG Demo Sablon v1.0",
            "description": "Demonstrációs sablon WYSIWYG szerkesztőhöz alapvető funkcionalitással",
            "page_size": "A4",
            "orientation": "portrait",
            "include_qr_code": True,
            "qr_code_position": "footer_right",
            "include_logo": True,
            "logo_position": "header_left",
            "demo": True
        }
        
        version_1 = wysiwyg_service.create_template_version(
            template_id=base_template.id,
            user_id=admin_user.id,
            html_content=html_v1,
            css_styles=css_v1,
            editor_content=editor_content_v1,
            version_type="major",
            version_name="Alapvető WYSIWYG Demo",
            metadata=metadata_v1
        )
        
        print(f"✅ Version 1.0 created (ID: {version_1.id})")
        
        # Publish version 1.0
        published_v1 = wysiwyg_service.publish_template_version(
            version_id=version_1.id,
            user_id=admin_user.id,
            approval_notes="Initial demo template approved"
        )
        
        print(f"✅ Version 1.0 published")
        
        # Create version 2.0 - Enhanced version
        print("\n🚀 Creating Version 2.0 - Enhanced WYSIWYG Template...")
        
        html_v2 = """
<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{document_title}}</title>
</head>
<body>
    <div class="document-container">
        <header class="modern-header">
            <div class="header-pattern"></div>
            <div class="header-content">
                <div class="logo-section">
                    <img src="{{organization.logo_url}}" alt="{{organization.name}}" class="company-logo" />
                </div>
                <div class="title-section">
                    <h1>Kapu Ellenőrzési Jegyzőkönyv</h1>
                    <p class="subtitle">Professzionális Kapurendszer Biztonsági Ellenőrzés</p>
                </div>
                <div class="doc-metadata">
                    <div class="doc-number">{{document_number}}</div>
                    <div class="doc-date">{{generation.date}}</div>
                    <div class="doc-status status-{{inspection.result|lower|replace(' ', '-')}}">{{inspection.result}}</div>
                </div>
            </div>
        </header>
        
        <main class="document-main">
            <!-- Summary Cards Section -->
            <section class="summary-cards">
                <div class="card organization-card">
                    <div class="card-icon">🏢</div>
                    <div class="card-content">
                        <h3>Szervezet</h3>
                        <h4>{{organization.name}}</h4>
                        <p>{{organization.address}}</p>
                        <small>Adószám: {{organization.tax_number}}</small>
                    </div>
                </div>
                
                <div class="card gate-card">
                    <div class="card-icon">🚪</div>
                    <div class="card-content">
                        <h3>Ellenőrzött Kapu</h3>
                        <h4>{{gate.name}}</h4>
                        <p>{{gate.location}}</p>
                        <small>ID: {{gate.id}} | {{gate.type}}</small>
                    </div>
                </div>
                
                <div class="card inspector-card">
                    <div class="card-icon">👨‍🔧</div>
                    <div class="card-content">
                        <h3>Ellenőr</h3>
                        <h4>{{inspector.name}}</h4>
                        <p>Engedély: {{inspector.license_number}}</p>
                        <small>{{inspection.date}}</small>
                    </div>
                </div>
            </section>
            
            <!-- Detailed Information -->
            <section class="details-section">
                <div class="section-header">
                    <h2>Ellenőrzés részletei</h2>
                    <span class="inspection-badge">{{inspection.type}}</span>
                </div>
                
                <div class="details-grid">
                    <div class="detail-panel timeline-panel">
                        <h4>🕐 Időbeosztás</h4>
                        <div class="timeline">
                            <div class="timeline-item">
                                <div class="timeline-marker"></div>
                                <div class="timeline-content">
                                    <strong>Ellenőrzés kezdete</strong>
                                    <span>{{inspection.start_time|default('09:00')}}</span>
                                </div>
                            </div>
                            <div class="timeline-item">
                                <div class="timeline-marker"></div>
                                <div class="timeline-content">
                                    <strong>Ellenőrzés befejezése</strong>
                                    <span>{{inspection.end_time|default('10:30')}}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="detail-panel checklist-panel">
                        <h4>✅ Ellenőrzött Elemek</h4>
                        <div class="checklist">
                            <div class="check-item completed">
                                <span class="check-mark">✓</span>
                                <span>Mechanikai alkatrészek</span>
                            </div>
                            <div class="check-item completed">
                                <span class="check-mark">✓</span>
                                <span>Elektromos rendszer</span>
                            </div>
                            <div class="check-item completed">
                                <span class="check-mark">✓</span>
                                <span>Biztonsági berendezések</span>
                            </div>
                            <div class="check-item completed">
                                <span class="check-mark">✓</span>
                                <span>Vezérlő egység</span>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
            
            <!-- Result Section -->
            <section class="result-section">
                <div class="result-header">
                    <h2>Ellenőrzés eredménye</h2>
                </div>
                
                <div class="result-display result-{{inspection.result|lower|replace(' ', '-')}}">
                    <div class="result-icon">
                        {% if inspection.result == 'Megfelelő' %}
                            ✅
                        {% elif inspection.result == 'Nem megfelelő' %}
                            ❌
                        {% else %}
                            ⚠️
                        {% endif %}
                    </div>
                    <div class="result-content">
                        <h3>{{inspection.result}}</h3>
                        <p class="result-description">
                            {% if inspection.result == 'Megfelelő' %}
                                A kapu teljes mértékben megfelel a biztonsági előírásoknak és használatra alkalmas.
                            {% elif inspection.result == 'Nem megfelelő' %}
                                A kapu ellenőrzése során kritikus hibákat találtunk, amelyek azonnali javítást igényelnek.
                            {% else %}
                                A kapu feltételesen megfelelő, kisebb javítások szükségesek a teljes megfelelőséghez.
                            {% endif %}
                        </p>
                    </div>
                </div>
                
                {% if inspection.notes %}
                <div class="notes-panel">
                    <h4>📝 Részletes megjegyzések</h4>
                    <div class="notes-content">
                        {{inspection.notes|default('Az ellenőrzés során különös eltérést nem találtunk.')}}
                    </div>
                </div>
                {% endif %}
            </section>
        </main>
        
        <footer class="document-footer">
            <div class="footer-grid">
                <div class="footer-section">
                    <h5>📄 Dokumentum információk</h5>
                    <p><strong>Generálás dátuma:</strong> {{generation.date}}</p>
                    <p><strong>Generálta:</strong> {{generation.generated_by}}</p>
                    <p><strong>Rendszer verzió:</strong> GarageReg WYSIWYG v2.0</p>
                </div>
                
                <div class="footer-section signature-section">
                    <h5>✍️ Digitális aláírás</h5>
                    <div class="signature-box">
                        <div class="signature-line">{{inspector.name}}</div>
                        <small>Szakképesített kapu ellenőr</small>
                    </div>
                </div>
                
                <div class="footer-section qr-section">
                    <h5>🔗 Azonosító</h5>
                    <div class="qr-code-enhanced">
                        <div class="qr-placeholder">QR</div>
                    </div>
                    <small>{{document_number}}</small>
                </div>
            </div>
        </footer>
    </div>
</body>
</html>
        """
        
        css_v2 = """
/* WYSIWYG Enhanced Template Styles - Demo Version 2.0 */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    line-height: 1.6;
    color: #1a202c;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}

.document-container {
    max-width: 210mm;
    margin: 0 auto;
    background: white;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
}

/* Enhanced Header */
.modern-header {
    position: relative;
    background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
    color: white;
    padding: 40px;
    overflow: hidden;
}

.header-pattern {
    position: absolute;
    top: 0;
    right: 0;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
    background-size: 20px 20px;
    opacity: 0.3;
}

.header-content {
    position: relative;
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: center;
    gap: 30px;
}

.company-logo {
    max-height: 80px;
    max-width: 160px;
    filter: brightness(0) invert(1);
}

.title-section h1 {
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 8px;
    background: linear-gradient(45deg, #fff, #e2e8f0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.subtitle {
    font-size: 16px;
    opacity: 0.9;
    font-weight: 400;
}

.doc-metadata {
    text-align: right;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.doc-number {
    font-size: 18px;
    font-weight: 600;
    font-family: 'Courier New', monospace;
}

.doc-date {
    font-size: 14px;
    opacity: 0.8;
}

.doc-status {
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
}

.status-megfelelő {
    background: rgba(72, 187, 120, 0.2);
    color: #22543d;
    border: 1px solid rgba(72, 187, 120, 0.3);
}

.status-nem-megfelelő {
    background: rgba(229, 62, 62, 0.2);
    color: #742a2a;
    border: 1px solid rgba(229, 62, 62, 0.3);
}

.status-feltételesen-megfelelő {
    background: rgba(214, 158, 46, 0.2);
    color: #744210;
    border: 1px solid rgba(214, 158, 46, 0.3);
}

/* Main Content */
.document-main {
    padding: 40px;
}

/* Summary Cards */
.summary-cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 25px;
    margin-bottom: 40px;
}

.card {
    padding: 25px;
    border-radius: 16px;
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    border: 1px solid rgba(226, 232, 240, 0.8);
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 16px;
}

.card-icon {
    font-size: 32px;
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.8);
}

.organization-card .card-icon {
    background: linear-gradient(135deg, #3182ce, #2c5aa0);
    filter: grayscale(1) brightness(1.5);
}

.gate-card .card-icon {
    background: linear-gradient(135deg, #38a169, #2f855a);
    filter: grayscale(1) brightness(1.5);
}

.inspector-card .card-icon {
    background: linear-gradient(135deg, #d69e2e, #b7791f);
    filter: grayscale(1) brightness(1.5);
}

.card-content h3 {
    font-size: 14px;
    font-weight: 600;
    color: #4a5568;
    margin-bottom: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.card-content h4 {
    font-size: 18px;
    font-weight: 700;
    color: #1a202c;
    margin-bottom: 4px;
}

.card-content p {
    font-size: 14px;
    color: #4a5568;
    margin-bottom: 4px;
}

.card-content small {
    font-size: 12px;
    color: #718096;
}

/* Details Section */
.details-section {
    background: #f7fafc;
    border-radius: 16px;
    padding: 30px;
    margin-bottom: 30px;
}

.section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 25px;
}

.section-header h2 {
    font-size: 24px;
    font-weight: 700;
    color: #2d3748;
}

.inspection-badge {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 8px 16px;
    border-radius: 25px;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.details-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 25px;
}

.detail-panel {
    background: white;
    padding: 25px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}

.detail-panel h4 {
    font-size: 16px;
    font-weight: 600;
    color: #2d3748;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Timeline */
.timeline {
    position: relative;
}

.timeline::before {
    content: '';
    position: absolute;
    left: 12px;
    top: 20px;
    bottom: 20px;
    width: 2px;
    background: linear-gradient(to bottom, #667eea, #764ba2);
}

.timeline-item {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 20px;
    position: relative;
}

.timeline-marker {
    width: 24px;
    height: 24px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 50%;
    border: 3px solid white;
    box-shadow: 0 0 0 2px #e2e8f0;
    z-index: 1;
}

.timeline-content {
    display: flex;
    flex-direction: column;
}

.timeline-content strong {
    font-weight: 600;
    color: #2d3748;
    margin-bottom: 2px;
}

.timeline-content span {
    color: #718096;
    font-size: 14px;
}

/* Checklist */
.checklist {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.check-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: #f8f9fa;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
}

.check-item.completed .check-mark {
    background: linear-gradient(135deg, #48bb78, #38a169);
    color: white;
}

.check-mark {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: #e2e8f0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: bold;
}

/* Result Section */
.result-section {
    background: white;
    border-radius: 16px;
    padding: 30px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
}

.result-header h2 {
    font-size: 24px;
    font-weight: 700;
    color: #2d3748;
    margin-bottom: 25px;
}

.result-display {
    display: flex;
    align-items: center;
    gap: 25px;
    padding: 25px;
    border-radius: 16px;
    margin-bottom: 25px;
}

.result-megfelelő {
    background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
    border: 2px solid #9ae6b4;
}

.result-nem-megfelelő {
    background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
    border: 2px solid #fc8181;
}

.result-feltételesen-megfelelő {
    background: linear-gradient(135deg, #fffbeb 0%, #feebc8 100%);
    border: 2px solid #f6ad55;
}

.result-icon {
    font-size: 48px;
    width: 80px;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.8);
}

.result-content h3 {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 8px;
}

.result-megfelelő .result-content h3 {
    color: #22543d;
}

.result-nem-megfelelő .result-content h3 {
    color: #742a2a;
}

.result-feltételesen-megfelelő .result-content h3 {
    color: #744210;
}

.result-description {
    font-size: 16px;
    color: #4a5568;
    line-height: 1.6;
}

.notes-panel {
    background: #f7fafc;
    padding: 20px;
    border-radius: 12px;
    border-left: 4px solid #667eea;
}

.notes-panel h4 {
    font-size: 16px;
    font-weight: 600;
    color: #2d3748;
    margin-bottom: 12px;
}

.notes-content {
    font-size: 14px;
    color: #4a5568;
    line-height: 1.6;
    font-style: italic;
}

/* Footer */
.document-footer {
    background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
    color: white;
    padding: 30px 40px;
}

.footer-grid {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 40px;
    align-items: center;
}

.footer-section h5 {
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 12px;
    color: #e2e8f0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.footer-section p {
    font-size: 13px;
    color: #cbd5e0;
    margin-bottom: 4px;
}

.signature-section {
    text-align: center;
}

.signature-box {
    padding: 20px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    backdrop-filter: blur(10px);
}

.signature-line {
    font-size: 16px;
    font-weight: 600;
    color: white;
    border-bottom: 2px solid rgba(255, 255, 255, 0.3);
    padding-bottom: 8px;
    margin-bottom: 8px;
    min-width: 200px;
}

.signature-box small {
    font-size: 12px;
    color: #cbd5e0;
}

.qr-section {
    text-align: center;
}

.qr-code-enhanced {
    width: 80px;
    height: 80px;
    background: linear-gradient(135deg, #f8f9fa, #e2e8f0);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.qr-placeholder {
    font-size: 24px;
    font-weight: bold;
    color: #2d3748;
}

.qr-section small {
    font-size: 11px;
    color: #a0aec0;
    font-family: 'Courier New', monospace;
}

/* Print Optimizations */
@media print {
    body {
        background: none !important;
        padding: 0;
    }
    
    .document-container {
        box-shadow: none;
        border-radius: 0;
    }
    
    .modern-header {
        background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%) !important;
        print-color-adjust: exact;
    }
    
    .summary-cards {
        break-inside: avoid;
    }
    
    .details-section {
        break-inside: avoid;
    }
    
    .result-section {
        break-inside: avoid;
    }
}

/* Responsive Design */
@media (max-width: 768px) {
    .header-content {
        grid-template-columns: 1fr;
        text-align: center;
        gap: 20px;
    }
    
    .summary-cards {
        grid-template-columns: 1fr;
    }
    
    .details-grid {
        grid-template-columns: 1fr;
    }
    
    .result-display {
        flex-direction: column;
        text-align: center;
    }
    
    .footer-grid {
        grid-template-columns: 1fr;
        text-align: center;
        gap: 20px;
    }
}
        """
        
        editor_content_v2 = {
            "content": html_v2,
            "wysiwyg_mode": True,
            "editor": "tinymce",
            "plugins": ["lists", "table", "link", "code", "preview", "template", "visualblocks", "fullscreen"],
            "toolbar_config": "enhanced",
            "custom_css": True,
            "responsive_design": True,
            "print_optimized": True,
            "modern_ui": True,
            "last_edit": datetime.now(timezone.utc).isoformat(),
            "changelog": [
                "Modern card-based layout with icons",
                "Enhanced typography with Inter font",
                "Interactive timeline and checklist elements",
                "Gradient backgrounds and improved colors",
                "Better responsive design",
                "Enhanced print styles",
                "Professional footer with signature section"
            ]
        }
        
        metadata_v2 = {
            "title": "WYSIWYG Demo Sablon v2.0",
            "description": "Fejlett demonstrációs sablon modern design elemekkel, kártya alapú elrendezéssel és interaktív komponensekkel",
            "page_size": "A4",
            "orientation": "portrait",
            "include_qr_code": True,
            "qr_code_position": "footer_right",
            "include_logo": True,
            "logo_position": "header_left",
            "modern_design": True,
            "responsive": True,
            "print_optimized": True,
            "demo_version": "2.0"
        }
        
        version_2 = wysiwyg_service.create_template_version(
            template_id=base_template.id,
            user_id=admin_user.id,
            html_content=html_v2,
            css_styles=css_v2,
            editor_content=editor_content_v2,
            version_type="major",
            version_name="Fejlett Modern WYSIWYG Demo",
            metadata=metadata_v2
        )
        
        print(f"✅ Version 2.0 created (ID: {version_2.id})")
        
        # Get version history
        versions = wysiwyg_service.get_template_versions(base_template.id)
        print(f"\n📚 Template version history ({len(versions)} versions):")
        
        for v in versions:
            status_icon = "🟢" if v.status == TemplateStatus.PUBLISHED else "🟡"
            current_icon = "⭐" if v.is_current else "  "
            print(f"   {status_icon} {current_icon} v{v.version_number} - {v.version_name}")
            print(f"      📅 {v.created_at.strftime('%Y-%m-%d %H:%M')} | 👤 {v.created_by.display_name}")
            print(f"      📄 HTML: {len(v.html_template)} chars | 🎨 CSS: {len(v.css_styles or '')} chars")
        
        # Get changelog
        changelog = wysiwyg_service.get_template_changelog(base_template.id)
        print(f"\n📋 Template changelog ({len(changelog)} entries):")
        
        for change in changelog:
            icon = "📝" if change.change_type == TemplateChangeType.CREATED else "🚀" if change.change_type == TemplateChangeType.PUBLISHED else "✏️"
            print(f"   {icon} {change.change_timestamp.strftime('%Y-%m-%d %H:%M')} | {change.change_type.value}")
            print(f"      📋 {change.change_summary}")
        
        # Sample data for rendering
        sample_data = {
            "document_title": "Kapu Ellenőrzési Jegyzőkönyv - WYSIWYG Demo",
            "document_number": "DEMO-2025-001",
            "organization": {
                "name": "GarageReg Demo Kft.",
                "address": "1234 Budapest, Demo utca 1.",
                "tax_number": "12345678-1-23",
                "registration_number": "Cg.01-09-123456",
                "logo_url": "/assets/logo-demo.png"
            },
            "gate": {
                "id": "GATE-DEMO-001",
                "name": "Főbejárat Automatikus Kapu",
                "location": "Budapest, Demo utca 1., főbejárat",
                "type": "Automatikus tolókapu DEMO-X1"
            },
            "inspector": {
                "name": "Demo Ellenőr Péter",
                "display_name": "Demo Ellenőr Péter",
                "license_number": "DEMO-ELL-12345"
            },
            "inspection": {
                "id": 1,
                "type": "Éves biztonsági ellenőrzés (Demo)",
                "date": "2025-01-02",
                "start_time": "09:00",
                "end_time": "10:30",
                "result": "Megfelelő",
                "notes": "Ez egy demonstrációs ellenőrzés a WYSIWYG sablon rendszer bemutatásához. Az összes komponens megfelelő állapotban van."
            },
            "generation": {
                "date": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
                "generated_by": "WYSIWYG Demo System v2.0",
                "document_number": "DEMO-2025-001"
            }
        }
        
        # Test HTML rendering (without PDF generation)
        print(f"\n🖼️ Testing template rendering...")
        
        try:
            from jinja2 import Template
            
            # Test version 1.0
            template_v1 = Template(version_1.html_template)
            rendered_html_v1 = template_v1.render(**sample_data)
            print(f"✅ Version 1.0 HTML rendered ({len(rendered_html_v1)} characters)")
            
            # Test version 2.0
            template_v2 = Template(version_2.html_template)
            rendered_html_v2 = template_v2.render(**sample_data)
            print(f"✅ Version 2.0 HTML rendered ({len(rendered_html_v2)} characters)")
            
            # Save sample HTML files for preview
            os.makedirs('demo_output', exist_ok=True)
            
            with open('demo_output/wysiwyg_demo_v1.html', 'w', encoding='utf-8') as f:
                f.write(f"<style>{version_1.css_styles}</style>\n{rendered_html_v1}")
            
            with open('demo_output/wysiwyg_demo_v2.html', 'w', encoding='utf-8') as f:
                f.write(f"<style>{version_2.css_styles}</style>\n{rendered_html_v2}")
            
            print(f"📁 Sample HTML files saved to demo_output/")
            
        except Exception as e:
            print(f"⚠️ Template rendering test failed: {e}")
        
        # Summary
        print(f"\n🎉 Simplified WYSIWYG Template Demo Complete!")
        print(f"📋 Template: {base_template.name} (ID: {base_template.id})")
        print(f"📈 Versions: {len(versions)}")
        print(f"📝 Changes: {len(changelog)}")
        print(f"🏢 Organization: {org.name}")
        print(f"👤 Admin User: {admin_user.display_name}")
        
        print(f"\n✨ WYSIWYG Features Demonstrated:")
        print(f"   ✅ Template versioning with semantic versioning")
        print(f"   ✅ WYSIWYG editor content management")
        print(f"   ✅ CSS styling with progressive enhancement")
        print(f"   ✅ Change tracking and audit logging")
        print(f"   ✅ Template publishing workflow")
        print(f"   ✅ Jinja2 template variable support")
        print(f"   ✅ Responsive design and print optimization")
        print(f"   ✅ Modern UI components (cards, timeline, etc.)")
        
        print(f"\n📂 Demo Output Files:")
        print(f"   🌐 Version 1.0: demo_output/wysiwyg_demo_v1.html")
        print(f"   🌐 Version 2.0: demo_output/wysiwyg_demo_v2.html")
        
        print(f"\n🔗 API Endpoints to Test:")
        print(f"   📊 Template Versions: GET /api/admin/wysiwyg-templates/templates/{base_template.id}/versions")
        print(f"   📋 Template Changelog: GET /api/admin/wysiwyg-templates/templates/{base_template.id}/changelog")
        print(f"   📝 Version Details: GET /api/admin/wysiwyg-templates/versions/{version_2.id}")
        print(f"   🆚 Version Compare: GET /api/admin/wysiwyg-templates/versions/{version_1.id}/compare/{version_2.id}")
        
        return {
            "success": True,
            "template_id": base_template.id,
            "versions": [{"id": v.id, "version": v.version_number, "name": v.version_name} for v in versions],
            "changelog_entries": len(changelog),
            "output_files": ["demo_output/wysiwyg_demo_v1.html", "demo_output/wysiwyg_demo_v2.html"]
        }
        
    except Exception as e:
        print(f"❌ Error creating WYSIWYG demo: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}
    finally:
        db.close()


if __name__ == "__main__":
    result = asyncio.run(create_simple_wysiwyg_demo())
    if result.get("success"):
        print(f"\n✅ WYSIWYG Demo completed successfully!")
        print(f"🎯 Ready for template modification → fresh PDF generation!")
    else:
        print(f"\n❌ Demo failed: {result.get('error', 'Unknown error')}")