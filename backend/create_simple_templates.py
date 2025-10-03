"""
Simple script to create default document templates in the database without using relationships
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

def create_default_templates():
    """Create default document templates using raw SQL"""
    
    # Create engine and session
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    # Read template files
    templates_dir = os.path.join(os.path.dirname(__file__), "app", "templates", "documents")
    
    templates = [
        {
            "name": "Alapértelmezett üzemeltetési napló",
            "document_type": "OPERATIONAL_LOG",
            "template_path": "operational_log.html",
            "title": "Üzemeltetési napló",
            "description": "Szabványos üzemeltetési napló sablon EU megfelelőséggel",
            "is_active": True,
            "version": "1.0"
        },
        {
            "name": "Alapértelmezett karbantartási jegyzőkönyv", 
            "document_type": "MAINTENANCE_PROTOCOL",
            "template_path": "maintenance_protocol.html",
            "title": "Karbantartási jegyzőkönyv",
            "description": "Karbantartási munkálatok dokumentálásához használt sablon",
            "is_active": True,
            "version": "1.0"
        },
        {
            "name": "Alapértelmezett munkalap",
            "document_type": "WORK_SHEET",
            "template_path": "work_sheet.html", 
            "title": "Munkalap",
            "description": "Ellenőrzési munkalapok és checklista dokumentálásához",
            "is_active": True,
            "version": "1.0"
        }
    ]
    
    try:
        for template_data in templates:
            # Check if template already exists
            existing_check = db.execute(text("""
                SELECT id FROM document_templates 
                WHERE document_type = :document_type AND name = :name
            """), {
                "document_type": template_data["document_type"],
                "name": template_data["name"]
            }).fetchone()
            
            if existing_check:
                print(f"Template already exists: {template_data['name']}")
                continue
                
            # Read template content
            template_file_path = os.path.join(templates_dir, template_data["template_path"])
            if os.path.exists(template_file_path):
                with open(template_file_path, 'r', encoding='utf-8') as f:
                    html_template = f.read()
            else:
                print(f"Warning: Template file not found: {template_file_path}")
                html_template = "<html><body>Template not found</body></html>"
            
            # Insert template record using raw SQL
            db.execute(text("""
                INSERT INTO document_templates 
                (name, document_type, version, title, description, html_template, 
                 page_size, orientation, include_qr_code, qr_code_position, qr_code_size,
                 include_logo, logo_position, is_active, is_default, org_id,
                 created_at, updated_at)
                VALUES 
                (:name, :document_type, :version, :title, :description, :html_template,
                 'A4', 'portrait', true, 'top_right', 100,
                 true, 'top_left', :is_active, false, 1,
                 NOW(), NOW())
            """), {
                "name": template_data["name"],
                "document_type": template_data["document_type"],
                "version": template_data["version"],
                "title": template_data["title"],
                "description": template_data["description"],
                "html_template": html_template,
                "is_active": template_data["is_active"]
            })
            
            print(f"Created template: {template_data['name']}")
        
        db.commit()
        print("All default templates created successfully!")
        
    except Exception as e:
        print(f"Error creating templates: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_default_templates()