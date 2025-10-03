"""Rate limiting middleware using Redis."""

import time
from typing import Callable, Optional
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
import redis
import structlog
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings

logger = structlog.get_logger(__name__)


class RateLimitConfig:
    """Rate limiting configuration."""
    
    # Default rate limits by endpoint type
    login_limit = 5
    register_limit = 3  
    default_limit = 100
    
    # Rate limit strings for slowapi
    AUTH_ENDPOINTS = "5/minute"     # Login, register, etc.
    API_ENDPOINTS = "100/minute"    # Regular API calls
    PUBLIC_ENDPOINTS = "200/minute" # Public endpoints
    
    # Strict limits for sensitive operations
    PASSWORD_RESET = "3/hour"       # Password reset requests
    EMAIL_VERIFICATION = "5/hour"   # Email verification
    TOTP_VERIFICATION = "10/minute" # TOTP verification attempts


def get_redis_client() -> Optional[redis.Redis]:
    """Get Redis client for rate limiting."""
    if not settings.RATE_LIMIT_ENABLED:
        return None
        
    try:
        client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        # Test connection
        client.ping()
        return client
    except Exception as e:
        logger.warning("Redis connection failed, rate limiting disabled", error=str(e))
        return None


def get_client_ip(request: Request) -> str:
    """
    Get client IP address with support for proxy headers.
    
    Args:
        request: FastAPI request
        
    Returns:
        Client IP address
    """
    # Check for forwarded headers (behind proxy/load balancer)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP (client IP) from the chain
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fallback to direct client IP
    return get_remote_address(request)


def create_rate_limiter() -> Limiter:
    """Create rate limiter instance."""
    redis_client = get_redis_client()
    config = RateLimitConfig()
    
    if redis_client:
        limiter = Limiter(
            key_func=get_client_ip,
            storage_uri=settings.REDIS_URL,
            default_limits=[config.API_ENDPOINTS]
        )
        logger.info("Rate limiting enabled with Redis backend")
    else:
        # In-memory fallback (not suitable for production)
        limiter = Limiter(
            key_func=get_client_ip,
            default_limits=[config.API_ENDPOINTS]
        )
        logger.warning("Rate limiting using in-memory storage (development only)")
    
    return limiter


# Global limiter instance
limiter = create_rate_limiter()


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom rate limit exceeded handler.
    
    Args:
        request: FastAPI request
        exc: Rate limit exceeded exception
        
    Returns:
        JSON error response
    """
    client_ip = get_client_ip(request)
    
    logger.warning(
        "Rate limit exceeded",
        client_ip=client_ip,
        endpoint=str(request.url),
        limit=exc.detail
    )
    
    response = JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please try again later.",
            "detail": exc.detail,
            "retry_after": exc.retry_after if hasattr(exc, 'retry_after') else None
        }
    )
    
    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(exc.detail)
    response.headers["X-RateLimit-Remaining"] = "0"
    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
    
    return response


class IPBanMiddleware:
    """
    IP-based blocking middleware for suspicious activity.
    
    Features:
    - Automatic IP blocking after too many failed auth attempts
    - Configurable ban duration and thresholds
    - Whitelist support for trusted IPs
    """
    
    def __init__(
        self,
        redis_client: Optional[redis.Redis] = None,
        ban_threshold: int = 10,
        ban_duration: int = 3600,  # 1 hour
        whitelist: Optional[list] = None
    ):
        self.redis = redis_client or get_redis_client()
        self.ban_threshold = ban_threshold
        self.ban_duration = ban_duration
        self.whitelist = whitelist or ["127.0.0.1", "::1"]  # localhost
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Process request through IP ban middleware."""
        if not self.redis:
            return await call_next(request)
        
        client_ip = get_client_ip(request)
        
        # Skip whitelist IPs
        if client_ip in self.whitelist:
            return await call_next(request)
        
        # Check if IP is banned
        ban_key = f"banned_ip:{client_ip}"
        if self.redis.exists(ban_key):
            logger.warning("Blocked request from banned IP", client_ip=client_ip)
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "error": "ip_banned",
                    "message": "Your IP address has been temporarily blocked due to suspicious activity."
                }
            )
        
        response = await call_next(request)
        
        # Track failed authentication attempts
        if (response.status_code == 401 and 
            request.url.path in ["/api/v1/auth/login", "/api/v1/auth/register"]):
            await self._track_failed_attempt(client_ip)
        
        return response
    
    async def _track_failed_attempt(self, client_ip: str):
        """Track failed authentication attempts."""
        if not self.redis:
            return
        
        attempts_key = f"failed_attempts:{client_ip}"
        
        # Increment attempts
        attempts = self.redis.incr(attempts_key)
        
        # Set expiration on first attempt
        if attempts == 1:
            self.redis.expire(attempts_key, 3600)  # Reset counter after 1 hour
        
        # Ban IP if threshold exceeded
        if attempts >= self.ban_threshold:
            ban_key = f"banned_ip:{client_ip}"
            self.redis.setex(ban_key, self.ban_duration, "banned")
            
            logger.warning(
                "IP banned for excessive failed attempts",
                client_ip=client_ip,
                attempts=attempts,
                ban_duration=self.ban_duration
            )
    
    def unban_ip(self, client_ip: str) -> bool:
        """
        Manually unban an IP address.
        
        Args:
            client_ip: IP address to unban
            
        Returns:
            True if IP was banned and is now unbanned
        """
        if not self.redis:
            return False
        
        ban_key = f"banned_ip:{client_ip}"
        attempts_key = f"failed_attempts:{client_ip}"
        
        # Remove ban and reset attempts
        banned = self.redis.delete(ban_key) > 0
        self.redis.delete(attempts_key)
        
        if banned:
            logger.info("IP manually unbanned", client_ip=client_ip)
        
        return banned


# Global IP ban middleware instance
ip_ban_middleware = IPBanMiddleware()


def get_rate_limit_info(request: Request) -> dict:
    """
    Get current rate limit information for client.
    
    Args:
        request: FastAPI request
        
    Returns:
        Rate limit information
    """
    client_ip = get_client_ip(request)
    
    if not limiter.storage:
        return {
            "rate_limiting": False,
            "message": "Rate limiting not configured"
        }
    
    # This would need to be implemented based on the storage backend
    # For now, return basic info
    return {
        "rate_limiting": True,
        "client_ip": client_ip,
        "limits": {
            "auth_endpoints": RateLimitConfig.AUTH_ENDPOINTS,
            "api_endpoints": RateLimitConfig.API_ENDPOINTS,
            "public_endpoints": RateLimitConfig.PUBLIC_ENDPOINTS
        }
    }