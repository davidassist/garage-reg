"""API routes for maintenance planning and scheduling."""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
import secrets

from app.database import get_db
from app.core.rbac import get_current_active_user, require_permission
from app.models.auth import User
from app.models.maintenance_advanced import (
    AdvancedMaintenancePlan, 
    ScheduledMaintenanceJob,
    MaintenanceCalendar
)
from app.schemas.maintenance_planning import (
    MaintenancePlanCreate,
    MaintenancePlanUpdate,
    MaintenancePlanResponse,
    ScheduledJobResponse,
    CalendarSettingsUpdate,
    CalendarSettingsResponse,
    JobGenerationRequest,
    JobGenerationResponse
)
from app.services.maintenance_scheduler import MaintenanceSchedulerService
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/maintenance", tags=["Maintenance Planning"])


@router.post("/plans", response_model=MaintenancePlanResponse)
async def create_maintenance_plan(
    plan_data: MaintenancePlanCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new maintenance plan with RRULE scheduling."""
    
    # Check permissions
    require_permission(current_user, "maintenance:write")
    
    # Validate RRULE
    try:
        from dateutil.rrule import rrulestr
        rrulestr(plan_data.schedule_rrule, dtstart=plan_data.schedule_start_date)
    except Exception as e:
        raise HTTPException(400, f"Invalid RRULE: {str(e)}")
    
    # Create plan
    plan = MaintenancePlan(
        **plan_data.model_dump(),
        org_id=current_user.org_id,
        created_by_id=current_user.id
    )
    
    db.add(plan)
    db.commit()
    db.refresh(plan)
    
    # Generate initial jobs
    background_tasks.add_task(
        generate_jobs_for_plan_task,
        plan.id,
        days_ahead=90
    )
    
    return MaintenancePlanResponse.model_validate(plan)


@router.get("/plans", response_model=List[MaintenancePlanResponse])
async def list_maintenance_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List maintenance plans for the organization."""
    
    require_permission(current_user, "maintenance:read")
    
    query = db.query(MaintenancePlan).filter(
        MaintenancePlan.org_id == current_user.org_id
    )
    
    if category:
        query = query.filter(MaintenancePlan.category == category)
    
    if is_active is not None:
        query = query.filter(MaintenancePlan.is_active == is_active)
    
    plans = query.offset(skip).limit(limit).all()
    
    return [MaintenancePlanResponse.model_validate(plan) for plan in plans]


@router.get("/plans/{plan_id}", response_model=MaintenancePlanResponse)
async def get_maintenance_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get maintenance plan details."""
    
    require_permission(current_user, "maintenance:read")
    
    plan = db.query(MaintenancePlan).filter(
        MaintenancePlan.id == plan_id,
        MaintenancePlan.org_id == current_user.org_id
    ).first()
    
    if not plan:
        raise HTTPException(404, "Maintenance plan not found")
    
    return MaintenancePlanResponse.model_validate(plan)


@router.put("/plans/{plan_id}", response_model=MaintenancePlanResponse)
async def update_maintenance_plan(
    plan_id: int,
    plan_data: MaintenancePlanUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update maintenance plan."""
    
    require_permission(current_user, "maintenance:write")
    
    plan = db.query(MaintenancePlan).filter(
        MaintenancePlan.id == plan_id,
        MaintenancePlan.org_id == current_user.org_id
    ).first()
    
    if not plan:
        raise HTTPException(404, "Maintenance plan not found")
    
    # Validate RRULE if provided
    if plan_data.schedule_rrule:
        try:
            from dateutil.rrule import rrulestr
            start_date = plan_data.schedule_start_date or plan.schedule_start_date
            rrulestr(plan_data.schedule_rrule, dtstart=start_date)
        except Exception as e:
            raise HTTPException(400, f"Invalid RRULE: {str(e)}")
    
    # Update plan
    update_data = plan_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plan, field, value)
    
    plan.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(plan)
    
    # Regenerate jobs if schedule changed
    if plan_data.schedule_rrule or plan_data.schedule_start_date:
        background_tasks.add_task(
            generate_jobs_for_plan_task,
            plan.id,
            days_ahead=90
        )
    
    return MaintenancePlanResponse.model_validate(plan)


@router.delete("/plans/{plan_id}")
async def delete_maintenance_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete maintenance plan (soft delete - deactivate)."""
    
    require_permission(current_user, "maintenance:write")
    
    plan = db.query(MaintenancePlan).filter(
        MaintenancePlan.id == plan_id,
        MaintenancePlan.org_id == current_user.org_id
    ).first()
    
    if not plan:
        raise HTTPException(404, "Maintenance plan not found")
    
    plan.is_active = False
    plan.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Maintenance plan deactivated"}


@router.post("/plans/{plan_id}/generate-jobs", response_model=JobGenerationResponse)
async def generate_jobs_for_plan(
    plan_id: int,
    request: JobGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Manually generate maintenance jobs for a specific plan."""
    
    require_permission(current_user, "maintenance:write")
    
    plan = db.query(MaintenancePlan).filter(
        MaintenancePlan.id == plan_id,
        MaintenancePlan.org_id == current_user.org_id
    ).first()
    
    if not plan:
        raise HTTPException(404, "Maintenance plan not found")
    
    scheduler = MaintenanceSchedulerService(db)
    result = scheduler.generate_jobs_for_plan(plan_id, request.days_ahead)
    
    return JobGenerationResponse(**result)


@router.get("/jobs", response_model=List[ScheduledJobResponse])
async def list_scheduled_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    assigned_to_me: bool = Query(False),
    days_ahead: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List scheduled maintenance jobs."""
    
    require_permission(current_user, "maintenance:read")
    
    query = db.query(ScheduledMaintenanceJob).filter(
        ScheduledMaintenanceJob.org_id == current_user.org_id
    )
    
    # Filter by assignment
    if assigned_to_me:
        query = query.filter(ScheduledMaintenanceJob.assigned_to_id == current_user.id)
    
    # Filter by status
    if status:
        query = query.filter(ScheduledMaintenanceJob.status == status)
    
    # Filter by date range
    end_date = datetime.utcnow() + timedelta(days=days_ahead)
    query = query.filter(
        ScheduledMaintenanceJob.scheduled_date <= end_date
    )
    
    jobs = query.order_by(ScheduledMaintenanceJob.scheduled_date).offset(skip).limit(limit).all()
    
    return [ScheduledJobResponse.model_validate(job) for job in jobs]


@router.get("/jobs/{job_id}", response_model=ScheduledJobResponse)
async def get_scheduled_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get scheduled job details."""
    
    require_permission(current_user, "maintenance:read")
    
    job = db.query(ScheduledMaintenanceJob).filter(
        ScheduledMaintenanceJob.id == job_id,
        ScheduledMaintenanceJob.org_id == current_user.org_id
    ).first()
    
    if not job:
        raise HTTPException(404, "Scheduled job not found")
    
    return ScheduledJobResponse.model_validate(job)


@router.post("/jobs/{job_id}/complete")
async def complete_maintenance_job(
    job_id: int,
    completion_data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark maintenance job as completed."""
    
    require_permission(current_user, "maintenance:write")
    
    job = db.query(ScheduledMaintenanceJob).filter(
        ScheduledMaintenanceJob.id == job_id,
        ScheduledMaintenanceJob.org_id == current_user.org_id
    ).first()
    
    if not job:
        raise HTTPException(404, "Scheduled job not found")
    
    if job.status == "completed":
        raise HTTPException(400, "Job already completed")
    
    # Update job
    job.status = "completed"
    job.completed_at = datetime.utcnow()
    job.completion_notes = completion_data.get("notes", "")
    job.actual_duration_minutes = completion_data.get("duration_minutes")
    job.issues_found = completion_data.get("issues_found", [])
    job.parts_used = completion_data.get("parts_used", [])
    
    db.commit()
    
    # Send completion notification
    background_tasks.add_task(
        send_completion_notification,
        job_id
    )
    
    return {"message": "Job marked as completed"}


@router.get("/calendar/settings", response_model=CalendarSettingsResponse)
async def get_calendar_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's calendar settings."""
    
    settings = db.query(MaintenanceCalendar).filter(
        MaintenanceCalendar.user_id == current_user.id
    ).first()
    
    if not settings:
        # Create default settings
        settings = MaintenanceCalendar(
            org_id=current_user.org_id,
            user_id=current_user.id,
            ics_feed_token=secrets.token_urlsafe(32)
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return CalendarSettingsResponse.model_validate(settings)


@router.put("/calendar/settings", response_model=CalendarSettingsResponse)
async def update_calendar_settings(
    settings_data: CalendarSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update user's calendar settings."""
    
    settings = db.query(MaintenanceCalendar).filter(
        MaintenanceCalendar.user_id == current_user.id
    ).first()
    
    if not settings:
        settings = MaintenanceCalendar(
            org_id=current_user.org_id,
            user_id=current_user.id,
            ics_feed_token=secrets.token_urlsafe(32)
        )
        db.add(settings)
    
    # Update settings
    update_data = settings_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    settings.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(settings)
    
    return CalendarSettingsResponse.model_validate(settings)


@router.post("/calendar/regenerate-token")
async def regenerate_calendar_token(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Regenerate calendar feed token for security."""
    
    settings = db.query(MaintenanceCalendar).filter(
        MaintenanceCalendar.user_id == current_user.id
    ).first()
    
    if not settings:
        raise HTTPException(404, "Calendar settings not found")
    
    settings.ics_feed_token = secrets.token_urlsafe(32)
    settings.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Calendar token regenerated",
        "new_token": settings.ics_feed_token
    }


@router.get("/calendar/feed.ics")
async def get_calendar_feed(
    token: str,
    db: Session = Depends(get_db)
):
    """Get ICS calendar feed for user (public endpoint with token)."""
    
    # Find user by token
    settings = db.query(MaintenanceCalendar).filter(
        MaintenanceCalendar.ics_feed_token == token,
        MaintenanceCalendar.feed_enabled == True
    ).first()
    
    if not settings:
        raise HTTPException(404, "Calendar feed not found or disabled")
    
    # Generate ICS feed
    notification_service = NotificationService(db)
    ics_content = notification_service.generate_calendar_feed(settings.user_id, token)
    
    from fastapi import Response
    
    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": "attachment; filename=maintenance-calendar.ics"
        }
    )


@router.post("/jobs/{job_id}/send-reminder")
async def send_job_reminder(
    job_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Manually send reminder for a maintenance job."""
    
    require_permission(current_user, "maintenance:write")
    
    job = db.query(ScheduledMaintenanceJob).filter(
        ScheduledMaintenanceJob.id == job_id,
        ScheduledMaintenanceJob.org_id == current_user.org_id
    ).first()
    
    if not job:
        raise HTTPException(404, "Scheduled job not found")
    
    background_tasks.add_task(
        send_maintenance_reminder,
        job_id
    )
    
    return {"message": "Reminder scheduled to be sent"}


# Background task helpers
def generate_jobs_for_plan_task(plan_id: int, days_ahead: int = 90):
    """Background task to generate jobs for a plan."""
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        scheduler = MaintenanceSchedulerService(db)
        scheduler.generate_jobs_for_plan(plan_id, days_ahead)
    finally:
        db.close()


def send_completion_notification(job_id: int):
    """Background task to send completion notification."""
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        notification_service = NotificationService(db)
        notification_service.send_maintenance_reminder(job_id, "completion")
    finally:
        db.close()


def send_maintenance_reminder(job_id: int):
    """Background task to send maintenance reminder."""
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        notification_service = NotificationService(db)
        notification_service.send_maintenance_reminder(job_id, "reminder")
    finally:
        db.close()