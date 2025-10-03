"""Pydantic models for GarageReg API."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from pydantic import BaseModel, Field, EmailStr


class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    MANAGER = "manager" 
    TECHNICIAN = "technician"
    VIEWER = "viewer"


class UserStatus(str, Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class VehicleStatus(str, Enum):
    """Vehicle status enumeration."""
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"
    RETIRED = "retired"


class FuelType(str, Enum):
    """Vehicle fuel type enumeration."""
    GASOLINE = "gasoline"
    DIESEL = "diesel"
    ELECTRIC = "electric"
    HYBRID = "hybrid"
    CNG = "cng"
    LPG = "lpg"


class TransmissionType(str, Enum):
    """Vehicle transmission type enumeration."""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    CVT = "cvt"


class ErrorLevel(str, Enum):
    """Error level enumeration."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# Request Models
class LoginRequest(BaseModel):
    """Login request model."""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")


class UserCreateRequest(BaseModel):
    """User creation request model."""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    full_name: str = Field(..., min_length=1, max_length=200, description="Full name")
    role: UserRole = Field(default=UserRole.VIEWER, description="User role")
    is_active: bool = Field(default=True, description="User active status")


class VehicleCreateRequest(BaseModel):
    """Vehicle creation request model."""
    license_plate: str = Field(..., min_length=1, max_length=20, description="License plate number")
    make: str = Field(..., min_length=1, max_length=50, description="Vehicle manufacturer")
    model: str = Field(..., min_length=1, max_length=50, description="Vehicle model")
    year: int = Field(..., ge=1900, le=2030, description="Manufacturing year")
    color: Optional[str] = Field(None, max_length=30, description="Vehicle color")
    vin: Optional[str] = Field(None, min_length=17, max_length=17, description="Vehicle Identification Number")
    owner_id: int = Field(..., description="Owner user ID")
    fuel_type: Optional[FuelType] = Field(None, description="Fuel type")
    transmission: Optional[TransmissionType] = Field(None, description="Transmission type")
    mileage: Optional[int] = Field(None, ge=0, description="Current mileage")


# Response Models
class UserResponse(BaseModel):
    """User response model."""
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    full_name: str = Field(..., description="Full name")
    role: UserRole = Field(..., description="User role")
    is_active: bool = Field(..., description="Active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class VehicleResponse(BaseModel):
    """Vehicle response model."""
    id: int = Field(..., description="Vehicle ID")
    license_plate: str = Field(..., description="License plate")
    make: str = Field(..., description="Manufacturer")
    model: str = Field(..., description="Model")
    year: int = Field(..., description="Year")
    color: Optional[str] = Field(None, description="Color")
    vin: Optional[str] = Field(None, description="VIN")
    owner_id: int = Field(..., description="Owner ID")
    fuel_type: Optional[FuelType] = Field(None, description="Fuel type")
    transmission: Optional[TransmissionType] = Field(None, description="Transmission")
    mileage: Optional[int] = Field(None, description="Mileage")
    status: VehicleStatus = Field(..., description="Vehicle status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="User information")


class ErrorFieldResponse(BaseModel):
    """Field error response model."""
    field: str = Field(..., description="Field name with error")
    message: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")


class ErrorResponse(BaseModel):
    """API error response model."""
    message: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    field_errors: Optional[List[ErrorFieldResponse]] = Field(
        None, description="Field-specific errors"
    )
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class PaginatedResponse(BaseModel):
    """Paginated response model."""
    items: List[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")


# Query parameter models
class UserListParams(BaseModel):
    """User list query parameters."""
    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=100, ge=1, le=1000, description="Number of items to return")
    search: Optional[str] = Field(None, description="Search term")
    role: Optional[UserRole] = Field(None, description="Filter by role")
    is_active: Optional[bool] = Field(None, description="Filter by active status")


class VehicleListParams(BaseModel):
    """Vehicle list query parameters."""
    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=100, ge=1, le=1000, description="Number of items to return")
    search: Optional[str] = Field(None, description="Search term")
    owner_id: Optional[int] = Field(None, description="Filter by owner ID")
    make: Optional[str] = Field(None, description="Filter by make")
    model: Optional[str] = Field(None, description="Filter by model")
    year: Optional[int] = Field(None, description="Filter by year")
    status: Optional[VehicleStatus] = Field(None, description="Filter by status")


# Configuration models
class APIConfig(BaseModel):
    """API client configuration."""
    base_url: str = Field(..., description="API base URL")
    timeout: float = Field(default=30.0, description="Request timeout in seconds")
    headers: Optional[Dict[str, str]] = Field(None, description="Additional headers")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")