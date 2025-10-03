"""
Simple SMTP server for testing email notifications (MailHog alternative)
"""
import asyncio
import smtpd
import smtplib
from email.mime.text import MIMEText
import threading
import time


class TestSMTPServer(smtpd.SMTPServer):
    """A simple SMTP server that logs received emails"""
    
    def __init__(self, localaddr, remoteaddr):
        super().__init__(localaddr, remoteaddr, decode_data=True)
        self.emails = []
        
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        print(f"\n📧 Email received:")
        print(f"From: {mailfrom}")
        print(f"To: {rcpttos}")
        print(f"Subject: {data.split('Subject: ')[1].split('\n')[0] if 'Subject: ' in data else 'N/A'}")
        print("--- Email Content ---")
        
        # Extract and show HTML content
        if 'Content-Type: text/html' in data:
            html_start = data.find('\n\n') + 2
            html_content = data[html_start:]
            if len(html_content) > 500:
                print(f"{html_content[:500]}...")
                print(f"[Email content: {len(html_content)} characters total]")
            else:
                print(html_content)
        else:
            print(data)
        print("--- End Email ---\n")
        
        self.emails.append({
            'from': mailfrom,
            'to': rcpttos,
            'data': data,
            'timestamp': time.time()
        })


def start_smtp_server():
    """Start the test SMTP server in a separate thread"""
    server = TestSMTPServer(('localhost', 1025), None)
    print("🚀 Test SMTP Server started on localhost:1025")
    print("📧 Listening for emails...\n")
    
    try:
        asyncio.run(server.serve_forever())
    except KeyboardInterrupt:
        print("SMTP server stopped")


if __name__ == "__main__":
    # Start SMTP server in background
    server_thread = threading.Thread(target=start_smtp_server, daemon=True)
    server_thread.start()
    
    print("Testing SMTP server with a sample email...")
    time.sleep(1)
    
    # Test email sending
    try:
        msg = MIMEText("This is a test email from GarageReg notification system")
        msg['Subject'] = 'Test Email'
        msg['From'] = 'test@garagereg.com'
        msg['To'] = 'recipient@test.com'
        
        server = smtplib.SMTP('localhost', 1025)
        server.send_message(msg)
        server.quit()
        print("✅ Test email sent successfully!")
        
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")
    
    print("\nPress Ctrl+C to stop the server")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nServer stopped.")