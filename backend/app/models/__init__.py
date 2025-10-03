"""Database models base module."""

from sqlalchemy import Column, Integer, DateTime, Boolean, String, text
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Any
import uuid


Base = declarative_base()


class BaseModel(Base):
    """Base model with common fields."""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Soft delete support
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        return cls.__name__.lower()


class TenantModel(BaseModel):
    """Base model for tenant-aware entities."""
    
    __abstract__ = True
    
    # Multi-tenant support - organization ID for row-level security
    org_id = Column(Integer, nullable=False, index=True)


class UUIDModel(BaseModel):
    """Base model with UUID primary key."""
    
    __abstract__ = True
    
    # Override id to be UUID instead of integer
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))


# Import all models to ensure they are registered with SQLAlchemy
from app.models.organization import Organization, Client, Site, Building, Gate
from app.models.components import GateComponent
from app.models.inspections import ChecklistTemplate, ChecklistItem, Inspection, InspectionItem, Measurement
from app.models.maintenance import MaintenancePlan, MaintenanceJob, Reminder
from app.models.tickets import Ticket, WorkOrder, WorkOrderItem, Part, PartUsage
from app.models.auth import User, Role, Permission, RoleAssignment, WebAuthnCredential, TOTPSecret, APIKey
from app.models.documents import Document, MediaObject, Integration, Webhook
from app.models.inventory import Warehouse, InventoryItem, StockMovement, StockAlert, StockTake, StockTakeLine, Event
from app.models.audit_logs import AuditLog

# Export all models
__all__ = [
    'Base', 'BaseModel', 'TenantModel', 'UUIDModel',
    # Organization hierarchy
    'Organization', 'Client', 'Site', 'Building', 'Gate',
    # Components
    'GateComponent',
    # Inspections and checklists
    'ChecklistTemplate', 'ChecklistItem', 'Inspection', 'InspectionItem', 'Measurement',
    # Maintenance
    'MaintenancePlan', 'MaintenanceJob', 'Reminder',
    # Tickets and work
    'Ticket', 'WorkOrder', 'WorkOrderItem', 'Part', 'PartUsage',
    # Authentication and authorization
    'User', 'Role', 'Permission', 'RoleAssignment', 'WebAuthnCredential', 'TOTPSecret', 'APIKey',
    # Documents and media
    'Document', 'MediaObject', 'Integration', 'Webhook',
    # Inventory and audit
    'Warehouse', 'InventoryItem', 'StockMovement', 'StockAlert', 'StockTake', 'StockTakeLine', 'AuditLog', 'Event',
]