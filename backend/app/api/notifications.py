"""
API endpoints for notification service
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user
from app.models.auth import User
from app.services.notifications import (
    NotificationService, 
    NotificationRequest, 
    NotificationTrigger,
    NotificationRecipient,
    NotificationPriority
)

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.get("/status")
async def get_notification_status(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get notification service status"""
    service = NotificationService()
    return service.get_service_status()


@router.post("/send")
async def send_notification(
    request: NotificationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Send a notification through configured channels"""
    service = NotificationService()
    
    # Send notification in background
    background_tasks.add_task(service.send_notification, request)
    
    return {
        "status": "accepted",
        "message": "Notification queued for delivery",
        "trigger": request.trigger.value,
        "recipients": len(request.recipients),
        "priority": request.priority.value
    }


@router.post("/test/email")
async def test_email_service(
    template_name: str,
    recipient_email: str,
    template_data: Dict[str, Any] = None,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Test email service with a specific template"""
    service = NotificationService()
    
    try:
        result = await service.email_service.send_notification_email(
            trigger=NotificationTrigger.INSPECTION_DUE,  # Default for testing
            recipient_email=recipient_email,
            recipient_name="Test User",
            template_data=template_data or {}
        )
        
        return {
            "status": "success",
            "result": result,
            "template": template_name,
            "recipient": recipient_email
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email test failed: {str(e)}")


@router.post("/test/sms")
async def test_sms_service(
    phone_number: str,
    template_name: str,
    template_data: Dict[str, Any] = None,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Test SMS service with a specific template"""
    service = NotificationService()
    
    try:
        result = await service.sms_service.send_notification_sms(
            trigger=NotificationTrigger.INSPECTION_DUE,  # Default for testing
            phone_number=phone_number,
            template_data=template_data or {}
        )
        
        return {
            "status": "success",
            "result": result,
            "template": template_name,
            "phone": phone_number
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SMS test failed: {str(e)}")


@router.post("/test/webhook")
async def test_webhook_service(
    target: str,
    payload: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Test webhook service with a specific payload"""
    service = NotificationService()
    
    try:
        result = await service.webhook_adapter.send_webhook(
            target=target,
            event_type="test",
            data=payload
        )
        
        return {
            "status": "success",
            "result": result,
            "target": target
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook test failed: {str(e)}")


@router.get("/templates")
async def list_notification_templates(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """List available notification templates"""
    service = NotificationService()
    
    return {
        "email_templates": [
            "inspection_due",
            "sla_expiring", 
            "work_order_completed"
        ],
        "sms_templates": [
            "inspection_due",
            "sla_expiring",
            "work_order_completed" 
        ],
        "triggers": [trigger.value for trigger in NotificationTrigger],
        "priorities": [priority.value for priority in NotificationPriority]
    }


@router.get("/triggers")
async def get_notification_triggers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get notification trigger service status"""
    from app.services.notifications.trigger_service import NotificationTriggerService
    
    trigger_service = NotificationTriggerService()
    
    return {
        "status": "active",
        "trigger_intervals": {
            "inspection_due_check": "6 hours",
            "sla_monitoring": "15 minutes", 
            "maintenance_due_check": "12 hours"
        },
        "available_triggers": [trigger.value for trigger in NotificationTrigger]
    }


@router.post("/triggers/run")
async def run_notification_triggers(
    trigger_type: str = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Manually trigger notification checks"""
    from app.services.notifications.trigger_service import NotificationTriggerService
    
    trigger_service = NotificationTriggerService()
    
    if trigger_type:
        # Run specific trigger
        if trigger_type == "inspection_due":
            background_tasks.add_task(trigger_service.check_due_inspections, db)
        elif trigger_type == "sla_monitoring":
            background_tasks.add_task(trigger_service.monitor_sla_deadlines, db)
        elif trigger_type == "maintenance_due":
            background_tasks.add_task(trigger_service.check_due_maintenance, db)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown trigger type: {trigger_type}")
    else:
        # Run all triggers
        background_tasks.add_task(trigger_service.check_due_inspections, db)
        background_tasks.add_task(trigger_service.monitor_sla_deadlines, db)
        background_tasks.add_task(trigger_service.check_due_maintenance, db)
    
    return {
        "status": "triggered", 
        "trigger_type": trigger_type or "all",
        "message": "Notification checks queued for execution"
    }