"""Schemas for organizational hierarchy (Client/Site/Building/Gate structure)."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enum definitions
class ClientType(str, Enum):
    """Client type enumeration."""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    MIXED = "mixed"


class BuildingType(str, Enum):
    """Building type enumeration."""
    RESIDENTIAL = "residential"
    OFFICE = "office"
    WAREHOUSE = "warehouse"
    RETAIL = "retail"
    MIXED = "mixed"
    OTHER = "other"


class GateType(str, Enum):
    """Gate type enumeration."""
    SWING = "swing"
    SLIDING = "sliding"
    BARRIER = "barrier"
    BOLLARD = "bollard"
    TURNSTILE = "turnstile"


class GateStatus(str, Enum):
    """Gate status enumeration."""
    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"
    BROKEN = "broken"
    DECOMMISSIONED = "decommissioned"


# Base schemas
class BaseEntitySchema(BaseModel):
    """Base schema for all entities."""
    name: str = Field(..., min_length=2, max_length=200)
    display_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    is_active: bool = True
    settings: Optional[Dict[str, Any]] = None


# Client schemas
class ClientBase(BaseEntitySchema):
    """Base client schema."""
    type: ClientType
    contact_person: Optional[str] = Field(None, max_length=200)
    email: Optional[str] = Field(None, max_length=320)
    phone: Optional[str] = Field(None, max_length=50)
    
    # Address
    address_line_1: Optional[str] = Field(None, max_length=200)
    address_line_2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    
    # Contract information
    contract_number: Optional[str] = Field(None, max_length=100)
    contract_start_date: Optional[datetime] = None
    contract_end_date: Optional[datetime] = None


class ClientCreate(ClientBase):
    """Client creation schema."""
    pass


class ClientUpdate(BaseModel):
    """Client update schema."""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    display_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    type: Optional[ClientType] = None
    contact_person: Optional[str] = Field(None, max_length=200)
    email: Optional[str] = Field(None, max_length=320)
    phone: Optional[str] = Field(None, max_length=50)
    address_line_1: Optional[str] = Field(None, max_length=200)
    address_line_2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    contract_number: Optional[str] = Field(None, max_length=100)
    contract_start_date: Optional[datetime] = None
    contract_end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None


class ClientResponse(ClientBase):
    """Client response schema."""
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Site schemas
class SiteBase(BaseEntitySchema):
    """Base site schema."""
    site_code: Optional[str] = Field(None, max_length=50)
    
    # Address
    address_line_1: Optional[str] = Field(None, max_length=200)
    address_line_2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    
    # Geographic coordinates
    latitude: Optional[str] = Field(None, max_length=20)
    longitude: Optional[str] = Field(None, max_length=20)
    
    # Site characteristics
    area_sqm: Optional[int] = Field(None, ge=0)
    access_instructions: Optional[str] = None
    emergency_contact: Optional[str] = Field(None, max_length=200)
    emergency_phone: Optional[str] = Field(None, max_length=50)


class SiteCreate(SiteBase):
    """Site creation schema."""
    client_id: int


class SiteUpdate(BaseModel):
    """Site update schema."""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    display_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    site_code: Optional[str] = Field(None, max_length=50)
    address_line_1: Optional[str] = Field(None, max_length=200)
    address_line_2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    latitude: Optional[str] = Field(None, max_length=20)
    longitude: Optional[str] = Field(None, max_length=20)
    area_sqm: Optional[int] = Field(None, ge=0)
    access_instructions: Optional[str] = None
    emergency_contact: Optional[str] = Field(None, max_length=200)
    emergency_phone: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None


class SiteResponse(SiteBase):
    """Site response schema."""
    id: int
    client_id: int
    org_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Building schemas
class BuildingBase(BaseEntitySchema):
    """Base building schema."""
    building_code: Optional[str] = Field(None, max_length=50)
    building_type: Optional[BuildingType] = None
    floors: Optional[int] = Field(None, ge=0)
    units: Optional[int] = Field(None, ge=0)
    year_built: Optional[int] = Field(None, ge=1800, le=2100)
    address_suffix: Optional[str] = Field(None, max_length=100)


class BuildingCreate(BuildingBase):
    """Building creation schema."""
    site_id: int


class BuildingUpdate(BaseModel):
    """Building update schema."""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    display_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    building_code: Optional[str] = Field(None, max_length=50)
    building_type: Optional[BuildingType] = None
    floors: Optional[int] = Field(None, ge=0)
    units: Optional[int] = Field(None, ge=0)
    year_built: Optional[int] = Field(None, ge=1800, le=2100)
    address_suffix: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None


class BuildingResponse(BuildingBase):
    """Building response schema."""
    id: int
    site_id: int
    org_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Gate schemas
class GateBase(BaseEntitySchema):
    """Base gate schema."""
    gate_code: Optional[str] = Field(None, max_length=50)
    gate_type: GateType
    manufacturer: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    
    # Installation information
    installation_date: Optional[datetime] = None
    installer: Optional[str] = Field(None, max_length=200)
    warranty_end_date: Optional[datetime] = None
    
    # Physical characteristics
    width_cm: Optional[int] = Field(None, ge=0)
    height_cm: Optional[int] = Field(None, ge=0)
    weight_kg: Optional[int] = Field(None, ge=0)
    material: Optional[str] = Field(None, max_length=100)
    
    # Operational information
    max_opening_cycles_per_day: Optional[int] = Field(None, ge=0)
    current_cycle_count: int = Field(default=0, ge=0)
    last_maintenance_date: Optional[datetime] = None
    next_maintenance_date: Optional[datetime] = None
    
    # Status
    status: GateStatus = GateStatus.OPERATIONAL


class GateCreate(GateBase):
    """Gate creation schema."""
    building_id: int


class GateUpdate(BaseModel):
    """Gate update schema."""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    display_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    gate_code: Optional[str] = Field(None, max_length=50)
    gate_type: Optional[GateType] = None
    manufacturer: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    installation_date: Optional[datetime] = None
    installer: Optional[str] = Field(None, max_length=200)
    warranty_end_date: Optional[datetime] = None
    width_cm: Optional[int] = Field(None, ge=0)
    height_cm: Optional[int] = Field(None, ge=0)
    weight_kg: Optional[int] = Field(None, ge=0)
    material: Optional[str] = Field(None, max_length=100)
    max_opening_cycles_per_day: Optional[int] = Field(None, ge=0)
    current_cycle_count: Optional[int] = Field(None, ge=0)
    last_maintenance_date: Optional[datetime] = None
    next_maintenance_date: Optional[datetime] = None
    status: Optional[GateStatus] = None
    is_active: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None


class GateResponse(GateBase):
    """Gate response schema."""
    id: int
    building_id: int
    org_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Pagination and search schemas
class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)


class SearchParams(BaseModel):
    """Search parameters."""
    query: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class ClientSearchParams(SearchParams):
    """Client-specific search parameters."""
    type: Optional[ClientType] = None
    city: Optional[str] = Field(None, max_length=100)


class SiteSearchParams(SearchParams):
    """Site-specific search parameters."""
    client_id: Optional[int] = None
    city: Optional[str] = Field(None, max_length=100)


class BuildingSearchParams(SearchParams):
    """Building-specific search parameters."""
    site_id: Optional[int] = None
    building_type: Optional[BuildingType] = None


class GateSearchParams(SearchParams):
    """Gate-specific search parameters."""
    building_id: Optional[int] = None
    gate_type: Optional[GateType] = None
    status: Optional[GateStatus] = None
    manufacturer: Optional[str] = Field(None, max_length=100)


class PaginatedResponse(BaseModel):
    """Paginated response wrapper.""" 
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int


# Hierarchical response schemas
class ClientWithStats(ClientResponse):
    """Client with statistics."""
    sites_count: int = 0
    buildings_count: int = 0
    gates_count: int = 0


class SiteWithStats(SiteResponse):
    """Site with statistics."""
    buildings_count: int = 0
    gates_count: int = 0


class BuildingWithStats(BuildingResponse):
    """Building with statistics."""
    gates_count: int = 0


# Import schemas
class ClientImportRow(BaseModel):
    """Client import row schema."""
    client_name: str = Field(..., min_length=2, max_length=200)
    client_type: ClientType = ClientType.RESIDENTIAL
    contact_person: Optional[str] = Field(None, max_length=200)
    email: Optional[str] = Field(None, max_length=320)
    phone: Optional[str] = Field(None, max_length=50)
    address_line_1: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    contract_number: Optional[str] = Field(None, max_length=100)


class SiteImportRow(BaseModel):
    """Site import row schema."""
    client_name: str = Field(..., min_length=2, max_length=200)
    site_name: str = Field(..., min_length=2, max_length=200)
    site_code: Optional[str] = Field(None, max_length=50)
    address_line_1: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    latitude: Optional[str] = Field(None, max_length=20)
    longitude: Optional[str] = Field(None, max_length=20)


class BuildingImportRow(BaseModel):
    """Building import row schema."""
    client_name: str = Field(..., min_length=2, max_length=200)
    site_name: str = Field(..., min_length=2, max_length=200)
    building_name: str = Field(..., min_length=2, max_length=200)
    building_code: Optional[str] = Field(None, max_length=50)
    building_type: Optional[BuildingType] = BuildingType.RESIDENTIAL
    floors: Optional[int] = Field(None, ge=0)
    units: Optional[int] = Field(None, ge=0)
    year_built: Optional[int] = Field(None, ge=1800, le=2100)


class GateImportRow(BaseModel):
    """Gate import row schema."""
    client_name: str = Field(..., min_length=2, max_length=200)
    site_name: str = Field(..., min_length=2, max_length=200)
    building_name: str = Field(..., min_length=2, max_length=200)
    gate_name: str = Field(..., min_length=2, max_length=200)
    gate_code: Optional[str] = Field(None, max_length=50)
    gate_type: GateType = GateType.SWING
    manufacturer: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    installation_date: Optional[str] = None  # Will be parsed to datetime


class ImportResult(BaseModel):
    """Import operation result."""
    success: bool
    total_rows: int
    processed_rows: int
    skipped_rows: int
    errors: List[str] = []
    warnings: List[str] = []
    created_entities: Dict[str, List[int]] = {}  # Entity type -> list of created IDs