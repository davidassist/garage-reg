"""
Ticket and Work Order Service Layer.

Ticket és munkarendelés szolgáltatási réteg - üzleti logika és állapotgép.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import uuid
from decimal import Decimal

from app.models.tickets import (
    Ticket, WorkOrder, TicketStatus, TicketPriority, WorkOrderStatus,
    TicketComment, TicketStatusHistory, WorkOrderTimeLog, PartUsage
)
from app.models.auth import User
from app.schemas.tickets import (
    TicketCreate, TicketUpdate, TicketStatusChange, TicketResponse,
    WorkOrderCreate, WorkOrderUpdate, WorkOrderStatusChange, WorkOrderResponse,
    PartUsageCreate, TimeLogCreate, SLAMetrics
)
from app.core.exceptions import ValidationError, NotFoundError, BusinessLogicError


class TicketStateMachine:
    """
    Ticket State Machine - manages ticket status transitions.
    
    Ticket állapotgép - ticket státusz átmenetek kezelése.
    """
    
    # Define valid state transitions
    VALID_TRANSITIONS = {
        TicketStatus.OPEN: [TicketStatus.IN_PROGRESS, TicketStatus.CANCELLED],
        TicketStatus.IN_PROGRESS: [
            TicketStatus.WAITING_PARTS, 
            TicketStatus.DONE, 
            TicketStatus.CANCELLED,
            TicketStatus.OPEN  # Can go back if needed
        ],
        TicketStatus.WAITING_PARTS: [
            TicketStatus.IN_PROGRESS, 
            TicketStatus.DONE,
            TicketStatus.CANCELLED
        ],
        TicketStatus.DONE: [TicketStatus.CLOSED, TicketStatus.IN_PROGRESS],  # Can reopen
        TicketStatus.CLOSED: [],  # Terminal state
        TicketStatus.CANCELLED: []  # Terminal state
    }
    
    @classmethod
    def can_transition(cls, from_status: TicketStatus, to_status: TicketStatus) -> bool:
        """Check if status transition is valid."""
        return to_status in cls.VALID_TRANSITIONS.get(from_status, [])
    
    @classmethod
    def get_valid_transitions(cls, from_status: TicketStatus) -> List[TicketStatus]:
        """Get list of valid transitions from current status."""
        return cls.VALID_TRANSITIONS.get(from_status, [])


class WorkOrderStateMachine:
    """
    Work Order State Machine - manages work order status transitions.
    
    Munkarendelés állapotgép - munkarendelés státusz átmenetek kezelése.
    """
    
    # Define valid state transitions  
    VALID_TRANSITIONS = {
        WorkOrderStatus.DRAFT: [
            WorkOrderStatus.SCHEDULED,
            WorkOrderStatus.IN_PROGRESS,
            WorkOrderStatus.CANCELLED
        ],
        WorkOrderStatus.SCHEDULED: [
            WorkOrderStatus.IN_PROGRESS,
            WorkOrderStatus.CANCELLED,
            WorkOrderStatus.DRAFT  # Can go back to draft
        ],
        WorkOrderStatus.IN_PROGRESS: [
            WorkOrderStatus.WAITING_PARTS,
            WorkOrderStatus.COMPLETED,
            WorkOrderStatus.CANCELLED
        ],
        WorkOrderStatus.WAITING_PARTS: [
            WorkOrderStatus.IN_PROGRESS,
            WorkOrderStatus.COMPLETED,
            WorkOrderStatus.CANCELLED
        ],
        WorkOrderStatus.COMPLETED: [],  # Terminal state
        WorkOrderStatus.CANCELLED: []   # Terminal state
    }
    
    @classmethod
    def can_transition(cls, from_status: WorkOrderStatus, to_status: WorkOrderStatus) -> bool:
        """Check if status transition is valid."""
        return to_status in cls.VALID_TRANSITIONS.get(from_status, [])


class TicketService:
    """
    Ticket Service - Business logic for ticket management.
    
    Ticket szolgáltatás - üzleti logika a ticket kezeléshez.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_ticket(self, ticket_data: TicketCreate, reporter: User) -> Ticket:
        """Create a new ticket with automatic SLA calculation."""
        
        # Generate unique ticket number
        ticket_number = self._generate_ticket_number()
        
        # Create ticket
        ticket_dict = ticket_data.model_dump(exclude={'reporter_id'})
        # Convert enums to strings for database storage
        if 'priority' in ticket_dict and hasattr(ticket_dict['priority'], 'value'):
            ticket_dict['priority'] = ticket_dict['priority'].value.upper()
        
        ticket = Ticket(
            ticket_number=ticket_number,
            reporter_id=reporter.id,
            **ticket_dict
        )
        
        # Calculate SLA due dates based on priority
        ticket.calculate_sla_due_dates()
        
        # Set audit fields
        ticket.org_id = reporter.org_id
        ticket.reported_at = datetime.utcnow()
        
        self.db.add(ticket)
        self.db.flush()  # Get the ID
        
        # Log initial status (commented out for testing)
        # self._log_status_change(
        #     ticket=ticket,
        #     old_status=None,
        #     new_status=TicketStatus.OPEN,
        #     changed_by=reporter,
        #     reason="Ticket created"
        # )
        
        self.db.commit()
        self.db.refresh(ticket)
        return ticket
    
    def update_ticket(self, ticket_id: int, ticket_data: TicketUpdate, user: User) -> Ticket:
        """Update ticket details."""
        
        ticket = self._get_ticket_by_id(ticket_id, user.org_id)
        
        # Update fields
        update_data = ticket_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(ticket, field, value)
        
        # Recalculate SLA if priority changed
        if 'priority' in update_data:
            ticket.calculate_sla_due_dates()
        
        ticket.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(ticket)
        return ticket
    
    def change_ticket_status(
        self, 
        ticket_id: int, 
        status_change: TicketStatusChange, 
        user: User
    ) -> Ticket:
        """Change ticket status with state machine validation."""
        
        ticket = self._get_ticket_by_id(ticket_id, user.org_id)
        
        # Validate state transition
        # Convert string to enum for validation
        if isinstance(ticket.status, str):
            # Database stores uppercase (e.g., 'OPEN'), enum values are lowercase (e.g., 'open')
            try:
                current_status = TicketStatus(ticket.status.lower())
            except ValueError:
                raise ValidationError(f"Invalid current ticket status: {ticket.status}")
        else:
            current_status = ticket.status
            
        # Convert new_status to enum if it's a string 
        if isinstance(status_change.new_status, str):
            try:
                new_status = TicketStatus(status_change.new_status.lower())
            except ValueError:
                raise ValidationError(f"Invalid new ticket status: {status_change.new_status}")
        else:
            new_status = status_change.new_status
        


        if not TicketStateMachine.can_transition(current_status, new_status):
            raise ValidationError(
                f"Invalid status transition from {current_status} to {new_status}"
            )
        
        old_status = ticket.status
        old_assignee_id = ticket.assigned_technician_id
        
        # Update ticket status (convert enum to string)
        ticket.status = str(status_change.new_status).upper()
        
        # Handle assignee change
        if status_change.assignee_id is not None:
            ticket.assigned_technician_id = status_change.assignee_id
        
        # Update timestamps based on status
        now = datetime.utcnow()
        
        if status_change.new_status == TicketStatus.IN_PROGRESS and not ticket.started_at:
            ticket.started_at = now
            if not ticket.acknowledged_at:
                ticket.acknowledged_at = now
        
        elif status_change.new_status == TicketStatus.DONE and not ticket.resolved_at:
            ticket.resolved_at = now
            
        elif status_change.new_status == TicketStatus.CLOSED and not ticket.closed_at:
            ticket.closed_at = now
        
        # Check SLA compliance
        self._check_sla_compliance(ticket)
        
        # Log status change (commented out for testing)
        # self._log_status_change(
        #     ticket=ticket,
        #     old_status=old_status,
        #     new_status=status_change.new_status,
        #     changed_by=user,
        #     reason=status_change.change_reason,
        #     old_assignee_id=old_assignee_id,
        #     new_assignee_id=status_change.assignee_id
        # )
        
        ticket.updated_at = now
        self.db.commit()
        self.db.refresh(ticket)
        return ticket
    
    def add_comment(
        self, 
        ticket_id: int, 
        content: str, 
        comment_type: str = "comment",
        is_internal: bool = False,
        is_solution: bool = False,
        user: User = None
    ) -> TicketComment:
        """Add comment to ticket."""
        
        ticket = self._get_ticket_by_id(ticket_id, user.org_id)
        
        comment = TicketComment(
            ticket_id=ticket_id,
            author_id=user.id,
            content=content,
            comment_type=comment_type,
            is_internal=is_internal,
            is_solution=is_solution,
            org_id=user.org_id
        )
        
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment
    
    def get_tickets(
        self,
        org_id: int,
        status: Optional[TicketStatus] = None,
        priority: Optional[TicketPriority] = None,
        assigned_to: Optional[int] = None,
        gate_id: Optional[int] = None,
        overdue_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Ticket]:
        """Get tickets with filtering."""
        
        query = self.db.query(Ticket).filter(
            Ticket.org_id == org_id,
            Ticket.is_active == True
        )
        
        # Apply filters
        if status:
            query = query.filter(Ticket.status == status)
        
        if priority:
            query = query.filter(Ticket.priority == priority)
        
        if assigned_to:
            query = query.filter(Ticket.assigned_technician_id == assigned_to)
        
        if gate_id:
            query = query.filter(Ticket.gate_id == gate_id)
        
        if overdue_only:
            now = datetime.utcnow()
            query = query.filter(
                or_(
                    and_(
                        Ticket.sla_response_by < now,
                        Ticket.acknowledged_at.is_(None)
                    ),
                    and_(
                        Ticket.sla_resolution_by < now,
                        Ticket.resolved_at.is_(None)
                    )
                )
            )
        
        return query.order_by(desc(Ticket.reported_at)).offset(offset).limit(limit).all()
    
    def get_sla_metrics(self, org_id: int, days_back: int = 30) -> List[SLAMetrics]:
        """Get SLA performance metrics by priority."""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        metrics = []
        for priority in TicketPriority:
            # Get tickets for this priority (convert enum to string for database query)
            tickets = self.db.query(Ticket).filter(
                Ticket.org_id == org_id,
                Ticket.priority == priority.value,
                Ticket.reported_at >= cutoff_date
            ).all()
            
            if not tickets:
                continue
            
            # Calculate metrics
            total_tickets = len(tickets)
            
            # Response metrics
            response_times = [
                t.time_to_acknowledge.total_seconds() / 3600 
                for t in tickets 
                if t.time_to_acknowledge
            ]
            
            resolution_times = [
                t.time_to_resolve.total_seconds() / 3600 
                for t in tickets 
                if t.time_to_resolve
            ]
            
            # Simplified breach calculation
            breached_tickets = sum(1 for t in tickets if t.sla_met is False)
            met_tickets = sum(1 for t in tickets if t.sla_met is True)
            
            # Get SLA targets (from first ticket)
            sample_ticket = tickets[0]
            sample_ticket.calculate_sla_due_dates()
            
            compliance_rate = met_tickets / total_tickets if total_tickets > 0 else None
            
            metrics.append(SLAMetrics(
                priority=priority,
                target_response_hours=sample_ticket.sla_response_hours,
                target_resolution_hours=sample_ticket.sla_resolution_hours,
                actual_avg_response_hours=sum(response_times) / len(response_times) if response_times else None,
                actual_avg_resolution_hours=sum(resolution_times) / len(resolution_times) if resolution_times else None,
                response_compliance_rate=compliance_rate,
                resolution_compliance_rate=compliance_rate,
                total_tickets=total_tickets,
                breached_response=breached_tickets,
                breached_resolution=breached_tickets
            ))
        
        return metrics
    
    def _generate_ticket_number(self) -> str:
        """Generate unique ticket number."""
        prefix = "TKT"
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        counter = self.db.query(func.count(Ticket.id)).filter(
            func.date(Ticket.reported_at) == datetime.utcnow().date()
        ).scalar() + 1
        
        return f"{prefix}-{timestamp}-{counter:04d}"
    
    def _get_ticket_by_id(self, ticket_id: int, org_id: int) -> Ticket:
        """Get ticket by ID with org validation."""
        ticket = self.db.query(Ticket).filter(
            Ticket.id == ticket_id,
            Ticket.org_id == org_id,
            Ticket.is_active == True
        ).first()
        
        if not ticket:
            raise NotFoundError(f"Ticket with ID {ticket_id} not found")
        
        return ticket
    
    def _log_status_change(
        self, 
        ticket: Ticket, 
        old_status: Optional[TicketStatus],
        new_status: TicketStatus,
        changed_by: User,
        reason: Optional[str] = None,
        old_assignee_id: Optional[int] = None,
        new_assignee_id: Optional[int] = None
    ):
        """Log status change for audit trail."""
        
        status_log = TicketStatusHistory(
            ticket_id=ticket.id,
            changed_by_id=changed_by.id,
            old_status=old_status,
            new_status=new_status,
            change_reason=reason,
            old_assignee_id=old_assignee_id,
            new_assignee_id=new_assignee_id,
            org_id=changed_by.org_id
        )
        
        self.db.add(status_log)
    
    def _check_sla_compliance(self, ticket: Ticket):
        """Check and update SLA compliance status."""
        now = datetime.utcnow()
        
        # Check SLA compliance (simplified)
        if ticket.resolved_at and ticket.sla_resolution_by:
            ticket.sla_met = ticket.resolved_at <= ticket.sla_resolution_by
        elif ticket.acknowledged_at and ticket.sla_response_by:
            ticket.sla_met = ticket.acknowledged_at <= ticket.sla_response_by


class WorkOrderService:
    """
    Work Order Service - Business logic for work order management.
    
    Munkarendelés szolgáltatás - üzleti logika a munkarendelések kezeléséhez.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_work_order(self, work_order_data: WorkOrderCreate, creator: User) -> WorkOrder:
        """Create a new work order."""
        
        # Generate unique work order number
        work_order_number = self._generate_work_order_number()
        
        # Create work order
        # Filter out fields that don't exist in the WorkOrder model and convert values
        work_order_dict = work_order_data.model_dump()
        # Remove fields not in WorkOrder model
        work_order_dict.pop('estimated_cost', None)
        work_order_dict.pop('custom_fields', None)
        
        # Convert enum values to strings for database storage
        if 'priority' in work_order_dict and hasattr(work_order_dict['priority'], 'value'):
            work_order_dict['priority'] = work_order_dict['priority'].value
        
        work_order = WorkOrder(
            work_order_number=work_order_number,
            **work_order_dict
        )
        
        work_order.org_id = creator.org_id
        
        self.db.add(work_order)
        self.db.commit()
        self.db.refresh(work_order)
        return work_order
    
    def create_work_order_from_ticket(self, ticket_id: int, creator: User) -> WorkOrder:
        """Create work order from existing ticket."""
        
        # Get the ticket
        ticket = self.db.query(Ticket).filter(
            Ticket.id == ticket_id,
            Ticket.org_id == creator.org_id,
            Ticket.is_active == True
        ).first()
        
        if not ticket:
            raise NotFoundError(f"Ticket with ID {ticket_id} not found")
        
        # Create work order based on ticket
        # Convert priority from string to enum if necessary
        if isinstance(ticket.priority, str):
            try:
                priority_enum = TicketPriority(ticket.priority.lower())
            except ValueError:
                priority_enum = TicketPriority.MEDIUM  # Default fallback
        else:
            priority_enum = ticket.priority
            
        work_order_data = WorkOrderCreate(
            title=f"Work Order for {ticket.title}",
            description=ticket.description,
            work_type="repair",  # Default type
            work_category=ticket.category,
            priority=priority_enum,  # Pass the enum directly, conversion handled by model_dump
            gate_id=ticket.gate_id,
            ticket_id=ticket.id,
            assigned_technician_id=ticket.assigned_technician_id
        )
        
        work_order = self.create_work_order(work_order_data, creator)
        
        # Update ticket status to indicate work order created
        if ticket.status == TicketStatus.OPEN:
            ticket.status = TicketStatus.IN_PROGRESS
            ticket.updated_at = datetime.utcnow()
            self.db.commit()
        
        return work_order
    
    def update_work_order(self, work_order_id: int, work_order_data: WorkOrderUpdate, user: User) -> WorkOrder:
        """Update work order details."""
        
        work_order = self._get_work_order_by_id(work_order_id, user.org_id)
        
        # Update fields
        update_data = work_order_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(work_order, field, value)
        
        # Calculate actual duration if both start and end times are set
        if work_order.actual_start and work_order.actual_end:
            duration = work_order.actual_end - work_order.actual_start
            work_order.actual_duration_hours = Decimal(str(duration.total_seconds() / 3600))
        
        work_order.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(work_order)
        return work_order
    
    def change_work_order_status(
        self, 
        work_order_id: int, 
        status_change: WorkOrderStatusChange, 
        user: User
    ) -> WorkOrder:
        """Change work order status with state machine validation."""
        
        work_order = self._get_work_order_by_id(work_order_id, user.org_id)
        
        # Validate state transition - convert string to enum if needed
        from_status = work_order.status
        if isinstance(from_status, str):
            # Database string is already in the correct format (draft, in_progress, etc)
            from_status = WorkOrderStatus(from_status)
        
        to_status = status_change.new_status
        if isinstance(to_status, str):
            to_status = WorkOrderStatus(to_status)
        
        if not WorkOrderStateMachine.can_transition(from_status, to_status):
            raise ValidationError(
                f"Invalid status transition from {from_status} to {to_status}"
            )
        
        old_status = work_order.status
        # Convert enum to lowercase string for database storage (as per model validator) 
        if hasattr(to_status, 'value'):
            # Convert enum value to the database format
            # DRAFT -> 'draft', IN_PROGRESS -> 'in_progress', etc.
            enum_name = to_status.name  # 'IN_PROGRESS'
            new_status_str = enum_name.lower()  # 'in_progress'
        else:
            new_status_str = str(to_status).lower()
        work_order.status = new_status_str
        
        # Update timestamps based on status
        now = datetime.utcnow()
        
        if status_change.new_status == WorkOrderStatus.IN_PROGRESS and not work_order.actual_start:
            work_order.actual_start = now
        
        elif status_change.new_status == WorkOrderStatus.COMPLETED and not work_order.actual_end:
            work_order.actual_end = now
            work_order.progress_percentage = 100
            
            # Calculate actual duration
            if work_order.actual_start:
                duration = work_order.actual_end - work_order.actual_start
                work_order.actual_duration_hours = Decimal(str(duration.total_seconds() / 3600))
        
        work_order.updated_at = now
        self.db.commit()
        # Don't refresh - it would cause enum conversion error when reading from DB
        # The status is already updated in the database and the object has the correct string value
        
        # Update related ticket status if applicable
        if status_change.new_status == WorkOrderStatus.COMPLETED:
            self._update_ticket_from_work_order_completion(work_order, user)
        
        return work_order
    
    def add_part_usage(self, part_usage_data: PartUsageCreate, user: User) -> PartUsage:
        """Add part usage to work order."""
        
        # Verify work order exists and user has access
        work_order = self._get_work_order_by_id(part_usage_data.work_order_id, user.org_id)
        
        # Create part usage
        # Filter out fields that don't exist in the PartUsage model
        part_usage_dict = part_usage_data.model_dump()
        # Remove fields not in PartUsage model
        part_usage_dict.pop('usage_notes', None)
        part_usage_dict.pop('batch_number', None)
        part_usage_dict.pop('serial_number', None)
        part_usage_dict.pop('warranty_months', None)
        
        part_usage = PartUsage(
            **part_usage_dict,
            used_by=user.display_name or user.username,
            org_id=user.org_id
        )
        
        # Calculate total cost
        if part_usage.quantity_used and part_usage.unit_cost:
            part_usage.total_cost = part_usage.quantity_used * part_usage.unit_cost
        
        # Set warranty start date for installed part
        part_usage.warranty_start_date = datetime.utcnow()
        
        self.db.add(part_usage)
        self.db.commit()
        self.db.refresh(part_usage)
        return part_usage
    
    def add_time_log(self, time_log_data: TimeLogCreate, user: User) -> WorkOrderTimeLog:
        """Add time log to work order."""
        
        # Verify work order exists and user has access
        work_order = self._get_work_order_by_id(time_log_data.work_order_id, user.org_id)
        
        # Create time log
        time_log = WorkOrderTimeLog(
            **time_log_data.model_dump(),
            technician_id=user.id,
            org_id=user.org_id
        )
        
        # Calculate duration and cost
        time_log.calculate_duration_and_cost()
        
        self.db.add(time_log)
        self.db.commit()
        self.db.refresh(time_log)
        return time_log
    
    def get_work_orders(
        self,
        org_id: int,
        status: Optional[WorkOrderStatus] = None,
        assigned_to: Optional[int] = None,
        gate_id: Optional[int] = None,
        ticket_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[WorkOrder]:
        """Get work orders with filtering."""
        
        query = self.db.query(WorkOrder).filter(
            WorkOrder.org_id == org_id,
            WorkOrder.is_active == True
        )
        
        # Apply filters
        if status:
            query = query.filter(WorkOrder.status == status)
        
        if assigned_to:
            query = query.filter(WorkOrder.assigned_technician_id == assigned_to)
        
        if gate_id:
            query = query.filter(WorkOrder.gate_id == gate_id)
        
        if ticket_id:
            query = query.filter(WorkOrder.ticket_id == ticket_id)
        
        return query.order_by(desc(WorkOrder.created_at)).offset(offset).limit(limit).all()
    
    def _generate_work_order_number(self) -> str:
        """Generate unique work order number."""
        prefix = "WO"
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        counter = self.db.query(func.count(WorkOrder.id)).filter(
            func.date(WorkOrder.created_at) == datetime.utcnow().date()
        ).scalar() + 1
        
        return f"{prefix}-{timestamp}-{counter:04d}"
    
    def _get_work_order_by_id(self, work_order_id: int, org_id: int) -> WorkOrder:
        """Get work order by ID with org validation."""
        work_order = self.db.query(WorkOrder).filter(
            WorkOrder.id == work_order_id,
            WorkOrder.org_id == org_id,
            WorkOrder.is_active == True
        ).first()
        
        if not work_order:
            raise NotFoundError(f"Work Order with ID {work_order_id} not found")
        
        return work_order
    
    def _update_ticket_from_work_order_completion(self, work_order: WorkOrder, user: User):
        """Update related ticket when work order is completed."""
        
        if not work_order.ticket_id:
            return
        
        ticket = self.db.query(Ticket).filter(
            Ticket.id == work_order.ticket_id,
            Ticket.org_id == user.org_id
        ).first()
        
        if ticket and ticket.status in [TicketStatus.IN_PROGRESS, TicketStatus.WAITING_PARTS]:
            # Check if all work orders for this ticket are completed
            incomplete_work_orders = self.db.query(WorkOrder).filter(
                WorkOrder.ticket_id == ticket.id,
                WorkOrder.status != WorkOrderStatus.COMPLETED,
                WorkOrder.status != WorkOrderStatus.CANCELLED,
                WorkOrder.is_active == True
            ).count()
            
            if incomplete_work_orders == 0:
                # All work orders completed, mark ticket as done
                ticket.status = TicketStatus.DONE
                if not ticket.resolved_at:
                    ticket.resolved_at = datetime.utcnow()
                ticket.updated_at = datetime.utcnow()
                
                self.db.commit()