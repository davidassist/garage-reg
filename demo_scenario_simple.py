#!/usr/bin/env python3
"""
GarageReg Demo Scenario - Simplified Data Generator

Creates demo data compatible with the current database structure:
- 1 Client organization
- 2 Sites  
- 3 Buildings
- 10 Gates
- 2 Inspection templates
- Sample inspection data
- Ticket → Work Order flow

Simplified demo adat generátor a jelenlegi adatbázis struktúrához.
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path


def create_demo_scenario_data():
    """Create comprehensive demo data for the Golden Path scenario."""
    
    print("🎯 GarageReg Demo Scenario - Simplified Data Generation")
    print("=" * 60)
    
    demo_data = {}
    
    # 1. Organization/Client Data
    print("\n1️⃣ Creating client organization data...")
    demo_data['client'] = {
        "id": 1,
        "name": "TechPark Business Center Kft.",
        "display_name": "TechPark Business Center",
        "address": "1117 Budapest, InfoPark sétány 1.",
        "tax_number": "12345678-2-41", 
        "registration_number": "01-09-876543",
        "contact_person": "Kovács László",
        "contact_phone": "+36 1 999 8877",
        "contact_email": "kovacs.laszlo@techpark.hu",
        "is_active": True
    }
    
    # 2. Sites Data
    print("2️⃣ Creating sites data...")
    demo_data['sites'] = [
        {
            "id": 1,
            "client_id": 1,
            "name": "TechPark Északi Campus",
            "display_name": "Északi Campus",
            "address": "1117 Budapest, InfoPark sétány 1/A",
            "description": "Irodapark + gyártás terület (15,000 m²)",
            "is_active": True
        },
        {
            "id": 2, 
            "client_id": 1,
            "name": "TechPark Déli Campus",
            "display_name": "Déli Campus", 
            "address": "1117 Budapest, InfoPark sétány 1/B",
            "description": "Logisztikai központ (8,500 m²)",
            "is_active": True
        }
    ]
    
    # 3. Buildings Data
    print("3️⃣ Creating buildings data...")
    demo_data['buildings'] = [
        # North Campus buildings
        {
            "id": 1,
            "site_id": 1,
            "name": "Alfa Épület",
            "display_name": "Alfa Épület",
            "description": "4 szintes irodaház, 120 irodaegység",
            "floor_count": 4,
            "total_area": 5000,
            "is_active": True
        },
        {
            "id": 2,
            "site_id": 1, 
            "name": "Béta Épület",
            "display_name": "Béta Épület",
            "description": "2 szintes gyártócsarnok, 8 gyártóegység", 
            "floor_count": 2,
            "total_area": 3000,
            "is_active": True
        },
        # South Campus building
        {
            "id": 3,
            "site_id": 2,
            "name": "Gamma Épület", 
            "display_name": "Gamma Épület",
            "description": "1 szintes logisztikai csarnok, 25 raktárégység",
            "floor_count": 1,
            "total_area": 4000,
            "is_active": True
        }
    ]
    
    # 4. Gates Data (10 gates)
    print("4️⃣ Creating gates data...")
    demo_data['gates'] = [
        # Alfa Building gates (4)
        {
            "id": 1,
            "building_id": 1,
            "name": "Főbejárat",
            "display_name": "Alfa Főbejárat", 
            "gate_type": "automatic_door",
            "manufacturer": "KABA",
            "model": "ED-250",
            "serial_number": "KABA-ED250-001",
            "installation_date": "2024-01-15",
            "location_description": "Földszint, főbejárat",
            "is_active": True
        },
        {
            "id": 2,
            "building_id": 1,
            "name": "Parkolóház bejárat",
            "display_name": "Alfa Parkoló",
            "gate_type": "barrier",
            "manufacturer": "CAME", 
            "model": "GARD-4000",
            "serial_number": "CAME-G4000-002",
            "installation_date": "2024-01-20",
            "location_description": "Parkolóház bejárat",
            "is_active": True
        },
        {
            "id": 3,
            "building_id": 1,
            "name": "Tűzjelző kijárat",
            "display_name": "Alfa Tűzkijárat",
            "gate_type": "emergency_exit",
            "manufacturer": "DORMA",
            "model": "FIRE-EXIT-200", 
            "serial_number": "DORMA-FE200-003",
            "installation_date": "2024-01-25",
            "location_description": "Északi szárny, tűzlépcsőház",
            "is_active": True
        },
        {
            "id": 4,
            "building_id": 1, 
            "name": "Szerviz bejárat",
            "display_name": "Alfa Szerviz",
            "gate_type": "manual_door",
            "manufacturer": "ABLOY",
            "model": "SEC-DOOR-150",
            "serial_number": "ABLOY-SD150-004", 
            "installation_date": "2024-02-01",
            "location_description": "Hátsó szerviz terület",
            "is_active": True
        },
        
        # Beta Building gates (3)
        {
            "id": 5,
            "building_id": 2,
            "name": "Gyártócsarnok főbejárat", 
            "display_name": "Béta Gyártócsarnok",
            "gate_type": "sliding",
            "manufacturer": "CAME",
            "model": "BXV-4",
            "serial_number": "CAME-BXV4-005",
            "installation_date": "2024-02-05",
            "location_description": "Gyártócsarnok bejárat", 
            "is_active": True
        },
        {
            "id": 6,
            "building_id": 2,
            "name": "Rakodó kapu",
            "display_name": "Béta Rakodó",
            "gate_type": "sectional",
            "manufacturer": "HÖRMANN", 
            "model": "SPU-F42",
            "serial_number": "HORM-SF42-006",
            "installation_date": "2024-02-10",
            "location_description": "Rakodó terület",
            "is_active": True
        },
        {
            "id": 7,
            "building_id": 2,
            "name": "Vészhelyzeti kijárat",
            "display_name": "Béta Vészkijárat", 
            "gate_type": "emergency_exit",
            "manufacturer": "PANIC",
            "model": "EMRG-300",
            "serial_number": "PANIC-E300-007",
            "installation_date": "2024-02-15",
            "location_description": "Gyártócsarnok keleti oldal",
            "is_active": True
        },
        
        # Gamma Building gates (3)
        {
            "id": 8,
            "building_id": 3,
            "name": "Dokkoló kapu #1",
            "display_name": "Gamma Dokkoló 1",
            "gate_type": "industrial",
            "manufacturer": "HÖRMANN",
            "model": "V-3015",
            "serial_number": "HORM-V3015-008", 
            "installation_date": "2024-02-20",
            "location_description": "1. dokkoló állás",
            "is_active": True
        },
        {
            "id": 9,
            "building_id": 3,
            "name": "Dokkoló kapu #2",
            "display_name": "Gamma Dokkoló 2", 
            "gate_type": "industrial",
            "manufacturer": "HÖRMANN",
            "model": "V-3015",
            "serial_number": "HORM-V3015-009",
            "installation_date": "2024-02-25",
            "location_description": "2. dokkoló állás",
            "is_active": True
        },
        {
            "id": 10,
            "building_id": 3,
            "name": "Udvar kapu",
            "display_name": "Gamma Udvar",
            "gate_type": "swing",
            "manufacturer": "NICE",
            "model": "ROBO-1000",
            "serial_number": "NICE-R1000-010",
            "installation_date": "2024-03-01", 
            "location_description": "Udvar bejárat",
            "is_active": True
        }
    ]
    
    # 5. Users Data
    print("5️⃣ Creating users data...")
    demo_data['users'] = [
        {
            "id": 1,
            "username": "admin",
            "email": "admin@garagereg.demo",
            "display_name": "Demo Admin",
            "is_active": True
        },
        {
            "id": 2, 
            "username": "szabo.peter",
            "email": "szabo.peter@garagereg.demo",
            "display_name": "Szabó Péter",
            "license_number": "ELL-2024-0156",
            "is_active": True
        },
        {
            "id": 3,
            "username": "nagy.anna", 
            "email": "nagy.anna@garagereg.demo",
            "display_name": "Nagy Anna",
            "license_number": "ELL-2024-0089",
            "is_active": True
        },
        {
            "id": 4,
            "username": "molnar.gabor",
            "email": "molnar.gabor@garagereg.demo",
            "display_name": "Molnár Gábor", 
            "license_number": "TECH-2024-0234",
            "is_active": True
        }
    ]
    
    # 6. Inspection Templates
    print("6️⃣ Creating inspection templates...")
    demo_data['inspection_templates'] = [
        {
            "id": 1,
            "name": "Havi Biztonsági Ellenőrzés",
            "description": "Rendszeres havi biztonsági ellenőrzés összes kaputípusra",
            "category": "safety",
            "estimated_duration": 30,
            "is_active": True,
            "checklist_items": [
                "Mechanikus működés ellenőrzése",
                "Biztonsági érzékelők tesztje", 
                "Vészmegállító funkcionalitás",
                "Világítás és jelzések",
                "Tömítések és kopási nyomok"
            ]
        },
        {
            "id": 2,
            "name": "Negyedéves Karbantartási Ellenőrzés", 
            "description": "Részletes karbantartási és műszaki ellenőrzés",
            "category": "maintenance",
            "estimated_duration": 90,
            "is_active": True,
            "checklist_items": [
                "Motor és hajtáslánc ellenőrzés",
                "Elektromos rendszer diagnosztika",
                "Hőmérséklet mérések",
                "Kenőanyag és folyadék szintek", 
                "Kopóalkatrészek felmérése",
                "Kalibrációs beállítások"
            ]
        }
    ]
    
    # 7. Demo Inspections
    print("7️⃣ Creating demo inspections...")
    demo_data['inspections'] = [
        {
            "id": 1,
            "gate_id": 1,  # Alfa főbejárat
            "template_id": 1,  # Safety template
            "inspector_id": 2,  # Szabó Péter
            "title": "Havi Biztonsági Ellenőrzés - Alfa Főbejárat",
            "scheduled_date": "2024-10-04T09:00:00",
            "actual_start": "2024-10-04T09:05:00",
            "actual_end": "2024-10-04T09:35:00",
            "status": "completed",
            "result": "minor_issue",
            "notes": "Kisebb hiba észlelve: kopott tömítés az ajtókeret alján. Működőképesség nem sérül, de cserét javaslom a következő karbantartáskor.",
            "checklist_results": {
                "mechanikus_mukodes": "OK",
                "biztonsagi_erzekelek": "OK", 
                "veszmegallito": "OK",
                "vilagitas": "OK",
                "tomitesek": "Kopás észlelhető"
            }
        },
        {
            "id": 2,
            "gate_id": 5,  # Béta gyártócsarnok
            "template_id": 2,  # Maintenance template
            "inspector_id": 3,  # Nagy Anna
            "title": "Negyedéves Karbantartási Ellenőrzés - Béta Gyártócsarnok",
            "scheduled_date": "2024-10-04T14:30:00", 
            "actual_start": "2024-10-04T14:35:00",
            "actual_end": "2024-10-04T16:15:00",
            "status": "completed",
            "result": "critical_issue", 
            "notes": "KRITIKUS HIBA: Motor túlmelegedés észlelhető (78°C normal üzemnél, max. 65°C). A kapu lassabban reagál, időnként 2-3 másodpercre megáll. Azonnali javítás szükséges az üzemzavar elkerüléséhez!",
            "checklist_results": {
                "motor_hajtaslancz": "KRITIKUS - Túlmelegedés",
                "elektromos_rendszer": "Normál", 
                "homerseklet": "78°C (MAX: 65°C) - TÚLLÉPÉS",
                "kenoanyag": "OK",
                "kopoalkatresz": "Ventillátor hibás",
                "kalibracio": "Hőszenzor eltérés"
            }
        }
    ]
    
    # 8. Ticket and Work Order
    print("8️⃣ Creating ticket → work order flow...")
    demo_data['ticket'] = {
        "id": 1,
        "ticket_number": "TICKET-2024-001",
        "title": "Motor túlmelegedés - PROD-BET-005",
        "description": "Automatikus tolókapu motorjánál túlmelegedés észlelhető (78°C). A kapu lassabban reagál, időnként 2-3 másodpercre megáll. Az ellenőrzés során kritikus hibát találtunk. Azonnali javítás szükséges az üzemzavar elkerüléséhez.",
        "category": "electrical",
        "priority": "high",
        "status": "resolved",
        "gate_id": 5,  # Béta gyártócsarnok
        "inspection_id": 2,  # Critical inspection
        "reporter_id": 3,  # Nagy Anna
        "created_at": "2024-10-04T16:20:00"
    }
    
    demo_data['work_order'] = {
        "id": 1,
        "work_order_number": "WO-2024-001",
        "title": "Motor túlmelegedés javítása - PROD-BET-005",
        "description": "Automatikus tolókapu motor hűtőrendszer javítása, ventillátor csere és hőszenzor kalibrálás a túlmelegedés megszüntetésére.",
        "work_type": "repair",
        "work_category": "electrical_repair", 
        "priority": "high",
        "status": "completed",
        "gate_id": 5,  # Béta gyártócsarnok
        "ticket_id": 1,
        "assigned_technician_id": 4,  # Molnár Gábor
        "estimated_duration_hours": 4.0,
        "actual_duration_hours": 3.5,
        "scheduled_start": "2024-10-04T08:00:00",
        "actual_start": "2024-10-04T08:15:00", 
        "actual_end": "2024-10-04T11:45:00",
        "work_performed": """Elvégzett munkálatok:
1. Motor hűtőventillátor demontálása és vizsgálata
2. Hibás ventillátor cseréje (CAME-FAN-200W)
3. Hőmérséklet szenzor kalibrálása és beállítása 
4. Hőpaszta felvitel a motor-hűtő felületekre
5. Működési teszt végrehajtása (30 ciklus)
6. Biztonsági ellenőrzés és dokumentálás""",
        "parts_used": """Felhasznált alkatrészek:
- Hűtőventillátor (CAME-FAN-200W) - 1 db
- Hőmérséklet szenzor (TEMP-SENS-A1) - 1 db  
- Hőpaszta (THERMAL-PASTE-5G) - 1 tubus
- Csavarok és rögzítők - készlet""",
        "quality_check_passed": True,
        "customer_satisfaction_rating": 5,
        "completion_notes": "Javítás sikeresen befejezve. Motor hőmérséklet stabilizálódott 52°C-ra. 30 ciklusos teszt hibátlan. Következő ellenőrzés 3 hónap múlva javasolt."
    }
    
    # 9. PDF Documents Configuration
    print("9️⃣ Configuring PDF document templates...")
    demo_data['pdf_documents'] = {
        "inspection_report": {
            "template": "inspection_report_template.html",
            "filename": "inspection-report-MAIN-ALF-001-20241004.pdf",
            "title": "Ellenőrzési Jegyzőkönyv",
            "inspection_id": 1
        },
        "work_order": {
            "template": "work_order_template.html", 
            "filename": "work-order-WO-2024-001.pdf",
            "title": "Munkalap",
            "work_order_id": 1
        },
        "completion_report": {
            "template": "completion_report_template.html",
            "filename": "completion-report-WO-2024-001.pdf", 
            "title": "Befejezési Riport",
            "work_order_id": 1
        }
    }
    
    # 10. Generate Summary
    print("🔟 Generating demo summary...")
    demo_data['summary'] = {
        "scenario_name": "GarageReg Golden Path Demo",
        "generated_at": datetime.now().isoformat(),
        "total_entities": {
            "clients": 1,
            "sites": 2, 
            "buildings": 3,
            "gates": 10,
            "users": 4,
            "inspection_templates": 2,
            "inspections": 2,
            "tickets": 1,
            "work_orders": 1,
            "pdf_documents": 3
        },
        "golden_path_steps": [
            "1. Dashboard overview",
            "2. Client management (TechPark)",
            "3. Site management (North/South Campus)", 
            "4. Building management (Alfa/Beta/Gamma)",
            "5. Gate management (10 gates)",
            "6. Inspection execution", 
            "7. Ticket creation",
            "8. Work order processing",
            "9. PDF document generation"
        ],
        "acceptance_criteria": {
            "ui_navigation": "Complete path navigable", 
            "pdf_generation": "3 documents must generate",
            "data_completeness": "All demo entities present"
        }
    }
    
    # Save to file
    output_file = Path("demo_scenario_data.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(demo_data, f, indent=2, ensure_ascii=False, default=str)
        
    print(f"\n✅ Demo Scenario Data Generated Successfully!")
    print(f"📁 Output file: {output_file.absolute()}")
    print(f"📊 Total entities: {sum(demo_data['summary']['total_entities'].values())}")
    
    return demo_data


def print_demo_summary(demo_data):
    """Print formatted summary of generated demo data."""
    
    print("\n" + "="*60)
    print("🎯 DEMO SCENARIO SUMMARY")
    print("="*60)
    
    print(f"\n📋 CLIENT: {demo_data['client']['name']}")
    print(f"   📍 Address: {demo_data['client']['address']}")
    print(f"   📞 Contact: {demo_data['client']['contact_person']}")
    
    print(f"\n🏢 SITES ({len(demo_data['sites'])}):")
    for site in demo_data['sites']:
        print(f"   • {site['name']} - {site['address']}")
        
    print(f"\n🏗️ BUILDINGS ({len(demo_data['buildings'])}):")
    for building in demo_data['buildings']:
        print(f"   • {building['name']} - {building['description']}")
        
    print(f"\n🚪 GATES ({len(demo_data['gates'])}):")
    for i, gate in enumerate(demo_data['gates'], 1):
        print(f"   {i:2}. {gate['display_name']} ({gate['gate_type']}) - {gate['manufacturer']} {gate['model']}")
        
    print(f"\n🔍 INSPECTIONS ({len(demo_data['inspections'])}):")
    for inspection in demo_data['inspections']:
        print(f"   • {inspection['title']}")
        print(f"     Result: {inspection['result']} | Inspector: {demo_data['users'][inspection['inspector_id']-1]['display_name']}")
        
    print(f"\n🎫 WORKFLOW:")
    print(f"   • Ticket: {demo_data['ticket']['ticket_number']} ({demo_data['ticket']['priority']} priority)")
    print(f"   • Work Order: {demo_data['work_order']['work_order_number']} ({demo_data['work_order']['status']})")
    print(f"   • Duration: {demo_data['work_order']['actual_duration_hours']} hours")
    
    print(f"\n📄 PDF DOCUMENTS:")
    for doc_type, doc_info in demo_data['pdf_documents'].items():
        print(f"   • {doc_info['title']}: {doc_info['filename']}")
        
    print(f"\n🌐 UI NAVIGATION PATH:")
    nav_steps = [
        "/dashboard → Overview",
        "/clients → TechPark setup", 
        "/sites → Campus management",
        "/buildings → Building registry",
        "/gates → Gate management", 
        "/inspection-demo → Execute inspections",
        "/tickets → Ticket workflow",
        "PDF Generation → 3 documents"
    ]
    for step in nav_steps:
        print(f"   → {step}")
        
    print(f"\n✅ ACCEPTANCE CRITERIA:")
    print(f"   ☐ Demo végigjátszható UI-ból")
    print(f"   ☐ 3 PDF keletkezik")  
    print(f"   ☐ Teljes workflow működik")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    demo_data = create_demo_scenario_data()
    print_demo_summary(demo_data)