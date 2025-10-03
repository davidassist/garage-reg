"""Tickets, work orders, and parts management models."""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Numeric, Index, Enum
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum as PyEnum

from app.models import TenantModel


class TicketStatus(PyEnum):
    """Ticket workflow status states."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"  
    WAITING_PARTS = "waiting_parts"
    DONE = "done"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class TicketPriority(PyEnum):
    """Ticket priority levels affecting SLA times."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class WorkOrderStatus(PyEnum):
    """Work order status states."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    WAITING_PARTS = "waiting_parts"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Ticket(TenantModel):
    """
    Tickets - issue reports and service requests.
    
    Hibajegyek (hibabejelentések és szerviz kérések)
    """
    __tablename__ = "tickets"
    
    # References
    gate_id = Column(Integer, ForeignKey("gates.id"), nullable=False, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    assigned_technician_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Ticket identification
    ticket_number = Column(String(50), nullable=False, unique=True, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    
    # Categorization
    category = Column(String(100), nullable=False, index=True)  # 'malfunction', 'maintenance', 'installation', 'inspection'
    subcategory = Column(String(100), nullable=True, index=True)
    issue_type = Column(String(100), nullable=False, index=True)  # 'electrical', 'mechanical', 'software', 'safety'
    
    # Problem details
    symptoms = Column(Text, nullable=True)
    error_codes = Column(JSONB, nullable=True)  # Array of error codes
    affected_components = Column(JSONB, nullable=True)  # Array of component IDs
    
    # Context information
    reported_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    occurred_at = Column(DateTime, nullable=True)
    first_noticed_at = Column(DateTime, nullable=True)
    weather_conditions = Column(String(200), nullable=True)
    usage_context = Column(Text, nullable=True)  # What was happening when issue occurred
    
    # Priority and urgency - Using string (stored as string in DB)
    priority = Column(String(20), default="MEDIUM", nullable=False, index=True)
    urgency = Column(String(20), default='normal', nullable=False)  # 'low', 'normal', 'high', 'emergency'
    severity = Column(String(20), default='medium', nullable=False)  # 'low', 'medium', 'high', 'critical'
    impact = Column(String(20), default='medium', nullable=False)  # 'low', 'medium', 'high', 'critical'
    
    # Safety considerations
    safety_hazard = Column(Boolean, default=False, nullable=False)
    safety_description = Column(Text, nullable=True)
    immediate_danger = Column(Boolean, default=False, nullable=False)
    
    # Status tracking - Full lifecycle state machine (stored as string)
    status = Column(String(50), default="OPEN", nullable=False, index=True)
    resolution_status = Column(String(50), nullable=True)  # 'fixed', 'workaround', 'duplicate', 'not_reproducible', 'wont_fix'
    
    # Time tracking
    acknowledged_at = Column(DateTime, nullable=True)
    assigned_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    
    # Service Level Agreements - Simplified SLA tracking (matching DB schema)
    sla_response_by = Column(DateTime, nullable=True, index=True)
    sla_resolution_by = Column(DateTime, nullable=True, index=True)
    sla_met = Column(Boolean, nullable=True)  # Simplified SLA status
    
    # Communication
    contact_method = Column(String(50), nullable=True)  # 'phone', 'email', 'app', 'onsite'
    contact_phone = Column(String(50), nullable=True)
    contact_email = Column(String(320), nullable=True)
    
    # Resolution information
    resolution_description = Column(Text, nullable=True)
    root_cause = Column(Text, nullable=True)
    preventive_actions = Column(Text, nullable=True)
    
    # Follow-up
    followup_required = Column(Boolean, default=False, nullable=False)
    followup_date = Column(DateTime, nullable=True)
    customer_satisfaction = Column(Integer, nullable=True)  # 1-5 rating
    
    # Cost tracking
    estimated_cost = Column(Numeric(10, 2), nullable=True)
    actual_cost = Column(Numeric(10, 2), nullable=True)
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSONB, nullable=True, default=lambda: {})
    
    # Relationships
    gate = relationship("Gate", back_populates="tickets")
    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="reported_tickets")
    assigned_technician = relationship("User", foreign_keys=[assigned_technician_id], back_populates="assigned_tickets")
    work_orders = relationship("WorkOrder", back_populates="ticket")
    status_history = relationship("TicketStatusHistory", back_populates="ticket", cascade="all, delete-orphan")
    comments = relationship("TicketComment", back_populates="ticket", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Ticket {self.ticket_number}: {self.title}>"
    
    @property
    def is_sla_response_overdue(self) -> bool:
        """Check if response SLA is overdue."""
        if not self.sla_response_by or self.acknowledged_at:
            return False
        return datetime.utcnow() > self.sla_response_by
    
    @property
    def is_sla_resolution_overdue(self) -> bool:
        """Check if resolution SLA is overdue."""
        if not self.sla_resolution_by or self.resolved_at:
            return False
        return datetime.utcnow() > self.sla_resolution_by
    
    @property
    def sla_response_hours(self) -> Optional[int]:
        """Calculate response hours from due date."""
        if self.sla_response_by and self.reported_at:
            delta = self.sla_response_by - self.reported_at
            return int(delta.total_seconds() / 3600)
        return None
    
    @property
    def sla_resolution_hours(self) -> Optional[int]:
        """Calculate resolution hours from due date.""" 
        if self.sla_resolution_by and self.reported_at:
            delta = self.sla_resolution_by - self.reported_at
            return int(delta.total_seconds() / 3600)
        return None
    
    @property
    def time_to_acknowledge(self) -> Optional[timedelta]:
        """Calculate time taken to acknowledge ticket."""
        if self.acknowledged_at:
            return self.acknowledged_at - self.reported_at
        return None
    
    @property  
    def time_to_resolve(self) -> Optional[timedelta]:
        """Calculate time taken to resolve ticket."""
        if self.resolved_at:
            return self.resolved_at - self.reported_at
        return None
    
    def calculate_sla_due_dates(self):
        """Calculate SLA due dates based on priority."""
        # SLA times by priority (in hours)
        sla_config = {
            TicketPriority.EMERGENCY: {"response": 1, "resolution": 4},
            TicketPriority.CRITICAL: {"response": 2, "resolution": 8}, 
            TicketPriority.HIGH: {"response": 4, "resolution": 24},
            TicketPriority.MEDIUM: {"response": 8, "resolution": 72},
            TicketPriority.LOW: {"response": 24, "resolution": 168}
        }
        
        # Convert string priority to enum for config lookup
        priority_enum = TicketPriority(self.priority.lower()) if isinstance(self.priority, str) else self.priority
        config = sla_config.get(priority_enum, sla_config[TicketPriority.MEDIUM])
        
        base_time = self.reported_at or datetime.utcnow()
        self.sla_response_by = base_time + timedelta(hours=config["response"])
        self.sla_resolution_by = base_time + timedelta(hours=config["resolution"])
    
    def check_sla_breaches(self):
        """Check and update SLA breach status (simplified).""" 
        # Set SLA met status
        if self.resolved_at and self.sla_resolution_by:
            self.sla_met = self.resolved_at <= self.sla_resolution_by
        elif self.acknowledged_at and self.sla_response_by:
            # If not yet resolved, check response SLA
            self.sla_met = self.acknowledged_at <= self.sla_response_by
        elif self.is_sla_response_overdue or self.is_sla_resolution_overdue:
            self.sla_met = False
    
    # Indexes
    __table_args__ = (
        Index("idx_ticket_gate", "gate_id"),
        Index("idx_ticket_number", "ticket_number"),
        Index("idx_ticket_reporter", "reporter_id"),
        Index("idx_ticket_assigned", "assigned_technician_id"),
        Index("idx_ticket_category", "category"),
        Index("idx_ticket_issue_type", "issue_type"),
        Index("idx_ticket_priority", "priority"),
        Index("idx_ticket_status", "status"),
        Index("idx_ticket_reported_date", "reported_at"),
        Index("idx_ticket_sla_response", "sla_response_by"),
        Index("idx_ticket_sla_resolution", "sla_resolution_by"),
        Index("idx_ticket_safety", "safety_hazard"),
    )
    



class WorkOrder(TenantModel):
    """
    Work Orders - formal work instructions and execution tracking.
    
    Munkalapok (formális munkautasítások és végrehajtás követés)
    """
    __tablename__ = "work_orders"
    
    # References
    gate_id = Column(Integer, ForeignKey("gates.id"), nullable=False, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=True, index=True)
    maintenance_job_id = Column(Integer, ForeignKey("maintenance_jobs.id"), nullable=True, index=True)
    assigned_technician_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Work order identification
    work_order_number = Column(String(50), nullable=False, unique=True, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    
    # Work details
    work_type = Column(String(50), nullable=False, index=True)  # 'repair', 'maintenance', 'installation', 'inspection', 'replacement'
    work_category = Column(String(100), nullable=False, index=True)
    instructions = Column(Text, nullable=True)
    safety_requirements = Column(Text, nullable=True)
    
    # Scheduling and timing
    scheduled_start = Column(DateTime, nullable=True, index=True)
    scheduled_end = Column(DateTime, nullable=True)
    estimated_duration_hours = Column(Numeric(5, 2), nullable=True)
    
    # Execution tracking
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    actual_duration_hours = Column(Numeric(5, 2), nullable=True)
    
    # Status and progress - Using string for database storage, validated via enum logic
    status = Column(String(20), default='draft', nullable=False, index=True)
    progress_percentage = Column(Integer, default=0, nullable=False)
    
    # Priority and urgency
    priority = Column(String(20), default='medium', nullable=False)
    urgency = Column(String(20), default='normal', nullable=False)
    
    # Resource requirements
    required_skills = Column(JSONB, nullable=True)  # Array of required skills
    required_tools = Column(JSONB, nullable=True)  # Array of required tools
    required_parts = Column(JSONB, nullable=True)  # Array of required parts
    
    # Results and completion
    work_performed = Column(Text, nullable=True)
    issues_encountered = Column(Text, nullable=True)
    parts_used = Column(JSONB, nullable=True)  # Parts actually used
    tools_used = Column(JSONB, nullable=True)  # Tools actually used
    
    # Quality and inspection
    quality_check_passed = Column(Boolean, nullable=True)
    quality_notes = Column(Text, nullable=True)
    customer_approval = Column(Boolean, nullable=True)
    customer_signature = Column(String(500), nullable=True)  # Digital signature or reference
    
    # Cost tracking
    estimated_labor_cost = Column(Numeric(10, 2), nullable=True)
    estimated_parts_cost = Column(Numeric(10, 2), nullable=True)
    actual_labor_cost = Column(Numeric(10, 2), nullable=True)
    actual_parts_cost = Column(Numeric(10, 2), nullable=True)
    total_cost = Column(Numeric(10, 2), nullable=True)
    
    # Follow-up
    followup_required = Column(Boolean, default=False, nullable=False)
    next_maintenance_date = Column(DateTime, nullable=True)
    warranty_period_months = Column(Integer, nullable=True)
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSONB, nullable=True, default=lambda: {})
    
    # Relationships
    gate = relationship("Gate", back_populates="work_orders")
    ticket = relationship("Ticket", back_populates="work_orders")
    maintenance_job = relationship("MaintenanceJob", back_populates="work_orders")
    assigned_technician = relationship("User", back_populates="work_orders")
    work_order_items = relationship("WorkOrderItem", back_populates="work_order", cascade="all, delete-orphan")
    part_usages = relationship("PartUsage", back_populates="work_order")
    time_logs = relationship("WorkOrderTimeLog", back_populates="work_order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WorkOrder {self.work_order_number}: {self.title}>"
    
    @property
    def total_labor_cost(self) -> Optional[float]:
        """Calculate total labor cost based on time logs."""
        if not self.time_logs:
            return None
        return sum(log.cost for log in self.time_logs if log.cost)
    
    @property 
    def total_parts_cost(self) -> Optional[float]:
        """Calculate total parts cost from part usages."""
        if not self.part_usages:
            return None
        return sum(usage.total_cost for usage in self.part_usages if usage.total_cost)
    
    @property
    def total_cost(self) -> Optional[float]:
        """Calculate total work order cost (labor + parts)."""
        labor_cost = self.total_labor_cost or 0
        parts_cost = self.total_parts_cost or 0
        return labor_cost + parts_cost if (labor_cost or parts_cost) else None
    
    # Indexes
    __table_args__ = (
        Index("idx_work_order_gate", "gate_id"),
        Index("idx_work_order_ticket", "ticket_id"),
        Index("idx_work_order_maintenance", "maintenance_job_id"),
        Index("idx_work_order_number", "work_order_number"),
        Index("idx_work_order_assigned", "assigned_technician_id"),
        Index("idx_work_order_type", "work_type"),
        Index("idx_work_order_status", "status"),
        Index("idx_work_order_scheduled", "scheduled_start"),
        Index("idx_work_order_priority", "priority"),
    )
    
    @validates("status")
    def validate_status(self, key, value):
        # Valid statuses must match WorkOrderStatus enum values
        valid_statuses = ['draft', 'scheduled', 'in_progress', 'waiting_parts', 'completed', 'cancelled']
        if value not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        return value
    
    @validates("work_type")
    def validate_work_type(self, key, value):
        valid_types = ['repair', 'maintenance', 'installation', 'inspection', 'replacement', 'upgrade']
        if value not in valid_types:
            raise ValueError(f"Work type must be one of: {valid_types}")
        return value


class WorkOrderItem(TenantModel):
    """
    Work Order Items - individual tasks within a work order.
    
    Munkalap tételek (munkalapon belüli egyes feladatok)
    """
    __tablename__ = "work_order_items"
    
    # Work order reference
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False, index=True)
    
    # Item details
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False, default=0)
    
    # Time tracking
    estimated_duration_minutes = Column(Integer, nullable=True)
    actual_duration_minutes = Column(Integer, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Status and results
    status = Column(String(50), default='pending', nullable=False)  # 'pending', 'in_progress', 'completed', 'skipped', 'failed'
    result = Column(String(50), nullable=True)  # 'success', 'partial', 'failed', 'na'
    notes = Column(Text, nullable=True)
    
    # Quality check
    requires_verification = Column(Boolean, default=False, nullable=False)
    verified = Column(Boolean, nullable=True)
    verified_by = Column(String(200), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSONB, nullable=True, default=lambda: {})
    
    # Relationships
    work_order = relationship("WorkOrder", back_populates="work_order_items")
    
    # Indexes
    __table_args__ = (
        Index("idx_work_order_item_wo", "work_order_id"),
        Index("idx_work_order_item_order", "order_index"),
        Index("idx_work_order_item_status", "status"),
    )
    
    @validates("status")
    def validate_status(self, key, value):
        valid_statuses = ['pending', 'in_progress', 'completed', 'skipped', 'failed', 'blocked']
        if value not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        return value


class Part(TenantModel):
    """
    Parts - spare parts and components inventory.
    
    Alkatrészek (tartalék alkatrészek és komponensek)
    """
    __tablename__ = "parts"
    
    # Part identification
    part_number = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, index=True)
    
    # Manufacturer information
    manufacturer = Column(String(100), nullable=True, index=True)
    manufacturer_part_number = Column(String(100), nullable=True, index=True)
    supplier = Column(String(100), nullable=True)
    supplier_part_number = Column(String(100), nullable=True)
    
    # Compatibility
    compatible_gate_types = Column(JSONB, nullable=True)  # Array of compatible gate types
    compatible_manufacturers = Column(JSONB, nullable=True)  # Array of compatible manufacturers
    compatible_models = Column(JSONB, nullable=True)  # Array of compatible models
    replaces_parts = Column(JSONB, nullable=True)  # Array of part numbers this replaces
    
    # Physical properties
    weight_kg = Column(Numeric(8, 3), nullable=True)
    dimensions_cm = Column(String(50), nullable=True)  # L x W x H
    material = Column(String(100), nullable=True)
    color = Column(String(50), nullable=True)
    
    # Inventory information
    unit_of_measure = Column(String(20), default='piece', nullable=False)
    minimum_stock_level = Column(Integer, default=0, nullable=False)
    maximum_stock_level = Column(Integer, nullable=True)
    reorder_point = Column(Integer, nullable=True)
    reorder_quantity = Column(Integer, nullable=True)
    
    # Cost information
    standard_cost = Column(Numeric(10, 2), nullable=True)
    last_purchase_cost = Column(Numeric(10, 2), nullable=True)
    average_cost = Column(Numeric(10, 2), nullable=True)
    
    # Lifecycle information
    lifecycle_status = Column(String(50), default='active', nullable=False)  # 'active', 'obsolete', 'discontinued'
    introduction_date = Column(DateTime, nullable=True)
    discontinuation_date = Column(DateTime, nullable=True)
    
    # Quality and specifications
    quality_grade = Column(String(20), nullable=True)  # 'OEM', 'aftermarket', 'generic'
    specifications = Column(JSONB, nullable=True)  # Technical specifications
    certifications = Column(JSONB, nullable=True)  # Array of certifications
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSONB, nullable=True, default=lambda: {})
    
    # Relationships
    part_usages = relationship("PartUsage", back_populates="part")
    inventory_items = relationship("InventoryItem", back_populates="part")
    
    # Indexes
    __table_args__ = (
        Index("idx_part_number", "part_number"),
        Index("idx_part_name", "name"),
        Index("idx_part_category", "category"),
        Index("idx_part_manufacturer", "manufacturer"),
        Index("idx_part_mfg_part_number", "manufacturer_part_number"),
        Index("idx_part_lifecycle", "lifecycle_status"),
        Index("idx_part_active", "is_active"),
    )
    
    @validates("lifecycle_status")
    def validate_lifecycle_status(self, key, value):
        valid_statuses = ['active', 'obsolete', 'discontinued', 'end_of_life']
        if value not in valid_statuses:
            raise ValueError(f"Lifecycle status must be one of: {valid_statuses}")
        return value


class PartUsage(TenantModel):
    """
    Part Usage - tracking of parts used in work orders with inventory integration.
    
    Alkatrész felhasználás (munkalapoknál használt alkatrészek raktárkezeléssel)
    """
    __tablename__ = "part_usages"
    
    # References
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False, index=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False, index=True)
    gate_id = Column(Integer, ForeignKey("gates.id"), nullable=False, index=True)
    component_id = Column(Integer, ForeignKey("gate_components.id"), nullable=True, index=True)
    
    # Inventory integration
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=True, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True, index=True)
    stock_movement_id = Column(Integer, ForeignKey("stock_movements.id"), nullable=True, index=True)
    
    # Usage details
    quantity_used = Column(Numeric(10, 3), nullable=False)
    quantity_issued = Column(Numeric(10, 3), nullable=True)  # Kiadott mennyiség (lehet több, mint felhasznált)
    unit_cost = Column(Numeric(10, 2), nullable=True)
    total_cost = Column(Numeric(10, 2), nullable=True)
    
    # Inventory tracking
    batch_number = Column(String(100), nullable=True)
    serial_number = Column(String(100), nullable=True)
    reserved_at = Column(DateTime, nullable=True)
    issued_at = Column(DateTime, nullable=True)
    consumed_at = Column(DateTime, nullable=True)
    
    # Context
    usage_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    used_by = Column(String(200), nullable=True)
    usage_reason = Column(String(200), nullable=True)  # 'replacement', 'repair', 'maintenance', 'upgrade'
    
    # Location and installation
    installation_location = Column(String(200), nullable=True)
    installation_notes = Column(Text, nullable=True)
    
    # Warranty for installed part
    warranty_start_date = Column(DateTime, nullable=True)
    warranty_end_date = Column(DateTime, nullable=True)
    warranty_terms = Column(Text, nullable=True)
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSONB, nullable=True, default=lambda: {})
    
    # Relationships
    work_order = relationship("WorkOrder", back_populates="part_usages")
    part = relationship("Part", back_populates="part_usages")
    gate = relationship("Gate")
    component = relationship("GateComponent", back_populates="part_usages")
    inventory_item = relationship("InventoryItem", back_populates="part_usages")
    warehouse = relationship("Warehouse")
    stock_movement = relationship("StockMovement")
    
    # Indexes
    __table_args__ = (
        Index("idx_part_usage_work_order", "work_order_id"),
        Index("idx_part_usage_part", "part_id"),
        Index("idx_part_usage_gate", "gate_id"),
        Index("idx_part_usage_component", "component_id"),
        Index("idx_part_usage_date", "usage_date"),
        Index("idx_part_usage_reason", "usage_reason"),
    )


class TicketComment(TenantModel):
    """
    Ticket Comment Model - Comments and communication on tickets.
    
    Ticket megjegyzés modell - megjegyzések és kommunikáció a ticketeken.
    """
    __tablename__ = "ticket_comments"

    # References
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Content
    content = Column(Text, nullable=False)
    comment_type = Column(String(50), default="comment", nullable=False)  # comment, status_change, system, resolution
    
    # Visibility and Classification
    is_internal = Column(Boolean, default=False, nullable=False)  # Internal vs customer-visible
    is_solution = Column(Boolean, default=False, nullable=False)  # Mark as solution
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    attachments = Column(JSONB, nullable=True)  # File references
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSONB, nullable=True, default=lambda: {})
    
    # Relationships
    ticket = relationship("Ticket", back_populates="comments")
    author = relationship("User", foreign_keys=[author_id])
    
    def __repr__(self):
        return f"<TicketComment {self.id}: {self.content[:50]}...>"


class TicketStatusHistory(TenantModel):
    """
    Ticket Status History Model - Track all status changes for audit trail.
    
    Ticket státusz történet modell - összes státusz változás nyomon követése.
    """
    __tablename__ = "ticket_status_history"

    # References
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False, index=True)
    changed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Status Change Details
    old_status = Column(Enum(TicketStatus), nullable=True)
    new_status = Column(Enum(TicketStatus), nullable=False)
    change_reason = Column(Text, nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Additional Context
    old_assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    new_assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSONB, nullable=True, default=lambda: {})
    
    # Relationships
    ticket = relationship("Ticket", back_populates="status_history")
    changed_by = relationship("User", foreign_keys=[changed_by_id])
    old_assignee = relationship("User", foreign_keys=[old_assignee_id])
    new_assignee = relationship("User", foreign_keys=[new_assignee_id])
    
    def __repr__(self):
        return f"<TicketStatusHistory Ticket:{self.ticket_id} {self.old_status}→{self.new_status}>"


class WorkOrderTimeLog(TenantModel):
    """
    Work Order Time Log Model - Track time spent on work orders for cost calculation.
    
    Munkarendelés időnapló modell - munkarendelésekre fordított idő nyomon követése.
    """
    __tablename__ = "work_order_time_logs"

    # References
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False, index=True)
    technician_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Time Tracking
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)  # Calculated field
    
    # Work Details
    activity_type = Column(String(50), nullable=False, index=True)  # diagnosis, repair, testing, travel, setup
    description = Column(Text, nullable=True)
    
    # Cost Calculation
    hourly_rate = Column(Numeric(8, 2), nullable=True)
    cost = Column(Numeric(10, 2), nullable=True)  # duration * rate
    
    # Billing and Classification
    is_billable = Column(Boolean, default=True, nullable=False)
    is_overtime = Column(Boolean, default=False, nullable=False)
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSONB, nullable=True, default=lambda: {})
    
    # Relationships
    work_order = relationship("WorkOrder", back_populates="time_logs")
    technician = relationship("User", foreign_keys=[technician_id])
    
    def __repr__(self):
        return f"<WorkOrderTimeLog WO:{self.work_order_id} Tech:{self.technician_id} {self.duration_minutes}min>"
    
    def calculate_duration_and_cost(self):
        """Calculate duration and cost based on start/end times."""
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            self.duration_minutes = int(duration.total_seconds() / 60)
            
            if self.hourly_rate and self.duration_minutes:
                hours = self.duration_minutes / 60
                self.cost = float(self.hourly_rate) * hours