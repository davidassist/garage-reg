"""
Unit Tests for Authentication Service
Tests core authentication functionality without external dependencies
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from jose import jwt

from app.core.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    authenticate_user
)
from app.core.config import get_settings
from app.models.user import User


class TestPasswordHashing:
    """Test password hashing functionality."""
    
    def test_password_hashing_and_verification(self):
        """Test password hashing and verification."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # Hash should be different from original password
        assert hashed != password
        assert len(hashed) > 50  # bcrypt hashes are long
        
        # Verify correct password
        assert verify_password(password, hashed) is True
        
        # Verify incorrect password
        assert verify_password("wrongpassword", hashed) is False
    
    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        password1 = "password123"
        password2 = "password456"
        
        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)
        
        assert hash1 != hash2
    
    def test_same_password_different_hashes(self):
        """Test that same password produces different hashes (salt)."""
        password = "samepassword"
        
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        
        # Both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """Test JWT token functionality."""
    
    def test_create_access_token(self):
        """Test access token creation."""
        data = {"sub": "testuser"}
        token = create_access_token(data=data)
        
        assert isinstance(token, str)
        assert len(token) > 100  # JWT tokens are long
        
        # Decode and verify token
        settings = get_settings()
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        assert payload["sub"] == "testuser"
        assert "exp" in payload
        assert "iat" in payload
    
    def test_create_access_token_with_expiration(self):
        """Test access token creation with custom expiration."""
        data = {"sub": "testuser"}
        expires_delta = timedelta(hours=1)
        token = create_access_token(data=data, expires_delta=expires_delta)
        
        settings = get_settings()
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        # Check expiration time is approximately 1 hour from now
        exp = datetime.fromtimestamp(payload["exp"])
        expected_exp = datetime.utcnow() + expires_delta
        
        # Allow 5 second tolerance for test execution time
        assert abs((exp - expected_exp).total_seconds()) < 5
    
    def test_verify_valid_token(self):
        """Test token verification with valid token."""
        data = {"sub": "testuser", "user_id": 123}
        token = create_access_token(data=data)
        
        payload = verify_token(token)
        
        assert payload["sub"] == "testuser"
        assert payload["user_id"] == 123
    
    def test_verify_expired_token(self):
        """Test token verification with expired token."""
        data = {"sub": "testuser"}
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = create_access_token(data=data, expires_delta=expires_delta)
        
        payload = verify_token(token)
        assert payload is None
    
    def test_verify_invalid_token(self):
        """Test token verification with invalid token."""
        invalid_token = "invalid.token.string"
        
        payload = verify_token(invalid_token)
        assert payload is None
    
    def test_verify_malformed_token(self):
        """Test token verification with malformed token."""
        malformed_token = "not-a-jwt-token"
        
        payload = verify_token(malformed_token)
        assert payload is None


class TestUserAuthentication:
    """Test user authentication functionality."""
    
    @pytest.fixture
    def mock_user(self):
        """Create mock user for testing."""
        user = Mock(spec=User)
        user.id = 1
        user.username = "testuser"
        user.email = "test@example.com"
        user.password_hash = get_password_hash("testpassword")
        user.is_active = True
        user.email_verified = True
        return user
    
    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        session = Mock()
        return session
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, mock_session, mock_user):
        """Test successful user authentication."""
        # Mock database query
        mock_session.execute.return_value.scalar_one_or_none.return_value = mock_user
        
        result = await authenticate_user(mock_session, "testuser", "testpassword")
        
        assert result == mock_user
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, mock_session, mock_user):
        """Test authentication with wrong password."""
        # Mock database query
        mock_session.execute.return_value.scalar_one_or_none.return_value = mock_user
        
        result = await authenticate_user(mock_session, "testuser", "wrongpassword")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, mock_session):
        """Test authentication with non-existent user."""
        # Mock database query returning None
        mock_session.execute.return_value.scalar_one_or_none.return_value = None
        
        result = await authenticate_user(mock_session, "nonexistent", "password")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_authenticate_inactive_user(self, mock_session, mock_user):
        """Test authentication with inactive user."""
        mock_user.is_active = False
        mock_session.execute.return_value.scalar_one_or_none.return_value = mock_user
        
        result = await authenticate_user(mock_session, "testuser", "testpassword")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_authenticate_unverified_user(self, mock_session, mock_user):
        """Test authentication with unverified user."""
        mock_user.email_verified = False
        mock_session.execute.return_value.scalar_one_or_none.return_value = mock_user
        
        result = await authenticate_user(mock_session, "testuser", "testpassword")
        
        assert result is None


class TestSecurityConstraints:
    """Test security constraints and edge cases."""
    
    def test_password_hash_empty_password(self):
        """Test password hashing with empty password."""
        with pytest.raises(ValueError):
            get_password_hash("")
    
    def test_password_hash_none_password(self):
        """Test password hashing with None password."""
        with pytest.raises(TypeError):
            get_password_hash(None)
    
    def test_verify_password_empty_inputs(self):
        """Test password verification with empty inputs."""
        hashed = get_password_hash("validpassword")
        
        # Empty plain password
        assert verify_password("", hashed) is False
        
        # Empty hash
        assert verify_password("validpassword", "") is False
    
    def test_token_with_invalid_secret(self):
        """Test token verification with wrong secret key."""
        data = {"sub": "testuser"}
        token = create_access_token(data=data)
        
        # Try to decode with wrong secret
        with patch('app.core.auth.get_settings') as mock_settings:
            mock_settings.return_value.secret_key = "wrong-secret"
            mock_settings.return_value.algorithm = "HS256"
            
            payload = verify_token(token)
            assert payload is None
    
    def test_token_with_no_subject(self):
        """Test token creation without subject."""
        data = {"user_id": 123}  # No 'sub' field
        token = create_access_token(data=data)
        
        # Should still create token
        assert isinstance(token, str)
        
        # Verify token
        payload = verify_token(token)
        assert payload["user_id"] == 123
        assert "sub" not in payload or payload["sub"] is None


class TestTokenExpiration:
    """Test token expiration scenarios."""
    
    def test_default_token_expiration(self):
        """Test token with default expiration."""
        data = {"sub": "testuser"}
        token = create_access_token(data=data)
        
        settings = get_settings()
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        # Check expiration is set to default (15 minutes)
        exp = datetime.fromtimestamp(payload["exp"])
        expected_exp = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        # Allow 5 second tolerance
        assert abs((exp - expected_exp).total_seconds()) < 5
    
    def test_custom_token_expiration(self):
        """Test token with custom expiration."""
        data = {"sub": "testuser"}
        custom_expiration = timedelta(days=1)
        token = create_access_token(data=data, expires_delta=custom_expiration)
        
        settings = get_settings()
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        # Check expiration is set to custom value
        exp = datetime.fromtimestamp(payload["exp"])
        expected_exp = datetime.utcnow() + custom_expiration
        
        # Allow 5 second tolerance
        assert abs((exp - expected_exp).total_seconds()) < 5
    
    @pytest.mark.slow
    def test_token_expiration_timing(self):
        """Test that tokens actually expire after the set time."""
        import time
        
        data = {"sub": "testuser"}
        expires_delta = timedelta(seconds=1)  # Very short expiration
        token = create_access_token(data=data, expires_delta=expires_delta)
        
        # Token should be valid immediately
        payload = verify_token(token)
        assert payload is not None
        
        # Wait for token to expire
        time.sleep(2)
        
        # Token should now be invalid
        payload = verify_token(token)
        assert payload is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])