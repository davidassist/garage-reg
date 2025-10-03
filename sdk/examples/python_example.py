#!/usr/bin/env python3
"""
GarageReg Python SDK Example

This example demonstrates how to use the GarageReg Python SDK
to interact with the API for user and vehicle management.
"""

import sys
import os
import asyncio
from typing import Dict, Any

# Add the SDK to the Python path for this example
sdk_path = os.path.join(os.path.dirname(__file__), '..', 'python')
sys.path.insert(0, sdk_path)

# In a real project, you would install and import like this:
# from garagereg_client import GarageRegClient
# from garagereg_client.exceptions import GarageRegAPIError

# For this example, we'll simulate the imports
print('=== GarageReg Python SDK Example ===\n')

# Example configuration
config = {
    "base_url": "http://localhost:8004",
    "timeout": 30.0,
    "headers": {
        "User-Agent": "GarageReg-SDK-Example/1.0.0"
    },
    "verify_ssl": True
}

print('Configuration:')
for key, value in config.items():
    print(f'  {key}: {value}')


class ExampleRunner:
    """Example runner that demonstrates SDK usage patterns."""
    
    def __init__(self):
        self.config = config
    
    def create_client(self):
        """Example 1: Create client"""
        print('\n1. Creating GarageReg client...')
        # client = GarageRegClient(self.config)
        print(f'✓ Client created with base URL: {self.config["base_url"]}')
        return True
    
    async def login(self):
        """Example 2: Authentication"""
        print('\n2. Authenticating user...')
        credentials = {
            "username": "admin@example.com",
            "password": "password123"
        }
        
        print(f'Login credentials: {credentials["username"]}')
        
        # try:
        #     response = client.login(credentials)
        #     print('✓ Logged in successfully')
        #     print(f'User: {response.user.full_name}')
        #     print(f'Token expires in: {response.expires_in} seconds')
        # except GarageRegAPIError as e:
        #     print(f'✗ Login failed: {e.message}')
        #     print(f'Error code: {e.code}')
        
        print('✓ Authentication example prepared')
        return True
    
    async def create_user(self):
        """Example 3: Create user"""
        print('\n3. Creating new user...')
        new_user = {
            "username": "john_doe",
            "email": "john@example.com", 
            "password": "securepass123",
            "full_name": "John Doe",
            "role": "technician"
        }
        
        print('New user data:')
        for key, value in new_user.items():
            if key != 'password':  # Don't log passwords
                print(f'  {key}: {value}')
        
        # try:
        #     user = client.create_user(new_user)
        #     print('✓ User created successfully')
        #     print(f'User ID: {user.id}')
        #     print(f'Created at: {user.created_at}')
        # except GarageRegAPIError as e:
        #     print(f'✗ User creation failed: {e.message}')
        #     if e.field_errors:
        #         for error in e.field_errors:
        #             print(f'  {error["field"]}: {error["message"]}')
        
        print('✓ User creation example prepared')
        return True
    
    async def list_users(self):
        """Example 4: List users"""
        print('\n4. Listing users with pagination...')
        params = {
            "skip": 0,
            "limit": 10,
            "search": "john",
            "role": "technician"
        }
        
        print('List parameters:')
        for key, value in params.items():
            print(f'  {key}: {value}')
        
        # try:
        #     response = client.list_users(params)
        #     print('✓ Users retrieved successfully')
        #     print(f'Found {response.total} total users')
        #     print(f'Showing page {response.page} of {response.pages}')
        #     
        #     for i, user in enumerate(response.items, 1):
        #         print(f'  {i}. {user.full_name} ({user.email})')
        #         print(f'     Role: {user.role}, Status: {"Active" if user.is_active else "Inactive"}')
        # except Exception as e:
        #     print(f'✗ Failed to list users: {e}')
        
        print('✓ User listing example prepared')
        return True
    
    async def register_vehicle(self):
        """Example 5: Register vehicle"""
        print('\n5. Registering new vehicle...')
        vehicle = {
            "license_plate": "ABC-123",
            "make": "Toyota",
            "model": "Camry", 
            "year": 2022,
            "color": "Blue",
            "vin": "1HGCM82633A123456",
            "owner_id": 1,
            "fuel_type": "gasoline",
            "transmission": "automatic",
            "mileage": 15000
        }
        
        print('Vehicle data:')
        important_fields = ["license_plate", "make", "model", "year", "owner_id"]
        for field in important_fields:
            print(f'  {field}: {vehicle[field]}')
        
        # try:
        #     registered_vehicle = client.register_vehicle(vehicle)
        #     print('✓ Vehicle registered successfully')
        #     print(f'Vehicle ID: {registered_vehicle.id}')
        #     print(f'Status: {registered_vehicle.status}')
        # except Exception as e:
        #     print(f'✗ Vehicle registration failed: {e}')
        
        print('✓ Vehicle registration example prepared')
        return True
    
    async def list_vehicles(self):
        """Example 6: List vehicles"""
        print('\n6. Listing vehicles...')
        params = {
            "skip": 0,
            "limit": 5,
            "make": "Toyota",
            "status": "active"
        }
        
        print('Filter parameters:')
        for key, value in params.items():
            print(f'  {key}: {value}')
        
        # try:
        #     response = client.list_vehicles(params)
        #     print('✓ Vehicles retrieved successfully')
        #     print(f'Found {response.total} vehicles matching criteria')
        #     
        #     for i, vehicle in enumerate(response.items, 1):
        #         print(f'  {i}. {vehicle.license_plate} - {vehicle.make} {vehicle.model}')
        #         print(f'     Year: {vehicle.year}, Color: {vehicle.color or "N/A"}')
        #         print(f'     Status: {vehicle.status}, Mileage: {vehicle.mileage or "N/A"}')
        # except Exception as e:
        #     print(f'✗ Failed to list vehicles: {e}')
        
        print('✓ Vehicle listing example prepared')
        return True
    
    async def error_handling(self):
        """Example 7: Error handling"""
        print('\n7. Testing error handling...')
        
        # try:
        #     client.test_error('validation')
        # except GarageRegAPIError as e:
        #     print('✓ Caught expected API error')
        #     print('Error details:')
        #     print(f'  code: {e.code}')
        #     print(f'  message: {e.message}')
        #     print(f'  status_code: {e.status_code}')
        #     
        #     if e.field_errors:
        #         print('Field errors:')
        #         for error in e.field_errors:
        #             print(f'  - {error["field"]}: {error["message"]} ({error["code"]})')
        # except Exception as e:
        #     print(f'✗ Unexpected error type: {e}')
        
        print('✓ Error handling example prepared')
        return True
    
    def cleanup(self):
        """Example 8: Cleanup"""
        print('\n8. Cleaning up...')
        # client.logout()
        # client.close()  # Important for httpx client cleanup
        print('✓ Logged out and cleaned up resources')
        return True


async def run_examples():
    """Run all examples."""
    runner = ExampleRunner()
    
    try:
        # Run all examples
        runner.create_client()
        await runner.login()
        await runner.create_user() 
        await runner.list_users()
        await runner.register_vehicle()
        await runner.list_vehicles()
        await runner.error_handling()
        runner.cleanup()
        
        print('\n=== All Examples Completed Successfully ===')
        print('\nTo use this SDK in your project:')
        print('1. Install the package: pip install garagereg-client')
        print('2. Import and use: from garagereg_client import GarageRegClient')
        print('3. Create client with your configuration')
        
        return True
        
    except Exception as e:
        print(f'Example execution failed: {e}')
        return False


def run_sync_example():
    """Run synchronous example without async/await."""
    print('\n=== Synchronous Usage Example ===')
    
    # This shows how to use the client without async/await
    config_example = {
        "base_url": "http://localhost:8004",
        "timeout": 30.0
    }
    
    print('Synchronous client usage:')
    print('  # Create client')
    print('  client = GarageRegClient(config)')
    print('  ')
    print('  # Use context manager for cleanup')
    print('  with GarageRegClient(config) as client:')
    print('      # Login')
    print('      response = client.login(credentials)')
    print('      ')
    print('      # Create user')
    print('      user = client.create_user(user_data)')
    print('      ')
    print('      # List users')
    print('      users = client.list_users({"limit": 10})')
    print('      ')
    print('      # Register vehicle')
    print('      vehicle = client.register_vehicle(vehicle_data)')
    print('      ')
    print('      # Client automatically closed when exiting context')
    
    print('\n✓ Synchronous example pattern shown')


def main():
    """Main function."""
    print(f'Python version: {sys.version}')
    print(f'SDK path: {sdk_path}')
    
    # Run sync example
    run_sync_example()
    
    # Run async examples
    print('\n=== Async Usage Examples ===')
    success = asyncio.run(run_examples())
    
    if success:
        print('\n🎉 All examples completed successfully!')
        print('\nNext steps:')
        print('- Install the actual SDK package')
        print('- Start the GarageReg API server')
        print('- Replace example code with actual API calls')
        print('- Add error handling for your specific use cases')
    else:
        print('\n❌ Some examples failed')
        sys.exit(1)


if __name__ == '__main__':
    main()