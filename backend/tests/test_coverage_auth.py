"""Additional tests to improve code coverage for authentication modules."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta


class TestSecurityModuleCoverage:
    """Test additional security module functions for coverage."""
    
    def test_password_handler_edge_cases(self):
        """Test PasswordHandler edge cases."""
        from app.core.security import password_handler
        
        # Test empty password handling
        with pytest.raises(Exception):
            password_handler.hash_password("")
        
        # Test invalid hash verification
        assert password_handler.verify_password("any", "invalid_hash") is False
        
    def test_refresh_token_creation(self):
        """Test refresh token creation."""
        from app.core.security import create_refresh_token
        
        user_data = {
            "user_id": 1,
            "username": "testuser",
            "email": "test@example.com"
        }
        
        refresh_token = create_refresh_token(user_data)
        assert isinstance(refresh_token, str)
        assert len(refresh_token.split('.')) == 3
        
    def test_password_reset_token(self):
        """Test password reset token creation."""
        from app.core.security import create_password_reset_token
        
        token = create_password_reset_token("test@example.com")
        assert isinstance(token, str)
        assert len(token) > 0
        
    def test_verify_password_reset_token(self):
        """Test password reset token verification."""
        from app.core.security import create_password_reset_token, verify_password_reset_token
        
        email = "test@example.com"
        token = create_password_reset_token(email)
        
        # Valid token should return email
        result = verify_password_reset_token(token)
        assert result == email
        
        # Invalid token should return None
        assert verify_password_reset_token("invalid") is None
        
    def test_email_verification_token(self):
        """Test email verification token functions."""
        from app.core.security import create_email_verification_token, verify_email_verification_token
        
        email = "test@example.com"
        token = create_email_verification_token(email)
        
        # Valid token should return email
        result = verify_email_verification_token(token)
        assert result == email
        
        # Invalid token should return None
        assert verify_email_verification_token("invalid") is None
        
    def test_api_key_generation(self):
        """Test API key generation functions."""
        from app.core.security import generate_api_key, hash_api_key, verify_api_key
        
        # Generate API key
        api_key = generate_api_key()
        assert isinstance(api_key, str)
        assert api_key.startswith("gr_")
        assert len(api_key) > 10
        
        # Hash and verify API key
        hashed = hash_api_key(api_key)
        assert hashed != api_key
        assert verify_api_key(api_key, hashed) is True
        assert verify_api_key("wrong_key", hashed) is False
        
    def test_token_validation_edge_cases(self):
        """Test token validation edge cases."""
        from app.core.security import verify_token
        
        # Invalid token should return None
        assert verify_token("invalid_token") is None
        
        # Empty token should return None
        assert verify_token("") is None
        
        # None token should return None
        assert verify_token(None) is None


class TestRBACModuleCoverage:
    """Test RBAC module functions for coverage."""
    
    @patch('app.core.rbac.get_db')
    def test_get_current_user_dependency(self, mock_get_db):
        """Test get_current_user dependency function."""
        from app.core.rbac import get_current_user
        from fastapi.security import HTTPAuthorizationCredentials
        from fastapi import HTTPException
        
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Test with invalid credentials
        with pytest.raises(HTTPException):
            get_current_user(
                credentials=HTTPAuthorizationCredentials(
                    scheme="Bearer",
                    credentials="invalid_token"
                ),
                db=mock_db
            )
    
    def test_permission_required_decorator(self):
        """Test permission_required decorator."""
        from app.core.rbac import permission_required
        
        @permission_required("test:read")
        def test_function():
            return "success"
        
        # Function should be decorated
        assert hasattr(test_function, '__wrapped__')
        
    def test_role_required_decorator(self):
        """Test role_required decorator.""" 
        from app.core.rbac import role_required
        
        @role_required("admin")
        def test_function():
            return "success"
        
        # Function should be decorated
        assert hasattr(test_function, '__wrapped__')
        
    def test_rbac_enum_values(self):
        """Test RBAC enum values."""
        from app.core.rbac import RoleNames, PermissionActions, Resources
        
        # Test RoleNames enum
        assert RoleNames.SUPER_ADMIN.value == "super_admin"
        assert RoleNames.ADMIN.value == "admin"
        assert RoleNames.CLIENT.value == "client"
        
        # Test PermissionActions enum
        assert PermissionActions.CREATE.value == "create"
        assert PermissionActions.READ.value == "read"
        assert PermissionActions.UPDATE.value == "update"
        assert PermissionActions.DELETE.value == "delete"
        
        # Test Resources enum
        assert Resources.USER.value == "user"
        assert Resources.ORGANIZATION.value == "organization"
        

class TestRateLimitModuleCoverage:
    """Test rate limiting module functions for coverage."""
    
    def test_get_client_ip_function(self):
        """Test get_client_ip function."""
        from app.core.rate_limit import get_client_ip
        from fastapi import Request
        
        # Mock request with headers
        mock_request = Mock(spec=Request)
        mock_request.headers = {"X-Forwarded-For": "192.168.1.1"}
        mock_request.client.host = "127.0.0.1"
        
        ip = get_client_ip(mock_request)
        assert isinstance(ip, str)
        
    def test_redis_connection_failure(self):
        """Test Redis connection failure handling."""
        from app.core.rate_limit import get_redis_client
        
        # Should handle connection failure gracefully
        client = get_redis_client()
        # Could be None if Redis is not available
        assert client is None or hasattr(client, 'ping')
        
    @patch('app.core.rate_limit.redis')
    def test_redis_client_success(self, mock_redis):
        """Test successful Redis client creation."""
        from app.core.rate_limit import get_redis_client
        
        # Mock successful Redis connection
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_redis.from_url.return_value = mock_client
        
        client = get_redis_client()
        assert client == mock_client
        
    def test_ip_ban_middleware_init(self):
        """Test IPBanMiddleware initialization."""
        from app.core.rate_limit import IPBanMiddleware
        from fastapi import FastAPI
        
        app = FastAPI()
        middleware = IPBanMiddleware(app)
        
        assert middleware.app == app
        assert hasattr(middleware, 'banned_ips')
        
    def test_rate_limit_exceeded_handler(self):
        """Test rate limit exceeded handler."""
        from app.core.rate_limit import rate_limit_exceeded_handler
        from fastapi import Request
        from slowapi.errors import RateLimitExceeded
        
        mock_request = Mock(spec=Request)
        mock_exc = Mock(spec=RateLimitExceeded)
        mock_exc.detail = "Rate limit exceeded"
        
        response = rate_limit_exceeded_handler(mock_request, mock_exc)
        assert response.status_code == 429


class TestSchemaValidationCoverage:
    """Test schema validation for additional coverage."""
    
    def test_token_data_schema(self):
        """Test TokenData schema."""
        from app.schemas.auth import TokenData
        
        token_data = TokenData(
            user_id=1,
            username="testuser",
            email="test@example.com",
            org_id=1,
            permissions=["read", "write"],
            exp=datetime.utcnow()
        )
        
        assert token_data.user_id == 1
        assert token_data.username == "testuser"
        assert len(token_data.permissions) == 2
        
    def test_refresh_token_request_schema(self):
        """Test RefreshTokenRequest schema."""
        from app.schemas.auth import RefreshTokenRequest
        
        request = RefreshTokenRequest(refresh_token="abc123")
        assert request.refresh_token == "abc123"
        
    def test_email_verification_request_schema(self):
        """Test EmailVerificationRequest schema."""
        from app.schemas.auth import EmailVerificationRequest
        
        request = EmailVerificationRequest(email="test@example.com")
        assert request.email == "test@example.com"
        
    def test_totp_setup_response_schema(self):
        """Test TOTPSetupResponse schema."""
        from app.schemas.auth import TOTPSetupResponse
        
        response = TOTPSetupResponse(
            secret="ABCD1234",
            qr_code_url="data:image/png;base64,abc",
            backup_codes=["123456", "789012"]
        )
        
        assert response.secret == "ABCD1234"
        assert len(response.backup_codes) == 2
        
    def test_totp_verify_request_schema(self):
        """Test TOTPVerifyRequest schema."""
        from app.schemas.auth import TOTPVerifyRequest
        
        request = TOTPVerifyRequest(code="123456")
        assert request.code == "123456"
        
    def test_webauthn_schemas(self):
        """Test WebAuthn schemas."""
        from app.schemas.auth import (
            WebAuthnRegisterInit, WebAuthnRegisterComplete,
            WebAuthnAuthInit, WebAuthnAuthComplete
        )
        
        # Test registration init
        reg_init = WebAuthnRegisterInit(
            username="testuser",
            display_name="Test User"
        )
        assert reg_init.username == "testuser"
        
        # Test registration complete
        reg_complete = WebAuthnRegisterComplete(
            credential={"id": "abc123"},
            username="testuser"
        )
        assert reg_complete.credential["id"] == "abc123"
        
        # Test auth init
        auth_init = WebAuthnAuthInit(username="testuser")
        assert auth_init.username == "testuser"
        
        # Test auth complete
        auth_complete = WebAuthnAuthComplete(
            credential={"response": "xyz789"},
            username="testuser"
        )
        assert auth_complete.credential["response"] == "xyz789"
        
    def test_api_key_schemas(self):
        """Test API key schemas."""
        from app.schemas.auth import APIKeyCreate, APIKeyResponse
        
        # Test creation request
        create_request = APIKeyCreate(
            name="Test API Key",
            description="For testing",
            expires_days=30
        )
        assert create_request.name == "Test API Key"
        assert create_request.expires_days == 30
        
        # Test response
        response = APIKeyResponse(
            id=1,
            name="Test API Key",
            key_prefix="gr_abc",
            api_key="gr_abc123456789",
            is_active=True,
            created_at=datetime.utcnow()
        )
        assert response.id == 1
        assert response.api_key.startswith("gr_")
        
    def test_password_validation_edge_cases(self):
        """Test password validation edge cases."""
        from app.schemas.auth import UserRegister, ChangePasswordRequest
        from pydantic import ValidationError
        
        # Test password that's too short
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                username="test",
                email="test@example.com",
                password="short",  # Too short
                first_name="Test",
                last_name="User", 
                organization_id=1
            )
        
        errors = exc_info.value.errors()
        password_errors = [e for e in errors if 'password' in str(e['loc'])]
        assert len(password_errors) > 0
        
        # Test ChangePasswordRequest validation
        with pytest.raises(ValidationError):
            ChangePasswordRequest(
                current_password="old",
                new_password="weak"  # Should fail validation
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])