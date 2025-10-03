"""
Ticket and Work Order API Endpoints.

Ticket és munkarendelés API végpontok.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from io import BytesIO

from app.database import get_db
from app.core.rbac import get_current_user, require_permissions
from app.models.auth import User
from app.models.tickets import TicketStatus, TicketPriority, WorkOrderStatus
from app.schemas.tickets import (
    TicketCreate, TicketUpdate, TicketResponse, TicketStatusChange, TicketSummary,
    WorkOrderCreate, WorkOrderUpdate, WorkOrderResponse, WorkOrderStatusChange, WorkOrderSummary,
    PartUsageCreate, PartUsageResponse, TimeLogCreate, TimeLogResponse,
    SLAMetrics, TicketComment, CommentCreate
)
from app.services.ticket_service import TicketService, WorkOrderService
from app.services.pdf_service import WorkOrderPDFController
from app.core.exceptions import ValidationError, NotFoundError, BusinessLogicError


# Create router
router = APIRouter()


# Ticket Endpoints
@router.post("/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new ticket.
    
    Új ticket létrehozása.
    """
    try:
        ticket_service = TicketService(db)
        ticket = ticket_service.create_ticket(ticket_data, current_user)
        return ticket
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating ticket: {str(e)}")


@router.get("/tickets", response_model=List[TicketResponse])
def get_tickets(
    status_filter: Optional[TicketStatus] = Query(None, alias="status"),
    priority: Optional[TicketPriority] = Query(None),
    assigned_to: Optional[int] = Query(None),
    gate_id: Optional[int] = Query(None),
    overdue_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get tickets with filtering options.
    
    Ticketek lekérése szűrési lehetőségekkel.
    """
    try:
        ticket_service = TicketService(db)
        tickets = ticket_service.get_tickets(
            org_id=current_user.org_id,
            status=status_filter,
            priority=priority,
            assigned_to=assigned_to,
            gate_id=gate_id,
            overdue_only=overdue_only,
            limit=limit,
            offset=offset
        )
        return tickets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tickets: {str(e)}")


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get ticket by ID.
    
    Ticket lekérése ID alapján.
    """
    try:
        ticket_service = TicketService(db)
        ticket = ticket_service._get_ticket_by_id(ticket_id, current_user.org_id)
        return ticket
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving ticket: {str(e)}")


@router.put("/tickets/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update ticket details.
    
    Ticket adatainak frissítése.
    """
    try:
        ticket_service = TicketService(db)
        ticket = ticket_service.update_ticket(ticket_id, ticket_data, current_user)
        return ticket
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating ticket: {str(e)}")


@router.post("/tickets/{ticket_id}/status", response_model=TicketResponse)
def change_ticket_status(
    ticket_id: int,
    status_change: TicketStatusChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Change ticket status with validation.
    
    Ticket státusz módosítása validációval.
    """
    try:
        ticket_service = TicketService(db)
        ticket = ticket_service.change_ticket_status(ticket_id, status_change, current_user)
        return ticket
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error changing ticket status: {str(e)}")


@router.post("/tickets/{ticket_id}/comments", response_model=TicketComment)
def add_ticket_comment(
    ticket_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add comment to ticket.
    
    Komment hozzáadása tickethez.
    """
    try:
        ticket_service = TicketService(db)
        comment = ticket_service.add_comment(
            ticket_id=ticket_id,
            content=comment_data.content,
            comment_type=comment_data.comment_type or "comment",
            is_internal=comment_data.is_internal or False,
            is_solution=comment_data.is_solution or False,
            user=current_user
        )
        return comment
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding comment: {str(e)}")


@router.get("/tickets/sla-metrics", response_model=List[SLAMetrics])
def get_sla_metrics(
    days_back: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get SLA performance metrics.
    
    SLA teljesítmény metrikák lekérése.
    """
    try:
        ticket_service = TicketService(db)
        metrics = ticket_service.get_sla_metrics(current_user.org_id, days_back)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving SLA metrics: {str(e)}")


# Work Order Endpoints
@router.post("/work-orders", response_model=WorkOrderResponse, status_code=status.HTTP_201_CREATED)
def create_work_order(
    work_order_data: WorkOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new work order.
    
    Új munkarendelés létrehozása.
    """
    try:
        work_order_service = WorkOrderService(db)
        work_order = work_order_service.create_work_order(work_order_data, current_user)
        return work_order
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating work order: {str(e)}")


@router.post("/tickets/{ticket_id}/work-orders", response_model=WorkOrderResponse, status_code=status.HTTP_201_CREATED)
def create_work_order_from_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create work order from existing ticket.
    
    Munkarendelés létrehozása meglévő ticketből.
    """
    try:
        work_order_service = WorkOrderService(db)
        work_order = work_order_service.create_work_order_from_ticket(ticket_id, current_user)
        return work_order
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating work order from ticket: {str(e)}")


@router.get("/work-orders", response_model=List[WorkOrderResponse])
def get_work_orders(
    status_filter: Optional[WorkOrderStatus] = Query(None, alias="status"),
    assigned_to: Optional[int] = Query(None),
    gate_id: Optional[int] = Query(None),
    ticket_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get work orders with filtering options.
    
    Munkarendelések lekérése szűrési lehetőségekkel.
    """
    try:
        work_order_service = WorkOrderService(db)
        work_orders = work_order_service.get_work_orders(
            org_id=current_user.org_id,
            status=status_filter,
            assigned_to=assigned_to,
            gate_id=gate_id,
            ticket_id=ticket_id,
            limit=limit,
            offset=offset
        )
        return work_orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving work orders: {str(e)}")


@router.get("/work-orders/{work_order_id}", response_model=WorkOrderResponse)
def get_work_order(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get work order by ID.
    
    Munkarendelés lekérése ID alapján.
    """
    try:
        work_order_service = WorkOrderService(db)
        work_order = work_order_service._get_work_order_by_id(work_order_id, current_user.org_id)
        return work_order
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving work order: {str(e)}")


@router.put("/work-orders/{work_order_id}", response_model=WorkOrderResponse)
def update_work_order(
    work_order_id: int,
    work_order_data: WorkOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update work order details.
    
    Munkarendelés adatainak frissítése.
    """
    try:
        work_order_service = WorkOrderService(db)
        work_order = work_order_service.update_work_order(work_order_id, work_order_data, current_user)
        return work_order
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating work order: {str(e)}")


@router.post("/work-orders/{work_order_id}/status", response_model=WorkOrderResponse)
def change_work_order_status(
    work_order_id: int,
    status_change: WorkOrderStatusChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Change work order status with validation.
    
    Munkarendelés státusz módosítása validációval.
    """
    try:
        work_order_service = WorkOrderService(db)
        work_order = work_order_service.change_work_order_status(work_order_id, status_change, current_user)
        return work_order
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error changing work order status: {str(e)}")


@router.post("/work-orders/{work_order_id}/parts", response_model=PartUsageResponse, status_code=status.HTTP_201_CREATED)
def add_part_usage(
    work_order_id: int,
    part_usage_data: PartUsageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add part usage to work order.
    
    Alkatrész használat hozzáadása munkarendeléshez.
    """
    try:
        # Ensure work_order_id matches the URL parameter
        part_usage_data.work_order_id = work_order_id
        
        work_order_service = WorkOrderService(db)
        part_usage = work_order_service.add_part_usage(part_usage_data, current_user)
        return part_usage
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding part usage: {str(e)}")


@router.post("/work-orders/{work_order_id}/time-logs", response_model=TimeLogResponse, status_code=status.HTTP_201_CREATED)
def add_time_log(
    work_order_id: int,
    time_log_data: TimeLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add time log to work order.
    
    Időnapló hozzáadása munkarendeléshez.
    """
    try:
        # Ensure work_order_id matches the URL parameter
        time_log_data.work_order_id = work_order_id
        
        work_order_service = WorkOrderService(db)
        time_log = work_order_service.add_time_log(time_log_data, current_user)
        return time_log
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding time log: {str(e)}")


# Summary and Reporting Endpoints
@router.get("/tickets/summary", response_model=TicketSummary)
def get_ticket_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get ticket summary statistics.
    
    Ticket összesítő statisztikák lekérése.
    """
    try:
        ticket_service = TicketService(db)
        
        # Get various ticket counts
        from sqlalchemy import func
        from app.models.tickets import Ticket
        
        # Total tickets
        total_tickets = db.query(func.count(Ticket.id)).filter(
            Ticket.org_id == current_user.org_id,
            Ticket.is_active == True
        ).scalar()
        
        # Open tickets  
        open_tickets = db.query(func.count(Ticket.id)).filter(
            Ticket.org_id == current_user.org_id,
            Ticket.status == TicketStatus.OPEN,
            Ticket.is_active == True
        ).scalar()
        
        # In progress tickets
        in_progress_tickets = db.query(func.count(Ticket.id)).filter(
            Ticket.org_id == current_user.org_id,
            Ticket.status == TicketStatus.IN_PROGRESS,
            Ticket.is_active == True
        ).scalar()
        
        # Overdue tickets (SLA breached)
        from datetime import datetime
        now = datetime.utcnow()
        
        overdue_tickets = db.query(func.count(Ticket.id)).filter(
            Ticket.org_id == current_user.org_id,
            Ticket.is_active == True,
            (
                (Ticket.sla_response_by < now) & (Ticket.acknowledged_at.is_(None)) |
                (Ticket.sla_resolution_by < now) & (Ticket.resolved_at.is_(None))
            )
        ).scalar()
        
        # High priority tickets
        high_priority_tickets = db.query(func.count(Ticket.id)).filter(
            Ticket.org_id == current_user.org_id,
            Ticket.priority.in_([TicketPriority.CRITICAL, TicketPriority.HIGH]),
            Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.WAITING_PARTS]),
            Ticket.is_active == True
        ).scalar()
        
        return TicketSummary(
            total_tickets=total_tickets,
            open_tickets=open_tickets,
            in_progress_tickets=in_progress_tickets,
            overdue_tickets=overdue_tickets,
            high_priority_tickets=high_priority_tickets
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving ticket summary: {str(e)}")


@router.get("/work-orders/summary", response_model=WorkOrderSummary)
def get_work_order_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get work order summary statistics.
    
    Munkarendelés összesítő statisztikák lekérése.
    """
    try:
        from sqlalchemy import func
        from app.models.tickets import WorkOrder
        
        # Total work orders
        total_work_orders = db.query(func.count(WorkOrder.id)).filter(
            WorkOrder.org_id == current_user.org_id,
            WorkOrder.is_active == True
        ).scalar()
        
        # Active work orders
        active_work_orders = db.query(func.count(WorkOrder.id)).filter(
            WorkOrder.org_id == current_user.org_id,
            WorkOrder.status.in_([WorkOrderStatus.SCHEDULED, WorkOrderStatus.IN_PROGRESS, WorkOrderStatus.WAITING_PARTS]),
            WorkOrder.is_active == True
        ).scalar()
        
        # Completed work orders
        completed_work_orders = db.query(func.count(WorkOrder.id)).filter(
            WorkOrder.org_id == current_user.org_id,
            WorkOrder.status == WorkOrderStatus.COMPLETED,
            WorkOrder.is_active == True
        ).scalar()
        
        # Calculate total cost for completed work orders
        from app.models.tickets import PartUsage, WorkOrderTimeLog
        
        parts_cost = db.query(func.coalesce(func.sum(PartUsage.total_cost), 0)).join(WorkOrder).filter(
            WorkOrder.org_id == current_user.org_id,
            WorkOrder.status == WorkOrderStatus.COMPLETED,
            WorkOrder.is_active == True,
            PartUsage.is_active == True
        ).scalar() or 0
        
        labor_cost = db.query(func.coalesce(func.sum(WorkOrderTimeLog.total_cost), 0)).join(WorkOrder).filter(
            WorkOrder.org_id == current_user.org_id,
            WorkOrder.status == WorkOrderStatus.COMPLETED,
            WorkOrder.is_active == True,
            WorkOrderTimeLog.is_active == True
        ).scalar() or 0
        
        total_cost = float(parts_cost) + float(labor_cost)
        
        return WorkOrderSummary(
            total_work_orders=total_work_orders,
            active_work_orders=active_work_orders,
            completed_work_orders=completed_work_orders,
            total_parts_cost=float(parts_cost),
            total_labor_cost=float(labor_cost),
            total_cost=total_cost
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving work order summary: {str(e)}")


# PDF Report Generation Endpoints
@router.get("/work-orders/{work_order_id}/completion-report")
def generate_work_order_completion_report(
    work_order_id: int,
    include_parts: bool = Query(True, description="Include parts usage in report"),
    include_time_logs: bool = Query(True, description="Include time logs in report"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate PDF completion report for work order.
    
    PDF befejezési riport generálása munkarendeléshez.
    """
    try:
        # Get work order with relationships
        work_order_service = WorkOrderService(db)
        work_order = work_order_service._get_work_order_by_id(work_order_id, current_user.org_id)
        
        # Check if work order is completed
        if work_order.status != WorkOrderStatus.COMPLETED:
            raise HTTPException(
                status_code=400, 
                detail="Work order must be completed to generate completion report"
            )
        
        # Generate PDF
        pdf_controller = WorkOrderPDFController()
        pdf_buffer = pdf_controller.generate_completion_report(
            work_order=work_order,
            include_parts=include_parts,
            include_time_logs=include_time_logs
        )
        
        # Return as streaming response
        return StreamingResponse(
            BytesIO(pdf_buffer.getvalue()),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=work_order_{work_order.work_order_number}_completion_report.pdf"
            }
        )
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF report: {str(e)}")