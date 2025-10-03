"""Security utilities for authentication, authorization, and password hashing."""

from datetime import datetime, timedelta
from typing import Any, Union, Optional
import secrets
from passlib.context import CryptContext
from passlib.hash import argon2
from jose import JWTError, jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, HashingError
import structlog

from app.core.config import get_settings

settings = get_settings()
logger = structlog.get_logger(__name__)


# =============================================================================
# PASSWORD HASHING WITH ARGON2ID
# =============================================================================

class PasswordHandler:
    """Secure password hashing using Argon2id algorithm."""
    
    def __init__(self):
        """Initialize Argon2 password hasher with secure parameters."""
        self.hasher = PasswordHasher(
            memory_cost=settings.ARGON2_MEMORY_COST,  # 64 MiB
            time_cost=settings.ARGON2_TIME_COST,      # 3 iterations  
            parallelism=settings.ARGON2_PARALLELISM,  # 4 threads
            hash_len=settings.ARGON2_HASH_LENGTH,     # 32 bytes
            salt_len=16,                              # 16 bytes salt
            encoding='utf-8'
        )
        
        # Fallback context for compatibility
        self.pwd_context = CryptContext(
            schemes=["argon2"],
            deprecated="auto",
            argon2__memory_cost=settings.ARGON2_MEMORY_COST,
            argon2__time_cost=settings.ARGON2_TIME_COST,
            argon2__parallelism=settings.ARGON2_PARALLELISM,
            argon2__hash_len=settings.ARGON2_HASH_LENGTH,
        )
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using Argon2id.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
            
        Raises:
            HashingError: If hashing fails
        """
        try:
            hashed = self.hasher.hash(password)
            logger.debug("Password hashed successfully")
            return hashed
        except HashingError as e:
            logger.error("Password hashing failed", error=str(e))
            raise
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password
            hashed_password: Stored hash
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            self.hasher.verify(hashed_password, password)
            logger.debug("Password verification successful")
            return True
        except VerifyMismatchError:
            logger.warning("Password verification failed - mismatch")
            return False
        except Exception as e:
            logger.error("Password verification error", error=str(e))
            return False
    
    def needs_update(self, hashed_password: str) -> bool:
        """
        Check if password hash needs updating (parameters changed).
        
        Args:
            hashed_password: Stored hash
            
        Returns:
            True if hash should be updated
        """
        try:
            return self.hasher.check_needs_rehash(hashed_password)
        except Exception:
            return True  # If we can't check, assume it needs update


# Global password handler instance
password_handler = PasswordHandler()

# Convenience functions
def hash_password(password: str) -> str:
    """Hash a password using Argon2id."""
    return password_handler.hash_password(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return password_handler.verify_password(password, hashed_password)


# =============================================================================
# JWT TOKEN MANAGEMENT
# =============================================================================

def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict] = None
) -> str:
    """
    Create JWT access token.
    
    Args:
        subject: Token subject (usually user ID)
        expires_delta: Custom expiration time
        additional_claims: Additional claims to include
        
    Returns:
        Encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    try:
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        logger.debug("Access token created", subject=subject, expires=expire)
        return encoded_jwt
    except Exception as e:
        logger.error("Failed to create access token", error=str(e))
        raise


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT refresh token.
    
    Args:
        subject: Token subject (usually user ID)
        expires_delta: Custom expiration time
        
    Returns:
        Encoded JWT refresh token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
        "jti": secrets.token_urlsafe(32)  # Unique token ID
    }
    
    try:
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        logger.debug("Refresh token created", subject=subject, expires=expire)
        return encoded_jwt
    except Exception as e:
        logger.error("Failed to create refresh token", error=str(e))
        raise


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """
    Verify and decode JWT token.
    
    Args:
        token: JWT token to verify
        token_type: Expected token type (access/refresh)
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Verify token type
        if payload.get("type") != token_type:
            logger.warning("Invalid token type", expected=token_type, got=payload.get("type"))
            return None
        
        # Verify expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            logger.warning("Token expired")
            return None
        
        logger.debug("Token verified successfully", subject=payload.get("sub"))
        return payload
        
    except JWTError as e:
        logger.warning("JWT verification failed", error=str(e))
        return None
    except Exception as e:
        logger.error("Token verification error", error=str(e))
        return None


def generate_password_reset_token(email: str) -> str:
    """
    Generate password reset token.
    
    Args:
        email: User email
        
    Returns:
        Password reset token
    """
    delta = timedelta(hours=1)  # Reset token valid for 1 hour
    return create_access_token(
        subject=email,
        expires_delta=delta,
        additional_claims={"type": "password_reset"}
    )


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify password reset token and return email.
    
    Args:
        token: Password reset token
        
    Returns:
        Email if token is valid, None otherwise
    """
    payload = verify_token(token, token_type="access")
    if payload and payload.get("type") == "password_reset":
        return payload.get("sub")
    return None


# =============================================================================
# SECURITY UTILITIES
# =============================================================================

def generate_secure_random_string(length: int = 32) -> str:
    """
    Generate cryptographically secure random string.
    
    Args:
        length: Length of the string
        
    Returns:
        Secure random string
    """
    return secrets.token_urlsafe(length)


def generate_api_key() -> str:
    """
    Generate API key.
    
    Returns:
        Secure API key
    """
    return f"grl_{secrets.token_urlsafe(32)}"  # grl = GarageReg Live


def constant_time_compare(a: str, b: str) -> bool:
    """
    Compare two strings in constant time to prevent timing attacks.
    
    Args:
        a: First string
        b: Second string
        
    Returns:
        True if strings are equal
    """
    return secrets.compare_digest(a.encode('utf-8'), b.encode('utf-8'))


def mask_sensitive_data(data: str, show_chars: int = 4) -> str:
    """
    Mask sensitive data for logging.
    
    Args:
        data: Sensitive data to mask
        show_chars: Number of characters to show at the end
        
    Returns:
        Masked string
    """
    if len(data) <= show_chars:
        return '*' * len(data)
    return '*' * (len(data) - show_chars) + data[-show_chars:]


# =============================================================================
# CORS AND SECURITY HEADERS
# =============================================================================

def get_cors_origins() -> list[str]:
    """Get CORS allowed origins from settings."""
    return [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]


def get_security_headers() -> dict[str, str]:
    """Get security headers for HTTP responses."""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    }


# =============================================================================
# VALIDATION UTILITIES
# =============================================================================

def validate_email_format(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid format
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, list of issues)
    """
    issues = []
    
    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")
    
    if len(password) > 128:
        issues.append("Password must not exceed 128 characters")
    
    if not any(c.isupper() for c in password):
        issues.append("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in password):
        issues.append("Password must contain at least one lowercase letter")
    
    if not any(c.isdigit() for c in password):
        issues.append("Password must contain at least one digit")
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        issues.append("Password must contain at least one special character")
    
    return len(issues) == 0, issues