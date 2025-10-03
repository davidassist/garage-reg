"""
Main notification service orchestrating email, SMS, and webhook notifications
"""
import logging
from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime, timezone

from .models import (
    NotificationRequest, NotificationResponse, NotificationTrigger, 
    NotificationRecipient, NotificationStatus, NotificationType,
    NotificationPriority
)
from .email_service import EmailService
from .sms_service import SMSService
from .webhook_service import WebhookAdapter
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class NotificationService:
    """
    Main notification service coordinating all notification channels
    """
    
    def __init__(self):
        self.email_service = EmailService()
        self.sms_service = SMSService()
        self.webhook_adapter = WebhookAdapter()
        
        # Service configuration
        self.enabled_channels = {
            NotificationType.EMAIL: getattr(settings, 'NOTIFICATIONS_EMAIL_ENABLED', True),
            NotificationType.SMS: getattr(settings, 'NOTIFICATIONS_SMS_ENABLED', True),
            NotificationType.WEBHOOK: getattr(settings, 'NOTIFICATIONS_WEBHOOK_ENABLED', True),
        }
        
        # Priority-based channel selection
        self.priority_channels = {
            NotificationPriority.LOW: [NotificationType.EMAIL],
            NotificationPriority.NORMAL: [NotificationType.EMAIL, NotificationType.WEBHOOK],
            NotificationPriority.HIGH: [NotificationType.EMAIL, NotificationType.SMS, NotificationType.WEBHOOK],
            NotificationPriority.URGENT: [NotificationType.EMAIL, NotificationType.SMS, NotificationType.WEBHOOK],
        }
    
    async def send_notification(self, request: NotificationRequest) -> Dict[str, Any]:
        """Send notification via appropriate channels based on priority"""
        
        # Determine channels based on priority
        channels = self.priority_channels.get(
            request.priority, 
            [NotificationType.EMAIL]
        )
        
        # Filter enabled channels
        active_channels = [
            channel for channel in channels 
            if self.enabled_channels.get(channel, False)
        ]
        
        if not active_channels:
            logger.warning("No active notification channels configured")
            return {
                'status': 'skipped',
                'message': 'No active channels',
                'channels_attempted': 0
            }
        
        # Send notifications
        results = {}
        
        # Send via each channel concurrently
        tasks = []
        
        if NotificationType.EMAIL in active_channels:
            tasks.append(self._send_email_notifications(request))
        
        if NotificationType.SMS in active_channels:
            tasks.append(self._send_sms_notifications(request))
        
        if NotificationType.WEBHOOK in active_channels:
            tasks.append(self._send_webhook_notifications(request))
        
        # Execute all notifications concurrently
        if tasks:
            channel_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(channel_results):
                channel_type = active_channels[i]
                if isinstance(result, Exception):
                    results[channel_type.value] = {
                        'status': 'failed',
                        'error': str(result)
                    }
                else:
                    results[channel_type.value] = result
        
        # Calculate overall status
        successful_channels = len([
            r for r in results.values() 
            if r.get('status') in ['sent', 'delivered']
        ])
        
        overall_status = 'sent' if successful_channels > 0 else 'failed'
        
        return {
            'status': overall_status,
            'trigger': request.trigger.value,
            'channels_attempted': len(active_channels),
            'channels_successful': successful_channels,
            'priority': request.priority.value,
            'recipients': len(request.recipients),
            'results': results,
            'timestamp': datetime.now(timezone.utc)
        }
    
    async def _send_email_notifications(self, request: NotificationRequest) -> Dict[str, Any]:
        """Send email notifications to all recipients"""
        
        results = []
        template_name = self._get_email_template(request.trigger)
        
        for recipient in request.recipients:
            if not recipient.email:
                continue
            
            try:
                # Prepare context data
                context = {
                    **request.template_data,
                    'user_name': recipient.name or 'Kedves Felhasználó',
                    'current_date': datetime.now(timezone.utc),
                    'current_time': datetime.now(timezone.utc),
                    'organization_name': getattr(settings, 'ORGANIZATION_NAME', 'GarageReg'),
                    'system_url': getattr(settings, 'FRONTEND_URL', 'https://app.garagereg.com')
                }
                
                # Generate subject
                subject = self._get_email_subject(request.trigger, request.template_data)
                
                # Send email
                result = await self.email_service.render_and_send(
                    template_name=template_name,
                    recipient=recipient.email,
                    context=context,
                    subject=subject,
                    recipient_name=recipient.name
                )
                
                results.append({
                    'recipient': recipient.email,
                    'result': result
                })
                
            except Exception as e:
                logger.error(f"Failed to send email to {recipient.email}: {e}")
                results.append({
                    'recipient': recipient.email,
                    'result': {'status': 'failed', 'error': str(e)}
                })
        
        # Summary
        successful = len([r for r in results if r['result']['status'] == 'sent'])
        
        return {
            'status': 'sent' if successful > 0 else 'failed',
            'channel': 'email',
            'recipients_attempted': len(results),
            'recipients_successful': successful,
            'details': results
        }
    
    async def _send_sms_notifications(self, request: NotificationRequest) -> Dict[str, Any]:
        """Send SMS notifications to all recipients"""
        
        results = []
        
        for recipient in request.recipients:
            if not recipient.phone:
                continue
            
            try:
                result = await self.sms_service.send_notification_sms(
                    trigger=request.trigger,
                    phone_number=recipient.phone,
                    template_data=request.template_data
                )
                
                results.append({
                    'recipient': recipient.phone,
                    'result': result
                })
                
            except Exception as e:
                logger.error(f"Failed to send SMS to {recipient.phone}: {e}")
                results.append({
                    'recipient': recipient.phone,
                    'result': {'status': 'failed', 'error': str(e)}
                })
        
        # Summary
        successful = len([r for r in results if r['result']['status'] == 'sent'])
        
        return {
            'status': 'sent' if successful > 0 else 'failed',
            'channel': 'sms',
            'recipients_attempted': len(results),
            'recipients_successful': successful,
            'details': results
        }
    
    async def _send_webhook_notifications(self, request: NotificationRequest) -> Dict[str, Any]:
        """Send webhook notifications"""
        
        try:
            # Get organization and user IDs from metadata or template data
            organization_id = request.metadata.get('organization_id') or request.template_data.get('organization_id')
            user_id = request.metadata.get('user_id') or request.template_data.get('user_id')
            
            result = await self.webhook_adapter.send_webhook(
                trigger=request.trigger,
                payload_data=request.template_data,
                organization_id=organization_id,
                user_id=user_id
            )
            
            return {
                'status': 'sent' if result['targets_successful'] > 0 else 'failed',
                'channel': 'webhook',
                'targets_attempted': result['targets_attempted'],
                'targets_successful': result['targets_successful'],
                'details': result
            }
            
        except Exception as e:
            logger.error(f"Failed to send webhooks: {e}")
            return {
                'status': 'failed',
                'channel': 'webhook',
                'error': str(e)
            }
    
    def _get_email_template(self, trigger: NotificationTrigger) -> str:
        """Get email template name for notification trigger"""
        
        template_mapping = {
            NotificationTrigger.INSPECTION_DUE: 'inspection_due',
            NotificationTrigger.INSPECTION_OVERDUE: 'inspection_due',  # Same template with different data
            NotificationTrigger.SLA_EXPIRING: 'sla_expiring',
            NotificationTrigger.SLA_EXPIRED: 'sla_expiring',  # Same template
            NotificationTrigger.WORK_ORDER_COMPLETED: 'work_order_completed',
            NotificationTrigger.WORK_ORDER_ASSIGNED: 'work_order_assigned',
            NotificationTrigger.MAINTENANCE_DUE: 'maintenance_due',
            NotificationTrigger.GATE_FAULT: 'gate_fault',
        }
        
        return template_mapping.get(trigger, 'generic_notification')
    
    def _get_email_subject(self, trigger: NotificationTrigger, data: Dict[str, Any]) -> str:
        """Generate email subject for notification trigger"""
        
        subjects = {
            NotificationTrigger.INSPECTION_DUE: f"Ellenőrzés esedékes - {data.get('gate_name', 'Kapu')}",
            NotificationTrigger.INSPECTION_OVERDUE: f"LEJÁRT ellenőrzés - {data.get('gate_name', 'Kapu')}",
            NotificationTrigger.SLA_EXPIRING: f"SLA figyelmeztetés - #{data.get('work_order_id', 'N/A')}",
            NotificationTrigger.SLA_EXPIRED: f"SLA LEJÁRT - #{data.get('work_order_id', 'N/A')}",
            NotificationTrigger.WORK_ORDER_COMPLETED: f"Munkalap kész - #{data.get('work_order_id', 'N/A')}",
            NotificationTrigger.WORK_ORDER_ASSIGNED: f"Új munkalap - #{data.get('work_order_id', 'N/A')}",
            NotificationTrigger.MAINTENANCE_DUE: f"Karbantartás esedékes - {data.get('gate_name', 'Kapu')}",
            NotificationTrigger.GATE_FAULT: f"KAPU HIBA - {data.get('gate_name', 'Kapu')}",
        }
        
        return subjects.get(trigger, "GarageReg Értesítés")
    
    async def send_inspection_due_notification(
        self,
        gate_name: str,
        gate_location: str,
        inspection_type: str,
        due_date: datetime,
        inspector_email: str,
        inspector_name: str,
        gate_id: int,
        days_until_due: int = 0
    ) -> Dict[str, Any]:
        """Send inspection due notification"""
        
        priority = NotificationPriority.URGENT if days_until_due <= 0 else (
            NotificationPriority.HIGH if days_until_due <= 3 else NotificationPriority.NORMAL
        )
        
        request = NotificationRequest(
            trigger=NotificationTrigger.INSPECTION_DUE,
            recipients=[
                NotificationRecipient(
                    email=inspector_email,
                    name=inspector_name
                )
            ],
            template_data={
                'gate_name': gate_name,
                'gate_location': gate_location,
                'inspection_type': inspection_type,
                'due_date': due_date,
                'inspector_name': inspector_name,
                'gate_id': gate_id,
                'days_until_due': days_until_due
            },
            priority=priority
        )
        
        return await self.send_notification(request)
    
    async def send_sla_expiring_notification(
        self,
        work_order_id: str,
        work_order_title: str,
        client_name: str,
        sla_deadline: datetime,
        hours_remaining: float,
        priority: str,
        assignee_email: str,
        assignee_name: str
    ) -> Dict[str, Any]:
        """Send SLA expiring notification"""
        
        notification_priority = NotificationPriority.URGENT if hours_remaining <= 2 else (
            NotificationPriority.HIGH if hours_remaining <= 24 else NotificationPriority.NORMAL
        )
        
        request = NotificationRequest(
            trigger=NotificationTrigger.SLA_EXPIRING,
            recipients=[
                NotificationRecipient(
                    email=assignee_email,
                    name=assignee_name
                )
            ],
            template_data={
                'work_order_id': work_order_id,
                'work_order_title': work_order_title,
                'client_name': client_name,
                'sla_deadline': sla_deadline,
                'hours_remaining': hours_remaining,
                'priority': priority
            },
            priority=notification_priority
        )
        
        return await self.send_notification(request)
    
    async def send_work_order_completed_notification(
        self,
        work_order_id: str,
        work_order_title: str,
        client_name: str,
        completed_by: str,
        completion_date: datetime,
        results_summary: str,
        client_email: str,
        manager_email: str
    ) -> Dict[str, Any]:
        """Send work order completed notification"""
        
        request = NotificationRequest(
            trigger=NotificationTrigger.WORK_ORDER_COMPLETED,
            recipients=[
                NotificationRecipient(
                    email=client_email,
                    name=client_name
                ),
                NotificationRecipient(
                    email=manager_email,
                    name="Manager"
                )
            ],
            template_data={
                'work_order_id': work_order_id,
                'work_order_title': work_order_title,
                'client_name': client_name,
                'completed_by': completed_by,
                'completion_date': completion_date,
                'results_summary': results_summary
            },
            priority=NotificationPriority.NORMAL
        )
        
        return await self.send_notification(request)
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get notification service status"""
        
        return {
            'email': {
                'enabled': self.enabled_channels.get(NotificationType.EMAIL, False),
                'smtp_host': self.email_service.smtp_host,
                'smtp_port': self.email_service.smtp_port
            },
            'sms': {
                'enabled': self.enabled_channels.get(NotificationType.SMS, False),
                'providers': self.sms_service.get_provider_status()
            },
            'webhook': {
                'enabled': self.enabled_channels.get(NotificationType.WEBHOOK, False),
                'endpoints_configured': len([
                    url for url in self.webhook_adapter.webhook_endpoints.values() 
                    if url
                ])
            },
            'priority_channels': {
                priority.value: [channel.value for channel in channels]
                for priority, channels in self.priority_channels.items()
            }
        }