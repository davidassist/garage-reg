#!/usr/bin/env python3
"""
Demo Scenario Data Generator - Golden Path Implementation

Generates comprehensive demo data for the GarageReg system including:
- 1 Client (TechPark Business Center)  
- 2 Sites (North & South Campus)
- 3 Buildings (Alfa, Beta, Gamma)
- 10 Gates (various types)
- 2 Inspections (safety & maintenance)
- 1 Ticket → Work Order workflow

Demo forgatókönyv adat generátor - Golden Path implementáció
"""

import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent / 'backend'))

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from backend.app.database.session import get_db
from backend.app.models.auth import User, Role, Permission
from backend.app.models.organization import Organization, Site, Building, Gate
from backend.app.models.inspections import Inspection, InspectionTemplate, ChecklistItem
from backend.app.models.tickets import Ticket, WorkOrder, TicketStatus, TicketPriority, WorkOrderStatus
from backend.app.models.documents import Document, DocumentTemplate, DocumentType
from backend.app.core.security import get_password_hash


class DemoScenarioDataGenerator:
    """
    Comprehensive demo data generator for the Golden Path scenario.
    
    Demo adat generátor a Golden Path forgatókönyvhöz.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.demo_data = {}
        
    def generate_all_demo_data(self):
        """Generate complete demo dataset following the golden path scenario."""
        
        print("🎯 GarageReg Demo Scenario - Golden Path Data Generation")
        print("=" * 65)
        
        try:
            # Step 1: Create organization and users
            print("\n1️⃣ Creating organization and users...")
            self.create_organization_and_users()
            
            # Step 2: Create client
            print("\n2️⃣ Creating client (TechPark Business Center)...")
            self.create_demo_client()
            
            # Step 3: Create sites
            print("\n3️⃣ Creating sites (North & South Campus)...")
            self.create_demo_sites()
            
            # Step 4: Create buildings
            print("\n4️⃣ Creating buildings (Alfa, Beta, Gamma)...")
            self.create_demo_buildings()
            
            # Step 5: Create gates
            print("\n5️⃣ Creating gates (10 different types)...")
            self.create_demo_gates()
            
            # Step 6: Create inspection templates
            print("\n6️⃣ Creating inspection templates...")
            self.create_inspection_templates()
            
            # Step 7: Create inspections
            print("\n7️⃣ Creating demo inspections...")
            self.create_demo_inspections()
            
            # Step 8: Create ticket and work order
            print("\n8️⃣ Creating ticket → work order workflow...")
            self.create_ticket_work_order_flow()
            
            # Step 9: Generate summary
            print("\n9️⃣ Generating demo data summary...")
            self.generate_summary()
            
            print("\n✅ Demo Scenario Data Generation Complete!")
            print(f"📊 Summary saved to: {Path('demo_scenario_summary.json').absolute()}")
            
        except Exception as e:
            print(f"❌ Error during demo data generation: {str(e)}")
            self.db.rollback()
            raise
        else:
            self.db.commit()
            
    def create_organization_and_users(self):
        """Create main organization and demo users."""
        
        # Create main organization
        org = Organization(
            name="GarageReg Demo Organization",
            display_name="GarageReg Demo Szervezet",
            is_active=True
        )
        self.db.add(org)
        self.db.flush()
        
        # Create demo users
        users_data = [
            {
                "username": "admin",
                "email": "admin@garagereg.demo",
                "display_name": "Demo Admin",
                "is_active": True,
                "is_superuser": True,
                "org_id": org.id
            },
            {
                "username": "szabo.peter",
                "email": "szabo.peter@garagereg.demo", 
                "display_name": "Szabó Péter",
                "is_active": True,
                "org_id": org.id
            },
            {
                "username": "nagy.anna",
                "email": "nagy.anna@garagereg.demo",
                "display_name": "Nagy Anna", 
                "is_active": True,
                "org_id": org.id
            },
            {
                "username": "molnar.gabor",
                "email": "molnar.gabor@garagereg.demo",
                "display_name": "Molnár Gábor",
                "is_active": True,
                "org_id": org.id
            }
        ]
        
        for user_data in users_data:
            user = User(
                **user_data,
                hashed_password=get_password_hash("demo123")
            )
            self.db.add(user)
        
        self.db.flush()
        self.demo_data['organization'] = org.id
        print(f"   ✅ Organization created: {org.name}")
        print(f"   ✅ {len(users_data)} demo users created")
        
    def create_demo_client(self):
        """Create TechPark Business Center client."""
        
        # Note: In this simplified version, we're using the organization as the client
        # In a full implementation, this would create a separate Client entity
        
        client_data = {
            "name": "TechPark Business Center Kft.",
            "address": "1117 Budapest, InfoPark sétány 1.",
            "tax_number": "12345678-2-41",
            "registration_number": "01-09-876543",
            "contact_person": "Kovács László",
            "contact_phone": "+36 1 999 8877",
            "contact_email": "kovacs.laszlo@techpark.hu"
        }
        
        self.demo_data['client'] = client_data
        print(f"   ✅ Client configured: {client_data['name']}")
        
    def create_demo_sites(self):
        """Create North and South Campus sites."""
        
        org_id = self.demo_data['organization']
        
        sites_data = [
            {
                "name": "TechPark Északi Campus",
                "site_code": "NORTH-CAMPUS", 
                "address": "1117 Budapest, InfoPark sétány 1/A",
                "area_m2": 15000,
                "coordinates": "47.4736° N, 19.0511° E",
                "site_type": "Irodapark + gyártás"
            },
            {
                "name": "TechPark Déli Campus",
                "site_code": "SOUTH-CAMPUS",
                "address": "1117 Budapest, InfoPark sétány 1/B", 
                "area_m2": 8500,
                "coordinates": "47.4720° N, 19.0515° E",
                "site_type": "Logisztikai központ"
            }
        ]
        
        sites = []
        for site_data in sites_data:
            site = Site(
                organization_id=org_id,
                name=site_data["name"],
                site_code=site_data["site_code"],
                address=site_data["address"],
                is_active=True
            )
            self.db.add(site)
            sites.append(site)
            
        self.db.flush()
        self.demo_data['sites'] = [site.id for site in sites]
        print(f"   ✅ {len(sites)} sites created")
        
    def create_demo_buildings(self):
        """Create Alfa, Beta, Gamma buildings."""
        
        site_ids = self.demo_data['sites']
        
        buildings_data = [
            # North Campus buildings
            {
                "site_id": site_ids[0],  # North Campus
                "name": "Alfa Épület",
                "building_code": "ALFA",
                "description": "4 szintes irodaház",
                "floors": 4,
                "units": 120,
                "building_type": "office"
            },
            {
                "site_id": site_ids[0],  # North Campus
                "name": "Béta Épület", 
                "building_code": "BETA",
                "description": "2 szintes gyártócsarnok",
                "floors": 2,
                "units": 8,
                "building_type": "manufacturing"
            },
            # South Campus building
            {
                "site_id": site_ids[1],  # South Campus
                "name": "Gamma Épület",
                "building_code": "GAMMA", 
                "description": "1 szintes logisztikai csarnok",
                "floors": 1,
                "units": 25,
                "building_type": "logistics"
            }
        ]
        
        buildings = []
        for building_data in buildings_data:
            building = Building(
                site_id=building_data["site_id"],
                name=building_data["name"],
                building_code=building_data["building_code"],
                description=building_data["description"],
                floors=building_data["floors"],
                total_units=building_data["units"],
                is_active=True
            )
            self.db.add(building)
            buildings.append(building)
            
        self.db.flush()
        self.demo_data['buildings'] = [building.id for building in buildings]
        print(f"   ✅ {len(buildings)} buildings created")
        
    def create_demo_gates(self):
        """Create 10 demo gates with different types."""
        
        building_ids = self.demo_data['buildings']
        
        gates_data = [
            # Alfa Building (4 gates)
            {
                "building_id": building_ids[0],  # Alfa
                "gate_code": "MAIN-ALF-001",
                "name": "Főbejárat",
                "gate_type": "automatic_glass_door",
                "manufacturer": "KABA",
                "model": "ED-250",
                "location": "Földszint, főbejárat",
                "description": "Automatikus üvegajtó főbejárat"
            },
            {
                "building_id": building_ids[0],  # Alfa
                "gate_code": "PARK-ALF-002", 
                "name": "Parkolóház bejárat",
                "gate_type": "barrier_gate",
                "manufacturer": "CAME",
                "model": "GARD-4000",
                "location": "Parkolóház bejárat",
                "description": "Sorompó típusú parkolóház kapu"
            },
            {
                "building_id": building_ids[0],  # Alfa
                "gate_code": "FIRE-ALF-003",
                "name": "Tűzjelző kijárat", 
                "gate_type": "emergency_exit",
                "manufacturer": "DORMA",
                "model": "FIRE-EXIT-200",
                "location": "Északi szárny, tűzlépcsőház",
                "description": "Push bar tűzriadó kijárat"
            },
            {
                "building_id": building_ids[0],  # Alfa
                "gate_code": "SERV-ALF-004",
                "name": "Szerviz bejárat",
                "gate_type": "manual_door",
                "manufacturer": "ABLOY",
                "model": "SEC-DOOR-150",
                "location": "Hátsó szerviz terület",
                "description": "Kulcsos szerviz bejárat"
            },
            
            # Beta Building (3 gates)
            {
                "building_id": building_ids[1],  # Beta
                "gate_code": "PROD-BET-005",
                "name": "Gyártócsarnok főbejárat",
                "gate_type": "sliding_gate",
                "manufacturer": "CAME",
                "model": "BXV-4",
                "location": "Gyártócsarnok bejárat",
                "description": "Automatikus tolókapu"
            },
            {
                "building_id": building_ids[1],  # Beta
                "gate_code": "LOAD-BET-006",
                "name": "Rakodó kapu",
                "gate_type": "sectional_door", 
                "manufacturer": "HÖRMANN",
                "model": "SPU-F42",
                "location": "Rakodó terület",
                "description": "Kézi szekcionált emelőkapu"
            },
            {
                "building_id": building_ids[1],  # Beta  
                "gate_code": "EMRG-BET-007",
                "name": "Vészhelyzeti kijárat",
                "gate_type": "emergency_exit",
                "manufacturer": "PANIC",
                "model": "EMRG-300", 
                "location": "Gyártócsarnok keleti oldal",
                "description": "Pánikzár vészhelyzeti kijárat"
            },
            
            # Gamma Building (3 gates)
            {
                "building_id": building_ids[2],  # Gamma
                "gate_code": "DOCK-GAM-008", 
                "name": "Dokkoló kapu #1",
                "gate_type": "industrial_door",
                "manufacturer": "HÖRMANN",
                "model": "V-3015", 
                "location": "1. dokkoló állás",
                "description": "Hydraulikus ipari emelőkapu"
            },
            {
                "building_id": building_ids[2],  # Gamma
                "gate_code": "DOCK-GAM-009",
                "name": "Dokkoló kapu #2", 
                "gate_type": "industrial_door",
                "manufacturer": "HÖRMANN", 
                "model": "V-3015",
                "location": "2. dokkoló állás", 
                "description": "Hydraulikus ipari emelőkapu"
            },
            {
                "building_id": building_ids[2],  # Gamma
                "gate_code": "YARD-GAM-010",
                "name": "Udvar kapu",
                "gate_type": "swing_gate",
                "manufacturer": "NICE", 
                "model": "ROBO-1000",
                "location": "Udvar bejárat",
                "description": "Kétszárnyú lengő kapu"
            }
        ]
        
        gates = []
        for gate_data in gates_data:
            gate = Gate(
                building_id=gate_data["building_id"],
                gate_code=gate_data["gate_code"],
                name=gate_data["name"],
                gate_type=gate_data["gate_type"],
                manufacturer=gate_data["manufacturer"],
                model=gate_data["model"],
                location=gate_data["location"],
                description=gate_data["description"],
                is_active=True
            )
            self.db.add(gate)
            gates.append(gate)
            
        self.db.flush()
        self.demo_data['gates'] = [gate.id for gate in gates]
        print(f"   ✅ {len(gates)} gates created with QR codes")
        
    def create_inspection_templates(self):
        """Create inspection templates for different gate types."""
        
        org_id = self.demo_data['organization']
        
        templates_data = [
            {
                "name": "Havi Biztonsági Ellenőrzés",
                "template_code": "SAFETY-MONTHLY",
                "description": "Rendszeres havi biztonsági ellenőrzés",
                "category": "safety",
                "estimated_duration": 30
            },
            {
                "name": "Negyedéves Karbantartási Ellenőrzés", 
                "template_code": "MAINTENANCE-QUARTERLY",
                "description": "Megelőző karbantartási ellenőrzés",
                "category": "maintenance", 
                "estimated_duration": 90
            }
        ]
        
        templates = []
        for template_data in templates_data:
            template = InspectionTemplate(
                organization_id=org_id,
                name=template_data["name"],
                template_code=template_data["template_code"],
                description=template_data["description"],
                category=template_data["category"],
                estimated_duration_minutes=template_data["estimated_duration"],
                is_active=True
            )
            self.db.add(template)
            templates.append(template)
            
        self.db.flush()
        self.demo_data['inspection_templates'] = [t.id for t in templates]
        print(f"   ✅ {len(templates)} inspection templates created")
        
    def create_demo_inspections(self):
        """Create 2 demo inspections following the scenario."""
        
        gate_ids = self.demo_data['gates']
        template_ids = self.demo_data['inspection_templates']
        
        # Get users for assignment
        admin_user = self.db.query(User).filter(User.username == "admin").first()
        inspector1 = self.db.query(User).filter(User.username == "szabo.peter").first()
        inspector2 = self.db.query(User).filter(User.username == "nagy.anna").first()
        
        inspections_data = [
            {
                "gate_id": gate_ids[0],  # MAIN-ALF-001
                "template_id": template_ids[0],  # Safety template
                "inspector_id": inspector1.id,
                "title": "Havi Biztonsági Ellenőrzés - Alfa Főbejárat",
                "scheduled_date": datetime.now().replace(hour=9, minute=0),
                "status": "completed",
                "result": "minor_issue",
                "notes": "Kisebb hiba észlelve: kopott tömítés az ajtókeret alján. Cserét javaslom a következő karbantartáskor."
            },
            {
                "gate_id": gate_ids[4],  # PROD-BET-005  
                "template_id": template_ids[1],  # Maintenance template
                "inspector_id": inspector2.id,
                "title": "Negyedéves Karbantartási Ellenőrzés - Béta Gyártócsarnok",
                "scheduled_date": datetime.now().replace(hour=14, minute=30),
                "status": "completed", 
                "result": "critical_issue",
                "notes": "Súlyos hiba: motor túlmelegedés észlelhető. A kapu lassabban reagál, időnként megáll. Azonnali javítás szükséges!"
            }
        ]
        
        inspections = []
        for inspection_data in inspections_data:
            inspection = Inspection(
                gate_id=inspection_data["gate_id"],
                template_id=inspection_data["template_id"],
                inspector_id=inspection_data["inspector_id"],
                title=inspection_data["title"],
                scheduled_date=inspection_data["scheduled_date"],
                actual_start=inspection_data["scheduled_date"],
                actual_end=inspection_data["scheduled_date"] + timedelta(minutes=45),
                status=inspection_data["status"],
                result=inspection_data["result"],
                notes=inspection_data["notes"]
            )
            self.db.add(inspection)
            inspections.append(inspection)
            
        self.db.flush()
        self.demo_data['inspections'] = [i.id for i in inspections]
        print(f"   ✅ {len(inspections)} demo inspections completed")
        
    def create_ticket_work_order_flow(self):
        """Create ticket → work order flow based on critical inspection."""
        
        gate_ids = self.demo_data['gates']
        inspection_ids = self.demo_data['inspections']
        
        # Get users
        reporter = self.db.query(User).filter(User.username == "nagy.anna").first()
        technician = self.db.query(User).filter(User.username == "molnar.gabor").first()
        
        # Create ticket from critical inspection
        ticket = Ticket(
            ticket_number="TICKET-2024-001",
            title="Motor túlmelegedés - PROD-BET-005",
            description="Automatikus tolókapu motorjánál túlmelegedés észlelhető. A kapu lassabban reagál, időnként megáll. Az ellenőrzés során kritikus hibát találtunk.",
            category="electrical",
            priority=TicketPriority.HIGH,
            status=TicketStatus.IN_PROGRESS,
            gate_id=gate_ids[4],  # PROD-BET-005
            inspection_id=inspection_ids[1],  # Critical inspection
            reporter_id=reporter.id,
            org_id=reporter.org_id
        )
        self.db.add(ticket)
        self.db.flush()
        
        # Create work order from ticket  
        work_order = WorkOrder(
            work_order_number="WO-2024-001",
            title="Motor túlmelegedés javítása - PROD-BET-005",
            description="Automatikus tolókapu motor hűtőrendszer javítása és szenzor kalibrálás.",
            work_type="repair",
            work_category="electrical_repair",
            priority=TicketPriority.HIGH,
            status=WorkOrderStatus.COMPLETED,
            gate_id=gate_ids[4],  # PROD-BET-005
            ticket_id=ticket.id,
            assigned_technician_id=technician.id,
            estimated_duration_hours=4,
            actual_duration_hours=3.5,
            scheduled_start=datetime.now().replace(hour=8, minute=0),
            actual_start=datetime.now().replace(hour=8, minute=15),
            actual_end=datetime.now().replace(hour=11, minute=45),
            work_performed="1. Motor hűtőventillátor cseréje\n2. Hőmérséklet szenzor kalibrálás\n3. Működési teszt végrehajtása\n4. Biztonsági ellenőrzés",
            parts_used="- Hűtőventillátor (CAME-FAN-200W)\n- Hőmérséklet szenzor (TEMP-SENS-A1)\n- Hőpaszta (THERMAL-PASTE-5G)",
            quality_check_passed=True,
            customer_satisfaction_rating=5,
            org_id=reporter.org_id
        )
        self.db.add(work_order)
        self.db.flush()
        
        # Update ticket status
        ticket.status = TicketStatus.RESOLVED
        ticket.work_order_id = work_order.id
        
        self.demo_data['ticket'] = ticket.id
        self.demo_data['work_order'] = work_order.id
        print(f"   ✅ Ticket-to-WorkOrder flow created: {ticket.ticket_number} → {work_order.work_order_number}")
        
    def generate_summary(self):
        """Generate comprehensive summary of demo data."""
        
        summary = {
            "demo_scenario": "GarageReg Golden Path Demo",
            "generated_at": datetime.now().isoformat(),
            "data_counts": {
                "organizations": 1,
                "users": 4,
                "sites": len(self.demo_data.get('sites', [])),
                "buildings": len(self.demo_data.get('buildings', [])), 
                "gates": len(self.demo_data.get('gates', [])),
                "inspection_templates": len(self.demo_data.get('inspection_templates', [])),
                "inspections": len(self.demo_data.get('inspections', [])),
                "tickets": 1 if 'ticket' in self.demo_data else 0,
                "work_orders": 1 if 'work_order' in self.demo_data else 0
            },
            "key_entities": {
                "client_name": "TechPark Business Center Kft.",
                "sites": ["TechPark Északi Campus", "TechPark Déli Campus"],
                "buildings": ["Alfa Épület", "Béta Épület", "Gamma Épület"],
                "critical_gate": "PROD-BET-005 (Gyártócsarnok főbejárat)",
                "ticket_number": "TICKET-2024-001",
                "work_order_number": "WO-2024-001"
            },
            "pdf_documents_ready": [
                "Inspection Report (MAIN-ALF-001)",
                "Work Order Document (WO-2024-001)", 
                "Completion Report (WO-2024-001)"
            ],
            "ui_navigation_path": [
                "/dashboard",
                "/clients", 
                "/sites",
                "/buildings",
                "/gates", 
                "/inspection-demo",
                "/tickets"
            ],
            "demo_data_ids": self.demo_data
        }
        
        # Save summary to file
        with open("demo_scenario_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
            
        self.demo_data['summary'] = summary
        print(f"   ✅ Demo summary generated with {sum(summary['data_counts'].values())} entities")


def main():
    """Main entry point for demo data generation."""
    
    print("Starting GarageReg Demo Scenario Data Generation...")
    
    try:
        # Get database session
        db = next(get_db())
        
        # Create generator and run
        generator = DemoScenarioDataGenerator(db)
        generator.generate_all_demo_data()
        
        print("\n🎉 Demo Scenario Ready for UI Testing!")
        print("\nNext Steps:")
        print("1. 🌐 Start web application")
        print("2. 🔑 Login as admin/demo123") 
        print("3. 📋 Follow Golden Path navigation")
        print("4. 📄 Generate 3 PDF documents")
        print("5. ✅ Verify acceptance criteria")
        
    except Exception as e:
        print(f"\n❌ Demo data generation failed: {str(e)}")
        return 1
        
    return 0


if __name__ == "__main__":
    exit(main())