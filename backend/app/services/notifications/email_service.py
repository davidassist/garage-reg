"""
Email service with MJML template support and MailHog integration
"""
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any, Optional, List
from jinja2 import Environment, FileSystemLoader, Template
from datetime import datetime

from .models import EmailMessage, NotificationTrigger, EmailTemplate
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class MJMLRenderer:
    """MJML template renderer with Handlebars support"""
    
    def __init__(self):
        self.template_dir = os.path.join(
            os.path.dirname(__file__), "templates", "email"
        )
        
        # Initialize Jinja2 environment with Handlebars-like syntax
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.template_dir),
            variable_start_string='{{',
            variable_end_string='}}',
            block_start_string='{%',
            block_end_string='%}',
            comment_start_string='{#',
            comment_end_string='#}',
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.jinja_env.filters['datetime'] = self._format_datetime
        self.jinja_env.filters['currency'] = self._format_currency
        self.jinja_env.filters['deadline'] = self._format_deadline
    
    def _format_datetime(self, dt: datetime, format_str: str = "%Y.%m.%d %H:%M") -> str:
        """Format datetime for Hungarian locale"""
        if not dt:
            return ""
        # Handle both timezone-aware and naive datetime objects
        if hasattr(dt, 'strftime'):
            return dt.strftime(format_str)
        return str(dt)
    
    def _format_currency(self, amount: float, currency: str = "HUF") -> str:
        """Format currency for Hungarian locale"""
        if currency == "HUF":
            return f"{amount:,.0f} Ft"
        return f"{amount:,.2f} {currency}"
    
    def _format_deadline(self, dt: datetime) -> str:
        """Format deadline with urgency indicator"""
        if not dt:
            return ""
        
        # Handle both timezone-aware and naive datetime objects
        if dt.tzinfo is not None:
            now = datetime.now(dt.tzinfo)
        else:
            now = datetime.now()
        
        diff = dt - now
        
        if diff.days < 0:
            return f"LEJÁRT ({abs(diff.days)} napja)"
        elif diff.days == 0:
            return "MA ESEDÉKES"
        elif diff.days <= 3:
            return f"SÜRGŐS ({diff.days} nap)"
        else:
            return f"{diff.days} nap múlva"
    
    def render_mjml(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render MJML template to HTML"""
        try:
            template = self.jinja_env.get_template(f"{template_name}.mjml")
            mjml_content = template.render(**context)
            
            # Convert MJML to HTML (simplified - in production use mjml-python)
            html_content = self._mjml_to_html(mjml_content)
            
            return html_content
            
        except Exception as e:
            logger.error(f"Failed to render MJML template {template_name}: {e}")
            # Fallback to basic HTML template
            return self._render_fallback_html(template_name, context)
    
    def _mjml_to_html(self, mjml_content: str) -> str:
        """
        Convert MJML to HTML
        
        In production, use:
        - mjml-python package
        - MJML API service
        - Pre-compiled templates
        """
        # Simplified MJML to HTML conversion
        # Replace MJML tags with HTML equivalents
        html = mjml_content
        
        # Basic MJML tag replacements
        replacements = {
            '<mjml>': '<!DOCTYPE html><html>',
            '</mjml>': '</html>',
            '<mj-head>': '<head>',
            '</mj-head>': '</head>',
            '<mj-body>': '<body style="margin:0;padding:0;background-color:#f4f4f4;">',
            '</mj-body>': '</body>',
            '<mj-section>': '<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">',
            '</mj-section>': '</td></tr></table>',
            '<mj-column>': '<div style="display:inline-block;vertical-align:top;width:100%;">',
            '</mj-column>': '</div>',
            '<mj-text': '<div',
            '</mj-text>': '</div>',
            '<mj-button': '<a',
            '</mj-button>': '</a>',
            '<mj-divider/>': '<hr style="border:none;border-top:1px solid #ccc;margin:20px 0;">',
        }
        
        for mjml_tag, html_tag in replacements.items():
            html = html.replace(mjml_tag, html_tag)
        
        return html
    
    def _render_fallback_html(self, template_name: str, context: Dict[str, Any]) -> str:
        """Fallback HTML template if MJML fails"""
        try:
            template = self.jinja_env.get_template(f"{template_name}_fallback.html")
            return template.render(**context)
        except:
            # Ultimate fallback - basic HTML
            return f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2>GarageReg Értesítés</h2>
                <p>Egy esemény történt a rendszerben.</p>
                <p>Template: {template_name}</p>
                <p>Időpont: {datetime.now().strftime('%Y.%m.%d %H:%M')}</p>
            </body>
            </html>
            """


class EmailService:
    """Email service with SMTP and MailHog support"""
    
    def __init__(self):
        self.mjml_renderer = MJMLRenderer()
        self.smtp_host = getattr(settings, 'SMTP_HOST', 'localhost')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 1025)  # MailHog default
        self.smtp_user = getattr(settings, 'SMTP_USER', None)
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', None)
        self.smtp_tls = getattr(settings, 'SMTP_TLS', False)
    
    async def send_email(self, message: EmailMessage) -> Dict[str, Any]:
        """Send email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = message.subject
            msg['From'] = f"{message.from_name} <{message.from_email}>"
            msg['To'] = f"{message.to_name} <{message.to_email}>" if message.to_name else message.to_email
            
            # Add text content
            if message.text_content:
                text_part = MIMEText(message.text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(message.html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Add attachments
            for attachment in message.attachments:
                self._add_attachment(msg, attachment)
            
            # Send via SMTP
            await self._send_smtp(msg, message.to_email)
            
            logger.info(f"Email sent successfully to {message.to_email}")
            
            return {
                'status': 'sent',
                'message': 'Email sent successfully',
                'recipient': message.to_email
            }
            
        except Exception as e:
            logger.error(f"Failed to send email to {message.to_email}: {e}")
            return {
                'status': 'failed',
                'message': str(e),
                'recipient': message.to_email
            }
    
    async def _send_smtp(self, message: MIMEMultipart, recipient: str):
        """Send message via SMTP"""
        server = None
        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            
            if self.smtp_tls:
                server.starttls()
            
            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)
            
            server.send_message(message, to_addrs=[recipient])
            
        finally:
            if server:
                server.quit()
    
    def _add_attachment(self, message: MIMEMultipart, attachment: Dict[str, Any]):
        """Add attachment to email message"""
        try:
            if 'content' in attachment and 'filename' in attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment['content'])
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {attachment["filename"]}'
                )
                message.attach(part)
        except Exception as e:
            logger.warning(f"Failed to add attachment: {e}")
    
    async def render_and_send(
        self,
        template_name: str,
        recipient: str,
        context: Dict[str, Any],
        subject: str,
        recipient_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Render template and send email"""
        
        # Render HTML content
        html_content = self.mjml_renderer.render_mjml(template_name, context)
        
        # Create email message
        message = EmailMessage(
            to_email=recipient,
            to_name=recipient_name,
            subject=subject,
            html_content=html_content
        )
        
        # Send email
        return await self.send_email(message)
    
    def get_template_variables(self, trigger: NotificationTrigger) -> List[str]:
        """Get available variables for a notification trigger"""
        
        common_vars = [
            'user_name', 'user_email', 'organization_name',
            'current_date', 'current_time'
        ]
        
        trigger_vars = {
            NotificationTrigger.INSPECTION_DUE: [
                'gate_name', 'gate_location', 'inspection_type',
                'due_date', 'days_until_due', 'inspector_name'
            ],
            NotificationTrigger.SLA_EXPIRING: [
                'work_order_id', 'work_order_title', 'client_name',
                'sla_deadline', 'hours_remaining', 'priority'
            ],
            NotificationTrigger.WORK_ORDER_COMPLETED: [
                'work_order_id', 'work_order_title', 'completed_by',
                'completion_date', 'client_name', 'results_summary'
            ],
            NotificationTrigger.GATE_FAULT: [
                'gate_name', 'gate_location', 'fault_description',
                'severity', 'reported_by', 'report_time'
            ]
        }
        
        return common_vars + trigger_vars.get(trigger, [])