"""
Audit Middleware
Automatikus audit naplózás middleware
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Callable, Dict, Any, Optional
import json
import time
from datetime import datetime

from app.database import get_db
from app.services.audit_service import AuditService
from app.models.audit_logs import AuditAction, AuditCategory, AuditSeverity, AuditResourceType
from app.core.deps import get_current_user_optional


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic audit logging of API requests
    Automatikus audit naplózás middleware API kérésekhez
    """
    
    def __init__(self, app):
        super().__init__(app)
        
        # Define which endpoints should be audited
        self.audit_paths = {
            # Gate operations
            "/api/gates": AuditResourceType.GATE,
            "/api/maintenance": AuditResourceType.MAINTENANCE,
            "/api/users": AuditResourceType.USER,
            "/api/auth": AuditResourceType.USER,
            
            # Add more paths as needed
        }
        
        # Define methods that should trigger audit logs
        self.audit_methods = {
            "POST": AuditAction.CREATE,
            "PUT": AuditAction.UPDATE,
            "PATCH": AuditAction.UPDATE,
            "DELETE": AuditAction.DELETE
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and potentially log audit entry"""
        
        start_time = time.time()
        
        # Check if this request should be audited
        should_audit = self._should_audit_request(request)
        
        # Store original body for audit purposes
        original_body = None
        if should_audit and request.method in self.audit_methods:
            try:
                body = await request.body()
                if body:
                    original_body = json.loads(body.decode('utf-8'))
            except:
                original_body = None
        
        # Process the request
        response = await call_next(request)
        
        # Log audit entry if needed
        if should_audit and response.status_code < 400:
            try:
                await self._log_audit_entry(request, response, original_body)
            except Exception as e:
                # Don't let audit logging break the main request
                print(f"Audit logging failed: {e}")
        
        # Add audit headers
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    def _should_audit_request(self, request: Request) -> bool:
        """Determine if a request should be audited"""
        
        # Skip health checks and static files
        if request.url.path in ["/health", "/metrics", "/favicon.ico"]:
            return False
        
        # Skip GET requests for read-only operations (optional)
        if request.method == "GET":
            return False
        
        # Check if path matches audit patterns
        for audit_path in self.audit_paths.keys():
            if request.url.path.startswith(audit_path):
                return True
        
        return False
    
    async def _log_audit_entry(
        self, 
        request: Request, 
        response: Response, 
        request_body: Optional[Dict[str, Any]]
    ):
        """Log an audit entry for the request"""
        
        # Get database session
        db = next(get_db())
        audit_service = AuditService(db)
        
        try:
            # Extract user info
            user_info = await self._get_user_info(request, db)
            
            # Determine resource type and action
            resource_type = self._get_resource_type(request.url.path)
            action = self.audit_methods.get(request.method, "UNKNOWN")
            
            # Extract resource ID from URL if possible
            resource_id = self._extract_resource_id(request.url.path)
            
            # Create description
            description = self._create_description(request, action, resource_type)
            
            # Determine category and severity
            category = self._determine_category(request.url.path, action)
            severity = self._determine_severity(action, response.status_code)
            
            # Log the audit entry
            audit_service.log_action(
                action=action,
                resource_type=resource_type,
                user_id=user_info.get("id"),
                user_email=user_info.get("email"),
                user_name=user_info.get("name"),
                resource_id=resource_id,
                description=description,
                new_values=request_body,
                organization_id=user_info.get("organization_id"),
                severity=severity,
                category=category,
                request=request
            )
            
        except Exception as e:
            print(f"Failed to log audit entry: {e}")
        
        finally:
            db.close()
    
    async def _get_user_info(self, request: Request, db: Session) -> Dict[str, Any]:
        """Extract user information from request"""
        try:
            user = await get_current_user_optional(request, db)
            if user:
                return {
                    "id": user.id,
                    "email": user.email,
                    "name": user.full_name,
                    "organization_id": user.organization_id
                }
        except:
            pass
        
        return {
            "id": None,
            "email": "anonymous",
            "name": "Anonymous User",
            "organization_id": None
        }
    
    def _get_resource_type(self, path: str) -> str:
        """Determine resource type from URL path"""
        for audit_path, resource_type in self.audit_paths.items():
            if path.startswith(audit_path):
                return resource_type
        
        # Default resource type based on path
        if "/gates" in path:
            return AuditResourceType.GATE
        elif "/users" in path:
            return AuditResourceType.USER
        elif "/maintenance" in path:
            return AuditResourceType.MAINTENANCE
        elif "/tickets" in path:
            return AuditResourceType.TICKET
        elif "/inventory" in path:
            return AuditResourceType.INVENTORY
        else:
            return "Unknown"
    
    def _extract_resource_id(self, path: str) -> Optional[str]:
        """Extract resource ID from URL path"""
        # Simple extraction for RESTful URLs like /api/gates/123
        path_parts = path.strip("/").split("/")
        
        # Look for numeric IDs in the path
        for part in reversed(path_parts):
            if part.isdigit():
                return part
        
        return None
    
    def _create_description(self, request: Request, action: str, resource_type: str) -> str:
        """Create human-readable description"""
        method = request.method
        path = request.url.path
        
        action_text = {
            AuditAction.CREATE: "created",
            AuditAction.UPDATE: "updated", 
            AuditAction.DELETE: "deleted"
        }.get(action, "performed action on")
        
        return f"User {action_text} {resource_type.lower()} via {method} {path}"
    
    def _determine_category(self, path: str, action: str) -> str:
        """Determine audit category based on path and action"""
        if "/auth" in path:
            return AuditCategory.SECURITY
        elif action in [AuditAction.CREATE, AuditAction.UPDATE, AuditAction.DELETE]:
            return AuditCategory.DATA
        else:
            return AuditCategory.BUSINESS
    
    def _determine_severity(self, action: str, status_code: int) -> str:
        """Determine severity based on action and response"""
        if status_code >= 500:
            return AuditSeverity.ERROR
        elif status_code >= 400:
            return AuditSeverity.WARNING
        elif action == AuditAction.DELETE:
            return AuditSeverity.WARNING
        else:
            return AuditSeverity.INFO


# Audit logging decorators for manual logging
class AuditLogger:
    """
    Decorator class for manual audit logging
    Dekorátor osztály manuális audit naplózáshoz
    """
    
    def __init__(self, db: Session):
        self.audit_service = AuditService(db)
    
    def log_gate_operation(
        self, 
        action: str, 
        gate_id: int, 
        gate_name: str,
        user_id: int,
        user_email: str,
        user_name: str,
        organization_id: int,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """Log gate-specific operations"""
        return self.audit_service.log_action(
            action=action,
            resource_type=AuditResourceType.GATE,
            user_id=user_id,
            user_email=user_email,
            user_name=user_name,
            resource_id=gate_id,
            resource_name=gate_name,
            description=f"Gate {action.lower()}: {gate_name}",
            new_values=additional_data,
            organization_id=organization_id,
            severity=AuditSeverity.INFO,
            category=AuditCategory.BUSINESS
        )
    
    def log_maintenance_operation(
        self,
        action: str,
        maintenance_id: int,
        gate_name: str,
        user_id: int,
        user_email: str,
        user_name: str,
        organization_id: int,
        old_data: Optional[Dict[str, Any]] = None,
        new_data: Optional[Dict[str, Any]] = None
    ):
        """Log maintenance-specific operations"""
        return self.audit_service.log_action(
            action=action,
            resource_type=AuditResourceType.MAINTENANCE,
            user_id=user_id,
            user_email=user_email,
            user_name=user_name,
            resource_id=maintenance_id,
            resource_name=f"Maintenance for {gate_name}",
            description=f"Maintenance {action.lower()} for gate: {gate_name}",
            old_values=old_data,
            new_values=new_data,
            organization_id=organization_id,
            severity=AuditSeverity.INFO,
            category=AuditCategory.BUSINESS
        )