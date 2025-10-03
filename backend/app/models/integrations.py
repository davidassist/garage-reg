"""
Integration models for external system connectivity
Integráció modellek külső rendszerek csatlakoztatásához
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.orm import relationship, validates
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any

from ..core.database import Base, TenantModel


class IntegrationType(str, Enum):
    """Integration type enumeration"""
    WEBHOOK = "webhook"
    API = "api" 
    ERP = "erp"
    FILE_SYNC = "file_sync"
    EMAIL = "email"


class IntegrationProvider(str, Enum):
    """Integration provider enumeration"""
    SAP = "sap"
    ORACLE = "oracle"
    MICROSOFT = "microsoft"
    SLACK = "slack"
    TEAMS = "teams"
    ZAPIER = "zapier"
    CUSTOM = "custom"


class WebhookDeliveryStatus(str, Enum):
    """Webhook delivery status"""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    EXPIRED = "expired"


class WebhookEventType(str, Enum):
    """Webhook event types"""
    # Gate management
    GATE_CREATED = "gate.created"
    GATE_UPDATED = "gate.updated"
    GATE_DELETED = "gate.deleted"
    GATE_INSPECTION_DUE = "gate.inspection_due"
    GATE_FAULT_DETECTED = "gate.fault_detected"
    
    # Work orders
    WORK_ORDER_CREATED = "work_order.created"
    WORK_ORDER_UPDATED = "work_order.updated"
    WORK_ORDER_COMPLETED = "work_order.completed"
    WORK_ORDER_ASSIGNED = "work_order.assigned"
    
    # Inventory
    INVENTORY_ITEM_CREATED = "inventory.item_created"
    INVENTORY_ITEM_UPDATED = "inventory.item_updated"
    INVENTORY_LOW_STOCK = "inventory.low_stock"
    INVENTORY_MOVEMENT = "inventory.movement"
    
    # Maintenance
    MAINTENANCE_SCHEDULED = "maintenance.scheduled"
    MAINTENANCE_COMPLETED = "maintenance.completed"
    MAINTENANCE_OVERDUE = "maintenance.overdue"
    
    # User management
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    
    # System events
    SYSTEM_HEALTH_CHECK = "system.health_check"
    SYSTEM_ERROR = "system.error"


class Integration(TenantModel):
    """
    Integration configurations for external systems
    Külső rendszerek integrációs konfigurációi
    """
    __tablename__ = "integrations"
    
    # Basic information
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    integration_type = Column(SQLEnum(IntegrationType), nullable=False, index=True)
    provider = Column(SQLEnum(IntegrationProvider), nullable=False, index=True)
    
    # Connection details
    endpoint_url = Column(String(1000), nullable=True)
    authentication_type = Column(String(50), nullable=True)  # 'none', 'api_key', 'oauth2', 'basic', 'hmac'
    credentials = Column(JSON, nullable=True)  # Encrypted credentials
    
    # Configuration
    settings = Column(JSON, nullable=True, default=lambda: {})
    field_mappings = Column(JSON, nullable=True)  # Field mapping configurations
    rate_limit_per_minute = Column(Integer, default=60, nullable=False)
    
    # Status and health monitoring
    is_active = Column(Boolean, default=True, nullable=False)
    health_status = Column(String(50), default='unknown', nullable=False)  # 'healthy', 'warning', 'error', 'unknown', 'disabled'
    last_sync_at = Column(DateTime, nullable=True)
    last_success_at = Column(DateTime, nullable=True)
    last_error_at = Column(DateTime, nullable=True)
    last_error_message = Column(Text, nullable=True)
    
    # Statistics
    total_requests = Column(Integer, default=0, nullable=False)
    successful_requests = Column(Integer, default=0, nullable=False)
    failed_requests = Column(Integer, default=0, nullable=False)
    
    # Relationships
    webhooks = relationship("WebhookSubscription", back_populates="integration", cascade="all, delete-orphan")
    delivery_logs = relationship("WebhookDeliveryLog", back_populates="integration", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_integration_name", "name"),
        Index("idx_integration_type_provider", "integration_type", "provider"),
        Index("idx_integration_active_health", "is_active", "health_status"),
        Index("idx_integration_last_sync", "last_sync_at"),
    )
    
    @validates("health_status")
    def validate_health_status(self, key, value):
        valid_statuses = ['healthy', 'warning', 'error', 'unknown', 'disabled']
        if value not in valid_statuses:
            raise ValueError(f"Health status must be one of: {valid_statuses}")
        return value
    
    def update_stats(self, success: bool):
        """Update integration statistics"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
            self.last_success_at = datetime.now(timezone.utc)
            if self.health_status in ['error', 'warning']:
                self.health_status = 'healthy'
        else:
            self.failed_requests += 1
            self.last_error_at = datetime.now(timezone.utc)
            # Calculate error rate
            error_rate = self.failed_requests / self.total_requests
            if error_rate > 0.5:
                self.health_status = 'error'
            elif error_rate > 0.2:
                self.health_status = 'warning'


class WebhookSubscription(TenantModel):
    """
    Webhook subscription configurations
    Webhook feliratkozás konfigurációk
    """
    __tablename__ = "webhook_subscriptions"
    
    # Integration reference
    integration_id = Column(Integer, ForeignKey("integrations.id"), nullable=False, index=True)
    
    # Subscription details
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    endpoint_url = Column(String(1000), nullable=False)
    
    # Event configuration
    subscribed_events = Column(JSON, nullable=False)  # Array of WebhookEventType values
    event_filters = Column(JSON, nullable=True)  # Filters to apply before sending
    
    # Security configuration
    secret_key = Column(String(200), nullable=True)  # HMAC signing secret
    signature_header = Column(String(100), default='X-GarageReg-Signature', nullable=False)
    verify_ssl = Column(Boolean, default=True, nullable=False)
    
    # Delivery configuration
    max_retries = Column(Integer, default=3, nullable=False)
    retry_delays = Column(JSON, default=lambda: [60, 300, 900], nullable=False)  # Seconds between retries
    timeout_seconds = Column(Integer, default=30, nullable=False)
    
    # Status and monitoring
    is_active = Column(Boolean, default=True, nullable=False)
    last_triggered_at = Column(DateTime, nullable=True)
    last_success_at = Column(DateTime, nullable=True)
    last_failure_at = Column(DateTime, nullable=True)
    consecutive_failures = Column(Integer, default=0, nullable=False)
    
    # Statistics
    total_deliveries_attempted = Column(Integer, default=0, nullable=False)
    successful_deliveries = Column(Integer, default=0, nullable=False)
    failed_deliveries = Column(Integer, default=0, nullable=False)
    
    # Relationships
    integration = relationship("Integration", back_populates="webhooks")
    delivery_logs = relationship("WebhookDeliveryLog", back_populates="webhook_subscription", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_webhook_integration", "integration_id"),
        Index("idx_webhook_active", "is_active"),
        Index("idx_webhook_events", "subscribed_events"),
        Index("idx_webhook_last_triggered", "last_triggered_at"),
    )
    
    def is_subscribed_to_event(self, event_type: WebhookEventType) -> bool:
        """Check if webhook is subscribed to event type"""
        return event_type.value in self.subscribed_events
    
    def should_retry(self) -> bool:
        """Check if webhook should be retried based on consecutive failures"""
        return self.consecutive_failures < self.max_retries
    
    def get_next_retry_delay(self) -> int:
        """Get next retry delay in seconds"""
        if self.consecutive_failures >= len(self.retry_delays):
            return self.retry_delays[-1]
        return self.retry_delays[self.consecutive_failures]


class WebhookDeliveryLog(TenantModel):
    """
    Webhook delivery logs for tracking and debugging
    Webhook kézbesítési naplók nyomon követéshez és hibakereséshez
    """
    __tablename__ = "webhook_delivery_logs"
    
    # References
    integration_id = Column(Integer, ForeignKey("integrations.id"), nullable=False, index=True)
    webhook_subscription_id = Column(Integer, ForeignKey("webhook_subscriptions.id"), nullable=True, index=True)
    
    # Delivery details
    event_type = Column(SQLEnum(WebhookEventType), nullable=False, index=True)
    endpoint_url = Column(String(1000), nullable=False)
    
    # Request details
    request_id = Column(String(100), nullable=False, unique=True, index=True)  # UUID for tracking
    request_headers = Column(JSON, nullable=True)
    request_payload = Column(JSON, nullable=False)
    request_signature = Column(String(200), nullable=True)
    
    # Response details
    delivery_status = Column(SQLEnum(WebhookDeliveryStatus), nullable=False, index=True)
    http_status_code = Column(Integer, nullable=True)
    response_headers = Column(JSON, nullable=True)
    response_body = Column(Text, nullable=True)
    
    # Timing
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    first_attempt_at = Column(DateTime, nullable=True)
    last_attempt_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Retry tracking
    attempt_count = Column(Integer, default=0, nullable=False)
    next_retry_at = Column(DateTime, nullable=True, index=True)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    integration = relationship("Integration", back_populates="delivery_logs")
    webhook_subscription = relationship("WebhookSubscription", back_populates="delivery_logs")
    
    # Indexes
    __table_args__ = (
        Index("idx_delivery_log_status_retry", "delivery_status", "next_retry_at"),
        Index("idx_delivery_log_event_created", "event_type", "created_at"),
        Index("idx_delivery_log_integration_status", "integration_id", "delivery_status"),
        Index("idx_delivery_log_webhook_status", "webhook_subscription_id", "delivery_status"),
    )
    
    def mark_attempt(self, success: bool, http_status: Optional[int] = None, 
                     response_headers: Optional[Dict] = None, response_body: Optional[str] = None,
                     error_message: Optional[str] = None):
        """Mark a delivery attempt"""
        now = datetime.now(timezone.utc)
        
        self.attempt_count += 1
        self.last_attempt_at = now
        
        if self.first_attempt_at is None:
            self.first_attempt_at = now
        
        self.http_status_code = http_status
        self.response_headers = response_headers
        self.response_body = response_body
        self.error_message = error_message
        
        if success:
            self.delivery_status = WebhookDeliveryStatus.DELIVERED
            self.completed_at = now
            self.next_retry_at = None
        else:
            if self.attempt_count >= 3:  # Max retries reached
                self.delivery_status = WebhookDeliveryStatus.FAILED
                self.completed_at = now
                self.next_retry_at = None
            else:
                self.delivery_status = WebhookDeliveryStatus.RETRYING
                # Calculate next retry time based on webhook subscription settings
                if self.webhook_subscription:
                    delay = self.webhook_subscription.get_next_retry_delay()
                else:
                    delay = [60, 300, 900][min(self.attempt_count - 1, 2)]
                
                self.next_retry_at = now.replace(second=0, microsecond=0) + timezone.utc.localize(datetime.fromtimestamp(delay)).utctimetuple()


class ERPSyncLog(TenantModel):
    """
    ERP synchronization logs
    ERP szinkronizálási naplók
    """
    __tablename__ = "erp_sync_logs"
    
    # Integration reference
    integration_id = Column(Integer, ForeignKey("integrations.id"), nullable=False, index=True)
    
    # Sync details
    sync_type = Column(String(50), nullable=False, index=True)  # 'parts', 'customers', 'orders', 'inventory'
    operation = Column(String(50), nullable=False)  # 'create', 'update', 'delete', 'sync'
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(100), nullable=True)
    
    # Request/Response
    request_data = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)
    
    # Status
    status = Column(String(50), nullable=False, index=True)  # 'success', 'failed', 'partial'
    error_message = Column(Text, nullable=True)
    records_processed = Column(Integer, default=0, nullable=False)
    records_successful = Column(Integer, default=0, nullable=False)
    records_failed = Column(Integer, default=0, nullable=False)
    
    # Timing
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Relationship
    integration = relationship("Integration")
    
    # Indexes
    __table_args__ = (
        Index("idx_erp_sync_type_status", "sync_type", "status"),
        Index("idx_erp_sync_started", "started_at"),
        Index("idx_erp_sync_integration", "integration_id", "sync_type"),
    )