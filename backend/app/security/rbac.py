"""
Role-Based Access Control (RBAC) System
Implements comprehensive authorization matrix and permission management
"""

from enum import Enum
from typing import Dict, List, Set, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
from functools import wraps

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import redis.asyncio as redis
import structlog

logger = structlog.get_logger(__name__)

# Permission Definitions
class Permission(Enum):
    """System permissions enumeration"""
    
    # User Management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_LIST = "user:list"
    
    # Vehicle Management  
    VEHICLE_CREATE = "vehicle:create"
    VEHICLE_READ = "vehicle:read"
    VEHICLE_UPDATE = "vehicle:update"
    VEHICLE_DELETE = "vehicle:delete"
    VEHICLE_LIST = "vehicle:list"
    
    # Maintenance Management
    MAINTENANCE_CREATE = "maintenance:create"
    MAINTENANCE_READ = "maintenance:read"
    MAINTENANCE_UPDATE = "maintenance:update"
    MAINTENANCE_DELETE = "maintenance:delete"
    MAINTENANCE_LIST = "maintenance:list"
    
    # Inventory Management
    INVENTORY_CREATE = "inventory:create"
    INVENTORY_READ = "inventory:read"
    INVENTORY_UPDATE = "inventory:update"
    INVENTORY_DELETE = "inventory:delete"
    INVENTORY_LIST = "inventory:list"
    
    # Report Access
    REPORT_VIEW = "report:view"
    REPORT_CREATE = "report:create"
    REPORT_EXPORT = "report:export"
    
    # Admin Functions
    ADMIN_USERS = "admin:users"
    ADMIN_ROLES = "admin:roles"
    ADMIN_SYSTEM = "admin:system"
    ADMIN_AUDIT = "admin:audit"
    ADMIN_BACKUP = "admin:backup"
    
    # Organization Management
    ORG_CREATE = "org:create"
    ORG_READ = "org:read"
    ORG_UPDATE = "org:update"
    ORG_DELETE = "org:delete"
    ORG_MANAGE_USERS = "org:manage_users"
    
    # Special Permissions
    SYSTEM_MAINTENANCE = "system:maintenance"
    API_ACCESS = "api:access"
    BULK_OPERATIONS = "bulk:operations"

class Role(Enum):
    """System roles enumeration"""
    
    SUPER_ADMIN = "super_admin"
    ORG_ADMIN = "org_admin" 
    MANAGER = "manager"
    MECHANIC = "mechanic"
    OPERATOR = "operator"
    VIEWER = "viewer"
    API_CLIENT = "api_client"

@dataclass
class RoleDefinition:
    """Role definition with permissions and constraints"""
    
    name: str
    display_name: str
    description: str
    permissions: Set[Permission] = field(default_factory=set)
    inherits_from: Optional['RoleDefinition'] = None
    is_system_role: bool = False
    max_users: Optional[int] = None
    requires_approval: bool = False
    auto_expire_days: Optional[int] = None

@dataclass 
class UserPermissions:
    """User's effective permissions"""
    
    user_id: str
    organization_id: Optional[str]
    roles: Set[str] = field(default_factory=set)
    permissions: Set[Permission] = field(default_factory=set)
    restrictions: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)

class AuthorizationMatrix:
    """Authorization matrix defining role permissions"""
    
    def __init__(self):
        self.role_definitions: Dict[str, RoleDefinition] = {}
        self._initialize_default_roles()
    
    def _initialize_default_roles(self):
        """Initialize default system roles"""
        
        # Super Admin - Full system access
        self.role_definitions[Role.SUPER_ADMIN.value] = RoleDefinition(
            name=Role.SUPER_ADMIN.value,
            display_name="Super Administrator",
            description="Full system access across all organizations",
            permissions=set(Permission),  # All permissions
            is_system_role=True,
            max_users=5,
            requires_approval=True
        )
        
        # Organization Admin - Full access within organization
        org_admin_permissions = {
            Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE, Permission.USER_DELETE, Permission.USER_LIST,
            Permission.VEHICLE_CREATE, Permission.VEHICLE_READ, Permission.VEHICLE_UPDATE, Permission.VEHICLE_DELETE, Permission.VEHICLE_LIST,
            Permission.MAINTENANCE_CREATE, Permission.MAINTENANCE_READ, Permission.MAINTENANCE_UPDATE, Permission.MAINTENANCE_DELETE, Permission.MAINTENANCE_LIST,
            Permission.INVENTORY_CREATE, Permission.INVENTORY_READ, Permission.INVENTORY_UPDATE, Permission.INVENTORY_DELETE, Permission.INVENTORY_LIST,
            Permission.REPORT_VIEW, Permission.REPORT_CREATE, Permission.REPORT_EXPORT,
            Permission.ADMIN_USERS, Permission.ADMIN_ROLES, Permission.ADMIN_AUDIT,
            Permission.ORG_READ, Permission.ORG_UPDATE, Permission.ORG_MANAGE_USERS,
            Permission.API_ACCESS, Permission.BULK_OPERATIONS
        }
        
        self.role_definitions[Role.ORG_ADMIN.value] = RoleDefinition(
            name=Role.ORG_ADMIN.value,
            display_name="Organization Administrator", 
            description="Full administrative access within organization",
            permissions=org_admin_permissions,
            requires_approval=True
        )
        
        # Manager - Management level access
        manager_permissions = {
            Permission.USER_READ, Permission.USER_LIST,
            Permission.VEHICLE_CREATE, Permission.VEHICLE_READ, Permission.VEHICLE_UPDATE, Permission.VEHICLE_LIST,
            Permission.MAINTENANCE_CREATE, Permission.MAINTENANCE_READ, Permission.MAINTENANCE_UPDATE, Permission.MAINTENANCE_LIST,
            Permission.INVENTORY_READ, Permission.INVENTORY_UPDATE, Permission.INVENTORY_LIST,
            Permission.REPORT_VIEW, Permission.REPORT_CREATE, Permission.REPORT_EXPORT,
            Permission.API_ACCESS
        }
        
        self.role_definitions[Role.MANAGER.value] = RoleDefinition(
            name=Role.MANAGER.value,
            display_name="Manager",
            description="Management level access to vehicles and maintenance",
            permissions=manager_permissions
        )
        
        # Mechanic - Maintenance focused access
        mechanic_permissions = {
            Permission.VEHICLE_READ, Permission.VEHICLE_LIST,
            Permission.MAINTENANCE_CREATE, Permission.MAINTENANCE_READ, Permission.MAINTENANCE_UPDATE, Permission.MAINTENANCE_LIST,
            Permission.INVENTORY_READ, Permission.INVENTORY_LIST,
            Permission.REPORT_VIEW
        }
        
        self.role_definitions[Role.MECHANIC.value] = RoleDefinition(
            name=Role.MECHANIC.value,
            display_name="Mechanic",
            description="Maintenance and repair focused access",
            permissions=mechanic_permissions
        )
        
        # Operator - Basic operational access
        operator_permissions = {
            Permission.VEHICLE_READ, Permission.VEHICLE_LIST,
            Permission.MAINTENANCE_READ, Permission.MAINTENANCE_LIST,
            Permission.INVENTORY_READ, Permission.INVENTORY_LIST,
            Permission.REPORT_VIEW
        }
        
        self.role_definitions[Role.OPERATOR.value] = RoleDefinition(
            name=Role.OPERATOR.value,
            display_name="Operator",
            description="Basic operational access for daily tasks",
            permissions=operator_permissions
        )

    def generate_authorization_matrix(self) -> Dict[str, Dict[str, bool]]:
        """Generate authorization matrix showing role-permission mapping"""
        matrix = {}
        
        for role_name, role_def in self.role_definitions.items():
            matrix[role_name] = {}
            for permission in Permission:
                matrix[role_name][permission.value] = permission in role_def.permissions
                
        return matrix
    
    def print_authorization_matrix(self) -> str:
        """Generate human-readable authorization matrix"""
        matrix = self.generate_authorization_matrix()
        
        output = ["\\n🔐 JOGOSULTSÁGI MÁTRIX (AUTHORIZATION MATRIX)"]
        output.append("=" * 80)
        
        # Header
        roles = list(self.role_definitions.keys())
        header = f"{'Permission':<30}"
        for role in roles:
            header += f"{role:<15}"
        output.append(header)
        output.append("-" * 80)
        
        # Permission rows
        for permission in Permission:
            row = f"{permission.value:<30}"
            for role in roles:
                has_permission = matrix[role][permission.value]
                symbol = "✅" if has_permission else "❌"
                row += f"{symbol:<15}"
            output.append(row)
            
        return "\\n".join(output)
    
    async def permission_check(
        self, 
        user_id: str, 
        permission: Union[Permission, str], 
        resource_id: Optional[str] = None
    ) -> bool:
        """Check if user has specific permission"""
        try:
            # Get user roles from cache or database
            user_roles = await self.get_user_roles(user_id)
            
            # Convert string permission to enum
            if isinstance(permission, str):
                try:
                    permission = Permission(permission)
                except ValueError:
                    logger.warning("Invalid permission", permission=permission)
                    return False
            
            # Check if any user role has the required permission
            for role_name in user_roles:
                role_def = self.role_definitions.get(role_name)
                if role_def and permission in role_def.permissions:
                    logger.debug("Permission granted", 
                               user_id=user_id, 
                               permission=permission.value, 
                               role=role_name)
                    return True
            
            logger.info("Permission denied", 
                       user_id=user_id, 
                       permission=permission.value, 
                       roles=user_roles)
            return False
            
        except Exception as e:
            logger.error("Permission check failed", 
                        user_id=user_id, 
                        permission=permission, 
                        error=str(e))
            return False
        
        # Viewer - Read-only access
        viewer_permissions = {
            Permission.VEHICLE_READ, Permission.VEHICLE_LIST,
            Permission.MAINTENANCE_READ, Permission.MAINTENANCE_LIST,
            Permission.INVENTORY_READ, Permission.INVENTORY_LIST,
            Permission.REPORT_VIEW
        }
        
        self.role_definitions[Role.VIEWER.value] = RoleDefinition(
            name=Role.VIEWER.value,
            display_name="Viewer",
            description="Read-only access to system data",
            permissions=viewer_permissions,
            auto_expire_days=90
        )
        
        # API Client - Programmatic access
        api_permissions = {
            Permission.VEHICLE_READ, Permission.VEHICLE_LIST, Permission.VEHICLE_CREATE, Permission.VEHICLE_UPDATE,
            Permission.MAINTENANCE_READ, Permission.MAINTENANCE_LIST, Permission.MAINTENANCE_CREATE,
            Permission.API_ACCESS
        }
        
        self.role_definitions[Role.API_CLIENT.value] = RoleDefinition(
            name=Role.API_CLIENT.value,
            display_name="API Client",
            description="Programmatic API access",
            permissions=api_permissions,
            is_system_role=True,
            auto_expire_days=365
        )
    
    def get_role_permissions(self, role_name: str) -> Set[Permission]:
        """Get all permissions for a role including inherited ones"""
        role_def = self.role_definitions.get(role_name)
        if not role_def:
            return set()
        
        permissions = role_def.permissions.copy()
        
        # Add inherited permissions
        if role_def.inherits_from:
            inherited_permissions = self.get_role_permissions(role_def.inherits_from.name)
            permissions.update(inherited_permissions)
        
        return permissions
    
    def get_user_permissions(self, roles: Set[str]) -> Set[Permission]:
        """Get combined permissions for multiple roles"""
        all_permissions = set()
        
        for role_name in roles:
            role_permissions = self.get_role_permissions(role_name)
            all_permissions.update(role_permissions)
        
        return all_permissions
    
    def can_assign_role(self, assigner_roles: Set[str], target_role: str) -> bool:
        """Check if user can assign a specific role"""
        # Super admins can assign any role
        if Role.SUPER_ADMIN.value in assigner_roles:
            return True
        
        # Org admins can assign non-system roles
        if Role.ORG_ADMIN.value in assigner_roles:
            target_role_def = self.role_definitions.get(target_role)
            return target_role_def and not target_role_def.is_system_role
        
        return False
    
    def validate_role_assignment(self, user_id: str, role: str, organization_id: Optional[str] = None) -> List[str]:
        """Validate role assignment and return any violations"""
        violations = []
        
        role_def = self.role_definitions.get(role)
        if not role_def:
            violations.append(f"Role '{role}' does not exist")
            return violations
        
        # Check if role requires approval
        if role_def.requires_approval:
            violations.append(f"Role '{role}' requires administrative approval")
        
        # Check organization requirement for non-system roles
        if not role_def.is_system_role and not organization_id:
            violations.append(f"Role '{role}' requires organization membership")
        
        return violations

class RBACManager:
    """Role-Based Access Control manager"""
    
    def __init__(self, redis_client: redis.Redis, jwt_secret: str):
        self.redis = redis_client
        self.jwt_secret = jwt_secret
        self.auth_matrix = AuthorizationMatrix()
        self.security = HTTPBearer()
    
    async def store_user_permissions(self, user_permissions: UserPermissions) -> bool:
        """Store user permissions in Redis cache"""
        try:
            key = f"permissions:{user_permissions.user_id}"
            
            # Convert to serializable format
            data = {
                "user_id": user_permissions.user_id,
                "organization_id": user_permissions.organization_id,
                "roles": list(user_permissions.roles),
                "permissions": [p.value for p in user_permissions.permissions],
                "restrictions": user_permissions.restrictions,
                "expires_at": user_permissions.expires_at.isoformat() if user_permissions.expires_at else None,
                "last_updated": user_permissions.last_updated.isoformat()
            }
            
            # Cache for 1 hour
            await self.redis.setex(key, 3600, json.dumps(data))
            
            logger.info("User permissions cached", user_id=user_permissions.user_id)
            return True
            
        except Exception as e:
            logger.error("Failed to cache user permissions", user_id=user_permissions.user_id, error=str(e))
            return False
    
    async def get_user_permissions(self, user_id: str) -> Optional[UserPermissions]:
        """Get user permissions from cache"""
        try:
            key = f"permissions:{user_id}"
            data = await self.redis.get(key)
            
            if not data:
                return None
            
            parsed_data = json.loads(data)
            
            # Convert back to UserPermissions object
            permissions = UserPermissions(
                user_id=parsed_data["user_id"],
                organization_id=parsed_data.get("organization_id"),
                roles=set(parsed_data["roles"]),
                permissions=set(Permission(p) for p in parsed_data["permissions"]),
                restrictions=parsed_data.get("restrictions", {}),
                expires_at=datetime.fromisoformat(parsed_data["expires_at"]) if parsed_data.get("expires_at") else None,
                last_updated=datetime.fromisoformat(parsed_data["last_updated"])
            )
            
            # Check if permissions have expired
            if permissions.expires_at and datetime.utcnow() > permissions.expires_at:
                await self.invalidate_user_permissions(user_id)
                return None
            
            return permissions
            
        except Exception as e:
            logger.error("Failed to get user permissions", user_id=user_id, error=str(e))
            return None
    
    async def invalidate_user_permissions(self, user_id: str) -> bool:
        """Invalidate cached user permissions"""
        try:
            key = f"permissions:{user_id}"
            await self.redis.delete(key)
            
            logger.info("User permissions invalidated", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error("Failed to invalidate user permissions", user_id=user_id, error=str(e))
            return False
    
    async def check_permission(self, user_id: str, required_permission: Permission, resource_id: Optional[str] = None) -> bool:
        """Check if user has specific permission"""
        user_permissions = await self.get_user_permissions(user_id)
        
        if not user_permissions:
            logger.warning("No permissions found for user", user_id=user_id)
            return False
        
        # Check if user has the required permission
        has_permission = required_permission in user_permissions.permissions
        
        if not has_permission:
            logger.warning("Permission denied", 
                          user_id=user_id, 
                          required_permission=required_permission.value,
                          user_permissions=[p.value for p in user_permissions.permissions])
        
        # TODO: Add resource-level access control here
        # if resource_id:
        #     return await self._check_resource_access(user_permissions, resource_id)
        
        return has_permission
    
    def create_access_token(self, user_id: str, user_permissions: UserPermissions) -> str:
        """Create JWT access token with embedded permissions"""
        payload = {
            "sub": user_id,
            "org": user_permissions.organization_id,
            "roles": list(user_permissions.roles),
            "permissions": [p.value for p in user_permissions.permissions],
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")
    
    async def verify_access_token(self, token: str) -> Optional[UserPermissions]:
        """Verify JWT token and return user permissions"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            
            user_permissions = UserPermissions(
                user_id=payload["sub"],
                organization_id=payload.get("org"),
                roles=set(payload.get("roles", [])),
                permissions=set(Permission(p) for p in payload.get("permissions", [])),
                expires_at=datetime.fromtimestamp(payload["exp"])
            )
            
            return user_permissions
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid token", error=str(e))
            return None
    
    async def assign_role(self, user_id: str, role: str, assigner_id: str, organization_id: Optional[str] = None) -> bool:
        """Assign role to user"""
        try:
            # Get assigner permissions
            assigner_permissions = await self.get_user_permissions(assigner_id)
            if not assigner_permissions:
                logger.warning("Assigner permissions not found", assigner_id=assigner_id)
                return False
            
            # Check if assigner can assign this role
            if not self.auth_matrix.can_assign_role(assigner_permissions.roles, role):
                logger.warning("Insufficient privileges to assign role", 
                              assigner_id=assigner_id, 
                              target_role=role)
                return False
            
            # Validate role assignment
            violations = self.auth_matrix.validate_role_assignment(user_id, role, organization_id)
            if violations:
                logger.warning("Role assignment validation failed", 
                              user_id=user_id, 
                              role=role, 
                              violations=violations)
                return False
            
            # Get current user permissions
            user_permissions = await self.get_user_permissions(user_id)
            if not user_permissions:
                # Create new permissions
                user_permissions = UserPermissions(
                    user_id=user_id,
                    organization_id=organization_id
                )
            
            # Add role
            user_permissions.roles.add(role)
            
            # Update permissions
            all_permissions = self.auth_matrix.get_user_permissions(user_permissions.roles)
            user_permissions.permissions = all_permissions
            
            # Set expiration if role has auto-expire
            role_def = self.auth_matrix.role_definitions.get(role)
            if role_def and role_def.auto_expire_days:
                user_permissions.expires_at = datetime.utcnow() + timedelta(days=role_def.auto_expire_days)
            
            # Store updated permissions
            success = await self.store_user_permissions(user_permissions)
            
            if success:
                logger.info("Role assigned successfully", 
                           user_id=user_id, 
                           role=role, 
                           assigner_id=assigner_id)
            
            return success
            
        except Exception as e:
            logger.error("Failed to assign role", 
                        user_id=user_id, 
                        role=role, 
                        error=str(e))
            return False
    
    async def revoke_role(self, user_id: str, role: str, revoker_id: str) -> bool:
        """Revoke role from user"""
        try:
            # Get revoker permissions  
            revoker_permissions = await self.get_user_permissions(revoker_id)
            if not revoker_permissions:
                return False
            
            # Check if revoker can revoke this role
            if not self.auth_matrix.can_assign_role(revoker_permissions.roles, role):
                logger.warning("Insufficient privileges to revoke role", 
                              revoker_id=revoker_id, 
                              target_role=role)
                return False
            
            # Get current user permissions
            user_permissions = await self.get_user_permissions(user_id)
            if not user_permissions:
                return False
            
            # Remove role
            user_permissions.roles.discard(role)
            
            # Update permissions
            all_permissions = self.auth_matrix.get_user_permissions(user_permissions.roles)
            user_permissions.permissions = all_permissions
            user_permissions.last_updated = datetime.utcnow()
            
            # Store updated permissions
            success = await self.store_user_permissions(user_permissions)
            
            if success:
                logger.info("Role revoked successfully", 
                           user_id=user_id, 
                           role=role, 
                           revoker_id=revoker_id)
            
            return success
            
        except Exception as e:
            logger.error("Failed to revoke role", 
                        user_id=user_id, 
                        role=role, 
                        error=str(e))
            return False

# Global RBAC manager instance
_rbac_manager: Optional[RBACManager] = None

def get_rbac_manager() -> Optional[RBACManager]:
    """Get global RBAC manager instance"""
    return _rbac_manager

def init_rbac_manager(redis_client: redis.Redis, jwt_secret: str) -> RBACManager:
    """Initialize global RBAC manager"""
    global _rbac_manager
    _rbac_manager = RBACManager(redis_client, jwt_secret)
    logger.info("RBAC manager initialized")
    return _rbac_manager

# Dependency injection for FastAPI
async def get_current_user_permissions(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> UserPermissions:
    """FastAPI dependency to get current user permissions"""
    rbac_manager = get_rbac_manager()
    if not rbac_manager:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="RBAC manager not initialized"
        )
    
    token = credentials.credentials
    user_permissions = await rbac_manager.verify_access_token(token)
    
    if not user_permissions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user_permissions

def require_permission(required_permission: Permission):
    """Decorator to require specific permission for endpoint access"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user_permissions: UserPermissions = Depends(get_current_user_permissions), **kwargs):
            rbac_manager = get_rbac_manager()
            if not rbac_manager:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="RBAC manager not initialized"
                )
            
            has_permission = await rbac_manager.check_permission(
                user_permissions.user_id, 
                required_permission
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission required: {required_permission.value}"
                )
            
            return await func(*args, user_permissions=user_permissions, **kwargs)
        
        return wrapper
    return decorator

def require_role(required_role: Role):
    """Decorator to require specific role for endpoint access"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user_permissions: UserPermissions = Depends(get_current_user_permissions), **kwargs):
            if required_role.value not in user_permissions.roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role required: {required_role.value}"
                )
            
            return await func(*args, user_permissions=user_permissions, **kwargs)
        
        return wrapper
    return decorator