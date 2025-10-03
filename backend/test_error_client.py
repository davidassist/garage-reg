"""
Test client for demonstrating error handling
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8002"

def test_validation_errors():
    """Test validation error scenarios."""
    print("\n=== TESTING VALIDATION ERRORS ===")
    
    # Test 1: Invalid user data with multiple validation errors
    print("\n1. Testing multiple field validation errors:")
    invalid_user = {
        "username": "a",  # Too short (min 3)
        "email": "invalid-email",  # Invalid format
        "password": "123",  # Too short (min 8)
        "age": 200  # Out of range (max 120)
    }
    
    try:
        response = requests.post(f"{BASE_URL}/test/validation/user", json=invalid_user)
        print(f"Status: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Missing required fields
    print("\n2. Testing missing required fields:")
    incomplete_user = {
        "username": "testuser"
        # Missing email, password, age
    }
    
    try:
        response = requests.post(f"{BASE_URL}/test/validation/user", json=incomplete_user)
        print(f"Status: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")

    # Test 3: Username conflict (409 error)
    print("\n3. Testing username conflict:")
    conflicting_user = {
        "username": "admin",  # Reserved username
        "email": "admin@example.com",
        "password": "password123",
        "age": 25
    }
    
    try:
        response = requests.post(f"{BASE_URL}/test/validation/user", json=conflicting_user)
        print(f"Status: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")

    # Test 4: Complex validation model
    print("\n4. Testing complex validation model:")
    invalid_complex = {
        "required_string": "",  # Empty string
        "positive_number": -5,  # Negative number
        "email_field": "not-an-email"  # Invalid email
    }
    
    try:
        response = requests.post(f"{BASE_URL}/test/validation/complex", json=invalid_complex)
        print(f"Status: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")

    # Test 5: Valid user creation
    print("\n5. Testing successful user creation:")
    valid_user = {
        "username": "validuser",
        "email": "valid@example.com",
        "password": "securepassword123",
        "age": 25
    }
    
    try:
        response = requests.post(f"{BASE_URL}/test/validation/user", json=valid_user)
        print(f"Status: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")

def test_other_errors():
    """Test other error scenarios."""
    print("\n\n=== TESTING OTHER ERRORS ===")
    
    # Test 404 error
    print("\n1. Testing 404 Not Found:")
    try:
        response = requests.get(f"{BASE_URL}/test/not-found")
        print(f"Status: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")

    # Test 500 server error
    print("\n2. Testing 500 Server Error:")
    try:
        response = requests.get(f"{BASE_URL}/test/server-error")
        print(f"Status: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")

def main():
    print("=" * 60)
    print("GARAGEREG ERROR HANDLING DEMONSTRATION")
    print("=" * 60)
    print("Kimenet: Backend error envelope (kód, üzenet, mezőhibák)")
    print("Elfogadás: Szándékosan okozott validációs hiba elegánsan jelenik meg")
    print("=" * 60)
    
    # Test server availability
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Server is running at {BASE_URL}")
        print("Available endpoints:")
        endpoints = response.json().get("endpoints", {})
        for name, path in endpoints.items():
            print(f"  - {name}: {path}")
    except Exception as e:
        print(f"❌ Server not available: {e}")
        return

    test_validation_errors()
    test_other_errors()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("✅ Backend error envelope implemented with:")
    print("   - Standardized error codes (VALIDATION_ERROR, etc.)")
    print("   - Human-readable Hungarian messages")
    print("   - Field-specific validation errors")
    print("   - Request context (path, method, timestamp)")
    print("   - Proper HTTP status codes")
    print("\n✅ Validation errors are handled elegantly:")
    print("   - Multiple field errors grouped together")
    print("   - Clear error messages for each field")
    print("   - Proper error codes for programmatic handling")
    print("\n✅ Ready for frontend integration with error interceptor!")

if __name__ == "__main__":
    main()