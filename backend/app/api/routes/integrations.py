"""
Integration API routes for webhook subscriptions and ERP adapters
Integráció API végpontok webhook feliratkozásokhoz és ERP adapterekhez
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..core.database import get_db
from ..core.auth import get_current_user
from ..core.rbac import require_permission, Permission
from ..models.auth import User
from ..models.integrations import (
    Integration, WebhookSubscription, WebhookDeliveryLog, ERPSyncLog,
    IntegrationType, IntegrationProvider, WebhookEventType, WebhookDeliveryStatus
)
from ..services.integration_service import IntegrationService, WebhookDeliveryService
from ..services.erp_adapter import ERPAdapterFactory, ERPSyncScheduler, ERPPartData

router = APIRouter()


# Pydantic schemas for API requests/responses
class CreateIntegrationRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    integration_type: IntegrationType
    provider: IntegrationProvider
    description: Optional[str] = None
    endpoint_url: Optional[str] = None
    authentication_type: Optional[str] = None
    credentials: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
    rate_limit_per_minute: int = Field(default=60, ge=1, le=10000)


class CreateWebhookSubscriptionRequest(BaseModel):
    integration_id: int
    name: str = Field(..., min_length=1, max_length=200)
    endpoint_url: str = Field(..., min_length=1)
    description: Optional[str] = None
    subscribed_events: List[WebhookEventType]
    event_filters: Optional[Dict[str, Any]] = None
    secret_key: Optional[str] = None
    signature_header: str = "X-GarageReg-Signature"
    verify_ssl: bool = True
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delays: List[int] = Field(default=[60, 300, 900])
    timeout_seconds: int = Field(default=30, ge=5, le=300)


class TriggerWebhookRequest(BaseModel):
    event_type: WebhookEventType
    payload_data: Dict[str, Any]
    entity_id: Optional[str] = None
    user_id: Optional[int] = None


class TestWebhookEndpointRequest(BaseModel):
    endpoint_url: str
    secret_key: Optional[str] = None
    verify_ssl: bool = True
    timeout_seconds: int = Field(default=30, ge=5, le=300)


class ERPSyncRequest(BaseModel):
    integration_id: int
    sync_type: str = Field(..., regex="^(from_erp|to_erp|bidirectional)$")
    part_numbers: Optional[List[str]] = None
    force_update: bool = False
    modified_since: Optional[datetime] = None


# Integration management endpoints
@router.post("/integrations")
@require_permission(Permission.INTEGRATION)
async def create_integration(
    request: CreateIntegrationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new integration configuration"""
    
    service = IntegrationService(db)
    
    integration = service.create_integration(
        name=request.name,
        integration_type=request.integration_type,
        provider=request.provider.value,
        endpoint_url=request.endpoint_url,
        settings=request.settings,
        organization_id=current_user.organization_id
    )
    
    if request.credentials:
        # TODO: Encrypt credentials before storing
        integration.credentials = request.credentials
    
    integration.description = request.description
    integration.authentication_type = request.authentication_type
    integration.rate_limit_per_minute = request.rate_limit_per_minute
    
    db.commit()
    
    return {
        "id": integration.id,
        "name": integration.name,
        "integration_type": integration.integration_type.value,
        "provider": integration.provider.value,
        "health_status": integration.health_status,
        "is_active": integration.is_active,
        "created_at": integration.created_at.isoformat()
    }


@router.get("/integrations")
@require_permission(Permission.INTEGRATION)
async def list_integrations(
    integration_type: Optional[IntegrationType] = Query(None),
    provider: Optional[IntegrationProvider] = Query(None),
    is_active: Optional[bool] = Query(None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List integrations with filtering"""
    
    query = db.query(Integration).filter(Integration.organization_id == current_user.organization_id)
    
    if integration_type:
        query = query.filter(Integration.integration_type == integration_type)
    
    if provider:
        query = query.filter(Integration.provider == provider)
    
    if is_active is not None:
        query = query.filter(Integration.is_active == is_active)
    
    integrations = query.order_by(Integration.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "integrations": [
            {
                "id": integration.id,
                "name": integration.name,
                "integration_type": integration.integration_type.value,
                "provider": integration.provider.value,
                "health_status": integration.health_status,
                "is_active": integration.is_active,
                "last_success_at": integration.last_success_at.isoformat() if integration.last_success_at else None,
                "last_error_at": integration.last_error_at.isoformat() if integration.last_error_at else None,
                "total_requests": integration.total_requests,
                "success_rate": integration.successful_requests / max(integration.total_requests, 1),
                "created_at": integration.created_at.isoformat()
            }
            for integration in integrations
        ],
        "total": query.count(),
        "limit": limit,
        "offset": offset
    }


@router.get("/integrations/{integration_id}")
@require_permission(Permission.INTEGRATION)
async def get_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get integration details"""
    
    integration = db.query(Integration).filter(
        Integration.id == integration_id,
        Integration.organization_id == current_user.organization_id
    ).first()
    
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    service = IntegrationService(db)
    health_data = service.get_integration_health(integration_id)
    
    return {
        **health_data,
        "integration_type": integration.integration_type.value,
        "provider": integration.provider.value,
        "endpoint_url": integration.endpoint_url,
        "authentication_type": integration.authentication_type,
        "settings": integration.settings,
        "created_at": integration.created_at.isoformat(),
        "updated_at": integration.updated_at.isoformat()
    }


@router.put("/integrations/{integration_id}/status")
@require_permission(Permission.INTEGRATION)
async def toggle_integration_status(
    integration_id: int,
    is_active: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enable/disable integration"""
    
    integration = db.query(Integration).filter(
        Integration.id == integration_id,
        Integration.organization_id == current_user.organization_id
    ).first()
    
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    integration.is_active = is_active
    integration.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    
    return {
        "id": integration.id,
        "name": integration.name,
        "is_active": integration.is_active,
        "updated_at": integration.updated_at.isoformat()
    }


# Webhook subscription endpoints
@router.post("/webhooks/subscriptions")
@require_permission(Permission.INTEGRATION)
async def create_webhook_subscription(
    request: CreateWebhookSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create webhook subscription"""
    
    # Verify integration exists and belongs to user's organization
    integration = db.query(Integration).filter(
        Integration.id == request.integration_id,
        Integration.organization_id == current_user.organization_id
    ).first()
    
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    service = IntegrationService(db)
    
    subscription = service.create_webhook_subscription(
        integration_id=request.integration_id,
        name=request.name,
        endpoint_url=request.endpoint_url,
        subscribed_events=request.subscribed_events,
        secret_key=request.secret_key,
        event_filters=request.event_filters,
        organization_id=current_user.organization_id
    )
    
    # Update additional fields
    subscription.description = request.description
    subscription.signature_header = request.signature_header
    subscription.verify_ssl = request.verify_ssl
    subscription.max_retries = request.max_retries
    subscription.retry_delays = request.retry_delays
    subscription.timeout_seconds = request.timeout_seconds
    
    db.commit()
    
    return {
        "id": subscription.id,
        "integration_id": subscription.integration_id,
        "name": subscription.name,
        "endpoint_url": subscription.endpoint_url,
        "subscribed_events": subscription.subscribed_events,
        "is_active": subscription.is_active,
        "created_at": subscription.created_at.isoformat()
    }


@router.get("/webhooks/subscriptions")
@require_permission(Permission.INTEGRATION)
async def list_webhook_subscriptions(
    integration_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    event_type: Optional[WebhookEventType] = Query(None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List webhook subscriptions"""
    
    query = db.query(WebhookSubscription).join(Integration).filter(
        Integration.organization_id == current_user.organization_id
    )
    
    if integration_id:
        query = query.filter(WebhookSubscription.integration_id == integration_id)
    
    if is_active is not None:
        query = query.filter(WebhookSubscription.is_active == is_active)
    
    if event_type:
        query = query.filter(WebhookSubscription.subscribed_events.contains([event_type.value]))
    
    subscriptions = query.order_by(WebhookSubscription.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "subscriptions": [
            {
                "id": subscription.id,
                "integration_id": subscription.integration_id,
                "integration_name": subscription.integration.name,
                "name": subscription.name,
                "endpoint_url": subscription.endpoint_url,
                "subscribed_events": subscription.subscribed_events,
                "is_active": subscription.is_active,
                "last_triggered_at": subscription.last_triggered_at.isoformat() if subscription.last_triggered_at else None,
                "last_success_at": subscription.last_success_at.isoformat() if subscription.last_success_at else None,
                "total_deliveries_attempted": subscription.total_deliveries_attempted,
                "successful_deliveries": subscription.successful_deliveries,
                "failed_deliveries": subscription.failed_deliveries,
                "consecutive_failures": subscription.consecutive_failures,
                "success_rate": subscription.successful_deliveries / max(subscription.total_deliveries_attempted, 1),
                "created_at": subscription.created_at.isoformat()
            }
            for subscription in subscriptions
        ],
        "total": query.count(),
        "limit": limit,
        "offset": offset
    }


@router.post("/webhooks/test-endpoint")
@require_permission(Permission.INTEGRATION)
async def test_webhook_endpoint(
    request: TestWebhookEndpointRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test webhook endpoint connectivity"""
    
    service = IntegrationService(db)
    
    result = await service.test_webhook_endpoint(
        endpoint_url=request.endpoint_url,
        secret_key=request.secret_key,
        verify_ssl=request.verify_ssl,
        timeout_seconds=request.timeout_seconds
    )
    
    return result


@router.post("/webhooks/trigger")
@require_permission(Permission.INTEGRATION)
async def trigger_webhook_event(
    request: TriggerWebhookRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually trigger webhook event"""
    
    service = IntegrationService(db)
    
    delivery_logs = await service.trigger_webhook_event(
        event_type=request.event_type,
        payload_data=request.payload_data,
        organization_id=current_user.organization_id,
        entity_id=request.entity_id,
        user_id=request.user_id or current_user.id
    )
    
    return {
        "event_type": request.event_type.value,
        "deliveries_attempted": len(delivery_logs),
        "delivery_ids": [log.request_id for log in delivery_logs],
        "triggered_at": datetime.now(timezone.utc).isoformat()
    }


# Webhook delivery logs
@router.get("/webhooks/deliveries")
@require_permission(Permission.INTEGRATION)
async def get_webhook_delivery_logs(
    integration_id: Optional[int] = Query(None),
    webhook_subscription_id: Optional[int] = Query(None),
    event_type: Optional[WebhookEventType] = Query(None),
    status: Optional[WebhookDeliveryStatus] = Query(None),
    since: Optional[datetime] = Query(None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get webhook delivery logs"""
    
    query = db.query(WebhookDeliveryLog).join(Integration).filter(
        Integration.organization_id == current_user.organization_id
    )
    
    if integration_id:
        query = query.filter(WebhookDeliveryLog.integration_id == integration_id)
    
    if webhook_subscription_id:
        query = query.filter(WebhookDeliveryLog.webhook_subscription_id == webhook_subscription_id)
    
    if event_type:
        query = query.filter(WebhookDeliveryLog.event_type == event_type)
    
    if status:
        query = query.filter(WebhookDeliveryLog.delivery_status == status)
    
    if since:
        query = query.filter(WebhookDeliveryLog.created_at >= since)
    
    logs = query.order_by(WebhookDeliveryLog.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "delivery_logs": [
            {
                "id": log.id,
                "integration_id": log.integration_id,
                "webhook_subscription_id": log.webhook_subscription_id,
                "event_type": log.event_type.value,
                "endpoint_url": log.endpoint_url,
                "request_id": log.request_id,
                "delivery_status": log.delivery_status.value,
                "http_status_code": log.http_status_code,
                "attempt_count": log.attempt_count,
                "error_message": log.error_message,
                "created_at": log.created_at.isoformat(),
                "first_attempt_at": log.first_attempt_at.isoformat() if log.first_attempt_at else None,
                "last_attempt_at": log.last_attempt_at.isoformat() if log.last_attempt_at else None,
                "completed_at": log.completed_at.isoformat() if log.completed_at else None,
                "next_retry_at": log.next_retry_at.isoformat() if log.next_retry_at else None
            }
            for log in logs
        ],
        "total": query.count(),
        "limit": limit,
        "offset": offset
    }


@router.get("/webhooks/deliveries/{request_id}")
@require_permission(Permission.INTEGRATION)
async def get_webhook_delivery_details(
    request_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed webhook delivery information"""
    
    log = db.query(WebhookDeliveryLog).join(Integration).filter(
        WebhookDeliveryLog.request_id == request_id,
        Integration.organization_id == current_user.organization_id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Delivery log not found")
    
    return {
        "id": log.id,
        "integration_id": log.integration_id,
        "webhook_subscription_id": log.webhook_subscription_id,
        "event_type": log.event_type.value,
        "endpoint_url": log.endpoint_url,
        "request_id": log.request_id,
        "request_headers": log.request_headers,
        "request_payload": log.request_payload,
        "request_signature": log.request_signature,
        "delivery_status": log.delivery_status.value,
        "http_status_code": log.http_status_code,
        "response_headers": log.response_headers,
        "response_body": log.response_body,
        "attempt_count": log.attempt_count,
        "error_message": log.error_message,
        "created_at": log.created_at.isoformat(),
        "first_attempt_at": log.first_attempt_at.isoformat() if log.first_attempt_at else None,
        "last_attempt_at": log.last_attempt_at.isoformat() if log.last_attempt_at else None,
        "completed_at": log.completed_at.isoformat() if log.completed_at else None,
        "next_retry_at": log.next_retry_at.isoformat() if log.next_retry_at else None
    }


# ERP synchronization endpoints
@router.post("/erp/sync")
@require_permission(Permission.INTEGRATION)
async def trigger_erp_sync(
    request: ERPSyncRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger ERP synchronization"""
    
    integration = db.query(Integration).filter(
        Integration.id == request.integration_id,
        Integration.organization_id == current_user.organization_id,
        Integration.integration_type == IntegrationType.ERP
    ).first()
    
    if not integration:
        raise HTTPException(status_code=404, detail="ERP integration not found")
    
    if not integration.is_active:
        raise HTTPException(status_code=400, detail="Integration is not active")
    
    try:
        adapter = ERPAdapterFactory.create_adapter(integration, db)
        
        if request.sync_type == "from_erp":
            result = await adapter.sync_parts_from_erp(
                part_numbers=request.part_numbers,
                modified_since=request.modified_since
            )
        elif request.sync_type == "to_erp":
            result = await adapter.sync_parts_to_erp(
                part_numbers=request.part_numbers,
                force_update=request.force_update
            )
        else:  # bidirectional
            from_result = await adapter.sync_parts_from_erp(
                part_numbers=request.part_numbers,
                modified_since=request.modified_since
            )
            to_result = await adapter.sync_parts_to_erp(
                part_numbers=request.part_numbers,
                force_update=request.force_update
            )
            
            result = {
                "success": from_result.success and to_result.success,
                "from_erp": {
                    "records_processed": from_result.records_processed,
                    "records_successful": from_result.records_successful,
                    "records_failed": from_result.records_failed,
                    "errors": from_result.errors
                },
                "to_erp": {
                    "records_processed": to_result.records_processed,
                    "records_successful": to_result.records_successful,
                    "records_failed": to_result.records_failed,
                    "errors": to_result.errors
                },
                "total_processed": from_result.records_processed + to_result.records_processed,
                "total_successful": from_result.records_successful + to_result.records_successful,
                "total_failed": from_result.records_failed + to_result.records_failed
            }
        
        return {
            "sync_type": request.sync_type,
            "integration_id": integration.id,
            "result": result,
            "triggered_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ERP sync failed: {str(e)}")


@router.get("/erp/sync/logs")
@require_permission(Permission.INTEGRATION)
async def get_erp_sync_logs(
    integration_id: Optional[int] = Query(None),
    sync_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    since: Optional[datetime] = Query(None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get ERP synchronization logs"""
    
    query = db.query(ERPSyncLog).join(Integration).filter(
        Integration.organization_id == current_user.organization_id
    )
    
    if integration_id:
        query = query.filter(ERPSyncLog.integration_id == integration_id)
    
    if sync_type:
        query = query.filter(ERPSyncLog.sync_type == sync_type)
    
    if status:
        query = query.filter(ERPSyncLog.status == status)
    
    if since:
        query = query.filter(ERPSyncLog.started_at >= since)
    
    logs = query.order_by(ERPSyncLog.started_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "sync_logs": [
            {
                "id": log.id,
                "integration_id": log.integration_id,
                "sync_type": log.sync_type,
                "operation": log.operation,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "status": log.status,
                "error_message": log.error_message,
                "records_processed": log.records_processed,
                "records_successful": log.records_successful,
                "records_failed": log.records_failed,
                "started_at": log.started_at.isoformat(),
                "completed_at": log.completed_at.isoformat() if log.completed_at else None,
                "duration_seconds": log.duration_seconds
            }
            for log in logs
        ],
        "total": query.count(),
        "limit": limit,
        "offset": offset
    }


@router.post("/erp/test-connection/{integration_id}")
@require_permission(Permission.INTEGRATION)
async def test_erp_connection(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test ERP system connection"""
    
    integration = db.query(Integration).filter(
        Integration.id == integration_id,
        Integration.organization_id == current_user.organization_id,
        Integration.integration_type == IntegrationType.ERP
    ).first()
    
    if not integration:
        raise HTTPException(status_code=404, detail="ERP integration not found")
    
    try:
        adapter = ERPAdapterFactory.create_adapter(integration, db)
        result = await adapter.test_connection()
        
        # Update integration health based on test result
        if result.get("success", False):
            integration.health_status = "healthy"
            integration.last_success_at = datetime.now(timezone.utc)
        else:
            integration.health_status = "error"
            integration.last_error_at = datetime.now(timezone.utc)
            integration.last_error_message = result.get("error", "Connection test failed")
        
        db.commit()
        
        return result
        
    except Exception as e:
        integration.health_status = "error"
        integration.last_error_at = datetime.now(timezone.utc)
        integration.last_error_message = str(e)
        db.commit()
        
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}")


# Background task endpoints
@router.post("/webhooks/process-retries")
@require_permission(Permission.INTEGRATION)
async def process_webhook_retries(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process pending webhook retries (manual trigger)"""
    
    async def process_retries():
        async with WebhookDeliveryService(db) as service:
            processed_count = await service.process_retry_queue()
            return processed_count
    
    background_tasks.add_task(process_retries)
    
    return {
        "message": "Webhook retry processing started",
        "triggered_at": datetime.now(timezone.utc).isoformat()
    }