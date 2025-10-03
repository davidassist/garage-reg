#!/usr/bin/env python3
"""
ERD Generation Script for GarageReg Database Schema

This script generates an Entity-Relationship Diagram (ERD) from the 
complete GarageReg database schema and exports it to /docs/erd.png.

Uses SQLAlchemy metadata to create a visual representation of the database schema.
"""

import os
import sys
import logging
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

try:
    from app.core.config import settings
    import app.models  # This loads all models and creates Base
    from app.models import Base  # Now we can import Base
    from sqlalchemy import inspect
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure all dependencies are installed")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_erd():
    """Generate ERD from the database schema using matplotlib."""
    
    # Ensure docs directory exists
    docs_dir = Path(__file__).parent.parent / "docs"
    docs_dir.mkdir(exist_ok=True)
    
    # Output file path
    erd_file = docs_dir / "erd.png"
    
    try:
        logger.info("Generating ERD from SQLAlchemy metadata...")
        
        # Create the ERD visualization
        create_erd_visualization(str(erd_file))
        
        logger.info(f"✅ ERD generated successfully: {erd_file}")
        
        # Print summary of the schema
        print_schema_summary()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to generate ERD: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_erd_visualization(output_file):
    """Create a visual ERD using matplotlib."""
    
    # Get all tables from SQLAlchemy metadata
    tables = Base.metadata.tables
    
    # Define table categories with colors
    table_categories = {
        "Organization": {"tables": ["organizations", "clients", "sites", "buildings", "gates"], "color": "#E3F2FD"},
        "Components": {"tables": ["gate_components", "parts"], "color": "#F3E5F5"},
        "Maintenance": {"tables": ["maintenance_plans", "maintenance_jobs", "reminders"], "color": "#E8F5E8"},
        "Inspections": {"tables": ["checklist_templates", "checklist_items", "inspections", "inspection_items", "measurements"], "color": "#FFF3E0"},
        "Work Management": {"tables": ["tickets", "work_orders", "work_order_items", "part_usages"], "color": "#FFEBEE"},
        "Auth & RBAC": {"tables": ["users", "roles", "permissions", "role_assignments", "role_permissions", "webauthn_credentials", "totp_secrets", "api_keys"], "color": "#F1F8E9"},
        "Documents": {"tables": ["documents", "media_objects", "integrations", "webhooks"], "color": "#E0F2F1"},
        "Inventory": {"tables": ["warehouses", "inventory_items", "stock_movements"], "color": "#FAFAFA"},
        "Audit": {"tables": ["audit_logs", "events"], "color": "#FFF8E1"}
    }
    
    # Create figure with multiple subplots for categories
    fig = plt.figure(figsize=(20, 16))
    fig.suptitle("GarageReg Database Schema - Entity Relationship Diagram", fontsize=20, fontweight='bold')
    
    # Create a grid layout
    rows = 3
    cols = 3
    
    category_names = list(table_categories.keys())
    
    for i, (category, info) in enumerate(table_categories.items()):
        if i < 9:  # Only show first 9 categories
            ax = fig.add_subplot(rows, cols, i + 1)
            ax.set_title(category, fontsize=14, fontweight='bold', pad=20)
            
            # Draw tables in this category
            y_pos = 0.9
            for table_name in info["tables"]:
                if table_name in tables:
                    table = tables[table_name]
                    
                    # Create a box for the table
                    box = FancyBboxPatch(
                        (0.1, y_pos - 0.15), 0.8, 0.12,
                        boxstyle="round,pad=0.02",
                        facecolor=info["color"],
                        edgecolor="black",
                        linewidth=1
                    )
                    ax.add_patch(box)
                    
                    # Add table name
                    ax.text(0.5, y_pos - 0.08, table_name, 
                           horizontalalignment='center', 
                           verticalalignment='center',
                           fontsize=10, fontweight='bold')
                    
                    # Add column count
                    column_count = len(table.columns)
                    ax.text(0.5, y_pos - 0.12, f"({column_count} columns)", 
                           horizontalalignment='center', 
                           verticalalignment='center',
                           fontsize=8, style='italic')
                    
                    y_pos -= 0.2
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
    
    # Add overall statistics in a text box
    stats_text = generate_statistics_text(tables)
    fig.text(0.02, 0.02, stats_text, fontsize=10, 
             bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.7))
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    logger.info(f"ERD saved to: {output_file}")

def generate_statistics_text(tables):
    """Generate statistics text for the ERD."""
    
    total_tables = len(tables)
    total_columns = sum(len(table.columns) for table in tables.values())
    total_indexes = sum(len(table.indexes) for table in tables.values())
    total_foreign_keys = sum(
        len([col for col in table.columns if col.foreign_keys]) 
        for table in tables.values()
    )
    
    return f"""Database Statistics:
📊 Total Tables: {total_tables}
📈 Total Columns: {total_columns}
🔗 Foreign Keys: {total_foreign_keys}
🚀 Indexes: {total_indexes}

Key Features:
• Multi-tenant architecture
• Soft delete pattern
• Comprehensive RBAC
• Audit logging
• WebAuthn/TOTP 2FA"""

def print_schema_summary():
    """Print a summary of the database schema."""
    
    # Base is already imported at module level
    pass  # Models are already loaded
    
    print("\n" + "="*60)
    print("📊 GarageReg Database Schema Summary")
    print("="*60)
    
    # Count models by category
    categories = {
        "Organization Hierarchy": ["Organization", "Client", "Site", "Building", "Gate"],
        "Components & Maintenance": ["GateComponent", "MaintenancePlan", "MaintenanceJob", "Reminder"],
        "Inspections & Quality": ["ChecklistTemplate", "ChecklistItem", "Inspection", "InspectionItem", "Measurement"],
        "Work Management": ["Ticket", "WorkOrder", "WorkOrderItem", "Part", "PartUsage"],
        "Authentication & RBAC": ["User", "Role", "Permission", "RoleAssignment", "WebAuthnCredential", "TOTPSecret", "APIKey"],
        "Documents & Media": ["Document", "MediaObject", "Integration", "Webhook"],
        "Inventory & Audit": ["Warehouse", "InventoryItem", "StockMovement", "AuditLog", "Event"]
    }
    
    total_models = 0
    for category, models in categories.items():
        print(f"\n🔹 {category}: {len(models)} models")
        for model in models:
            print(f"   • {model}")
        total_models += len(models)
    
    print(f"\n📈 Total Models: {total_models}")
    print(f"📊 Total Tables: {len(Base.metadata.tables)}")
    
    # Key features
    print(f"\n🎯 Key Features:")
    print(f"   • Multi-tenant architecture with org_id filtering")
    print(f"   • Soft delete pattern with is_deleted/deleted_at")
    print(f"   • Comprehensive indexing for performance")
    print(f"   • RBAC with scope-based permissions")
    print(f"   • Audit logging and event tracking")
    print(f"   • WebAuthn/TOTP 2FA support")
    print(f"   • Document management with S3 integration")
    print(f"   • Full maintenance lifecycle management")
    
    print("="*60)

if __name__ == "__main__":
    print("🚀 Starting ERD generation for GarageReg database...")
    
    success = generate_erd()
    
    if success:
        print("\n✅ ERD generation completed successfully!")
        print("📁 File saved to: docs/erd.png")
    else:
        print("\n❌ ERD generation failed!")
        sys.exit(1)