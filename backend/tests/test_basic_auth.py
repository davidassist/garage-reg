"""Basic authentication tests to verify system functionality."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.models import Base


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_basic_auth.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def setup_test_db():
    """Create test database tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(setup_test_db):
    """Database session fixture."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(setup_test_db):
    """Test client fixture with database override."""
    from app.main import app
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c


class TestAuthEndpoints:
    """Test basic authentication endpoint functionality."""
    
    def test_auth_endpoints_exist(self, client):
        """Test that authentication endpoints are accessible."""
        # Test login endpoint exists (should return 422 for missing data)
        response = client.post("/api/v1/auth/login")
        assert response.status_code in [422, 401]  # Validation error or unauthorized
        
        # Test register endpoint exists (should return 422 for missing data) 
        response = client.post("/api/v1/auth/register")
        assert response.status_code == 422  # Validation error
        
        # Test profile endpoint exists (should return 403 for no auth)
        response = client.get("/api/v1/auth/profile")
        assert response.status_code == 403  # No authentication provided


class TestPasswordValidation:
    """Test password validation logic."""
    
    def test_password_strength_validation(self, client):
        """Test password strength validation."""
        weak_passwords = [
            "123",                    # Too short
            "password",              # No uppercase, numbers, symbols
            "PASSWORD",              # No lowercase, numbers, symbols  
            "Password",              # No numbers
        ]
        
        for weak_password in weak_passwords:
            registration_data = {
                "username": f"user_{weak_password[:3]}",
                "email": f"user_{weak_password[:3]}@example.com",
                "password": weak_password,
                "first_name": "Test",
                "last_name": "User", 
                "organization_id": 1
            }
            
            response = client.post("/api/v1/auth/register", json=registration_data)
            
            # Should fail validation
            assert response.status_code == 422


class TestSecurityModule:
    """Test security utilities."""
    
    def test_password_hashing(self):
        """Test password hashing functionality."""
        from app.core.security import hash_password, verify_password
        
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        # Hash should be different from original password
        assert hashed != password
        
        # Should be able to verify correct password
        assert verify_password(password, hashed) is True
        
        # Should reject incorrect password
        assert verify_password("WrongPassword", hashed) is False
    
    def test_jwt_token_creation(self):
        """Test JWT token creation and validation."""
        from app.core.security import create_access_token, decode_jwt_token
        
        test_data = {
            "user_id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "org_id": 1,
            "permissions": ["read", "write"]
        }
        
        # Create token
        token = create_access_token(test_data)
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode token
        decoded = decode_jwt_token(token)
        assert decoded is not None
        assert decoded["user_id"] == test_data["user_id"]
        assert decoded["username"] == test_data["username"]


class TestRBACModule:
    """Test Role-Based Access Control utilities."""
    
    def test_rbac_constants(self):
        """Test that RBAC constants are defined."""
        from app.core.rbac import Roles, Permissions
        
        # Test roles exist
        assert hasattr(Roles, 'CLIENT')
        assert hasattr(Roles, 'TECHNICIAN') 
        assert hasattr(Roles, 'MANAGER')
        assert hasattr(Roles, 'ADMIN')
        assert hasattr(Roles, 'SUPER_ADMIN')
        
        # Test permission structure exists
        assert hasattr(Permissions, 'GATE')
        assert hasattr(Permissions, 'MAINTENANCE')


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_rate_limit_config(self):
        """Test rate limiting configuration."""
        from app.core.rate_limit import RateLimitConfig
        
        config = RateLimitConfig()
        
        # Should have rate limits defined
        assert hasattr(config, 'login_limit')
        assert hasattr(config, 'register_limit') 
        assert hasattr(config, 'default_limit')
        
        # Limits should be reasonable numbers
        assert config.login_limit > 0
        assert config.register_limit > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])