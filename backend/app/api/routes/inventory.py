"""
Inventory management API endpoints
Raktárkezelési API végpontok
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from pydantic import BaseModel, Field

from app.database import get_db
from app.core.deps import get_current_active_user
from app.core.rbac import require_permission, PermissionActions, Resources
from app.models.auth import User
from app.models.inventory import InventoryItem, Warehouse, StockMovement, StockAlert, StockTake
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["inventory"])


# Pydantic Models
class StockReceiptRequest(BaseModel):
    inventory_item_id: int
    quantity: Decimal = Field(..., gt=0)
    unit_cost: Optional[Decimal] = Field(None, ge=0)
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    notes: Optional[str] = None


class StockIssueRequest(BaseModel):
    inventory_item_id: int
    quantity: Decimal = Field(..., gt=0)
    work_order_id: Optional[int] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    notes: Optional[str] = None


class StockAdjustmentRequest(BaseModel):
    inventory_item_id: int
    new_quantity: Decimal = Field(..., ge=0)
    reason: str
    notes: Optional[str] = None


class StockBalanceResponse(BaseModel):
    warehouse_code: str
    warehouse_name: str
    part_code: str
    part_name: str
    location_code: Optional[str]
    quantity_on_hand: Decimal
    quantity_reserved: Decimal
    quantity_available: Decimal
    minimum_stock: Decimal
    unit_cost: Optional[Decimal]
    average_cost: Optional[Decimal]
    total_value: Optional[Decimal]
    last_movement_date: Optional[datetime]
    stock_status: str


class StockMovementResponse(BaseModel):
    movement_number: str
    movement_date: datetime
    movement_type: str
    warehouse_code: str
    part_code: str
    part_name: str
    debit_quantity: Decimal
    credit_quantity: Decimal
    net_quantity: Decimal
    unit_cost: Optional[Decimal]
    total_cost: Optional[Decimal]
    quantity_before: Decimal
    quantity_after: Decimal
    reference_type: Optional[str]
    reference_id: Optional[int]
    notes: Optional[str]


# API Endpoints

@router.post("/receipt")
@require_permission(Resources.GATE, PermissionActions.UPDATE)
async def receive_stock(
    request: StockReceiptRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Bevételezés - Receive stock into inventory
    """
    try:
        inventory_service = InventoryService(db)
        movement = inventory_service.receive_stock(
            inventory_item_id=request.inventory_item_id,
            quantity=request.quantity,
            unit_cost=request.unit_cost,
            reference_type=request.reference_type,
            reference_id=request.reference_id,
            notes=request.notes,
            user_id=current_user.id
        )
        
        return {
            "status": "success",
            "movement_number": movement.movement_number,
            "message": f"Successfully received {request.quantity} units"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/issue")
@require_permission(Resources.GATE, PermissionActions.UPDATE)
async def issue_stock(
    request: StockIssueRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Kiadás - Issue stock from inventory
    """
    try:
        inventory_service = InventoryService(db)
        movement, part_usage = inventory_service.issue_stock(
            inventory_item_id=request.inventory_item_id,
            quantity=request.quantity,
            work_order_id=request.work_order_id,
            reference_type=request.reference_type,
            reference_id=request.reference_id,
            notes=request.notes,
            user_id=current_user.id
        )
        
        response = {
            "status": "success",
            "movement_number": movement.movement_number,
            "message": f"Successfully issued {request.quantity} units"
        }
        
        if part_usage:
            response["part_usage_id"] = part_usage.id
            response["work_order_id"] = request.work_order_id
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/adjustment")
@require_permission(Resources.GATE, PermissionActions.UPDATE)
async def adjust_stock(
    request: StockAdjustmentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Leltári korrekció - Adjust stock levels
    """
    try:
        inventory_service = InventoryService(db)
        movement = inventory_service.adjust_stock(
            inventory_item_id=request.inventory_item_id,
            new_quantity=request.new_quantity,
            reason=request.reason,
            notes=request.notes,
            user_id=current_user.id
        )
        
        if not movement:
            return {
                "status": "no_change",
                "message": "No adjustment needed - quantities match"
            }
        
        return {
            "status": "success",
            "movement_number": movement.movement_number,
            "message": f"Stock adjusted to {request.new_quantity} units"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/balance", response_model=List[StockBalanceResponse])
@require_permission(Resources.GATE, PermissionActions.READ)
async def get_stock_balance_report(
    warehouse_id: Optional[int] = Query(None, description="Filter by warehouse"),
    part_id: Optional[int] = Query(None, description="Filter by part"),
    include_zero_stock: bool = Query(False, description="Include zero stock items"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Készletegyenleg riport - Stock balance report
    """
    try:
        inventory_service = InventoryService(db)
        report = inventory_service.get_stock_balance_report(
            warehouse_id=warehouse_id,
            part_id=part_id,
            include_zero_stock=include_zero_stock
        )
        
        return report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/movements", response_model=List[StockMovementResponse])
@require_permission(Resources.GATE, PermissionActions.READ)
async def get_stock_movement_report(
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    warehouse_id: Optional[int] = Query(None, description="Filter by warehouse"),
    part_id: Optional[int] = Query(None, description="Filter by part"),
    movement_type: Optional[str] = Query(None, description="Filter by movement type"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Készletmozgás riport - Stock movement report
    """
    try:
        inventory_service = InventoryService(db)
        report = inventory_service.get_stock_movement_report(
            start_date=start_date,
            end_date=end_date,
            warehouse_id=warehouse_id,
            part_id=part_id,
            movement_type=movement_type
        )
        
        return report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/alerts")
@require_permission(Resources.GATE, PermissionActions.READ)
async def get_stock_alerts(
    status: Optional[str] = Query(None, description="Filter by alert status"),
    alert_type: Optional[str] = Query(None, description="Filter by alert type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    warehouse_id: Optional[int] = Query(None, description="Filter by warehouse"),
    limit: int = Query(50, le=100, description="Maximum number of alerts"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Készletriasztások - Get stock alerts
    """
    try:
        query = db.query(StockAlert)\
            .join(InventoryItem)\
            .join(InventoryItem.part)\
            .join(InventoryItem.warehouse)
        
        if status:
            query = query.filter(StockAlert.status == status)
        
        if alert_type:
            query = query.filter(StockAlert.alert_type == alert_type)
        
        if severity:
            query = query.filter(StockAlert.severity == severity)
        
        if warehouse_id:
            query = query.filter(StockAlert.warehouse_id == warehouse_id)
        
        alerts = query.order_by(StockAlert.first_detected.desc()).limit(limit).all()
        
        result = []
        for alert in alerts:
            result.append({
                "id": alert.id,
                "alert_type": alert.alert_type,
                "status": alert.status,
                "severity": alert.severity,
                "warehouse_code": alert.warehouse.code,
                "warehouse_name": alert.warehouse.name,
                "part_code": alert.inventory_item.part.part_number,
                "part_name": alert.inventory_item.part.name,
                "current_quantity": float(alert.current_quantity),
                "threshold_quantity": float(alert.threshold_quantity),
                "shortage_quantity": float(alert.shortage_quantity) if alert.shortage_quantity else None,
                "first_detected": alert.first_detected,
                "last_updated": alert.last_updated,
                "message": alert.message,
                "action_required": alert.action_required,
                "priority": alert.priority
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/alerts/{alert_id}/acknowledge")
@require_permission(Resources.GATE, PermissionActions.UPDATE)
async def acknowledge_alert(
    alert_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Riasztás nyugtázása - Acknowledge stock alert
    """
    try:
        alert = db.query(StockAlert).get(alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.status = "acknowledged"
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = current_user.id
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Alert acknowledged successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/validation")
@require_permission(Resources.GATE, PermissionActions.READ)
async def validate_double_entry_balance(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Kettős könyvelés egyenleg ellenőrzése - Validate double-entry balance
    """
    try:
        inventory_service = InventoryService(db)
        validation_result = inventory_service.validate_double_entry_balance()
        
        return {
            "status": "success",
            "validation": validation_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/warehouses")
@require_permission(Resources.GATE, PermissionActions.READ)
async def get_warehouses(
    is_active: bool = Query(True, description="Filter by active status"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Raktárak listája - Get warehouses list
    """
    try:
        query = db.query(Warehouse)
        
        if is_active is not None:
            query = query.filter(Warehouse.is_active == is_active)
        
        warehouses = query.order_by(Warehouse.name).all()
        
        result = []
        for warehouse in warehouses:
            result.append({
                "id": warehouse.id,
                "code": warehouse.code,
                "name": warehouse.name,
                "description": warehouse.description,
                "warehouse_type": warehouse.warehouse_type,
                "is_active": warehouse.is_active,
                "address": {
                    "line_1": warehouse.address_line_1,
                    "line_2": warehouse.address_line_2,
                    "city": warehouse.city,
                    "state": warehouse.state,
                    "postal_code": warehouse.postal_code,
                    "country": warehouse.country
                },
                "contact": {
                    "manager_name": warehouse.manager_name,
                    "phone": warehouse.contact_phone,
                    "email": warehouse.contact_email
                }
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/items")
@require_permission(Resources.GATE, PermissionActions.READ)
async def get_inventory_items(
    warehouse_id: Optional[int] = Query(None, description="Filter by warehouse"),
    part_id: Optional[int] = Query(None, description="Filter by part"),
    low_stock_only: bool = Query(False, description="Show only low stock items"),
    limit: int = Query(100, le=500, description="Maximum number of items"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Készlet tételek listája - Get inventory items list
    """
    try:
        query = db.query(InventoryItem)\
            .join(InventoryItem.part)\
            .join(InventoryItem.warehouse)
        
        if warehouse_id:
            query = query.filter(InventoryItem.warehouse_id == warehouse_id)
        
        if part_id:
            query = query.filter(InventoryItem.part_id == part_id)
        
        if low_stock_only:
            query = query.filter(InventoryItem.quantity_available <= InventoryItem.minimum_stock)
        
        items = query.order_by(InventoryItem.part.has(name=True)).limit(limit).all()
        
        result = []
        for item in items:
            result.append({
                "id": item.id,
                "warehouse_id": item.warehouse_id,
                "warehouse_code": item.warehouse.code,
                "warehouse_name": item.warehouse.name,
                "part_id": item.part_id,
                "part_code": item.part.part_number,
                "part_name": item.part.name,
                "location_code": item.location_code,
                "zone": item.zone,
                "quantities": {
                    "on_hand": float(item.quantity_on_hand),
                    "reserved": float(item.quantity_reserved),
                    "available": float(item.quantity_available),
                    "on_order": float(item.quantity_on_order)
                },
                "thresholds": {
                    "minimum_stock": float(item.minimum_stock),
                    "maximum_stock": float(item.maximum_stock) if item.maximum_stock else None,
                    "reorder_point": float(item.reorder_point) if item.reorder_point else None,
                    "reorder_quantity": float(item.reorder_quantity) if item.reorder_quantity else None
                },
                "costs": {
                    "unit_cost": float(item.unit_cost) if item.unit_cost else None,
                    "average_cost": float(item.average_cost) if item.average_cost else None,
                    "last_cost": float(item.last_cost) if item.last_cost else None,
                    "total_value": float(item.total_value) if item.total_value else None
                },
                "dates": {
                    "last_received": item.last_received_date,
                    "last_issued": item.last_issued_date,
                    "last_counted": item.last_counted_date
                },
                "status": {
                    "stock_status": item.stock_status,
                    "needs_reorder": item.needs_reorder,
                    "is_active": item.is_active
                }
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")