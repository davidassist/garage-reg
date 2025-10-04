#!/usr/bin/env python3
"""
Egyszerű email teszt MailHog-hoz
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_test_email():
    """Send a test email to MailHog"""
    
    # Email configuration
    smtp_server = "localhost"
    smtp_port = 1025
    sender = "garagereg@system.local"
    recipients = ["teszt@garagereg.com", "manager@garagereg.com"]
    
    # Create test scenarios
    scenarios = [
        {
            'subject': 'GarageReg - Közelgő ellenőrzés: Főbejárat kapu #001',
            'content': """
            <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
                    <div style="background-color: #1976d2; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1>GarageReg Értesítő Rendszer</h1>
                        <h2>🔍 Ellenőrzés esedékes</h2>
                    </div>
                    
                    <div style="padding: 20px;">
                        <h3>Kedves Kiss János!</h3>
                        <p>Szeretnénk értesíteni, hogy a következő kapu ellenőrzése esedékes:</p>
                        
                        <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid #1976d2; margin: 15px 0;">
                            <strong>Kapu neve:</strong> Főbejárat kapu #001<br/>
                            <strong>Helyszín:</strong> Budapest, Váci út 123.<br/>
                            <strong>Ellenőrzés típusa:</strong> Rendszeres biztonsági ellenőrzés<br/>
                            <strong>Esedékesség:</strong> <span style="color: #d32f2f; font-weight: bold;">MA ESEDÉKES</span>
                        </div>
                        
                        <p><strong>Ellenőrző:</strong> Nagy Péter<br/>
                        <strong>Telefon:</strong> +36-30-123-4567</p>
                        
                        <h4>Ellenőrzési pontok:</h4>
                        <ul>
                            <li>Kapuautomatika működése</li>
                            <li>Biztonsági érzékelők tesztje</li>
                            <li>Távirányítók működése</li>
                            <li>Fizikai állapot ellenőrzése</li>
                        </ul>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="https://garagereg.com/inspections/12345" 
                               style="background-color: #1976d2; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                               📋 Ellenőrzés megtekintése
                            </a>
                        </div>
                    </div>
                    
                    <div style="text-align: center; color: #666; font-size: 12px; margin-top: 30px;">
                        GarageReg Rendszer | Generated: {timestamp}
                    </div>
                </div>
            </body>
            </html>
            """.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        },
        {
            'subject': 'GarageReg - SLA szerződés lejárat: Példa Kft.',
            'content': """
            <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
                    <div style="background-color: #f57c00; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1>GarageReg Értesítő Rendszer</h1>
                        <h2>⚠️ SLA lejárat figyelmeztetés</h2>
                    </div>
                    
                    <div style="padding: 20px;">
                        <h3>Kedves Szabó Mária!</h3>
                        <p>Szerződés lejárat figyelmeztetés:</p>
                        
                        <div style="background-color: #fff3e0; padding: 15px; border-left: 4px solid #f57c00; margin: 15px 0;">
                            <strong>Ügyfél:</strong> Példa Kft.<br/>
                            <strong>Szerződés szám:</strong> SLA-2024-001<br/>
                            <strong>Szolgáltatás:</strong> Kapu karbantartási szerződés<br/>
                            <strong>Lejárat:</strong> <span style="color: #f57c00; font-weight: bold;">7 nap múlva</span><br/>
                            <strong>SLA szint:</strong> Gold<br/>
                            <strong>Éves díj:</strong> 125,000 Ft
                        </div>
                        
                        <p><strong>Lefedett kapuk:</strong></p>
                        <ul>
                            <li>Főbejárat #001</li>
                            <li>Hátsó kapu #002</li>
                            <li>Teherkapu #003</li>
                        </ul>
                        
                        <p><strong>Kapcsolattartó:</strong> Kovács Andrea<br/>
                        <strong>Telefon:</strong> +36-1-234-5678</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="https://garagereg.com/contracts/sla-2024-001" 
                               style="background-color: #f57c00; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                               📄 Szerződés részletei
                            </a>
                        </div>
                    </div>
                    
                    <div style="text-align: center; color: #666; font-size: 12px; margin-top: 30px;">
                        GarageReg Rendszer | Generated: {timestamp}
                    </div>
                </div>
            </body>
            </html>
            """.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        },
        {
            'subject': 'GarageReg - Munkalap befejezve: WO-2024-0789',
            'content': """
            <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
                    <div style="background-color: #388e3c; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1>GarageReg Értesítő Rendszer</h1>
                        <h2>✅ Munkalap befejezve</h2>
                    </div>
                    
                    <div style="padding: 20px;">
                        <h3>Kedves Tóth László!</h3>
                        <p>Munkalap sikeresen befejezve:</p>
                        
                        <div style="background-color: #e8f5e8; padding: 15px; border-left: 4px solid #388e3c; margin: 15px 0;">
                            <strong>Munkalap szám:</strong> WO-2024-0789<br/>
                            <strong>Kapu:</strong> Garázskapu #005<br/>
                            <strong>Helyszín:</strong> Debrecen, Kossuth u. 45.<br/>
                            <strong>Technikus:</strong> Molnár György<br/>
                            <strong>Befejezés:</strong> {timestamp}<br/>
                            <strong>Munka típusa:</strong> Javítás<br/>
                            <strong>Munkaidő:</strong> 2.5 óra<br/>
                            <strong>Teljes költség:</strong> 45,500 Ft
                        </div>
                        
                        <h4>Elvégzett munka:</h4>
                        <p>Kapuautomatika szervó motor cseréje</p>
                        
                        <h4>Felhasznált alkatrészek:</h4>
                        <ul>
                            <li>Szervó motor SM-240V</li>
                            <li>Biztonsági kondenzátor 4μF</li>
                            <li>Végelállás kapcsoló</li>
                        </ul>
                        
                        <p><strong>Garancia:</strong> 12 hónap<br/>
                        <strong>Következő ellenőrzés:</strong> 6 hónap múlva</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="https://garagereg.com/workorders/wo-2024-0789" 
                               style="background-color: #388e3c; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin-right: 10px;">
                               📋 Munkalap megtekintése
                            </a>
                            <a href="https://garagereg.com/survey/wo-2024-0789" 
                               style="background-color: #1976d2; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                               ⭐ Értékelés
                            </a>
                        </div>
                    </div>
                    
                    <div style="text-align: center; color: #666; font-size: 12px; margin-top: 30px;">
                        GarageReg Rendszer | Generated: {timestamp}
                    </div>
                </div>
            </body>
            </html>
            """.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        }
    ]
    
    print("🎯 GarageReg Notifikációs Teszt")
    print("=" * 50)
    print(f"📧 SMTP Server: {smtp_server}:{smtp_port}")
    print(f"📬 MailHog Web UI: http://localhost:8025")
    print(f"📮 {len(scenarios)} teszt email küldése...")
    
    for i, scenario in enumerate(scenarios, 1):
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = sender
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = scenario['subject']
            
            # Add HTML content
            html_part = MIMEText(scenario['content'], 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.send_message(msg)
            
            print(f"   ✅ Email {i}: {scenario['subject'][:50]}...")
            
        except Exception as e:
            print(f"   ❌ Email {i} küldés hiba: {e}")
    
    print(f"\n🎉 Teszt befejezve!")
    print(f"📬 Ellenőrizd az email-eket: http://localhost:8025")

if __name__ == "__main__":
    send_test_email()