"""
Webhook adapter service for external system integrations
"""
import hashlib
import hmac
import json
import logging
from typing import Dict, Any, Optional, List
import aiohttp
import asyncio
from datetime import datetime, timezone

from .models import WebhookPayload, NotificationTrigger, NotificationStatus
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class WebhookAdapter:
    """Webhook service for external integrations"""
    
    def __init__(self):
        self.default_timeout = 30  # seconds
        self.max_retries = 3
        self.retry_delays = [1, 5, 15]  # seconds
        
        # Webhook endpoints configuration
        self.webhook_endpoints = {
            'maintenance_system': getattr(settings, 'WEBHOOK_MAINTENANCE_URL', None),
            'client_portal': getattr(settings, 'WEBHOOK_CLIENT_URL', None),
            'monitoring': getattr(settings, 'WEBHOOK_MONITORING_URL', None),
            'erp_system': getattr(settings, 'WEBHOOK_ERP_URL', None),
        }
        
        # Webhook secrets for HMAC signatures
        self.webhook_secrets = {
            'maintenance_system': getattr(settings, 'WEBHOOK_MAINTENANCE_SECRET', None),
            'client_portal': getattr(settings, 'WEBHOOK_CLIENT_SECRET', None),
            'monitoring': getattr(settings, 'WEBHOOK_MONITORING_SECRET', None),
            'erp_system': getattr(settings, 'WEBHOOK_ERP_SECRET', None),
        }
    
    async def send_webhook(
        self,
        trigger: NotificationTrigger,
        payload_data: Dict[str, Any],
        targets: Optional[List[str]] = None,
        organization_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send webhook notifications to configured endpoints"""
        
        # Create webhook payload
        payload = WebhookPayload(
            event=trigger,
            timestamp=datetime.now(timezone.utc),
            data=payload_data,
            organization_id=organization_id,
            user_id=user_id
        )
        
        # Determine target endpoints
        if targets is None:
            targets = self._get_targets_for_trigger(trigger)
        
        results = {}
        
        # Send to each target endpoint
        for target in targets:
            if target not in self.webhook_endpoints:
                logger.warning(f"Unknown webhook target: {target}")
                continue
                
            endpoint_url = self.webhook_endpoints[target]
            if not endpoint_url:
                logger.warning(f"No URL configured for webhook target: {target}")
                continue
            
            try:
                result = await self._send_to_endpoint(
                    endpoint_url, payload, target
                )
                results[target] = result
                
            except Exception as e:
                logger.error(f"Failed to send webhook to {target}: {e}")
                results[target] = {
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now(timezone.utc)
                }
        
        return {
            'trigger': trigger.value,
            'targets_attempted': len(targets),
            'targets_successful': len([r for r in results.values() if r.get('status') == 'sent']),
            'results': results
        }
    
    async def _send_to_endpoint(
        self,
        url: str,
        payload: WebhookPayload,
        target: str
    ) -> Dict[str, Any]:
        """Send webhook to specific endpoint with retries"""
        
        # Generate signature if secret is available
        secret = self.webhook_secrets.get(target)
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'GarageReg-Webhook/1.0',
            'X-GarageReg-Event': payload.event.value,
            'X-GarageReg-Timestamp': payload.timestamp.isoformat(),
        }
        
        payload_json = payload.model_dump_json()
        
        if secret:
            signature = self._generate_signature(payload_json, secret)
            headers['X-GarageReg-Signature'] = signature
        
        # Attempt delivery with retries
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        url,
                        data=payload_json,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=self.default_timeout)
                    ) as response:
                        
                        response_data = {
                            'status': 'sent' if response.status < 400 else 'failed',
                            'status_code': response.status,
                            'response_text': await response.text(),
                            'attempt': attempt + 1,
                            'timestamp': datetime.now(timezone.utc)
                        }
                        
                        if response.status < 400:
                            logger.info(f"Webhook delivered to {target}: {response.status}")
                            return response_data
                        else:
                            logger.warning(f"Webhook delivery failed to {target}: {response.status}")
                            last_exception = Exception(f"HTTP {response.status}: {await response.text()}")
                            
            except Exception as e:
                last_exception = e
                logger.warning(f"Webhook attempt {attempt + 1} to {target} failed: {e}")
                
                # Wait before retry (except on last attempt)
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delays[attempt])
        
        # All attempts failed
        return {
            'status': 'failed',
            'error': str(last_exception),
            'attempts': self.max_retries,
            'timestamp': datetime.now(timezone.utc)
        }
    
    def _generate_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC-SHA256 signature for webhook verification"""
        mac = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        )
        return f"sha256={mac.hexdigest()}"
    
    def _get_targets_for_trigger(self, trigger: NotificationTrigger) -> List[str]:
        """Get appropriate webhook targets for notification trigger"""
        
        # Default targets for different trigger types
        trigger_targets = {
            NotificationTrigger.INSPECTION_DUE: ['maintenance_system', 'monitoring'],
            NotificationTrigger.INSPECTION_OVERDUE: ['maintenance_system', 'monitoring', 'client_portal'],
            NotificationTrigger.SLA_EXPIRING: ['maintenance_system', 'client_portal', 'monitoring'],
            NotificationTrigger.SLA_EXPIRED: ['maintenance_system', 'client_portal', 'monitoring'],
            NotificationTrigger.WORK_ORDER_COMPLETED: ['client_portal', 'erp_system'],
            NotificationTrigger.WORK_ORDER_ASSIGNED: ['maintenance_system'],
            NotificationTrigger.MAINTENANCE_DUE: ['maintenance_system', 'monitoring'],
            NotificationTrigger.GATE_FAULT: ['maintenance_system', 'client_portal', 'monitoring'],
            NotificationTrigger.USER_REGISTERED: ['erp_system'],
            NotificationTrigger.PASSWORD_RESET: []  # No webhook for security events
        }
        
        return trigger_targets.get(trigger, ['monitoring'])
    
    async def verify_webhook_signature(
        self,
        payload: str,
        signature: str,
        target: str
    ) -> bool:
        """Verify incoming webhook signature"""
        
        secret = self.webhook_secrets.get(target)
        if not secret:
            logger.warning(f"No secret configured for target: {target}")
            return False
        
        expected_signature = self._generate_signature(payload, secret)
        
        # Constant-time comparison to prevent timing attacks
        return hmac.compare_digest(signature, expected_signature)
    
    def create_webhook_payload(
        self,
        trigger: NotificationTrigger,
        entity_data: Dict[str, Any],
        organization_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> WebhookPayload:
        """Create standardized webhook payload"""
        
        # Standardize data based on trigger type
        standardized_data = self._standardize_data(trigger, entity_data)
        
        return WebhookPayload(
            event=trigger,
            timestamp=datetime.now(timezone.utc),
            data=standardized_data,
            organization_id=organization_id,
            user_id=user_id
        )
    
    def _standardize_data(
        self,
        trigger: NotificationTrigger,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Standardize webhook data format for external systems"""
        
        # Common fields for all webhooks
        standardized = {
            'event_type': trigger.value,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source_system': 'garagereg',
            'version': '1.0'
        }
        
        # Add trigger-specific standardized fields
        if trigger in [NotificationTrigger.INSPECTION_DUE, NotificationTrigger.INSPECTION_OVERDUE]:
            standardized.update({
                'gate_id': data.get('gate_id'),
                'gate_name': data.get('gate_name'),
                'inspection_type': data.get('inspection_type'),
                'due_date': data.get('due_date'),
                'location': data.get('gate_location'),
                'inspector': data.get('inspector_name')
            })
        
        elif trigger in [NotificationTrigger.SLA_EXPIRING, NotificationTrigger.SLA_EXPIRED]:
            standardized.update({
                'work_order_id': data.get('work_order_id'),
                'title': data.get('work_order_title'),
                'client_name': data.get('client_name'),
                'sla_deadline': data.get('sla_deadline'),
                'priority': data.get('priority'),
                'hours_remaining': data.get('hours_remaining')
            })
        
        elif trigger == NotificationTrigger.WORK_ORDER_COMPLETED:
            standardized.update({
                'work_order_id': data.get('work_order_id'),
                'title': data.get('work_order_title'),
                'completed_by': data.get('completed_by'),
                'completion_date': data.get('completion_date'),
                'client_name': data.get('client_name'),
                'results': data.get('results_summary')
            })
        
        # Include original data for systems that need it
        standardized['original_data'] = data
        
        return standardized


class WebhookEventHandler:
    """Handle incoming webhook events from external systems"""
    
    def __init__(self):
        self.webhook_adapter = WebhookAdapter()
    
    async def handle_incoming_webhook(
        self,
        source: str,
        payload: Dict[str, Any],
        signature: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process incoming webhook from external system"""
        
        try:
            # Verify signature if provided
            if signature:
                payload_str = json.dumps(payload, sort_keys=True)
                if not await self.webhook_adapter.verify_webhook_signature(
                    payload_str, signature, source
                ):
                    return {
                        'status': 'failed',
                        'error': 'Invalid signature',
                        'timestamp': datetime.now(timezone.utc)
                    }
            
            # Process the webhook based on source and event type
            event_type = payload.get('event_type')
            
            if source == 'maintenance_system':
                return await self._handle_maintenance_webhook(payload)
            elif source == 'client_portal':
                return await self._handle_client_webhook(payload)
            elif source == 'monitoring':
                return await self._handle_monitoring_webhook(payload)
            else:
                logger.warning(f"Unknown webhook source: {source}")
                return {
                    'status': 'ignored',
                    'message': f'Unknown source: {source}',
                    'timestamp': datetime.now(timezone.utc)
                }
        
        except Exception as e:
            logger.error(f"Error processing webhook from {source}: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc)
            }
    
    async def _handle_maintenance_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle webhooks from maintenance management system"""
        # Implementation depends on external system's payload format
        return {'status': 'processed', 'source': 'maintenance_system'}
    
    async def _handle_client_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle webhooks from client portal"""
        return {'status': 'processed', 'source': 'client_portal'}
    
    async def _handle_monitoring_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle webhooks from monitoring system"""
        return {'status': 'processed', 'source': 'monitoring'}