"""
Audit Log Models
Naplózási modellek minden lényeges változáshoz
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Index, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import json
from typing import Dict, Any, Optional

from app.models import Base


class AuditLog(Base):
    """
    Audit log entries for tracking all significant changes
    Minden lényeges változás naplózása
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Base model fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    # Ki végezte a műveletet - Who performed the action
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    username = Column(String(100), nullable=True)   # Username at time of action
    
    # Mikor történt - When it happened
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Mit csinált - What was done
    action = Column(String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, LOGIN, etc.
    action_description = Column(String(500), nullable=True)  # Human-readable description
    
    # Mit érintett - What was affected
    entity_type = Column(String(100), nullable=False, index=True)  # Gate, User, Maintenance, etc.
    entity_id = Column(Integer, nullable=False, index=True)  # ID of affected resource
    
    # Előtte/utána adatok - Before/After data
    old_values = Column(JSON, nullable=True)  # Data before change
    new_values = Column(JSON, nullable=True)  # Data after change
    changed_fields = Column(JSON, nullable=True)  # List of changed field names
    
    # Technikai részletek - Technical details
    ip_address = Column(String(45), nullable=True, index=True)  # IPv4/IPv6
    user_agent = Column(Text, nullable=True)  # Browser/Client info
    session_id = Column(String(100), nullable=True, index=True)  # Session identifier
    request_method = Column(String(10), nullable=True)  # GET, POST, PUT, DELETE
    request_path = Column(String(1000), nullable=True)  # API endpoint path
    request_id = Column(String(100), nullable=True, index=True)  # Unique request ID
    
    # Szervezet - Organization context
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True, index=True)
    
    # Művelet eredménye - Operation result
    success = Column(Boolean, nullable=False, default=True, index=True)
    error_message = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)  # Operation duration in milliseconds
    
    # Üzleti logika - Business context
    risk_level = Column(String(20), default="LOW", nullable=False, index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    compliance_flags = Column(JSON, nullable=True)  # Compliance-related flags
    
    # Kapcsolatok - Relationships
    user = relationship("User", back_populates="audit_logs")
    organization = relationship("Organization")
    
    # Indexek - Database indexes
    __table_args__ = (
        Index('idx_audit_timestamp_action', 'timestamp', 'action'),
        Index('idx_audit_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_organization_timestamp', 'organization_id', 'timestamp'),
        {'extend_existing': True}
    )

    def __repr__(self):
        return f"<AuditLog({self.id}: {self.user_email} {self.action} {self.resource_type} at {self.timestamp})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "action": self.action,
            "action_description": self.action_description,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "old_values": self.old_values,
            "new_values": self.new_values,
            "changed_fields": self.changed_fields,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "session_id": self.session_id,
            "request_method": self.request_method,
            "request_path": self.request_path,
            "organization_id": self.organization_id,
            "success": self.success,
            "error_message": self.error_message,
            "duration_ms": self.duration_ms,
            "risk_level": self.risk_level,
            "compliance_flags": self.compliance_flags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AuditAction:
    """Audit action constants"""
    # CRUD Operations
    CREATE = "CREATE"
    UPDATE = "UPDATE" 
    DELETE = "DELETE"
    VIEW = "VIEW"
    
    # Authentication
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    LOGIN_FAILED = "LOGIN_FAILED"
    PASSWORD_CHANGED = "PASSWORD_CHANGED"
    
    # Gate Operations
    GATE_OPENED = "GATE_OPENED"
    GATE_CLOSED = "GATE_CLOSED"
    GATE_MAINTENANCE = "GATE_MAINTENANCE"
    GATE_INSPECTION = "GATE_INSPECTION"
    
    # Maintenance Operations
    MAINTENANCE_SCHEDULED = "MAINTENANCE_SCHEDULED"
    MAINTENANCE_COMPLETED = "MAINTENANCE_COMPLETED"
    MAINTENANCE_CANCELLED = "MAINTENANCE_CANCELLED"
    
    # System Operations
    SYSTEM_BACKUP = "SYSTEM_BACKUP"
    SYSTEM_RESTORE = "SYSTEM_RESTORE"
    DATA_IMPORT = "DATA_IMPORT"
    DATA_EXPORT = "DATA_EXPORT"
    
    # Permission Operations
    PERMISSION_GRANTED = "PERMISSION_GRANTED"
    PERMISSION_REVOKED = "PERMISSION_REVOKED"
    ROLE_ASSIGNED = "ROLE_ASSIGNED"
    ROLE_REMOVED = "ROLE_REMOVED"


class AuditCategory:
    """Audit category constants"""
    SECURITY = "SECURITY"      # Authentication, authorization, permissions
    DATA = "DATA"             # CRUD operations on business data
    SYSTEM = "SYSTEM"         # System operations, configuration changes
    BUSINESS = "BUSINESS"     # Business process operations
    INTEGRATION = "INTEGRATION"  # External system interactions


class AuditSeverity:
    """Audit severity levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AuditResourceType:
    """Resource type constants"""
    USER = "User"
    GATE = "Gate"
    ORGANIZATION = "Organization"
    SITE = "Site"
    BUILDING = "Building"
    MAINTENANCE = "Maintenance"
    INSPECTION = "Inspection"
    TICKET = "Ticket"
    NOTIFICATION = "Notification"
    INVENTORY = "Inventory"
    ROLE = "Role"
    PERMISSION = "Permission"
    SYSTEM = "System"