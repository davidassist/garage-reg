"""
Integration service for external system connectivity
Integrációs szolgáltatás külső rendszerek csatlakoztatásához
"""
import asyncio
import hashlib
import hmac
import json
import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
import aiohttp
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..core.database import get_db
from ..models.integrations import (
    Integration, WebhookSubscription, WebhookDeliveryLog, ERPSyncLog,
    WebhookEventType, WebhookDeliveryStatus, IntegrationType
)

logger = logging.getLogger(__name__)


class WebhookDeliveryService:
    """
    Service for webhook delivery and retry management
    Webhook kézbesítés és újrapróbálkozás kezelő szolgáltatás
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.client_session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.client_session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.client_session:
            await self.client_session.close()
    
    async def deliver_webhook(
        self,
        event_type: WebhookEventType,
        payload_data: Dict[str, Any],
        organization_id: Optional[int] = None,
        entity_id: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> List[WebhookDeliveryLog]:
        """
        Deliver webhook to all subscribed endpoints
        Webhook kézbesítése az összes feliratkozott végpontra
        """
        delivery_logs = []
        
        # Get all active webhook subscriptions for this event
        subscriptions = self.db.query(WebhookSubscription).join(Integration).filter(
            and_(
                WebhookSubscription.is_active == True,
                Integration.is_active == True,
                WebhookSubscription.subscribed_events.contains([event_type.value])
            )
        ).all()
        
        if organization_id:
            subscriptions = [s for s in subscriptions if s.organization_id == organization_id]
        
        logger.info(f"Found {len(subscriptions)} webhook subscriptions for event {event_type.value}")
        
        # Create delivery tasks for each subscription
        for subscription in subscriptions:
            # Apply event filters if configured
            if subscription.event_filters and not self._passes_filters(payload_data, subscription.event_filters):
                logger.debug(f"Payload filtered out for webhook {subscription.name}")
                continue
            
            # Create delivery log entry
            delivery_log = WebhookDeliveryLog(
                integration_id=subscription.integration_id,
                webhook_subscription_id=subscription.id,
                organization_id=subscription.organization_id,
                event_type=event_type,
                endpoint_url=subscription.endpoint_url,
                request_id=str(uuid.uuid4()),
                request_payload=self._create_webhook_payload(
                    event_type, payload_data, entity_id, user_id, organization_id
                ),
                delivery_status=WebhookDeliveryStatus.PENDING
            )
            
            # Generate HMAC signature if secret is configured
            if subscription.secret_key:
                payload_json = json.dumps(delivery_log.request_payload, sort_keys=True)
                signature = self._generate_hmac_signature(payload_json, subscription.secret_key)
                delivery_log.request_signature = signature
            
            self.db.add(delivery_log)
            self.db.flush()  # Get the ID
            
            delivery_logs.append(delivery_log)
            
            # Attempt immediate delivery
            await self._attempt_delivery(delivery_log, subscription)
        
        self.db.commit()
        return delivery_logs
    
    async def process_retry_queue(self) -> int:
        """
        Process pending webhook retries
        Függő webhook újrapróbálkozások feldolgozása
        """
        now = datetime.now(timezone.utc)
        
        # Get webhooks ready for retry
        pending_deliveries = self.db.query(WebhookDeliveryLog).join(WebhookSubscription).filter(
            and_(
                WebhookDeliveryLog.delivery_status == WebhookDeliveryStatus.RETRYING,
                WebhookDeliveryLog.next_retry_at <= now,
                WebhookSubscription.is_active == True
            )
        ).all()
        
        logger.info(f"Processing {len(pending_deliveries)} webhook retries")
        
        processed_count = 0
        for delivery_log in pending_deliveries:
            subscription = delivery_log.webhook_subscription
            
            if subscription:
                await self._attempt_delivery(delivery_log, subscription)
                processed_count += 1
        
        self.db.commit()
        return processed_count
    
    async def _attempt_delivery(self, delivery_log: WebhookDeliveryLog, subscription: WebhookSubscription):
        """
        Attempt webhook delivery to endpoint
        Webhook kézbesítés kísérlete végpontra
        """
        if not self.client_session:
            self.client_session = aiohttp.ClientSession()
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'GarageReg-Webhook/2.0',
            'X-GarageReg-Event': delivery_log.event_type.value,
            'X-GarageReg-Request-ID': delivery_log.request_id,
            'X-GarageReg-Timestamp': delivery_log.created_at.isoformat(),
        }
        
        # Add HMAC signature header if available
        if delivery_log.request_signature:
            headers[subscription.signature_header] = delivery_log.request_signature
        
        delivery_log.request_headers = headers
        
        try:
            timeout = aiohttp.ClientTimeout(total=subscription.timeout_seconds)
            
            async with self.client_session.post(
                subscription.endpoint_url,
                json=delivery_log.request_payload,
                headers=headers,
                timeout=timeout,
                ssl=subscription.verify_ssl
            ) as response:
                
                response_text = await response.text()
                
                success = 200 <= response.status < 300
                
                delivery_log.mark_attempt(
                    success=success,
                    http_status=response.status,
                    response_headers=dict(response.headers),
                    response_body=response_text
                )
                
                # Update webhook subscription stats
                subscription.total_deliveries_attempted += 1
                subscription.last_triggered_at = datetime.now(timezone.utc)
                
                if success:
                    subscription.successful_deliveries += 1
                    subscription.last_success_at = datetime.now(timezone.utc)
                    subscription.consecutive_failures = 0
                    logger.info(f"Webhook delivered successfully: {subscription.name} -> {response.status}")
                else:
                    subscription.failed_deliveries += 1
                    subscription.last_failure_at = datetime.now(timezone.utc)
                    subscription.consecutive_failures += 1
                    logger.warning(f"Webhook delivery failed: {subscription.name} -> {response.status}")
                
                # Update integration stats
                subscription.integration.update_stats(success)
                
        except asyncio.TimeoutError:
            delivery_log.mark_attempt(
                success=False,
                error_message=f"Request timeout after {subscription.timeout_seconds} seconds"
            )
            subscription.consecutive_failures += 1
            logger.error(f"Webhook timeout: {subscription.name}")
            
        except Exception as e:
            delivery_log.mark_attempt(
                success=False,
                error_message=str(e)
            )
            subscription.consecutive_failures += 1
            logger.error(f"Webhook delivery error: {subscription.name} -> {e}")
    
    def _create_webhook_payload(
        self,
        event_type: WebhookEventType,
        payload_data: Dict[str, Any],
        entity_id: Optional[str] = None,
        user_id: Optional[int] = None,
        organization_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create standardized webhook payload
        Szabványosított webhook payload létrehozása
        """
        return {
            "event_type": event_type.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "garagereg",
            "version": "2.0",
            "entity_id": entity_id,
            "user_id": user_id,
            "organization_id": organization_id,
            "data": payload_data
        }
    
    def _generate_hmac_signature(self, payload: str, secret: str) -> str:
        """
        Generate HMAC-SHA256 signature for webhook verification
        HMAC-SHA256 aláírás generálása webhook ellenőrzéshez
        """
        signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"
    
    def _passes_filters(self, payload_data: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """
        Check if payload passes configured filters
        Ellenőrzi, hogy a payload megfelel-e a beállított szűrőknek
        """
        for field_path, expected_value in filters.items():
            actual_value = self._get_nested_value(payload_data, field_path)
            
            if isinstance(expected_value, list):
                if actual_value not in expected_value:
                    return False
            elif isinstance(expected_value, dict):
                # Support for operators like {"$gt": 100}, {"$contains": "text"}
                if "$gt" in expected_value and actual_value <= expected_value["$gt"]:
                    return False
                if "$lt" in expected_value and actual_value >= expected_value["$lt"]:
                    return False
                if "$contains" in expected_value and expected_value["$contains"] not in str(actual_value):
                    return False
            elif actual_value != expected_value:
                return False
        
        return True
    
    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """
        Get value from nested dictionary using dot notation
        Érték lekérése beágyazott dictionary-ból pont jelöléssel
        """
        keys = field_path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value


class IntegrationService:
    """
    Main integration service for managing external system connections
    Fő integrációs szolgáltatás külső rendszerek csatlakoztatásának kezeléséhez
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.webhook_service = WebhookDeliveryService(db)
    
    async def trigger_webhook_event(
        self,
        event_type: WebhookEventType,
        payload_data: Dict[str, Any],
        organization_id: Optional[int] = None,
        entity_id: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> List[WebhookDeliveryLog]:
        """
        Trigger webhook event for all subscribed integrations
        Webhook esemény kiváltása az összes feliratkozott integrációhoz
        """
        async with self.webhook_service:
            return await self.webhook_service.deliver_webhook(
                event_type=event_type,
                payload_data=payload_data,
                organization_id=organization_id,
                entity_id=entity_id,
                user_id=user_id
            )
    
    def create_integration(
        self,
        name: str,
        integration_type: IntegrationType,
        provider: str,
        endpoint_url: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
        organization_id: Optional[int] = None
    ) -> Integration:
        """
        Create new integration configuration
        Új integráció konfiguráció létrehozása
        """
        integration = Integration(
            name=name,
            integration_type=integration_type,
            provider=provider,
            endpoint_url=endpoint_url,
            settings=settings or {},
            organization_id=organization_id,
            health_status='unknown'
        )
        
        self.db.add(integration)
        self.db.commit()
        
        logger.info(f"Created integration: {name} ({integration_type.value})")
        return integration
    
    def create_webhook_subscription(
        self,
        integration_id: int,
        name: str,
        endpoint_url: str,
        subscribed_events: List[WebhookEventType],
        secret_key: Optional[str] = None,
        event_filters: Optional[Dict[str, Any]] = None,
        organization_id: Optional[int] = None
    ) -> WebhookSubscription:
        """
        Create webhook subscription
        Webhook feliratkozás létrehozása
        """
        subscription = WebhookSubscription(
            integration_id=integration_id,
            name=name,
            endpoint_url=endpoint_url,
            subscribed_events=[event.value for event in subscribed_events],
            secret_key=secret_key,
            event_filters=event_filters,
            organization_id=organization_id
        )
        
        self.db.add(subscription)
        self.db.commit()
        
        logger.info(f"Created webhook subscription: {name} for events {[e.value for e in subscribed_events]}")
        return subscription
    
    def get_delivery_logs(
        self,
        integration_id: Optional[int] = None,
        event_type: Optional[WebhookEventType] = None,
        status: Optional[WebhookDeliveryStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[WebhookDeliveryLog]:
        """
        Get webhook delivery logs with filters
        Webhook kézbesítési naplók lekérése szűrőkkel
        """
        query = self.db.query(WebhookDeliveryLog).order_by(WebhookDeliveryLog.created_at.desc())
        
        if integration_id:
            query = query.filter(WebhookDeliveryLog.integration_id == integration_id)
        
        if event_type:
            query = query.filter(WebhookDeliveryLog.event_type == event_type)
        
        if status:
            query = query.filter(WebhookDeliveryLog.delivery_status == status)
        
        return query.offset(offset).limit(limit).all()
    
    def get_integration_health(self, integration_id: int) -> Dict[str, Any]:
        """
        Get integration health status and statistics
        Integráció egészség státusz és statisztikák lekérése
        """
        integration = self.db.query(Integration).filter(Integration.id == integration_id).first()
        
        if not integration:
            raise ValueError(f"Integration not found: {integration_id}")
        
        # Get recent delivery stats (last 24 hours)
        since = datetime.now(timezone.utc) - timedelta(hours=24)
        recent_deliveries = self.db.query(WebhookDeliveryLog).filter(
            and_(
                WebhookDeliveryLog.integration_id == integration_id,
                WebhookDeliveryLog.created_at >= since
            )
        ).all()
        
        successful_recent = len([d for d in recent_deliveries if d.delivery_status == WebhookDeliveryStatus.DELIVERED])
        failed_recent = len([d for d in recent_deliveries if d.delivery_status == WebhookDeliveryStatus.FAILED])
        
        return {
            "integration_id": integration.id,
            "name": integration.name,
            "health_status": integration.health_status,
            "is_active": integration.is_active,
            "last_success_at": integration.last_success_at.isoformat() if integration.last_success_at else None,
            "last_error_at": integration.last_error_at.isoformat() if integration.last_error_at else None,
            "last_error_message": integration.last_error_message,
            "total_requests": integration.total_requests,
            "success_rate": integration.successful_requests / max(integration.total_requests, 1),
            "recent_24h": {
                "total_deliveries": len(recent_deliveries),
                "successful_deliveries": successful_recent,
                "failed_deliveries": failed_recent,
                "success_rate": successful_recent / max(len(recent_deliveries), 1)
            }
        }
    
    async def test_webhook_endpoint(
        self,
        endpoint_url: str,
        secret_key: Optional[str] = None,
        verify_ssl: bool = True,
        timeout_seconds: int = 30
    ) -> Dict[str, Any]:
        """
        Test webhook endpoint connectivity
        Webhook végpont kapcsolat tesztelése
        """
        test_payload = {
            "event_type": "system.test",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "garagereg",
            "version": "2.0",
            "data": {
                "test": True,
                "message": "This is a test webhook from GarageReg"
            }
        }
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'GarageReg-Webhook-Test/2.0',
            'X-GarageReg-Event': 'system.test',
            'X-GarageReg-Test': 'true'
        }
        
        if secret_key:
            payload_json = json.dumps(test_payload, sort_keys=True)
            signature = hmac.new(
                secret_key.encode('utf-8'),
                payload_json.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            headers['X-GarageReg-Signature'] = f"sha256={signature}"
        
        async with aiohttp.ClientSession() as session:
            try:
                timeout = aiohttp.ClientTimeout(total=timeout_seconds)
                
                async with session.post(
                    endpoint_url,
                    json=test_payload,
                    headers=headers,
                    timeout=timeout,
                    ssl=verify_ssl
                ) as response:
                    
                    response_text = await response.text()
                    
                    return {
                        "success": 200 <= response.status < 300,
                        "status_code": response.status,
                        "response_headers": dict(response.headers),
                        "response_body": response_text,
                        "error": None
                    }
                    
            except asyncio.TimeoutError:
                return {
                    "success": False,
                    "error": f"Request timeout after {timeout_seconds} seconds"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }