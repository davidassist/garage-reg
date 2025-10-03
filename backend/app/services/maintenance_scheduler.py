"""Maintenance scheduling service with RRULE support."""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from dateutil.rrule import rrulestr
import structlog

from app.models.maintenance_advanced import AdvancedMaintenancePlan, ScheduledMaintenanceJob, MaintenanceCalendar, MaintenanceNotification
from app.models.organization import Gate
from app.core.celery_app import celery_app, maintenance_task

logger = structlog.get_logger(__name__)


class MaintenanceSchedulerService:
    """Service for generating and managing scheduled maintenance jobs."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_jobs_for_organization(self, org_id: int, days_ahead: int = 90) -> Dict[str, Any]:
        """Generate maintenance jobs for all active plans in an organization."""
        logger.info("Generating jobs for organization", org_id=org_id, days_ahead=days_ahead)
        
        # Get all active maintenance plans
        plans = self.db.query(AdvancedMaintenancePlan).filter(
            and_(
                AdvancedMaintenancePlan.org_id == org_id,
                AdvancedMaintenancePlan.is_active == True
            )
        ).all()
        
        total_jobs_created = 0
        plan_results = []
        
        for plan in plans:
            try:
                result = self.generate_jobs_for_plan(plan.id, days_ahead)
                total_jobs_created += result["jobs_created"]
                plan_results.append({
                    "plan_id": plan.id,
                    "plan_name": plan.name,
                    **result
                })
            except Exception as e:
                logger.error("Failed to generate jobs for plan", 
                           plan_id=plan.id, error=str(e))
                plan_results.append({
                    "plan_id": plan.id,
                    "plan_name": plan.name,
                    "error": str(e),
                    "jobs_created": 0
                })
        
        logger.info("Job generation completed", 
                   org_id=org_id, 
                   total_jobs=total_jobs_created,
                   plans_processed=len(plans))
        
        return {
            "org_id": org_id,
            "days_ahead": days_ahead,
            "plans_processed": len(plans),
            "total_jobs_created": total_jobs_created,
            "plan_results": plan_results
        }
    
    def generate_jobs_for_plan(self, plan_id: int, days_ahead: int = 90) -> Dict[str, Any]:
        """Generate maintenance jobs for a specific plan."""
        plan = self.db.query(AdvancedMaintenancePlan).filter(AdvancedMaintenancePlan.id == plan_id).first()
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
        
        logger.info("Generating jobs for plan", plan_id=plan_id, plan_name=plan.name)
        
        # Get applicable gates
        gates = self._get_applicable_gates(plan)
        
        # Generate occurrences for the next period
        end_date = datetime.utcnow() + timedelta(days=days_ahead)
        occurrences = self._get_plan_occurrences(plan, end_date)
        
        jobs_created = 0
        
        for occurrence in occurrences:
            for gate in gates:
                # Check if job already exists for this occurrence and gate
                occurrence_id = self._generate_occurrence_id(plan.id, gate.id, occurrence)
                
                existing_job = self.db.query(ScheduledMaintenanceJob).filter(
                    and_(
                        ScheduledMaintenanceJob.plan_id == plan_id,
                        ScheduledMaintenanceJob.gate_id == gate.id,
                        ScheduledMaintenanceJob.plan_occurrence_id == occurrence_id
                    )
                ).first()
                
                if existing_job:
                    continue  # Job already exists
                
                # Create new job
                job = self._create_maintenance_job(plan, gate, occurrence, occurrence_id)
                self.db.add(job)
                jobs_created += 1
        
        self.db.commit()
        
        logger.info("Jobs generated for plan", 
                   plan_id=plan_id, 
                   jobs_created=jobs_created,
                   gates_count=len(gates),
                   occurrences_count=len(occurrences))
        
        return {
            "jobs_created": jobs_created,
            "gates_processed": len(gates),
            "occurrences_generated": len(occurrences)
        }
    
    def _get_applicable_gates(self, plan: AdvancedMaintenancePlan) -> List[Gate]:
        """Get all gates that this maintenance plan applies to."""
        query = self.db.query(Gate).filter(Gate.org_id == plan.org_id)
        
        gates = query.all()
        applicable_gates = []
        
        for gate in gates:
            if plan.is_applicable_to_gate(gate):
                applicable_gates.append(gate)
        
        return applicable_gates
    
    def _get_plan_occurrences(self, plan: AdvancedMaintenancePlan, end_date: datetime) -> List[datetime]:
        """Get scheduled occurrences for a plan using RRULE."""
        try:
            # Parse RRULE and get occurrences
            rule = rrulestr(plan.schedule_rrule, dtstart=plan.schedule_start_date)
            
            occurrences = []
            now = datetime.utcnow()
            
            # Adjust start date to account for lead time
            effective_start = now - timedelta(days=plan.lead_time_days or 0)
            
            for occurrence in rule:
                # Only include future occurrences (accounting for lead time)
                if occurrence >= effective_start and occurrence <= end_date:
                    occurrences.append(occurrence)
                
                # Stop if we've passed the plan's end date
                if plan.schedule_end_date and occurrence > plan.schedule_end_date:
                    break
                
                # Safety limit
                if len(occurrences) >= 100:
                    break
            
            return occurrences
            
        except Exception as e:
            logger.error("Failed to parse RRULE", 
                        plan_id=plan.id, 
                        rrule=plan.schedule_rrule, 
                        error=str(e))
            return []
    
    def _generate_occurrence_id(self, plan_id: int, gate_id: int, occurrence: datetime) -> str:
        """Generate unique ID for a plan occurrence."""
        # Format: plan_id-gate_id-YYYYMMDD-HHMMSS
        timestamp = occurrence.strftime("%Y%m%d-%H%M%S")
        return f"{plan_id}-{gate_id}-{timestamp}"
    
    def _create_maintenance_job(
        self, 
        plan: AdvancedMaintenancePlan, 
        gate: Gate, 
        scheduled_date: datetime,
        occurrence_id: str
    ) -> ScheduledMaintenanceJob:
        """Create a new scheduled maintenance job."""
        
        # Calculate due date (scheduled date + buffer)
        due_date = scheduled_date + timedelta(days=plan.deadline_buffer_days or 3)
        
        # Determine assignee
        assignee_id = None
        if plan.auto_assign and plan.default_assignee_id:
            assignee_id = plan.default_assignee_id
        
        job = ScheduledMaintenanceJob(
            org_id=plan.org_id,
            plan_id=plan.id,
            plan_occurrence_id=occurrence_id,
            gate_id=gate.id,
            scheduled_date=scheduled_date,
            due_date=due_date,
            assigned_to_id=assignee_id,
            assigned_at=datetime.utcnow() if assignee_id else None,
            status="scheduled"
        )
        
        return job
    
    def check_overdue_jobs(self, org_id: Optional[int] = None) -> Dict[str, Any]:
        """Check for overdue jobs and update their status."""
        query = self.db.query(ScheduledMaintenanceJob).filter(
            and_(
                ScheduledMaintenanceJob.status.in_(["scheduled", "notified", "in_progress"]),
                ScheduledMaintenanceJob.due_date < datetime.utcnow()
            )
        )
        
        if org_id:
            query = query.filter(ScheduledMaintenanceJob.org_id == org_id)
        
        overdue_jobs = query.all()
        updated_count = 0
        
        for job in overdue_jobs:
            if job.status != "overdue":
                job.status = "overdue"
                updated_count += 1
        
        self.db.commit()
        
        logger.info("Overdue job check completed", 
                   overdue_jobs=len(overdue_jobs),
                   updated_count=updated_count,
                   org_id=org_id)
        
        return {
            "overdue_jobs_found": len(overdue_jobs),
            "jobs_updated": updated_count
        }
    
    def get_upcoming_jobs(
        self, 
        org_id: int, 
        days_ahead: int = 30,
        assignee_id: Optional[int] = None
    ) -> List[ScheduledMaintenanceJob]:
        """Get upcoming maintenance jobs."""
        end_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        query = self.db.query(ScheduledMaintenanceJob).filter(
            and_(
                ScheduledMaintenanceJob.org_id == org_id,
                ScheduledMaintenanceJob.scheduled_date <= end_date,
                ScheduledMaintenanceJob.status.in_(["scheduled", "notified", "in_progress"])
            )
        ).order_by(ScheduledMaintenanceJob.scheduled_date)
        
        if assignee_id:
            query = query.filter(ScheduledMaintenanceJob.assigned_to_id == assignee_id)
        
        return query.all()
    
    def cleanup_old_data(self, days_old: int = 365) -> Dict[str, Any]:
        """Clean up old completed jobs and notifications."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Clean up old completed jobs
        old_jobs = self.db.query(ScheduledMaintenanceJob).filter(
            and_(
                ScheduledMaintenanceJob.status == "completed",
                ScheduledMaintenanceJob.completed_at < cutoff_date
            )
        )
        
        jobs_deleted = old_jobs.count()
        old_jobs.delete()
        
        # Clean up old notifications
        from app.models.maintenance_planning import MaintenanceNotification
        old_notifications = self.db.query(MaintenanceNotification).filter(
            MaintenanceNotification.sent_at < cutoff_date
        )
        
        notifications_deleted = old_notifications.count()
        old_notifications.delete()
        
        self.db.commit()
        
        logger.info("Old data cleanup completed",
                   jobs_deleted=jobs_deleted,
                   notifications_deleted=notifications_deleted,
                   cutoff_date=cutoff_date)
        
        return {
            "jobs_deleted": jobs_deleted,
            "notifications_deleted": notifications_deleted,
            "cutoff_date": cutoff_date.isoformat()
        }


# Celery tasks
@maintenance_task(name="maintenance.generate_scheduled_jobs")
def generate_scheduled_jobs(self):
    """Celery task to generate scheduled maintenance jobs."""
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        scheduler = MaintenanceSchedulerService(db)
        
        # Get all active organizations
        from app.models.organization import Organization
        orgs = db.query(Organization).filter(Organization.is_active == True).all()
        
        total_results = []
        
        for org in orgs:
            try:
                result = scheduler.generate_jobs_for_organization(org.id, days_ahead=90)
                total_results.append(result)
            except Exception as e:
                logger.error("Failed to generate jobs for org", org_id=org.id, error=str(e))
        
        return {
            "organizations_processed": len(orgs),
            "results": total_results
        }
        
    finally:
        db.close()


@maintenance_task(name="maintenance.check_overdue_jobs")
def check_overdue_jobs(self):
    """Celery task to check and update overdue jobs."""
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        scheduler = MaintenanceSchedulerService(db)
        return scheduler.check_overdue_jobs()
    finally:
        db.close()


@maintenance_task(name="maintenance.cleanup_old_data")
def cleanup_old_data(self, days_old: int = 365):
    """Celery task to clean up old data."""
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        scheduler = MaintenanceSchedulerService(db)
        return scheduler.cleanup_old_data(days_old)
    finally:
        db.close()