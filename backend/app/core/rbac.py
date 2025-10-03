"""Role-Based Access Control (RBAC) system with permission decorators."""

from functools import wraps
from typing import List, Optional, Union, Callable, Any
from enum import Enum
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import and_
import structlog

from app.database import get_db
from app.models.auth import User, Role, Permission, RoleAssignment
from app.schemas.auth import TokenData
from app.core.security import verify_token

logger = structlog.get_logger(__name__)

# Security scheme for FastAPI
security = HTTPBearer()


# Aliases for backward compatibility
class Roles:
    """Role constants for backward compatibility."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    TECHNICIAN = "technician"
    CLIENT = "client"
    AUDITOR = "auditor"


class RBACPermission(str, Enum):
    """RBAC permission enumeration for decorators."""
    # Users and organization
    MANAGE_USERS = "user:manage"
    VIEW_USERS = "user:read"
    MANAGE_ORGANIZATION = "organization:manage"
    VIEW_ORGANIZATION = "organization:read"
    
    # Structural entities
    MANAGE_CLIENTS = "client:manage"
    VIEW_CLIENTS = "client:read"
    MANAGE_SITES = "site:manage"
    VIEW_SITES = "site:read"
    MANAGE_BUILDINGS = "building:manage"
    VIEW_BUILDINGS = "building:read"
    MANAGE_GATES = "gate:manage"
    VIEW_GATES = "gate:read"
    
    # Maintenance
    MANAGE_MAINTENANCE = "maintenance:manage"
    VIEW_MAINTENANCE = "maintenance:read"
    MANAGE_WORK_ORDERS = "work_order:manage"
    VIEW_WORK_ORDERS = "work_order:read"
    
    # Tickets and inspections
    MANAGE_TICKETS = "ticket:manage"
    VIEW_TICKETS = "ticket:read"
    MANAGE_INSPECTIONS = "inspection:manage"
    VIEW_INSPECTIONS = "inspection:read"
    
    # Inventory
    MANAGE_INVENTORY = "inventory:manage"
    VIEW_INVENTORY = "inventory:read"
    
    # Documents and reports
    MANAGE_DOCUMENTS = "document:manage"
    VIEW_DOCUMENTS = "document:read"
    VIEW_REPORTS = "report:read"
    
    # System administration
    VIEW_AUDIT_LOGS = "audit_log:read"
    MANAGE_INTEGRATIONS = "integration:manage"


class Permissions:
    """Permission constants organized by resource."""
    
    class GATE:
        READ = "gate:read"
        CREATE = "gate:create"
        UPDATE = "gate:update"
        DELETE = "gate:delete"
        
    class MAINTENANCE:
        READ = "maintenance:read"
        CREATE = "maintenance:create"
        UPDATE = "maintenance:update"
        DELETE = "maintenance:delete"
        
    class USER:
        READ = "user:read"
        CREATE = "user:create"
        UPDATE = "user:update"
        DELETE = "user:delete"


class RoleNames(str, Enum):
    """Standard role names."""
    SUPER_ADMIN = "super_admin"      # Full system access
    ADMIN = "admin"                  # Organization admin
    MANAGER = "manager"              # Site/building manager
    TECHNICIAN = "technician"        # Field technician/maintenance
    CLIENT = "client"                # Customer/client access
    AUDITOR = "auditor"             # Read-only access for auditing
    

class PermissionActions(str, Enum):
    """Permission action types."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    APPROVE = "approve"
    ADMIN = "admin"


class Resources(str, Enum):
    """System resources that can be protected."""
    # Core entities
    ORGANIZATION = "organization"
    USER = "user"
    ROLE = "role"
    
    # Business entities
    CLIENT = "client"
    SITE = "site" 
    BUILDING = "building"
    GATE = "gate"
    COMPONENT = "component"
    
    # Maintenance
    MAINTENANCE_PLAN = "maintenance_plan"
    MAINTENANCE_JOB = "maintenance_job"
    WORK_ORDER = "work_order"
    TICKET = "ticket"
    
    # Quality
    INSPECTION = "inspection"
    CHECKLIST = "checklist"
    MEASUREMENT = "measurement"
    
    # Inventory
    INVENTORY = "inventory"
    PART = "part"
    WAREHOUSE = "warehouse"
    
    # Documents
    DOCUMENT = "document"
    MEDIA = "media"
    
    # System
    AUDIT_LOG = "audit_log"
    REPORT = "report"
    INTEGRATION = "integration"
    SYNC = "sync"


def permission_required(
    resource: Resources,
    action: PermissionActions,
    scope_type: Optional[str] = None,
    scope_field: Optional[str] = None
):
    """
    Decorator for endpoint permission checking.
    
    Args:
        resource: Resource being accessed
        action: Action being performed
        scope_type: Scope type for permission (organization, site, etc.)
        scope_field: Field name in request data for scope checking
        
    Usage:
        @permission_required(Resources.GATE, PermissionActions.CREATE)
        async def create_gate(gate_data: GateCreate, user: TokenData = Depends(get_current_user)):
            # Only users with gate:create permission can access this
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from dependencies
            current_user = None
            for arg in args:
                if isinstance(arg, TokenData):
                    current_user = arg
                    break
            
            # Check if user found in kwargs
            if not current_user:
                current_user = kwargs.get('current_user') or kwargs.get('user')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check permission
            permission_name = f"{resource.value}:{action.value}"
            if permission_name not in current_user.permissions:
                logger.warning(
                    "Permission denied",
                    user_id=current_user.user_id,
                    required_permission=permission_name,
                    user_permissions=current_user.permissions
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission_name}"
                )
            
            # TODO: Implement scope checking if needed
            # This would check if user has permission for specific organization/site/etc.
            
            logger.debug(
                "Permission granted",
                user_id=current_user.user_id,
                permission=permission_name
            )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def role_required(roles: Union[RoleNames, List[RoleNames]]):
    """
    Decorator for role-based access control.
    
    Args:
        roles: Required role(s) - single role or list of roles
        
    Usage:
        @role_required([RoleNames.ADMIN, RoleNames.MANAGER])
        async def admin_endpoint():
            # Only admins and managers can access
            pass
    """
    if isinstance(roles, RoleNames):
        roles = [roles]
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from dependencies
            current_user = None
            for arg in args:
                if isinstance(arg, TokenData):
                    current_user = arg
                    break
            
            if not current_user:
                current_user = kwargs.get('current_user') or kwargs.get('user')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Get user roles from database
            db = kwargs.get('db')
            if not db:
                # Try to get from function signature
                for param_name, param_value in kwargs.items():
                    if isinstance(param_value, Session):
                        db = param_value
                        break
            
            if not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database session not available"
                )
            
            user_roles = await get_user_roles(db, current_user.user_id)
            
            # Check if user has required role
            has_required_role = any(role.value in user_roles for role in roles)
            
            if not has_required_role:
                logger.warning(
                    "Role access denied",
                    user_id=current_user.user_id,
                    required_roles=[role.value for role in roles],
                    user_roles=user_roles
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires one of roles: {[role.value for role in roles]}"
                )
            
            logger.debug(
                "Role access granted",
                user_id=current_user.user_id,
                user_roles=user_roles
            )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> TokenData:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
        db: Database session
        
    Returns:
        Current user token data
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    
    # Verify token
    payload = verify_token(token, token_type="access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database to ensure they're still active
    user = db.query(User).filter(
        and_(User.id == user_id, User.is_deleted == False, User.is_active == True)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get current permissions
    permissions = await get_user_permissions(db, user.id)
    
    return TokenData(
        user_id=user.id,
        username=payload.get("username"),
        org_id=payload.get("org_id"),
        permissions=permissions,
        token_type="access"
    )


async def get_current_active_user(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current active user object.
    
    Args:
        current_user: Current user token data
        db: Database session
        
    Returns:
        Current active user object
    """
    user = db.query(User).filter(User.id == current_user.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return user


async def get_current_superuser(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TokenData:
    """
    Dependency that requires superuser access.
    
    Args:
        current_user: Current user token data
        db: Database session
        
    Returns:
        Current user if they are superuser
    """
    user_roles = await get_user_roles(db, current_user.user_id)
    
    if RoleNames.SUPER_ADMIN.value not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser access required"
        )
    
    return current_user


async def get_user_roles(db: Session, user_id: int) -> List[str]:
    """
    Get all roles for a user.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        List of role names
    """
    roles = db.query(Role.name).join(
        RoleAssignment, RoleAssignment.role_id == Role.id
    ).filter(
        and_(
            RoleAssignment.user_id == user_id,
            RoleAssignment.is_active == True,
            RoleAssignment.is_deleted == False
        )
    ).all()
    
    return [role.name for role in roles]


async def get_user_permissions(db: Session, user_id: int) -> List[str]:
    """
    Get all permissions for a user through their roles.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        List of permission codenames
    """
    permissions = db.query(Permission.codename).join(
        Role.permissions
    ).join(
        RoleAssignment, RoleAssignment.role_id == Role.id
    ).filter(
        and_(
            RoleAssignment.user_id == user_id,
            RoleAssignment.is_active == True,
            RoleAssignment.is_deleted == False
        )
    ).distinct().all()
    
    return [perm.codename for perm in permissions]


async def has_permission(
    db: Session,
    user_id: int,
    resource: Resources,
    action: PermissionActions,
    scope_type: Optional[str] = None,
    scope_id: Optional[int] = None
) -> bool:
    """
    Check if user has specific permission.
    
    Args:
        db: Database session
        user_id: User ID
        resource: Resource type
        action: Action type
        scope_type: Optional scope type (organization, site, etc.)
        scope_id: Optional scope ID
        
    Returns:
        True if user has permission
    """
    permission_name = f"{resource.value}:{action.value}"
    user_permissions = await get_user_permissions(db, user_id)
    
    # Basic permission check
    if permission_name not in user_permissions:
        return False
    
    # TODO: Implement scope-based permission checking
    # This would check if the user has permission for the specific scope
    # For example, checking if user can modify gates only in their assigned sites
    
    return True


def require_permissions(required_permissions: List[RBACPermission]):
    """
    Decorator that requires specific permissions.
    
    Args:
        required_permissions: List of required RBAC permissions
        
    Usage:
        @require_permissions([RBACPermission.MANAGE_GATES])
        async def create_gate(gate_data: GateCreate, current_user: User = Depends(get_current_active_user)):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Get database session
            db = kwargs.get('db')
            if not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database session not available"
                )
            
            # Get user permissions
            user_permissions = await get_user_permissions(db, current_user.id)
            
            # Check if user has all required permissions
            missing_permissions = []
            for perm in required_permissions:
                if perm.value not in user_permissions:
                    missing_permissions.append(perm.value)
            
            if missing_permissions:
                logger.warning(
                    "Permission denied",
                    user_id=current_user.id,
                    required_permissions=[p.value for p in required_permissions],
                    missing_permissions=missing_permissions,
                    user_permissions=user_permissions
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permissions: {', '.join(missing_permissions)}"
                )
            
            logger.debug(
                "Permission granted",
                user_id=current_user.id,
                required_permissions=[p.value for p in required_permissions]
            )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def create_permission(resource: Resources, action: PermissionActions) -> str:
    """
    Create permission string from resource and action.
    
    Args:
        resource: Resource type
        action: Action type
        
    Returns:
        Permission codename
    """
    return f"{resource.value}:{action.value}"


# Standard permission sets for common roles
ROLE_PERMISSIONS = {
    RoleNames.SUPER_ADMIN: [
        # Full system access - all permissions
        create_permission(resource, action)
        for resource in Resources
        for action in PermissionActions
    ],
    
    RoleNames.ADMIN: [
        # Organization-level admin permissions - using both new and legacy
        RBACPermission.MANAGE_USERS.value,
        RBACPermission.VIEW_USERS.value,
        RBACPermission.MANAGE_CLIENTS.value,
        RBACPermission.VIEW_CLIENTS.value,
        RBACPermission.MANAGE_SITES.value,
        RBACPermission.VIEW_SITES.value,
        RBACPermission.MANAGE_BUILDINGS.value,
        RBACPermission.VIEW_BUILDINGS.value,
        RBACPermission.MANAGE_GATES.value,
        RBACPermission.VIEW_GATES.value,
        RBACPermission.VIEW_REPORTS.value,
        RBACPermission.VIEW_AUDIT_LOGS.value,
        # Legacy permissions for compatibility
        create_permission(Resources.USER, PermissionActions.CREATE),
        create_permission(Resources.USER, PermissionActions.READ),
        create_permission(Resources.USER, PermissionActions.UPDATE),
        create_permission(Resources.ROLE, PermissionActions.READ),
        create_permission(Resources.CLIENT, PermissionActions.CREATE),
        create_permission(Resources.CLIENT, PermissionActions.READ),
        create_permission(Resources.CLIENT, PermissionActions.UPDATE),
        create_permission(Resources.SITE, PermissionActions.CREATE),
        create_permission(Resources.SITE, PermissionActions.READ),
        create_permission(Resources.SITE, PermissionActions.UPDATE),
        create_permission(Resources.BUILDING, PermissionActions.CREATE),
        create_permission(Resources.BUILDING, PermissionActions.READ),
        create_permission(Resources.BUILDING, PermissionActions.UPDATE),
        create_permission(Resources.GATE, PermissionActions.CREATE),
        create_permission(Resources.GATE, PermissionActions.READ),
        create_permission(Resources.GATE, PermissionActions.UPDATE),
        create_permission(Resources.REPORT, PermissionActions.READ),
        create_permission(Resources.AUDIT_LOG, PermissionActions.READ),
    ],
    
    RoleNames.MANAGER: [
        # Site/building manager permissions
        create_permission(Resources.SITE, PermissionActions.READ),
        create_permission(Resources.BUILDING, PermissionActions.READ),
        create_permission(Resources.BUILDING, PermissionActions.UPDATE),
        create_permission(Resources.GATE, PermissionActions.READ),
        create_permission(Resources.GATE, PermissionActions.UPDATE),
        create_permission(Resources.MAINTENANCE_PLAN, PermissionActions.CREATE),
        create_permission(Resources.MAINTENANCE_PLAN, PermissionActions.READ),
        create_permission(Resources.MAINTENANCE_PLAN, PermissionActions.UPDATE),
        create_permission(Resources.MAINTENANCE_JOB, PermissionActions.READ),
        create_permission(Resources.MAINTENANCE_JOB, PermissionActions.APPROVE),
        create_permission(Resources.WORK_ORDER, PermissionActions.CREATE),
        create_permission(Resources.WORK_ORDER, PermissionActions.READ),
        create_permission(Resources.WORK_ORDER, PermissionActions.UPDATE),
        create_permission(Resources.TICKET, PermissionActions.READ),
        create_permission(Resources.TICKET, PermissionActions.UPDATE),
        create_permission(Resources.INSPECTION, PermissionActions.READ),
        create_permission(Resources.REPORT, PermissionActions.READ),
    ],
    
    RoleNames.TECHNICIAN: [
        # Field technician permissions
        create_permission(Resources.GATE, PermissionActions.READ),
        create_permission(Resources.COMPONENT, PermissionActions.READ),
        create_permission(Resources.COMPONENT, PermissionActions.UPDATE),
        create_permission(Resources.MAINTENANCE_JOB, PermissionActions.READ),
        create_permission(Resources.MAINTENANCE_JOB, PermissionActions.UPDATE),
        create_permission(Resources.WORK_ORDER, PermissionActions.READ),
        create_permission(Resources.WORK_ORDER, PermissionActions.UPDATE),
        create_permission(Resources.TICKET, PermissionActions.CREATE),
        create_permission(Resources.TICKET, PermissionActions.READ),
        create_permission(Resources.TICKET, PermissionActions.UPDATE),
        create_permission(Resources.INSPECTION, PermissionActions.CREATE),
        create_permission(Resources.INSPECTION, PermissionActions.READ),
        create_permission(Resources.INSPECTION, PermissionActions.UPDATE),
        create_permission(Resources.MEASUREMENT, PermissionActions.CREATE),
        create_permission(Resources.MEASUREMENT, PermissionActions.READ),
        create_permission(Resources.PART, PermissionActions.READ),
        create_permission(Resources.INVENTORY, PermissionActions.READ),
        create_permission(Resources.INVENTORY, PermissionActions.UPDATE),
        create_permission(Resources.DOCUMENT, PermissionActions.CREATE),
        create_permission(Resources.DOCUMENT, PermissionActions.READ),
        create_permission(Resources.MEDIA, PermissionActions.CREATE),
        create_permission(Resources.MEDIA, PermissionActions.READ),
    ],
    
    RoleNames.CLIENT: [
        # Customer/client read-only access
        create_permission(Resources.GATE, PermissionActions.READ),
        create_permission(Resources.MAINTENANCE_JOB, PermissionActions.READ),
        create_permission(Resources.WORK_ORDER, PermissionActions.READ),
        create_permission(Resources.TICKET, PermissionActions.CREATE),
        create_permission(Resources.TICKET, PermissionActions.READ),
        create_permission(Resources.INSPECTION, PermissionActions.READ),
        create_permission(Resources.DOCUMENT, PermissionActions.READ),
        create_permission(Resources.REPORT, PermissionActions.READ),
    ],
    
    RoleNames.AUDITOR: [
        # Read-only access for auditing
        create_permission(Resources.USER, PermissionActions.READ),
        create_permission(Resources.ORGANIZATION, PermissionActions.READ),
        create_permission(Resources.CLIENT, PermissionActions.READ),
        create_permission(Resources.SITE, PermissionActions.READ),
        create_permission(Resources.BUILDING, PermissionActions.READ),
        create_permission(Resources.GATE, PermissionActions.READ),
        create_permission(Resources.COMPONENT, PermissionActions.READ),
        create_permission(Resources.MAINTENANCE_PLAN, PermissionActions.READ),
        create_permission(Resources.MAINTENANCE_JOB, PermissionActions.READ),
        create_permission(Resources.WORK_ORDER, PermissionActions.READ),
        create_permission(Resources.TICKET, PermissionActions.READ),
        create_permission(Resources.INSPECTION, PermissionActions.READ),
        create_permission(Resources.MEASUREMENT, PermissionActions.READ),
        create_permission(Resources.INVENTORY, PermissionActions.READ),
        create_permission(Resources.PART, PermissionActions.READ),
        create_permission(Resources.DOCUMENT, PermissionActions.READ),
        create_permission(Resources.MEDIA, PermissionActions.READ),
        create_permission(Resources.AUDIT_LOG, PermissionActions.READ),
        create_permission(Resources.REPORT, PermissionActions.READ),
    ]
}


def check_permission(permission_string: str, current_user, db=None) -> bool:
    """
    Check if current user has a specific permission.
    
    Args:
        permission_string: Permission string like "checklist:write"
        current_user: Current authenticated user
        db: Database session (optional, for future use)
        
    Returns:
        True if user has permission, False otherwise
    """
    # For now, return True for development
    # TODO: Implement proper permission checking
    return True


def require_permission(permission_string: str, current_user, db=None):
    """
    Check permission and raise exception if not authorized.
    
    Args:
        permission_string: Permission string like "checklist:write"
        current_user: Current authenticated user
        db: Database session (optional)
        
    Raises:
        HTTPException: If user doesn't have permission
    """
    if not check_permission(permission_string, current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions: {permission_string} required"
        )