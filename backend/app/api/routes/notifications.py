"""
Notification API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.core.deps import get_db, get_current_active_user
from app.core.rbac import require_permission, PermissionActions, Resources
from app.models.auth import User
from app.services.notifications.notification_service import NotificationService
from app.services.notifications.trigger_service import NotificationTriggerService
from app.services.notifications.models import (
    NotificationRequest, NotificationTrigger, NotificationPriority,
    NotificationRecipient, NotificationType
)

router = APIRouter(prefix="/notifications", tags=["notifications"])

# Initialize services
notification_service = NotificationService()
trigger_service = NotificationTriggerService()


@router.post("/send")
@require_permission(Resources.GATE, PermissionActions.UPDATE)  # Requires update permission for notifications
async def send_notification(
    request: NotificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Send notification via configured channels"""
    
    try:
        # Add current user context
        request.metadata['user_id'] = current_user.id
        request.metadata['organization_id'] = getattr(current_user, 'organization_id', None)
        
        result = await notification_service.send_notification(request)
        
        return {
            "success": True,
            "message": "Notification sent successfully",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send notification: {str(e)}"
        )


@router.post("/test/email")
@require_permission(Resources.GATE, PermissionActions.UPDATE)
async def test_email_notification(
    recipient_email: str,
    trigger: NotificationTrigger = NotificationTrigger.INSPECTION_DUE,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Send test email notification"""
    
    try:
        # Create test data based on trigger
        if trigger == NotificationTrigger.INSPECTION_DUE:
            template_data = {
                'gate_name': 'Test Kapu #1',
                'gate_location': 'Teszt Épület - A szárny',
                'inspection_type': 'Éves biztonsági ellenőrzés',
                'due_date': datetime.now(),
                'inspector_name': current_user.full_name,
                'gate_id': 999,
                'days_until_due': 3
            }
        elif trigger == NotificationTrigger.SLA_EXPIRING:
            template_data = {
                'work_order_id': 'TEST-001',
                'work_order_title': 'Teszt munkalap javítás',
                'client_name': 'Teszt Ügyfél Kft.',
                'sla_deadline': datetime.now(),
                'hours_remaining': 2.5,
                'priority': 'high'
            }
        elif trigger == NotificationTrigger.WORK_ORDER_COMPLETED:
            template_data = {
                'work_order_id': 'TEST-002',
                'work_order_title': 'Kapu karbantartás',
                'client_name': 'Teszt Ügyfél Kft.',
                'completed_by': current_user.full_name,
                'completion_date': datetime.now(),
                'results_summary': 'A kapu sikeresen megjavításra került. Minden funkció működik.'
            }
        else:
            template_data = {
                'user_name': current_user.full_name,
                'message': 'Ez egy teszt értesítés.',
                'timestamp': datetime.now()
            }
        
        # Send test notification
        request = NotificationRequest(
            trigger=trigger,
            recipients=[
                NotificationRecipient(
                    email=recipient_email,
                    name=current_user.full_name
                )
            ],
            template_data=template_data,
            priority=NotificationPriority.NORMAL
        )
        
        result = await notification_service.send_notification(request)
        
        return {
            "success": True,
            "message": f"Test {trigger.value} notification sent to {recipient_email}",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send test notification: {str(e)}"
        )


@router.post("/test/sms")
@require_permission(Resources.GATE, PermissionActions.UPDATE)
async def test_sms_notification(
    phone_number: str,
    trigger: NotificationTrigger = NotificationTrigger.SLA_EXPIRING,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Send test SMS notification"""
    
    try:
        # Create test SMS data
        template_data = {
            'gate_name': 'Teszt Kapu',
            'due_date': datetime.now().strftime('%Y-%m-%d'),
            'work_order_id': 'TEST-SMS',
            'hours_remaining': 1,
            'url': 'https://app.garagereg.com/test'
        }
        
        result = await notification_service.sms_service.send_notification_sms(
            trigger=trigger,
            phone_number=phone_number,
            template_data=template_data
        )
        
        return {
            "success": True,
            "message": f"Test SMS sent to {phone_number}",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send test SMS: {str(e)}"
        )


@router.post("/test/webhook")
@require_permission(Resources.GATE, PermissionActions.UPDATE)
async def test_webhook_notification(
    targets: Optional[List[str]] = None,
    trigger: NotificationTrigger = NotificationTrigger.GATE_FAULT,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Send test webhook notification"""
    
    try:
        # Create test webhook data
        template_data = {
            'gate_id': 999,
            'gate_name': 'Teszt Kapu #1',
            'fault_description': 'Teszt hiba - automatikus értesítés',
            'severity': 'high',
            'reported_by': current_user.full_name,
            'timestamp': datetime.now().isoformat()
        }
        
        result = await notification_service.webhook_adapter.send_webhook(
            trigger=trigger,
            payload_data=template_data,
            targets=targets,
            organization_id=getattr(current_user, 'organization_id', None),
            user_id=current_user.id
        )
        
        return {
            "success": True,
            "message": "Test webhook sent",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send test webhook: {str(e)}"
        )


@router.get("/status")
@require_permission(Resources.GATE, PermissionActions.READ)
async def get_notification_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get notification service status and configuration"""
    
    try:
        status = notification_service.get_service_status()
        
        return {
            "success": True,
            "status": status,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get notification status: {str(e)}"
        )


@router.post("/triggers/check")
@require_permission(Resources.GATE, PermissionActions.ADMIN)
async def run_notification_checks(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Manually trigger notification checks"""
    
    def run_checks():
        """Background task to run notification checks"""
        import asyncio
        
        async def async_checks():
            try:
                result = await trigger_service.run_periodic_checks(db)
                logger.info(f"Manual notification checks completed: {result}")
            except Exception as e:
                logger.error(f"Manual notification checks failed: {e}")
        
        # Run async function in new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(async_checks())
        loop.close()
    
    background_tasks.add_task(run_checks)
    
    return {
        "success": True,
        "message": "Notification checks started in background",
        "timestamp": datetime.now()
    }


@router.get("/templates")
@require_permission(Resources.GATE, PermissionActions.READ)
async def get_notification_templates(
    trigger: Optional[NotificationTrigger] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get available notification templates and their variables"""
    
    try:
        templates = {}
        
        triggers_to_check = [trigger] if trigger else list(NotificationTrigger)
        
        for trig in triggers_to_check:
            # Email template variables
            email_vars = notification_service.email_service.get_template_variables(trig)
            
            # SMS template variables  
            sms_vars = notification_service.sms_service.get_sms_template_variables(trig)
            
            templates[trig.value] = {
                'email': {
                    'template_name': notification_service._get_email_template(trig),
                    'variables': email_vars,
                    'sample_subject': notification_service._get_email_subject(trig, {
                        'gate_name': 'Sample Gate',
                        'work_order_id': 'WO-001'
                    })
                },
                'sms': {
                    'variables': sms_vars,
                    'sample_message': notification_service.sms_service.templates.get(trig, 'No template')
                }
            }
        
        return {
            "success": True,
            "templates": templates
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get templates: {str(e)}"
        )


@router.post("/webhook/receive/{source}")
async def receive_webhook(
    source: str,
    payload: Dict[str, Any],
    signature: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Receive webhook from external system"""
    
    try:
        from app.services.notifications.webhook_service import WebhookEventHandler
        
        handler = WebhookEventHandler()
        result = await handler.handle_incoming_webhook(
            source=source,
            payload=payload,
            signature=signature
        )
        
        return {
            "success": True,
            "message": "Webhook processed",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process webhook: {str(e)}"
        )


@router.get("/history")
@require_permission(Resources.GATE, PermissionActions.READ)
async def get_notification_history(
    limit: int = 50,
    offset: int = 0,
    trigger: Optional[NotificationTrigger] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get notification history"""
    
    # This would query a notification_log table in production
    # For now, return mock data
    
    history = [
        {
            "id": i,
            "trigger": "inspection_due",
            "recipient": f"user{i}@example.com",
            "channel": "email",
            "status": "sent" if i % 3 != 0 else "failed",
            "created_at": datetime.now(),
            "sent_at": datetime.now() if i % 3 != 0 else None
        }
        for i in range(offset, offset + limit)
    ]
    
    return {
        "success": True,
        "history": history,
        "total": 100,  # Mock total
        "limit": limit,
        "offset": offset
    }


# Import logger
import logging
logger = logging.getLogger(__name__)