"""
Audit API Routes
Audit naplózási API végpontok
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import io

from app.database import get_db
from app.core.deps import get_current_active_user
from app.core.rbac import require_permission, PermissionActions, Resources
from app.models.auth import User
from app.services.audit_service import AuditService
from app.models.audit_logs import AuditLog, AuditAction, AuditCategory, AuditSeverity, AuditResourceType

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/logs")
@require_permission(Resources.SYSTEM, PermissionActions.READ)
async def get_audit_logs(
    organization_id: Optional[int] = Query(None, description="Filter by organization"),
    user_id: Optional[int] = Query(None, description="Filter by user"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[int] = Query(None, description="Filter by entity ID"),
    action: Optional[str] = Query(None, description="Filter by action"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    success: Optional[bool] = Query(None, description="Filter by success status"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    search_term: Optional[str] = Query(None, description="Search in description, user, resource name"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=1000, description="Items per page"),
    sort_by: str = Query("timestamp", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Audit logok lekérdezése szűrőkkel és lapozással
    Get audit logs with filters and pagination
    """
    try:
        audit_service = AuditService(db)
        
        # If not superuser, limit to own organization
        if not current_user.is_superuser:
            organization_id = current_user.organization_id
        
        result = audit_service.get_audit_logs(
            organization_id=organization_id,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            risk_level=risk_level,
            success=success,
            start_date=start_date,
            end_date=end_date,
            search_term=search_term,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return {
            "status": "success",
            "data": result,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit logs retrieval error: {str(e)}")


@router.get("/logs/{log_id}")
@require_permission(Resources.SYSTEM, PermissionActions.READ)
async def get_audit_log_detail(
    log_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Konkrét audit log részletes adatai
    Get detailed audit log entry
    """
    try:
        audit_service = AuditService(db)
        
        # Get the specific log entry
        audit_log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
        
        if not audit_log:
            raise HTTPException(status_code=404, detail="Audit log not found")
        
        # Check organization access
        if not current_user.is_superuser and audit_log.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied to this audit log")
        
        return {
            "status": "success",
            "data": audit_log.to_dict(),
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit log retrieval error: {str(e)}")


@router.get("/statistics")
@require_permission(Resources.SYSTEM, PermissionActions.READ)
async def get_audit_statistics(
    organization_id: Optional[int] = Query(None, description="Filter by organization"),
    days_back: int = Query(30, ge=1, le=365, description="Days back for statistics"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Audit statisztikák dashboard-hoz
    Get audit statistics for dashboard
    """
    try:
        audit_service = AuditService(db)
        
        # If not superuser, limit to own organization
        if not current_user.is_superuser:
            organization_id = current_user.organization_id
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        stats = audit_service.get_audit_statistics(
            organization_id=organization_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "status": "success",
            "data": stats,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days_back": days_back
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit statistics error: {str(e)}")


@router.get("/export/csv")
@require_permission(Resources.SYSTEM, PermissionActions.READ)
async def export_audit_logs_csv(
    organization_id: Optional[int] = Query(None, description="Filter by organization"),
    user_id: Optional[int] = Query(None, description="Filter by user"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    action: Optional[str] = Query(None, description="Filter by action"),
    category: Optional[str] = Query(None, description="Filter by category"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Audit logok CSV exportálása
    Export audit logs as CSV
    """
    try:
        audit_service = AuditService(db)
        
        # If not superuser, limit to own organization
        if not current_user.is_superuser:
            organization_id = current_user.organization_id
        
        csv_data = audit_service.export_audit_logs_csv(
            organization_id=organization_id,
            user_id=user_id,
            resource_type=resource_type,
            action=action,
            category=category,
            severity=severity,
            start_date=start_date,
            end_date=end_date
        )
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audit_logs_{timestamp}.csv"
        
        return StreamingResponse(
            io.BytesIO(csv_data),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit export error: {str(e)}")


@router.get("/search")
@require_permission(Resources.SYSTEM, PermissionActions.READ)
async def search_audit_logs(
    query: str = Query(..., description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Gyors keresés audit logokban
    Quick search in audit logs
    """
    try:
        audit_service = AuditService(db)
        
        # Determine organization filter
        organization_id = None if current_user.is_superuser else current_user.organization_id
        
        result = audit_service.get_audit_logs(
            organization_id=organization_id,
            search_term=query,
            per_page=limit,
            page=1
        )
        
        return {
            "status": "success",
            "query": query,
            "data": result["logs"],
            "total_found": result["pagination"]["total"],
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit search error: {str(e)}")


@router.get("/user-activity/{user_id}")
@require_permission(Resources.SYSTEM, PermissionActions.READ)
async def get_user_activity(
    user_id: int,
    days_back: int = Query(30, ge=1, le=365, description="Days back to analyze"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Konkrét felhasználó aktivitásának elemzése
    Analyze specific user's activity
    """
    try:
        audit_service = AuditService(db)
        
        # Check if user can access this user's data
        if not current_user.is_superuser:
            # Users can only see their own activity or users from same org
            target_user = db.query(User).filter(User.id == user_id).first()
            if not target_user:
                raise HTTPException(status_code=404, detail="User not found")
            
            if target_user.organization_id != current_user.organization_id and user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Access denied to this user's activity")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        result = audit_service.get_audit_logs(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            per_page=1000  # Get all activity for analysis
        )
        
        # Additional analysis
        logs = result["logs"]
        
        # Activity by action
        action_counts = {}
        for log in logs:
            action = log["action"]
            action_counts[action] = action_counts.get(action, 0) + 1
        
        # Activity by day
        daily_activity = {}
        for log in logs:
            day = log["timestamp"][:10]  # YYYY-MM-DD
            daily_activity[day] = daily_activity.get(day, 0) + 1
        
        # Most active resources
        resource_counts = {}
        for log in logs:
            resource = log["resource_type"]
            resource_counts[resource] = resource_counts.get(resource, 0) + 1
        
        return {
            "status": "success",
            "user_id": user_id,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days_back": days_back
            },
            "summary": {
                "total_actions": len(logs),
                "actions_by_type": action_counts,
                "daily_activity": daily_activity,
                "resources_accessed": resource_counts
            },
            "recent_logs": logs[:10],  # Most recent 10 actions
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User activity analysis error: {str(e)}")


# =============================================================================
# UTILITY ENDPOINTS - SEGÉDVÉGPONTOK
# =============================================================================

@router.get("/actions")
@require_permission(Resources.SYSTEM, PermissionActions.READ)
async def get_available_actions(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Elérhető audit akciók listája
    Get list of available audit actions
    """
    return {
        "status": "success",
        "data": {
            "actions": [
                AuditAction.CREATE, AuditAction.UPDATE, AuditAction.DELETE, AuditAction.VIEW,
                AuditAction.LOGIN, AuditAction.LOGOUT, AuditAction.LOGIN_FAILED,
                AuditAction.GATE_OPENED, AuditAction.GATE_CLOSED, AuditAction.GATE_MAINTENANCE,
                AuditAction.MAINTENANCE_SCHEDULED, AuditAction.MAINTENANCE_COMPLETED
            ],
            "categories": [
                AuditCategory.SECURITY, AuditCategory.DATA, AuditCategory.SYSTEM, 
                AuditCategory.BUSINESS, AuditCategory.INTEGRATION
            ],
            "severities": [
                AuditSeverity.DEBUG, AuditSeverity.INFO, AuditSeverity.WARNING,
                AuditSeverity.ERROR, AuditSeverity.CRITICAL
            ],
            "resource_types": [
                AuditResourceType.USER, AuditResourceType.GATE, AuditResourceType.MAINTENANCE,
                AuditResourceType.TICKET, AuditResourceType.ORGANIZATION
            ]
        }
    }


@router.post("/manual-log")
@require_permission(Resources.SYSTEM, PermissionActions.CREATE)
async def create_manual_audit_log(
    action: str,
    resource_type: str,
    description: str,
    resource_id: Optional[str] = None,
    resource_name: Optional[str] = None,
    category: str = AuditCategory.BUSINESS,
    severity: str = AuditSeverity.INFO,
    additional_data: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Manuális audit log bejegyzés létrehozása
    Create manual audit log entry
    """
    try:
        audit_service = AuditService(db)
        
        audit_log = audit_service.log_action(
            action=action,
            resource_type=resource_type,
            user_id=current_user.id,
            user_email=current_user.email,
            user_name=current_user.full_name,
            resource_id=resource_id,
            resource_name=resource_name,
            description=description,
            new_values=additional_data,
            organization_id=current_user.organization_id,
            category=category,
            severity=severity
        )
        
        return {
            "status": "success",
            "message": "Manual audit log created successfully",
            "data": audit_log.to_dict(),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Manual audit log creation error: {str(e)}")