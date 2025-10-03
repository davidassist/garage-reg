"""Security utilities for authentication, authorization, and password hashing."""

from datetime import datetime, timedelta
from typing import Any, Union, Optional, List
import secrets
import hashlib
import hmac
from jose import JWTError, jwt
from passlib.context import CryptContext
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, HashingError
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class PasswordHandler:
    """Secure password hashing using Argon2id algorithm."""
    
    def __init__(self):
        """Initialize Argon2 password hasher with secure parameters from handbook."""
        self.hasher = PasswordHasher(
            memory_cost=65536,      # 64 MiB (from handbook)
            time_cost=3,            # 3 iterations
            parallelism=4,          # 4 threads
            hash_len=32,            # 32 bytes output
            salt_len=16,            # 16 bytes salt
            encoding='utf-8'
        )
        
        # Fallback context for compatibility
        self.pwd_context = CryptContext(
            schemes=["argon2"],
            deprecated="auto",
            argon2__memory_cost=65536,
            argon2__time_cost=3,
            argon2__parallelism=4,
            argon2__hash_len=32,
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


# Global password handler
password_handler = PasswordHandler()


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
        "type": "access",
        "jti": generate_secure_random_string(16)  # JWT ID for revocation
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
        expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
        "jti": generate_secure_random_string(16)
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


def generate_email_verification_token(email: str) -> str:
    """
    Generate email verification token.
    
    Args:
        email: User email
        
    Returns:
        Email verification token
    """
    delta = timedelta(days=7)  # Verification token valid for 7 days
    return create_access_token(
        subject=email,
        expires_delta=delta,
        additional_claims={"type": "email_verification"}
    )


def verify_email_verification_token(token: str) -> Optional[str]:
    """
    Verify email verification token and return email.
    
    Args:
        token: Email verification token
        
    Returns:
        Email if token is valid, None otherwise
    """
    payload = verify_token(token, token_type="access")
    if payload and payload.get("type") == "email_verification":
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
        API key string
    """
    return f"gr_{generate_secure_random_string(40)}"


def constant_time_compare(a: str, b: str) -> bool:
    """
    Constant time string comparison to prevent timing attacks.
    
    Args:
        a: First string
        b: Second string
        
    Returns:
        True if strings are equal
    """
    return hmac.compare_digest(a.encode(), b.encode())


def mask_sensitive_data(data: str, show_chars: int = 4) -> str:
    """
    Mask sensitive data for logging.
    
    Args:
        data: Data to mask
        show_chars: Number of characters to show at end
        
    Returns:
        Masked data string
    """
    if len(data) <= show_chars:
        return "*" * len(data)
    return "*" * (len(data) - show_chars) + data[-show_chars:]


def hash_password(password: str) -> str:
    """Hash a password using Argon2id."""
    return password_handler.hash_password(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return password_handler.verify_password(password, hashed_password)


def get_cors_origins() -> List[str]:
    """Get CORS origins from settings."""
    return settings.CORS_ORIGINS.split(",")


def decode_jwt_token(token: str) -> Optional[Any]:
    """Decode JWT token and return payload."""
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning("JWT token decode failed", error=str(e))
        return None


def get_security_headers() -> dict:
    """Get security headers."""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
    }


# =============================================================================
# FIELD TOKEN MANAGEMENT (for QR/NFC access)
# =============================================================================

def create_field_token(
    gate_id: int,
    org_id: int,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict] = None
) -> str:
    """
    Create JWT field access token for QR/NFC gate access.
    
    Args:
        gate_id: Gate ID
        org_id: Organization ID
        expires_delta: Custom expiration time
        additional_claims: Additional claims to include
        
    Returns:
        Encoded JWT field token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=168)  # Default 1 week
    
    to_encode = {
        "gate_id": gate_id,
        "org_id": org_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "field_access",
        "jti": generate_secure_random_string(16)  # JWT ID for tracking
    }
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    try:
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        logger.debug("Field token created", gate_id=gate_id, org_id=org_id, expires=expire)
        return encoded_jwt
    except Exception as e:
        logger.error("Failed to create field token", error=str(e))
        raise


def verify_field_token(token: str) -> Optional[dict]:
    """
    Verify and decode field access token.
    
    Args:
        token: Field access token to verify
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Verify token type
        if payload.get("type") != "field_access":
            logger.warning("Invalid field token type", got=payload.get("type"))
            return None
        
        # Verify expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            logger.warning("Field token expired")
            return None
        
        # Verify required fields
        if not payload.get("gate_id") or not payload.get("org_id"):
            logger.warning("Field token missing required fields")
            return None
        
        logger.debug("Field token verified successfully", 
                    gate_id=payload.get("gate_id"), 
                    org_id=payload.get("org_id"))
        return payload
        
    except JWTError as e:
        logger.warning("Field token JWT verification failed", error=str(e))
        return None
    except Exception as e:
        logger.error("Field token verification error", error=str(e))
        return None