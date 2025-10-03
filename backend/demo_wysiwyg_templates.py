"""
Demo script for WYSIWYG Template Editor System
WYSIWYG sablon szerkesztő rendszer demó szkript
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
from app.services.wysiwyg_template_service import WYSIWYGTemplateService


async def create_sample_wysiwyg_templates():
    """
    Create sample WYSIWYG templates with versioning
    Minta WYSIWYG sablonok létrehozása verziókezeléssel
    """
    print("🎨 Creating WYSIWYG Template Editor Demo...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Get or create organization
        org = db.query(Organization).filter(Organization.name == "GarageReg Demo Kft.").first()
        if not org:
            org = Organization(
                name="GarageReg Demo Kft.",
                address="1234 Budapest, Demo utca 1.",
                tax_number="12345678-1-23",
                registration_number="Cg.01-09-123456"
            )
            db.add(org)
            db.flush()
        
        # Get or create admin user
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@garagereg.local",
                display_name="Admin User",
                is_admin=True,
                organization_id=org.id
            )
            admin_user.set_password("admin123")
            db.add(admin_user)
            db.flush()
        
        # Get or create document type
        doc_type = db.query(DocumentType).filter(DocumentType.code == "GATE_INSPECTION").first()
        if not doc_type:
            doc_type = DocumentType(
                code="GATE_INSPECTION",
                name="Kapu Ellenőrzési Jegyzőkönyv",
                organization_id=org.id
            )
            db.add(doc_type)
            db.flush()
        
        # Create base template
        base_template = db.query(DocumentTemplate).filter(
            DocumentTemplate.name == "WYSIWYG Ellenőrzési Sablon"
        ).first()
        
        if not base_template:
            base_template = DocumentTemplate(
                name="WYSIWYG Ellenőrzési Sablon",
                document_type_id=doc_type.id,
                organization_id=org.id,
                html_template="<p>Placeholder template</p>",
                created_by_id=admin_user.id
            )
            db.add(base_template)
            db.flush()
        
        db.commit()
        
        # Initialize WYSIWYG service
        wysiwyg_service = WYSIWYGTemplateService(db)
        
        print(f"✅ Base template created: {base_template.name} (ID: {base_template.id})")
        
        # Create version 1.0 - Basic HTML template
        print("\n📝 Creating Version 1.0 - Basic Template...")
        
        html_v1 = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{document_title}}</title>
</head>
<body>
    <div class="document-header">
        <h1>Kapu Ellenőrzési Jegyzőkönyv</h1>
        <p><strong>Dokumentum száma:</strong> {{document_number}}</p>
        <p><strong>Dátum:</strong> {{generation.date}}</p>
    </div>
    
    <div class="document-content">
        <h2>Alapadatok</h2>
        <table class="info-table">
            <tr>
                <td><strong>Szervezet:</strong></td>
                <td>{{organization.name}}</td>
            </tr>
            <tr>
                <td><strong>Cím:</strong></td>
                <td>{{organization.address}}</td>
            </tr>
            <tr>
                <td><strong>Kapu azonosító:</strong></td>
                <td>{{gate.id}}</td>
            </tr>
            <tr>
                <td><strong>Kapu neve:</strong></td>
                <td>{{gate.name}}</td>
            </tr>
            <tr>
                <td><strong>Kapu típusa:</strong></td>
                <td>{{gate.type}}</td>
            </tr>
        </table>
        
        <h2>Ellenőrzés adatai</h2>
        <table class="info-table">
            <tr>
                <td><strong>Ellenőr:</strong></td>
                <td>{{inspector.name}}</td>
            </tr>
            <tr>
                <td><strong>Ellenőr engedély szám:</strong></td>
                <td>{{inspector.license_number}}</td>
            </tr>
            <tr>
                <td><strong>Ellenőrzés típusa:</strong></td>
                <td>{{inspection.type}}</td>
            </tr>
            <tr>
                <td><strong>Ellenőrzés dátuma:</strong></td>
                <td>{{inspection.date}}</td>
            </tr>
            <tr>
                <td><strong>Eredmény:</strong></td>
                <td class="result-{{inspection.result|lower}}">{{inspection.result}}</td>
            </tr>
        </table>
    </div>
    
    <div class="document-footer">
        <p>Generálva: {{generation.date}} - {{generation.generated_by}}</p>
    </div>
</body>
</html>
        """
        
        css_v1 = """
/* WYSIWYG Template Styles v1.0 */
body {
    font-family: 'Arial', sans-serif;
    margin: 20px;
    line-height: 1.6;
    color: #333;
}

.document-header {
    text-align: center;
    border-bottom: 2px solid #2196F3;
    padding-bottom: 20px;
    margin-bottom: 30px;
}

.document-header h1 {
    color: #2196F3;
    margin: 0 0 15px 0;
    font-size: 24px;
}

.document-content h2 {
    color: #1976D2;
    border-bottom: 1px solid #E0E0E0;
    padding-bottom: 5px;
    margin-top: 30px;
}

.info-table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
}

.info-table td {
    padding: 8px 12px;
    border: 1px solid #E0E0E0;
}

.info-table td:first-child {
    background-color: #F5F5F5;
    font-weight: bold;
    width: 200px;
}

.result-megfelelő {
    color: #4CAF50;
    font-weight: bold;
}

.result-nem-megfelelő {
    color: #F44336;
    font-weight: bold;
}

.result-feltételesen-megfelelő {
    color: #FF9800;
    font-weight: bold;
}

.document-footer {
    margin-top: 50px;
    padding-top: 20px;
    border-top: 1px solid #E0E0E0;
    text-align: center;
    font-size: 12px;
    color: #757575;
}
        """
        
        editor_content_v1 = {
            "content": html_v1,
            "wysiwyg_mode": True,
            "editor": "tinymce",
            "plugins": ["lists", "table", "link"],
            "last_edit": datetime.now(timezone.utc).isoformat()
        }
        
        metadata_v1 = {
            "title": "Kapu Ellenőrzési Jegyzőkönyv v1.0",
            "description": "Alapvető ellenőrzési sablon egyszerű táblázatos megjelenítéssel",
            "page_size": "A4",
            "orientation": "portrait",
            "include_qr_code": True,
            "qr_code_position": "top_right",
            "include_logo": True,
            "logo_position": "top_left",
            "sample_data": {
                "document_title": "Kapu Ellenőrzési Jegyzőkönyv",
                "gate_type": "Automatikus tolókapu"
            }
        }
        
        version_1 = wysiwyg_service.create_template_version(
            template_id=base_template.id,
            user_id=admin_user.id,
            html_content=html_v1,
            css_styles=css_v1,
            editor_content=editor_content_v1,
            version_type="major",
            version_name="Alapvető sablon",
            metadata=metadata_v1
        )
        
        print(f"✅ Version 1.0 created (ID: {version_1.id})")
        
        # Publish version 1.0
        published_v1 = wysiwyg_service.publish_template_version(
            version_id=version_1.id,
            user_id=admin_user.id,
            approval_notes="Initial template version approved"
        )
        
        print(f"✅ Version 1.0 published")
        
        # Create version 1.1 - Enhanced styling
        print("\n🎨 Creating Version 1.1 - Enhanced Styling...")
        
        html_v1_1 = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{document_title}}</title>
</head>
<body>
    <div class="document-header">
        <div class="header-logo">
            <img src="{{organization.logo_url}}" alt="Logo" class="company-logo" />
        </div>
        <div class="header-content">
            <h1>Kapu Ellenőrzési Jegyzőkönyv</h1>
            <div class="header-info">
                <span class="doc-number">Dokumentum: <strong>{{document_number}}</strong></span>
                <span class="doc-date">Dátum: <strong>{{generation.date}}</strong></span>
            </div>
        </div>
    </div>
    
    <div class="document-content">
        <div class="section organization-section">
            <h2><i class="icon-building"></i> Szervezet adatai</h2>
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
        </div>
        
        <div class="section gate-section">
            <h2><i class="icon-gate"></i> Kapu adatai</h2>
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
        </div>
        
        <div class="section inspection-section">
            <h2><i class="icon-check"></i> Ellenőrzés adatai</h2>
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
            
            <div class="result-box result-{{inspection.result|lower|replace(' ', '-')}}">
                <h3>Ellenőrzés eredménye</h3>
                <div class="result-value">{{inspection.result}}</div>
            </div>
        </div>
    </div>
    
    <div class="document-footer">
        <div class="footer-left">
            <p>Generálva: {{generation.date}}</p>
            <p>Generálta: {{generation.generated_by}}</p>
        </div>
        <div class="footer-right">
            <div class="qr-code">
                <!-- QR kód helye -->
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        css_v1_1 = """
/* WYSIWYG Template Styles v1.1 - Enhanced */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 20px;
    line-height: 1.6;
    color: #2c3e50;
    background-color: #f8f9fa;
}

.document-header {
    display: flex;
    align-items: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 25px;
    border-radius: 10px 10px 0 0;
    margin-bottom: 0;
}

.header-logo {
    margin-right: 20px;
}

.company-logo {
    max-height: 60px;
    max-width: 120px;
}

.header-content {
    flex: 1;
}

.header-content h1 {
    margin: 0 0 10px 0;
    font-size: 28px;
    font-weight: 300;
}

.header-info {
    display: flex;
    gap: 30px;
    font-size: 14px;
    opacity: 0.9;
}

.document-content {
    background: white;
    padding: 0;
    border-radius: 0 0 10px 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.section {
    padding: 30px;
    border-bottom: 1px solid #e9ecef;
}

.section:last-child {
    border-bottom: none;
}

.section h2 {
    color: #495057;
    margin: 0 0 20px 0;
    font-size: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 15px;
    margin-bottom: 20px;
}

.info-item {
    display: flex;
    flex-direction: column;
    padding: 15px;
    background-color: #f8f9fa;
    border-radius: 8px;
    border-left: 4px solid #667eea;
}

.info-item label {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    color: #6c757d;
    margin-bottom: 5px;
}

.info-item span {
    font-size: 16px;
    color: #2c3e50;
    font-weight: 500;
}

.highlight {
    background-color: #fff3cd;
    padding: 4px 8px;
    border-radius: 4px;
    border: 1px solid #ffeaa7;
    color: #856404 !important;
    font-weight: 700 !important;
}

.result-box {
    margin-top: 25px;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
}

.result-box h3 {
    margin: 0 0 10px 0;
    font-size: 16px;
    font-weight: 600;
}

.result-value {
    font-size: 24px;
    font-weight: 700;
    text-transform: uppercase;
}

.result-megfelelő {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
}

.result-nem-megfelelő {
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
}

.result-feltételesen-megfelelő {
    background-color: #fff3cd;
    border: 1px solid #ffeaa7;
    color: #856404;
}

.organization-section {
    background-color: #f8f9fa;
}

.gate-section {
    background-color: white;
}

.inspection-section {
    background-color: #f1f3f4;
}

.document-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 30px;
    padding: 20px;
    background-color: #e9ecef;
    border-radius: 8px;
    font-size: 12px;
    color: #6c757d;
}

.footer-left p {
    margin: 0 0 5px 0;
}

.qr-code {
    width: 80px;
    height: 80px;
    background-color: white;
    border: 2px solid #dee2e6;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    text-align: center;
    color: #adb5bd;
}

/* Print styles */
@media print {
    body {
        background-color: white;
        padding: 0;
    }
    
    .document-content {
        box-shadow: none;
    }
}
        """
        
        editor_content_v1_1 = {
            "content": html_v1_1,
            "wysiwyg_mode": True,
            "editor": "tinymce",
            "plugins": ["lists", "table", "link", "image", "code"],
            "toolbar_config": "enhanced",
            "last_edit": datetime.now(timezone.utc).isoformat(),
            "changelog": ["Enhanced styling", "Added grid layout", "Improved visual hierarchy"]
        }
        
        metadata_v1_1 = {
            "title": "Kapu Ellenőrzési Jegyzőkönyv v1.1",
            "description": "Fejlett megjelenésű sablon rácsos elrendezéssel és javított vizuális hierarchiával",
            "page_size": "A4",
            "orientation": "portrait",
            "include_qr_code": True,
            "qr_code_position": "bottom_right",
            "include_logo": True,
            "logo_position": "top_left"
        }
        
        version_1_1 = wysiwyg_service.create_template_version(
            template_id=base_template.id,
            user_id=admin_user.id,
            html_content=html_v1_1,
            css_styles=css_v1_1,
            editor_content=editor_content_v1_1,
            version_type="minor",
            version_name="Fejlett megjelenés",
            metadata=metadata_v1_1
        )
        
        print(f"✅ Version 1.1 created (ID: {version_1_1.id})")
        
        # Create version 2.0 - Interactive elements
        print("\n🚀 Creating Version 2.0 - Interactive Features...")
        
        html_v2 = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
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
                    <p class="subtitle">Automatikus Kapurendszer Biztonsági Ellenőrzés</p>
                </div>
                <div class="doc-info">
                    <div class="doc-number">{{document_number}}</div>
                    <div class="doc-date">{{generation.date|strftime('%Y. %m. %d.')}}</div>
                </div>
            </div>
        </header>
        
        <main class="document-main">
            <div class="summary-cards">
                <div class="summary-card organization-card">
                    <h3><i class="icon-building"></i> Szervezet</h3>
                    <h4>{{organization.name}}</h4>
                    <p>{{organization.address}}</p>
                    <small>Adószám: {{organization.tax_number}}</small>
                </div>
                
                <div class="summary-card gate-card">
                    <h3><i class="icon-gate"></i> Ellenőrzött Kapu</h3>
                    <h4>{{gate.name}}</h4>
                    <p>{{gate.location}}</p>
                    <small>ID: {{gate.id}} | Típus: {{gate.type}}</small>
                </div>
                
                <div class="summary-card inspector-card">
                    <h3><i class="icon-user"></i> Ellenőr</h3>
                    <h4>{{inspector.name}}</h4>
                    <p>Engedély: {{inspector.license_number}}</p>
                    <small>{{inspection.date|strftime('%Y. %m. %d.')}}</small>
                </div>
            </div>
            
            <section class="inspection-details">
                <div class="section-header">
                    <h2>Ellenőrzés részletei</h2>
                    <span class="section-badge">{{inspection.type}}</span>
                </div>
                
                <div class="details-grid">
                    <div class="detail-group">
                        <h4>Időpontok</h4>
                        <div class="timeline">
                            <div class="timeline-item">
                                <span class="timeline-dot"></span>
                                <div class="timeline-content">
                                    <strong>Ellenőrzés kezdete</strong>
                                    <small>{{inspection.start_time|default('09:00')}}</small>
                                </div>
                            </div>
                            <div class="timeline-item">
                                <span class="timeline-dot"></span>
                                <div class="timeline-content">
                                    <strong>Ellenőrzés vége</strong>
                                    <small>{{inspection.end_time|default('10:30')}}</small>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="detail-group">
                        <h4>Ellenőrzött Komponensek</h4>
                        <div class="checklist">
                            <div class="check-item checked">
                                <i class="check-icon">✓</i>
                                <span>Mechanikai elemek</span>
                            </div>
                            <div class="check-item checked">
                                <i class="check-icon">✓</i>
                                <span>Elektromos rendszer</span>
                            </div>
                            <div class="check-item checked">
                                <i class="check-icon">✓</i>
                                <span>Biztonsági berendezések</span>
                            </div>
                            <div class="check-item checked">
                                <i class="check-icon">✓</i>
                                <span>Vezérlőrendszer</span>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
            
            <section class="result-section">
                <div class="result-header">
                    <h2>Ellenőrzés eredménye</h2>
                </div>
                
                <div class="result-display result-{{inspection.result|lower|replace(' ', '-')}}">
                    <div class="result-icon">
                        {% if inspection.result == 'Megfelelő' %}
                            <i class="icon-check-circle"></i>
                        {% elif inspection.result == 'Nem megfelelő' %}
                            <i class="icon-x-circle"></i>
                        {% else %}
                            <i class="icon-alert-circle"></i>
                        {% endif %}
                    </div>
                    <div class="result-content">
                        <h3>{{inspection.result}}</h3>
                        <p class="result-description">
                            {% if inspection.result == 'Megfelelő' %}
                                A kapu minden ellenőrzött komponense megfelel a biztonsági előírásoknak.
                            {% elif inspection.result == 'Nem megfelelő' %}
                                A kapu ellenőrzése során hiányosságokat találtunk, amelyek javítást igényelnek.
                            {% else %}
                                A kapu feltételesen megfelelő, kisebb javításokat igényel.
                            {% endif %}
                        </p>
                    </div>
                </div>
                
                {% if inspection.notes %}
                <div class="notes-section">
                    <h4>Megjegyzések</h4>
                    <div class="notes-content">
                        {{inspection.notes|default('Nincsenek további megjegyzések.')}}
                    </div>
                </div>
                {% endif %}
            </section>
        </main>
        
        <footer class="document-footer">
            <div class="footer-content">
                <div class="footer-left">
                    <h5>Ellenőrzés adatai</h5>
                    <p>Dokumentum generálva: {{generation.date}}</p>
                    <p>Generálta: {{generation.generated_by}}</p>
                    <p>Rendszer: GarageReg v2.0</p>
                </div>
                
                <div class="footer-center">
                    <div class="verification-box">
                        <h6>Digitális Aláírás</h6>
                        <div class="signature-line">
                            {{inspector.name}}
                        </div>
                        <small>Szakképesített ellenőr</small>
                    </div>
                </div>
                
                <div class="footer-right">
                    <div class="qr-section">
                        <div class="qr-code">
                            <!-- QR Code Placeholder -->
                            <div class="qr-placeholder">QR</div>
                        </div>
                        <small>Dokumentum azonosító</small>
                    </div>
                </div>
            </div>
        </footer>
    </div>
</body>
</html>
        """
        
        css_v2 = """
/* WYSIWYG Template Styles v2.0 - Interactive & Modern */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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

/* Modern Header */
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
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
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
    opacity: 0.8;
    font-weight: 400;
}

.doc-info {
    text-align: right;
}

.doc-number {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 4px;
}

.doc-date {
    font-size: 14px;
    opacity: 0.8;
}

/* Main Content */
.document-main {
    padding: 40px;
}

/* Summary Cards */
.summary-cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-bottom: 40px;
}

.summary-card {
    padding: 24px;
    border-radius: 12px;
    border-left: 4px solid;
    background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
    transition: transform 0.2s ease;
}

.organization-card {
    border-left-color: #3182ce;
}

.gate-card {
    border-left-color: #38a169;
}

.inspector-card {
    border-left-color: #d69e2e;
}

.summary-card h3 {
    font-size: 14px;
    font-weight: 600;
    color: #4a5568;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.summary-card h4 {
    font-size: 18px;
    font-weight: 700;
    color: #1a202c;
    margin-bottom: 4px;
}

.summary-card p {
    font-size: 14px;
    color: #4a5568;
    margin-bottom: 8px;
}

.summary-card small {
    font-size: 12px;
    color: #718096;
}

/* Inspection Details */
.inspection-details {
    background: #f7fafc;
    border-radius: 12px;
    padding: 30px;
    margin-bottom: 30px;
}

.section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
}

.section-header h2 {
    font-size: 24px;
    font-weight: 700;
    color: #2d3748;
}

.section-badge {
    background: #667eea;
    color: white;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
}

.details-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 30px;
}

.detail-group h4 {
    font-size: 16px;
    font-weight: 600;
    color: #2d3748;
    margin-bottom: 16px;
}

/* Timeline */
.timeline {
    position: relative;
}

.timeline::before {
    content: '';
    position: absolute;
    left: 8px;
    top: 12px;
    bottom: 12px;
    width: 2px;
    background: #e2e8f0;
}

.timeline-item {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    margin-bottom: 20px;
    position: relative;
}

.timeline-dot {
    width: 16px;
    height: 16px;
    background: #667eea;
    border-radius: 50%;
    border: 3px solid white;
    box-shadow: 0 0 0 2px #e2e8f0;
    z-index: 1;
}

.timeline-content strong {
    display: block;
    font-weight: 600;
    color: #2d3748;
    margin-bottom: 2px;
}

.timeline-content small {
    color: #718096;
    font-size: 14px;
}

/* Checklist */
.checklist {
    space-y: 12px;
}

.check-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: white;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    margin-bottom: 8px;
}

.check-item.checked .check-icon {
    background: #48bb78;
    color: white;
}

.check-icon {
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
    border-radius: 12px;
    padding: 30px;
    border: 1px solid #e2e8f0;
}

.result-header h2 {
    font-size: 24px;
    font-weight: 700;
    color: #2d3748;
    margin-bottom: 24px;
}

.result-display {
    display: flex;
    align-items: center;
    gap: 24px;
    padding: 24px;
    border-radius: 12px;
    margin-bottom: 20px;
}

.result-megfelelő {
    background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
    border: 1px solid #9ae6b4;
}

.result-nem-megfelelő {
    background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
    border: 1px solid #fc8181;
}

.result-feltételesen-megfelelő {
    background: linear-gradient(135deg, #fffbeb 0%, #feebc8 100%);
    border: 1px solid #f6ad55;
}

.result-icon {
    font-size: 48px;
}

.result-megfelelő .result-icon {
    color: #38a169;
}

.result-nem-megfelelő .result-icon {
    color: #e53e3e;
}

.result-feltételesen-megfelelő .result-icon {
    color: #d69e2e;
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
    line-height: 1.5;
}

.notes-section {
    background: #f7fafc;
    padding: 20px;
    border-radius: 8px;
    border-left: 4px solid #667eea;
}

.notes-section h4 {
    font-size: 16px;
    font-weight: 600;
    color: #2d3748;
    margin-bottom: 12px;
}

.notes-content {
    font-size: 14px;
    color: #4a5568;
    line-height: 1.6;
}

/* Footer */
.document-footer {
    background: #2d3748;
    color: white;
    padding: 30px 40px;
}

.footer-content {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 40px;
    align-items: center;
}

.footer-left h5 {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 12px;
    color: #e2e8f0;
}

.footer-left p {
    font-size: 14px;
    color: #a0aec0;
    margin-bottom: 4px;
}

.verification-box {
    text-align: center;
    padding: 20px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    backdrop-filter: blur(10px);
}

.verification-box h6 {
    font-size: 12px;
    font-weight: 600;
    color: #e2e8f0;
    margin-bottom: 12px;
    text-transform: uppercase;
}

.signature-line {
    font-size: 16px;
    font-weight: 600;
    color: white;
    border-bottom: 2px solid #4a5568;
    padding-bottom: 8px;
    margin-bottom: 8px;
    min-width: 200px;
}

.verification-box small {
    font-size: 12px;
    color: #a0aec0;
}

.qr-section {
    text-align: center;
}

.qr-code {
    width: 80px;
    height: 80px;
    background: white;
    border-radius: 8px;
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

.footer-right small {
    font-size: 12px;
    color: #a0aec0;
}

/* Print Styles */
@media print {
    body {
        background: none;
        padding: 0;
    }
    
    .document-container {
        box-shadow: none;
        border-radius: 0;
    }
    
    .summary-cards {
        grid-template-columns: repeat(3, 1fr);
    }
    
    .details-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .footer-content {
        grid-template-columns: 1fr auto 1fr;
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
    
    .footer-content {
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
            "plugins": ["lists", "table", "link", "image", "code", "template", "visualblocks"],
            "toolbar_config": "full",
            "custom_css": True,
            "responsive_design": True,
            "print_optimized": True,
            "last_edit": datetime.now(timezone.utc).isoformat(),
            "changelog": ["Modern card-based layout", "Interactive timeline", "Enhanced typography", "Responsive design", "Print optimization"]
        }
        
        metadata_v2 = {
            "title": "Kapu Ellenőrzési Jegyzőkönyv v2.0",
            "description": "Modern, interaktív sablon kártya alapú elrendezéssel, idővonalas megjelenítéssel és reszponzív design-nal",
            "page_size": "A4",
            "orientation": "portrait",
            "include_qr_code": True,
            "qr_code_position": "footer_right",
            "include_logo": True,
            "logo_position": "header_left",
            "responsive": True,
            "print_optimized": True
        }
        
        version_2 = wysiwyg_service.create_template_version(
            template_id=base_template.id,
            user_id=admin_user.id,
            html_content=html_v2,
            css_styles=css_v2,
            editor_content=editor_content_v2,
            version_type="major",
            version_name="Modern interaktív sablon",
            metadata=metadata_v2
        )
        
        print(f"✅ Version 2.0 created (ID: {version_2.id})")
        
        # Create preview sessions
        print("\n🖼️ Creating preview sessions...")
        
        sample_data = {
            "document_title": "Kapu Ellenőrzési Jegyzőkönyv - Demo",
            "document_number": "GATE-2025-001",
            "organization": {
                "name": "GarageReg Demo Kft.",
                "address": "1234 Budapest, Demo utca 1.",
                "tax_number": "12345678-1-23",
                "registration_number": "Cg.01-09-123456",
                "logo_url": "/assets/logo.png"
            },
            "gate": {
                "id": "GATE-DEMO-001",
                "name": "Főbejárat Automatikus Kapu",
                "location": "Budapest, Fő utca 1., főbejárat",
                "type": "Automatikus tolókapu CAME BXV-04"
            },
            "inspector": {
                "name": "Demo Ellenőr Péter",
                "display_name": "Demo Ellenőr Péter",
                "license_number": "ELL-DEMO-12345"
            },
            "inspection": {
                "id": 1,
                "type": "Éves biztonsági ellenőrzés",
                "date": "2025-01-02",
                "result": "Megfelelő",
                "start_time": "09:00",
                "end_time": "10:30",
                "notes": "Az ellenőrzés során minden komponens megfelelő állapotban volt. A kapu mechanikai és elektromos rendszerei kifogástalanul működnek."
            },
            "generation": {
                "date": datetime.now(timezone.utc),
                "generated_by": "WYSIWYG Demo System",
                "document_number": "GATE-2025-001"
            }
        }
        
        # Create preview for version 2.0
        preview_session_2 = wysiwyg_service.create_preview_session(
            version_id=version_2.id,
            user_id=admin_user.id,
            sample_data=sample_data,
            preview_options={"format": "pdf", "quality": "high"}
        )
        
        print(f"✅ Preview session created for v2.0: {preview_session_2.session_token}")
        
        # Create preview for version 1.1
        preview_session_1_1 = wysiwyg_service.create_preview_session(
            version_id=version_1_1.id,
            user_id=admin_user.id,
            sample_data=sample_data,
            preview_options={"format": "pdf", "quality": "high"}
        )
        
        print(f"✅ Preview session created for v1.1: {preview_session_1_1.session_token}")
        
        # Test version comparison
        print("\n🔍 Testing version comparison...")
        
        comparison = wysiwyg_service.compare_template_versions(
            version_id_1=version_1.id,
            version_id_2=version_2.id
        )
        
        print(f"✅ Version comparison completed between v{comparison['version_1']['version_number']} and v{comparison['version_2']['version_number']}")
        
        # Get template changelog
        print("\n📋 Getting template changelog...")
        
        changelog = wysiwyg_service.get_template_changelog(
            template_id=base_template.id,
            limit=10
        )
        
        print(f"✅ Found {len(changelog)} changes in template history")
        
        for change in changelog:
            print(f"   - {change.change_timestamp.strftime('%Y-%m-%d %H:%M')} | {change.change_type.value} | {change.change_summary}")
        
        # Get version history
        print("\n📚 Getting version history...")
        
        versions = wysiwyg_service.get_template_versions(
            template_id=base_template.id,
            include_drafts=True,
            limit=10
        )
        
        print(f"✅ Found {len(versions)} versions:")
        for v in versions:
            status_icon = "🟢" if v.status == TemplateStatus.PUBLISHED else "🟡" if v.status == TemplateStatus.DRAFT else "⚪"
            current_icon = "⭐" if v.is_current else "  "
            print(f"   {status_icon} {current_icon} v{v.version_number} - {v.version_name} ({v.status.value}) - {v.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        # Summary
        print(f"\n🎉 WYSIWYG Template System Demo Complete!")
        print(f"📋 Template ID: {base_template.id}")
        print(f"📈 Versions created: {len(versions)}")
        print(f"🖼️ Preview sessions: 2")
        print(f"📝 Change log entries: {len(changelog)}")
        print(f"✨ Features demonstrated:")
        print(f"   - Template versioning with semantic versioning")
        print(f"   - WYSIWYG editor content management")
        print(f"   - CSS styling with progressive enhancement")
        print(f"   - Preview generation (HTML/PDF/Image)")
        print(f"   - Change tracking and audit logging")
        print(f"   - Version comparison and diff generation")
        print(f"   - Template publishing workflow")
        print(f"   - Sample data injection for previews")
        
        print(f"\n🚀 Test the system:")
        print(f"   1. Access preview URLs:")
        print(f"      - V1.1 Preview: /api/admin/wysiwyg-templates/preview/{preview_session_1_1.session_token}/html")
        print(f"      - V2.0 Preview: /api/admin/wysiwyg-templates/preview/{preview_session_2.session_token}/html")
        print(f"   2. Use WYSIWYG Editor: /admin/templates/{base_template.id}/versions/{version_2.id}")
        print(f"   3. View changelog: GET /api/admin/wysiwyg-templates/templates/{base_template.id}/changelog")
        print(f"   4. Compare versions: GET /api/admin/wysiwyg-templates/versions/{version_1.id}/compare/{version_2.id}")
        
        return {
            "template_id": base_template.id,
            "versions": [v.id for v in versions],
            "preview_sessions": [preview_session_1_1.session_token, preview_session_2.session_token],
            "changelog_entries": len(changelog)
        }
        
    except Exception as e:
        print(f"❌ Error creating WYSIWYG template demo: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()


if __name__ == "__main__":
    result = asyncio.run(create_sample_wysiwyg_templates())
    if result:
        print(f"\n✅ Demo completed successfully!")
        print(f"Template ID: {result['template_id']}")
        print(f"Created versions: {result['versions']}")
        print(f"Preview tokens: {result['preview_sessions']}")
    else:
        print(f"\n❌ Demo failed!")