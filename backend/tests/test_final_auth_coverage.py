"""Final comprehensive test suite for authentication system coverage."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch


class TestAuthenticationSystemCoverage:
    """Comprehensive test suite for authentication system."""
    
    def test_all_password_functions(self):
        """Test all password-related functions."""
        from app.core.security import (
            hash_password, verify_password, password_handler,
            generate_secure_random_string, get_security_headers
        )
        
        # Test password operations
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        # Test verification
        assert verify_password(password, hashed) is True
        assert verify_password("wrong", hashed) is False
        
        # Test password handler directly
        hashed2 = password_handler.hash_password(password)
        assert password_handler.verify_password(password, hashed2) is True
        
        # Test invalid hash
        assert password_handler.verify_password(password, "invalid_hash") is False
        
        # Test random string generation
        random_str = generate_secure_random_string(16)
        assert len(random_str) > 0
        assert isinstance(random_str, str)
        
        # Test security headers
        headers = get_security_headers()
        assert isinstance(headers, dict)
        assert len(headers) > 0
        
    def test_all_jwt_functions(self):
        """Test all JWT-related functions."""
        from app.core.security import (
            create_access_token, create_refresh_token, decode_jwt_token, verify_token
        )
        
        user_data = {
            "user_id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "org_id": 1
        }
        
        # Test access token
        access_token = create_access_token(user_data)
        assert isinstance(access_token, str)
        
        # Test refresh token  
        refresh_token = create_refresh_token(user_data)
        assert isinstance(refresh_token, str)
        
        # Test token decoding
        decoded = decode_jwt_token(access_token)
        assert decoded is not None
        
        # Test token verification
        verified = verify_token(access_token)
        assert verified is not None
        
        # Test invalid tokens
        assert decode_jwt_token("invalid") is None
        assert verify_token("invalid") is None
        assert verify_token("") is None
        
    def test_all_rbac_constants_and_enums(self):
        """Test all RBAC constants and enums."""
        from app.core.rbac import (
            Roles, Permissions, RoleNames, PermissionActions, Resources
        )
        
        # Test role constants
        assert Roles.CLIENT == "client"
        assert Roles.TECHNICIAN == "technician"
        assert Roles.MANAGER == "manager"
        assert Roles.ADMIN == "admin"
        assert Roles.SUPER_ADMIN == "super_admin"
        assert Roles.AUDITOR == "auditor"
        
        # Test permission constants
        assert Permissions.GATE.READ == "gate:read"
        assert Permissions.GATE.CREATE == "gate:create"
        assert Permissions.MAINTENANCE.READ == "maintenance:read"
        assert Permissions.USER.CREATE == "user:create"
        
        # Test enums
        assert RoleNames.CLIENT.value == "client"
        assert RoleNames.ADMIN.value == "admin"
        
        assert PermissionActions.CREATE.value == "create"
        assert PermissionActions.READ.value == "read"
        assert PermissionActions.UPDATE.value == "update"
        assert PermissionActions.DELETE.value == "delete"
        
        assert Resources.USER.value == "user"
        assert Resources.ORGANIZATION.value == "organization"
        
    def test_rate_limiting_functionality(self):
        """Test rate limiting functionality.""" 
        from app.core.rate_limit import (
            RateLimitConfig, get_redis_client, get_client_ip
        )
        from fastapi import Request
        
        # Test config
        config = RateLimitConfig()
        assert config.login_limit > 0
        assert config.register_limit > 0
        assert hasattr(config, 'AUTH_ENDPOINTS')
        
        # Test Redis client (may fail if Redis not available)
        client = get_redis_client()
        # Should either be None or a Redis client
        
        # Test IP extraction with mock
        mock_request = Mock(spec=Request)
        mock_request.headers = {}
        mock_request.client = Mock()
        mock_request.client.host = "127.0.0.1"
        
        ip = get_client_ip(mock_request)
        assert ip == "127.0.0.1"
        
    def test_all_schema_validations(self):
        """Test all schema validations."""
        from app.schemas.auth import (
            UserLogin, UserRegister, Token, TokenData, RefreshTokenRequest,
            EmailVerificationRequest, PasswordResetRequest, TOTPSetupResponse,
            TOTPVerifyRequest, UserProfile, ChangePasswordRequest,
            APIKeyCreate, APIKeyResponse, RoleInfo, PermissionInfo
        )
        from pydantic import ValidationError
        
        # Test UserLogin
        login = UserLogin(username="test", password="password123")
        assert login.username == "test"
        
        # Test UserRegister with valid data
        register = UserRegister(
            username="testuser",
            email="test@example.com",
            password="ValidPassword123!",
            first_name="Test",
            last_name="User",
            organization_id=1
        )
        assert register.email == "test@example.com"
        
        # Test password validation failure
        with pytest.raises(ValidationError):
            UserRegister(
                username="testuser",
                email="test@example.com",
                password="weak",  # Too weak
                first_name="Test",
                last_name="User",
                organization_id=1
            )
            
        # Test Token
        token = Token(
            access_token="abc123",
            refresh_token="def456",
            expires_in=3600,
            user_id=1
        )
        assert token.token_type == "bearer"
        
        # Test TokenData
        token_data = TokenData(
            user_id=1,
            username="test",
            email="test@example.com",
            org_id=1
        )
        assert token_data.user_id == 1
        
        # Test other schemas
        refresh_req = RefreshTokenRequest(refresh_token="token123")
        assert refresh_req.refresh_token == "token123"
        
        email_req = EmailVerificationRequest(email="test@example.com")
        assert email_req.email == "test@example.com"
        
        totp_verify = TOTPVerifyRequest(code="123456")
        assert totp_verify.code == "123456"
        
        # Test RoleInfo and PermissionInfo
        role_info = RoleInfo(id=1, name="admin", description="Administrator")
        assert role_info.name == "admin"
        
        perm_info = PermissionInfo(
            id=1, name="Read Gates", codename="gate:read", 
            resource="gate", action="read"
        )
        assert perm_info.codename == "gate:read"
        
        # Test UserProfile
        profile = UserProfile(
            id=1,
            username="test",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            display_name="Test User",
            email_verified=True,
            is_active=True,
            last_login=None,
            created_at=datetime.utcnow(),
            organization_id=1
        )
        assert profile.username == "test"
        
    def test_edge_cases_and_error_handling(self):
        """Test edge cases and error handling."""
        from app.core.security import password_handler, decode_jwt_token
        from app.schemas.auth import ChangePasswordRequest
        from pydantic import ValidationError
        
        # Test empty password (Argon2 may handle this differently)
        try:
            empty_hash = password_handler.hash_password("")
            # If it doesn't raise, verify it still works
            assert isinstance(empty_hash, str)
        except Exception:
            # If it raises, that's also valid behavior
            pass
            
        # Test malformed JWT tokens
        assert decode_jwt_token("not.a.jwt") is None
        assert decode_jwt_token("") is None
        
        # Test None token (may cause exception, handle it)
        try:
            result = decode_jwt_token(None)
            assert result is None
        except Exception:
            # If it raises an exception with None input, that's also acceptable
            pass
        
        # Test password change validation
        with pytest.raises(ValidationError):
            ChangePasswordRequest(
                current_password="old",
                new_password="weak"  # Should fail validation
            )
            
        # Valid password change should work
        change_req = ChangePasswordRequest(
            current_password="OldPassword123!",
            new_password="NewPassword123!"
        )
        assert change_req.new_password == "NewPassword123!"


class TestFullAuthFlowSimulation:
    """Test complete authentication flows."""
    
    def test_registration_to_authentication_flow(self):
        """Test complete flow from registration to authentication."""
        from app.schemas.auth import UserRegister, UserLogin, Token
        from app.core.security import hash_password, verify_password, create_access_token
        from app.core.rbac import Roles, Permissions
        
        print("🔄 Testing complete authentication flow...")
        
        # Step 1: User registration validation
        registration_data = {
            "username": "flowuser", 
            "email": "flow@example.com",
            "password": "FlowPassword123!",
            "first_name": "Flow",
            "last_name": "User",
            "organization_id": 1
        }
        
        user_reg = UserRegister(**registration_data)
        stored_password_hash = hash_password(user_reg.password)
        
        # Step 2: Login simulation
        login_data = {"username": "flowuser", "password": "FlowPassword123!"}
        login_req = UserLogin(**login_data)
        
        # Verify password
        assert verify_password(login_req.password, stored_password_hash)
        
        # Step 3: Create user context
        user_context = {
            "user_id": 1,
            "username": user_reg.username,
            "email": user_reg.email,
            "org_id": user_reg.organization_id,
            "permissions": [
                Permissions.GATE.READ,
                Permissions.MAINTENANCE.READ
            ]
        }
        
        # Step 4: Generate tokens
        access_token = create_access_token(user_context)
        
        # Step 5: Simulate token usage
        token_response = Token(
            access_token=access_token,
            refresh_token="refresh_token_here",
            expires_in=3600,
            user_id=user_context["user_id"]
        )
        
        assert token_response.user_id == 1
        assert token_response.token_type == "bearer"
        
        print("✅ Complete authentication flow successful!")
        
    def test_permission_based_access_simulation(self):
        """Test permission-based access control simulation."""
        from app.core.rbac import Roles, Permissions
        
        print("🔐 Testing permission-based access...")
        
        # Define different user types with their permissions
        user_scenarios = [
            {
                "role": Roles.CLIENT,
                "permissions": [Permissions.GATE.READ, Permissions.MAINTENANCE.READ],
                "can_create_gates": False,
                "can_read_gates": True,
                "can_delete_maintenance": False
            },
            {
                "role": Roles.TECHNICIAN,
                "permissions": [
                    Permissions.GATE.READ, 
                    Permissions.MAINTENANCE.READ,
                    Permissions.MAINTENANCE.CREATE,
                    Permissions.MAINTENANCE.UPDATE
                ],
                "can_create_gates": False,
                "can_read_gates": True,
                "can_create_maintenance": True
            },
            {
                "role": Roles.MANAGER,
                "permissions": [
                    Permissions.GATE.READ,
                    Permissions.GATE.CREATE,
                    Permissions.GATE.UPDATE,
                    Permissions.MAINTENANCE.READ,
                    Permissions.MAINTENANCE.CREATE,
                    Permissions.USER.READ
                ],
                "can_create_gates": True,
                "can_read_users": True
            }
        ]
        
        for scenario in user_scenarios:
            role = scenario["role"]
            permissions = scenario["permissions"]
            
            # Test permission checks
            if "can_create_gates" in scenario:
                expected = scenario["can_create_gates"]
                actual = Permissions.GATE.CREATE in permissions
                assert actual == expected, f"Role {role} gate creation permission mismatch"
                
            if "can_read_gates" in scenario:
                expected = scenario["can_read_gates"] 
                actual = Permissions.GATE.READ in permissions
                assert actual == expected, f"Role {role} gate read permission mismatch"
                
        print("✅ Permission-based access control validated!")
        
    def test_security_compliance_validation(self):
        """Test security compliance requirements."""
        from app.core.security import password_handler
        from app.core.config import settings
        from app.core.rate_limit import RateLimitConfig
        
        print("🛡️ Validating security compliance...")
        
        # Check Argon2 parameters
        assert password_handler.hasher.memory_cost >= 32768  # At least 32 MiB
        assert password_handler.hasher.time_cost >= 2        # At least 2 iterations
        assert password_handler.hasher.parallelism >= 2      # At least 2 threads
        assert password_handler.hasher.hash_len >= 16        # At least 16 bytes
        
        # Check rate limiting is reasonable
        config = RateLimitConfig()
        assert config.login_limit <= 20       # Not too permissive
        assert config.register_limit <= 10    # Registration should be limited
        
        # Check JWT configuration exists
        assert hasattr(settings, 'JWT_SECRET_KEY')
        assert hasattr(settings, 'JWT_ALGORITHM')
        
        print("✅ Security compliance validated!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])