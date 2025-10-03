"""Celery configuration for maintenance job scheduling."""

import os
from datetime import timedelta
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "garagereg_maintenance",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.services.maintenance_scheduler",
        "app.services.notification_service",
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_backend_transport_options={
        "retry_policy": {
            "timeout": 5.0
        }
    },
    
    # Task routing
    task_routes={
        "app.services.maintenance_scheduler.generate_scheduled_jobs": {"queue": "maintenance"},
        "app.services.maintenance_scheduler.check_overdue_jobs": {"queue": "maintenance"},
        "app.services.notification_service.send_maintenance_reminder": {"queue": "notifications"},
        "app.services.notification_service.send_overdue_notification": {"queue": "notifications"},
        "app.services.notification_service.generate_calendar_feed": {"queue": "calendar"},
    },
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Beat settings (scheduler)
    beat_schedule={
        # Generate maintenance jobs every hour
        "generate-maintenance-jobs": {
            "task": "app.services.maintenance_scheduler.generate_scheduled_jobs",
            "schedule": timedelta(hours=1),
            "options": {"queue": "maintenance"}
        },
        
        # Check for overdue jobs every 30 minutes
        "check-overdue-jobs": {
            "task": "app.services.maintenance_scheduler.check_overdue_jobs", 
            "schedule": timedelta(minutes=30),
            "options": {"queue": "maintenance"}
        },
        
        # Send daily reminders at 9 AM
        "send-daily-reminders": {
            "task": "app.services.notification_service.send_daily_reminders",
            "schedule": crontab(hour=9, minute=0),
            "options": {"queue": "notifications"}
        },
        
        # Send overdue notifications at 10 AM and 3 PM
        "send-overdue-notifications": {
            "task": "app.services.notification_service.send_overdue_notifications",
            "schedule": crontab(hour=[10, 15], minute=0),
            "options": {"queue": "notifications"}
        },
        
        # Update calendar feeds every 4 hours
        "update-calendar-feeds": {
            "task": "app.services.notification_service.update_all_calendar_feeds",
            "schedule": timedelta(hours=4),
            "options": {"queue": "calendar"}
        },
        
        # Cleanup old notifications weekly
        "cleanup-old-notifications": {
            "task": "app.services.maintenance_scheduler.cleanup_old_data",
            "schedule": crontab(day_of_week=0, hour=2, minute=0),  # Sunday 2 AM
            "options": {"queue": "maintenance"}
        }
    },
    
    # Error handling
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_ignore_result=False,
    
    # Security
    worker_hijack_root_logger=False,
    worker_log_color=False,
)

# Configure queues
celery_app.conf.task_default_queue = "default"
celery_app.conf.task_create_missing_queues = True


def get_celery_app():
    """Get configured Celery app instance."""
    return celery_app


# Task decorators and utilities
def maintenance_task(name=None, **kwargs):
    """Decorator for maintenance-related tasks."""
    def decorator(func):
        return celery_app.task(
            name=name or f"maintenance.{func.__name__}",
            bind=True,
            autoretry_for=(Exception,),
            retry_kwargs={"max_retries": 3, "countdown": 60},
            **kwargs
        )(func)
    return decorator


def notification_task(name=None, **kwargs):
    """Decorator for notification-related tasks."""
    def decorator(func):
        return celery_app.task(
            name=name or f"notification.{func.__name__}",
            bind=True,
            autoretry_for=(Exception,),
            retry_kwargs={"max_retries": 5, "countdown": 30},
            **kwargs
        )(func)
    return decorator


# Health check task
@celery_app.task(bind=True)
def health_check(self):
    """Health check task for monitoring."""
    return {
        "status": "healthy",
        "worker_id": self.request.id,
        "timestamp": "2025-10-01T20:50:00Z"
    }


# Task for manual job generation
@celery_app.task(bind=True)
def manual_job_generation(self, org_id: int, plan_ids: list = None):
    """Manually trigger job generation for specific org/plans."""
    from app.services.maintenance_scheduler import MaintenanceSchedulerService
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        scheduler = MaintenanceSchedulerService(db)
        
        if plan_ids:
            results = []
            for plan_id in plan_ids:
                result = scheduler.generate_jobs_for_plan(plan_id, days_ahead=90)
                results.append(result)
            return {"generated_jobs": sum(r["jobs_created"] for r in results)}
        else:
            result = scheduler.generate_jobs_for_organization(org_id, days_ahead=90)
            return result
            
    finally:
        db.close()