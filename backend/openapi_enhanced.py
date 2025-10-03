"""
GarageReg API with comprehensive OpenAPI documentation and SDK support
"""
from fastapi import FastAPI, HTTPException, Request, Depends, status, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional, Any, Union
from datetime import datetime, date
from enum import Enum
import json

# ===== OPENAPI CONFIGURATION =====

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
- **Multilingual**: Hungarian and English language support

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

### SDK Support
Generated SDKs are available for:
- **TypeScript/JavaScript**: For web and Node.js applications
- **Python**: For Python applications and integrations
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
                "name": "Maintenance",
                "description": "Maintenance scheduling and tracking"
            },
            {
                "name": "Testing",
                "description": "Test endpoints for validation and error handling"
            }
        ]
    )
    
    # Add custom properties
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
            "url": "http://localhost:8003",
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
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API Key for service-to-service communication"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# ===== ENUMS FOR BETTER API DOCUMENTATION =====

class UserRole(str, Enum):
    """User roles in the system."""
    admin = "admin"
    manager = "manager" 
    user = "user"
    readonly = "readonly"

class VehicleType(str, Enum):
    """Types of vehicles that can be registered."""
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

class MaintenanceCreateRequest(BaseModel):
    """Request model for scheduling maintenance."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "vehicle_id": 67890,
                "maintenance_type": "oil_change", 
                "description": "Regular oil change and filter replacement",
                "scheduled_date": "2025-10-15",
                "estimated_cost": 75.50,
                "notes": "Use synthetic oil"
            }
        }
    )
    
    vehicle_id: int = Field(..., description="ID of the vehicle")
    maintenance_type: MaintenanceType = Field(..., description="Type of maintenance")
    description: str = Field(
        ..., 
        min_length=5, 
        max_length=500,
        description="Detailed description of maintenance work",
        examples=["Oil change and filter replacement", "Brake pad replacement"]
    )
    scheduled_date: date = Field(..., description="Scheduled date for maintenance")
    estimated_cost: Optional[float] = Field(
        None, 
        ge=0,
        description="Estimated cost in currency units",
        examples=[75.50, 150.00, 300.25]
    )
    notes: Optional[str] = Field(
        None, 
        max_length=1000,
        description="Additional notes or instructions"
    )

class MaintenanceResponse(BaseModel):
    """Maintenance record response model.""" 
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 11111,
                "vehicle_id": 67890,
                "maintenance_type": "oil_change",
                "description": "Regular oil change and filter replacement",
                "status": "scheduled",
                "scheduled_date": "2025-10-15",
                "completed_date": None,
                "estimated_cost": 75.50,
                "actual_cost": None,
                "notes": "Use synthetic oil",
                "created_at": "2025-10-03T10:00:00Z",
                "updated_at": "2025-10-03T10:00:00Z"
            }
        }
    )
    
    id: int = Field(..., description="Unique maintenance record identifier")
    vehicle_id: int = Field(..., description="ID of the vehicle")
    maintenance_type: MaintenanceType = Field(..., description="Type of maintenance")
    description: str = Field(..., description="Description of maintenance work")
    status: MaintenanceStatus = Field(..., description="Current status")
    scheduled_date: date = Field(..., description="Scheduled date")
    completed_date: Optional[date] = Field(None, description="Actual completion date")
    estimated_cost: Optional[float] = Field(None, description="Estimated cost")
    actual_cost: Optional[float] = Field(None, description="Actual cost")
    notes: Optional[str] = Field(None, description="Additional notes")
    created_at: datetime = Field(..., description="Creation timestamp")
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

# ===== SUCCESS RESPONSE MODELS =====

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

# ===== CREATE FASTAPI APP =====

app = FastAPI(
    title="GarageReg API",
    description="Comprehensive garage registration and maintenance management system",
    version="2.0.0",
    docs_url=None,  # Disable default docs to use custom ones
    redoc_url=None,  # Disable default redoc to use custom ones
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

# ===== ERROR HANDLERS =====

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

# ===== INCLUDE API ROUTES =====

# Import and include routers
try:
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from api_routes import auth_router, users_router, vehicles_router, maintenance_router, testing_router
    
    app.include_router(auth_router, prefix="/api")
    app.include_router(users_router, prefix="/api")
    app.include_router(vehicles_router, prefix="/api")
    app.include_router(maintenance_router, prefix="/api")
    app.include_router(testing_router, prefix="/api")
    print("✅ API routes loaded successfully")
except ImportError as e:
    print(f"⚠️ API routes not found: {e}")
    print("Running with basic endpoints only")

# ===== CUSTOM DOCUMENTATION ENDPOINTS =====

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
    """API root with links to documentation."""
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
            "maintenance": "/api/maintenance/*",
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
    print("   - Swagger UI: http://127.0.0.1:8003/docs")
    print("   - ReDoc: http://127.0.0.1:8003/redoc") 
    print("   - OpenAPI JSON: http://127.0.0.1:8003/api/openapi.json")
    uvicorn.run(app, host="127.0.0.1", port=8004)