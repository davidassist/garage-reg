"""Exception classes for GarageReg API client."""

from typing import Any, Dict, List, Optional


class GarageRegAPIError(Exception):
    """Base exception for GarageReg API errors."""
    
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int,
        field_errors: Optional[List[Dict[str, Any]]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.field_errors = field_errors or []


class GarageRegNetworkError(Exception):
    """Exception for network-related errors."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.original_error = original_error


class GarageRegAuthenticationError(GarageRegAPIError):
    """Exception for authentication-related errors."""
    pass


class GarageRegValidationError(GarageRegAPIError):
    """Exception for validation-related errors."""
    pass


class GarageRegNotFoundError(GarageRegAPIError):
    """Exception for resource not found errors."""
    pass