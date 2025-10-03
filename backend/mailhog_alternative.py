#!/usr/bin/env python3
"""
Simple MailHog-like SMTP server for testing notifications
Captures emails and provides a web interface to view them
"""

import asyncio
import email
import json
import threading
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
from typing import List, Dict, Any
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Message


class EmailCapture:
    """Store captured emails"""
    def __init__(self):
        self.emails: List[Dict[str, Any]] = []
    
    def add_email(self, sender: str, recipients: List[str], data: str):
        """Add captured email"""
        try:
            msg = email.message_from_string(data)
            
            email_data = {
                'id': len(self.emails) + 1,
                'sender': sender,
                'recipients': recipients,
                'subject': msg.get('Subject', 'No Subject'),
                'date': datetime.now().isoformat(),
                'headers': dict(msg.items()),
                'body_text': self._get_text_body(msg),
                'body_html': self._get_html_body(msg),
                'raw': data
            }
            
            self.emails.append(email_data)
            print(f"📧 Email captured: {sender} -> {recipients}")
            print(f"   Subject: {email_data['subject']}")
            print(f"   Time: {email_data['date']}")
            
        except Exception as e:
            print(f"❌ Error parsing email: {e}")
    
    def _get_text_body(self, msg):
        """Extract plain text body"""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            if msg.get_content_type() == "text/plain":
                return msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        return ""
    
    def _get_html_body(self, msg):
        """Extract HTML body"""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    return part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            if msg.get_content_type() == "text/html":
                return msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        return ""
    
    def get_emails(self):
        """Get all captured emails"""
        return self.emails
    
    def clear_emails(self):
        """Clear all emails"""
        self.emails.clear()


# Global email storage
email_capture = EmailCapture()


class SMTPHandler:
    """Custom SMTP handler that captures emails"""
    
    async def handle_DATA(self, server, session, envelope):
        """Handle incoming email data"""
        email_capture.add_email(
            envelope.mail_from, 
            envelope.rcpt_tos, 
            envelope.content.decode('utf-8', errors='ignore')
        )
        return '250 Message accepted for delivery'


class WebInterface(BaseHTTPRequestHandler):
    """Simple web interface to view captured emails"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self._serve_main_page()
        elif self.path == '/api/emails':
            self._serve_emails_json()
        elif self.path.startswith('/email/'):
            email_id = int(self.path.split('/')[-1])
            self._serve_email_detail(email_id)
        elif self.path == '/clear':
            email_capture.clear_emails()
            self._redirect('/')
        else:
            self._serve_404()
    
    def _serve_main_page(self):
        """Serve main email list page"""
        emails = email_capture.get_emails()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>MailHog Alternative - Email Capture</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: #1976d2; color: white; padding: 20px; border-radius: 5px; }
                .email-list { margin-top: 20px; }
                .email-item { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
                .email-meta { font-size: 0.9em; color: #666; }
                .email-subject { font-weight: bold; margin: 5px 0; }
                .btn { background: #1976d2; color: white; padding: 10px 15px; text-decoration: none; border-radius: 3px; }
                .btn-danger { background: #d32f2f; }
                .empty { text-align: center; color: #999; margin: 50px 0; }
                .refresh { float: right; }
            </style>
            <script>
                function autoRefresh() {
                    setTimeout(() => { location.reload(); }, 5000);
                }
                window.onload = autoRefresh;
            </script>
        </head>
        <body>
            <div class="header">
                <h1>📧 MailHog Alternative - GarageReg Notifications</h1>
                <p>SMTP Server: localhost:1025 | Web Interface: localhost:8025</p>
                <a href="/clear" class="btn btn-danger">🗑️ Clear All</a>
                <a href="/" class="btn refresh">🔄 Refresh</a>
            </div>
        """
        
        if emails:
            html += f"<div class='email-list'><h2>📨 Captured Emails ({len(emails)})</h2>"
            for email_data in reversed(emails):  # Show newest first
                html += f"""
                <div class="email-item">
                    <div class="email-subject">📧 {email_data['subject']}</div>
                    <div class="email-meta">
                        <strong>From:</strong> {email_data['sender']}<br>
                        <strong>To:</strong> {', '.join(email_data['recipients'])}<br>
                        <strong>Date:</strong> {email_data['date']}<br>
                        <a href="/email/{email_data['id']}" class="btn">📋 View Details</a>
                    </div>
                </div>
                """
            html += "</div>"
        else:
            html += """
            <div class="empty">
                <h2>📭 No emails captured yet</h2>
                <p>Send test emails to localhost:1025 to see them here</p>
            </div>
            """
        
        html += "</body></html>"
        
        self._send_html(html)
    
    def _serve_email_detail(self, email_id: int):
        """Serve detailed view of specific email"""
        emails = email_capture.get_emails()
        email_data = next((e for e in emails if e['id'] == email_id), None)
        
        if not email_data:
            self._serve_404()
            return
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Email #{email_id} - MailHog Alternative</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #1976d2; color: white; padding: 20px; border-radius: 5px; }}
                .email-details {{ margin: 20px 0; }}
                .email-headers {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .email-body {{ border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 5px; }}
                .btn {{ background: #1976d2; color: white; padding: 10px 15px; text-decoration: none; border-radius: 3px; }}
                pre {{ white-space: pre-wrap; word-wrap: break-word; }}
                .tab-buttons {{ margin: 10px 0; }}
                .tab-button {{ background: #f0f0f0; border: 1px solid #ddd; padding: 10px 15px; cursor: pointer; display: inline-block; }}
                .tab-button.active {{ background: #1976d2; color: white; }}
                .tab-content {{ display: none; }}
                .tab-content.active {{ display: block; }}
            </style>
            <script>
                function showTab(tabName) {{
                    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
                    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
                    document.getElementById(tabName).classList.add('active');
                    document.querySelector(`[onclick="showTab('${{tabName}}')"]`).classList.add('active');
                }}
            </script>
        </head>
        <body>
            <div class="header">
                <h1>📧 Email Details #{email_id}</h1>
                <a href="/" class="btn">⬅️ Back to List</a>
            </div>
            
            <div class="email-details">
                <h2>📋 Email Information</h2>
                <div class="email-headers">
                    <strong>Subject:</strong> {email_data['subject']}<br>
                    <strong>From:</strong> {email_data['sender']}<br>
                    <strong>To:</strong> {', '.join(email_data['recipients'])}<br>
                    <strong>Date:</strong> {email_data['date']}
                </div>
                
                <div class="tab-buttons">
                    <div class="tab-button active" onclick="showTab('html')">🌐 HTML View</div>
                    <div class="tab-button" onclick="showTab('text')">📄 Text View</div>
                    <div class="tab-button" onclick="showTab('raw')">🔍 Raw Email</div>
                    <div class="tab-button" onclick="showTab('headers')">📝 Headers</div>
                </div>
                
                <div id="html" class="tab-content active email-body">
                    <h3>HTML Content</h3>
                    {"<iframe srcdoc='" + email_data['body_html'].replace("'", "&apos;") + "' style='width:100%; height:400px; border:1px solid #ddd;'></iframe>" if email_data['body_html'] else "<p>No HTML content</p>"}
                </div>
                
                <div id="text" class="tab-content email-body">
                    <h3>Plain Text Content</h3>
                    <pre>{email_data['body_text'] if email_data['body_text'] else 'No plain text content'}</pre>
                </div>
                
                <div id="raw" class="tab-content email-body">
                    <h3>Raw Email Source</h3>
                    <pre>{email_data['raw']}</pre>
                </div>
                
                <div id="headers" class="tab-content email-body">
                    <h3>Email Headers</h3>
                    <pre>{json.dumps(email_data['headers'], indent=2)}</pre>
                </div>
            </div>
        </body>
        </html>
        """
        
        self._send_html(html)
    
    def _serve_emails_json(self):
        """Serve emails as JSON API"""
        emails = email_capture.get_emails()
        self._send_json(emails)
    
    def _send_html(self, html: str):
        """Send HTML response"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def _send_json(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
    
    def _redirect(self, location):
        """Send redirect response"""
        self.send_response(302)
        self.send_header('Location', location)
        self.end_headers()
    
    def _serve_404(self):
        """Serve 404 page"""
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = """
        <html><body>
        <h1>404 Not Found</h1>
        <p><a href="/">Back to main page</a></p>
        </body></html>
        """
        self.wfile.write(html.encode('utf-8'))


def start_smtp_server():
    """Start SMTP server thread"""
    handler = SMTPHandler()
    controller = Controller(handler, hostname='localhost', port=1025)
    controller.start()
    print("🚀 SMTP Server started on localhost:1025")
    
    # Keep the server running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        controller.stop()


def start_web_server():
    """Start web server thread"""
    web_server = HTTPServer(('localhost', 8025), WebInterface)
    print("🌐 Web Interface started on http://localhost:8025")
    web_server.serve_forever()


if __name__ == "__main__":
    print("🎯 Starting MailHog Alternative for GarageReg Notifications")
    print("=" * 60)
    
    # Start SMTP server in background thread
    smtp_thread = threading.Thread(target=start_smtp_server, daemon=True)
    smtp_thread.start()
    
    # Give SMTP server time to start
    time.sleep(1)
    
    try:
        # Start web server (blocking)
        start_web_server()
    except KeyboardInterrupt:
        print("\n👋 Shutting down MailHog Alternative")