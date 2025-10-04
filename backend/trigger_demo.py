#!/usr/bin/env python3
"""
Notifikációs Trigger Rendszer - Eseményvezérelt Tesztelés
"""
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

class NotificationTriggerDemo:
    """Trigger-alapú notifikáció szimuláció"""
    
    def __init__(self):
        self.smtp_server = "localhost"
        self.smtp_port = 1025
        self.sender = "garagereg@system.local"
    
    def simulate_inspection_due_trigger(self):
        """Szimulálja a közelgő ellenőrzés triggerét"""
        print("\n🔍 TRIGGER: Közelgő ellenőrzés észlelve")
        print("=" * 50)
        
        # Szimulált adatbázis lekérdezés eredménye
        due_inspections = [
            {
                'gate_id': 'GATE001',
                'gate_name': 'Főbejárat kapu #001',
                'location': 'Budapest, Váci út 123.',
                'due_date': datetime.now() + timedelta(hours=4),
                'inspector': 'Nagy Péter',
                'contact': 'peter.nagy@garagereg.com'
            },
            {
                'gate_id': 'GATE005',
                'gate_name': 'Teherkapu #005',
                'location': 'Budapest, Kossuth u. 89.',
                'due_date': datetime.now() + timedelta(hours=2),
                'inspector': 'Kiss Anna',
                'contact': 'anna.kiss@garagereg.com'
            }
        ]
        
        print(f"📊 Talált ellenőrzések: {len(due_inspections)}")
        
        for inspection in due_inspections:
            self._send_inspection_notification(inspection)
            time.sleep(1)  # Rate limiting
    
    def simulate_sla_expiring_trigger(self):
        """Szimulálja az SLA lejárat triggerét"""
        print("\n⚠️ TRIGGER: SLA lejárat figyelmeztetés")
        print("=" * 50)
        
        # Szimulált lejáró szerződések
        expiring_contracts = [
            {
                'contract_id': 'SLA-2024-001',
                'client_name': 'Példa Kft.',
                'expiry_date': datetime.now() + timedelta(days=5),
                'sla_level': 'Gold',
                'annual_fee': 125000,
                'contact': 'maria.szabo@peldakft.hu'
            }
        ]
        
        print(f"📊 Lejáró szerződések: {len(expiring_contracts)}")
        
        for contract in expiring_contracts:
            self._send_sla_notification(contract)
            time.sleep(1)
    
    def simulate_work_order_completed_trigger(self, work_order_data):
        """Szimulálja a munkalap befejezés triggerét"""
        print("\n✅ TRIGGER: Munkalap befejezve")
        print("=" * 50)
        print(f"📋 Munkalap: {work_order_data['work_order_id']}")
        print(f"🏠 Helyszín: {work_order_data['location']}")
        
        self._send_work_order_notification(work_order_data)
    
    def _send_inspection_notification(self, inspection):
        """Küld ellenőrzés értesítést"""
        hours_until = (inspection['due_date'] - datetime.now()).seconds // 3600
        urgency = "SÜRGŐS" if hours_until < 6 else "NORMÁL"
        
        subject = f"🔍 TRIGGER: Ellenőrzés esedékes - {inspection['gate_name']} ({urgency})"
        
        content = f"""
        <html>
        <body style="font-family: Arial; background: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px;">
                <div style="background: #1976d2; color: white; padding: 15px; text-align: center; border-radius: 5px;">
                    <h2>🔍 Automatikus Trigger: Közelgő ellenőrzés</h2>
                </div>
                
                <div style="padding: 20px;">
                    <p><strong>Trigger időpontja:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    
                    <div style="background: #fff3e0; padding: 15px; border-left: 4px solid #ff9800; margin: 15px 0;">
                        <strong>Kapu ID:</strong> {inspection['gate_id']}<br/>
                        <strong>Kapu neve:</strong> {inspection['gate_name']}<br/>
                        <strong>Helyszín:</strong> {inspection['location']}<br/>
                        <strong>Esedékesség:</strong> {inspection['due_date'].strftime('%Y-%m-%d %H:%M')}<br/>
                        <strong>Sürgősség:</strong> <span style="color: {'red' if urgency == 'SÜRGŐS' else 'orange'};">{urgency}</span>
                    </div>
                    
                    <p><strong>Kijelölt ellenőr:</strong> {inspection['inspector']}</p>
                    
                    <div style="background: #e3f2fd; padding: 10px; border-radius: 5px; font-size: 12px;">
                        <strong>Trigger információ:</strong><br/>
                        - Automatikus detektálás 6 óránként<br/>
                        - Sürgősségi küszöb: 6 óra<br/>
                        - Következő ellenőrzés: {(datetime.now() + timedelta(hours=6)).strftime('%H:%M')}
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        self._send_email(inspection['contact'], subject, content)
        print(f"   ✅ Értesítés elküldve: {inspection['inspector']} ({urgency})")
    
    def _send_sla_notification(self, contract):
        """Küld SLA lejárat értesítést"""
        days_left = (contract['expiry_date'] - datetime.now()).days
        
        subject = f"⚠️ TRIGGER: SLA lejárat - {contract['client_name']} ({days_left} nap)"
        
        content = f"""
        <html>
        <body style="font-family: Arial; background: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px;">
                <div style="background: #f57c00; color: white; padding: 15px; text-align: center; border-radius: 5px;">
                    <h2>⚠️ Automatikus Trigger: SLA lejárat</h2>
                </div>
                
                <div style="padding: 20px;">
                    <p><strong>Trigger időpontja:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    
                    <div style="background: #fff3e0; padding: 15px; border-left: 4px solid #f57c00; margin: 15px 0;">
                        <strong>Szerződés ID:</strong> {contract['contract_id']}<br/>
                        <strong>Ügyfél:</strong> {contract['client_name']}<br/>
                        <strong>Lejárat:</strong> {contract['expiry_date'].strftime('%Y-%m-%d')}<br/>
                        <strong>Hátralevő napok:</strong> <span style="color: red; font-weight: bold;">{days_left}</span><br/>
                        <strong>SLA szint:</strong> {contract['sla_level']}<br/>
                        <strong>Éves díj:</strong> {contract['annual_fee']:,} Ft
                    </div>
                    
                    <div style="background: #e3f2fd; padding: 10px; border-radius: 5px; font-size: 12px;">
                        <strong>Trigger információ:</strong><br/>
                        - Automatikus ellenőrzés 15 percenként<br/>
                        - Figyelmeztetés küszöb: 30 nap<br/>
                        - Sürgős figyelmeztetés: 7 nap<br/>
                        - Következő ellenőrzés: {(datetime.now() + timedelta(minutes=15)).strftime('%H:%M')}
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        self._send_email(contract['contact'], subject, content)
        print(f"   ✅ SLA figyelmeztetés elküldve: {contract['client_name']} ({days_left} nap)")
    
    def _send_work_order_notification(self, work_order):
        """Küld munkalap befejezés értesítést"""
        subject = f"✅ TRIGGER: Munkalap befejezve - {work_order['work_order_id']}"
        
        content = f"""
        <html>
        <body style="font-family: Arial; background: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px;">
                <div style="background: #388e3c; color: white; padding: 15px; text-align: center; border-radius: 5px;">
                    <h2>✅ Automatikus Trigger: Munkalap befejezve</h2>
                </div>
                
                <div style="padding: 20px;">
                    <p><strong>Trigger időpontja:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    
                    <div style="background: #e8f5e8; padding: 15px; border-left: 4px solid #388e3c; margin: 15px 0;">
                        <strong>Munkalap ID:</strong> {work_order['work_order_id']}<br/>
                        <strong>Technikus:</strong> {work_order['technician']}<br/>
                        <strong>Helyszín:</strong> {work_order['location']}<br/>
                        <strong>Befejezés:</strong> {work_order['completion_time'].strftime('%Y-%m-%d %H:%M')}<br/>
                        <strong>Munkaidő:</strong> {work_order['hours']} óra<br/>
                        <strong>Költség:</strong> {work_order['cost']:,} Ft
                    </div>
                    
                    <h4>Elvégzett munka:</h4>
                    <p>{work_order['description']}</p>
                    
                    <div style="background: #e3f2fd; padding: 10px; border-radius: 5px; font-size: 12px;">
                        <strong>Trigger információ:</strong><br/>
                        - Eseményvezérelt trigger<br/>
                        - Aktiválás: munkalap státusz = "befejezve"<br/>
                        - Automatikus értesítés küldés<br/>
                        - Számla generálás indítása
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        self._send_email(work_order['customer_email'], subject, content)
        print(f"   ✅ Befejezés értesítés elküldve: {work_order['customer_email']}")
    
    def _send_email(self, recipient, subject, content):
        """Egyszerű email küldés"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender
            msg['To'] = recipient
            msg['Subject'] = subject
            
            html_part = MIMEText(content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.send_message(msg)
                
        except Exception as e:
            print(f"   ❌ Email küldés hiba: {e}")

def run_trigger_demonstration():
    """Futtatja a teljes trigger demonstrációt"""
    print("🎯 GarageReg Notifikációs Trigger Rendszer")
    print("Eseményvezérelt Értesítések Demonstrációja")
    print("=" * 60)
    
    demo = NotificationTriggerDemo()
    
    # 1. Közelgő ellenőrzések triggerelése
    demo.simulate_inspection_due_trigger()
    
    time.sleep(2)
    
    # 2. SLA lejárat triggerelése  
    demo.simulate_sla_expiring_trigger()
    
    time.sleep(2)
    
    # 3. Munkalap befejezés triggerelése
    work_order_data = {
        'work_order_id': 'WO-2024-0999',
        'technician': 'Kovács Béla',
        'location': 'Szeged, Dugonics tér 5.',
        'completion_time': datetime.now(),
        'hours': 3.5,
        'cost': 62500,
        'description': 'Kapu track tisztítása és kenése, automatika kalibrálása',
        'customer_email': 'ugyfel@szegedikft.hu'
    }
    
    demo.simulate_work_order_completed_trigger(work_order_data)
    
    print(f"\n🎉 Trigger demonstráció befejezve!")
    print(f"📧 Összesen küldött trigger emailek: 4")
    print(f"📬 MailHog felület: http://localhost:8025")
    print(f"⏰ Trigger ütemezés:")
    print(f"   • Közelgő ellenőrzés: 6 óránként")
    print(f"   • SLA lejárat: 15 percenként") 
    print(f"   • Munkalap befejezés: eseményvezérelt")

if __name__ == "__main__":
    run_trigger_demonstration()