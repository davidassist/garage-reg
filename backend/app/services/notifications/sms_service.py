"""
SMS notification service stub with provider support
"""
import logging
from typing import Dict, Any, Optional, List
import aiohttp
from datetime import datetime, timezone

from .models import SMSMessage, NotificationStatus, NotificationTrigger
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SMSProvider:
    """Base SMS provider interface"""
    
    async def send_sms(self, message: SMSMessage) -> Dict[str, Any]:
        raise NotImplementedError
    
    def format_phone_number(self, phone: str) -> str:
        """Format phone number to international format"""
        # Remove spaces and special characters
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # Add Hungarian country code if needed
        if len(clean_phone) == 9 and clean_phone.startswith('06'):
            return f"+36{clean_phone[2:]}"
        elif len(clean_phone) == 9:
            return f"+36{clean_phone[1:]}"
        elif len(clean_phone) == 8:
            return f"+36{clean_phone}"
        elif clean_phone.startswith('36'):
            return f"+{clean_phone}"
        elif clean_phone.startswith('+36'):
            return clean_phone
        else:
            return f"+36{clean_phone}"


class TwilioProvider(SMSProvider):
    """Twilio SMS provider"""
    
    def __init__(self):
        self.account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        self.auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        self.from_number = getattr(settings, 'TWILIO_FROM_NUMBER', None)
        self.enabled = bool(self.account_sid and self.auth_token)
    
    async def send_sms(self, message: SMSMessage) -> Dict[str, Any]:
        if not self.enabled:
            return {
                'status': 'skipped',
                'message': 'Twilio not configured',
                'provider': 'twilio'
            }
        
        try:
            # In production, use Twilio SDK
            # from twilio.rest import Client
            # client = Client(self.account_sid, self.auth_token)
            
            # Simulate Twilio API call
            formatted_phone = self.format_phone_number(message.phone_number)
            
            logger.info(f"[TWILIO STUB] SMS to {formatted_phone}: {message.message}")
            
            return {
                'status': 'sent',
                'provider': 'twilio',
                'to': formatted_phone,
                'message_id': f"twilio_msg_{datetime.now().timestamp()}",
                'timestamp': datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"Twilio SMS failed: {e}")
            return {
                'status': 'failed',
                'provider': 'twilio',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc)
            }


class VodafoneProvider(SMSProvider):
    """Vodafone Hungary SMS provider"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'VODAFONE_API_KEY', None)
        self.sender_id = getattr(settings, 'VODAFONE_SENDER_ID', 'GarageReg')
        self.api_url = "https://api.vodafone.hu/sms/v1/send"
        self.enabled = bool(self.api_key)
    
    async def send_sms(self, message: SMSMessage) -> Dict[str, Any]:
        if not self.enabled:
            return {
                'status': 'skipped',
                'message': 'Vodafone API not configured',
                'provider': 'vodafone'
            }
        
        try:
            formatted_phone = self.format_phone_number(message.phone_number)
            
            payload = {
                'to': formatted_phone,
                'message': message.message,
                'sender': self.sender_id
            }
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Simulate API call
            logger.info(f"[VODAFONE STUB] SMS to {formatted_phone}: {message.message}")
            
            return {
                'status': 'sent',
                'provider': 'vodafone',
                'to': formatted_phone,
                'message_id': f"vodafone_msg_{datetime.now().timestamp()}",
                'timestamp': datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"Vodafone SMS failed: {e}")
            return {
                'status': 'failed',
                'provider': 'vodafone',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc)
            }


class TelekomProvider(SMSProvider):
    """Magyar Telekom SMS provider"""
    
    def __init__(self):
        self.username = getattr(settings, 'TELEKOM_USERNAME', None)
        self.password = getattr(settings, 'TELEKOM_PASSWORD', None)
        self.sender_id = getattr(settings, 'TELEKOM_SENDER_ID', 'GarageReg')
        self.enabled = bool(self.username and self.password)
    
    async def send_sms(self, message: SMSMessage) -> Dict[str, Any]:
        if not self.enabled:
            return {
                'status': 'skipped',
                'message': 'Telekom not configured',
                'provider': 'telekom'
            }
        
        try:
            formatted_phone = self.format_phone_number(message.phone_number)
            
            logger.info(f"[TELEKOM STUB] SMS to {formatted_phone}: {message.message}")
            
            return {
                'status': 'sent',
                'provider': 'telekom',
                'to': formatted_phone,
                'message_id': f"telekom_msg_{datetime.now().timestamp()}",
                'timestamp': datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"Telekom SMS failed: {e}")
            return {
                'status': 'failed',
                'provider': 'telekom',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc)
            }


class SMSService:
    """SMS notification service with multiple provider support"""
    
    def __init__(self):
        self.providers = {
            'twilio': TwilioProvider(),
            'vodafone': VodafoneProvider(),
            'telekom': TelekomProvider()
        }
        
        # Primary provider selection
        self.primary_provider = getattr(settings, 'SMS_PRIMARY_PROVIDER', 'twilio')
        self.fallback_enabled = getattr(settings, 'SMS_FALLBACK_ENABLED', True)
        
        # SMS templates
        self.templates = {
            NotificationTrigger.INSPECTION_DUE: "GarageReg: {gate_name} kapu ellenőrzése esedékes {due_date}-ig. További info: {url}",
            NotificationTrigger.SLA_EXPIRING: "GarageReg SÜRGŐS: #{work_order_id} munkalap SLA {hours_remaining}h múlva lejár. Azonnali intézkedés szükséges!",
            NotificationTrigger.WORK_ORDER_COMPLETED: "GarageReg: #{work_order_id} munkalap elkészült. Elvégző: {completed_by}. Részletek: {url}",
            NotificationTrigger.GATE_FAULT: "GarageReg RIASZTÁS: {gate_name} kapu hibás! {fault_description}. Azonnal ellenőrizze!",
            NotificationTrigger.MAINTENANCE_DUE: "GarageReg: Karbantartás esedékes - {gate_name}. Időpont: {due_date}",
        }
    
    async def send_sms(
        self,
        phone_number: str,
        message: str,
        sender_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send SMS via configured provider with fallback"""
        
        sms_message = SMSMessage(
            phone_number=phone_number,
            message=message,
            sender_id=sender_id or "GarageReg"
        )
        
        # Try primary provider first
        primary_result = await self._send_via_provider(
            self.primary_provider, sms_message
        )
        
        if primary_result['status'] == 'sent':
            return primary_result
        
        # Try fallback providers if enabled
        if self.fallback_enabled:
            for provider_name, provider in self.providers.items():
                if provider_name == self.primary_provider:
                    continue
                
                logger.info(f"Trying fallback SMS provider: {provider_name}")
                
                fallback_result = await self._send_via_provider(
                    provider_name, sms_message
                )
                
                if fallback_result['status'] == 'sent':
                    return fallback_result
        
        # All providers failed
        return {
            'status': 'failed',
            'message': 'All SMS providers failed',
            'primary_result': primary_result,
            'timestamp': datetime.now(timezone.utc)
        }
    
    async def _send_via_provider(
        self,
        provider_name: str,
        message: SMSMessage
    ) -> Dict[str, Any]:
        """Send SMS via specific provider"""
        
        provider = self.providers.get(provider_name)
        if not provider:
            return {
                'status': 'failed',
                'message': f'Unknown provider: {provider_name}',
                'provider': provider_name
            }
        
        return await provider.send_sms(message)
    
    async def send_notification_sms(
        self,
        trigger: NotificationTrigger,
        phone_number: str,
        template_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send SMS notification using predefined templates"""
        
        template = self.templates.get(trigger)
        if not template:
            return {
                'status': 'failed',
                'message': f'No SMS template for trigger: {trigger.value}',
                'timestamp': datetime.now(timezone.utc)
            }
        
        try:
            # Format message with template data
            message = template.format(**template_data)
            
            # Truncate if too long (SMS limit is usually 160 chars)
            if len(message) > 160:
                message = message[:157] + "..."
            
            return await self.send_sms(phone_number, message)
            
        except Exception as e:
            logger.error(f"SMS template formatting failed: {e}")
            return {
                'status': 'failed',
                'error': f'Template error: {str(e)}',
                'timestamp': datetime.now(timezone.utc)
            }
    
    def get_sms_template_variables(self, trigger: NotificationTrigger) -> List[str]:
        """Get available variables for SMS templates"""
        
        template = self.templates.get(trigger, "")
        
        # Extract variables from template
        import re
        variables = re.findall(r'\{(\w+)\}', template)
        
        return list(set(variables))
    
    async def validate_phone_number(self, phone_number: str) -> Dict[str, Any]:
        """Validate and format phone number"""
        
        try:
            provider = list(self.providers.values())[0]  # Use any provider for formatting
            formatted = provider.format_phone_number(phone_number)
            
            # Basic validation
            if not formatted.startswith('+36'):
                return {
                    'valid': False,
                    'message': 'Invalid Hungarian phone number',
                    'formatted': None
                }
            
            if len(formatted) != 12:  # +36 + 9 digits
                return {
                    'valid': False,
                    'message': 'Invalid phone number length',
                    'formatted': None
                }
            
            return {
                'valid': True,
                'formatted': formatted,
                'original': phone_number
            }
            
        except Exception as e:
            return {
                'valid': False,
                'message': str(e),
                'formatted': None
            }
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all SMS providers"""
        
        status = {}
        
        for name, provider in self.providers.items():
            status[name] = {
                'enabled': provider.enabled,
                'type': provider.__class__.__name__,
                'is_primary': name == self.primary_provider
            }
        
        return {
            'providers': status,
            'primary_provider': self.primary_provider,
            'fallback_enabled': self.fallback_enabled
        }