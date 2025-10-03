"""
Pydantic schemas for tickets and work orders management.

Ticket és munkarendelés kezelés Pydantic sémái.
"""

from pydantic import BaseModel, validator, Field, EmailStr
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal

from app.models.tickets import TicketStatus, TicketPriority, WorkOrderStatus


# ===============================
# Base Schemas
# ===============================

class TicketBase(BaseModel):
    """Base ticket schema."""
    title: str = Field(..., max_length=300, description="Ticket title")
    description: str = Field(..., description="Detailed description of the issue")
    category: str = Field(..., max_length=100, description="Issue category")
    subcategory: Optional[str] = Field(None, max_length=100)
    issue_type: str = Field(..., max_length=100, description="Type of issue")
    priority: TicketPriority = Field(TicketPriority.MEDIUM, description="Ticket priority")
    urgency: str = Field("normal", description="Urgency level")
    severity: str = Field("medium", description="Severity level")
    impact: str = Field("medium", description="Impact level")
    
    # Problem details
    symptoms: Optional[str] = None
    error_codes: Optional[List[str]] = None
    affected_components: Optional[List[str]] = None
    
    # Context
    occurred_at: Optional[datetime] = None
    first_noticed_at: Optional[datetime] = None
    weather_conditions: Optional[str] = None
    usage_context: Optional[str] = None
    
    # Safety
    safety_hazard: bool = False
    safety_description: Optional[str] = None
    immediate_danger: bool = False
    
    # Communication
    contact_method: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None


class TicketCreate(TicketBase):
    """Schema for creating a new ticket."""
    gate_id: int = Field(..., description="Gate ID this ticket relates to")
    reporter_id: Optional[int] = None  # Will be set from auth context
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TicketUpdate(BaseModel):
    """Schema for updating an existing ticket."""
    title: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    issue_type: Optional[str] = Field(None, max_length=100)
    priority: Optional[TicketPriority] = None
    urgency: Optional[str] = None
    severity: Optional[str] = None
    impact: Optional[str] = None
    
    # Assignment
    assigned_technician_id: Optional[int] = None
    
    # Status (controlled by separate endpoints)
    # status: Optional[TicketStatus] = None
    
    # Resolution
    resolution_description: Optional[str] = None
    root_cause: Optional[str] = None
    preventive_actions: Optional[str] = None
    
    # Follow-up
    followup_required: Optional[bool] = None
    followup_date: Optional[datetime] = None
    
    # Cost
    estimated_cost: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    
    # Custom data
    custom_fields: Optional[Dict[str, Any]] = None


class TicketStatusChange(BaseModel):
    """Schema for changing ticket status."""
    new_status: TicketStatus = Field(..., description="New status to set")
    change_reason: Optional[str] = Field(None, description="Reason for status change")
    assignee_id: Optional[int] = Field(None, description="New assignee if changing")
    
    class Config:
        use_enum_values = True


class CommentCreate(BaseModel):
    """Schema for creating ticket comments."""
    content: str = Field(..., description="Comment content")
    comment_type: Optional[str] = Field("comment", description="Type of comment")
    is_internal: Optional[bool] = Field(False, description="Internal comment not visible to customer")
    is_solution: Optional[bool] = Field(False, description="Mark this comment as solution")
    attachments: Optional[List[Dict[str, Any]]] = None


class TicketComment(BaseModel):
    """Schema for ticket comment responses."""
    id: int
    ticket_id: int
    author_id: int
    author_name: Optional[str] = None
    content: str
    comment_type: str = "comment"
    is_internal: bool = False
    is_solution: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TicketResponse(TicketBase):
    """Schema for ticket responses."""
    id: int
    ticket_number: str
    status: TicketStatus
    gate_id: int
    reporter_id: Optional[int] = None
    assigned_technician_id: Optional[int] = None
    
    # Timestamps
    reported_at: datetime
    acknowledged_at: Optional[datetime] = None
    assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    # SLA tracking
    sla_response_hours: Optional[int] = None
    sla_resolution_hours: Optional[int] = None
    sla_response_by: Optional[datetime] = None
    sla_resolution_by: Optional[datetime] = None
    sla_response_met: Optional[bool] = None
    sla_resolution_met: Optional[bool] = None
    sla_response_breached: bool = False
    sla_resolution_breached: bool = False
    
    # Resolution
    resolution_status: Optional[str] = None
    resolution_description: Optional[str] = None
    root_cause: Optional[str] = None
    preventive_actions: Optional[str] = None
    
    # Follow-up
    followup_required: bool = False
    followup_date: Optional[datetime] = None
    customer_satisfaction: Optional[int] = None
    
    # Cost tracking
    estimated_cost: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    
    # Audit
    created_at: datetime
    updated_at: datetime
    org_id: int
    
    class Config:
        from_attributes = True
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v) if v else None
        }


# ===============================
# Work Order Schemas
# ===============================

class WorkOrderBase(BaseModel):
    """Base work order schema."""
    title: str = Field(..., max_length=300, description="Work order title")
    description: str = Field(..., description="Work instructions")
    work_type: str = Field(..., max_length=50, description="Type of work")
    work_category: str = Field(..., max_length=100, description="Work category")
    priority: TicketPriority = Field(TicketPriority.MEDIUM, description="Work priority")
    urgency: str = Field("normal", description="Urgency level")
    
    # Instructions
    instructions: Optional[str] = None
    safety_requirements: Optional[str] = None
    
    # Scheduling
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    estimated_duration_hours: Optional[Decimal] = None
    
    # Requirements
    required_skills: Optional[List[str]] = None
    required_tools: Optional[List[str]] = None
    required_parts: Optional[List[Dict[str, Any]]] = None
    
    # Cost estimation
    estimated_cost: Optional[Decimal] = None
    
    # Custom data
    custom_fields: Optional[Dict[str, Any]] = None


class WorkOrderCreate(WorkOrderBase):
    """Schema for creating a work order."""
    gate_id: int = Field(..., description="Gate ID for this work order")
    ticket_id: Optional[int] = Field(None, description="Source ticket ID if applicable")
    maintenance_job_id: Optional[int] = Field(None, description="Maintenance job ID if applicable")
    assigned_technician_id: Optional[int] = Field(None, description="Assigned technician")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v) if v else None
        }


class WorkOrderUpdate(BaseModel):
    """Schema for updating a work order."""
    title: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = None
    work_type: Optional[str] = Field(None, max_length=50)
    work_category: Optional[str] = Field(None, max_length=100)
    priority: Optional[TicketPriority] = None
    urgency: Optional[str] = None
    
    # Assignment
    assigned_technician_id: Optional[int] = None
    
    # Scheduling
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    estimated_duration_hours: Optional[Decimal] = None
    
    # Execution
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    actual_duration_hours: Optional[Decimal] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    
    # Instructions and requirements
    instructions: Optional[str] = None
    safety_requirements: Optional[str] = None
    required_skills: Optional[List[str]] = None
    required_tools: Optional[List[str]] = None
    required_parts: Optional[List[Dict[str, Any]]] = None
    
    # Results
    work_performed: Optional[str] = None
    issues_encountered: Optional[str] = None
    parts_used: Optional[List[Dict[str, Any]]] = None
    tools_used: Optional[List[Dict[str, Any]]] = None
    
    # Quality
    quality_check_passed: Optional[bool] = None
    quality_notes: Optional[str] = None
    
    # Cost tracking
    estimated_cost: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    
    # Custom data
    custom_fields: Optional[Dict[str, Any]] = None


class WorkOrderStatusChange(BaseModel):
    """Schema for changing work order status."""
    new_status: WorkOrderStatus = Field(..., description="New status to set")
    change_reason: Optional[str] = Field(None, description="Reason for status change")
    
    class Config:
        use_enum_values = True


class WorkOrderResponse(WorkOrderBase):
    """Schema for work order responses."""
    id: int
    work_order_number: str
    status: WorkOrderStatus
    gate_id: int
    ticket_id: Optional[int] = None
    maintenance_job_id: Optional[int] = None
    assigned_technician_id: Optional[int] = None
    
    # Execution tracking
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    actual_duration_hours: Optional[Decimal] = None
    progress_percentage: int = 0
    
    # Results
    work_performed: Optional[str] = None
    issues_encountered: Optional[str] = None
    parts_used: Optional[List[Dict[str, Any]]] = None
    tools_used: Optional[List[Dict[str, Any]]] = None
    
    # Quality
    quality_check_passed: Optional[bool] = None
    quality_notes: Optional[str] = None
    
    # Cost tracking
    actual_cost: Optional[Decimal] = None
    
    # Audit
    created_at: datetime
    updated_at: datetime
    org_id: int
    
    class Config:
        from_attributes = True
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v) if v else None
        }


# ===============================
# Part Usage Schemas
# ===============================

class PartUsageBase(BaseModel):
    """Base part usage schema."""
    part_id: int = Field(..., description="Part ID")
    quantity_used: Decimal = Field(..., gt=0, description="Quantity used")
    unit_cost: Optional[Decimal] = Field(None, ge=0, description="Unit cost at time of usage")
    usage_reason: Optional[str] = Field(None, description="Reason for usage")
    usage_notes: Optional[str] = None
    
    # Quality tracking
    batch_number: Optional[str] = None
    serial_number: Optional[str] = None
    warranty_months: Optional[int] = Field(None, ge=0)


class PartUsageCreate(PartUsageBase):
    """Schema for creating part usage."""
    work_order_id: int = Field(..., description="Work order ID")
    gate_id: int = Field(..., description="Gate ID")
    component_id: Optional[int] = Field(None, description="Component ID if applicable")
    
    # Installation details
    installation_location: Optional[str] = None
    installation_notes: Optional[str] = None


class PartUsageResponse(PartUsageBase):
    """Schema for part usage responses."""
    id: int
    work_order_id: int
    gate_id: int
    component_id: Optional[int] = None
    total_cost: Optional[Decimal] = None
    usage_date: datetime
    used_by: Optional[str] = None
    
    # Installation details
    installation_location: Optional[str] = None
    installation_notes: Optional[str] = None
    
    # Warranty
    warranty_start_date: Optional[datetime] = None
    warranty_end_date: Optional[datetime] = None
    warranty_terms: Optional[str] = None
    
    # Audit
    created_at: datetime
    updated_at: datetime
    org_id: int
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v) if v else None
        }


# ===============================
# Time Log Schemas  
# ===============================

class TimeLogBase(BaseModel):
    """Base time log schema."""
    activity_type: str = Field(..., max_length=50, description="Type of activity")
    description: Optional[str] = Field(None, description="Activity description")
    hourly_rate: Optional[Decimal] = Field(None, ge=0, description="Hourly rate")
    is_billable: bool = Field(True, description="Is this time billable")
    is_overtime: bool = Field(False, description="Is this overtime work")


class TimeLogCreate(TimeLogBase):
    """Schema for creating time log."""
    work_order_id: int = Field(..., description="Work order ID")
    start_time: datetime = Field(..., description="Start time")
    end_time: Optional[datetime] = Field(None, description="End time (if completed)")


class TimeLogUpdate(BaseModel):
    """Schema for updating time log."""
    end_time: Optional[datetime] = Field(None, description="End time")
    description: Optional[str] = None
    hourly_rate: Optional[Decimal] = Field(None, ge=0)
    is_billable: Optional[bool] = None
    is_overtime: Optional[bool] = None


class TimeLogResponse(TimeLogBase):
    """Schema for time log responses."""
    id: int
    work_order_id: int
    technician_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    cost: Optional[Decimal] = None
    
    # Audit
    created_at: datetime
    updated_at: datetime
    org_id: int
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v) if v else None
        }


# ===============================
# Summary and Statistics Schemas
# ===============================

class TicketSummary(BaseModel):
    """Summary statistics for tickets."""
    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    waiting_parts_tickets: int
    completed_tickets: int
    overdue_response: int
    overdue_resolution: int
    avg_response_time_hours: Optional[float]
    avg_resolution_time_hours: Optional[float]
    sla_response_compliance: Optional[float]  # Percentage
    sla_resolution_compliance: Optional[float]  # Percentage


class WorkOrderSummary(BaseModel):
    """Summary statistics for work orders."""
    total_work_orders: int
    draft_work_orders: int
    scheduled_work_orders: int
    in_progress_work_orders: int
    waiting_parts_work_orders: int
    completed_work_orders: int
    total_labor_cost: Optional[Decimal]
    total_parts_cost: Optional[Decimal]
    avg_completion_time_hours: Optional[float]


class SLAMetrics(BaseModel):
    """SLA performance metrics."""
    priority: TicketPriority
    target_response_hours: int
    target_resolution_hours: int
    actual_avg_response_hours: Optional[float]
    actual_avg_resolution_hours: Optional[float]
    response_compliance_rate: Optional[float]  # 0.0 - 1.0
    resolution_compliance_rate: Optional[float]  # 0.0 - 1.0
    total_tickets: int
    breached_response: int
    breached_resolution: int
    
    class Config:
        use_enum_values = True