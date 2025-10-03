"""
Audit Service
Audit log rendszer szolgáltatások
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timedelta
from fastapi import Request
import json
import difflib
import pandas as pd
import io

from app.models.audit_logs import (
    AuditLog, AuditAction, AuditCategory, AuditSeverity, AuditResourceType
)
from app.models.auth import User


class AuditService:
    """
    Audit logging service for tracking all significant changes
    Audit naplózási szolgáltatás minden lényeges változás követéséhez
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_action(
        self,
        action: str,
        entity_type: str,
        entity_id: Union[str, int],
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        description: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        organization_id: Optional[int] = None,
        risk_level: str = "LOW",
        success: bool = True,
        error_message: Optional[str] = None,
        request: Optional[Request] = None
    ) -> AuditLog:
        """
        Log an audit action
        Audit művelet naplózása
        """
        
        # Extract info from request if provided
        request_method = None
        request_path = None
        if request:
            if not ip_address:
                ip_address = self._get_client_ip(request)
            if not user_agent:
                user_agent = request.headers.get("user-agent")
            request_method = request.method
            request_path = str(request.url.path)
        
        # Calculate changed fields
        changed_fields = []
        if old_values and new_values:
            changed_fields = self._calculate_changed_fields(old_values, new_values)
        
        # Create audit log entry
        audit_log = AuditLog(
            user_id=user_id,
            username=username,
            timestamp=datetime.utcnow(),
            action=action,
            action_description=description,
            entity_type=entity_type,
            entity_id=int(entity_id) if str(entity_id).isdigit() else 0,
            old_values=old_values,
            new_values=new_values,
            changed_fields=changed_fields,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            request_method=request_method,
            request_path=request_path,
            organization_id=organization_id,
            success=success,
            error_message=error_message,
            risk_level=risk_level
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        return audit_log
    
    def log_create(
        self,
        entity_type: str,
        entity_id: Union[str, int],
        resource_data: Dict[str, Any],
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        organization_id: Optional[int] = None,
        request: Optional[Request] = None
    ) -> AuditLog:
        """Log create operation"""
        return self.log_action(
            action=AuditAction.CREATE,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            username=username,
            description=f"Created {entity_type.lower()} with ID: {entity_id}",
            new_values=resource_data,
            organization_id=organization_id,
            risk_level="LOW",
            request=request
        )
    
    def log_update(
        self,
        entity_type: str,
        entity_id: Union[str, int],
        old_data: Dict[str, Any],
        new_data: Dict[str, Any],
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        organization_id: Optional[int] = None,
        request: Optional[Request] = None
    ) -> AuditLog:
        """Log update operation"""
        changed_fields = self._calculate_changed_fields(old_data, new_data)
        
        return self.log_action(
            action=AuditAction.UPDATE,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            username=username,
            description=f"Updated {entity_type.lower()} ID {entity_id}. Fields: {', '.join(changed_fields)}",
            old_values=old_data,
            new_values=new_data,
            organization_id=organization_id,
            risk_level="LOW",
            request=request
        )
    
    def log_delete(
        self,
        entity_type: str,
        entity_id: Union[str, int],
        resource_data: Dict[str, Any],
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        organization_id: Optional[int] = None,
        request: Optional[Request] = None
    ) -> AuditLog:
        """Log delete operation"""
        return self.log_action(
            action=AuditAction.DELETE,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            username=username,
            description=f"Deleted {entity_type.lower()} with ID: {entity_id}",
            old_values=resource_data,
            organization_id=organization_id,
            risk_level="MEDIUM",
            request=request
        )
    
    def log_login(
        self,
        user_id: int,
        username: str,
        success: bool = True,
        organization_id: Optional[int] = None,
        error_message: Optional[str] = None,
        request: Optional[Request] = None
    ) -> AuditLog:
        """Log login attempt"""
        action = AuditAction.LOGIN if success else AuditAction.LOGIN_FAILED
        risk_level = "LOW" if success else "MEDIUM"
        
        return self.log_action(
            action=action,
            entity_type=AuditResourceType.USER,
            entity_id=user_id,
            user_id=user_id if success else None,
            username=username,
            description=f"{'Successful' if success else 'Failed'} login attempt for {username}",
            organization_id=organization_id,
            success=success,
            error_message=error_message,
            risk_level=risk_level,
            request=request
        )
    
    def get_audit_logs(
        self,
        organization_id: Optional[int] = None,
        user_id: Optional[int] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        action: Optional[str] = None,
        risk_level: Optional[str] = None,
        success: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        search_term: Optional[str] = None,
        page: int = 1,
        per_page: int = 50,
        sort_by: str = "timestamp",
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        """
        Get filtered audit logs with pagination
        Szűrt audit logok lekérdezése lapozással
        """
        
        query = self.db.query(AuditLog)
        
        # Apply filters
        if organization_id:
            query = query.filter(AuditLog.organization_id == organization_id)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        
        if entity_id:
            query = query.filter(AuditLog.entity_id == entity_id)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        if risk_level:
            query = query.filter(AuditLog.risk_level == risk_level)
        
        if success is not None:
            query = query.filter(AuditLog.success == success)
        
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        if search_term:
            search_filter = or_(
                AuditLog.action_description.ilike(f"%{search_term}%"),
                AuditLog.username.ilike(f"%{search_term}%"),
                AuditLog.entity_type.ilike(f"%{search_term}%"),
                AuditLog.ip_address.ilike(f"%{search_term}%"),
                AuditLog.request_path.ilike(f"%{search_term}%")
            )
            query = query.filter(search_filter)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply sorting
        sort_column = getattr(AuditLog, sort_by, AuditLog.timestamp)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Apply pagination
        offset = (page - 1) * per_page
        audit_logs = query.offset(offset).limit(per_page).all()
        
        return {
            "logs": [log.to_dict() for log in audit_logs],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page,
                "has_next": page * per_page < total,
                "has_prev": page > 1
            }
        }
    
    def get_audit_statistics(
        self,
        organization_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get audit statistics for dashboard
        Audit statisztikák dashboard-hoz
        """
        
        query = self.db.query(AuditLog)
        
        if organization_id:
            query = query.filter(AuditLog.organization_id == organization_id)
        
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        # Total logs
        total_logs = query.count()
        
        # By action
        by_action = self.db.query(
            AuditLog.action,
            func.count(AuditLog.id).label('count')
        ).filter(query.whereclause if hasattr(query, 'whereclause') else True)\
         .group_by(AuditLog.action)\
         .all()
        
        # By entity type
        by_entity_type = self.db.query(
            AuditLog.entity_type,
            func.count(AuditLog.id).label('count')
        ).filter(query.whereclause if hasattr(query, 'whereclause') else True)\
         .group_by(AuditLog.entity_type)\
         .all()
        
        # By risk level
        by_risk_level = self.db.query(
            AuditLog.risk_level,
            func.count(AuditLog.id).label('count')
        ).filter(query.whereclause if hasattr(query, 'whereclause') else True)\
         .group_by(AuditLog.risk_level)\
         .all()
        
        # By success status
        by_success = self.db.query(
            AuditLog.success,
            func.count(AuditLog.id).label('count')
        ).filter(query.whereclause if hasattr(query, 'whereclause') else True)\
         .group_by(AuditLog.success)\
         .all()
        
        # Top users
        top_users = self.db.query(
            AuditLog.username,
            func.count(AuditLog.id).label('count')
        ).filter(query.whereclause if hasattr(query, 'whereclause') else True)\
         .filter(AuditLog.username.isnot(None))\
         .group_by(AuditLog.username)\
         .order_by(desc('count'))\
         .limit(10)\
         .all()
        
        return {
            "total_logs": total_logs,
            "by_action": [{"action": action, "count": count} for action, count in by_action],
            "by_entity_type": [{"entity_type": entity_type, "count": count} for entity_type, count in by_entity_type],
            "by_risk_level": [{"risk_level": risk_level, "count": count} for risk_level, count in by_risk_level],
            "by_success": [{"success": success, "count": count} for success, count in by_success],
            "top_users": [
                {
                    "username": username,
                    "count": count
                }
                for username, count in top_users
            ]
        }
    
    def export_audit_logs_csv(
        self,
        organization_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        **filters
    ) -> bytes:
        """
        Export audit logs as CSV
        Audit logok CSV export
        """
        
        # Get all logs without pagination
        logs_data = self.get_audit_logs(
            organization_id=organization_id,
            start_date=start_date,
            end_date=end_date,
            per_page=10000,  # Large number to get all
            **filters
        )
        
        # Convert to DataFrame
        df = pd.DataFrame(logs_data["logs"])
        
        if df.empty:
            df = pd.DataFrame(columns=[
                "id", "timestamp", "username", "action", "action_description",
                "entity_type", "entity_id", "success", "risk_level", 
                "ip_address", "request_method", "request_path"
            ])
        else:
            # Select relevant columns for export
            df = df[[
                "id", "timestamp", "username", "action", "action_description",
                "entity_type", "entity_id", "success", "risk_level",
                "ip_address", "request_method", "request_path"
            ]]
        
        # Convert to CSV
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8')
        csv_data = output.getvalue().encode('utf-8-sig')  # BOM for Excel compatibility
        
        return csv_data
    
    def _get_client_ip(self, request: Request) -> Optional[str]:
        """Extract client IP from request"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to direct connection
        if hasattr(request, 'client') and request.client:
            return request.client.host
        
        return None
    
    def _calculate_changed_fields(
        self, 
        old_data: Dict[str, Any], 
        new_data: Dict[str, Any]
    ) -> List[str]:
        """Calculate which fields changed between old and new data"""
        changed = []
        
        all_keys = set(old_data.keys()) | set(new_data.keys())
        
        for key in all_keys:
            old_val = old_data.get(key)
            new_val = new_data.get(key)
            
            # Handle None values and type differences
            if old_val != new_val:
                changed.append(key)
        
        return changed