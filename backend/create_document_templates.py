"""
Script to create default document templates in the database
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.documents import DocumentTemplate, DocumentType
from sqlalchemy.orm import Session

def create_default_templates():
    """Create default document templates"""
    
    # Read template files
    templates_dir = os.path.join(os.path.dirname(__file__), "app", "templates", "documents")
    
    templates = [
        {
            "name": "Alapértelmezett üzemeltetési napló",
            "document_type": DocumentType.OPERATIONAL_LOG,
            "template_path": "operational_log.html",
            "description": "Szabványos üzemeltetési napló sablon EU megfelelőséggel",
            "is_active": True,
            "version": "1.0"
        },
        {
            "name": "Alapértelmezett karbantartási jegyzőkönyv", 
            "document_type": DocumentType.MAINTENANCE_PROTOCOL,
            "template_path": "maintenance_protocol.html",
            "description": "Karbantartási munkálatok dokumentálásához használt sablon",
            "is_active": True,
            "version": "1.0"
        },
        {
            "name": "Alapértelmezett munkalap",
            "document_type": DocumentType.WORK_SHEET,
            "template_path": "work_sheet.html", 
            "description": "Ellenőrzési munkalapok és checklista dokumentálásához",
            "is_active": True,
            "version": "1.0"
        }
    ]
    
    db = next(get_db())
    
    try:
        for template_data in templates:
            # Check if template already exists
            existing = db.query(DocumentTemplate).filter(
                DocumentTemplate.document_type == template_data["document_type"],
                DocumentTemplate.name == template_data["name"]
            ).first()
            
            if existing:
                print(f"Template already exists: {template_data['name']}")
                continue
                
            # Read template content
            template_file_path = os.path.join(templates_dir, template_data["template_path"])
            if os.path.exists(template_file_path):
                with open(template_file_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
            else:
                print(f"Warning: Template file not found: {template_file_path}")
                template_content = ""
            
            # Create template record
            template = DocumentTemplate(
                name=template_data["name"],
                document_type=template_data["document_type"],
                template_content=template_content,
                template_path=template_data["template_path"],
                description=template_data["description"],
                is_active=template_data["is_active"],
                version=template_data["version"]
            )
            
            db.add(template)
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