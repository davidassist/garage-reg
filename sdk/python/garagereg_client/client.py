"""GarageReg API Client implementation."""

import json
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

import httpx
from pydantic import ValidationError

from .exceptions import (
    GarageRegAPIError,
    GarageRegAuthenticationError,
    GarageRegNetworkError,
    GarageRegNotFoundError,
    GarageRegValidationError,
)
from .models import (
    APIConfig,
    ErrorResponse,
    LoginRequest,
    LoginResponse,
    PaginatedResponse,
    UserCreateRequest,
    UserListParams,
    UserResponse,
    VehicleCreateRequest,
    VehicleListParams,
    VehicleResponse,
)


class GarageRegClient:
    """GarageReg API client."""
    
    def __init__(self, config: Union[APIConfig, Dict[str, Any]]):
        """Initialize the client with configuration.
        
        Args:
            config: API configuration (APIConfig instance or dict)
        """
        if isinstance(config, dict):
            self.config = APIConfig(**config)
        else:
            self.config = config
            
        self._access_token: Optional[str] = None
        
        # Create HTTP client
        self._client = httpx.Client(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            verify=self.config.verify_ssl,
            headers=self.config.headers or {}
        )
    
    def __enter__(self) -> "GarageRegClient":
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
    
    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()
    
    def set_auth_token(self, token: str) -> None:
        """Set the authentication token.
        
        Args:
            token: JWT access token
        """
        self._access_token = token
        self._client.headers["Authorization"] = f"Bearer {token}"
    
    def clear_auth_token(self) -> None:
        """Clear the authentication token."""
        self._access_token = None
        if "Authorization" in self._client.headers:
            del self._client.headers["Authorization"]
    
    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle HTTP response and raise appropriate exceptions.
        
        Args:
            response: HTTP response
            
        Returns:
            Parsed JSON response data
            
        Raises:
            GarageRegAPIError: For API errors
        """
        try:
            if response.headers.get("content-type", "").startswith("application/json"):
                data = response.json()
            else:
                data = {"message": response.text}
        except json.JSONDecodeError:
            data = {"message": "Invalid JSON response"}
        
        if response.is_success:
            return data
        
        # Handle different error types
        error_message = data.get("message", "Unknown error")
        error_code = data.get("code", "UNKNOWN_ERROR")
        field_errors = data.get("field_errors", [])
        
        if response.status_code == 401:
            raise GarageRegAuthenticationError(
                error_message, error_code, response.status_code, field_errors
            )
        elif response.status_code == 404:
            raise GarageRegNotFoundError(
                error_message, error_code, response.status_code, field_errors
            )
        elif response.status_code == 422:
            raise GarageRegValidationError(
                error_message, error_code, response.status_code, field_errors
            )
        else:
            raise GarageRegAPIError(
                error_message, error_code, response.status_code, field_errors
            )
    
    def _request(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make HTTP request.
        
        Args:
            method: HTTP method
            path: Request path
            json_data: JSON request body
            params: Query parameters
            
        Returns:
            Response data
            
        Raises:
            GarageRegNetworkError: For network errors
            GarageRegAPIError: For API errors
        """
        try:
            response = self._client.request(
                method=method,
                url=path,
                json=json_data,
                params=params,
            )
            return self._handle_response(response)
        except httpx.RequestError as e:
            raise GarageRegNetworkError(f"Network error: {str(e)}", e)
    
    # Authentication methods
    def login(self, credentials: Union[LoginRequest, Dict[str, Any]]) -> LoginResponse:
        """Authenticate user and get access token.
        
        Args:
            credentials: Login credentials
            
        Returns:
            Login response with access token
        """
        if isinstance(credentials, dict):
            credentials = LoginRequest(**credentials)
        
        data = self._request("POST", "/api/auth/login", credentials.model_dump())
        response = LoginResponse(**data)
        self.set_auth_token(response.access_token)
        return response
    
    def logout(self) -> Dict[str, str]:
        """Logout user.
        
        Returns:
            Logout confirmation
        """
        try:
            data = self._request("POST", "/api/auth/logout")
            self.clear_auth_token()
            return data
        except Exception:
            self.clear_auth_token()
            raise
    
    # User methods
    def create_user(self, user: Union[UserCreateRequest, Dict[str, Any]]) -> UserResponse:
        """Create a new user.
        
        Args:
            user: User creation data
            
        Returns:
            Created user information
        """
        if isinstance(user, dict):
            user = UserCreateRequest(**user)
        
        data = self._request("POST", "/api/users", user.model_dump())
        return UserResponse(**data)
    
    def list_users(
        self, params: Optional[Union[UserListParams, Dict[str, Any]]] = None
    ) -> PaginatedResponse:
        """List users with pagination.
        
        Args:
            params: Query parameters for filtering and pagination
            
        Returns:
            Paginated list of users
        """
        if params is None:
            params = UserListParams()
        elif isinstance(params, dict):
            params = UserListParams(**params)
        
        # Convert to dict and remove None values
        query_params = {k: v for k, v in params.model_dump().items() if v is not None}
        
        data = self._request("GET", "/api/users", params=query_params)
        
        # Convert items to UserResponse objects
        users = [UserResponse(**item) for item in data["items"]]
        data["items"] = users
        
        return PaginatedResponse(**data)
    
    def get_user(self, user_id: int) -> UserResponse:
        """Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User information
        """
        data = self._request("GET", f"/api/users/{user_id}")
        return UserResponse(**data)
    
    # Vehicle methods
    def register_vehicle(
        self, vehicle: Union[VehicleCreateRequest, Dict[str, Any]]
    ) -> VehicleResponse:
        """Register a new vehicle.
        
        Args:
            vehicle: Vehicle registration data
            
        Returns:
            Registered vehicle information
        """
        if isinstance(vehicle, dict):
            vehicle = VehicleCreateRequest(**vehicle)
        
        data = self._request("POST", "/api/vehicles", vehicle.model_dump())
        return VehicleResponse(**data)
    
    def list_vehicles(
        self, params: Optional[Union[VehicleListParams, Dict[str, Any]]] = None
    ) -> PaginatedResponse:
        """List vehicles with pagination.
        
        Args:
            params: Query parameters for filtering and pagination
            
        Returns:
            Paginated list of vehicles
        """
        if params is None:
            params = VehicleListParams()
        elif isinstance(params, dict):
            params = VehicleListParams(**params)
        
        # Convert to dict and remove None values
        query_params = {k: v for k, v in params.model_dump().items() if v is not None}
        
        data = self._request("GET", "/api/vehicles", params=query_params)
        
        # Convert items to VehicleResponse objects
        vehicles = [VehicleResponse(**item) for item in data["items"]]
        data["items"] = vehicles
        
        return PaginatedResponse(**data)
    
    def get_vehicle(self, vehicle_id: int) -> VehicleResponse:
        """Get vehicle by ID.
        
        Args:
            vehicle_id: Vehicle ID
            
        Returns:
            Vehicle information
        """
        data = self._request("GET", f"/api/vehicles/{vehicle_id}")
        return VehicleResponse(**data)
    
    # Test methods
    def test_user_validation(
        self, user: Union[UserCreateRequest, Dict[str, Any]]
    ) -> UserResponse:
        """Test user validation endpoint.
        
        Args:
            user: User data to validate
            
        Returns:
            Validated user information
        """
        if isinstance(user, dict):
            user = UserCreateRequest(**user)
        
        data = self._request("POST", "/api/test/validation/user", user.model_dump())
        return UserResponse(**data)
    
    def test_error(self, error_type: str) -> ErrorResponse:
        """Test error handling endpoint.
        
        Args:
            error_type: Type of error to generate
            
        Returns:
            Error response
        """
        data = self._request("GET", f"/api/test/errors/{error_type}")
        return ErrorResponse(**data)