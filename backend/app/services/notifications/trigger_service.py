"""
Event trigger system for automatic notifications
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .notification_service import NotificationService
from .models import NotificationTrigger, NotificationPriority
from ...models.organization import Gate
from ...models.inspections import Inspection
from ...models.tickets import WorkOrder
from ...models.maintenance import MaintenanceJob
from ...models.auth import User
from ...database import get_db

logger = logging.getLogger(__name__)


class NotificationTriggerService:
    """Service for handling notification triggers based on system events"""
    
    def __init__(self):
        self.notification_service = NotificationService()
        self.trigger_intervals = {
            'inspection_due_check': timedelta(hours=6),  # Check every 6 hours
            'sla_monitoring': timedelta(minutes=15),     # Check every 15 minutes
            'maintenance_due_check': timedelta(hours=12), # Check every 12 hours
        }
    
    async def check_inspection_due_notifications(self, db: Session) -> Dict[str, Any]:
        """Check for due inspections and send notifications"""
        
        try:
            # Get inspections due in the next 7 days
            cutoff_date = datetime.now(timezone.utc) + timedelta(days=7)
            
            due_inspections = db.query(Inspection).filter(
                and_(
                    Inspection.scheduled_date <= cutoff_date,
                    Inspection.status.in_(['scheduled', 'pending']),
                    or_(
                        Inspection.notification_sent == False,
                        Inspection.notification_sent.is_(None)
                    )
                )
            ).all()
            
            notifications_sent = 0
            
            for inspection in due_inspections:
                # Calculate days until due
                days_until_due = (inspection.scheduled_date - datetime.now(timezone.utc)).days
                
                # Skip if too far in future (more than 7 days)
                if days_until_due > 7:
                    continue
                
                # Get gate and inspector information
                gate = inspection.gate
                inspector = inspection.assigned_to
                
                if not gate or not inspector:
                    logger.warning(f"Missing gate or inspector for inspection {inspection.id}")
                    continue
                
                # Determine notification timing
                should_notify = False
                
                if days_until_due <= 0:  # Overdue
                    should_notify = True
                elif days_until_due <= 1:  # Due today/tomorrow
                    should_notify = True
                elif days_until_due <= 3:  # Due in 3 days
                    should_notify = True
                elif days_until_due == 7:  # 1 week advance notice
                    should_notify = True
                
                if should_notify:
                    try:
                        result = await self.notification_service.send_inspection_due_notification(
                            gate_name=gate.name,
                            gate_location=f"{gate.building.name if gate.building else ''} - {gate.location}",
                            inspection_type=inspection.inspection_type or "Általános ellenőrzés",
                            due_date=inspection.scheduled_date,
                            inspector_email=inspector.email,
                            inspector_name=inspector.full_name,
                            gate_id=gate.id,
                            days_until_due=days_until_due
                        )
                        
                        if result['status'] == 'sent':
                            # Mark as notified
                            inspection.notification_sent = True
                            inspection.last_notification_at = datetime.now(timezone.utc)
                            notifications_sent += 1
                            
                            logger.info(f"Sent inspection due notification for gate {gate.name}")
                        
                    except Exception as e:
                        logger.error(f"Failed to send inspection notification for {inspection.id}: {e}")
            
            # Commit changes
            db.commit()
            
            return {
                'status': 'completed',
                'inspections_checked': len(due_inspections),
                'notifications_sent': notifications_sent,
                'timestamp': datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"Error checking inspection due notifications: {e}")
            db.rollback()
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc)
            }
    
    async def check_sla_expiring_notifications(self, db: Session) -> Dict[str, Any]:
        """Check for SLA violations and send notifications"""
        
        try:
            # Get active work orders with SLA deadlines
            active_work_orders = db.query(WorkOrder).filter(
                and_(
                    WorkOrder.status.in_(['assigned', 'in_progress']),
                    WorkOrder.sla_deadline.isnot(None),
                    WorkOrder.sla_deadline > datetime.now(timezone.utc)
                )
            ).all()
            
            notifications_sent = 0
            
            for work_order in active_work_orders:
                # Calculate hours remaining
                time_remaining = work_order.sla_deadline - datetime.now(timezone.utc)
                hours_remaining = time_remaining.total_seconds() / 3600
                
                # Determine if notification is needed
                should_notify = False
                notification_type = None
                
                if hours_remaining <= 0:  # Already expired
                    continue  # Handle expired separately
                elif hours_remaining <= 2:  # Critical: 2 hours remaining
                    should_notify = True
                    notification_type = 'critical'
                elif hours_remaining <= 4:  # Warning: 4 hours remaining
                    should_notify = True
                    notification_type = 'warning'
                elif hours_remaining <= 24:  # Notice: 24 hours remaining
                    should_notify = True
                    notification_type = 'notice'
                
                # Check if already notified for this level
                if should_notify:
                    last_notification = getattr(work_order, 'last_sla_notification_type', None)
                    
                    # Only send if we haven't notified at this level or higher
                    if (last_notification != notification_type and 
                        not (last_notification == 'critical' and notification_type in ['warning', 'notice'])):
                        
                        # Get assignee information
                        assignee = work_order.assigned_to
                        if not assignee:
                            logger.warning(f"No assignee for work order {work_order.id}")
                            continue
                        
                        try:
                            result = await self.notification_service.send_sla_expiring_notification(
                                work_order_id=str(work_order.id),
                                work_order_title=work_order.title,
                                client_name=work_order.client.name if work_order.client else "N/A",
                                sla_deadline=work_order.sla_deadline,
                                hours_remaining=hours_remaining,
                                priority=work_order.priority or "normal",
                                assignee_email=assignee.email,
                                assignee_name=assignee.full_name
                            )
                            
                            if result['status'] == 'sent':
                                # Update notification tracking
                                work_order.last_sla_notification_type = notification_type
                                work_order.last_sla_notification_at = datetime.now(timezone.utc)
                                notifications_sent += 1
                                
                                logger.info(f"Sent SLA notification for work order {work_order.id}")
                        
                        except Exception as e:
                            logger.error(f"Failed to send SLA notification for {work_order.id}: {e}")
            
            # Commit changes
            db.commit()
            
            return {
                'status': 'completed',
                'work_orders_checked': len(active_work_orders),
                'notifications_sent': notifications_sent,
                'timestamp': datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"Error checking SLA expiring notifications: {e}")
            db.rollback()
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc)
            }
    
    async def on_work_order_completed(
        self,
        work_order: WorkOrder,
        completed_by_user: User,
        db: Session
    ) -> Dict[str, Any]:
        """Trigger notification when work order is completed"""
        
        try:
            # Get notification recipients
            recipients_emails = []
            
            # Add client contact if available
            if work_order.client and work_order.client.contact_email:
                recipients_emails.append(work_order.client.contact_email)
            
            # Add manager/supervisor
            if work_order.created_by and work_order.created_by.email:
                recipients_emails.append(work_order.created_by.email)
            
            # Remove duplicates
            recipients_emails = list(set(recipients_emails))
            
            if not recipients_emails:
                logger.warning(f"No recipients for work order completion notification: {work_order.id}")
                return {'status': 'skipped', 'reason': 'no_recipients'}
            
            # Send notification to each recipient
            notifications_sent = 0
            
            for email in recipients_emails:
                try:
                    result = await self.notification_service.send_work_order_completed_notification(
                        work_order_id=str(work_order.id),
                        work_order_title=work_order.title,
                        client_name=work_order.client.name if work_order.client else "N/A",
                        completed_by=completed_by_user.full_name,
                        completion_date=work_order.completed_at or datetime.now(timezone.utc),
                        results_summary=work_order.completion_notes or "Munka sikeresen elvégezve",
                        client_email=email,
                        manager_email=email  # Same email for both in this iteration
                    )
                    
                    if result['status'] == 'sent':
                        notifications_sent += 1
                
                except Exception as e:
                    logger.error(f"Failed to send completion notification to {email}: {e}")
            
            # Mark work order as notification sent
            work_order.completion_notification_sent = True
            work_order.completion_notification_at = datetime.now(timezone.utc)
            db.commit()
            
            return {
                'status': 'completed',
                'work_order_id': work_order.id,
                'recipients': len(recipients_emails),
                'notifications_sent': notifications_sent,
                'timestamp': datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"Error sending work order completion notification: {e}")
            db.rollback()
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc)
            }
    
    async def on_gate_fault_detected(
        self,
        gate: Gate,
        fault_description: str,
        severity: str,
        reported_by_user: User,
        db: Session
    ) -> Dict[str, Any]:
        """Trigger urgent notification when gate fault is detected"""
        
        try:
            # Get maintenance team emails
            maintenance_users = db.query(User).filter(
                User.role_name.in_(['technician', 'manager'])
            ).all()
            
            notifications_sent = 0
            
            for user in maintenance_users:
                if not user.email:
                    continue
                
                try:
                    # Send urgent notification
                    from .models import NotificationRequest, NotificationRecipient
                    
                    request = NotificationRequest(
                        trigger=NotificationTrigger.GATE_FAULT,
                        recipients=[
                            NotificationRecipient(
                                email=user.email,
                                name=user.full_name,
                                phone=getattr(user, 'phone', None)
                            )
                        ],
                        template_data={
                            'gate_name': gate.name,
                            'gate_location': f"{gate.building.name if gate.building else ''} - {gate.location}",
                            'fault_description': fault_description,
                            'severity': severity,
                            'reported_by': reported_by_user.full_name,
                            'report_time': datetime.now(timezone.utc),
                            'gate_id': gate.id
                        },
                        priority=NotificationPriority.URGENT
                    )
                    
                    result = await self.notification_service.send_notification(request)
                    
                    if result['status'] == 'sent':
                        notifications_sent += 1
                
                except Exception as e:
                    logger.error(f"Failed to send gate fault notification to {user.email}: {e}")
            
            return {
                'status': 'completed',
                'gate_id': gate.id,
                'fault_severity': severity,
                'notifications_sent': notifications_sent,
                'timestamp': datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"Error sending gate fault notification: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc)
            }
    
    async def run_periodic_checks(self, db: Session) -> Dict[str, Any]:
        """Run all periodic notification checks"""
        
        results = {}
        
        # Check inspections due
        try:
            inspection_result = await self.check_inspection_due_notifications(db)
            results['inspection_checks'] = inspection_result
        except Exception as e:
            results['inspection_checks'] = {'status': 'failed', 'error': str(e)}
        
        # Check SLA violations
        try:
            sla_result = await self.check_sla_expiring_notifications(db)
            results['sla_checks'] = sla_result
        except Exception as e:
            results['sla_checks'] = {'status': 'failed', 'error': str(e)}
        
        return {
            'periodic_check_completed': True,
            'timestamp': datetime.now(timezone.utc),
            'results': results
        }