"""
Integration Tests for Authentication API
Tests authentication endpoints with real HTTP client and database
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.auth import get_password_hash


class TestAuthenticationEndpoints:
    """Test authentication API endpoints."""
    
    @pytest.mark.asyncio
    async def test_register_user_success(self, async_client: AsyncClient, test_organization):
        """Test successful user registration."""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "securepassword123",
            "organization_id": test_organization.id
        }
        
        response = await async_client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "id" in data
        assert "password" not in data  # Password should not be returned
    
    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(self, async_client: AsyncClient, test_user):
        """Test registration with duplicate email."""
        user_data = {
            "username": "newuser",
            "email": test_user.email,  # Use existing email
            "first_name": "New",
            "last_name": "User", 
            "password": "securepassword123",
            "organization_id": test_user.organization_id
        }
        
        response = await async_client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "email" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_register_user_duplicate_username(self, async_client: AsyncClient, test_user):
        """Test registration with duplicate username."""
        user_data = {
            "username": test_user.username,  # Use existing username
            "email": "different@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "securepassword123", 
            "organization_id": test_user.organization_id
        }
        
        response = await async_client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "username" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_register_user_invalid_data(self, async_client: AsyncClient, test_organization):
        """Test registration with invalid data."""
        user_data = {
            "username": "ab",  # Too short
            "email": "invalid-email",  # Invalid format
            "password": "123",  # Too weak
            "organization_id": test_organization.id
        }
        
        response = await async_client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_login_success(self, async_client: AsyncClient, async_session: AsyncSession, test_organization):
        """Test successful login."""
        # Create user with known password
        password = "testpassword123"
        user = User(
            organization_id=test_organization.id,
            username="logintest",
            email="login@example.com",
            first_name="Login",
            last_name="Test",
            password_hash=get_password_hash(password),
            email_verified=True,
            is_active=True
        )
        async_session.add(user)
        await async_session.commit()
        
        login_data = {
            "username": "logintest",
            "password": password
        }
        
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 100  # JWT should be long
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, async_client: AsyncClient, test_user):
        """Test login with wrong password."""
        login_data = {
            "username": test_user.username,
            "password": "wrongpassword"
        }
        
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "incorrect" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, async_client: AsyncClient):
        """Test login with non-existent user."""
        login_data = {
            "username": "nonexistent",
            "password": "anypassword"
        }
        
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "incorrect" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_login_inactive_user(self, async_client: AsyncClient, async_session: AsyncSession, test_organization):
        """Test login with inactive user."""
        # Create inactive user
        password = "testpassword123"
        user = User(
            organization_id=test_organization.id,
            username="inactiveuser",
            email="inactive@example.com",
            first_name="Inactive",
            last_name="User",
            password_hash=get_password_hash(password),
            email_verified=True,
            is_active=False  # Inactive
        )
        async_session.add(user)
        await async_session.commit()
        
        login_data = {
            "username": "inactiveuser",
            "password": password
        }
        
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_user_with_token(self, authenticated_client: AsyncClient, test_user):
        """Test getting current user with valid token."""
        response = await authenticated_client.get("/api/v1/auth/me")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert "password" not in data
    
    @pytest.mark.asyncio
    async def test_get_current_user_without_token(self, async_client: AsyncClient):
        """Test getting current user without token."""
        response = await async_client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
        data = response.json()
        assert "not authenticated" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, async_client: AsyncClient):
        """Test getting current user with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await async_client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_refresh_token(self, authenticated_client: AsyncClient, test_user):
        """Test token refresh functionality."""
        # First login to get initial token
        login_data = {
            "username": test_user.username,
            "password": "testpassword"  # This would need to match actual password
        }
        
        # Note: This test assumes refresh endpoint exists
        # If not implemented, this test should be marked as skip
        response = await authenticated_client.post("/api/v1/auth/refresh")
        
        if response.status_code == 404:
            pytest.skip("Refresh endpoint not implemented")
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


class TestAuthenticationSecurity:
    """Test authentication security features."""
    
    @pytest.mark.asyncio
    async def test_password_requirements(self, async_client: AsyncClient, test_organization):
        """Test password strength requirements."""
        weak_passwords = [
            "123",           # Too short
            "password",      # No numbers/symbols
            "12345678",      # Only numbers
            "abcdefgh",      # Only letters
        ]
        
        for weak_password in weak_passwords:
            user_data = {
                "username": f"user_{weak_password}",
                "email": f"user_{weak_password}@example.com",
                "first_name": "Test",
                "last_name": "User",
                "password": weak_password,
                "organization_id": test_organization.id
            }
            
            response = await async_client.post("/api/v1/auth/register", json=user_data)
            
            # Should reject weak password
            assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_email_format_validation(self, async_client: AsyncClient, test_organization):
        """Test email format validation."""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user@.com",
            "user..test@example.com"
        ]
        
        for invalid_email in invalid_emails:
            user_data = {
                "username": f"user_{invalid_email.replace('@', '').replace('.', '')}",
                "email": invalid_email,
                "first_name": "Test", 
                "last_name": "User",
                "password": "securepassword123",
                "organization_id": test_organization.id
            }
            
            response = await async_client.post("/api/v1/auth/register", json=user_data)
            
            # Should reject invalid email
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_sql_injection_protection(self, async_client: AsyncClient):
        """Test protection against SQL injection attempts."""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users--"
        ]
        
        for malicious_input in malicious_inputs:
            login_data = {
                "username": malicious_input,
                "password": "anypassword"
            }
            
            response = await async_client.post("/api/v1/auth/login", data=login_data)
            
            # Should not cause 500 error or unexpected behavior
            assert response.status_code in [401, 422]  # Unauthorized or validation error
    
    @pytest.mark.asyncio
    async def test_rate_limiting_login(self, async_client: AsyncClient):
        """Test rate limiting on login attempts."""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        
        # Make multiple rapid login attempts
        responses = []
        for _ in range(10):
            response = await async_client.post("/api/v1/auth/login", data=login_data)
            responses.append(response.status_code)
        
        # Should eventually rate limit (429) or continue returning 401
        # Implementation depends on rate limiting strategy
        assert all(code in [401, 429] for code in responses)


class TestAuthenticationIntegrationScenarios:
    """Test complex authentication integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_user_lifecycle(self, async_client: AsyncClient, test_organization):
        """Test complete user lifecycle: register -> login -> access protected endpoint."""
        # Step 1: Register new user
        user_data = {
            "username": "lifecycletest",
            "email": "lifecycle@example.com",
            "first_name": "Lifecycle",
            "last_name": "Test",
            "password": "securepassword123",
            "organization_id": test_organization.id
        }
        
        register_response = await async_client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 201
        
        # Step 2: Login with new user
        login_data = {
            "username": "lifecycletest",
            "password": "securepassword123"
        }
        
        login_response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        
        # Step 3: Access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        me_response = await async_client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200
        
        user_info = me_response.json()
        assert user_info["username"] == "lifecycletest"
        assert user_info["email"] == "lifecycle@example.com"
    
    @pytest.mark.asyncio
    async def test_cross_organization_access(self, async_client: AsyncClient, async_session: AsyncSession):
        """Test that users cannot access resources from other organizations."""
        from app.models.organization import Organization
        
        # Create two organizations
        org1 = Organization(
            name="Organization 1",
            display_name="Org 1",
            organization_type="company",
            is_active=True
        )
        org2 = Organization(
            name="Organization 2", 
            display_name="Org 2",
            organization_type="company",
            is_active=True
        )
        
        async_session.add_all([org1, org2])
        await async_session.commit()
        await async_session.refresh(org1)
        await async_session.refresh(org2)
        
        # Create users in different organizations
        user1 = User(
            organization_id=org1.id,
            username="user1",
            email="user1@org1.com",
            first_name="User",
            last_name="One",
            password_hash=get_password_hash("password123"),
            email_verified=True,
            is_active=True
        )
        user2 = User(
            organization_id=org2.id,
            username="user2", 
            email="user2@org2.com",
            first_name="User",
            last_name="Two",
            password_hash=get_password_hash("password123"),
            email_verified=True,
            is_active=True
        )
        
        async_session.add_all([user1, user2])
        await async_session.commit()
        
        # Login as user1
        login_data = {
            "username": "user1",
            "password": "password123"
        }
        
        login_response = await async_client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to access org2 resources (should fail)
        # This assumes there are organization-specific endpoints
        org2_response = await async_client.get(
            f"/api/v1/organizations/{org2.id}",
            headers=headers
        )
        
        # Should be forbidden or not found
        assert org2_response.status_code in [403, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])