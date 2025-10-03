"""Notification service for maintenance reminders and calendar feeds."""

import uuid
import smtplib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from icalendar import Calendar, Event, vText
from jinja2 import Template
import structlog

from app.models.maintenance_advanced import (
    AdvancedMaintenancePlan,
    ScheduledMaintenanceJob, 
    MaintenanceCalendar,
    MaintenanceNotification
)
from app.models.auth import User
from app.core.celery_app import celery_app, notification_task
from app.core.config import settings

logger = structlog.get_logger(__name__)


class NotificationService:
    """Service for sending maintenance notifications and generating calendar feeds."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def send_maintenance_reminder(
        self, 
        job_id: int, 
        notification_type: str = "reminder",
        channels: List[str] = None
    ) -> Dict[str, Any]:
        """Send maintenance reminder for a specific job."""
        job = self.db.query(ScheduledMaintenanceJob).filter(
            ScheduledMaintenanceJob.id == job_id
        ).first()
        
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        if channels is None:
            channels = ["email"]  # Default to email only
        
        results = {}
        
        # Get assignee or fallback users
        recipients = self._get_notification_recipients(job)
        
        for recipient in recipients:
            for channel in channels:
                try:
                    if channel == "email":
                        result = self._send_email_notification(job, recipient, notification_type)
                        results[f"{recipient.id}_{channel}"] = result
                    elif channel == "sms":
                        result = self._send_sms_notification(job, recipient, notification_type)
                        results[f"{recipient.id}_{channel}"] = result
                    elif channel == "push":
                        result = self._send_push_notification(job, recipient, notification_type)
                        results[f"{recipient.id}_{channel}"] = result
                        
                except Exception as e:
                    logger.error("Failed to send notification", 
                               job_id=job_id, 
                               recipient_id=recipient.id,
                               channel=channel,
                               error=str(e))
                    results[f"{recipient.id}_{channel}"] = {"error": str(e)}
        
        return {
            "job_id": job_id,
            "notification_type": notification_type,
            "recipients_count": len(recipients),
            "channels": channels,
            "results": results
        }
    
    def _get_notification_recipients(self, job: ScheduledMaintenanceJob) -> List[User]:
        """Get list of users who should receive notifications for a job."""
        recipients = []
        
        # Primary: assigned user
        if job.assigned_to:
            recipients.append(job.assigned_to)
        
        # Fallback: plan default assignee
        elif job.plan.default_assignee:
            recipients.append(job.plan.default_assignee)
        
        # Fallback: org admins
        if not recipients:
            from app.models.auth import Role
            admin_role = self.db.query(Role).filter(Role.name == "admin").first()
            if admin_role:
                admin_users = self.db.query(User).filter(
                    and_(
                        User.org_id == job.org_id,
                        User.role_id == admin_role.id,
                        User.is_active == True
                    )
                ).all()
                recipients.extend(admin_users)
        
        return recipients
    
    def _send_email_notification(
        self, 
        job: ScheduledMaintenanceJob, 
        recipient: User,
        notification_type: str
    ) -> Dict[str, Any]:
        """Send email notification using Mailhog (for testing) or SMTP."""
        
        # Generate email content
        subject, body = self._generate_email_content(job, recipient, notification_type)
        
        # Create email message
        msg = MIMEMultipart()
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = recipient.email
        msg["Subject"] = subject
        
        msg.attach(MIMEText(body, "html"))
        
        # Send email
        try:
            # Use Mailhog for development/testing
            smtp_server = settings.SMTP_HOST or "localhost"
            smtp_port = settings.SMTP_PORT or 1025  # Mailhog default port
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.starttls()
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                
                server.send_message(msg)
            
            # Log notification
            notification = MaintenanceNotification(
                org_id=job.org_id,
                job_id=job.id,
                user_id=recipient.id,
                notification_type=notification_type,
                channel="email",
                subject=subject,
                message=body,
                recipient_address=recipient.email,
                delivery_status="sent"
            )
            self.db.add(notification)
            self.db.commit()
            
            logger.info("Email notification sent",
                       job_id=job.id,
                       recipient_id=recipient.id,
                       notification_type=notification_type)
            
            return {"status": "sent", "recipient": recipient.email}
            
        except Exception as e:
            logger.error("Failed to send email", error=str(e))
            
            # Log failed notification
            notification = MaintenanceNotification(
                org_id=job.org_id,
                job_id=job.id,
                user_id=recipient.id,
                notification_type=notification_type,
                channel="email",
                subject=subject,
                message=body,
                recipient_address=recipient.email,
                delivery_status="failed",
                delivery_details={"error": str(e)}
            )
            self.db.add(notification)
            self.db.commit()
            
            return {"status": "failed", "error": str(e)}
    
    def _generate_email_content(
        self, 
        job: ScheduledMaintenanceJob, 
        recipient: User,
        notification_type: str
    ) -> tuple[str, str]:
        """Generate email subject and body for maintenance notification."""
        
        gate_name = job.gate.name if job.gate else "Unknown Gate"
        plan_name = job.plan.name if job.plan else "Unknown Plan"
        
        # Subject templates
        subject_templates = {
            "reminder": f"🔧 Maintenance Reminder: {plan_name} for {gate_name}",
            "overdue": f"⚠️ OVERDUE Maintenance: {plan_name} for {gate_name}",
            "escalation": f"🚨 URGENT: Overdue Maintenance Escalation - {gate_name}",
            "completion": f"✅ Maintenance Completed: {plan_name} for {gate_name}"
        }
        
        subject = subject_templates.get(notification_type, f"Maintenance Notification: {gate_name}")
        
        # Body template
        body_template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
                .header { border-bottom: 2px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }
                .title { color: #007bff; margin: 0; font-size: 24px; }
                .badge { display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: bold; text-transform: uppercase; }
                .badge-reminder { background: #e3f2fd; color: #1976d2; }
                .badge-overdue { background: #ffebee; color: #d32f2f; }
                .badge-urgent { background: #f3e5f5; color: #7b1fa2; }
                .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }
                .info-item { padding: 15px; background: #f8f9fa; border-radius: 4px; }
                .info-label { font-weight: bold; color: #666; margin-bottom: 5px; }
                .info-value { color: #333; }
                .actions { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }
                .btn { display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; margin-right: 10px; }
                .btn-secondary { background: #6c757d; }
                .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 class="title">GarageReg Maintenance System</h1>
                    <span class="badge badge-{{ badge_class }}">{{ notification_type.upper() }}</span>
                </div>
                
                <h2>{{ subject }}</h2>
                
                <p>Hello {{ recipient_name }},</p>
                
                <p>{{ main_message }}</p>
                
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">Gate Information</div>
                        <div class="info-value">
                            <strong>{{ gate_name }}</strong><br>
                            {% if gate_code %}Code: {{ gate_code }}<br>{% endif %}
                            {% if gate_location %}Location: {{ gate_location }}<br>{% endif %}
                            Type: {{ gate_type }}
                        </div>
                    </div>
                    
                    <div class="info-item">
                        <div class="info-label">Maintenance Details</div>
                        <div class="info-value">
                            <strong>{{ plan_name }}</strong><br>
                            Scheduled: {{ scheduled_date }}<br>
                            Due: {{ due_date }}<br>
                            Priority: {{ priority }}
                        </div>
                    </div>
                </div>
                
                {% if instructions %}
                <div class="info-item">
                    <div class="info-label">Instructions</div>
                    <div class="info-value">{{ instructions }}</div>
                </div>
                {% endif %}
                
                <div class="actions">
                    <a href="{{ view_job_url }}" class="btn">View Job Details</a>
                    <a href="{{ mark_complete_url }}" class="btn btn-secondary">Mark as Complete</a>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from GarageReg Maintenance System.</p>
                    <p>If you have questions, please contact your system administrator.</p>
                </div>
            </div>
        </body>
        </html>
        """)
        
        # Prepare template variables
        badge_class = {
            "reminder": "reminder",
            "overdue": "overdue", 
            "escalation": "urgent",
            "completion": "reminder"
        }.get(notification_type, "reminder")
        
        main_messages = {
            "reminder": f"This is a reminder that maintenance is scheduled for {gate_name}.",
            "overdue": f"⚠️ The maintenance for {gate_name} is now overdue. Please complete as soon as possible.",
            "escalation": f"🚨 The maintenance for {gate_name} has been overdue for several days and requires immediate attention.",
            "completion": f"✅ The maintenance for {gate_name} has been completed successfully."
        }
        
        # Build location string
        gate_location = ""
        if job.gate and hasattr(job.gate, 'building') and job.gate.building:
            building_name = job.gate.building.name
            if hasattr(job.gate.building, 'site') and job.gate.building.site:
                gate_location = f"{job.gate.building.site.name} - {building_name}"
            else:
                gate_location = building_name
        
        template_vars = {
            "subject": subject,
            "notification_type": notification_type,
            "badge_class": badge_class,
            "recipient_name": recipient.first_name or recipient.username,
            "main_message": main_messages.get(notification_type, "Maintenance notification"),
            "gate_name": gate_name,
            "gate_code": job.gate.gate_code if job.gate else "",
            "gate_location": gate_location,
            "gate_type": job.gate.gate_type if job.gate else "Unknown",
            "plan_name": plan_name,
            "scheduled_date": job.scheduled_date.strftime("%Y-%m-%d %H:%M"),
            "due_date": job.due_date.strftime("%Y-%m-%d %H:%M"),
            "priority": job.effective_priority.title(),
            "instructions": job.plan.instructions if job.plan else "",
            "view_job_url": f"{settings.FRONTEND_URL}/maintenance/jobs/{job.id}",
            "mark_complete_url": f"{settings.FRONTEND_URL}/maintenance/jobs/{job.id}/complete"
        }
        
        body = body_template.render(**template_vars)
        
        return subject, body
    
    def _send_sms_notification(
        self, 
        job: ScheduledMaintenanceJob, 
        recipient: User,
        notification_type: str
    ) -> Dict[str, Any]:
        """Send SMS notification (placeholder - integrate with SMS provider)."""
        # Placeholder for SMS integration
        logger.info("SMS notification would be sent", 
                   job_id=job.id, 
                   recipient_id=recipient.id)
        
        return {"status": "not_implemented", "message": "SMS notifications not yet implemented"}
    
    def _send_push_notification(
        self, 
        job: ScheduledMaintenanceJob, 
        recipient: User,
        notification_type: str
    ) -> Dict[str, Any]:
        """Send push notification (placeholder - integrate with push service)."""
        # Placeholder for push notification integration
        logger.info("Push notification would be sent", 
                   job_id=job.id, 
                   recipient_id=recipient.id)
        
        return {"status": "not_implemented", "message": "Push notifications not yet implemented"}
    
    def generate_calendar_feed(self, user_id: int, token: Optional[str] = None) -> str:
        """Generate ICS calendar feed for user's maintenance schedule."""
        
        # Get user's calendar settings
        calendar_settings = self.db.query(MaintenanceCalendar).filter(
            MaintenanceCalendar.user_id == user_id
        ).first()
        
        if not calendar_settings:
            raise ValueError(f"No calendar settings found for user {user_id}")
        
        if token and calendar_settings.ics_feed_token != token:
            raise ValueError("Invalid calendar feed token")
        
        # Create calendar
        cal = Calendar()
        cal.add('prodid', '-//GarageReg//Maintenance Calendar//EN')
        cal.add('version', '2.0')
        cal.add('calscale', 'GREGORIAN')
        cal.add('method', 'PUBLISH')
        cal.add('x-wr-calname', calendar_settings.calendar_name)
        cal.add('x-wr-caldesc', 'Maintenance schedule from GarageReg')
        
        # Get jobs based on calendar settings
        jobs = self._get_calendar_jobs(calendar_settings)
        
        # Add events
        for job in jobs:
            event = Event()
            
            # Basic event info
            event.add('uid', f'maintenance-{job.id}@garagereg.com')
            event.add('dtstart', job.scheduled_date)
            event.add('dtend', job.scheduled_date + timedelta(hours=2))  # Default 2 hour duration
            event.add('dtstamp', datetime.utcnow())
            
            # Event details
            summary = f"{job.plan.name} - {job.gate.name}"
            event.add('summary', summary)
            
            # Description with details
            description_parts = [
                f"Maintenance: {job.plan.name}",
                f"Gate: {job.gate.name} ({job.gate.gate_code or 'No code'})",
                f"Type: {job.gate.gate_type}",
                f"Priority: {job.effective_priority.title()}",
                f"Status: {job.status.title()}"
            ]
            
            if job.plan.instructions:
                description_parts.append(f"Instructions: {job.plan.instructions}")
            
            if job.assigned_to:
                description_parts.append(f"Assigned to: {job.assigned_to.first_name} {job.assigned_to.last_name}")
            
            event.add('description', '\\n'.join(description_parts))
            
            # Location
            if job.gate and hasattr(job.gate, 'building'):
                location_parts = []
                if hasattr(job.gate.building, 'site') and job.gate.building.site:
                    location_parts.append(job.gate.building.site.name)
                location_parts.append(job.gate.building.name)
                location_parts.append(f"Gate: {job.gate.name}")
                event.add('location', ', '.join(location_parts))
            
            # Categories and priority
            event.add('categories', [job.plan.category or 'maintenance'])
            
            priority_map = {
                'low': 9,
                'medium': 5, 
                'high': 3,
                'critical': 1
            }
            event.add('priority', priority_map.get(job.effective_priority, 5))
            
            # Status
            status_map = {
                'scheduled': 'TENTATIVE',
                'notified': 'CONFIRMED',
                'in_progress': 'CONFIRMED',
                'completed': 'CONFIRMED',
                'cancelled': 'CANCELLED',
                'overdue': 'CONFIRMED'
            }
            event.add('status', status_map.get(job.status, 'TENTATIVE'))
            
            # Alarms for reminders
            if job.status in ['scheduled', 'notified'] and job.plan.notification_config:
                notify_days = job.plan.notification_config.get('notify_before_days', [1])
                for days in notify_days:
                    from icalendar import Alarm
                    alarm = Alarm()
                    alarm.add('action', 'DISPLAY')
                    alarm.add('description', f'Maintenance reminder: {summary}')
                    alarm.add('trigger', timedelta(days=-days))
                    event.add_component(alarm)
            
            cal.add_component(event)
        
        return cal.to_ical().decode('utf-8')
    
    def _get_calendar_jobs(self, calendar_settings: MaintenanceCalendar) -> List[ScheduledMaintenanceJob]:
        """Get maintenance jobs for calendar based on user settings."""
        
        # Base query for user's organization
        query = self.db.query(ScheduledMaintenanceJob).filter(
            ScheduledMaintenanceJob.org_id == calendar_settings.org_id
        )
        
        # Apply user-specific filters
        if calendar_settings.include_assigned_jobs and not calendar_settings.include_all_org_jobs:
            # Only assigned jobs
            query = query.filter(
                ScheduledMaintenanceJob.assigned_to_id == calendar_settings.user_id
            )
        elif not calendar_settings.include_all_org_jobs:
            # No jobs if not assigned and not all org jobs
            return []
        
        # Filter by categories
        if calendar_settings.filter_categories:
            query = query.join(AdvancedMaintenancePlan).filter(
                AdvancedMaintenancePlan.category.in_(calendar_settings.filter_categories)
            )
        
        # Filter by priorities  
        if calendar_settings.filter_priorities:
            query = query.join(AdvancedMaintenancePlan).filter(
                AdvancedMaintenancePlan.priority.in_(calendar_settings.filter_priorities)
            )
        
        # Filter by gate types
        if calendar_settings.filter_gate_types:
            from app.models.organization import Gate
            query = query.join(Gate).filter(
                Gate.gate_type.in_(calendar_settings.filter_gate_types)
            )
        
        # Only include future and recent jobs (last 30 days, next 365 days)
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow() + timedelta(days=365)
        
        query = query.filter(
            and_(
                ScheduledMaintenanceJob.scheduled_date >= start_date,
                ScheduledMaintenanceJob.scheduled_date <= end_date
            )
        )
        
        return query.order_by(ScheduledMaintenanceJob.scheduled_date).all()


# Celery tasks
@notification_task(name="notification.send_daily_reminders")
def send_daily_reminders(self):
    """Send daily maintenance reminders."""
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        notification_service = NotificationService(db)
        
        # Get jobs that need reminders today
        tomorrow = datetime.utcnow() + timedelta(days=1)
        next_week = datetime.utcnow() + timedelta(days=7)
        
        jobs_needing_reminders = db.query(ScheduledMaintenanceJob).filter(
            and_(
                ScheduledMaintenanceJob.status.in_(["scheduled", "notified"]),
                or_(
                    ScheduledMaintenanceJob.scheduled_date.between(
                        datetime.utcnow(), tomorrow
                    ),
                    ScheduledMaintenanceJob.scheduled_date.between(
                        datetime.utcnow() + timedelta(days=6), next_week
                    )
                )
            )
        ).all()
        
        results = []
        
        for job in jobs_needing_reminders:
            try:
                result = notification_service.send_maintenance_reminder(
                    job.id, 
                    "reminder", 
                    ["email"]
                )
                results.append(result)
            except Exception as e:
                logger.error("Failed to send reminder", job_id=job.id, error=str(e))
        
        return {
            "reminders_sent": len(results),
            "jobs_processed": len(jobs_needing_reminders)
        }
        
    finally:
        db.close()


@notification_task(name="notification.send_overdue_notifications")
def send_overdue_notifications(self):
    """Send overdue maintenance notifications."""
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        notification_service = NotificationService(db)
        
        # Get overdue jobs
        overdue_jobs = db.query(ScheduledMaintenanceJob).filter(
            and_(
                ScheduledMaintenanceJob.status == "overdue",
                ScheduledMaintenanceJob.due_date < datetime.utcnow()
            )
        ).all()
        
        results = []
        
        for job in overdue_jobs:
            try:
                result = notification_service.send_maintenance_reminder(
                    job.id,
                    "overdue", 
                    ["email"]
                )
                results.append(result)
            except Exception as e:
                logger.error("Failed to send overdue notification", job_id=job.id, error=str(e))
        
        return {
            "overdue_notifications_sent": len(results),
            "overdue_jobs_processed": len(overdue_jobs)
        }
        
    finally:
        db.close()


@notification_task(name="notification.update_all_calendar_feeds")
def update_all_calendar_feeds(self):
    """Update all user calendar feeds (cache refresh)."""
    # This is a placeholder for cache invalidation
    # In a real implementation, you might update Redis cache here
    logger.info("Calendar feeds cache refresh triggered")
    return {"status": "completed"}


@notification_task(name="notification.send_maintenance_reminder")
def send_maintenance_reminder_task(self, job_id: int, notification_type: str = "reminder"):
    """Celery task to send individual maintenance reminder."""
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        notification_service = NotificationService(db)
        return notification_service.send_maintenance_reminder(job_id, notification_type)
    finally:
        db.close()