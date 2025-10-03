"""
Test endpoints for demonstrating error handling and validation.
"""

from typing import Optional
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, validator
from app.core.error_models import (
    ValidationException,
    NotFoundError,
    ConflictError,
    create_validation_error,
    create_multiple_field_errors,
    FieldError,
    ErrorCodes
)

router = APIRouter(prefix="/test", tags=["test"])


class TestUserCreate(BaseModel):
    """Test user creation model with validation."""
    
    name: str = Field(..., min_length=2, max_length=100, description="User name")
    email: str = Field(..., description="Email address")
    age: int = Field(..., ge=18, le=120, description="Age in years")
    phone: Optional[str] = Field(None, description="Phone number")
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.startswith('+'):
            raise ValueError('Phone number must start with +')
        return v


class TestUserResponse(BaseModel):
    """Test user response model."""
    
    id: int
    name: str
    email: str
    age: int
    phone: Optional[str] = None
    status: str = "active"


@router.post("/users", response_model=TestUserResponse)
async def create_test_user(user_data: TestUserCreate):
    """
    Create a test user - demonstrates validation error handling.
    
    This endpoint will trigger various validation errors for testing:
    - Missing required fields
    - Invalid field formats
    - Business logic violations
    """
    
    # Simulate business logic validation
    if user_data.email == "banned@example.com":
        raise ValidationException(
            message="Email address is banned",
            field_errors=[
                FieldError(
                    field="email",
                    message="This email address is not allowed",
                    code=ErrorCodes.FORBIDDEN_OPERATION,
                    value=user_data.email
                )
            ]
        )
    
    # Simulate duplicate check
    if user_data.email == "duplicate@example.com":
        raise ConflictError(
            message="User with this email already exists",
            details="A user account with this email address is already registered"
        )
    
    # Simulate multiple field errors
    if user_data.name.lower() == "invalid":
        errors = [
            ("name", "Name 'invalid' is not allowed", user_data.name),
            ("email", "Email domain not supported", user_data.email),
        ]
        raise create_multiple_field_errors(errors)
    
    # Return mock user data
    return TestUserResponse(
        id=12345,
        name=user_data.name,
        email=user_data.email,
        age=user_data.age,
        phone=user_data.phone
    )


@router.get("/users/{user_id}", response_model=TestUserResponse)
async def get_test_user(user_id: int):
    """
    Get a test user - demonstrates 404 error handling.
    """
    
    # Simulate user not found
    if user_id == 404:
        raise NotFoundError(
            message=f"User with ID {user_id} not found",
            resource_type="User"
        )
    
    # Return mock user data
    return TestUserResponse(
        id=user_id,
        name="Test User",
        email="test@example.com",
        age=30
    )


@router.post("/errors/validation")
async def trigger_validation_error():
    """
    Trigger a custom validation error for testing.
    """
    raise create_validation_error(
        field="test_field",
        message="This is a test validation error",
        value="invalid_value"
    )


@router.post("/errors/multiple")
async def trigger_multiple_errors():
    """
    Trigger multiple field validation errors for testing.
    """
    errors = [
        ("field1", "Field 1 is required", None),
        ("field2", "Field 2 has invalid format", "invalid_format"),
        ("field3", "Field 3 is out of range", 999),
    ]
    raise create_multiple_field_errors(errors)


@router.post("/errors/conflict")
async def trigger_conflict_error():
    """
    Trigger a conflict error for testing.
    """
    raise ConflictError(
        message="Resource already exists",
        details="A resource with the same identifier already exists in the system"
    )


@router.post("/errors/not-found")
async def trigger_not_found_error():
    """
    Trigger a not found error for testing.
    """
    raise NotFoundError(
        message="Test resource not found",
        resource_type="TestResource"
    )


@router.get("/errors/server")
async def trigger_server_error():
    """
    Trigger a server error for testing.
    """
    # This will be caught by the general exception handler
    raise Exception("This is a test server error")


class TestValidationModel(BaseModel):
    """Model with various validation rules for testing."""
    
    required_string: str = Field(..., description="Required string field")
    optional_string: Optional[str] = Field(None, description="Optional string field")
    positive_number: int = Field(..., gt=0, description="Must be positive")
    range_number: int = Field(..., ge=1, le=100, description="Must be between 1-100")
    email_field: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$', description="Valid email")
    phone_field: Optional[str] = Field(None, pattern=r'^\+\d{1,3}\d{4,14}$', description="Valid phone with +")


@router.post("/validation/complex")
async def test_complex_validation(data: TestValidationModel):
    """
    Test complex validation scenarios.
    
    Try sending:
    - Empty required fields
    - Invalid email formats
    - Numbers out of range
    - Invalid phone formats
    """
    
    return {
        "message": "Validation successful",
        "data": data.dict()
    }


@router.get("/validation/success")
async def validation_success():
    """
    Return a successful response for comparison.
    """
    
    return {
        "success": True,
        "error": False,
        "message": "Request processed successfully",
        "data": {
            "timestamp": "2024-01-01T00:00:00Z",
            "status": "ok"
        }
    }