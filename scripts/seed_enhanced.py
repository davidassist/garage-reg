#!/usr/bin/env python3
"""
Enhanced GarageReg Database Seed Script

Creates comprehensive sample data for GarageReg system:
- Sample organization with 5 gates
- 2 checklist templates (maintenance & inspection)
- Users with different roles
- Maintenance plans and schedules

Usage:
    python scripts/seed_enhanced.py [options]
    
Options:
    --reset                     Drop and recreate database
    --org-name="Custom Name"    Organization name (default: "Sample Garage Corp")
    --gates=5                   Number of gates to create (default: 5)
    --users=10                  Number of users to create (default: 10)
    --confirm                   Skip confirmation prompts
    --verbose                   Detailed output
"""

import os
import sys
import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add backend to Python path
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

# Import utilities
from werkzeug.security import generate_password_hash


class EnhancedDatabaseSeeder:
    """Enhanced database seeder with comprehensive sample data."""
    
    def __init__(self, database_url: str = None, verbose: bool = False):
        self.database_url = database_url or os.getenv("DATABASE_URL", "sqlite:///./garagereg.db")
        self.verbose = verbose
        self.engine = create_engine(self.database_url, echo=verbose)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session: Session = None
        
        # Sample data configurations
        self.gate_types = ["sliding", "swing", "rolling", "barrier", "sectional"]
        self.gate_manufacturers = ["CAME", "BFT", "FAAC", "Nice", "DITEC", "V2", "Beninca"]
        self.user_roles = ["admin", "manager", "technician", "operator", "viewer"]
        
    def __enter__(self):
        self.session = self.SessionLocal()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.session.close()
    
    def log(self, message: str, level: str = "info"):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if level == "error":
            print(f"❌ [{timestamp}] {message}")
        elif level == "warning":
            print(f"⚠️  [{timestamp}] {message}")
        elif level == "success":
            print(f"✅ [{timestamp}] {message}")
        else:
            print(f"ℹ️  [{timestamp}] {message}")
    
    def reset_database(self):
        """Drop all tables and recreate them."""
        self.log("Dropping all tables...")
        Base.metadata.drop_all(bind=self.engine)
        self.log("Creating all tables...")
        Base.metadata.create_all(bind=self.engine)
        self.log("Database reset completed!", "success")
    
    def seed_permissions(self) -> List[Permission]:
        """Create comprehensive permission set."""
        self.log("Creating permissions...")
        
        permissions_data = [
            # User management
            {"name": "user.create", "description": "Create new users", "category": "user_management"},
            {"name": "user.read", "description": "View user information", "category": "user_management"},
            {"name": "user.update", "description": "Update user information", "category": "user_management"},
            {"name": "user.delete", "description": "Delete users", "category": "user_management"},
            {"name": "user.assign_roles", "description": "Assign roles to users", "category": "user_management"},
            
            # Organization management
            {"name": "org.manage", "description": "Manage organization settings", "category": "organization"},
            {"name": "org.view", "description": "View organization information", "category": "organization"},
            {"name": "org.sites.manage", "description": "Manage organization sites", "category": "organization"},
            
            # Gate management
            {"name": "gate.create", "description": "Create new gates", "category": "gate_management"},
            {"name": "gate.read", "description": "View gate information", "category": "gate_management"},
            {"name": "gate.update", "description": "Update gate information", "category": "gate_management"},
            {"name": "gate.delete", "description": "Delete gates", "category": "gate_management"},
            {"name": "gate.operate", "description": "Operate gates (open/close)", "category": "gate_operations"},
            {"name": "gate.maintain", "description": "Perform gate maintenance", "category": "gate_operations"},
            
            # Inspection management
            {"name": "inspection.create", "description": "Create inspections", "category": "inspections"},
            {"name": "inspection.read", "description": "View inspections", "category": "inspections"},
            {"name": "inspection.update", "description": "Update inspections", "category": "inspections"},
            {"name": "inspection.delete", "description": "Delete inspections", "category": "inspections"},
            {"name": "inspection.templates", "description": "Manage inspection templates", "category": "inspections"},
            
            # Maintenance management
            {"name": "maintenance.schedule", "description": "Schedule maintenance", "category": "maintenance"},
            {"name": "maintenance.perform", "description": "Perform maintenance", "category": "maintenance"},
            {"name": "maintenance.view", "description": "View maintenance records", "category": "maintenance"},
            {"name": "maintenance.plans", "description": "Manage maintenance plans", "category": "maintenance"},
            
            # Reporting and analytics
            {"name": "report.view", "description": "View reports", "category": "reporting"},
            {"name": "report.export", "description": "Export reports", "category": "reporting"},
            {"name": "analytics.view", "description": "View analytics dashboards", "category": "reporting"},
            
            # System administration
            {"name": "system.admin", "description": "Full system administration", "category": "system"},
            {"name": "system.config", "description": "Configure system settings", "category": "system"},
            {"name": "system.backup", "description": "Manage system backups", "category": "system"},
            {"name": "system.logs", "description": "View system logs", "category": "system"},
        ]
        
        permissions = []
        for perm_data in permissions_data:
            permission = Permission(**perm_data)
            self.session.add(permission)
            permissions.append(permission)
        
        try:
            self.session.commit()
            self.log(f"Created {len(permissions)} permissions", "success")
        except IntegrityError as e:
            self.session.rollback()
            self.log(f"Some permissions already exist: {e}", "warning")
            # Try to get existing permissions
            permissions = self.session.query(Permission).all()
        
        return permissions
    
    def seed_roles(self, permissions: List[Permission]) -> List[Role]:
        """Create roles with appropriate permissions."""
        self.log("Creating roles...")
        
        # Create permission lookup
        perm_map = {p.name: p for p in permissions}
        
        roles_config = [
            {
                "name": "admin",
                "display_name": "System Administrator", 
                "description": "Full system access",
                "permissions": [p.name for p in permissions]  # All permissions
            },
            {
                "name": "manager",
                "display_name": "Site Manager",
                "description": "Manage sites and operations",
                "permissions": [
                    "org.view", "org.sites.manage",
                    "gate.create", "gate.read", "gate.update", "gate.operate",
                    "inspection.create", "inspection.read", "inspection.update", "inspection.templates",
                    "maintenance.schedule", "maintenance.view", "maintenance.plans",
                    "report.view", "report.export", "analytics.view",
                    "user.read", "user.update"
                ]
            },
            {
                "name": "technician", 
                "display_name": "Maintenance Technician",
                "description": "Perform maintenance and inspections",
                "permissions": [
                    "gate.read", "gate.operate", "gate.maintain",
                    "inspection.create", "inspection.read", "inspection.update",
                    "maintenance.perform", "maintenance.view",
                    "report.view"
                ]
            },
            {
                "name": "operator",
                "display_name": "Gate Operator", 
                "description": "Basic gate operations",
                "permissions": [
                    "gate.read", "gate.operate",
                    "inspection.read",
                    "maintenance.view"
                ]
            },
            {
                "name": "viewer",
                "display_name": "Read-Only User",
                "description": "View-only access",
                "permissions": [
                    "org.view", "gate.read", "inspection.read", 
                    "maintenance.view", "report.view"
                ]
            }
        ]
        
        roles = []
        for role_config in roles_config:
            # Create role
            role = Role(
                name=role_config["name"],
                display_name=role_config["display_name"],
                description=role_config["description"]
            )
            self.session.add(role)
            
            # Add permissions to role
            for perm_name in role_config["permissions"]:
                if perm_name in perm_map:
                    role.permissions.append(perm_map[perm_name])
            
            roles.append(role)
        
        try:
            self.session.commit()
            self.log(f"Created {len(roles)} roles", "success")
        except IntegrityError as e:
            self.session.rollback()
            self.log(f"Some roles already exist: {e}", "warning")
            roles = self.session.query(Role).all()
        
        return roles
    
    def seed_organization(self, org_name: str = "Sample Garage Corp") -> Organization:
        """Create sample organization."""
        self.log(f"Creating organization: {org_name}")
        
        organization = Organization(
            name=org_name,
            display_name=org_name,
            description=f"Sample garage management organization",
            contact_person="John Manager",
            email="manager@samplegarage.com",
            phone="+1-555-0123",
            address_line_1="123 Industrial Drive",
            city="Technology City",
            state="Tech State", 
            postal_code="12345",
            country="United States",
            is_active=True,
            settings={
                "timezone": "UTC",
                "business_hours": {
                    "monday": {"open": "08:00", "close": "17:00"},
                    "tuesday": {"open": "08:00", "close": "17:00"},
                    "wednesday": {"open": "08:00", "close": "17:00"},
                    "thursday": {"open": "08:00", "close": "17:00"},
                    "friday": {"open": "08:00", "close": "17:00"},
                    "weekend": {"open": "09:00", "close": "15:00"}
                },
                "maintenance_schedule": "weekly",
                "notification_preferences": {
                    "email_enabled": True,
                    "sms_enabled": False,
                    "maintenance_reminders": True
                }
            }
        )
        
        self.session.add(organization)
        self.session.commit()
        self.log("Organization created successfully", "success")
        
        return organization
    
    def seed_sites_and_gates(self, organization: Organization, num_gates: int = 5) -> List[Gate]:
        """Create sample sites and gates."""
        self.log(f"Creating sites and {num_gates} gates...")
        
        # Create client
        client = Client(
            org_id=organization.id,
            name="Main Client",
            display_name="Primary Client Organization",
            type="corporate",
            contact_person="Jane Client",
            email="client@example.com", 
            phone="+1-555-0456"
        )
        self.session.add(client)
        
        # Create site
        site = Site(
            client_id=client.id,
            name="Main Industrial Site",
            display_name="Primary Industrial Complex",
            description="Main industrial facility with multiple gates",
            site_code="IND-001",
            address_line_1="456 Factory Road",
            city="Industrial City",
            state="Tech State",
            postal_code="12346",
            country="United States",
            latitude="40.7128",
            longitude="-74.0060",
            manager_name="Site Manager",
            contact_phone="+1-555-0789",
            contact_email="site@example.com"
        )
        self.session.add(site)
        
        # Create building
        building = Building(
            site_id=site.id,
            name="Main Building",
            display_name="Primary Building Complex",
            description="Main building with gate access points"
        )
        self.session.add(building)
        self.session.commit()
        
        # Create gates
        gates = []
        gate_names = [
            "Main Entrance Gate",
            "Loading Dock Gate", 
            "Emergency Exit Gate",
            "Personnel Access Gate",
            "Vehicle Parking Gate"
        ]
        
        for i in range(num_gates):
            gate_name = gate_names[i] if i < len(gate_names) else f"Gate {i+1}"
            gate_type = random.choice(self.gate_types)
            manufacturer = random.choice(self.gate_manufacturers)
            
            gate = Gate(
                building_id=building.id,
                name=gate_name,
                display_name=gate_name,
                description=f"Automated {gate_type} gate - {gate_name.lower()}",
                gate_code=f"GT-{i+1:03d}",
                gate_type=gate_type,
                manufacturer=manufacturer,
                model=f"{manufacturer}-{random.randint(100, 999)}",
                serial_number=f"SN{random.randint(100000, 999999)}",
                installation_date=datetime.now() - timedelta(days=random.randint(30, 730)),
                width_cm=random.randint(300, 800),
                height_cm=random.randint(200, 400),
                weight_kg=random.randint(100, 1000),
                material=random.choice(["steel", "aluminum", "composite"]),
                max_opening_cycles_per_day=random.randint(50, 500),
                operating_voltage=random.choice([12, 24, 230]),
                power_consumption_w=random.randint(100, 800),
                current_status="operational",
                last_maintenance_date=datetime.now() - timedelta(days=random.randint(7, 90)),
                next_maintenance_date=datetime.now() + timedelta(days=random.randint(7, 30)),
                cycle_count=random.randint(1000, 50000),
                operating_hours=random.randint(500, 8760),
                settings={
                    "auto_close_delay": random.randint(30, 300),
                    "safety_sensors": True,
                    "remote_control": True,
                    "manual_override": True,
                    "maintenance_alerts": True
                }
            )
            
            self.session.add(gate)
            gates.append(gate)
        
        self.session.commit()
        self.log(f"Created {len(gates)} gates", "success")
        
        return gates
    
    def seed_users(self, organization: Organization, roles: List[Role], num_users: int = 10) -> List[User]:
        """Create sample users with various roles."""
        self.log(f"Creating {num_users} users...")
        
        # Create role lookup
        role_map = {r.name: r for r in roles}
        
        # Predefined admin user
        admin_users = [
            {
                "username": "admin",
                "email": "admin@garagereg.com",
                "first_name": "System",
                "last_name": "Administrator", 
                "password": "admin123",
                "role": "admin",
                "phone": "+1-555-0001"
            },
            {
                "username": "manager1",
                "email": "manager@garagereg.com", 
                "first_name": "Site",
                "last_name": "Manager",
                "password": "manager123",
                "role": "manager",
                "phone": "+1-555-0002"
            },
            {
                "username": "tech1",
                "email": "tech@garagereg.com",
                "first_name": "Lead", 
                "last_name": "Technician",
                "password": "tech123", 
                "role": "technician",
                "phone": "+1-555-0003"
            }
        ]
        
        users = []
        
        # Create predefined users
        for user_data in admin_users:
            user = User(
                org_id=organization.id,
                username=user_data["username"],
                email=user_data["email"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                display_name=f"{user_data['first_name']} {user_data['last_name']}",
                password_hash=generate_password_hash(user_data["password"]),
                phone=user_data["phone"],
                email_verified=True,
                is_active=True
            )
            self.session.add(user)
            
            # Assign role
            if user_data["role"] in role_map:
                role_assignment = RoleAssignment(
                    user=user,
                    role=role_map[user_data["role"]],
                    assigned_by_user_id=None,  # System assigned
                    assigned_at=datetime.now()
                )
                self.session.add(role_assignment)
            
            users.append(user)
        
        # Generate additional random users
        first_names = ["John", "Jane", "Mike", "Sarah", "David", "Lisa", "Chris", "Anna", "Robert", "Emily"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        
        for i in range(len(admin_users), num_users):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"{first_name.lower()}.{last_name.lower()}{i}"
            email = f"{username}@garagereg.com"
            role_name = random.choice(self.user_roles)
            
            user = User(
                org_id=organization.id,
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                display_name=f"{first_name} {last_name}",
                password_hash=generate_password_hash("password123"),
                phone=f"+1-555-{1000+i:04d}",
                job_title=random.choice(["Technician", "Operator", "Supervisor", "Manager"]),
                email_verified=True,
                is_active=random.choice([True, True, True, False])  # Mostly active
            )
            self.session.add(user)
            
            # Assign role
            if role_name in role_map:
                role_assignment = RoleAssignment(
                    user=user,
                    role=role_map[role_name],
                    assigned_by_user_id=1,  # Assigned by admin
                    assigned_at=datetime.now()
                )
                self.session.add(role_assignment)
            
            users.append(user)
        
        self.session.commit()
        self.log(f"Created {len(users)} users", "success")
        
        return users
    
    def seed_checklist_templates(self) -> List[ChecklistTemplate]:
        """Create 2 comprehensive checklist templates."""
        self.log("Creating 2 checklist templates...")
        
        templates_config = [
            {
                "name": "Monthly Maintenance Checklist",
                "description": "Comprehensive monthly maintenance inspection for all gate types",
                "category": "maintenance",
                "template_type": "maintenance",
                "version": "1.0",
                "estimated_duration_minutes": 60,
                "recommended_frequency_days": 30,
                "applicable_gate_types": ["sliding", "swing", "rolling", "barrier", "sectional"],
                "required_tools": ["multimeter", "lubricant", "torque_wrench", "safety_gear"],
                "required_skills": ["electrical_basics", "mechanical_maintenance"],
                "items": [
                    {"title": "Visual Inspection", "description": "Check for physical damage, wear, or corrosion", "order_index": 1, "item_type": "visual", "is_required": True},
                    {"title": "Lubrication Points", "description": "Lubricate all moving parts and pivot points", "order_index": 2, "item_type": "maintenance", "is_required": True},
                    {"title": "Safety Sensors Test", "description": "Test all safety sensors and emergency stops", "order_index": 3, "item_type": "safety", "is_required": True},
                    {"title": "Motor Operation", "description": "Check motor operation and current draw", "order_index": 4, "item_type": "electrical", "is_required": True},
                    {"title": "Control System Check", "description": "Verify control system responsiveness", "order_index": 5, "item_type": "electronic", "is_required": True},
                    {"title": "Opening/Closing Cycles", "description": "Test 5 complete open/close cycles", "order_index": 6, "item_type": "operational", "is_required": True},
                    {"title": "Battery Backup Test", "description": "Test backup power system (if applicable)", "order_index": 7, "item_type": "electrical", "is_required": False},
                    {"title": "Remote Control Test", "description": "Test all remote control devices", "order_index": 8, "item_type": "operational", "is_required": True},
                    {"title": "Noise Level Check", "description": "Assess operational noise levels", "order_index": 9, "item_type": "diagnostic", "is_required": False},
                    {"title": "Documentation Update", "description": "Update maintenance log and cycle counter", "order_index": 10, "item_type": "documentation", "is_required": True}
                ]
            },
            {
                "name": "Safety Inspection Checklist", 
                "description": "Quarterly safety inspection focusing on safety systems and compliance",
                "category": "safety",
                "template_type": "inspection",
                "version": "1.0", 
                "estimated_duration_minutes": 45,
                "recommended_frequency_days": 90,
                "applicable_gate_types": ["sliding", "swing", "rolling", "barrier", "sectional"],
                "required_tools": ["measuring_tape", "force_gauge", "safety_equipment"],
                "required_skills": ["safety_inspection", "compliance_knowledge"],
                "items": [
                    {"title": "Emergency Stop Systems", "description": "Verify all emergency stop mechanisms function properly", "order_index": 1, "item_type": "safety", "is_required": True},
                    {"title": "Photocell Sensors", "description": "Test photocell beam interruption and alignment", "order_index": 2, "item_type": "safety", "is_required": True},
                    {"title": "Pressure Sensors", "description": "Test ground pressure/contact sensors", "order_index": 3, "item_type": "safety", "is_required": True},
                    {"title": "Force Adjustment", "description": "Measure and adjust closing force limits", "order_index": 4, "item_type": "safety", "is_required": True},
                    {"title": "Manual Release", "description": "Test manual release mechanism operation", "order_index": 5, "item_type": "safety", "is_required": True},
                    {"title": "Warning Signals", "description": "Test audible and visual warning signals", "order_index": 6, "item_type": "safety", "is_required": True},
                    {"title": "Access Control", "description": "Verify access control systems and authorization", "order_index": 7, "item_type": "security", "is_required": True},
                    {"title": "Structural Integrity", "description": "Inspect mounting points and structural components", "order_index": 8, "item_type": "structural", "is_required": True},
                    {"title": "Compliance Labels", "description": "Check safety labels and compliance markings", "order_index": 9, "item_type": "compliance", "is_required": True},
                    {"title": "Safety Documentation", "description": "Review and update safety documentation", "order_index": 10, "item_type": "documentation", "is_required": True}
                ]
            }
        ]
        
        templates = []
        for template_config in templates_config:
            # Create template
            items_data = template_config.pop("items")
            template = ChecklistTemplate(**template_config)
            self.session.add(template)
            self.session.flush()  # Get template ID
            
            # Create checklist items
            for item_data in items_data:
                item = ChecklistItem(
                    template_id=template.id,
                    **item_data
                )
                self.session.add(item)
            
            templates.append(template)
        
        self.session.commit()
        self.log(f"Created {len(templates)} checklist templates", "success")
        
        return templates
    
    def seed_maintenance_plans(self, gates: List[Gate], templates: List[ChecklistTemplate]) -> List[MaintenancePlan]:
        """Create maintenance plans for gates."""
        self.log("Creating maintenance plans...")
        
        plans = []
        for gate in gates:
            # Create monthly maintenance plan
            monthly_plan = MaintenancePlan(
                gate_id=gate.id,
                name=f"Monthly Maintenance - {gate.name}",
                description=f"Regular monthly maintenance schedule for {gate.name}",
                maintenance_type="preventive",
                frequency_days=30,
                estimated_duration_hours=1.0,
                is_active=True,
                checklist_template_id=templates[0].id if templates else None,  # Maintenance template
                settings={
                    "auto_schedule": True,
                    "advance_notice_days": 7,
                    "required_technician_level": "certified",
                    "weather_dependent": False
                }
            )
            self.session.add(monthly_plan)
            plans.append(monthly_plan)
            
            # Create quarterly safety inspection plan  
            quarterly_plan = MaintenancePlan(
                gate_id=gate.id,
                name=f"Safety Inspection - {gate.name}",
                description=f"Quarterly safety inspection for {gate.name}",
                maintenance_type="inspection",
                frequency_days=90,
                estimated_duration_hours=0.75,
                is_active=True,
                checklist_template_id=templates[1].id if len(templates) > 1 else None,  # Safety template
                settings={
                    "auto_schedule": True,
                    "advance_notice_days": 14,
                    "required_technician_level": "certified",
                    "compliance_required": True
                }
            )
            self.session.add(quarterly_plan)
            plans.append(quarterly_plan)
        
        self.session.commit()
        self.log(f"Created {len(plans)} maintenance plans", "success")
        
        return plans
    
    def seed_all(self, 
                org_name: str = "Sample Garage Corp",
                num_gates: int = 5, 
                num_users: int = 10,
                reset_db: bool = False) -> Dict[str, Any]:
        """Seed complete database with all sample data."""
        
        if reset_db:
            self.reset_database()
        
        self.log("Starting comprehensive database seeding...")
        
        # Seed in dependency order
        permissions = self.seed_permissions()
        roles = self.seed_roles(permissions)
        organization = self.seed_organization(org_name)
        gates = self.seed_sites_and_gates(organization, num_gates)
        users = self.seed_users(organization, roles, num_users)
        templates = self.seed_checklist_templates()
        maintenance_plans = self.seed_maintenance_plans(gates, templates)
        
        self.log("Database seeding completed successfully!", "success")
        
        return {
            "organization": organization,
            "gates": gates,
            "users": users, 
            "permissions": permissions,
            "roles": roles,
            "templates": templates,
            "maintenance_plans": maintenance_plans,
            "summary": {
                "gates_created": len(gates),
                "users_created": len(users),
                "templates_created": len(templates),
                "maintenance_plans_created": len(maintenance_plans)
            }
        }


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Enhanced GarageReg Database Seed Script",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--database-url",
        help="Database URL (default: sqlite:///./garagereg.db)"
    )
    
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop and recreate database before seeding"
    )
    
    parser.add_argument(
        "--org-name",
        default="Sample Garage Corp", 
        help="Organization name (default: Sample Garage Corp)"
    )
    
    parser.add_argument(
        "--gates",
        type=int,
        default=5,
        help="Number of gates to create (default: 5)"
    )
    
    parser.add_argument(
        "--users", 
        type=int,
        default=10,
        help="Number of users to create (default: 10)"
    )
    
    parser.add_argument(
        "--confirm",
        action="store_true", 
        help="Skip confirmation prompts"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Detailed output"
    )
    
    args = parser.parse_args()
    
    # Confirmation for reset
    if args.reset and not args.confirm:
        response = input("⚠️  This will DELETE all existing data. Continue? (yes/no): ")
        if response.lower() != "yes":
            print("❌ Operation cancelled")
            sys.exit(1)
    
    # Run seeding
    try:
        with EnhancedDatabaseSeeder(args.database_url, args.verbose) as seeder:
            result = seeder.seed_all(
                org_name=args.org_name,
                num_gates=args.gates, 
                num_users=args.users,
                reset_db=args.reset
            )
            
            print("\\n" + "="*50)
            print("🎉 SEEDING COMPLETED SUCCESSFULLY!")
            print("="*50)
            print(f"📊 Summary:")
            print(f"   Organization: {result['organization'].name}")
            print(f"   Gates: {result['summary']['gates_created']}")
            print(f"   Users: {result['summary']['users_created']}")
            print(f"   Templates: {result['summary']['templates_created']}") 
            print(f"   Maintenance Plans: {result['summary']['maintenance_plans_created']}")
            print("\\n✅ Database ready for application use!")
            
            # Show sample login credentials
            print("\\n🔑 Sample Login Credentials:")
            print("   Admin: username=admin, password=admin123")
            print("   Manager: username=manager1, password=manager123") 
            print("   Technician: username=tech1, password=tech123")
            
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()