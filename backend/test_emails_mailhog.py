#!/usr/bin/env python3
"""
Notifikációs szolgáltatás tesztelés
Esemény-alapú emailek küldése MailHog-ba
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from datetime import datetime, timedelta
from app.services.notifications.email_service import EmailService
from app.services.notifications.models import EmailMessage, NotificationTrigger

def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")

async def test_notification_emails():
    """Test sending notification emails to MailHog"""
    
    print_header("GarageReg Notifikációs Tesztelés")
    print("Email-ek küldése MailHog szerverbe (localhost:1025)")
    
    email_service = EmailService()
    
    # Test data for different scenarios
    test_scenarios = [
        {
            'name': 'Közelgő ellenőrzés',
            'template': 'inspection_due',
            'trigger': NotificationTrigger.INSPECTION_DUE,
            'context': {
                'user_name': 'Kiss János',
                'gate_name': 'Főbejárat kapu #001',
                'gate_location': 'Budapest, Váci út 123.',
                'inspection_type': 'Rendszeres biztonsági ellenőrzés',
                'due_date': datetime.now() + timedelta(hours=6),
                'days_until_due': 0,
                'inspector_name': 'Nagy Péter',
                'inspector_phone': '+36-30-123-4567',
                'checklist_items': [
                    'Kapuautomatika működése',
                    'Biztonsági érzékelők tesztje',
                    'Távirányítók működése',
                    'Fizikai állapot ellenőrzése'
                ],
                'last_inspection': datetime.now() - timedelta(days=90),
                'url': 'https://garagereg.com/inspections/12345'
            }
        },
        {
            'name': 'SLA lejárat figyelmeztetés',
            'template': 'sla_expiring',
            'trigger': NotificationTrigger.SLA_EXPIRING,
            'context': {
                'user_name': 'Szabó Mária',
                'client_name': 'Példa Kft.',
                'contract_number': 'SLA-2024-001',
                'service_type': 'Kapu karbantartási szerződés',
                'expiry_date': datetime.now() + timedelta(days=7),
                'days_until_expiry': 7,
                'current_sla_level': 'Gold',
                'covered_gates': ['Főbejárat #001', 'Hátsó kapu #002', 'Teherkapu #003'],
                'annual_fee': 125000,
                'contact_person': 'Kovács Andrea',
                'contact_phone': '+36-1-234-5678',
                'url': 'https://garagereg.com/contracts/sla-2024-001'
            }
        },
        {
            'name': 'Munkalap befejezve',
            'template': 'work_order_completed',
            'trigger': NotificationTrigger.WORK_ORDER_COMPLETED,
            'context': {
                'user_name': 'Tóth László',
                'work_order_number': 'WO-2024-0789',
                'gate_name': 'Garázskapu #005',
                'gate_location': 'Debrecen, Kossuth u. 45.',
                'technician_name': 'Molnár György',
                'completion_date': datetime.now(),
                'work_type': 'Javítás',
                'work_description': 'Kapuautomatika szervó motor cseréje',
                'parts_used': [
                    'Szervó motor SM-240V',
                    'Biztonsági kondenzátor 4μF',
                    'Végelállás kapcsoló'
                ],
                'labor_hours': 2.5,
                'total_cost': 45500,
                'warranty_months': 12,
                'next_inspection': datetime.now() + timedelta(days=180),
                'satisfaction_survey_url': 'https://garagereg.com/survey/wo-2024-0789',
                'url': 'https://garagereg.com/workorders/wo-2024-0789'
            }
        }
    ]
    
    print(f"\n📧 {len(test_scenarios)} teszt scenario futtatása...")
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📋 Scenario {i}: {scenario['name']}")
        print(f"   Template: {scenario['template']}")
        print(f"   Trigger: {scenario['trigger'].value}")
        
        try:
            # Create email message
            email_msg = EmailMessage(
                to=['teszt@garagereg.com', 'manager@garagereg.com'],
                cc=['admin@garagereg.com'] if i == 1 else [],
                subject=f"GarageReg - {scenario['name']}",
                template=scenario['template'],
                context=scenario['context'],
                trigger=scenario['trigger'],
                priority='high' if i <= 2 else 'normal'
            )
            
            # Send email
            result = await email_service.send_email(email_msg)
            
            if result['success']:
                print(f"   ✅ Email sikeresen elküldve")
                print(f"   📧 Címzettek: {', '.join(email_msg.to)}")
                if email_msg.cc:
                    print(f"   📧 Másolat: {', '.join(email_msg.cc)}")
            else:
                print(f"   ❌ Email küldés sikertelen: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Hiba történt: {e}")
        
        # Small delay between emails
        await asyncio.sleep(1)
    
    print(f"\n🎉 Tesztelés befejezve!")
    print(f"📬 Ellenőrizd a MailHog webes felületet: http://localhost:8025")
    print(f"📧 SMTP konfiguráció: localhost:1025")

if __name__ == "__main__":
    asyncio.run(test_notification_emails())