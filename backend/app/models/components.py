"""Gate component models."""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Numeric, Index
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional
from datetime import datetime

from app.models import TenantModel


class GateComponent(TenantModel):
    """
    Gate Components - individual parts/components of gates.
    
    Kapu komponensek (motor, vezérlőegység, érzékelők, stb.)
    """
    __tablename__ = "gate_components"
    
    # Gate reference
    gate_id = Column(Integer, ForeignKey("gates.id"), nullable=False, index=True)
    
    # Component identification
    name = Column(String(200), nullable=False, index=True)
    component_type = Column(String(100), nullable=False, index=True)  # 'motor', 'controller', 'sensor', 'remote', 'safety'
    category = Column(String(100), nullable=True)  # Subcategory for organization
    
    # Manufacturer information
    manufacturer = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    part_number = Column(String(100), nullable=True, index=True)
    serial_number = Column(String(100), nullable=True, index=True)
    
    # Installation information
    installation_date = Column(DateTime, nullable=True)
    installer = Column(String(200), nullable=True)
    location_description = Column(String(500), nullable=True)  # Where on the gate this component is located
    
    # Warranty and lifecycle
    warranty_start_date = Column(DateTime, nullable=True)
    warranty_end_date = Column(DateTime, nullable=True)
    expected_lifespan_months = Column(Integer, nullable=True)
    replacement_recommendation_date = Column(DateTime, nullable=True)
    
    # Usage tracking
    cycle_count = Column(Integer, default=0, nullable=False)  # How many times this component has been used
    max_cycles = Column(Integer, nullable=True)  # Maximum recommended cycles
    operating_hours = Column(Integer, default=0, nullable=False)  # Total operating hours
    max_operating_hours = Column(Integer, nullable=True)
    
    # Technical specifications
    specifications = Column(JSONB, nullable=True, default=lambda: {})  # Technical specs as JSON
    
    # Maintenance information
    last_maintenance_date = Column(DateTime, nullable=True)
    next_maintenance_date = Column(DateTime, nullable=True)
    maintenance_interval_days = Column(Integer, nullable=True)
    
    # Condition and status
    condition = Column(String(50), default='good', nullable=False)  # 'excellent', 'good', 'fair', 'poor', 'critical'
    status = Column(String(50), default='operational', nullable=False)  # 'operational', 'maintenance', 'broken', 'replaced'
    condition_notes = Column(Text, nullable=True)
    
    # Cost information
    purchase_cost = Column(Numeric(10, 2), nullable=True)
    installation_cost = Column(Numeric(10, 2), nullable=True)
    replacement_cost_estimate = Column(Numeric(10, 2), nullable=True)
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSONB, nullable=True, default=lambda: {})
    
    # Relationships
    gate = relationship("Gate", back_populates="components")
    part_usages = relationship("PartUsage", back_populates="component", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_component_gate", "gate_id"),
        Index("idx_component_type", "component_type"),
        Index("idx_component_name", "name"),
        Index("idx_component_part_number", "part_number"),
        Index("idx_component_serial", "serial_number"),
        Index("idx_component_condition", "condition"),
        Index("idx_component_status", "status"),
        Index("idx_component_warranty", "warranty_end_date"),
        Index("idx_component_maintenance", "next_maintenance_date"),
        Index("idx_component_replacement", "replacement_recommendation_date"),
    )
    
    @validates("condition")
    def validate_condition(self, key, value):
        valid_conditions = ['excellent', 'good', 'fair', 'poor', 'critical']
        if value not in valid_conditions:
            raise ValueError(f"Condition must be one of: {valid_conditions}")
        return value
    
    @validates("status")
    def validate_status(self, key, value):
        valid_statuses = ['operational', 'maintenance', 'broken', 'replaced', 'decommissioned']
        if value not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        return value
    
    @validates("component_type")
    def validate_component_type(self, key, value):
        valid_types = [
            'motor', 'controller', 'sensor', 'remote', 'safety', 'power_supply',
            'hydraulic', 'mechanical', 'electronic', 'communication', 'lighting'
        ]
        if value not in valid_types:
            raise ValueError(f"Component type must be one of: {valid_types}")
        return value
    
    @property
    def is_due_for_replacement(self) -> bool:
        """Check if component is due for replacement."""
        if self.replacement_recommendation_date:
            return datetime.utcnow() >= self.replacement_recommendation_date
        return False
    
    @property
    def is_under_warranty(self) -> bool:
        """Check if component is still under warranty."""
        if self.warranty_end_date:
            return datetime.utcnow() <= self.warranty_end_date
        return False
    
    @property
    def cycle_usage_percentage(self) -> Optional[float]:
        """Get cycle usage as percentage of maximum cycles."""
        if self.max_cycles and self.max_cycles > 0:
            return (self.cycle_count / self.max_cycles) * 100
        return None
    
    @property
    def operating_hours_percentage(self) -> Optional[float]:
        """Get operating hours usage as percentage of maximum hours."""
        if self.max_operating_hours and self.max_operating_hours > 0:
            return (self.operating_hours / self.max_operating_hours) * 100
        return None