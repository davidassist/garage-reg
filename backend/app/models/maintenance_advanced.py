"""Maintenance planning and scheduling models with RRULE support."""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY

from app.models import Base


class AdvancedMaintenancePlan(Base):
    """
    Maintenance plan with RRULE-based scheduling.
    Supports yearly, half-yearly, quarterly recurring maintenance.
    """
    __tablename__ = "advanced_maintenance_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Plan identification
    name = Column(String(200), nullable=False)
    description = Column(Text)
    plan_code = Column(String(50), unique=True, nullable=False)
    category = Column(String(100))  # preventive, corrective, emergency, inspection
    priority = Column(String(50), default="medium")  # low, medium, high, critical
    
    # Applicability
    applies_to_gate_types = Column(JSON)  # Array of gate types
    applies_to_manufacturers = Column(JSON)  # Array of manufacturers
    applies_to_models = Column(JSON)  # Array of specific models
    applies_to_locations = Column(JSON)  # Array of location IDs
    
    # Scheduling (RRULE-based)
    schedule_rrule = Column(Text, nullable=False)  # RFC 5545 RRULE string
    schedule_start_date = Column(DateTime, nullable=False)
    schedule_end_date = Column(DateTime)  # Optional end date
    schedule_timezone = Column(String(50), default="UTC")
    
    # Advanced scheduling
    lead_time_days = Column(Integer, default=7)  # How many days before to create job
    deadline_buffer_days = Column(Integer, default=3)  # Grace period after due date
    
    # Task details
    estimated_duration_minutes = Column(Integer)
    required_skills = Column(JSON)  # Array of required skills/certifications
    required_tools = Column(JSON)  # Array of required tools
    required_parts = Column(JSON)  # Array of potentially needed parts
    
    # Instructions
    instructions = Column(Text)
    checklist_template_id = Column(Integer, ForeignKey("checklist_templates.id"))
    safety_notes = Column(Text)
    
    # Notification settings
    notification_config = Column(JSON, default=lambda: {
        "email_enabled": True,
        "sms_enabled": False,
        "push_enabled": True,
        "notify_before_days": [7, 3, 1],  # Notify 7, 3, and 1 days before
        "notify_overdue_days": [1, 3, 7],  # Notify 1, 3, 7 days after overdue
        "escalation_enabled": False,
        "escalation_after_days": 14
    })
    
    # Assignment
    default_assignee_id = Column(Integer, ForeignKey("users.id"))
    auto_assign = Column(Boolean, default=False)
    assignment_rules = Column(JSON)  # Rules for automatic assignment
    
    # Status and control
    is_active = Column(Boolean, default=True)
    is_template = Column(Boolean, default=False)  # Template plans for copying
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    organization = relationship("Organization", back_populates="maintenance_plans")
    checklist_template = relationship("ChecklistTemplate")
    default_assignee = relationship("User", foreign_keys=[default_assignee_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
    scheduled_jobs = relationship("ScheduledMaintenanceJob", back_populates="plan")
    
    def get_next_occurrences(self, count: int = 10, from_date: Optional[datetime] = None) -> List[datetime]:
        """Get next scheduled occurrences using RRULE."""
        try:
            from dateutil.rrule import rrulestr
            
            if from_date is None:
                from_date = datetime.utcnow()
            
            # Parse the RRULE string
            rule = rrulestr(self.schedule_rrule, dtstart=self.schedule_start_date)
            
            # Get occurrences after from_date
            occurrences = []
            for occurrence in rule:
                if occurrence >= from_date:
                    occurrences.append(occurrence)
                    if len(occurrences) >= count:
                        break
                # Stop if we've passed end date
                if self.schedule_end_date and occurrence > self.schedule_end_date:
                    break
            
            return occurrences
            
        except Exception as e:
            # Fallback: return empty list if RRULE parsing fails
            return []
    
    def is_applicable_to_gate(self, gate) -> bool:
        """Check if this plan applies to a specific gate."""
        # Check gate type
        if self.applies_to_gate_types:
            if gate.gate_type not in self.applies_to_gate_types:
                return False
        
        # Check manufacturer
        if self.applies_to_manufacturers and gate.manufacturer:
            if gate.manufacturer not in self.applies_to_manufacturers:
                return False
        
        # Check model
        if self.applies_to_models and gate.model:
            if gate.model not in self.applies_to_models:
                return False
        
        # Check location (building/site)
        if self.applies_to_locations:
            gate_locations = [gate.building_id]
            if hasattr(gate.building, 'site_id'):
                gate_locations.append(gate.building.site_id)
            if not any(loc in self.applies_to_locations for loc in gate_locations):
                return False
        
        return True


class ScheduledMaintenanceJob(Base):
    """
    Individual scheduled maintenance job generated from maintenance plans.
    """
    __tablename__ = "advanced_scheduled_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Source plan
    plan_id = Column(Integer, ForeignKey("advanced_maintenance_plans.id"), nullable=False)
    plan_occurrence_id = Column(String(100))  # Unique ID for this occurrence
    
    # Target
    gate_id = Column(Integer, ForeignKey("gates.id"), nullable=False)
    
    # Scheduling
    scheduled_date = Column(DateTime, nullable=False, index=True)
    due_date = Column(DateTime, nullable=False, index=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    
    # Assignment
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    assigned_at = Column(DateTime)
    
    # Status tracking
    status = Column(String(50), default="scheduled", index=True)
    # scheduled, notified, in_progress, completed, cancelled, overdue
    
    # Execution tracking
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    actual_duration_minutes = Column(Integer)
    
    # Results
    completion_notes = Column(Text)
    issues_found = Column(JSON)  # Array of issues discovered
    parts_used = Column(JSON)  # Array of parts actually used
    next_maintenance_date = Column(DateTime)  # Suggested next maintenance
    
    # Notifications
    notifications_sent = Column(JSON, default=lambda: {
        "reminders": [],  # List of reminder notification timestamps
        "overdue": [],    # List of overdue notification timestamps
        "escalations": [] # List of escalation timestamps
    })
    
    # Priority override
    priority_override = Column(String(50))  # Can override plan priority
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization")
    plan = relationship("MaintenancePlan", back_populates="scheduled_jobs")
    gate = relationship("Gate")
    assigned_to = relationship("User")
    
    @property
    def effective_priority(self) -> str:
        """Get the effective priority (override or plan priority)."""
        return self.priority_override or self.plan.priority
    
    @property
    def is_overdue(self) -> bool:
        """Check if job is overdue."""
        return (self.status in ['scheduled', 'notified', 'in_progress'] and 
                datetime.utcnow() > self.due_date)
    
    @property
    def days_until_due(self) -> int:
        """Get days until due date (negative if overdue)."""
        delta = self.due_date - datetime.utcnow()
        return delta.days


class MaintenanceCalendar(Base):
    """
    User-specific maintenance calendar settings for ICS feed generation.
    """
    __tablename__ = "advanced_maintenance_calendars"
    
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Calendar settings
    calendar_name = Column(String(200), default="Maintenance Schedule")
    include_assigned_jobs = Column(Boolean, default=True)
    include_team_jobs = Column(Boolean, default=False)
    include_all_org_jobs = Column(Boolean, default=False)
    
    # Filtering
    filter_categories = Column(JSON)  # Only include specific categories
    filter_priorities = Column(JSON)  # Only include specific priorities
    filter_gate_types = Column(JSON)  # Only include specific gate types
    
    # ICS feed settings
    ics_feed_token = Column(String(64), unique=True)  # Secret token for feed access
    feed_enabled = Column(Boolean, default=True)
    timezone = Column(String(50), default="UTC")
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    push_notifications = Column(Boolean, default=True)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization")
    user = relationship("User")


class MaintenanceNotification(Base):
    """
    Maintenance notification log for tracking sent notifications.
    """
    __tablename__ = "advanced_maintenance_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Source
    job_id = Column(Integer, ForeignKey("advanced_scheduled_jobs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Notification details
    notification_type = Column(String(50), nullable=False)  # reminder, overdue, escalation, completion
    channel = Column(String(50), nullable=False)  # email, sms, push
    
    # Content
    subject = Column(String(500))
    message = Column(Text)
    recipient_address = Column(String(320))  # email or phone
    
    # Delivery tracking
    sent_at = Column(DateTime, default=datetime.utcnow)
    delivery_status = Column(String(50), default="sent")  # sent, delivered, failed, bounced
    delivery_details = Column(JSON)  # Provider-specific delivery info
    
    # User interaction
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)
    
    # Relationships
    job = relationship("ScheduledMaintenanceJob")
    user = relationship("User")
    organization = relationship("Organization")