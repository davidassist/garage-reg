"""
Security Middleware Stack for GarageReg
Implements Helmet-style security headers, CORS, and protection mechanisms
"""

from typing import Dict, List, Optional, Set, Union
import time
import asyncio
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from collections import defaultdict, deque
from ipaddress import ip_address, ip_network
import re

from fastapi import Request, Response, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import redis.asyncio as redis
from starlette.types import ASGIApp
import structlog

logger = structlog.get_logger(__name__)

class SecurityConfig:
    """Security configuration settings"""
    
    # Security Headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY", 
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        "X-Permitted-Cross-Domain-Policies": "none",
        "Cache-Control": "no-store, max-age=0",
    }
    
    # Content Security Policy
    CSP_POLICY = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )
    
    # CORS Settings
    CORS_SETTINGS = {
        "allow_origins": [
            "https://admin.garagereg.local",
            "https://app.garagereg.local", 
            "http://localhost:3000",  # Development
            "http://localhost:5173",  # Vite dev server
        ],
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        "allow_headers": [
            "Authorization",
            "Content-Type",
            "X-Requested-With",
            "Accept",
            "Origin",
            "Cache-Control",
            "X-CSRF-Token",
        ],
        "max_age": 3600,
    }
    
    # Rate Limiting
    RATE_LIMITS = {
        "global": {"requests": 1000, "window": 3600},  # 1000 requests per hour
        "auth": {"requests": 10, "window": 300},       # 10 auth attempts per 5 minutes
        "api": {"requests": 100, "window": 300},       # 100 API calls per 5 minutes
        "upload": {"requests": 5, "window": 300},      # 5 uploads per 5 minutes
    }
    
    # Brute Force Protection
    BRUTE_FORCE_SETTINGS = {
        "max_attempts": 5,
        "lockout_duration": 900,  # 15 minutes
        "progressive_delay": True,
        "notification_threshold": 3,
    }
    
    # Input Validation
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_JSON_DEPTH = 10
    BLOCKED_USER_AGENTS = [
        "sqlmap", "nikto", "nmap", "masscan", "zap",
        "burp", "acunetix", "nessus", "openvas"
    ]
    
    # Security Monitoring
    SUSPICIOUS_PATTERNS = [
        r"(\bor\b|\band\b).+(=|<|>)",  # SQL injection patterns
        r"<script[^>]*>",              # XSS patterns
        r"javascript:",                # XSS patterns
        r"\.\./",                      # Path traversal
        r"cmd\.exe|powershell\.exe",   # Command injection
    ]

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Implements Helmet-style security headers"""
    
    def __init__(self, app: ASGIApp, config: SecurityConfig = None):
        super().__init__(app)
        self.config = config or SecurityConfig()
    
    async def dispatch(self, request: Request, call_next):
        # Process request
        response = await call_next(request)
        
        # Add security headers
        for header, value in self.config.SECURITY_HEADERS.items():
            response.headers[header] = value
        
        # Add Content Security Policy
        response.headers["Content-Security-Policy"] = self.config.CSP_POLICY
        
        # Add security identifiers
        response.headers["X-Security-Framework"] = "GarageReg-Security-v1.0"
        response.headers["X-Request-ID"] = getattr(request.state, "request_id", "unknown")
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Advanced rate limiting with Redis backend"""
    
    def __init__(
        self, 
        app: ASGIApp, 
        redis_client: redis.Redis,
        config: SecurityConfig = None
    ):
        super().__init__(app)
        self.redis = redis_client
        self.config = config or SecurityConfig()
        self.rate_limits = self.config.RATE_LIMITS
    
    async def dispatch(self, request: Request, call_next):
        # Determine rate limit type based on path
        limit_type = self._get_limit_type(request.url.path)
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Check rate limit
        is_allowed, retry_after = await self._check_rate_limit(
            client_id, limit_type
        )
        
        if not is_allowed:
            logger.warning(
                "Rate limit exceeded",
                client_id=client_id,
                limit_type=limit_type,
                path=request.url.path,
                retry_after=retry_after
            )
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": retry_after,
                    "limit_type": limit_type
                },
                headers={"Retry-After": str(retry_after)}
            )
        
        # Continue with request
        response = await call_next(request)
        
        # Add rate limit headers
        limit_info = await self._get_limit_info(client_id, limit_type)
        response.headers["X-RateLimit-Limit"] = str(limit_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(limit_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(limit_info["reset"])
        
        return response
    
    def _get_limit_type(self, path: str) -> str:
        """Determine rate limit type based on request path"""
        if "/auth/" in path:
            return "auth"
        elif "/upload" in path:
            return "upload"
        elif path.startswith("/api/"):
            return "api"
        else:
            return "global"
    
    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier"""
        # Try to get user ID from authenticated request
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        
        # Fall back to IP address
        client_ip = request.client.host
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
    
    async def _check_rate_limit(self, client_id: str, limit_type: str) -> tuple[bool, int]:
        """Check if request is within rate limits"""
        limit_config = self.rate_limits[limit_type]
        key = f"rate_limit:{limit_type}:{client_id}"
        
        # Use sliding window algorithm with Redis
        now = int(time.time())
        window = limit_config["window"]
        limit = limit_config["requests"]
        
        # Remove old entries
        await self.redis.zremrangebyscore(key, 0, now - window)
        
        # Count current requests
        current_count = await self.redis.zcard(key)
        
        if current_count >= limit:
            # Get oldest entry to calculate retry time
            oldest_entries = await self.redis.zrange(key, 0, 0, withscores=True)
            if oldest_entries:
                oldest_time = int(oldest_entries[0][1])
                retry_after = (oldest_time + window) - now
                return False, max(retry_after, 1)
            return False, window
        
        # Add current request
        await self.redis.zadd(key, {str(now): now})
        await self.redis.expire(key, window)
        
        return True, 0
    
    async def _get_limit_info(self, client_id: str, limit_type: str) -> Dict[str, int]:
        """Get current rate limit information"""
        limit_config = self.rate_limits[limit_type]
        key = f"rate_limit:{limit_type}:{client_id}"
        
        now = int(time.time())
        window = limit_config["window"]
        limit = limit_config["requests"]
        
        # Clean old entries
        await self.redis.zremrangebyscore(key, 0, now - window)
        
        # Get current count
        current_count = await self.redis.zcard(key)
        remaining = max(0, limit - current_count)
        
        # Calculate reset time
        reset_time = now + window
        
        return {
            "limit": limit,
            "remaining": remaining,
            "reset": reset_time
        }

class BruteForceProtectionMiddleware(BaseHTTPMiddleware):
    """Brute force attack protection"""
    
    def __init__(
        self, 
        app: ASGIApp, 
        redis_client: redis.Redis,
        config: SecurityConfig = None
    ):
        super().__init__(app)
        self.redis = redis_client
        self.config = config or SecurityConfig()
        self.bf_settings = self.config.BRUTE_FORCE_SETTINGS
    
    async def dispatch(self, request: Request, call_next):
        # Only check authentication endpoints
        if not self._is_auth_endpoint(request.url.path):
            return await call_next(request)
        
        client_id = self._get_client_id(request)
        
        # Check if client is locked out
        lockout_info = await self._check_lockout(client_id)
        if lockout_info["locked"]:
            logger.warning(
                "Brute force lockout",
                client_id=client_id,
                remaining_time=lockout_info["remaining_time"]
            )
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Account temporarily locked due to too many failed attempts",
                    "retry_after": lockout_info["remaining_time"],
                    "lockout_reason": "brute_force_protection"
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Handle authentication result
        if response.status_code == 401:
            await self._record_failed_attempt(client_id)
        elif response.status_code == 200:
            await self._clear_failed_attempts(client_id)
        
        return response
    
    def _is_auth_endpoint(self, path: str) -> bool:
        """Check if path is an authentication endpoint"""
        auth_patterns = ["/auth/login", "/auth/token", "/auth/refresh"]
        return any(pattern in path for pattern in auth_patterns)
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for brute force tracking"""
        client_ip = request.client.host
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        return f"bf:{client_ip}"
    
    async def _check_lockout(self, client_id: str) -> Dict[str, Union[bool, int]]:
        """Check if client is currently locked out"""
        lockout_key = f"lockout:{client_id}"
        
        lockout_until = await self.redis.get(lockout_key)
        if not lockout_until:
            return {"locked": False, "remaining_time": 0}
        
        lockout_time = int(lockout_until)
        now = int(time.time())
        
        if now < lockout_time:
            return {
                "locked": True,
                "remaining_time": lockout_time - now
            }
        
        # Lockout expired, clean up
        await self.redis.delete(lockout_key)
        return {"locked": False, "remaining_time": 0}
    
    async def _record_failed_attempt(self, client_id: str):
        """Record a failed authentication attempt"""
        attempts_key = f"attempts:{client_id}"
        
        # Increment attempts counter
        attempts = await self.redis.incr(attempts_key)
        await self.redis.expire(attempts_key, self.bf_settings["lockout_duration"])
        
        # Apply progressive delay
        if self.bf_settings["progressive_delay"]:
            delay = min(attempts * 2, 30)  # Max 30 second delay
            await asyncio.sleep(delay)
        
        # Check if lockout threshold reached
        if attempts >= self.bf_settings["max_attempts"]:
            await self._apply_lockout(client_id)
            
            # Trigger notification for security team
            if attempts >= self.bf_settings["notification_threshold"]:
                await self._notify_security_team(client_id, attempts)
    
    async def _apply_lockout(self, client_id: str):
        """Apply lockout to client"""
        lockout_key = f"lockout:{client_id}"
        lockout_until = int(time.time()) + self.bf_settings["lockout_duration"]
        
        await self.redis.setex(
            lockout_key,
            self.bf_settings["lockout_duration"],
            lockout_until
        )
        
        logger.warning(
            "Brute force lockout applied",
            client_id=client_id,
            lockout_duration=self.bf_settings["lockout_duration"]
        )
    
    async def _clear_failed_attempts(self, client_id: str):
        """Clear failed attempts after successful authentication"""
        attempts_key = f"attempts:{client_id}"
        await self.redis.delete(attempts_key)
    
    async def _notify_security_team(self, client_id: str, attempts: int):
        """Notify security team of brute force attempt"""
        # This would integrate with your notification system
        logger.critical(
            "Brute force attack detected",
            client_id=client_id,
            attempts=attempts,
            action_required=True
        )

class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """Input validation and sanitization middleware"""
    
    def __init__(self, app: ASGIApp, config: SecurityConfig = None):
        super().__init__(app)
        self.config = config or SecurityConfig()
        self.suspicious_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.config.SUSPICIOUS_PATTERNS
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.config.MAX_REQUEST_SIZE:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"error": "Request too large"}
            )
        
        # Check User-Agent
        user_agent = request.headers.get("user-agent", "").lower()
        if any(blocked in user_agent for blocked in self.config.BLOCKED_USER_AGENTS):
            logger.warning(
                "Blocked user agent detected",
                user_agent=user_agent,
                client_ip=request.client.host
            )
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"error": "Forbidden"}
            )
        
        # Validate request path
        if self._contains_suspicious_content(request.url.path):
            logger.warning(
                "Suspicious request path",
                path=request.url.path,
                client_ip=request.client.host
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Invalid request"}
            )
        
        # Validate query parameters
        for key, value in request.query_params.items():
            if self._contains_suspicious_content(f"{key}={value}"):
                logger.warning(
                    "Suspicious query parameter",
                    parameter=key,
                    value=value[:100],  # Log first 100 chars only
                    client_ip=request.client.host
                )
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"error": "Invalid parameters"}
                )
        
        # Continue processing
        return await call_next(request)
    
    def _contains_suspicious_content(self, content: str) -> bool:
        """Check if content contains suspicious patterns"""
        return any(pattern.search(content) for pattern in self.suspicious_patterns)

class SecurityAuditMiddleware(BaseHTTPMiddleware):
    """Security event logging and audit trail"""
    
    def __init__(
        self, 
        app: ASGIApp, 
        redis_client: redis.Redis,
        config: SecurityConfig = None
    ):
        super().__init__(app)
        self.redis = redis_client
        self.config = config or SecurityConfig()
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Generate request ID
        request_id = secrets.token_hex(16)
        request.state.request_id = request_id
        
        # Prepare audit log entry
        audit_entry = {
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": request.url.path,
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent"),
            "user_id": getattr(request.state, "user_id", None),
        }
        
        # Process request
        response = await call_next(request)
        
        # Complete audit entry
        audit_entry.update({
            "status_code": response.status_code,
            "response_time": round((time.time() - start_time) * 1000, 2),
            "response_size": response.headers.get("content-length", 0),
        })
        
        # Log security events
        await self._log_security_event(audit_entry)
        
        # Check for suspicious activity
        await self._analyze_request_patterns(audit_entry)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host
    
    async def _log_security_event(self, audit_entry: Dict):
        """Log security event to audit trail"""
        # Store in Redis for real-time monitoring
        audit_key = f"audit:{audit_entry['timestamp'][:10]}:{audit_entry['request_id']}"
        await self.redis.setex(
            audit_key,
            86400,  # 24 hours
            json.dumps(audit_entry)
        )
        
        # Log to structured logger
        logger.info(
            "Security audit event",
            **audit_entry
        )
        
        # Check for high-risk events
        if self._is_high_risk_event(audit_entry):
            logger.warning(
                "High-risk security event detected",
                **audit_entry
            )
    
    def _is_high_risk_event(self, audit_entry: Dict) -> bool:
        """Determine if event is high-risk"""
        high_risk_conditions = [
            audit_entry["status_code"] == 401,  # Authentication failure
            audit_entry["status_code"] == 403,  # Forbidden access
            audit_entry["status_code"] >= 500,  # Server errors
            "/admin" in audit_entry["path"],     # Admin area access
            audit_entry["method"] in ["DELETE", "PUT"],  # Destructive operations
        ]
        return any(high_risk_conditions)
    
    async def _analyze_request_patterns(self, audit_entry: Dict):
        """Analyze patterns for anomaly detection"""
        client_ip = audit_entry["client_ip"]
        
        # Track request frequency per IP
        frequency_key = f"freq:{client_ip}:{int(time.time()) // 60}"  # Per minute
        request_count = await self.redis.incr(frequency_key)
        await self.redis.expire(frequency_key, 60)
        
        # Alert on suspicious frequency
        if request_count > 100:  # More than 100 requests per minute
            logger.warning(
                "High request frequency detected",
                client_ip=client_ip,
                requests_per_minute=request_count
            )

def setup_security_middleware(app, redis_client: redis.Redis):
    """Setup all security middleware"""
    config = SecurityConfig()
    
    # Add CORS middleware first
    app.add_middleware(
        CORSMiddleware,
        **config.CORS_SETTINGS
    )
    
    # Add security middleware stack
    app.add_middleware(SecurityAuditMiddleware, redis_client=redis_client, config=config)
    app.add_middleware(InputSanitizationMiddleware, config=config)
    app.add_middleware(BruteForceProtectionMiddleware, redis_client=redis_client, config=config)
    app.add_middleware(RateLimitMiddleware, redis_client=redis_client, config=config)
    app.add_middleware(SecurityHeadersMiddleware, config=config)
    
    logger.info("Security middleware stack initialized")
    return app