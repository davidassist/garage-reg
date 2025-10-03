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
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            code=ErrorCodes.INSUFFICIENT_PERMISSIONS
        )


class NotFoundError(APIException):
    def __init__(self, message: str = "Resource not found", resource_type: str = "Resource"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            code=ErrorCodes.RESOURCE_NOT_FOUND,
            details=f"{resource_type} was not found"
        )


class ConflictError(APIException):
    def __init__(self, message: str = "Resource conflict", details: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=message,
            code=ErrorCodes.RESOURCE_CONFLICT,
            details=details
        )


class DatabaseError(APIException):
    def __init__(self, message: str = "Database operation failed", operation: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message,
            code=ErrorCodes.DATABASE_ERROR,
            details=f"Database operation failed: {operation}" if operation else None
        )


class ExternalServiceError(APIException):
    def __init__(self, message: str = "External service error", service: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            message=message,
            code=ErrorCodes.EXTERNAL_SERVICE_ERROR,
            details=f"External service '{service}' error" if service else None
        )


def create_error_response(
    request: Request,
    status_code: int,
    message: str,
    code: str = ErrorCodes.INTERNAL_SERVER_ERROR,
    details: Optional[str] = None,
    field_errors: Optional[List[FieldError]] = None,
    debug_info: Optional[Dict[str, Any]] = None
) -> ErrorResponse:
    """Create a standardized error response."""
    
    from datetime import datetime
    
    return ErrorResponse(
        code=code,
        message=message,
        details=details,
        field_errors=field_errors,
        path=str(request.url.path),
        method=request.method,
        timestamp=datetime.utcnow().isoformat() + "Z",
        debug_info=debug_info
    )


def convert_validation_error(validation_error: RequestValidationError) -> List[FieldError]:
    """Convert FastAPI validation errors to our FieldError format."""
    
    field_errors = []
    
    for error in validation_error.errors():
        # Extract field path
        field_path = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        if not field_path:
            field_path = "root"
        
        # Map error types to our error codes
        error_type = error["type"]
        error_code_mapping = {
            "missing": ErrorCodes.REQUIRED_FIELD_MISSING,
            "value_error": ErrorCodes.INVALID_INPUT,
            "type_error": ErrorCodes.INVALID_FORMAT,
            "assertion_error": ErrorCodes.VALIDATION_ERROR,
        }
        
        # Get appropriate error code
        code = ErrorCodes.VALIDATION_ERROR
        for err_type, err_code in error_code_mapping.items():
            if err_type in error_type:
                code = err_code
                break
        
        # Create field error
        field_error = FieldError(
            field=field_path,
            message=error["msg"],
            code=code,
            value=error.get("input")
        )
        
        field_errors.append(field_error)
    
    return field_errors


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Handle our custom API exceptions."""
    
    logger.error(
        "API Exception",
        status_code=exc.status_code,
        error_code=exc.code,
        message=exc.message,
        path=request.url.path,
        method=request.method
    )
    
    error_response = create_error_response(
        request=request,
        status_code=exc.status_code,
        message=exc.message,
        code=exc.code,
        details=exc.details,
        field_errors=exc.field_errors,
        debug_info=exc.debug_info
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(exclude_none=True)
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle FastAPI validation errors."""
    
    field_errors = convert_validation_error(exc)
    
    logger.warning(
        "Validation Error", 
        path=request.url.path,
        method=request.method,
        field_errors=[fe.model_dump() for fe in field_errors]
    )
    
    error_response = create_error_response(
        request=request,
        status_code=status.HTTP_400_BAD_REQUEST,
        message="Validation failed",
        code=ErrorCodes.VALIDATION_ERROR,
        details=f"Request validation failed with {len(field_errors)} field errors",
        field_errors=field_errors
    )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_response.model_dump(exclude_none=True)
    )


async def http_exception_handler(request: Request, exc: Union[HTTPException, StarletteHTTPException]) -> JSONResponse:
    """Handle standard HTTP exceptions."""
    
    # Map HTTP status codes to our error codes
    status_code_mapping = {
        401: ErrorCodes.AUTHENTICATION_REQUIRED,
        403: ErrorCodes.INSUFFICIENT_PERMISSIONS,
        404: ErrorCodes.RESOURCE_NOT_FOUND,
        409: ErrorCodes.RESOURCE_CONFLICT,
        500: ErrorCodes.INTERNAL_SERVER_ERROR,
    }
    
    code = status_code_mapping.get(exc.status_code, ErrorCodes.INTERNAL_SERVER_ERROR)
    
    logger.error(
        "HTTP Exception",
        status_code=exc.status_code,
        message=str(exc.detail),
        path=request.url.path,
        method=request.method
    )
    
    error_response = create_error_response(
        request=request,
        status_code=exc.status_code,
        message=str(exc.detail),
        code=code
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(exclude_none=True)
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    
    logger.exception(
        "Unexpected Exception",
        path=request.url.path,
        method=request.method,
        exception_type=type(exc).__name__
    )
    
    # Don't expose internal error details in production
    from app.core.config import get_settings
    settings = get_settings()
    
    debug_info = None
    if not settings.is_production:
        debug_info = {
            "exception_type": type(exc).__name__,
            "exception_message": str(exc)
        }
    
    error_response = create_error_response(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Internal server error",
        code=ErrorCodes.INTERNAL_SERVER_ERROR,
        details="An unexpected error occurred while processing your request",
        debug_info=debug_info
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(exclude_none=True)
    )


# Utility functions for creating specific errors
def create_validation_error(field: str, message: str, value: Any = None) -> ValidationException:
    """Create a validation error for a specific field."""
    
    field_error = FieldError(
        field=field,
        message=message,
        code=ErrorCodes.INVALID_INPUT,
        value=value
    )
    
    return ValidationException(
        message=f"Validation failed for field: {field}",
        field_errors=[field_error]
    )


def create_multiple_field_errors(errors: List[tuple]) -> ValidationException:
    """Create validation error with multiple field errors.
    
    Args:
        errors: List of tuples (field_name, message, value)
    """
    
    field_errors = [
        FieldError(
            field=field,
            message=message,
            code=ErrorCodes.INVALID_INPUT,
            value=value
        )
        for field, message, value in errors
    ]
    
    return ValidationException(
        message=f"Validation failed for {len(field_errors)} fields",
        field_errors=field_errors
    )