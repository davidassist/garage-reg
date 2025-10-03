"""Pydantic schemas for maintenance planning API."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class MaintenancePlanBase(BaseModel):
    """Base maintenance plan schema."""
    
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    plan_code: str = Field(..., min_length=1, max_length=50)
    category: Optional[str] = Field(None, description="preventive, corrective, emergency, inspection")
    priority: str = Field("medium", description="low, medium, high, critical")
    
    # Applicability
    applies_to_gate_types: Optional[List[str]] = None
    applies_to_manufacturers: Optional[List[str]] = None
    applies_to_models: Optional[List[str]] = None
    applies_to_locations: Optional[List[int]] = None
    
    # Scheduling
    schedule_rrule: str = Field(..., description="RFC 5545 RRULE string")
    schedule_start_date: datetime
    schedule_end_date: Optional[datetime] = None
    schedule_timezone: str = Field("UTC")
    
    # Advanced scheduling
    lead_time_days: int = Field(7, ge=0, le=365)
    deadline_buffer_days: int = Field(3, ge=0, le=30)
    
    # Task details
    estimated_duration_minutes: Optional[int] = Field(None, ge=1)
    required_skills: Optional[List[str]] = None
    required_tools: Optional[List[str]] = None
    required_parts: Optional[List[str]] = None
    
    # Instructions
    instructions: Optional[str] = None
    checklist_template_id: Optional[int] = None
    safety_notes: Optional[str] = None
    
    # Notification settings
    notification_config: Optional[Dict[str, Any]] = Field(default_factory=lambda: {
        "email_enabled": True,
        "sms_enabled": False,
        "push_enabled": True,
        "notify_before_days": [7, 3, 1],
        "notify_overdue_days": [1, 3, 7],
        "escalation_enabled": False,
        "escalation_after_days": 14
    })
    
    # Assignment
    default_assignee_id: Optional[int] = None
    auto_assign: bool = False
    assignment_rules: Optional[Dict[str, Any]] = None
    
    # Status
    is_active: bool = True
    is_template: bool = False


class MaintenancePlanCreate(MaintenancePlanBase):
    """Schema for creating maintenance plan."""
    pass


class MaintenancePlanUpdate(BaseModel):
    """Schema for updating maintenance plan."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    
    applies_to_gate_types: Optional[List[str]] = None
    applies_to_manufacturers: Optional[List[str]] = None
    applies_to_models: Optional[List[str]] = None
    applies_to_locations: Optional[List[int]] = None
    
    schedule_rrule: Optional[str] = None
    schedule_start_date: Optional[datetime] = None
    schedule_end_date: Optional[datetime] = None
    schedule_timezone: Optional[str] = None
    
    lead_time_days: Optional[int] = Field(None, ge=0, le=365)
    deadline_buffer_days: Optional[int] = Field(None, ge=0, le=30)
    
    estimated_duration_minutes: Optional[int] = Field(None, ge=1)
    required_skills: Optional[List[str]] = None
    required_tools: Optional[List[str]] = None
    required_parts: Optional[List[str]] = None
    
    instructions: Optional[str] = None
    checklist_template_id: Optional[int] = None
    safety_notes: Optional[str] = None
    
    notification_config: Optional[Dict[str, Any]] = None
    
    default_assignee_id: Optional[int] = None
    auto_assign: Optional[bool] = None
    assignment_rules: Optional[Dict[str, Any]] = None
    
    is_active: Optional[bool] = None
    is_template: Optional[bool] = None


class MaintenancePlanResponse(MaintenancePlanBase):
    """Schema for maintenance plan response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    org_id: int
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int] = None
    
    # Computed fields
    next_occurrence: Optional[datetime] = None
    applicable_gates_count: Optional[int] = None
    scheduled_jobs_count: Optional[int] = None


class ScheduledJobBase(BaseModel):
    """Base scheduled job schema."""
    
    scheduled_date: datetime
    due_date: datetime
    assigned_to_id: Optional[int] = None
    status: str = Field("scheduled")
    priority_override: Optional[str] = None
    
    # Execution
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    actual_duration_minutes: Optional[int] = None
    
    # Results
    completion_notes: Optional[str] = None
    issues_found: Optional[List[Dict[str, Any]]] = None
    parts_used: Optional[List[Dict[str, Any]]] = None
    next_maintenance_date: Optional[datetime] = None


class ScheduledJobResponse(ScheduledJobBase):
    """Schema for scheduled job response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    org_id: int
    plan_id: int
    gate_id: int
    plan_occurrence_id: str
    created_at: datetime
    updated_at: datetime
    
    # Related data
    plan_name: Optional[str] = None
    gate_name: Optional[str] = None
    gate_code: Optional[str] = None
    gate_location: Optional[str] = None
    assignee_name: Optional[str] = None
    
    # Computed fields
    effective_priority: Optional[str] = None
    is_overdue: Optional[bool] = None
    days_until_due: Optional[int] = None


class JobCompletionData(BaseModel):
    """Schema for job completion data."""
    
    notes: Optional[str] = Field(None, max_length=2000)
    duration_minutes: Optional[int] = Field(None, ge=1)
    issues_found: Optional[List[Dict[str, Any]]] = None
    parts_used: Optional[List[Dict[str, Any]]] = None
    next_maintenance_date: Optional[datetime] = None


class CalendarSettingsBase(BaseModel):
    """Base calendar settings schema."""
    
    calendar_name: str = Field("Maintenance Schedule", max_length=200)
    include_assigned_jobs: bool = True
    include_team_jobs: bool = False
    include_all_org_jobs: bool = False
    
    # Filtering
    filter_categories: Optional[List[str]] = None
    filter_priorities: Optional[List[str]] = None
    filter_gate_types: Optional[List[str]] = None
    
    # Settings
    feed_enabled: bool = True
    timezone: str = "UTC"
    
    # Notifications
    email_notifications: bool = True
    sms_notifications: bool = False
    push_notifications: bool = True


class CalendarSettingsUpdate(CalendarSettingsBase):
    """Schema for updating calendar settings."""
    pass


class CalendarSettingsResponse(CalendarSettingsBase):
    """Schema for calendar settings response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    org_id: int
    ics_feed_token: str
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    feed_url: Optional[str] = None


class JobGenerationRequest(BaseModel):
    """Schema for job generation request."""
    
    days_ahead: int = Field(90, ge=7, le=365, description="Generate jobs for next N days")
    force_regenerate: bool = Field(False, description="Regenerate existing jobs")


class JobGenerationResponse(BaseModel):
    """Schema for job generation response."""
    
    jobs_created: int
    gates_processed: int
    occurrences_generated: int
    
    # Optional details
    plan_id: Optional[int] = None
    plan_name: Optional[str] = None
    error: Optional[str] = None


class MaintenanceStatsResponse(BaseModel):
    """Schema for maintenance statistics."""
    
    total_plans: int
    active_plans: int
    scheduled_jobs: int
    overdue_jobs: int
    completed_jobs_this_month: int
    
    # By category
    jobs_by_category: Dict[str, int]
    jobs_by_priority: Dict[str, int]
    jobs_by_status: Dict[str, int]
    
    # Upcoming
    jobs_due_today: int
    jobs_due_this_week: int
    jobs_due_next_week: int


class RRuleHelper(BaseModel):
    """Helper schema for RRULE generation."""
    
    frequency: str = Field(..., description="YEARLY, MONTHLY, WEEKLY, DAILY")
    interval: int = Field(1, ge=1, description="Every N intervals")
    count: Optional[int] = Field(None, ge=1, description="Number of occurrences")
    until: Optional[datetime] = Field(None, description="End date")
    
    # Weekly options
    byweekday: Optional[List[str]] = Field(None, description="MO,TU,WE,TH,FR,SA,SU")
    
    # Monthly options
    bymonthday: Optional[List[int]] = Field(None, description="Day of month (1-31)")
    bysetpos: Optional[List[int]] = Field(None, description="Nth occurrence (-1 for last)")
    
    # Yearly options
    bymonth: Optional[List[int]] = Field(None, description="Month (1-12)")
    byyearday: Optional[List[int]] = Field(None, description="Day of year (1-366)")


class NotificationLog(BaseModel):
    """Schema for notification log entry."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    job_id: int
    user_id: int
    notification_type: str
    channel: str
    subject: Optional[str] = None
    recipient_address: str
    sent_at: datetime
    delivery_status: str
    
    # User interaction
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None


class MaintenanceReportRequest(BaseModel):
    """Schema for maintenance report request."""
    
    start_date: datetime
    end_date: datetime
    include_categories: Optional[List[str]] = None
    include_priorities: Optional[List[str]] = None
    include_gate_types: Optional[List[str]] = None
    group_by: str = Field("month", description="day, week, month, quarter")


class MaintenanceReportResponse(BaseModel):
    """Schema for maintenance report response."""
    
    period_start: datetime
    period_end: datetime
    total_jobs: int
    completed_jobs: int
    overdue_jobs: int
    cancelled_jobs: int
    
    # Performance metrics
    avg_completion_time_minutes: Optional[float] = None
    completion_rate_percent: float
    on_time_completion_rate_percent: float
    
    # Breakdown data
    data_by_period: List[Dict[str, Any]]
    data_by_category: Dict[str, Any]
    data_by_priority: Dict[str, Any]
    data_by_gate_type: Dict[str, Any]
    
    # Top lists
    most_frequent_issues: List[Dict[str, Any]]
    most_used_parts: List[Dict[str, Any]]