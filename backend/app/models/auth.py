"""Authentication and authorization models."""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Index, LargeBinary
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, List, Dict, Any
from datetime import datetime
import secrets
import base64

from app.models import BaseModel, TenantModel


class User(BaseModel):
    """
    Users - system users with authentication and authorization.
    
    Felhasználók (rendszer felhasználók hitelesítéssel és jogosultságokkal)
    """
    __tablename__ = "users"
    
    # Organization reference
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Basic information
    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(320), nullable=False, unique=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    display_name = Column(String(200), nullable=True)
    
    # Authentication
    password_hash = Column(String(255), nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(String(100), nullable=True, unique=True)
    password_reset_token = Column(String(100), nullable=True, unique=True)
    password_reset_expires = Column(DateTime, nullable=True)
    
    # Contact information
    phone = Column(String(50), nullable=True)
    mobile = Column(String(50), nullable=True)
    
    # Profile information
    job_title = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    employee_id = Column(String(50), nullable=True, index=True)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Activity tracking
    last_login = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    account_locked_until = Column(DateTime, nullable=True)
    
    # Preferences
    timezone = Column(String(50), default='UTC', nullable=False)
    language = Column(String(10), default='en', nullable=False)
    theme = Column(String(20), default='auto', nullable=False)
    
    # Settings
    settings = Column(JSONB, nullable=True, default=lambda: {})
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    role_assignments = relationship("RoleAssignment", foreign_keys="RoleAssignment.user_id", back_populates="user", cascade="all, delete-orphan")
    webauthn_credentials = relationship("WebAuthnCredential", back_populates="user", cascade="all, delete-orphan")
    totp_secrets = relationship("TOTPSecret", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    
    # Activity relationships
    inspections = relationship("Inspection", foreign_keys="Inspection.inspector_id", back_populates="inspector")
    assigned_maintenance_jobs = relationship("MaintenanceJob", back_populates="assigned_technician")
    reported_tickets = relationship("Ticket", foreign_keys="Ticket.reporter_id", back_populates="reporter")
    assigned_tickets = relationship("Ticket", foreign_keys="Ticket.assigned_technician_id", back_populates="assigned_technician")
    work_orders = relationship("WorkOrder", back_populates="assigned_technician")
    reminders = relationship("Reminder", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    # Indexes
    __table_args__ = (
        Index("idx_user_username", "username"),
        Index("idx_user_email", "email"),
        Index("idx_user_org", "organization_id"),
        Index("idx_user_active", "is_active"),
        Index("idx_user_employee_id", "employee_id"),
        Index("idx_user_last_login", "last_login"),
    )
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_locked(self) -> bool:
        """Check if account is locked."""
        if self.account_locked_until:
            return datetime.utcnow() < self.account_locked_until
        return False


class Role(BaseModel):
    """
    Roles - role definitions for RBAC.
    
    Szerepkörök (RBAC szerepkör definíciók)
    """
    __tablename__ = "roles"
    
    # Role information
    name = Column(String(100), nullable=False, unique=True, index=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Role characteristics
    is_system_role = Column(Boolean, default=False, nullable=False)
    is_assignable = Column(Boolean, default=True, nullable=False)
    scope = Column(String(50), default='organization', nullable=False)  # 'global', 'organization', 'site'
    
    # Relationships
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")
    role_assignments = relationship("RoleAssignment", back_populates="role")
    
    # Indexes
    __table_args__ = (
        Index("idx_role_name", "name"),
        Index("idx_role_system", "is_system_role"),
        Index("idx_role_assignable", "is_assignable"),
    )


class Permission(BaseModel):
    """
    Permissions - granular permissions for RBAC.
    
    Jogosultságok (részletes jogosultságok RBAC-hoz)
    """
    __tablename__ = "permissions"
    
    # Permission information
    name = Column(String(100), nullable=False, unique=True, index=True)
    codename = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # Permission categorization
    resource = Column(String(50), nullable=False, index=True)  # 'gate', 'inspection', 'ticket', etc.
    action = Column(String(50), nullable=False, index=True)    # 'create', 'read', 'update', 'delete'
    scope = Column(String(50), default='organization', nullable=False)  # 'global', 'organization', 'own'
    
    # Relationships
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")
    
    # Indexes
    __table_args__ = (
        Index("idx_permission_name", "name"),
        Index("idx_permission_codename", "codename"),
        Index("idx_permission_resource", "resource"),
        Index("idx_permission_action", "action"),
        Index("idx_permission_resource_action", "resource", "action"),
    )


# Association table for Role-Permission many-to-many relationship
from sqlalchemy import Table
role_permissions = Table(
    'role_permissions',
    BaseModel.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True),
    Column('created_at', DateTime, nullable=False, default=datetime.utcnow),
    Index('idx_role_perm_role', 'role_id'),
    Index('idx_role_perm_permission', 'permission_id'),
)


class RoleAssignment(TenantModel):
    """
    Role Assignments - user-role assignments with scope.
    
    Szerepkör hozzárendelések (felhasználó-szerepkör hozzárendelések hatókörrel)
    """
    __tablename__ = "role_assignments"
    
    # References
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    
    # Assignment scope
    scope_type = Column(String(20), nullable=False)  # 'global', 'organization', 'site', 'building', 'gate'
    scope_id = Column(Integer, nullable=True)  # ID of the scoped entity
    
    # Assignment details
    assigned_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="role_assignments")
    role = relationship("Role", back_populates="role_assignments")
    assigned_by = relationship("User", foreign_keys=[assigned_by_user_id])
    
    # Indexes
    __table_args__ = (
        Index("idx_role_assignment_user", "user_id"),
        Index("idx_role_assignment_role", "role_id"),
        Index("idx_role_assignment_scope", "scope_type", "scope_id"),
        Index("idx_role_assignment_active", "is_active"),
        Index("idx_role_assignment_expires", "expires_at"),
    )
    
    @property
    def is_expired(self) -> bool:
        """Check if role assignment is expired."""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False


class WebAuthnCredential(TenantModel):
    """
    WebAuthn Credentials - FIDO2/WebAuthn authentication credentials.
    
    WebAuthn hitelesítő adatok (FIDO2/WebAuthn hitelesítési hitelesítő adatok)
    """
    __tablename__ = "webauthn_credentials"
    
    # User reference
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Credential information
    credential_id = Column(LargeBinary, nullable=False, unique=True, index=True)
    public_key = Column(LargeBinary, nullable=False)
    sign_count = Column(Integer, default=0, nullable=False)
    
    # Device information
    device_name = Column(String(200), nullable=True)
    device_type = Column(String(50), nullable=True)  # 'platform', 'cross-platform'
    aaguid = Column(String(36), nullable=True)  # Authenticator AAGUID
    
    # Registration details
    registered_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    use_count = Column(Integer, default=0, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="webauthn_credentials")
    
    # Indexes
    __table_args__ = (
        Index("idx_webauthn_user", "user_id"),
        Index("idx_webauthn_credential_id", "credential_id"),
        Index("idx_webauthn_active", "is_active"),
        Index("idx_webauthn_last_used", "last_used_at"),
    )


class TOTPSecret(TenantModel):
    """
    TOTP Secrets - Time-based One-Time Password secrets for 2FA.
    
    TOTP titkok (időalapú egyszeri jelszó titkok 2FA-hoz)
    """
    __tablename__ = "totp_secrets"
    
    # User reference
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # TOTP information
    secret = Column(LargeBinary, nullable=False)  # Encrypted secret
    backup_codes = Column(JSONB, nullable=True)  # Encrypted backup codes
    
    # Device/app information
    device_name = Column(String(200), nullable=True)
    issuer = Column(String(100), default='GarageReg', nullable=False)
    
    # Status and usage
    is_verified = Column(Boolean, default=False, nullable=False)
    verified_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    use_count = Column(Integer, default=0, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="totp_secrets")
    
    # Indexes
    __table_args__ = (
        Index("idx_totp_user", "user_id"),
        Index("idx_totp_verified", "is_verified"),
        Index("idx_totp_active", "is_active"),
    )


class APIKey(TenantModel):
    """
    API Keys - API access keys for programmatic access.
    
    API kulcsok (API hozzáférési kulcsok programozott hozzáféréshez)
    """
    __tablename__ = "api_keys"
    
    # User reference
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Key information
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    key_hash = Column(String(255), nullable=False, unique=True, index=True)
    key_prefix = Column(String(10), nullable=False, index=True)
    
    # Permissions and scope
    scopes = Column(JSONB, nullable=True)  # Array of allowed scopes
    permissions = Column(JSONB, nullable=True)  # Array of allowed permissions
    
    # Usage tracking
    last_used_at = Column(DateTime, nullable=True)
    use_count = Column(Integer, default=0, nullable=False)
    
    # Expiration
    expires_at = Column(DateTime, nullable=True, index=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    # Indexes
    __table_args__ = (
        Index("idx_api_key_user", "user_id"),
        Index("idx_api_key_hash", "key_hash"),
        Index("idx_api_key_prefix", "key_prefix"),
        Index("idx_api_key_active", "is_active"),
        Index("idx_api_key_expires", "expires_at"),
    )
    
    @property
    def is_expired(self) -> bool:
        """Check if API key is expired."""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    @classmethod
    def generate_key_prefix(cls) -> str:
        """Generate a random key prefix."""
        return secrets.token_hex(4)
    
    @classmethod  
    def generate_key(cls) -> tuple[str, str]:
        """Generate API key and its hash."""
        key = secrets.token_urlsafe(32)
        key_hash = ... # Would use proper hashing in real implementation
        return key, key_hash