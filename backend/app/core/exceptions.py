"""
Consistent Error Models and Handlers for API responses.
Provides standardized error envelope structure and global error handling.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import structlog


logger = structlog.get_logger(__name__)


class FieldError(BaseModel):
    """Individual field validation error."""
    field: str = Field(..., description="Field name that caused the error")
    message: str = Field(..., description="Human-readable error message")
    code: str = Field(..., description="Error code for programmatic handling")
    value: Optional[Any] = Field(None, description="The invalid value that was provided")


class ErrorResponse(BaseModel):
    """Standardized error response envelope."""
    
    # Core error information
    success: bool = Field(False, description="Always false for error responses")
    error: bool = Field(True, description="Always true for error responses")
    
    # Error details
    code: str = Field(..., description="Error code for programmatic handling")
    message: str = Field(..., description="Human-readable error message")
    
    # Optional detailed information
    details: Optional[str] = Field(None, description="Additional error details")
    field_errors: Optional[List[FieldError]] = Field(None, description="Field-specific validation errors")
    
    # Request context
    path: Optional[str] = Field(None, description="API path where error occurred")
    method: Optional[str] = Field(None, description="HTTP method")
    timestamp: Optional[str] = Field(None, description="ISO timestamp when error occurred")
    
    # Debug information (only in development)
    debug_info: Optional[Dict[str, Any]] = Field(None, description="Debug information")


class ErrorCodes:
    """Standardized error codes for consistent error handling."""
    
    # Validation errors (400 range)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    REQUIRED_FIELD_MISSING = "REQUIRED_FIELD_MISSING"
    INVALID_FORMAT = "INVALID_FORMAT"
    OUT_OF_RANGE = "OUT_OF_RANGE"
    
    # Authentication errors (401 range)
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    
    # Authorization errors (403 range)
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    ACCESS_DENIED = "ACCESS_DENIED"
    FORBIDDEN_OPERATION = "FORBIDDEN_OPERATION"
    
    # Resource errors (404 range)
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    ENDPOINT_NOT_FOUND = "ENDPOINT_NOT_FOUND"
    
    # Conflict errors (409 range)
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    DUPLICATE_RESOURCE = "DUPLICATE_RESOURCE"
    RESOURCE_LOCKED = "RESOURCE_LOCKED"
    
    # Server errors (500 range)
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"


class APIException(HTTPException):
    """Enhanced HTTPException with error code and field errors support."""
    
    def __init__(
        self,
        status_code: int,
        message: str,
        code: str = ErrorCodes.INTERNAL_SERVER_ERROR,
        details: Optional[str] = None,
        field_errors: Optional[List[FieldError]] = None,
        debug_info: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=message)
        self.code = code
        self.message = message
        self.details = details
        self.field_errors = field_errors or []
        self.debug_info = debug_info


class ValidationException(APIException):
    """Validation-specific exception with field error support."""
    
    def __init__(
        self,
        message: str = "Validation failed",
        field_errors: Optional[List[FieldError]] = None,
        details: Optional[str] = None
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            code=ErrorCodes.VALIDATION_ERROR,
            details=details,
            field_errors=field_errors
        )


# Pre-defined common exceptions for easy use
class AuthenticationError(APIException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            code=ErrorCodes.AUTHENTICATION_REQUIRED
        )


class AuthorizationError(APIException):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Access denied", error_code: str = "AUTHORIZATION_ERROR"):
        super().__init__(message, error_code)


class DatabaseError(GarageRegException):
    """Raised when database operations fail."""
    
    def __init__(self, message: str, operation: str = None, error_code: str = "DATABASE_ERROR"):
        self.operation = operation
        super().__init__(message, error_code)


class ConfigurationError(GarageRegException):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str, setting: str = None, error_code: str = "CONFIG_ERROR"):
        self.setting = setting
        super().__init__(message, error_code)


class ExternalServiceError(GarageRegException):
    """Raised when external service calls fail."""
    
    def __init__(self, message: str, service: str = None, error_code: str = "EXTERNAL_SERVICE_ERROR"):
        self.service = service
        super().__init__(message, error_code)


class RateLimitError(GarageRegException):
    """Raised when rate limits are exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", error_code: str = "RATE_LIMIT_ERROR"):
        super().__init__(message, error_code)


class DuplicateError(GarageRegException):
    """Raised when attempting to create duplicate resources."""
    
    def __init__(self, message: str, field: str = None, error_code: str = "DUPLICATE_ERROR"):
        self.field = field
        super().__init__(message, error_code)


class StateTransitionError(BusinessLogicError):
    """Raised when invalid state transitions are attempted."""
    
    def __init__(self, message: str, from_state: str = None, to_state: str = None):
        self.from_state = from_state
        self.to_state = to_state
        super().__init__(message, "state_transition", "STATE_TRANSITION_ERROR")


class SLAViolationError(BusinessLogicError):
    """Raised when SLA requirements are violated."""
    
    def __init__(self, message: str, sla_type: str = None):
        self.sla_type = sla_type
        super().__init__(message, "sla_violation", "SLA_VIOLATION_ERROR")


class InventoryError(BusinessLogicError):
    """Raised when inventory operations fail."""
    
    def __init__(self, message: str, part_id: int = None):
        self.part_id = part_id
        super().__init__(message, "inventory", "INVENTORY_ERROR")


# HTTP Exception Converters
def convert_to_http_exception(exc: GarageRegException) -> HTTPException:
    """Convert custom exceptions to HTTP exceptions."""
    
    status_code_map = {
        "VALIDATION_ERROR": 400,
        "NOT_FOUND": 404,
        "AUTH_ERROR": 401,
        "AUTHORIZATION_ERROR": 403,
        "BUSINESS_LOGIC_ERROR": 422,
        "STATE_TRANSITION_ERROR": 422,
        "SLA_VIOLATION_ERROR": 422,
        "INVENTORY_ERROR": 422,
        "DUPLICATE_ERROR": 409,
        "RATE_LIMIT_ERROR": 429,
        "DATABASE_ERROR": 500,
        "CONFIG_ERROR": 500,
        "EXTERNAL_SERVICE_ERROR": 502,
    }
    
    status_code = status_code_map.get(exc.error_code, 500)
    
    detail = {
        "message": exc.message,
        "error_code": exc.error_code
    }
    
    # Add specific fields for certain exception types
    if isinstance(exc, ValidationError) and exc.field:
        detail["field"] = exc.field
    elif isinstance(exc, NotFoundError) and exc.resource_type:
        detail["resource_type"] = exc.resource_type
    elif isinstance(exc, StateTransitionError):
        detail["from_state"] = exc.from_state
        detail["to_state"] = exc.to_state
    elif isinstance(exc, SLAViolationError):
        detail["sla_type"] = exc.sla_type
    elif isinstance(exc, InventoryError) and exc.part_id:
        detail["part_id"] = exc.part_id
    
    return HTTPException(status_code=status_code, detail=detail)