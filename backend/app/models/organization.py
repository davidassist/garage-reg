"""Organizational hierarchy models."""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship, validates
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSON
from typing import Optional, Dict, Any

from app.models import BaseModel, TenantModel


class Organization(BaseModel):
    """
    Organizations - top level tenant entity.
    
    Minden szervezet (társasház kezelő, kapu szerviz cég, stb.)
    """
    __tablename__ = "organizations"
    
    # Basic information
    name = Column(String(200), nullable=False, index=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Contact information
    email = Column(String(320), nullable=True)
    phone = Column(String(50), nullable=True)
    website = Column(String(500), nullable=True)
    
    # Address
    address_line_1 = Column(String(200), nullable=True)
    address_line_2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Business information
    tax_number = Column(String(50), nullable=True)
    registration_number = Column(String(100), nullable=True)
    
    # Status and configuration
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSON, nullable=True, default=lambda: {})
    
    # Relationships
    clients = relationship("Client", back_populates="organization", cascade="all, delete-orphan")
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_org_name", "name"),
        Index("idx_org_active", "is_active"),
        Index("idx_org_tax_number", "tax_number"),
    )
    
    @validates("name")
    def validate_name(self, key, value):
        if not value or len(value.strip()) < 2:
            raise ValueError("Organization name must be at least 2 characters")
        return value.strip()


class Client(TenantModel):
    """
    Clients - organizations that own buildings/gates.
    
    Ügyfelek (társasházak, ingatlan kezelők, akik kapukat üzemeltetnek)
    """
    __tablename__ = "clients"
    
    # Organization reference
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Basic information
    name = Column(String(200), nullable=False, index=True)
    display_name = Column(String(200), nullable=False)
    type = Column(String(50), nullable=False)  # 'residential', 'commercial', 'industrial', 'mixed'
    
    # Contact information  
    contact_person = Column(String(200), nullable=True)
    email = Column(String(320), nullable=True)
    phone = Column(String(50), nullable=True)
    
    # Address
    address_line_1 = Column(String(200), nullable=True)
    address_line_2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Business information
    contract_number = Column(String(100), nullable=True)
    contract_start_date = Column(DateTime, nullable=True)
    contract_end_date = Column(DateTime, nullable=True)
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSON, nullable=True, default=lambda: {})
    
    # Relationships
    organization = relationship("Organization", back_populates="clients")
    sites = relationship("Site", back_populates="client", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_client_org", "organization_id"),
        Index("idx_client_name", "name"),
        Index("idx_client_type", "type"),
        Index("idx_client_active", "is_active"),
        Index("idx_client_contract", "contract_number"),
    )


class Site(TenantModel):
    """
    Sites - physical locations within a client's property.
    
    Telephelyek (egy ügyfél több telephellyel rendelkezhet)
    """
    __tablename__ = "sites"
    
    # Client reference
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    
    # Basic information
    name = Column(String(200), nullable=False, index=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    site_code = Column(String(50), nullable=True, unique=True, index=True)
    
    # Address (can be different from client address)
    address_line_1 = Column(String(200), nullable=True)
    address_line_2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Geographic coordinates
    latitude = Column(String(20), nullable=True)
    longitude = Column(String(20), nullable=True)
    
    # Site characteristics
    area_sqm = Column(Integer, nullable=True)  # Square meters
    access_instructions = Column(Text, nullable=True)
    emergency_contact = Column(String(200), nullable=True)
    emergency_phone = Column(String(50), nullable=True)
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSON, nullable=True, default=lambda: {})
    
    # Relationships
    client = relationship("Client", back_populates="sites")
    buildings = relationship("Building", back_populates="site", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_site_client", "client_id"),
        Index("idx_site_name", "name"),
        Index("idx_site_code", "site_code"),
        Index("idx_site_active", "is_active"),
        Index("idx_site_location", "latitude", "longitude"),
    )


class Building(TenantModel):
    """
    Buildings - physical structures within a site.
    
    Épületek (egy telephelyen több épület lehet)
    """
    __tablename__ = "buildings"
    
    # Site reference
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)
    
    # Basic information
    name = Column(String(200), nullable=False, index=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    building_code = Column(String(50), nullable=True, index=True)
    
    # Building characteristics
    building_type = Column(String(50), nullable=True)  # 'residential', 'office', 'warehouse', etc.
    floors = Column(Integer, nullable=True)
    units = Column(Integer, nullable=True)  # Number of apartments/offices
    year_built = Column(Integer, nullable=True)
    
    # Address within site (if applicable)
    address_suffix = Column(String(100), nullable=True)  # Building number, wing, etc.
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSON, nullable=True, default=lambda: {})
    
    # Relationships
    site = relationship("Site", back_populates="buildings")
    gates = relationship("Gate", back_populates="building", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_building_site", "site_id"),
        Index("idx_building_name", "name"),
        Index("idx_building_code", "building_code"),
        Index("idx_building_type", "building_type"),
        Index("idx_building_active", "is_active"),
    )


class Gate(TenantModel):
    """
    Gates - the main entity representing gate installations.
    
    Kapuk - a rendszer fő entitása (kapuberendezések)
    """
    __tablename__ = "gates"
    
    # Building reference
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False, index=True)
    
    # Basic information
    name = Column(String(200), nullable=False, index=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    gate_code = Column(String(50), nullable=True, unique=True, index=True)
    
    # Gate specifications
    gate_type = Column(String(50), nullable=False)  # 'swing', 'sliding', 'barrier', 'bollard'
    manufacturer = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    serial_number = Column(String(100), nullable=True, index=True)
    
    # Installation information
    installation_date = Column(DateTime, nullable=True)
    installer = Column(String(200), nullable=True)
    warranty_end_date = Column(DateTime, nullable=True)
    
    # Physical characteristics
    width_cm = Column(Integer, nullable=True)
    height_cm = Column(Integer, nullable=True)
    weight_kg = Column(Integer, nullable=True)
    material = Column(String(100), nullable=True)
    
    # Operational information
    max_opening_cycles_per_day = Column(Integer, nullable=True)
    current_cycle_count = Column(Integer, default=0, nullable=False)
    last_maintenance_date = Column(DateTime, nullable=True)
    next_maintenance_date = Column(DateTime, nullable=True)
    
    # Status and settings
    status = Column(String(50), default='operational', nullable=False)  # 'operational', 'maintenance', 'broken', 'decommissioned'
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSON, nullable=True, default=lambda: {})
    
    # QR/NFC token management
    token_version = Column(Integer, default=1, nullable=False)  # For token invalidation
    last_token_rotation = Column(DateTime, nullable=True)  # Last token rotation timestamp
    
    # Factory QR support
    factory_qr_token = Column(String(100), nullable=True, unique=True, index=True)  # Pre-manufactured QR token
    factory_qr_assigned_at = Column(DateTime, nullable=True)  # When factory QR was assigned
    factory_qr_batch = Column(String(50), nullable=True)  # Manufacturing batch for tracking
    
    # Relationships
    building = relationship("Building", back_populates="gates")
    components = relationship("GateComponent", back_populates="gate", cascade="all, delete-orphan")
    inspections = relationship("Inspection", back_populates="gate", cascade="all, delete-orphan")
    maintenance_jobs = relationship("MaintenanceJob", back_populates="gate", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="gate", cascade="all, delete-orphan")
    work_orders = relationship("WorkOrder", back_populates="gate", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_gate_building", "building_id"),
        Index("idx_gate_name", "name"), 
        Index("idx_gate_code", "gate_code"),
        Index("idx_gate_type", "gate_type"),
        Index("idx_gate_manufacturer", "manufacturer"),
        Index("idx_gate_serial", "serial_number"),
        Index("idx_gate_status", "status"),
        Index("idx_gate_active", "is_active"),
        Index("idx_gate_maintenance", "next_maintenance_date"),
    )
    
    @validates("status")
    def validate_status(self, key, value):
        valid_statuses = ['operational', 'maintenance', 'broken', 'decommissioned']
        if value not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        return value
    
    @validates("gate_type")  
    def validate_gate_type(self, key, value):
        valid_types = ['swing', 'sliding', 'barrier', 'bollard', 'turnstile']
        if value not in valid_types:
            raise ValueError(f"Gate type must be one of: {valid_types}")
        return value
