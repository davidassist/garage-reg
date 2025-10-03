#!/usr/bin/env python3
"""
Simple GarageReg Database Seed Script
Creates sample organization with 5 gates and 2 templates.

Usage:
    python scripts/seed_simple.py [--org-name="Custom Org"] [--gates=N]
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import models
from app.models import Base
from app.models.auth import User, Role, Permission, RoleAssignment
from app.models.organization import Organization, Client, Site, Building, Gate
from app.models.inspections import ChecklistTemplate, ChecklistItem

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./garagereg.db")


class SimpleSeeder:
    """Simple database seeder with minimal sample data."""
    
    def __init__(self, database_url: str = DATABASE_URL):
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def seed_all(self, org_name: str = "GarageReg Demo Corp", num_gates: int = 5):
        """Seed database with sample data."""
        print("Starting database seeding...")
        print(f"Organization: {org_name}")
        print(f"Number of gates: {num_gates}")
        
        session = self.SessionLocal()
        
        try:
            # Create organization
            print("Creating organization...")
            org = Organization(
                name=org_name,
                display_name=org_name,
                description=f"Sample organization: {org_name}",
                website="https://garagereg.com",
                email="admin@garagereg.com",
                phone="+1-555-0123",
                address_line_1="123 Business Ave",
                city="Demo City",
                state="Demo State",
                postal_code="12345",
                country="United States",
                is_active=True
            )
            session.add(org)
            session.flush()
            
            # Create permissions
            print("Creating permissions...")
            permissions_data = [
                {"name": "gate.read", "codename": "gate_read", "description": "View gate information", "resource": "gate", "action": "read", "scope": "organization"},
                {"name": "gate.update", "codename": "gate_update", "description": "Update gate information", "resource": "gate", "action": "update", "scope": "organization"},
                {"name": "gate.maintain", "codename": "gate_maintain", "description": "Perform gate maintenance", "resource": "gate", "action": "maintain", "scope": "organization"},
                {"name": "inspection.create", "codename": "inspection_create", "description": "Create inspections", "resource": "inspection", "action": "create", "scope": "organization"},
                {"name": "inspection.read", "codename": "inspection_read", "description": "View inspections", "resource": "inspection", "action": "read", "scope": "organization"},
                {"name": "system.admin", "codename": "system_admin", "description": "Full system administration", "resource": "system", "action": "admin", "scope": "global"},
            ]
            
            permissions = []
            for perm_data in permissions_data:
                permission = Permission(**perm_data)
                session.add(permission)
                permissions.append(permission)
            session.flush()
            
            # Create roles
            print("Creating roles...")
            admin_role = Role(
                name="admin",
                display_name="Administrator", 
                description="Full system access"
            )
            tech_role = Role(
                name="technician",
                display_name="Technician",
                description="Maintenance and inspections"
            )
            
            admin_role.permissions = permissions
            tech_role.permissions = permissions[:5]  # Limited permissions
            
            session.add(admin_role)
            session.add(tech_role)
            session.flush()
            
            # Create users
            print("Creating users...")
            admin_user = User(
                organization_id=org.id,
                username="admin",
                email="admin@garagereg.com",
                first_name="System",
                last_name="Administrator",
                password_hash="$2b$12$dummy.hash.for.demo.purposes.only",
                is_active=True,
                email_verified=True
            )
            
            tech_user = User(
                organization_id=org.id,
                username="tech1",
                email="tech1@garagereg.com", 
                first_name="Bob",
                last_name="Technician",
                password_hash="$2b$12$dummy.hash.for.demo.purposes.only",
                is_active=True,
                email_verified=True
            )
            
            session.add(admin_user)
            session.add(tech_user)
            session.flush()
            
            # Assign roles
            admin_assignment = RoleAssignment(
                user_id=admin_user.id,
                role_id=admin_role.id,
                scope_type="organization",
                scope_id=org.id,
                assigned_at=datetime.utcnow(),
                is_active=True,
                org_id=org.id
            )
            
            tech_assignment = RoleAssignment(
                user_id=tech_user.id,
                role_id=tech_role.id,
                scope_type="organization", 
                scope_id=org.id,
                assigned_at=datetime.utcnow(),
                is_active=True,
                org_id=org.id
            )
            
            session.add(admin_assignment)
            session.add(tech_assignment)
            session.flush()
            
            # Create site and building
            print("Creating site and building...")
            site = Site(
                organization_id=org.id,
                name="headquarters",
                display_name="Corporate Headquarters",
                description="Main corporate facility",
                site_code="HQ001",
                site_type="corporate",
                address_line_1="100 Corporate Blvd",
                city="Demo City",
                state="Demo State",
                postal_code="12345",
                country="United States",
                is_active=True
            )
            session.add(site)
            session.flush()
            
            building = Building(
                site_id=site.id,
                name="main_building",
                display_name="Main Office Building",
                description="Primary office building with parking",
                building_code="MAIN",
                building_type="office",
                floors=3,
                units=30,
                year_built=2020,
                org_id=org.id,
                is_active=True
            )
            session.add(building)
            session.flush()
            
            # Create gates
            print(f"Creating {num_gates} gates...")
            gate_types = ["automatic", "manual", "barrier", "sliding", "swing"]
            manufacturers = ["FAAC", "BFT", "Came", "Nice", "LiftMaster"]
            
            gates = []
            for i in range(num_gates):
                gate_type = gate_types[i % len(gate_types)]
                manufacturer = manufacturers[i % len(manufacturers)]
                
                gate = Gate(
                    building_id=building.id,
                    name=f"gate_{i+1:02d}",
                    display_name=f"Gate {i+1:02d} - {gate_type.title()}",
                    description=f"Sample {gate_type} gate #{i+1}",
                    gate_code=f"G{i+1:03d}",
                    gate_type=gate_type,
                    manufacturer=manufacturer,
                    model=f"Model-{gate_type.upper()}-{i+1:02d}",
                    serial_number=f"SN{manufacturer[:3].upper()}{i+1:06d}",
                    installation_date=datetime.utcnow() - timedelta(days=365-i*30),
                    installer=f"{manufacturer} Installation Team",
                    warranty_end_date=datetime.utcnow() + timedelta(days=365+i*30),
                    width_cm=300 + i*50,
                    height_cm=200 + i*20,
                    weight_kg=500 + i*100,
                    max_opening_width_cm=(300 + i*50) - 20,
                    opening_speed_cm_per_sec=15 + i*2,
                    closing_speed_cm_per_sec=12 + i*2,
                    safety_features=["photocells", "pressure_sensors"],
                    access_control_type="keypad" if i % 2 == 0 else "card_reader",
                    power_supply_voltage=230 if i % 2 == 0 else 24,
                    power_consumption_watts=150 + i*25,
                    backup_battery_hours=8 + i,
                    operating_temperature_min=-20,
                    operating_temperature_max=60,
                    ip_rating="IP54",
                    certifications=["CE", "FCC"],
                    status="active",
                    last_maintenance_date=datetime.utcnow() - timedelta(days=30),
                    next_maintenance_date=datetime.utcnow() + timedelta(days=90),
                    maintenance_interval_days=90,
                    is_active=True,
                    org_id=org.id,
                    settings={"auto_close_delay": 10, "obstruction_sensitivity": "medium"}
                )
                
                session.add(gate)
                gates.append(gate)
            
            session.flush()
            
            # Create 2 checklist templates
            print("Creating 2 checklist templates...")
            
            # Template 1: Daily Inspection
            daily_template = ChecklistTemplate(
                name="daily_inspection",
                description="Daily operational inspection checklist",
                category="routine",
                version="1.0",
                template_type="inspection",
                applicable_gate_types=["automatic", "barrier"],
                estimated_duration_minutes=15,
                recommended_frequency_days=1,
                required_tools=["flashlight", "multimeter"],
                required_skills=["basic_electrical"],
                org_id=org.id,
                is_active=True
            )
            session.add(daily_template)
            session.flush()
            
            # Daily template items
            daily_items = [
                {
                    "title": "Visual inspection of gate structure",
                    "description": "Check for visible damage, wear, or corrosion",
                    "instructions": "Examine the gate structure for cracks, rust, or loose parts",
                    "item_type": "visual_check",
                    "category": "structure",
                    "order_index": 1,
                    "is_required": True,
                    "requires_photo": True,
                    "requires_note": False
                },
                {
                    "title": "Test gate opening/closing",
                    "description": "Verify smooth operation",
                    "instructions": "Operate the gate through a complete cycle",
                    "item_type": "operation_test", 
                    "category": "operation",
                    "order_index": 2,
                    "is_required": True,
                    "requires_photo": False,
                    "requires_note": True
                }
            ]
            
            for item_data in daily_items:
                item = ChecklistItem(
                    template_id=daily_template.id,
                    org_id=org.id,
                    is_active=True,
                    **item_data
                )
                session.add(item)
            
            # Template 2: Monthly Maintenance
            monthly_template = ChecklistTemplate(
                name="monthly_maintenance",
                description="Monthly maintenance checklist",
                category="maintenance",
                version="1.0",
                template_type="maintenance", 
                applicable_gate_types=["automatic", "barrier", "sliding"],
                estimated_duration_minutes=60,
                recommended_frequency_days=30,
                required_tools=["grease_gun", "cleaning_supplies"],
                required_skills=["mechanical", "electrical"],
                org_id=org.id,
                is_active=True
            )
            session.add(monthly_template)
            session.flush()
            
            # Monthly template items
            monthly_items = [
                {
                    "title": "Lubricate moving parts",
                    "description": "Apply lubricant to hinges and tracks",
                    "instructions": "Use manufacturer-specified grease",
                    "item_type": "maintenance_task",
                    "category": "lubrication",
                    "order_index": 1,
                    "is_required": True,
                    "requires_photo": True,
                    "requires_note": True
                },
                {
                    "title": "Check electrical connections",
                    "description": "Inspect connections for tightness",
                    "instructions": "Tighten loose connections and clean terminals",
                    "item_type": "electrical_check",
                    "category": "electrical",
                    "order_index": 2,
                    "is_required": True,
                    "requires_photo": True,
                    "requires_note": True
                }
            ]
            
            for item_data in monthly_items:
                item = ChecklistItem(
                    template_id=monthly_template.id,
                    org_id=org.id,
                    is_active=True,
                    **item_data
                )
                session.add(item)
            
            # Commit all changes
            session.commit()
            
            print(f"\nDatabase seeding completed successfully!")
            print(f"Summary:")
            print(f"  - Organization: {org.name}")
            print(f"  - Users: 2 (admin, tech1)")
            print(f"  - Gates: {num_gates}")
            print(f"  - Templates: 2 (daily, monthly)")
            print(f"  - Roles: 2 (admin, technician)")
            print(f"  - Permissions: {len(permissions)}")
            
            print(f"\nSample login credentials:")
            print(f"  Admin: admin / password")
            print(f"  Technician: tech1 / password")
            
        except Exception as e:
            print(f"Seeding failed: {e}")
            session.rollback()
            raise
        finally:
            session.close()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Seed GarageReg database")
    parser.add_argument("--org-name", default="GarageReg Demo Corp", help="Organization name")
    parser.add_argument("--gates", type=int, default=5, help="Number of gates")
    parser.add_argument("--db-url", default=DATABASE_URL, help="Database URL")
    
    args = parser.parse_args()
    
    try:
        seeder = SimpleSeeder(args.db_url)
        seeder.seed_all(org_name=args.org_name, num_gates=args.gates)
        print("\nSeeding completed successfully!")
    except Exception as e:
        print(f"ERROR: Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()