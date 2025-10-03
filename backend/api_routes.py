"""
API Routes with comprehensive OpenAPI documentation
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from fastapi.security import HTTPBearer
from typing import List, Optional
from datetime import date
import random

# Import models - these will be available when imported into the main app

# Security scheme
security = HTTPBearer()

# ===== AUTHENTICATION ROUTER =====

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate user and obtain access token",
    responses={
        200: {
            "description": "Login successful",
            "model": LoginResponse
        },
        401: {
            "description": "Invalid credentials",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": True,
                        "code": "AUTHENTICATION_REQUIRED",
                        "message": "Invalid username or password",
                        "path": "/auth/login",
                        "method": "POST",
                        "timestamp": "2025-10-03T10:00:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Validation error",
            "model": ErrorResponse
        }
    }
)
async def login(credentials: LoginRequest):
    """
    Authenticate user with username/email and password.
    
    Returns JWT access token that should be included in subsequent requests.
    """
    # Simulate authentication
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

@auth_router.post(
    "/logout",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="User Logout",
    description="Invalidate the current access token",
    dependencies=[Depends(security)]
)
async def logout():
    """
    Logout current user and invalidate access token.
    
    Requires valid JWT token in Authorization header.
    """
    return SuccessResponse(
        message="Logout successful"
    )

# ===== USERS ROUTER =====

users_router = APIRouter(prefix="/users", tags=["Users"])

@users_router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create New User",
    description="Register a new user account",
    responses={
        201: {
            "description": "User created successfully",
            "model": UserResponse
        },
        400: {
            "description": "Validation error", 
            "model": ErrorResponse
        },
        409: {
            "description": "User already exists",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": True,
                        "code": "RESOURCE_CONFLICT",
                        "message": "Username 'john_doe' is already taken",
                        "details": "A user with this username already exists",
                        "path": "/users",
                        "method": "POST",
                        "timestamp": "2025-10-03T10:00:00Z"
                    }
                }
            }
        }
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
    # Simulate conflict check
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

@users_router.get(
    "/",
    response_model=PaginatedResponse,
    summary="List Users",
    description="Get paginated list of users",
    dependencies=[Depends(security)],
    responses={
        200: {
            "description": "Users retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "id": 12345,
                                "username": "john_doe",
                                "email": "john.doe@example.com",
                                "full_name": "John Doe",
                                "phone": "+36301234567",
                                "role": "user",
                                "is_active": True,
                                "created_at": "2025-01-01T10:00:00Z",
                                "updated_at": "2025-10-03T10:00:00Z"
                            }
                        ],
                        "total": 100,
                        "page": 1,
                        "per_page": 20,
                        "pages": 5,
                        "has_next": True,
                        "has_prev": False
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "model": ErrorResponse
        }
    }
)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    search: Optional[str] = Query(None, description="Search in username, email, or full name")
):
    """
    Get paginated list of users with optional filtering.
    
    Supports:
    - Pagination with page and per_page parameters
    - Role-based filtering
    - Text search in username, email, and full name
    """
    # Mock data
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

@users_router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get User by ID",
    description="Retrieve specific user information",
    dependencies=[Depends(security)],
    responses={
        200: {
            "description": "User found",
            "model": UserResponse
        },
        404: {
            "description": "User not found",
            "model": ErrorResponse
        },
        401: {
            "description": "Authentication required",
            "model": ErrorResponse
        }
    }
)
async def get_user(
    user_id: int = Path(..., description="Unique user identifier", example=12345)
):
    """
    Get detailed information about a specific user.
    
    Returns complete user profile including contact information and role.
    """
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

# ===== VEHICLES ROUTER =====

vehicles_router = APIRouter(prefix="/vehicles", tags=["Vehicles"])

@vehicles_router.post(
    "/",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New Vehicle",
    description="Register a new vehicle in the system",
    dependencies=[Depends(security)],
    responses={
        201: {
            "description": "Vehicle registered successfully",
            "model": VehicleResponse
        },
        400: {
            "description": "Validation error",
            "model": ErrorResponse
        },
        409: {
            "description": "Vehicle already exists",
            "model": ErrorResponse
        },
        401: {
            "description": "Authentication required",
            "model": ErrorResponse
        }
    }
)
async def register_vehicle(vehicle: VehicleCreateRequest):
    """
    Register a new vehicle in the system.
    
    - **license_plate**: Unique vehicle identifier
    - **make**: Vehicle manufacturer (e.g., Toyota, Ford)
    - **model**: Vehicle model (e.g., Camry, F-150)
    - **year**: Manufacturing year (1900-2030)
    - **vehicle_type**: Type of vehicle (car, truck, motorcycle, etc.)
    - **vin**: Optional 17-character Vehicle Identification Number
    - **color**: Optional vehicle color
    - **engine_size**: Optional engine size specification
    """
    # Simulate duplicate check
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
        owner_id=12345,  # Mock owner ID
        created_at="2025-10-03T10:00:00Z",
        updated_at="2025-10-03T10:00:00Z"
    )

@vehicles_router.get(
    "/",
    response_model=PaginatedResponse,
    summary="List Vehicles",
    description="Get paginated list of vehicles",
    dependencies=[Depends(security)],
    responses={
        200: {
            "description": "Vehicles retrieved successfully"
        },
        401: {
            "description": "Authentication required",
            "model": ErrorResponse
        }
    }
)
async def list_vehicles(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    vehicle_type: Optional[VehicleType] = Query(None, description="Filter by vehicle type"),
    make: Optional[str] = Query(None, description="Filter by manufacturer"),
    owner_id: Optional[int] = Query(None, description="Filter by owner ID")
):
    """
    Get paginated list of vehicles with optional filtering.
    
    Supports filtering by:
    - Vehicle type (car, truck, motorcycle, etc.)
    - Manufacturer/make
    - Owner ID
    """
    # Mock data
    vehicles = [
        VehicleResponse(
            id=67890,
            license_plate="ABC-123",
            make="Toyota",
            model="Camry", 
            year=2022,
            vehicle_type=VehicleType.car,
            vin="1HGBH41JXMN109186",
            color="Blue",
            engine_size="2.5L",
            owner_id=12345,
            created_at="2025-01-01T10:00:00Z",
            updated_at="2025-10-03T10:00:00Z"
        )
    ]
    
    return PaginatedResponse(
        items=vehicles,
        total=50,
        page=page,
        per_page=per_page,
        pages=3,
        has_next=page < 3,
        has_prev=page > 1
    )

@vehicles_router.get(
    "/{vehicle_id}",
    response_model=VehicleResponse,
    summary="Get Vehicle by ID",
    description="Retrieve specific vehicle information",
    dependencies=[Depends(security)],
    responses={
        200: {
            "description": "Vehicle found",
            "model": VehicleResponse
        },
        404: {
            "description": "Vehicle not found",
            "model": ErrorResponse
        },
        401: {
            "description": "Authentication required",
            "model": ErrorResponse
        }
    }
)
async def get_vehicle(
    vehicle_id: int = Path(..., description="Unique vehicle identifier", example=67890)
):
    """
    Get detailed information about a specific vehicle.
    
    Returns complete vehicle information including registration details and owner.
    """
    if vehicle_id == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with ID {vehicle_id} not found"
        )
    
    return VehicleResponse(
        id=vehicle_id,
        license_plate="ABC-123",
        make="Toyota",
        model="Camry",
        year=2022,
        vehicle_type=VehicleType.car,
        vin="1HGBH41JXMN109186",
        color="Blue",
        engine_size="2.5L",
        owner_id=12345,
        created_at="2025-01-01T10:00:00Z",
        updated_at="2025-10-03T10:00:00Z"
    )

# ===== MAINTENANCE ROUTER =====

maintenance_router = APIRouter(prefix="/maintenance", tags=["Maintenance"])

@maintenance_router.post(
    "/",
    response_model=MaintenanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Schedule Maintenance",
    description="Schedule new maintenance for a vehicle",
    dependencies=[Depends(security)],
    responses={
        201: {
            "description": "Maintenance scheduled successfully",
            "model": MaintenanceResponse
        },
        400: {
            "description": "Validation error",
            "model": ErrorResponse
        },
        404: {
            "description": "Vehicle not found",
            "model": ErrorResponse
        },
        401: {
            "description": "Authentication required", 
            "model": ErrorResponse
        }
    }
)
async def schedule_maintenance(maintenance: MaintenanceCreateRequest):
    """
    Schedule maintenance for a vehicle.
    
    - **vehicle_id**: ID of the vehicle requiring maintenance
    - **maintenance_type**: Type of maintenance (oil_change, brake_service, etc.)
    - **description**: Detailed description of work to be performed
    - **scheduled_date**: When the maintenance should be performed
    - **estimated_cost**: Optional estimated cost
    - **notes**: Optional additional notes or instructions
    """
    return MaintenanceResponse(
        id=random.randint(10000, 99999),
        vehicle_id=maintenance.vehicle_id,
        maintenance_type=maintenance.maintenance_type,
        description=maintenance.description,
        status=MaintenanceStatus.scheduled,
        scheduled_date=maintenance.scheduled_date,
        completed_date=None,
        estimated_cost=maintenance.estimated_cost,
        actual_cost=None,
        notes=maintenance.notes,
        created_at="2025-10-03T10:00:00Z",
        updated_at="2025-10-03T10:00:00Z"
    )

@maintenance_router.get(
    "/",
    response_model=PaginatedResponse,
    summary="List Maintenance Records",
    description="Get paginated list of maintenance records",
    dependencies=[Depends(security)],
    responses={
        200: {
            "description": "Maintenance records retrieved successfully"
        },
        401: {
            "description": "Authentication required",
            "model": ErrorResponse
        }
    }
)
async def list_maintenance(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    vehicle_id: Optional[int] = Query(None, description="Filter by vehicle ID"),
    status: Optional[MaintenanceStatus] = Query(None, description="Filter by status"),
    maintenance_type: Optional[MaintenanceType] = Query(None, description="Filter by type")
):
    """
    Get paginated list of maintenance records with optional filtering.
    
    Supports filtering by:
    - Vehicle ID
    - Maintenance status
    - Maintenance type
    """
    # Mock data
    records = [
        MaintenanceResponse(
            id=11111,
            vehicle_id=67890,
            maintenance_type=MaintenanceType.oil_change,
            description="Regular oil change and filter replacement",
            status=MaintenanceStatus.scheduled,
            scheduled_date="2025-10-15",
            completed_date=None,
            estimated_cost=75.50,
            actual_cost=None,
            notes="Use synthetic oil",
            created_at="2025-10-03T10:00:00Z",
            updated_at="2025-10-03T10:00:00Z"
        )
    ]
    
    return PaginatedResponse(
        items=records,
        total=25,
        page=page,
        per_page=per_page,
        pages=2,
        has_next=page < 2,
        has_prev=page > 1
    )

@maintenance_router.get(
    "/{maintenance_id}",
    response_model=MaintenanceResponse,
    summary="Get Maintenance Record by ID",
    description="Retrieve specific maintenance record",
    dependencies=[Depends(security)],
    responses={
        200: {
            "description": "Maintenance record found",
            "model": MaintenanceResponse
        },
        404: {
            "description": "Maintenance record not found",
            "model": ErrorResponse
        },
        401: {
            "description": "Authentication required",
            "model": ErrorResponse
        }
    }
)
async def get_maintenance(
    maintenance_id: int = Path(..., description="Unique maintenance record identifier", example=11111)
):
    """
    Get detailed information about a specific maintenance record.
    
    Returns complete maintenance information including status and cost details.
    """
    if maintenance_id == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Maintenance record with ID {maintenance_id} not found"
        )
    
    return MaintenanceResponse(
        id=maintenance_id,
        vehicle_id=67890,
        maintenance_type=MaintenanceType.oil_change,
        description="Regular oil change and filter replacement",
        status=MaintenanceStatus.completed,
        scheduled_date="2025-10-15",
        completed_date="2025-10-15",
        estimated_cost=75.50,
        actual_cost=78.25,
        notes="Used synthetic oil as requested",
        created_at="2025-10-03T10:00:00Z",
        updated_at="2025-10-15T14:30:00Z"
    )

# ===== TESTING ROUTER =====

testing_router = APIRouter(prefix="/test", tags=["Testing"])

@testing_router.post(
    "/validation/user",
    response_model=UserResponse,
    summary="Test User Validation",
    description="Test endpoint for user validation scenarios",
    responses={
        200: {
            "description": "User validation passed",
            "model": UserResponse
        },
        400: {
            "description": "Validation failed",
            "model": ErrorResponse
        },
        409: {
            "description": "Username conflict",
            "model": ErrorResponse
        }
    }
)
async def test_user_validation(user: UserCreateRequest):
    """
    Test endpoint for user validation scenarios.
    
    Use this endpoint to test various validation error cases:
    - Try username 'admin' to trigger conflict
    - Send invalid email formats
    - Use passwords shorter than 8 characters
    - Test with missing required fields
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

@testing_router.get(
    "/errors/{error_type}",
    summary="Test Error Scenarios",
    description="Test endpoint for different error scenarios",
    responses={
        400: {"description": "Bad Request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse},
        403: {"description": "Forbidden", "model": ErrorResponse},
        404: {"description": "Not Found", "model": ErrorResponse},
        409: {"description": "Conflict", "model": ErrorResponse},
        500: {"description": "Internal Server Error", "model": ErrorResponse}
    }
)
async def test_errors(
    error_type: str = Path(..., description="Type of error to simulate", example="validation")
):
    """
    Test different error scenarios for SDK and error handling testing.
    
    Available error types:
    - **validation**: 400 Bad Request
    - **auth**: 401 Unauthorized
    - **forbidden**: 403 Forbidden
    - **not_found**: 404 Not Found
    - **conflict**: 409 Conflict
    - **server**: 500 Internal Server Error
    """
    error_map = {
        "validation": (400, "Validation error occurred"),
        "auth": (401, "Authentication required"),
        "forbidden": (403, "Access denied"),
        "not_found": (404, f"Resource not found"),
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