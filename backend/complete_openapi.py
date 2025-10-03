"""
Complete GarageReg API with comprehensive OpenAPI documentation
"""
from fastapi import FastAPI, HTTPException, Request, Depends, status, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional, Any, Union
from datetime import datetime, date
from enum import Enum
import random

# ===== ENUMS =====

class UserRole(str, Enum):
    """User roles in the system."""
    admin = "admin"
    manager = "manager"
    user = "user" 
    readonly = "readonly"

class VehicleType(str, Enum):
    """Types of vehicles."""
    car = "car"
    truck = "truck"
    motorcycle = "motorcycle"
    van = "van"
    bus = "bus"
    other = "other"

class MaintenanceStatus(str, Enum):
    """Status of maintenance tasks."""
    scheduled = "scheduled"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"
    overdue = "overdue"

class MaintenanceType(str, Enum):
    """Types of maintenance operations."""
    oil_change = "oil_change"
    tire_rotation = "tire_rotation"
    brake_service = "brake_service"
    inspection = "inspection"
    repair = "repair"
    other = "other"

# ===== ERROR MODELS =====

class FieldError(BaseModel):
    """Individual field validation error."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "field": "email",
                "message": "Invalid email format",
                "code": "INVALID_FORMAT",
                "value": "not-an-email"
            }
        }
    )
    
    field: str = Field(..., description="Field name that caused the error")
    message: str = Field(..., description="Human-readable error message") 
    code: str = Field(..., description="Error code for programmatic handling")
    value: Optional[Any] = Field(None, description="The invalid value that was provided")

class ErrorResponse(BaseModel):
    """Standardized error response envelope."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "error": True,
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": "Request validation failed with 2 field errors",
                "field_errors": [
                    {
                        "field": "email",
                        "message": "Invalid email format",
                        "code": "INVALID_FORMAT", 
                        "value": "not-an-email"
                    }
                ],
                "path": "/api/users",
                "method": "POST",
                "timestamp": "2025-10-03T10:00:00Z"
            }
        }
    )
    
    success: bool = Field(False, description="Always false for error responses")
    error: bool = Field(True, description="Always true for error responses")
    code: str = Field(..., description="Error code for programmatic handling")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[str] = Field(None, description="Additional error details")
    field_errors: Optional[List[FieldError]] = Field(None, description="Field-specific validation errors")
    path: Optional[str] = Field(None, description="API path where error occurred")
    method: Optional[str] = Field(None, description="HTTP method")
    timestamp: Optional[str] = Field(None, description="ISO timestamp when error occurred")

# ===== REQUEST/RESPONSE MODELS =====

class UserCreateRequest(BaseModel):
    """Request model for creating a new user."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "john_doe",
                "email": "john.doe@example.com",
                "password": "securePassword123", 
                "full_name": "John Doe",
                "phone": "+36301234567",
                "role": "user"
            }
        }
    )
    
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r'^[a-zA-Z0-9_-]+$',
        description="Unique username (3-50 chars, alphanumeric, underscore, dash)",
        examples=["john_doe", "user123", "test-user"]
    )
    email: EmailStr = Field(
        ...,
        description="Valid email address",
        examples=["user@example.com", "test@garagereg.com"] 
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password (minimum 8 characters)",
        examples=["securePassword123"]
    )
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="User's full name",
        examples=["John Doe", "Jane Smith"]
    )
    phone: Optional[str] = Field(
        None,
        pattern=r'^\+\d{1,3}\d{4,14}$',
        description="Phone number in international format (+country code)",
        examples=["+36301234567", "+1234567890"]
    )
    role: UserRole = Field(
        UserRole.user,
        description="User role in the system"
    )

class UserResponse(BaseModel):
    """User response model."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 12345,
                "username": "john_doe",
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "phone": "+36301234567",
                "role": "user",
                "is_active": True,
                "created_at": "2025-10-03T10:00:00Z",
                "updated_at": "2025-10-03T10:00:00Z"
            }
        }
    )
    
    id: int = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Username")
    email: EmailStr = Field(..., description="Email address")
    full_name: str = Field(..., description="Full name")
    phone: Optional[str] = Field(None, description="Phone number")
    role: UserRole = Field(..., description="User role")
    is_active: bool = Field(..., description="Whether user account is active")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class VehicleCreateRequest(BaseModel):
    """Request model for registering a new vehicle."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "license_plate": "ABC-123",
                "make": "Toyota",
                "model": "Camry",
                "year": 2022,
                "vehicle_type": "car",
                "vin": "1HGBH41JXMN109186",
                "color": "Blue",
                "engine_size": "2.5L"
            }
        }
    )
    
    license_plate: str = Field(
        ...,
        min_length=2,
        max_length=20,
        description="Vehicle license plate number",
        examples=["ABC-123", "XYZ-789"]
    )
    make: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Vehicle manufacturer",
        examples=["Toyota", "Ford", "BMW"]
    )
    model: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Vehicle model",
        examples=["Camry", "F-150", "X3"]
    )
    year: int = Field(
        ...,
        ge=1900,
        le=2030,
        description="Manufacturing year",
        examples=[2022, 2023, 2024]
    )
    vehicle_type: VehicleType = Field(
        ...,
        description="Type of vehicle"
    )
    vin: Optional[str] = Field(
        None,
        min_length=17,
        max_length=17,
        pattern=r'^[A-HJ-NPR-Z0-9]{17}$',
        description="Vehicle Identification Number (17 characters)",
        examples=["1HGBH41JXMN109186"]
    )
    color: Optional[str] = Field(
        None,
        max_length=30,
        description="Vehicle color",
        examples=["Blue", "Red", "White", "Black"]
    )
    engine_size: Optional[str] = Field(
        None,
        max_length=20,
        description="Engine size/displacement",
        examples=["2.5L", "V6 3.0L", "1.6L Turbo"]
    )

class VehicleResponse(BaseModel):
    """Vehicle response model."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 67890,
                "license_plate": "ABC-123",
                "make": "Toyota",
                "model": "Camry",
                "year": 2022,
                "vehicle_type": "car",
                "vin": "1HGBH41JXMN109186",
                "color": "Blue",
                "engine_size": "2.5L",
                "owner_id": 12345,
                "created_at": "2025-10-03T10:00:00Z",
                "updated_at": "2025-10-03T10:00:00Z"
            }
        }
    )
    
    id: int = Field(..., description="Unique vehicle identifier")
    license_plate: str = Field(..., description="License plate number")
    make: str = Field(..., description="Vehicle manufacturer")
    model: str = Field(..., description="Vehicle model")
    year: int = Field(..., description="Manufacturing year")
    vehicle_type: VehicleType = Field(..., description="Type of vehicle")
    vin: Optional[str] = Field(None, description="Vehicle Identification Number")
    color: Optional[str] = Field(None, description="Vehicle color")
    engine_size: Optional[str] = Field(None, description="Engine size")
    owner_id: int = Field(..., description="ID of the vehicle owner")
    created_at: datetime = Field(..., description="Registration timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class LoginRequest(BaseModel):
    """Login request model."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "john_doe",
                "password": "securePassword123"
            }
        }
    )
    
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")

class LoginResponse(BaseModel):
    """Login response model."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "user": {
                    "id": 12345,
                    "username": "john_doe",
                    "email": "john.doe@example.com",
                    "full_name": "John Doe",
                    "role": "user"
                }
            }
        }
    )
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="Authenticated user information")

class SuccessResponse(BaseModel):
    """Generic success response."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {}
            }
        }
    )
    
    success: bool = Field(True, description="Always true for success responses")
    message: str = Field(..., description="Success message")
    data: Optional[Any] = Field(None, description="Response data")

class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 100,
                "page": 1,
                "per_page": 20,
                "pages": 5,
                "has_next": True,
                "has_prev": False
            }
        }
    )
    
    items: List[Any] = Field(..., description="List of items for current page")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")

# ===== ERROR HANDLING =====

class ErrorCodes:
    VALIDATION_ERROR = "VALIDATION_ERROR"
    REQUIRED_FIELD_MISSING = "REQUIRED_FIELD_MISSING"
    INVALID_INPUT = "INVALID_INPUT"
    INVALID_FORMAT = "INVALID_FORMAT"
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"

def create_error_response(
    request: Request,
    status_code: int,
    message: str,
    code: str,
    details: Optional[str] = None,
    field_errors: Optional[List[FieldError]] = None
) -> ErrorResponse:
    """Create standardized error response."""
    return ErrorResponse(
        code=code,
        message=message,
        details=details,
        field_errors=field_errors,
        path=str(request.url.path),
        method=request.method,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )

def convert_validation_errors(validation_error: RequestValidationError) -> List[FieldError]:
    """Convert FastAPI validation errors to our format."""
    field_errors = []
    for error in validation_error.errors():
        field_path = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        if not field_path:
            field_path = "root"
            
        error_type = error["type"]
        code = ErrorCodes.VALIDATION_ERROR
        if "missing" in error_type:
            code = ErrorCodes.REQUIRED_FIELD_MISSING
        elif "value_error" in error_type:
            code = ErrorCodes.INVALID_INPUT
        elif "type_error" in error_type:
            code = ErrorCodes.INVALID_FORMAT
            
        field_error = FieldError(
            field=field_path,
            message=error["msg"],
            code=code,
            value=error.get("input")
        )
        field_errors.append(field_error)
    
    return field_errors

# ===== CUSTOM OPENAPI =====

def custom_openapi():
    """Generate custom OpenAPI specification with enhanced metadata."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="GarageReg API",
        version="2.0.0",
        description="""
## 🚗 GarageReg API Documentation

A comprehensive garage registration and maintenance management system.

### Features
- **User Management**: Complete user registration and authentication
- **Vehicle Registration**: Add and manage vehicles with detailed information
- **Maintenance Tracking**: Schedule and track vehicle maintenance
- **Error Handling**: Standardized error responses with field-level validation
- **SDK Support**: Generated TypeScript and Python clients

### Authentication
Most endpoints require authentication. Use the `/auth/login` endpoint to obtain an access token.

### Error Handling
All errors follow a standardized format with proper HTTP status codes:
- **400**: Validation errors with field-specific details
- **401**: Authentication required
- **403**: Insufficient permissions
- **404**: Resource not found
- **409**: Resource conflict (e.g., duplicate email)
- **500**: Internal server error

### SDK Generation
This API supports automatic SDK generation for:
- **TypeScript/JavaScript**: For web and Node.js applications
- **Python**: For Python applications and integrations

Download generated SDKs from the `/sdk/` endpoints.
        """,
        routes=app.routes,
        tags=[
            {
                "name": "Authentication",
                "description": "User authentication and authorization endpoints"
            },
            {
                "name": "Users", 
                "description": "User management operations"
            },
            {
                "name": "Vehicles",
                "description": "Vehicle registration and management"
            },
            {
                "name": "Testing",
                "description": "Test endpoints for validation and error handling"
            }
        ]
    )
    
    # Add enhanced metadata
    openapi_schema["info"]["contact"] = {
        "name": "GarageReg API Support",
        "email": "support@garagereg.com",
        "url": "https://garagereg.com/support"
    }
    
    openapi_schema["info"]["license"] = {
        "name": "MIT License", 
        "url": "https://opensource.org/licenses/MIT"
    }
    
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8004",
            "description": "Development server"
        },
        {
            "url": "https://api.garagereg.com",
            "description": "Production server"
        }
    ]
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# ===== CREATE FASTAPI APP =====

app = FastAPI(
    title="GarageReg API",
    description="Comprehensive garage registration and maintenance management system",
    version="2.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url="/api/openapi.json"
)

# Set custom OpenAPI function
app.openapi = custom_openapi

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security scheme
security = HTTPBearer()

# ===== ERROR HANDLERS =====

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    field_errors = convert_validation_errors(exc)
    error_response = create_error_response(
        request=request,
        status_code=400,
        message="Validation failed",
        code=ErrorCodes.VALIDATION_ERROR,
        details=f"Request validation failed with {len(field_errors)} field errors",
        field_errors=field_errors
    )
    return JSONResponse(status_code=400, content=error_response.model_dump(exclude_none=True))

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    status_code_mapping = {
        401: ErrorCodes.AUTHENTICATION_REQUIRED,
        403: ErrorCodes.INSUFFICIENT_PERMISSIONS,
        404: ErrorCodes.RESOURCE_NOT_FOUND,
        409: ErrorCodes.RESOURCE_CONFLICT,
        500: ErrorCodes.INTERNAL_SERVER_ERROR,
    }
    
    code = status_code_mapping.get(exc.status_code, ErrorCodes.INTERNAL_SERVER_ERROR)
    error_response = create_error_response(
        request=request,
        status_code=exc.status_code,
        message=str(exc.detail),
        code=code
    )
    return JSONResponse(status_code=exc.status_code, content=error_response.model_dump(exclude_none=True))

# ===== API ENDPOINTS =====

# Authentication endpoints
@app.post(
    "/api/auth/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate user and obtain access token",
    tags=["Authentication"],
    responses={
        200: {"description": "Login successful", "model": LoginResponse},
        401: {"description": "Invalid credentials", "model": ErrorResponse},
        400: {"description": "Validation error", "model": ErrorResponse}
    }
)
async def login(credentials: LoginRequest):
    """
    Authenticate user with username/email and password.
    
    Returns JWT access token that should be included in subsequent requests.
    """
    if credentials.username in ["admin", "test", "demo"] and credentials.password == "password123":
        return LoginResponse(
            access_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.example.token",
            token_type="bearer",
            expires_in=3600,
            user=UserResponse(
                id=12345,
                username=credentials.username,
                email=f"{credentials.username}@garagereg.com",
                full_name=f"Demo {credentials.username.title()}",
                phone="+36301234567",
                role=UserRole.admin if credentials.username == "admin" else UserRole.user,
                is_active=True,
                created_at="2025-01-01T10:00:00Z",
                updated_at="2025-10-03T10:00:00Z"
            )
        )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password"
    )

# User endpoints
@app.post(
    "/api/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create New User",
    description="Register a new user account",
    tags=["Users"],
    responses={
        201: {"description": "User created successfully", "model": UserResponse},
        400: {"description": "Validation error", "model": ErrorResponse},
        409: {"description": "User already exists", "model": ErrorResponse}
    }
)
async def create_user(user: UserCreateRequest):
    """
    Create a new user account.
    
    - **username**: Must be unique, 3-50 characters, alphanumeric + underscore/dash
    - **email**: Must be valid email address and unique
    - **password**: Minimum 8 characters
    - **full_name**: User's display name
    - **phone**: Optional, international format
    - **role**: User role (default: user)
    """
    if user.username in ["admin", "test", "demo"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{user.username}' is already taken"
        )
    
    return UserResponse(
        id=random.randint(10000, 99999),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        role=user.role,
        is_active=True,
        created_at="2025-10-03T10:00:00Z",
        updated_at="2025-10-03T10:00:00Z"
    )

@app.get(
    "/api/users",
    response_model=PaginatedResponse,
    summary="List Users",
    description="Get paginated list of users",
    tags=["Users"],
    dependencies=[Depends(security)],
    responses={
        200: {"description": "Users retrieved successfully"},
        401: {"description": "Authentication required", "model": ErrorResponse}
    }
)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    role: Optional[UserRole] = Query(None, description="Filter by user role")
):
    """Get paginated list of users with optional filtering."""
    users = [
        UserResponse(
            id=12345,
            username="john_doe",
            email="john.doe@example.com",
            full_name="John Doe",
            phone="+36301234567",
            role=UserRole.user,
            is_active=True,
            created_at="2025-01-01T10:00:00Z",
            updated_at="2025-10-03T10:00:00Z"
        )
    ]
    
    return PaginatedResponse(
        items=users,
        total=100,
        page=page,
        per_page=per_page,
        pages=5,
        has_next=page < 5,
        has_prev=page > 1
    )

@app.get(
    "/api/users/{user_id}",
    response_model=UserResponse,
    summary="Get User by ID",
    description="Retrieve specific user information",
    tags=["Users"],
    dependencies=[Depends(security)],
    responses={
        200: {"description": "User found", "model": UserResponse},
        404: {"description": "User not found", "model": ErrorResponse},
        401: {"description": "Authentication required", "model": ErrorResponse}
    }
)
async def get_user(user_id: int = Path(..., description="Unique user identifier", example=12345)):
    """Get detailed information about a specific user."""
    if user_id == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return UserResponse(
        id=user_id,
        username="john_doe",
        email="john.doe@example.com",
        full_name="John Doe",
        phone="+36301234567",
        role=UserRole.user,
        is_active=True,
        created_at="2025-01-01T10:00:00Z",
        updated_at="2025-10-03T10:00:00Z"
    )

# Vehicle endpoints
@app.post(
    "/api/vehicles",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New Vehicle",
    description="Register a new vehicle in the system",
    tags=["Vehicles"],
    dependencies=[Depends(security)],
    responses={
        201: {"description": "Vehicle registered successfully", "model": VehicleResponse},
        400: {"description": "Validation error", "model": ErrorResponse},
        409: {"description": "Vehicle already exists", "model": ErrorResponse},
        401: {"description": "Authentication required", "model": ErrorResponse}
    }
)
async def register_vehicle(vehicle: VehicleCreateRequest):
    """Register a new vehicle in the system."""
    if vehicle.license_plate.upper() in ["ABC-123", "TEST-001"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Vehicle with license plate '{vehicle.license_plate}' is already registered"
        )
    
    return VehicleResponse(
        id=random.randint(60000, 99999),
        license_plate=vehicle.license_plate,
        make=vehicle.make,
        model=vehicle.model,
        year=vehicle.year,
        vehicle_type=vehicle.vehicle_type,
        vin=vehicle.vin,
        color=vehicle.color,
        engine_size=vehicle.engine_size,
        owner_id=12345,
        created_at="2025-10-03T10:00:00Z",
        updated_at="2025-10-03T10:00:00Z"
    )

# Testing endpoints
@app.post(
    "/api/test/validation/user",
    response_model=UserResponse,
    summary="Test User Validation",
    description="Test endpoint for user validation scenarios",
    tags=["Testing"],
    responses={
        200: {"description": "User validation passed", "model": UserResponse},
        400: {"description": "Validation failed", "model": ErrorResponse},
        409: {"description": "Username conflict", "model": ErrorResponse}
    }
)
async def test_user_validation(user: UserCreateRequest):
    """
    Test endpoint for user validation scenarios.
    
    Use this to test validation errors:
    - Try username 'admin' to trigger conflict
    - Send invalid email formats  
    - Use passwords shorter than 8 characters
    """
    if user.username.lower() in ["admin", "test", "demo"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{user.username}' is already taken"
        )
    
    return UserResponse(
        id=99999,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        role=user.role,
        is_active=True,
        created_at="2025-10-03T10:00:00Z",
        updated_at="2025-10-03T10:00:00Z"
    )

@app.get(
    "/api/test/errors/{error_type}",
    summary="Test Error Scenarios",
    description="Test endpoint for different error scenarios",
    tags=["Testing"],
    responses={
        400: {"description": "Bad Request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse},
        403: {"description": "Forbidden", "model": ErrorResponse},
        404: {"description": "Not Found", "model": ErrorResponse},
        409: {"description": "Conflict", "model": ErrorResponse},
        500: {"description": "Internal Server Error", "model": ErrorResponse}
    }
)
async def test_errors(error_type: str = Path(..., description="Type of error to simulate")):
    """Test different error scenarios for SDK testing."""
    error_map = {
        "validation": (400, "Validation error occurred"),
        "auth": (401, "Authentication required"),
        "forbidden": (403, "Access denied"),
        "not_found": (404, "Resource not found"),
        "conflict": (409, "Resource conflict"),
        "server": (500, "Internal server error")
    }
    
    if error_type not in error_map:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown error type '{error_type}'. Available: {list(error_map.keys())}"
        )
    
    status_code, message = error_map[error_type]
    raise HTTPException(status_code=status_code, detail=message)

# ===== DOCUMENTATION ENDPOINTS =====

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI with enhanced styling."""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """Custom ReDoc documentation."""
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.1.2/bundles/redoc.standalone.js",
        redoc_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )

@app.get("/", include_in_schema=False)
async def root():
    """Redirect to API documentation."""
    return RedirectResponse(url="/docs")

@app.get("/api", include_in_schema=False)
async def api_info():
    """API information and available endpoints."""
    return {
        "title": "GarageReg API",
        "version": "2.0.0",
        "description": "Comprehensive garage registration and maintenance management system",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/api/openapi.json"
        },
        "endpoints": {
            "authentication": "/api/auth/*",
            "users": "/api/users/*",
            "vehicles": "/api/vehicles/*",
            "testing": "/api/test/*"
        },
        "sdk": {
            "typescript": "/sdk/typescript/",
            "python": "/sdk/python/"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting GarageReg API with comprehensive OpenAPI documentation...")
    print("📚 API Documentation available at:")
    print("   - Swagger UI: http://127.0.0.1:8004/docs")
    print("   - ReDoc: http://127.0.0.1:8004/redoc")
    print("   - OpenAPI JSON: http://127.0.0.1:8004/api/openapi.json")
    print("\n🧪 Test endpoints:")
    print("   - User validation: POST /api/test/validation/user")
    print("   - Error scenarios: GET /api/test/errors/{type}")
    print("\n📦 SDK generation available at /sdk/")
    uvicorn.run(app, host="127.0.0.1", port=8004)