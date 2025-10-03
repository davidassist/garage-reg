"""
Very simple script to create default document templates in the database
"""
import sys
import os
import sqlite3

def create_default_templates():
    """Create default document templates using sqlite3"""
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), "garagereg.db")
    
    # Read template files
    templates_dir = os.path.join(os.path.dirname(__file__), "app", "templates", "documents")
    
    templates = [
        {
            "name": "Alapértelmezett üzemeltetési napló",
            "document_type": "OPERATIONAL_LOG",
            "template_path": "operational_log.html",
            "title": "Üzemeltetési napló",
            "description": "Szabványos üzemeltetési napló sablon EU megfelelőséggel",
            "is_active": 1,
            "version": "1.0"
        },
        {
            "name": "Alapértelmezett karbantartási jegyzőkönyv", 
            "document_type": "MAINTENANCE_PROTOCOL",
            "template_path": "maintenance_protocol.html",
            "title": "Karbantartási jegyzőkönyv",
            "description": "Karbantartási munkálatok dokumentálásához használt sablon",
            "is_active": 1,
            "version": "1.0"
        },
        {
            "name": "Alapértelmezett munkalap",
            "document_type": "WORK_SHEET",
            "template_path": "work_sheet.html", 
            "title": "Munkalap",
            "description": "Ellenőrzési munkalapok és checklista dokumentálásához",
            "is_active": 1,
            "version": "1.0"
        }
    ]
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for template_data in templates:
            # Check if template already exists
            cursor.execute("""
                SELECT id FROM document_templates 
                WHERE document_type = ? AND name = ?
            """, (template_data["document_type"], template_data["name"]))
            
            existing = cursor.fetchone()
            if existing:
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
            
            # Insert template record
            cursor.execute("""
                INSERT INTO document_templates 
                (name, document_type, version, title, description, html_template, 
                 page_size, orientation, include_qr_code, qr_code_position, qr_code_size,
                 include_logo, logo_position, is_active, is_default, org_id,
                 created_at, updated_at)
                VALUES 
                (?, ?, ?, ?, ?, ?,
                 'A4', 'portrait', 1, 'top_right', 100,
                 1, 'top_left', ?, 0, 1,
                 datetime('now'), datetime('now'))
            """, (
                template_data["name"],
                template_data["document_type"],
                template_data["version"],
                template_data["title"],
                template_data["description"],
                html_template,
                template_data["is_active"]
            ))
            
            print(f"Created template: {template_data['name']}")
        
        conn.commit()
        print("All default templates created successfully!")
        
    except Exception as e:
        print(f"Error creating templates: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_default_templates()