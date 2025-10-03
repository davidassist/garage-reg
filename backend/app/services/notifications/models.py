"""
Notification service core models and types
"""
from enum import Enum
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class NotificationType(str, Enum):
    """Notification type enumeration"""
    EMAIL = "email"
    SMS = "sms" 
    WEBHOOK = "webhook"
    PUSH = "push"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatus(str, Enum):
    """Notification delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRY = "retry"


class NotificationTrigger(str, Enum):
    """Event triggers for notifications"""
    INSPECTION_DUE = "inspection_due"
    INSPECTION_OVERDUE = "inspection_overdue"
    SLA_EXPIRING = "sla_expiring"
    SLA_EXPIRED = "sla_expired"
    WORK_ORDER_COMPLETED = "work_order_completed"
    WORK_ORDER_ASSIGNED = "work_order_assigned"
    MAINTENANCE_DUE = "maintenance_due"
    GATE_FAULT = "gate_fault"
    USER_REGISTERED = "user_registered"
    PASSWORD_RESET = "password_reset"


class EmailTemplate(BaseModel):
    """Email template configuration"""
    name: str
    subject_template: str
    html_template: str  # MJML template
    text_template: str  # Plain text fallback
    variables: List[str] = Field(default_factory=list)
    trigger: NotificationTrigger
    enabled: bool = True


class NotificationRecipient(BaseModel):
    """Notification recipient information"""
    email: Optional[str] = None
    phone: Optional[str] = None
    webhook_url: Optional[str] = None
    user_id: Optional[int] = None
    name: Optional[str] = None
    language: str = "hu"  # Default Hungarian
    timezone: str = "Europe/Budapest"


class NotificationRequest(BaseModel):
    """Notification request payload"""
    trigger: NotificationTrigger
    recipients: List[NotificationRecipient]
    template_data: Dict[str, Any] = Field(default_factory=dict)
    priority: NotificationPriority = NotificationPriority.NORMAL
    delivery_time: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NotificationResponse(BaseModel):
    """Notification service response"""
    notification_id: str
    status: NotificationStatus
    message: str
    delivery_attempts: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None


class WebhookPayload(BaseModel):
    """Webhook notification payload"""
    event: NotificationTrigger
    timestamp: datetime
    data: Dict[str, Any]
    organization_id: Optional[int] = None
    user_id: Optional[int] = None
    signature: Optional[str] = None  # HMAC signature for verification


class SMSMessage(BaseModel):
    """SMS notification message"""
    phone_number: str
    message: str
    sender_id: str = "GarageReg"
    
    
class EmailMessage(BaseModel):
    """Email notification message"""
    to_email: str
    to_name: Optional[str] = None
    from_email: str = "noreply@garagereg.com"
    from_name: str = "GarageReg System"
    subject: str
    html_content: str
    text_content: Optional[str] = None
    attachments: List[Dict[str, Any]] = Field(default_factory=list)


class NotificationTemplate(BaseModel):
    """Template definition with localization support"""
    trigger: NotificationTrigger
    type: NotificationType
    language: str = "hu"
    subject: str
    content: str  # Template content (MJML for email, plain text for SMS)
    variables: List[str] = Field(default_factory=list)
    enabled: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))