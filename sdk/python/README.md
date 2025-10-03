# GarageReg Python SDK

A Python client library for the GarageReg API.

## Installation

```bash
pip install garagereg-client
```

## Usage

```python
from garagereg_client import GarageRegClient
from garagereg_client.exceptions import GarageRegAPIError

# Create client
client = GarageRegClient({
    "base_url": "http://localhost:8004",
    "timeout": 30.0
})

# Or use context manager for automatic cleanup
with GarageRegClient({"base_url": "http://localhost:8004"}) as client:
    # Authentication
    try:
        login_response = client.login({
            "username": "admin@example.com",
            "password": "password123"
        })
        print(f"Logged in: {login_response.user.full_name}")
    except GarageRegAPIError as e:
        print(f"Login failed: {e.message}")
    
    # Create a user
    try:
        user = client.create_user({
            "username": "john_doe",
            "email": "john@example.com",
            "password": "password123",
            "full_name": "John Doe"
        })
        print(f"User created: {user.username}")
    except GarageRegAPIError as e:
        print(f"User creation failed: {e.message}")
        if e.field_errors:
            for error in e.field_errors:
                print(f"  {error['field']}: {error['message']}")
    
    # List users with pagination
    users = client.list_users({
        "skip": 0,
        "limit": 10,
        "search": "john"
    })
    print(f"Found {users.total} users")
    for user in users.items:
        print(f"  - {user.username} ({user.email})")
    
    # Register a vehicle
    vehicle = client.register_vehicle({
        "license_plate": "ABC-123",
        "make": "Toyota", 
        "model": "Camry",
        "year": 2022,
        "color": "Blue",
        "vin": "1HGCM82633A123456",
        "owner_id": 1
    })
    print(f"Vehicle registered: {vehicle.license_plate}")
    
    # Error handling
    try:
        client.test_error("validation")
    except GarageRegAPIError as e:
        print(f"Error: {e.code} - {e.message}")
        print(f"Status: {e.status_code}")
```

## Async Support

The client also supports async operations:

```python
import asyncio
from garagereg_client import AsyncGarageRegClient

async def main():
    async with AsyncGarageRegClient({"base_url": "http://localhost:8004"}) as client:
        # All methods are available as async versions
        login_response = await client.login({
            "username": "admin@example.com",
            "password": "password123"
        })
        
        users = await client.list_users({"limit": 10})
        print(f"Found {len(users.items)} users")

asyncio.run(main())
```

## API Reference

### Authentication

- `login(credentials)` - Authenticate user and get access token
- `logout()` - Logout user and clear token

### Users

- `create_user(user)` - Create a new user
- `list_users(params=None)` - List users with pagination
- `get_user(user_id)` - Get user by ID

### Vehicles

- `register_vehicle(vehicle)` - Register a new vehicle
- `list_vehicles(params=None)` - List vehicles with pagination
- `get_vehicle(vehicle_id)` - Get vehicle by ID

### Testing

- `test_user_validation(user)` - Test user validation
- `test_error(error_type)` - Test error handling

## Error Handling

The SDK raises specific exceptions for different error types:

- `GarageRegAPIError` - Base API error
- `GarageRegAuthenticationError` - Authentication errors (401)
- `GarageRegValidationError` - Validation errors (422)
- `GarageRegNotFoundError` - Resource not found (404)
- `GarageRegNetworkError` - Network/connection errors

All API errors include:
- `message` - Error description
- `code` - Error code
- `status_code` - HTTP status code
- `field_errors` - Field-specific validation errors (if any)

## Models

The SDK includes comprehensive Pydantic models for all API entities:

- Request models: `LoginRequest`, `UserCreateRequest`, `VehicleCreateRequest`
- Response models: `UserResponse`, `VehicleResponse`, `LoginResponse`
- Query parameter models: `UserListParams`, `VehicleListParams`
- Utility models: `PaginatedResponse`, `ErrorResponse`

## Configuration

Client configuration options:

```python
config = {
    "base_url": "https://api.garagereg.com",  # Required
    "timeout": 30.0,                          # Request timeout
    "headers": {"Custom-Header": "value"},    # Additional headers
    "verify_ssl": True                        # SSL verification
}
```

## License

MIT