"""Inventory management and audit logging models."""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Numeric, Index
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import JSONB, INET
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models import TenantModel, BaseModel


class Warehouse(TenantModel):
    """
    Warehouses - storage locations for inventory.
    
    Raktárak (készletkezelési tárolóhelyek)
    """
    __tablename__ = "warehouses"
    
    # Warehouse information
    name = Column(String(200), nullable=False, index=True)
    code = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    warehouse_type = Column(String(50), nullable=False, index=True)  # 'main', 'mobile', 'temporary', 'supplier'
    
    # Location information
    address_line_1 = Column(String(200), nullable=True)
    address_line_2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Geographic coordinates
    latitude = Column(String(20), nullable=True)
    longitude = Column(String(20), nullable=True)
    
    # Warehouse characteristics
    total_capacity_m3 = Column(Numeric(10, 2), nullable=True)
    available_capacity_m3 = Column(Numeric(10, 2), nullable=True)
    temperature_controlled = Column(Boolean, default=False, nullable=False)
    security_level = Column(String(20), default='standard', nullable=False)  # 'low', 'standard', 'high', 'maximum'
    
    # Contact information
    manager_name = Column(String(200), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    contact_email = Column(String(320), nullable=True)
    
    # Operating hours
    operating_hours = Column(JSONB, nullable=True)  # JSON with day-specific hours
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSONB, nullable=True, default=lambda: {})
    
    # Relationships
    inventory_items = relationship("InventoryItem", back_populates="warehouse", cascade="all, delete-orphan")
    stock_movements = relationship("StockMovement", back_populates="warehouse")
    
    # Indexes
    __table_args__ = (
        Index("idx_warehouse_name", "name"),
        Index("idx_warehouse_code", "code"),
        Index("idx_warehouse_type", "warehouse_type"),
        Index("idx_warehouse_active", "is_active"),
        Index("idx_warehouse_location", "latitude", "longitude"),
    )
    
    @validates("warehouse_type")
    def validate_warehouse_type(self, key, value):
        valid_types = ['main', 'mobile', 'temporary', 'supplier', 'customer', 'service_van']
        if value not in valid_types:
            raise ValueError(f"Warehouse type must be one of: {valid_types}")
        return value


class InventoryItem(TenantModel):
    """
    Inventory Items - stock levels and locations for parts.
    
    Készlet tételek (alkatrészek raktári szintjei és helye)
    """
    __tablename__ = "inventory_items"
    
    # References
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False, index=True)
    
    # Location within warehouse
    location_code = Column(String(50), nullable=True, index=True)  # Aisle, shelf, bin location
    zone = Column(String(50), nullable=True)
    
    # Stock levels
    quantity_on_hand = Column(Numeric(15, 3), default=0, nullable=False)
    quantity_reserved = Column(Numeric(15, 3), default=0, nullable=False)
    quantity_available = Column(Numeric(15, 3), default=0, nullable=False)
    quantity_on_order = Column(Numeric(15, 3), default=0, nullable=False)
    
    # Stock level management
    minimum_stock = Column(Numeric(15, 3), default=0, nullable=False)
    maximum_stock = Column(Numeric(15, 3), nullable=True)
    reorder_point = Column(Numeric(15, 3), nullable=True)
    reorder_quantity = Column(Numeric(15, 3), nullable=True)
    
    # Cost tracking
    unit_cost = Column(Numeric(10, 4), nullable=True)
    average_cost = Column(Numeric(10, 4), nullable=True)
    last_cost = Column(Numeric(10, 4), nullable=True)
    total_value = Column(Numeric(15, 2), nullable=True)
    
    # Stock dates
    last_received_date = Column(DateTime, nullable=True)
    last_issued_date = Column(DateTime, nullable=True)
    last_counted_date = Column(DateTime, nullable=True)
    
    # Cycle counting
    cycle_count_frequency_days = Column(Integer, nullable=True)
    next_cycle_count_date = Column(DateTime, nullable=True)
    variance_tolerance_percentage = Column(Numeric(5, 2), default=5.0, nullable=False)
    
    # Status tracking
    stock_status = Column(String(50), default='normal', nullable=False)  # 'normal', 'low', 'critical', 'overstock'
    last_movement_type = Column(String(50), nullable=True)
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSONB, nullable=True, default=lambda: {})
    
    # Relationships
    warehouse = relationship("Warehouse", back_populates="inventory_items")
    part = relationship("Part", back_populates="inventory_items")
    stock_movements = relationship("StockMovement", back_populates="inventory_item")
    part_usages = relationship("PartUsage", back_populates="inventory_item")
    
    # Indexes
    __table_args__ = (
        Index("idx_inventory_warehouse", "warehouse_id"),
        Index("idx_inventory_part", "part_id"),
        Index("idx_inventory_location", "location_code"),
        Index("idx_inventory_status", "stock_status"),
        Index("idx_inventory_reorder", "reorder_point"),
        Index("idx_inventory_cycle_count", "next_cycle_count_date"),
    )
    
    @validates("stock_status")
    def validate_stock_status(self, key, value):
        valid_statuses = ['normal', 'low', 'critical', 'overstock', 'out_of_stock', 'discontinued']
        if value not in valid_statuses:
            raise ValueError(f"Stock status must be one of: {valid_statuses}")
        return value
    
    @property
    def needs_reorder(self) -> bool:
        """Check if inventory item needs reordering."""
        if self.reorder_point:
            return self.quantity_available <= self.reorder_point
        return False
    
    @property
    def days_since_last_movement(self) -> Optional[int]:
        """Calculate days since last stock movement."""
        last_movement = max(
            self.last_received_date or datetime.min,
            self.last_issued_date or datetime.min
        )
        if last_movement != datetime.min:
            return (datetime.utcnow() - last_movement).days
        return None


class StockMovement(TenantModel):
    """
    Stock Movements with Double-Entry Bookkeeping - all inventory transactions.
    
    Raktármozgások kettős könyvelés elvvel (összes készlet tranzakció)
    """
    __tablename__ = "stock_movements"
    
    # Movement identification
    movement_number = Column(String(50), nullable=False, unique=True, index=True)
    
    # References
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False, index=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False, index=True)
    
    # Movement details
    movement_type = Column(String(50), nullable=False, index=True)  # 'receipt', 'issue', 'transfer', 'adjustment', 'return'
    movement_reason = Column(String(100), nullable=True, index=True)  # 'purchase', 'usage', 'damaged', 'obsolete', etc.
    reference_type = Column(String(50), nullable=True)  # 'work_order', 'purchase_order', 'transfer_order'
    reference_id = Column(Integer, nullable=True, index=True)
    
    # Double-Entry Bookkeeping - Kettős könyvelés
    debit_quantity = Column(Numeric(15, 3), nullable=False, default=0)   # Tartozik oldal (beáramlás)
    credit_quantity = Column(Numeric(15, 3), nullable=False, default=0)  # Követel oldal (kiáramlás)
    
    # Legacy quantity field for compatibility
    quantity = Column(Numeric(15, 3), nullable=False)
    unit_cost = Column(Numeric(10, 4), nullable=True)
    total_cost = Column(Numeric(15, 2), nullable=True)
    
    # Balances after movement
    quantity_before = Column(Numeric(15, 3), nullable=False)
    quantity_after = Column(Numeric(15, 3), nullable=False)
    
    # Movement execution
    movement_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    processed_by = Column(String(200), nullable=True)
    processed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Additional information
    notes = Column(Text, nullable=True)
    location_from = Column(String(100), nullable=True)
    location_to = Column(String(100), nullable=True)
    
    # Document references
    document_number = Column(String(100), nullable=True, index=True)
    batch_number = Column(String(100), nullable=True)
    serial_number = Column(String(100), nullable=True)
    
    # Status and validation
    status = Column(String(50), default='completed', nullable=False)  # 'pending', 'completed', 'cancelled', 'reversed'
    is_validated = Column(Boolean, default=False, nullable=False)
    validated_by = Column(String(200), nullable=True)
    validated_at = Column(DateTime, nullable=True)
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSONB, nullable=True, default=lambda: {})
    
    # Relationships
    warehouse = relationship("Warehouse", back_populates="stock_movements")
    inventory_item = relationship("InventoryItem", back_populates="stock_movements")
    part = relationship("Part")
    processed_by_user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index("idx_stock_movement_warehouse", "warehouse_id"),
        Index("idx_stock_movement_inventory", "inventory_item_id"),
        Index("idx_stock_movement_part", "part_id"),
        Index("idx_stock_movement_type", "movement_type"),
        Index("idx_stock_movement_date", "movement_date"),
        Index("idx_stock_movement_reference", "reference_type", "reference_id"),
        Index("idx_stock_movement_document", "document_number"),
        Index("idx_stock_movement_status", "status"),
    )
    
    @validates("movement_type")
    def validate_movement_type(self, key, value):
        valid_types = ['receipt', 'issue', 'transfer', 'adjustment', 'return', 'waste', 'found']
        if value not in valid_types:
            raise ValueError(f"Movement type must be one of: {valid_types}")
        return value
    
    @validates("status")
    def validate_status(self, key, value):
        valid_statuses = ['pending', 'completed', 'cancelled', 'reversed', 'error']
        if value not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        return value


class InventoryAuditLog(BaseModel):
    """
    Inventory Audit Logs - audit trail for inventory-specific changes.
    
    Készlet audit naplók (készlet-specifikus változások nyomvonala)
    """
    __tablename__ = "inventory_audit_logs"
    
    # Entity information
    entity_type = Column(String(100), nullable=False, index=True)  # Table/model name
    entity_id = Column(Integer, nullable=False, index=True)
    
    # Action information
    action = Column(String(50), nullable=False, index=True)  # 'create', 'update', 'delete', 'login', 'logout'
    action_description = Column(String(500), nullable=True)
    
    # User context
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    username = Column(String(100), nullable=True)
    organization_id = Column(Integer, nullable=True, index=True)
    
    # Session context
    session_id = Column(String(100), nullable=True, index=True)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Change details
    old_values = Column(JSONB, nullable=True)  # Previous values
    new_values = Column(JSONB, nullable=True)  # New values
    changed_fields = Column(JSONB, nullable=True)  # Array of changed field names
    
    # Context information
    request_method = Column(String(10), nullable=True)
    request_path = Column(String(1000), nullable=True)
    request_id = Column(String(100), nullable=True, index=True)
    
    # Timing
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    duration_ms = Column(Integer, nullable=True)  # Processing duration
    
    # Result and status
    success = Column(Boolean, nullable=False, default=True)
    error_message = Column(Text, nullable=True)
    
    # Risk assessment
    risk_level = Column(String(20), default='low', nullable=False)  # 'low', 'medium', 'high', 'critical'
    compliance_flags = Column(JSONB, nullable=True)  # Array of compliance-related flags
    
    # Relationships
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index("idx_audit_entity", "entity_type", "entity_id"),
        Index("idx_audit_action", "action"),
        Index("idx_audit_user", "user_id"),
        Index("idx_audit_org", "organization_id"),
        Index("idx_audit_timestamp", "timestamp"),
        Index("idx_audit_session", "session_id"),
        Index("idx_audit_risk", "risk_level"),
        Index("idx_audit_success", "success"),
        Index("idx_audit_request", "request_id"),
    )
    
    @validates("action")
    def validate_action(self, key, value):
        valid_actions = [
            'create', 'update', 'delete', 'login', 'logout', 'access', 'export',
            'import', 'approve', 'reject', 'escalate', 'close', 'reopen'
        ]
        if value not in valid_actions:
            raise ValueError(f"Action must be one of: {valid_actions}")
        return value
    
    @validates("risk_level")
    def validate_risk_level(self, key, value):
        valid_levels = ['low', 'medium', 'high', 'critical']
        if value not in valid_levels:
            raise ValueError(f"Risk level must be one of: {valid_levels}")
        return value


class Event(TenantModel):
    """
    Events - business events and notifications.
    
    Események (üzleti események és értesítések)
    """
    __tablename__ = "events"
    
    # Event information
    event_type = Column(String(100), nullable=False, index=True)
    event_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Entity references
    entity_type = Column(String(100), nullable=True, index=True)
    entity_id = Column(Integer, nullable=True, index=True)
    
    # Event data
    event_data = Column(JSONB, nullable=True)  # Event-specific data
    event_metadata = Column(JSONB, nullable=True)   # Additional metadata
    
    # Timing
    occurred_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    scheduled_for = Column(DateTime, nullable=True, index=True)
    
    # Processing
    processing_status = Column(String(50), default='pending', nullable=False)  # 'pending', 'processed', 'failed', 'skipped'
    processed_at = Column(DateTime, nullable=True)
    processing_attempts = Column(Integer, default=0, nullable=False)
    last_error = Column(Text, nullable=True)
    
    # Priority and categorization
    priority = Column(String(20), default='normal', nullable=False)  # 'low', 'normal', 'high', 'urgent'
    severity = Column(String(20), default='info', nullable=False)   # 'info', 'warning', 'error', 'critical'
    category = Column(String(100), nullable=True, index=True)
    tags = Column(JSONB, nullable=True)  # Array of tags
    
    # Source information
    source_system = Column(String(100), nullable=True)
    source_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    source_ip = Column(INET, nullable=True)
    
    # Notification tracking
    notifications_sent = Column(Boolean, default=False, nullable=False)
    notification_count = Column(Integer, default=0, nullable=False)
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSONB, nullable=True, default=lambda: {})
    
    # Relationships
    source_user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index("idx_event_type", "event_type"),
        Index("idx_event_entity", "entity_type", "entity_id"),
        Index("idx_event_occurred", "occurred_at"),
        Index("idx_event_scheduled", "scheduled_for"),
        Index("idx_event_processing", "processing_status"),
        Index("idx_event_priority", "priority"),
        Index("idx_event_severity", "severity"),
        Index("idx_event_category", "category"),
        Index("idx_event_source", "source_user_id"),
    )
    
    @validates("processing_status")
    def validate_processing_status(self, key, value):
        valid_statuses = ['pending', 'processed', 'failed', 'skipped', 'retry']
        if value not in valid_statuses:
            raise ValueError(f"Processing status must be one of: {valid_statuses}")
        return value
    
    @validates("priority")
    def validate_priority(self, key, value):
        valid_priorities = ['low', 'normal', 'high', 'urgent']
        if value not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}")
        return value
    
    @validates("severity")
    def validate_severity(self, key, value):
        valid_severities = ['info', 'warning', 'error', 'critical']
        if value not in valid_severities:
            raise ValueError(f"Severity must be one of: {valid_severities}")
        return value


class StockAlert(TenantModel):
    """
    Stock level alerts for minimum stock warnings and notifications.
    
    Készletszint riasztások minimumkészlet figyelmeztetésekhez
    """
    __tablename__ = "stock_alerts"
    
    # Alert identification
    alert_type = Column(String(50), nullable=False, index=True)  # 'low_stock', 'out_of_stock', 'overstock', 'reorder_needed'
    status = Column(String(20), nullable=False, default="active", index=True)  # 'active', 'acknowledged', 'resolved', 'dismissed'
    
    # References
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False, index=True)
    
    # Alert details
    current_quantity = Column(Numeric(15, 3), nullable=False)
    threshold_quantity = Column(Numeric(15, 3), nullable=False)
    severity = Column(String(20), nullable=False, default="medium")  # 'low', 'medium', 'high', 'critical'
    
    # Calculated values
    shortage_quantity = Column(Numeric(15, 3), nullable=True)  # Hiányzó mennyiség
    days_of_stock = Column(Integer, nullable=True)  # Hány napra elegendő a készlet
    
    # Timestamps
    first_detected = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # Users
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Alert information
    message = Column(String(500), nullable=True)
    action_required = Column(String(500), nullable=True)
    priority = Column(String(20), nullable=False, default="normal")  # 'low', 'normal', 'high', 'urgent'
    
    # Notification tracking
    notifications_sent = Column(Integer, nullable=False, default=0)
    last_notification_sent = Column(DateTime, nullable=True)
    
    # Business impact
    estimated_cost_impact = Column(Numeric(12, 2), nullable=True)
    business_criticality = Column(String(20), nullable=True)  # 'low', 'medium', 'high', 'critical'
    
    # Settings and metadata
    auto_reorder_enabled = Column(Boolean, nullable=False, default=False)
    auto_reorder_triggered = Column(Boolean, nullable=False, default=False)
    settings = Column(JSONB, nullable=True, default=lambda: {})
    
    # Relationships
    inventory_item = relationship("InventoryItem")
    warehouse = relationship("Warehouse")
    part = relationship("Part")
    acknowledged_by_user = relationship("User", foreign_keys=[acknowledged_by])
    resolved_by_user = relationship("User", foreign_keys=[resolved_by])
    
    # Indexes
    __table_args__ = (
        Index("idx_stock_alert_type", "alert_type"),
        Index("idx_stock_alert_status", "status"),
        Index("idx_stock_alert_inventory", "inventory_item_id"),
        Index("idx_stock_alert_warehouse", "warehouse_id"),
        Index("idx_stock_alert_part", "part_id"),
        Index("idx_stock_alert_severity", "severity"),
        Index("idx_stock_alert_detected", "first_detected"),
        Index("idx_stock_alert_priority", "priority"),
        Index("idx_stock_alert_business", "business_criticality"),
    )
    
    def __repr__(self):
        return f"<StockAlert {self.alert_type}: {self.part_id} @ {self.warehouse_id}>"
    
    @validates("alert_type")
    def validate_alert_type(self, key, value):
        valid_types = ['low_stock', 'out_of_stock', 'overstock', 'reorder_needed', 'expired', 'slow_moving']
        if value not in valid_types:
            raise ValueError(f"Alert type must be one of: {valid_types}")
        return value
    
    @validates("status")
    def validate_status(self, key, value):
        valid_statuses = ['active', 'acknowledged', 'resolved', 'dismissed', 'expired']
        if value not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        return value
    
    @validates("severity")
    def validate_severity(self, key, value):
        valid_severities = ['low', 'medium', 'high', 'critical']
        if value not in valid_severities:
            raise ValueError(f"Severity must be one of: {valid_severities}")
        return value
    
    @validates("priority")
    def validate_priority(self, key, value):
        valid_priorities = ['low', 'normal', 'high', 'urgent']
        if value not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}")
        return value


class StockTake(TenantModel):
    """
    Physical stock takes and cycle counts for inventory management.
    
    Fizikai leltárok és ciklikus számlálások a készletkezeléshez
    """
    __tablename__ = "stock_takes"
    
    # Stock take identification
    stock_take_number = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Scope and type
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)
    stock_take_type = Column(String(20), nullable=False, default="full")  # 'full', 'partial', 'cycle', 'spot'
    
    # Status and timing
    status = Column(String(20), nullable=False, default="planned", index=True)  # 'planned', 'in_progress', 'completed', 'cancelled'
    planned_date = Column(DateTime, nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Users and responsibility
    planned_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    performed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    supervised_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Counters and summary
    items_planned = Column(Integer, nullable=False, default=0)
    items_counted = Column(Integer, nullable=False, default=0)
    items_with_variance = Column(Integer, nullable=False, default=0)
    adjustments_created = Column(Integer, nullable=False, default=0)
    
    # Financial impact
    total_variance_quantity = Column(Numeric(15, 3), nullable=False, default=0)
    total_variance_value = Column(Numeric(15, 2), nullable=False, default=0)
    variance_percentage = Column(Numeric(5, 2), nullable=True)
    
    # Settings and controls
    freeze_movements = Column(Boolean, nullable=False, default=True)  # Mozgások befagyasztása leltár alatt
    variance_tolerance = Column(Numeric(5, 2), nullable=False, default=2.0)  # Tűréshatár százalékban
    require_approval = Column(Boolean, nullable=False, default=True)
    
    # Approval workflow
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approval_notes = Column(Text, nullable=True)
    
    # Settings and metadata
    settings = Column(JSONB, nullable=True, default=lambda: {})
    notes = Column(Text, nullable=True)
    
    # Relationships
    warehouse = relationship("Warehouse")
    planned_by_user = relationship("User", foreign_keys=[planned_by])
    performed_by_user = relationship("User", foreign_keys=[performed_by])
    supervised_by_user = relationship("User", foreign_keys=[supervised_by])
    approved_by_user = relationship("User", foreign_keys=[approved_by])
    stock_take_lines = relationship("StockTakeLine", back_populates="stock_take", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_stock_take_number", "stock_take_number"),
        Index("idx_stock_take_warehouse", "warehouse_id"),
        Index("idx_stock_take_status", "status"),
        Index("idx_stock_take_planned", "planned_date"),
        Index("idx_stock_take_type", "stock_take_type"),
    )
    
    def __repr__(self):
        return f"<StockTake {self.stock_take_number}: {self.name}>"
    
    @validates("stock_take_type")
    def validate_stock_take_type(self, key, value):
        valid_types = ['full', 'partial', 'cycle', 'spot', 'blind']
        if value not in valid_types:
            raise ValueError(f"Stock take type must be one of: {valid_types}")
        return value
    
    @validates("status")
    def validate_status(self, key, value):
        valid_statuses = ['planned', 'in_progress', 'completed', 'cancelled', 'pending_approval', 'approved']
        if value not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        return value


class StockTakeLine(TenantModel):
    """
    Individual stock take line items for detailed inventory counting.
    
    Egyéni leltári sorok a részletes készletszámláláshoz
    """
    __tablename__ = "stock_take_lines"
    
    # References
    stock_take_id = Column(Integer, ForeignKey("stock_takes.id"), nullable=False, index=True)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False, index=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False, index=True)
    
    # Location information
    location_code = Column(String(50), nullable=True)
    bin_location = Column(String(50), nullable=True)
    
    # Quantities
    system_quantity = Column(Numeric(15, 3), nullable=False)  # Rendszer szerinti mennyiség
    counted_quantity = Column(Numeric(15, 3), nullable=True)  # Megszámolt mennyiség
    variance_quantity = Column(Numeric(15, 3), nullable=True)  # Eltérés mennyisége
    variance_percentage = Column(Numeric(5, 2), nullable=True)  # Eltérés százalékban
    
    # Cost and financial impact
    unit_cost = Column(Numeric(10, 4), nullable=True)
    variance_value = Column(Numeric(15, 2), nullable=True)  # Eltérés értéke
    
    # Counting details
    is_counted = Column(Boolean, nullable=False, default=False)
    count_sequence = Column(Integer, nullable=True)  # Számlálási sorrend
    counted_at = Column(DateTime, nullable=True)
    counted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Variance analysis
    variance_reason = Column(String(200), nullable=True)  # Eltérés oka
    variance_category = Column(String(50), nullable=True)  # 'shrinkage', 'damage', 'error', 'theft'
    requires_investigation = Column(Boolean, nullable=False, default=False)
    
    # Adjustment tracking
    is_adjusted = Column(Boolean, nullable=False, default=False)
    adjustment_created = Column(Boolean, nullable=False, default=False)
    stock_movement_id = Column(Integer, ForeignKey("stock_movements.id"), nullable=True)
    
    # Quality and validation
    count_confidence = Column(String(20), nullable=True)  # 'high', 'medium', 'low'
    requires_recount = Column(Boolean, nullable=False, default=False)
    recount_reason = Column(String(200), nullable=True)
    
    # Notes and comments
    notes = Column(Text, nullable=True)
    counting_notes = Column(Text, nullable=True)
    
    # Relationships
    stock_take = relationship("StockTake", back_populates="stock_take_lines")
    inventory_item = relationship("InventoryItem")
    part = relationship("Part")
    counted_by_user = relationship("User", foreign_keys=[counted_by])
    adjustment_movement = relationship("StockMovement", foreign_keys=[stock_movement_id])
    
    # Indexes
    __table_args__ = (
        Index("idx_stock_take_line_stock_take", "stock_take_id"),
        Index("idx_stock_take_line_inventory", "inventory_item_id"),
        Index("idx_stock_take_line_part", "part_id"),
        Index("idx_stock_take_line_location", "location_code"),
        Index("idx_stock_take_line_counted", "is_counted"),
        Index("idx_stock_take_line_variance", "variance_quantity"),
    )
    
    def __repr__(self):
        return f"<StockTakeLine ST:{self.stock_take_id} Part:{self.part_id}>"
    
    @validates("variance_category")
    def validate_variance_category(self, key, value):
        if value is not None:
            valid_categories = ['shrinkage', 'damage', 'error', 'theft', 'obsolescence', 'found', 'unknown']
            if value not in valid_categories:
                raise ValueError(f"Variance category must be one of: {valid_categories}")
        return value
    
    @validates("count_confidence")
    def validate_count_confidence(self, key, value):
        if value is not None:
            valid_confidence = ['high', 'medium', 'low']
            if value not in valid_confidence:
                raise ValueError(f"Count confidence must be one of: {valid_confidence}")
        return value