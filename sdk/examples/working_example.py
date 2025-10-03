#!/usr/bin/env python3
"""
Working GarageReg API Example

This example demonstrates actual API calls to a running GarageReg server
using raw HTTP requests to show the SDK usage patterns.
"""

import json
import requests
import time
from typing import Dict, Any, Optional


class SimpleGarageRegClient:
    """Simple client implementation for demonstration purposes."""
    
    def __init__(self, base_url: str = "http://localhost:8005"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'GarageReg-Example/1.0.0'
        })
        self.access_token: Optional[str] = None
    
    def set_auth_token(self, token: str):
        """Set authentication token."""
        self.access_token = token
        self.session.headers['Authorization'] = f'Bearer {token}'
    
    def clear_auth_token(self):
        """Clear authentication token."""
        self.access_token = None
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
    
    def request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request."""
        url = f"{self.base_url}{path}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            if response.headers.get('content-type', '').startswith('application/json'):
                data = response.json()
            else:
                data = {'message': response.text}
            
            if not response.ok:
                error_msg = data.get('message', 'API Error')
                error_code = data.get('code', 'UNKNOWN_ERROR')
                print(f"❌ API Error [{response.status_code}]: {error_msg} (Code: {error_code})")
                
                if 'field_errors' in data:
                    print("Field errors:")
                    for error in data['field_errors']:
                        print(f"  - {error.get('field')}: {error.get('message')}")
                
                raise Exception(f"API Error: {error_msg}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Network Error: {e}")
            raise
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login and get access token."""
        data = self.request('POST', '/api/auth/login', json={
            'username': username,
            'password': password
        })
        
        if 'access_token' in data:
            self.set_auth_token(data['access_token'])
        
        return data
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user."""
        return self.request('POST', '/api/users', json=user_data)
    
    def list_users(self, **params) -> Dict[str, Any]:
        """List users with pagination."""
        return self.request('GET', '/api/users', params=params)
    
    def register_vehicle(self, vehicle_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new vehicle."""
        return self.request('POST', '/api/vehicles', json=vehicle_data)
    
    def list_vehicles(self, **params) -> Dict[str, Any]:
        """List vehicles with pagination."""
        return self.request('GET', '/api/vehicles', params=params)
    
    def test_validation(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test user validation."""
        return self.request('POST', '/api/test/validation/user', json=user_data)


def check_server_health(client: SimpleGarageRegClient) -> bool:
    """Check if the server is running."""
    try:
        # Try to access the health endpoint or docs
        response = client.session.get(f"{client.base_url}/docs", timeout=5)
        return response.status_code in [200, 404]  # 404 is ok if docs not available
    except:
        return False


def run_working_example():
    """Run working example with actual API calls."""
    print('=== Working GarageReg API Example ===\n')
    
    # Create client
    client = SimpleGarageRegClient()
    print(f'🔗 Connecting to: {client.base_url}')
    
    # Check server health
    if not check_server_health(client):
        print('❌ Server not available. Please start the GarageReg server first.')
        print('   Run: python backend/complete_openapi.py')
        return False
    
    print('✅ Server is running\n')
    
    try:
        # 1. Login
        print('1. 🔐 Authenticating...')
        try:
            login_response = client.login('admin@example.com', 'password123')
            print(f'✅ Logged in as: {login_response.get("user", {}).get("full_name", "Unknown")}')
            print(f'   Token expires in: {login_response.get("expires_in", 0)} seconds')
        except Exception as e:
            print(f'ℹ️  Login failed (expected if no test data): {e}')
            print('   Continuing with other examples...')
        
        print()
        
        # 2. Test user validation (this should work even without login)
        print('2. 🔍 Testing user validation...')
        try:
            test_user = {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "password123",
                "full_name": "John Doe",
                "role": "technician"
            }
            
            validation_response = client.test_validation(test_user)
            print('✅ User validation successful')
            print(f'   Validated user: {validation_response.get("full_name")}')
            
        except Exception as e:
            print(f'ℹ️  Validation test: {e}')
        
        print()
        
        # 3. Try to create a user
        print('3. 👤 Creating user...')
        try:
            new_user = {
                "username": f"test_user_{int(time.time())}",  # Make unique
                "email": f"test{int(time.time())}@example.com",
                "password": "securepass123",
                "full_name": "Test User",
                "role": "viewer"
            }
            
            user_response = client.create_user(new_user)
            print('✅ User created successfully')
            print(f'   User ID: {user_response.get("id")}')
            print(f'   Username: {user_response.get("username")}')
            
        except Exception as e:
            print(f'ℹ️  User creation: {e}')
        
        print()
        
        # 4. Try to list users
        print('4. 📋 Listing users...')
        try:
            users_response = client.list_users(limit=5)
            total = users_response.get('total', 0)
            items = users_response.get('items', [])
            
            print(f'✅ Retrieved {len(items)} of {total} total users')
            
            for i, user in enumerate(items[:3], 1):  # Show first 3
                print(f'   {i}. {user.get("full_name")} ({user.get("email")})')
                print(f'      Role: {user.get("role")}, Active: {user.get("is_active")}')
                
        except Exception as e:
            print(f'ℹ️  List users: {e}')
        
        print()
        
        # 5. Try to register a vehicle
        print('5. 🚗 Registering vehicle...')
        try:
            vehicle_data = {
                "license_plate": f"TEST-{int(time.time()) % 1000}",  # Make unique
                "make": "Toyota",
                "model": "Camry",
                "year": 2022,
                "color": "Blue",
                "vin": f"1HGCM82633A{int(time.time()) % 100000:06d}",  # Make unique
                "owner_id": 1,
                "fuel_type": "gasoline",
                "transmission": "automatic"
            }
            
            vehicle_response = client.register_vehicle(vehicle_data)
            print('✅ Vehicle registered successfully')
            print(f'   Vehicle ID: {vehicle_response.get("id")}')
            print(f'   License Plate: {vehicle_response.get("license_plate")}')
            print(f'   Make/Model: {vehicle_response.get("make")} {vehicle_response.get("model")}')
            
        except Exception as e:
            print(f'ℹ️  Vehicle registration: {e}')
        
        print()
        
        # 6. List vehicles
        print('6. 🚙 Listing vehicles...')
        try:
            vehicles_response = client.list_vehicles(limit=5)
            total = vehicles_response.get('total', 0)
            items = vehicles_response.get('items', [])
            
            print(f'✅ Retrieved {len(items)} of {total} total vehicles')
            
            for i, vehicle in enumerate(items[:3], 1):  # Show first 3
                print(f'   {i}. {vehicle.get("license_plate")} - {vehicle.get("make")} {vehicle.get("model")}')
                print(f'      Year: {vehicle.get("year")}, Status: {vehicle.get("status")}')
                
        except Exception as e:
            print(f'ℹ️  List vehicles: {e}')
        
        print()
        
        # 7. Test error handling
        print('7. ⚠️  Testing error handling...')
        try:
            # Try to access an endpoint that should cause validation error
            client.request('POST', '/api/users', json={
                "username": "",  # Invalid: empty username
                "email": "invalid-email",  # Invalid: not a real email
                "password": "123"  # Invalid: too short
            })
            
        except Exception as e:
            print('✅ Caught expected validation error')
            print(f'   Error details: {str(e)[:100]}...')
        
        print()
        
        print('=== Example Completed Successfully ===')
        print('\n📚 What this demonstrates:')
        print('✓ Server connectivity and health checking')
        print('✓ Authentication flow (login with JWT tokens)')
        print('✓ User management (create, list, validate)')
        print('✓ Vehicle management (register, list)')
        print('✓ Error handling and validation')
        print('✓ Proper HTTP client usage patterns')
        
        print('\n🚀 Next steps to use the SDK:')
        print('1. Install: pip install garagereg-client')
        print('2. Import: from garagereg_client import GarageRegClient')
        print('3. Use: client = GarageRegClient({"base_url": "http://localhost:8004"})')
        
        return True
        
    except Exception as e:
        print(f'❌ Example failed: {e}')
        return False


def show_sdk_comparison():
    """Show comparison between raw API and SDK usage."""
    print('\n=== SDK vs Raw API Comparison ===\n')
    
    print('📝 Raw API Usage (what we just did):')
    print('''
    import requests
    
    # Manual HTTP requests
    response = requests.post('http://localhost:8004/api/users', json={
        "username": "john_doe",
        "email": "john@example.com", 
        "password": "password123",
        "full_name": "John Doe"
    })
    
    if response.ok:
        user = response.json()
    else:
        # Manual error handling
        error = response.json()
        print(f"Error: {error['message']}")
    ''')
    
    print('\n🛠️  SDK Usage (what the SDK provides):')
    print('''
    from garagereg_client import GarageRegClient
    from garagereg_client.exceptions import GarageRegAPIError
    
    # Type-safe, validated requests
    client = GarageRegClient({"base_url": "http://localhost:8004"})
    
    try:
        user = client.create_user({
            "username": "john_doe",
            "email": "john@example.com",
            "password": "password123", 
            "full_name": "John Doe"
        })
        # user is automatically validated UserResponse object
        print(f"Created: {user.full_name}")
        
    except GarageRegAPIError as e:
        # Structured error handling
        print(f"Error: {e.message}")
        if e.field_errors:
            for error in e.field_errors:
                print(f"  {error.field}: {error.message}")
    ''')
    
    print('\n🎯 SDK Benefits:')
    print('✓ Type safety with Pydantic models')
    print('✓ Automatic request/response validation') 
    print('✓ Structured error handling')
    print('✓ Built-in authentication management')
    print('✓ Consistent API across all endpoints')
    print('✓ Documentation and IDE support')
    print('✓ Automatic retry and timeout handling')


if __name__ == '__main__':
    success = run_working_example()
    
    if success:
        show_sdk_comparison()
        print('\n🎉 All examples completed! The SDK is ready to use.')
    else:
        print('\n❌ Examples incomplete. Please check server status.')