#!/usr/bin/env python3
"""
GarageReg Database Seed Script
Creates sample organization with gates, users, and templates.

Usage:
    python scripts/seed.py [--reset] [--org-name="Custom Org"] [--gates=N]
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

# Add the backend directory to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Database setup
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

# Import models
from app.models import Base
from app.models.auth import User, Role, Permission, RoleAssignment
from app.models.organization import Organization, Client, Site, Building, Gate
from app.models.inspections import ChecklistTemplate, ChecklistItem
from app.models.maintenance import MaintenancePlan

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./garagereg.db")


class DatabaseSeeder:
    """Database seeding utility with comprehensive sample data."""
    
    def __init__(self, database_url: str = DATABASE_URL):
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session: Session = None
    
    def __enter__(self):
        self.session = self.SessionLocal()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.session.close()
    
    def reset_database(self):
        """Drop all tables and recreate them."""
        print("🗑️  Dropping all tables...")
        Base.metadata.drop_all(bind=self.engine)
        print("🏗️  Creating all tables...")
        Base.metadata.create_all(bind=self.engine)
        print("✅ Database reset completed!")
    
    def seed_permissions(self) -> List[Permission]:
        """Create basic permissions."""
        print("Creating permissions...")
        
        permissions_data = [
            # User management
            {"name": "user.create", "description": "Create new users"},
            {"name": "user.read", "description": "View user information"},
            {"name": "user.update", "description": "Update user information"},
            {"name": "user.delete", "description": "Delete users"},
            
            # Organization management
            {"name": "org.manage", "description": "Manage organization settings"},
            {"name": "org.view", "description": "View organization information"},
            
            # Gate management
            {"name": "gate.create", "description": "Create new gates"},
            {"name": "gate.read", "description": "View gate information"},
            {"name": "gate.update", "description": "Update gate information"},
            {"name": "gate.delete", "description": "Delete gates"},
            {"name": "gate.maintain", "description": "Perform gate maintenance"},
            
            # Inspection management
            {"name": "inspection.create", "description": "Create inspections"},
            {"name": "inspection.read", "description": "View inspections"},
            {"name": "inspection.update", "description": "Update inspections"},
            {"name": "inspection.delete", "description": "Delete inspections"},
            
            # Maintenance management
            {"name": "maintenance.schedule", "description": "Schedule maintenance"},
            {"name": "maintenance.perform", "description": "Perform maintenance"},
            {"name": "maintenance.view", "description": "View maintenance records"},
            
            # Reporting
            {"name": "report.view", "description": "View reports"},
            {"name": "report.export", "description": "Export reports"},
            
            # System administration
            {"name": "system.admin", "description": "Full system administration"},
        ]
        
        permissions = []
        for perm_data in permissions_data:
            permission = Permission(**perm_data)
            self.session.add(permission)
            permissions.append(permission)
        
        self.session.commit()
        print(f"✅ Created {len(permissions)} permissions")
        return permissions
    
    def seed_roles(self, permissions: List[Permission]) -> List[Role]:
        """Create roles with associated permissions."""
        print("👥 Creating roles...")
        
        # Map permission names for easy lookup
        perm_map = {p.name: p for p in permissions}
        
        roles_data = [
            {
                "name": "admin",
                "display_name": "System Administrator",
                "description": "Full system access",
                "permissions": list(perm_map.values())  # All permissions
            },
            {
                "name": "manager",
                "display_name": "Facility Manager",
                "description": "Manage gates, inspections, and maintenance",
                "permissions": [
                    perm_map["org.view"], perm_map["gate.create"], perm_map["gate.read"],
                    perm_map["gate.update"], perm_map["gate.maintain"], perm_map["inspection.create"],
                    perm_map["inspection.read"], perm_map["inspection.update"], perm_map["maintenance.schedule"],
                    perm_map["maintenance.view"], perm_map["report.view"], perm_map["report.export"]
                ]
            },
            {
                "name": "technician",
                "display_name": "Maintenance Technician",
                "description": "Perform maintenance and inspections",
                "permissions": [
                    perm_map["gate.read"], perm_map["gate.maintain"], perm_map["inspection.create"],
                    perm_map["inspection.read"], perm_map["inspection.update"], perm_map["maintenance.perform"],
                    perm_map["maintenance.view"]
                ]
            },
            {
                "name": "viewer",
                "display_name": "Read-Only User",
                "description": "View-only access to system",
                "permissions": [
                    perm_map["org.view"], perm_map["gate.read"], perm_map["inspection.read"],
                    perm_map["maintenance.view"], perm_map["report.view"]
                ]
            }
        ]
        
        roles = []
        for role_data in roles_data:
            permissions = role_data.pop("permissions")
            role = Role(**role_data)
            role.permissions = permissions
            self.session.add(role)
            roles.append(role)
        
        self.session.commit()
        print(f"✅ Created {len(roles)} roles")
        return roles
    
    def seed_organization(self, org_name: str = "GarageReg Demo Corp") -> Organization:
        """Create sample organization."""
        print(f"🏢 Creating organization: {org_name}")
        
        org = Organization(
            name=org_name,
            display_name=org_name,
            description=f"Sample organization for {org_name}",
            org_code=org_name.upper().replace(" ", "_")[:10],
            website="https://garagereg.com",
            email="admin@garagereg.com",
            phone="+1-555-0123",
            address_line_1="123 Business Ave",
            city="Demo City",
            state="Demo State",
            postal_code="12345",
            country="United States",
            is_active=True,
            settings={
                "timezone": "UTC",
                "currency": "USD",
                "language": "en",
                "theme": "default"
            }
        )
        
        self.session.add(org)
        self.session.commit()
        print(f"✅ Created organization: {org.name} (ID: {org.id})")
        return org
    
    def seed_users(self, organization: Organization, roles: List[Role]) -> List[User]:
        """Create sample users."""
        print("👤 Creating users...")
        
        # Map roles for easy access
        role_map = {r.name: r for r in roles}
        
        users_data = [
            {
                "username": "admin",
                "email": "admin@garagereg.com",
                "first_name": "System",
                "last_name": "Administrator",
                "display_name": "Admin User",
                "role": "admin",
                "is_active": True,
                "email_verified": True
            },
            {
                "username": "manager1",
                "email": "manager@garagereg.com",
                "first_name": "Jane",
                "last_name": "Manager",
                "display_name": "Jane Manager",
                "role": "manager",
                "is_active": True,
                "email_verified": True
            },
            {
                "username": "tech1",
                "email": "tech1@garagereg.com",
                "first_name": "Bob",
                "last_name": "Technician",
                "display_name": "Bob Tech",
                "role": "technician",
                "is_active": True,
                "email_verified": True
            },
            {
                "username": "tech2",
                "email": "tech2@garagereg.com",
                "first_name": "Alice",
                "last_name": "Engineer",
                "display_name": "Alice Engineer",
                "role": "technician",
                "is_active": True,
                "email_verified": True
            },
            {
                "username": "viewer1",
                "email": "viewer@garagereg.com",
                "first_name": "John",
                "last_name": "Observer",
                "display_name": "John Observer",
                "role": "viewer",
                "is_active": True,
                "email_verified": True
            }
        ]
        
        users = []
        for user_data in users_data:
            role_name = user_data.pop("role")
            user = User(
                organization_id=organization.id,
                password_hash="$2b$12$dummy.hash.for.demo.purposes.only",  # Demo hash
                **user_data
            )
            self.session.add(user)
            self.session.flush()  # Get the user ID
            
            # Assign role
            role_assignment = RoleAssignment(
                user_id=user.id,
                role_id=role_map[role_name].id,
                scope_type="organization",
                scope_id=organization.id,
                assigned_by_user_id=None,  # System assigned
                assigned_at=datetime.utcnow(),
                is_active=True,
                org_id=organization.id
            )
            self.session.add(role_assignment)
            users.append(user)
        
        self.session.commit()
        print(f"✅ Created {len(users)} users")
        return users
    
    def seed_sites_and_buildings(self, organization: Organization) -> List[Site]:
        """Create sample sites and buildings."""
        print("🏗️  Creating sites and buildings...")
        
        sites_data = [
            {
                "name": "headquarters",
                "display_name": "Corporate Headquarters",
                "description": "Main corporate facility with executive parking",
                "site_code": "HQ001",
                "site_type": "corporate",
                "address_line_1": "100 Corporate Blvd",
                "city": "Demo City",
                "state": "Demo State",
                "postal_code": "12345",
                "country": "United States",
                "buildings": [
                    {
                        "name": "main_building",
                        "display_name": "Main Office Building",
                        "description": "Primary office building with underground parking",
                        "building_code": "MAIN",
                        "building_type": "office",
                        "floors": 5,
                        "units": 50,
                        "year_built": 2020,
                    },
                    {
                        "name": "parking_structure",
                        "display_name": "Parking Structure A",
                        "description": "Multi-level parking structure",
                        "building_code": "PARK_A",
                        "building_type": "parking",
                        "floors": 3,
                        "units": 200,
                        "year_built": 2021,
                    }
                ]
            },
            {
                "name": "warehouse_complex",
                "display_name": "Distribution Warehouse Complex",
                "description": "Warehouse and distribution facility",
                "site_code": "WH001",
                "site_type": "warehouse",
                "address_line_1": "500 Industrial Pkwy",
                "city": "Demo City",
                "state": "Demo State",
                "postal_code": "12346",
                "country": "United States",
                "buildings": [
                    {
                        "name": "warehouse_main",
                        "display_name": "Main Warehouse",
                        "description": "Primary storage and distribution center",
                        "building_code": "WH_MAIN",
                        "building_type": "warehouse",
                        "floors": 1,
                        "units": 20,
                        "year_built": 2018,
                    }
                ]
            }
        ]
        
        sites = []
        for site_data in sites_data:
            buildings_data = site_data.pop("buildings", [])
            site = Site(
                organization_id=organization.id,
                is_active=True,
                **site_data
            )
            self.session.add(site)
            self.session.flush()  # Get site ID
            
            # Add buildings
            for building_data in buildings_data:
                building = Building(
                    site_id=site.id,
                    org_id=organization.id,
                    is_active=True,
                    **building_data
                )
                self.session.add(building)
            
            sites.append(site)
        
        self.session.commit()
        print(f"✅ Created {len(sites)} sites with buildings")
        return sites
    
    def seed_gates(self, organization: Organization, sites: List[Site], num_gates: int = 5) -> List[Gate]:
        """Create sample gates."""
        print(f"🚪 Creating {num_gates} gates...")
        
        # Get buildings for gate placement
        buildings = []
        for site in sites:
            site_buildings = self.session.query(Building).filter_by(site_id=site.id).all()
            buildings.extend(site_buildings)
        
        if not buildings:
            print("❌ No buildings found for gate placement")
            return []
        
        gate_types = ["automatic", "manual", "barrier", "sliding", "swing"]
        manufacturers = ["FAAC", "BFT", "Came", "Nice", "Automatic Systems"]
        
        gates = []
        for i in range(num_gates):
            building = buildings[i % len(buildings)]
            gate_type = gate_types[i % len(gate_types)]
            manufacturer = manufacturers[i % len(manufacturers)]
            
            gate = Gate(
                building_id=building.id,
                name=f"gate_{i+1:02d}",
                display_name=f"Gate {i+1:02d} - {gate_type.title()}",
                description=f"Sample {gate_type} gate for demonstration purposes",
                gate_code=f"G{i+1:03d}",
                gate_type=gate_type,
                manufacturer=manufacturer,
                model=f"Model-{gate_type.upper()}-{i+1:02d}",
                serial_number=f"SN{manufacturer[:3].upper()}{i+1:06d}",
                installation_date=datetime.utcnow() - timedelta(days=365-i*30),  # Stagger installation dates
                installer=f"{manufacturer} Installation Team",
                warranty_end_date=datetime.utcnow() + timedelta(days=365+i*30),  # Future warranty dates
                width_cm=300 + i*50,  # Varying widths
                height_cm=200 + i*20,  # Varying heights
                weight_kg=500 + i*100,  # Varying weights
                max_opening_width_cm=(300 + i*50) - 20,
                opening_speed_cm_per_sec=15 + i*2,
                closing_speed_cm_per_sec=12 + i*2,
                safety_features=["photocells", "pressure_sensors", "emergency_stop"],
                access_control_type="keypad" if i % 2 == 0 else "card_reader",
                power_supply_voltage=230 if i % 2 == 0 else 24,
                power_consumption_watts=150 + i*25,
                backup_battery_hours=8 + i,
                operating_temperature_min=-20 - i*5,
                operating_temperature_max=60 + i*5,
                ip_rating=f"IP{54 + i if 54 + i <= 68 else 68}",
                certifications=["CE", "FCC", "UL"] if i % 2 == 0 else ["CE", "RoHS"],
                status="active",
                last_maintenance_date=datetime.utcnow() - timedelta(days=30+i*10),
                next_maintenance_date=datetime.utcnow() + timedelta(days=90-i*10),
                maintenance_interval_days=90,
                is_active=True,
                org_id=organization.id,
                settings={
                    "auto_close_delay": 10 + i*5,
                    "obstruction_sensitivity": "medium" if i % 2 == 0 else "high",
                    "remote_monitoring": True,
                    "maintenance_alerts": True
                }
            )
            
            self.session.add(gate)
            gates.append(gate)
        
        self.session.commit()
        print(f"✅ Created {len(gates)} gates")
        return gates
    
    def seed_checklist_templates(self, organization: Organization) -> List[ChecklistTemplate]:
        """Create sample inspection checklist templates."""
        print("📋 Creating checklist templates...")
        
        templates_data = [
            {
                "name": "daily_inspection",
                "description": "Daily operational inspection checklist",
                "category": "routine",
                "version": "1.0",
                "template_type": "inspection",
                "applicable_gate_types": ["automatic", "barrier", "sliding"],
                "estimated_duration_minutes": 15,
                "recommended_frequency_days": 1,
                "required_tools": ["flashlight", "multimeter", "cleaning_cloth"],
                "required_skills": ["basic_electrical", "visual_inspection"],
                "items": [
                    {
                        "title": "Visual inspection of gate structure",
                        "description": "Check for any visible damage, wear, or corrosion",
                        "instructions": "Examine the entire gate structure for cracks, rust, or loose components",
                        "item_type": "visual_check",
                        "category": "structure",
                        "order_index": 1,
                        "is_required": True,
                        "requires_photo": True,
                        "requires_note": False
                    },
                    {
                        "title": "Test gate opening/closing operation",
                        "description": "Verify smooth opening and closing operation",
                        "instructions": "Operate the gate through a complete cycle and note any irregularities",
                        "item_type": "operation_test",
                        "category": "operation",
                        "order_index": 2,
                        "is_required": True,
                        "requires_photo": False,
                        "requires_note": True
                    },
                    {
                        "title": "Check safety sensors",
                        "description": "Test all photocells and pressure sensors",
                        "instructions": "Trigger each safety sensor and verify proper response",
                        "item_type": "safety_test",
                        "category": "safety",
                        "order_index": 3,
                        "is_required": True,
                        "requires_photo": False,
                        "requires_note": True
                    },
                    {
                        "title": "Measure opening speed",
                        "description": "Time the gate opening cycle",
                        "instructions": "Use a stopwatch to measure complete opening time",
                        "item_type": "measurement",
                        "category": "performance",
                        "order_index": 4,
                        "is_required": False,
                        "requires_measurement": True,
                        "measurement_unit": "seconds",
                        "measurement_min": 8.0,
                        "measurement_max": 25.0
                    }
                ]
            },
            {
                "name": "monthly_maintenance",
                "description": "Comprehensive monthly maintenance checklist",
                "category": "maintenance",
                "version": "1.0", 
                "template_type": "maintenance",
                "applicable_gate_types": ["automatic", "barrier", "sliding", "swing"],
                "estimated_duration_minutes": 60,
                "recommended_frequency_days": 30,
                "required_tools": ["multimeter", "grease_gun", "cleaning_supplies", "torque_wrench"],
                "required_skills": ["mechanical", "electrical", "lubrication"],
                "items": [
                    {
                        "title": "Lubricate moving parts",
                        "description": "Apply appropriate lubricant to hinges, tracks, and moving components",
                        "instructions": "Use manufacturer-specified grease for all moving parts",
                        "item_type": "maintenance_task",
                        "category": "lubrication",
                        "order_index": 1,
                        "is_required": True,
                        "requires_photo": True,
                        "requires_note": True
                    },
                    {
                        "title": "Check electrical connections",
                        "description": "Inspect all electrical connections for tightness and corrosion",
                        "instructions": "Tighten loose connections and clean corroded terminals",
                        "item_type": "electrical_check",
                        "category": "electrical",
                        "order_index": 2,
                        "is_required": True,
                        "requires_photo": True,
                        "requires_note": True
                    },
                    {
                        "title": "Test backup power system",
                        "description": "Verify battery backup system operation",
                        "instructions": "Disconnect main power and test gate operation on battery",
                        "item_type": "system_test",
                        "category": "power",
                        "order_index": 3,
                        "is_required": True,
                        "requires_photo": False,
                        "requires_note": True
                    }
                ]
            }
        ]
        
        templates = []
        for template_data in templates_data:
            items_data = template_data.pop("items", [])
            template = ChecklistTemplate(
                org_id=organization.id,
                is_active=True,
                **template_data
            )
            self.session.add(template)
            self.session.flush()  # Get template ID
            
            # Add checklist items
            for item_data in items_data:
                item = ChecklistItem(
                    template_id=template.id,
                    org_id=organization.id,
                    is_active=True,
                    **item_data
                )
                self.session.add(item)
            
            templates.append(template)
        
        self.session.commit()
        print(f"✅ Created {len(templates)} checklist templates")
        return templates
    
    def seed_all(self, org_name: str = "GarageReg Demo Corp", num_gates: int = 5, reset: bool = False):
        """Seed the entire database with sample data."""
        print("Starting database seeding...")
        print(f"Organization: {org_name}")
        print(f"Number of gates: {num_gates}")
        
        if reset:
            self.reset_database()
        
        # Seed in dependency order
        permissions = self.seed_permissions()
        roles = self.seed_roles(permissions)
        organization = self.seed_organization(org_name)
        users = self.seed_users(organization, roles)
        sites = self.seed_sites_and_buildings(organization)
        gates = self.seed_gates(organization, sites, num_gates)
        templates = self.seed_checklist_templates(organization)
        
        print(f"\n✅ Database seeding completed successfully!")
        print(f"📊 Summary:")
        print(f"  - Organization: {organization.name}")
        print(f"  - Users: {len(users)}")
        print(f"  - Sites: {len(sites)}")
        print(f"  - Gates: {len(gates)}")
        print(f"  - Templates: {len(templates)}")
        print(f"  - Roles: {len(roles)}")
        print(f"  - Permissions: {len(permissions)}")
        
        print(f"\n👤 Sample login credentials:")
        print(f"  Admin: admin / password (Full access)")
        print(f"  Manager: manager1 / password (Management access)")
        print(f"  Technician: tech1 / password (Maintenance access)")
        print(f"  Viewer: viewer1 / password (Read-only access)")


def main():
    """Main function with CLI argument parsing."""
    parser = argparse.ArgumentParser(description="Seed GarageReg database with sample data")
    parser.add_argument("--reset", action="store_true", help="Reset database before seeding")
    parser.add_argument("--org-name", default="GarageReg Demo Corp", help="Organization name")
    parser.add_argument("--gates", type=int, default=5, help="Number of gates to create")
    parser.add_argument("--db-url", default=DATABASE_URL, help="Database URL")
    
    args = parser.parse_args()
    
    try:
        with DatabaseSeeder(args.db_url) as seeder:
            seeder.seed_all(
                org_name=args.org_name,
                num_gates=args.gates,
                reset=args.reset
            )
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()