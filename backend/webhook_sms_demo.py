#!/usr/bin/env python3
"""
Webhook és SMS Stub Demonstráció
"""
import json
import hmac
import hashlib
import time
from datetime import datetime

class WebhookAdapter:
    """Webhook adapter HMAC aláírással"""
    
    def __init__(self):
        self.secret_key = "garagereg_webhook_secret_2024"
        self.endpoints = {
            'monitoring': 'https://monitoring.garagereg.com/webhook',
            'maintenance_system': 'https://maintenance.external.com/api/notifications',
            'external_api': 'https://partner-api.example.com/events'
        }
    
    def send_webhook(self, endpoint_name, event_type, payload):
        """Küldi a webhook-ot HMAC aláírással"""
        if endpoint_name not in self.endpoints:
            print(f"   ❌ Ismeretlen webhook endpoint: {endpoint_name}")
            return False
        
        url = self.endpoints[endpoint_name]
        
        # Payload előkészítés
        webhook_payload = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'source': 'garagereg_system',
            'data': payload
        }
        
        # HMAC aláírás generálás
        payload_json = json.dumps(webhook_payload, sort_keys=True)
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            payload_json.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Webhook küldés szimuláció
        print(f"   🔗 Webhook küldés: {endpoint_name}")
        print(f"      URL: {url}")
        print(f"      Event: {event_type}")
        print(f"      HMAC: {signature[:16]}...")
        print(f"      Payload méret: {len(payload_json)} bytes")
        
        # Szimuláljuk a válasz időt
        response_time = 0.1 + (len(payload_json) / 10000)
        time.sleep(response_time)
        
        print(f"      ✅ Sikeres (válasz idő: {response_time:.2f}s)")
        return True

class SMSService:
    """SMS szolgáltatás multi-provider támogatással"""
    
    def __init__(self):
        self.providers = {
            'twilio': {
                'name': 'Twilio International',
                'endpoint': 'https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json',
                'auth_type': 'basic',
                'cost_per_sms': 0.05  # USD
            },
            'vodafone_hu': {
                'name': 'Vodafone Hungary',
                'endpoint': 'https://api.vodafone.hu/sms/v1/send',
                'auth_type': 'api_key',
                'cost_per_sms': 15  # HUF
            },
            'telekom_hu': {
                'name': 'Magyar Telekom',
                'endpoint': 'https://api.telekom.hu/messaging/sms',
                'auth_type': 'oauth2',
                'cost_per_sms': 18  # HUF
            }
        }
        
        self.templates = {
            'inspection_due': "Ellenőrzés esedékes: {gate_name} - {due_date}. Ellenőr: {inspector}. Részletek: {url}",
            'sla_expiring': "SLA lejár {days} nap múlva: {client_name}. Szerződés: {contract_id}. Info: {url}",
            'work_order_completed': "Munka befejezve: {work_order_id}. Technikus: {technician}. Költség: {cost} Ft. {url}"
        }
    
    def send_sms(self, phone_number, template_name, context, provider='vodafone_hu'):
        """SMS küldés szimuláció"""
        if provider not in self.providers:
            print(f"   ❌ Ismeretlen SMS provider: {provider}")
            return False
        
        if template_name not in self.templates:
            print(f"   ❌ Ismeretlen SMS sablon: {template_name}")
            return False
        
        provider_info = self.providers[provider]
        template = self.templates[template_name]
        
        # Telefon szám validáció
        formatted_phone = self._format_phone_number(phone_number)
        if not formatted_phone:
            print(f"   ❌ Érvénytelen telefonszám: {phone_number}")
            return False
        
        # SMS szöveg generálás
        try:
            message = template.format(**context)
            if len(message) > 160:
                message = message[:157] + "..."
        except KeyError as e:
            print(f"   ❌ Hiányzó template változó: {e}")
            return False
        
        # SMS küldés szimuláció
        print(f"   📱 SMS küldés: {provider_info['name']}")
        print(f"      Címzett: {formatted_phone}")
        print(f"      Sablon: {template_name}")
        print(f"      Hossz: {len(message)}/160 karakter")
        print(f"      Költség: {provider_info['cost_per_sms']} {'HUF' if provider.endswith('_hu') else 'USD'}")
        print(f"      Üzenet: '{message}'")
        
        # Szimuláljuk a küldési időt
        time.sleep(0.5)
        print(f"      ✅ Sikeres küldés")
        
        return True
    
    def _format_phone_number(self, phone):
        """Magyar telefonszám formázás"""
        # Távolítsuk el a szóközöket és kötőjeleket
        clean_phone = phone.replace(' ', '').replace('-', '')
        
        # Magyar formátum ellenőrzés
        if clean_phone.startswith('+36'):
            return clean_phone
        elif clean_phone.startswith('36'):
            return f"+{clean_phone}"
        elif clean_phone.startswith('06'):
            return f"+36{clean_phone[2:]}"
        elif len(clean_phone) == 9 and clean_phone.startswith(('20', '30', '70')):
            return f"+36{clean_phone}"
        
        return None

def demonstrate_webhook_sms():
    """Webhook és SMS szolgáltatások demonstrációja"""
    
    print("🎯 GarageReg Webhook & SMS Szolgáltatások")
    print("=" * 60)
    
    webhook_adapter = WebhookAdapter()
    sms_service = SMSService()
    
    # 1. Webhook demonstráció - Közelgő ellenőrzés
    print("\n🔗 WEBHOOK DEMONSTRÁCIÓ")
    print("=" * 30)
    
    inspection_payload = {
        'gate_id': 'GATE001',
        'gate_name': 'Főbejárat kapu #001',
        'location': 'Budapest, Váci út 123.',
        'due_date': '2024-10-04T08:00:00Z',
        'inspector_id': 'INSP001',
        'priority': 'high'
    }
    
    webhook_adapter.send_webhook('monitoring', 'inspection_due', inspection_payload)
    webhook_adapter.send_webhook('maintenance_system', 'inspection_due', inspection_payload)
    
    time.sleep(1)
    
    # 2. SMS demonstráció
    print("\n📱 SMS DEMONSTRÁCIÓ")
    print("=" * 20)
    
    # SMS 1: Közelgő ellenőrzés
    sms_context = {
        'gate_name': 'Főbejárat #001',
        'due_date': '2024-10-04 08:00',
        'inspector': 'Nagy Péter',
        'url': 'https://garagereg.com/i/12345'
    }
    
    sms_service.send_sms('+36301234567', 'inspection_due', sms_context, 'vodafone_hu')
    
    time.sleep(1)
    
    # SMS 2: SLA lejárat
    sla_context = {
        'days': 5,
        'client_name': 'Példa Kft',
        'contract_id': 'SLA-001',
        'url': 'https://garagereg.com/sla/001'
    }
    
    sms_service.send_sms('06-30-987-6543', 'sla_expiring', sla_context, 'telekom_hu')
    
    time.sleep(1)
    
    # SMS 3: Munkalap befejezés
    wo_context = {
        'work_order_id': 'WO-999',
        'technician': 'Kovács B.',
        'cost': 45500,
        'url': 'https://garagereg.com/wo/999'
    }
    
    sms_service.send_sms('36201119876', 'work_order_completed', wo_context, 'twilio')
    
    # 3. Webhook - Munkalap befejezés
    print(f"\n🔗 WEBHOOK: Munkalap befejezés")
    print("=" * 30)
    
    work_order_payload = {
        'work_order_id': 'WO-2024-0999',
        'gate_id': 'GATE005',
        'technician_id': 'TECH003',
        'completion_time': datetime.now().isoformat(),
        'total_cost': 45500,
        'customer_id': 'CUST123',
        'next_inspection_due': '2025-04-04T10:00:00Z'
    }
    
    webhook_adapter.send_webhook('external_api', 'work_order_completed', work_order_payload)
    
    print(f"\n🎉 Webhook & SMS demonstráció befejezve!")
    print(f"📊 Összefoglalás:")
    print(f"   • Webhook küldések: 3")
    print(f"   • SMS küldések: 3 (3 provider)")
    print(f"   • HMAC aláírás: Minden webhook-nál")
    print(f"   • Telefon validáció: Magyar formátumok")
    print(f"   • Template rendszer: 3 sablon típus")

if __name__ == "__main__":
    demonstrate_webhook_sms()