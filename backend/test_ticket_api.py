"""
Test script to verify ticket API functionality.

Teszt szkript a ticket API működésének ellenőrzésére.
"""

from fastapi.testclient import TestClient
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from app.main import app

client = TestClient(app)

# Test basic health check
def test_health():
    response = client.get("/api/v1/health")
    print(f"Health check: {response.status_code}")
    if response.status_code == 200:
        print("✓ API is running")
        return True
    else:
        print(f"✗ API health check failed: {response.text}")
        return False

# Test ticket endpoints (without auth for now)
def test_ticket_endpoints():
    print("\nTesting ticket endpoints...")
    
    # Test GET /tickets (this might require auth)
    try:
        response = client.get("/api/v1/tickets")
        print(f"GET /api/v1/tickets: {response.status_code}")
        if response.status_code == 401:
            print("✓ Authentication required (expected)")
        elif response.status_code == 200:
            print("✓ Tickets endpoint accessible")
        else:
            print(f"✗ Unexpected response: {response.text}")
    except Exception as e:
        print(f"✗ Error testing tickets endpoint: {e}")

if __name__ == "__main__":
    print("Testing Ticket API...")
    
    if test_health():
        test_ticket_endpoints()
    else:
        print("Cannot test further without healthy API")