"""Maintenance scheduling and execution models."""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Numeric, Index
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from app.models import TenantModel


class MaintenancePlan(TenantModel):
    """
    Maintenance Plans - scheduled maintenance templates.
    
    Karbantartási tervek (ütemezett karbantartási sablonok)
    """
    __tablename__ = "maintenance_plans"
    
    # Plan identification
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    plan_type = Column(String(50), nullable=False, index=True)  # 'preventive', 'predictive', 'corrective'
    
    # Scope and applicability
    applies_to_gate_types = Column(JSONB, nullable=True)  # Array of gate types
    applies_to_manufacturers = Column(JSONB, nullable=True)  # Array of manufacturers
    applies_to_components = Column(JSONB, nullable=True)  # Array of component types
    
    # Schedule information
    frequency_type = Column(String(20), nullable=False)  # 'days', 'weeks', 'months', 'cycles', 'hours'
    frequency_value = Column(Integer, nullable=False)  # Number of units
    season_dependent = Column(Boolean, default=False, nullable=False)
    preferred_months = Column(JSONB, nullable=True)  # Array of month numbers (1-12)
    
    # Time and resource requirements
    estimated_duration_hours = Column(Numeric(5, 2), nullable=True)
    required_technicians = Column(Integer, default=1, nullable=False)
    required_skills = Column(JSONB, nullable=True)  # Array of required skills
    required_tools = Column(JSONB, nullable=True)  # Array of required tools
    required_parts = Column(JSONB, nullable=True)  # Array of parts that might be needed
    
    # Cost estimates
    estimated_labor_cost = Column(Numeric(10, 2), nullable=True)
    estimated_parts_cost = Column(Numeric(10, 2), nullable=True)
    estimated_total_cost = Column(Numeric(10, 2), nullable=True)
    
    # Conditions and requirements
    weather_requirements = Column(String(200), nullable=True)
    temperature_min = Column(Integer, nullable=True)
    temperature_max = Column(Integer, nullable=True)
    advance_notice_days = Column(Integer, default=7, nullable=False)
    
    # Priority and classification
    priority = Column(String(20), default='medium', nullable=False)  # 'low', 'medium', 'high', 'critical'
    safety_category = Column(String(20), default='standard', nullable=False)  # 'standard', 'safety_critical'
    regulatory_required = Column(Boolean, default=False, nullable=False)
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSONB, nullable=True, default=lambda: {})
    
    # Relationships
    maintenance_jobs = relationship("MaintenanceJob", back_populates="maintenance_plan")
    
    # Indexes
    __table_args__ = (
        Index("idx_maintenance_plan_name", "name"),
        Index("idx_maintenance_plan_type", "plan_type"),
        Index("idx_maintenance_plan_frequency", "frequency_type", "frequency_value"),
        Index("idx_maintenance_plan_priority", "priority"),
        Index("idx_maintenance_plan_active", "is_active"),
        Index("idx_maintenance_plan_regulatory", "regulatory_required"),
    )
    
    @validates("plan_type")
    def validate_plan_type(self, key, value):
        valid_types = ['preventive', 'predictive', 'corrective', 'emergency']
        if value not in valid_types:
            raise ValueError(f"Plan type must be one of: {valid_types}")
        return value
    
    @validates("frequency_type")
    def validate_frequency_type(self, key, value):
        valid_types = ['days', 'weeks', 'months', 'cycles', 'hours', 'years']
        if value not in valid_types:
            raise ValueError(f"Frequency type must be one of: {valid_types}")
        return value
    
    @validates("priority")
    def validate_priority(self, key, value):
        valid_priorities = ['low', 'medium', 'high', 'critical']
        if value not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}")
        return value


class MaintenanceJob(TenantModel):
    """
    Maintenance Jobs - generated or scheduled maintenance tasks.
    
    Karbantartási feladatok (generált vagy ütemezett feladatok)
    """
    __tablename__ = "maintenance_jobs"
    
    # References
    gate_id = Column(Integer, ForeignKey("gates.id"), nullable=False, index=True)
    maintenance_plan_id = Column(Integer, ForeignKey("maintenance_plans.id"), nullable=True, index=True)
    
    # Job identification
    job_number = Column(String(50), nullable=False, unique=True, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    job_type = Column(String(50), nullable=False, index=True)  # 'preventive', 'predictive', 'corrective', 'emergency'
    
    # Scheduling
    scheduled_date = Column(DateTime, nullable=False, index=True)
    due_date = Column(DateTime, nullable=True, index=True)
    earliest_start_date = Column(DateTime, nullable=True)
    latest_completion_date = Column(DateTime, nullable=True)
    
    # Assignment and resources
    assigned_technician_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    assigned_team_id = Column(Integer, nullable=True)  # Future: team assignment
    estimated_duration_hours = Column(Numeric(5, 2), nullable=True)
    required_skills = Column(JSONB, nullable=True)
    
    # Status and progress
    status = Column(String(50), default='scheduled', nullable=False, index=True)  # 'scheduled', 'assigned', 'in_progress', 'completed', 'cancelled', 'postponed'
    progress_percentage = Column(Integer, default=0, nullable=False)
    
    # Execution tracking
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    actual_duration_hours = Column(Numeric(5, 2), nullable=True)
    
    # Results and outcomes
    completion_notes = Column(Text, nullable=True)
    issues_found = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    followup_required = Column(Boolean, default=False, nullable=False)
    next_maintenance_date = Column(DateTime, nullable=True)
    
    # Cost tracking
    estimated_cost = Column(Numeric(10, 2), nullable=True)
    actual_labor_cost = Column(Numeric(10, 2), nullable=True)
    actual_parts_cost = Column(Numeric(10, 2), nullable=True)
    actual_total_cost = Column(Numeric(10, 2), nullable=True)
    
    # Quality and safety
    quality_rating = Column(Integer, nullable=True)  # 1-5 rating
    safety_incidents = Column(Text, nullable=True)
    customer_satisfaction = Column(Integer, nullable=True)  # 1-5 rating
    
    # Priority and urgency
    priority = Column(String(20), default='medium', nullable=False)
    urgency = Column(String(20), default='normal', nullable=False)  # 'low', 'normal', 'high', 'emergency'
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSONB, nullable=True, default=lambda: {})
    
    # Relationships
    gate = relationship("Gate", back_populates="maintenance_jobs")
    maintenance_plan = relationship("MaintenancePlan", back_populates="maintenance_jobs")
    assigned_technician = relationship("User", back_populates="assigned_maintenance_jobs")
    work_orders = relationship("WorkOrder", back_populates="maintenance_job")
    reminders = relationship("Reminder", back_populates="maintenance_job")
    
    # Indexes
    __table_args__ = (
        Index("idx_maintenance_job_gate", "gate_id"),
        Index("idx_maintenance_job_plan", "maintenance_plan_id"),
        Index("idx_maintenance_job_number", "job_number"),
        Index("idx_maintenance_job_type", "job_type"),
        Index("idx_maintenance_job_status", "status"),
        Index("idx_maintenance_job_scheduled", "scheduled_date"),
        Index("idx_maintenance_job_due", "due_date"),
        Index("idx_maintenance_job_assigned", "assigned_technician_id"),
        Index("idx_maintenance_job_priority", "priority"),
        Index("idx_maintenance_job_urgency", "urgency"),
    )
    
    @validates("status")
    def validate_status(self, key, value):
        valid_statuses = ['scheduled', 'assigned', 'in_progress', 'completed', 'cancelled', 'postponed', 'on_hold']
        if value not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        return value
    
    @validates("job_type")
    def validate_job_type(self, key, value):
        valid_types = ['preventive', 'predictive', 'corrective', 'emergency', 'installation', 'inspection']
        if value not in valid_types:
            raise ValueError(f"Job type must be one of: {valid_types}")
        return value
    
    @property
    def is_overdue(self) -> bool:
        """Check if maintenance job is overdue."""
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return datetime.utcnow() > self.due_date
        return False
    
    @property
    def days_until_due(self) -> Optional[int]:
        """Calculate days until due date."""
        if self.due_date:
            delta = self.due_date - datetime.utcnow()
            return delta.days
        return None


class Reminder(TenantModel):
    """
    Reminders - automated or manual reminders for maintenance.
    
    Emlékeztetők (automatikus vagy kézi emlékeztetők)
    """
    __tablename__ = "reminders"
    
    # References
    gate_id = Column(Integer, ForeignKey("gates.id"), nullable=True, index=True)
    maintenance_job_id = Column(Integer, ForeignKey("maintenance_jobs.id"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Reminder information
    title = Column(String(300), nullable=False)
    message = Column(Text, nullable=False)
    reminder_type = Column(String(50), nullable=False, index=True)  # 'maintenance_due', 'inspection_due', 'warranty_expiring', 'custom'
    
    # Scheduling
    scheduled_for = Column(DateTime, nullable=False, index=True)
    repeat_interval_days = Column(Integer, nullable=True)
    repeat_count = Column(Integer, default=1, nullable=False)
    times_sent = Column(Integer, default=0, nullable=False)
    
    # Delivery methods
    send_email = Column(Boolean, default=True, nullable=False)
    send_sms = Column(Boolean, default=False, nullable=False)
    send_push = Column(Boolean, default=False, nullable=False)
    send_in_app = Column(Boolean, default=True, nullable=False)
    
    # Recipients
    recipient_emails = Column(JSONB, nullable=True)  # Array of email addresses
    recipient_phones = Column(JSONB, nullable=True)  # Array of phone numbers
    
    # Status tracking
    status = Column(String(50), default='pending', nullable=False, index=True)  # 'pending', 'sent', 'delivered', 'failed', 'cancelled'
    last_sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String(200), nullable=True)
    
    # Priority and urgency
    priority = Column(String(20), default='normal', nullable=False)
    urgency = Column(String(20), default='normal', nullable=False)
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSONB, nullable=True, default=lambda: {})
    
    # Relationships
    gate = relationship("Gate")
    maintenance_job = relationship("MaintenanceJob", back_populates="reminders")
    user = relationship("User", back_populates="reminders")
    
    # Indexes
    __table_args__ = (
        Index("idx_reminder_gate", "gate_id"),
        Index("idx_reminder_job", "maintenance_job_id"),
        Index("idx_reminder_user", "user_id"),
        Index("idx_reminder_type", "reminder_type"),
        Index("idx_reminder_scheduled", "scheduled_for"),
        Index("idx_reminder_status", "status"),
        Index("idx_reminder_priority", "priority"),
    )
    
    @validates("reminder_type")
    def validate_reminder_type(self, key, value):
        valid_types = ['maintenance_due', 'inspection_due', 'warranty_expiring', 'component_replacement', 'custom', 'overdue']
        if value not in valid_types:
            raise ValueError(f"Reminder type must be one of: {valid_types}")
        return value
    
    @validates("status")
    def validate_status(self, key, value):
        valid_statuses = ['pending', 'sent', 'delivered', 'failed', 'cancelled', 'acknowledged']
        if value not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        return value
    
    @property
    def is_overdue_to_send(self) -> bool:
        """Check if reminder is overdue to be sent."""
        return datetime.utcnow() > self.scheduled_for and self.status == 'pending'
    
    @property
    def should_repeat(self) -> bool:
        """Check if reminder should be repeated."""
        return (
            self.repeat_interval_days and 
            self.times_sent < self.repeat_count and
            self.status in ['sent', 'delivered']
        )