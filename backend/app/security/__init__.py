"""
Security Integration and Initialization
Integrates all security components and provides initialization functions
"""

import asyncio
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

import redis.asyncio as redis
import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

# Import security components
from app.security.middleware import (
    SecurityConfig, SecurityHeadersMiddleware, RateLimitMiddleware,
    BruteForceProtectionMiddleware, InputSanitizationMiddleware,
    SecurityAuditMiddleware
)
from app.security.validation import InputValidator
from app.security.secrets import SecretsManager, init_secrets_manager
from app.security.rbac import RBACManager, init_rbac_manager
from app.security.audit import SecurityAuditor, init_security_auditor
from app.security.testing import run_security_tests

logger = structlog.get_logger(__name__)

class SecurityManager:
    """Central security management system"""
    
    def __init__(self):
        self.config: Optional[SecurityConfig] = None
        self.secrets_manager: Optional[SecretsManager] = None
        self.rbac_manager: Optional[RBACManager] = None
        self.security_auditor: Optional[SecurityAuditor] = None
        self.input_validator: Optional[InputValidator] = None
        self.redis_client: Optional[redis.Redis] = None
        self.initialized = False
    
    async def initialize(self, 
                        redis_url: str = "redis://localhost:6379",
                        jwt_secret: Optional[str] = None,
                        config_overrides: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize all security components"""
        try:
            logger.info("Initializing security manager")
            
            # Initialize Redis connection
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            await self.redis_client.ping()
            logger.info("Redis connection established")
            
            # Initialize security configuration
            self.config = SecurityConfig()
            if config_overrides:
                for key, value in config_overrides.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
            
            # Initialize secrets manager
            self.secrets_manager = init_secrets_manager(self.redis_client)
            logger.info("Secrets manager initialized")
            
            # Get or generate JWT secret
            if not jwt_secret:
                jwt_secret = await self.secrets_manager.get_secret("jwt_secret")
                if not jwt_secret:
                    jwt_secret = self.secrets_manager._generate_secret_key()
                    await self.secrets_manager.set_secret("jwt_secret", jwt_secret)
            
            # Initialize RBAC manager
            self.rbac_manager = init_rbac_manager(self.redis_client, jwt_secret)
            logger.info("RBAC manager initialized")
            
            # Initialize security auditor
            self.security_auditor = init_security_auditor(self.redis_client)
            logger.info("Security auditor initialized")
            
            # Initialize input validator
            self.input_validator = InputValidator()
            logger.info("Input validator initialized")
            
            self.initialized = True
            logger.info("Security manager initialization complete")
            
            return True
            
        except Exception as e:
            logger.error("Security manager initialization failed", error=str(e))
            return False
    
    async def shutdown(self):
        """Shutdown security manager and cleanup resources"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            # Stop any background tasks
            if self.secrets_manager:
                await self.secrets_manager.stop_key_rotation()
            
            logger.info("Security manager shutdown complete")
            
        except Exception as e:
            logger.error("Error during security manager shutdown", error=str(e))
    
    def configure_fastapi_security(self, app: FastAPI) -> FastAPI:
        """Configure FastAPI application with security middleware and settings"""
        if not self.initialized:
            raise RuntimeError("Security manager not initialized")
        
        logger.info("Configuring FastAPI security")
        
        # Configure CORS (restrictive by default)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.cors_allowed_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
            expose_headers=["X-Request-ID"]
        )
        
        # Add security middleware (order matters - reverse of processing order)
        app.add_middleware(SecurityAuditMiddleware, security_auditor=self.security_auditor)
        app.add_middleware(InputSanitizationMiddleware, input_validator=self.input_validator)
        app.add_middleware(BruteForceProtectionMiddleware, redis_client=self.redis_client)
        app.add_middleware(RateLimitMiddleware, redis_client=self.redis_client, config=self.config)
        app.add_middleware(SecurityHeadersMiddleware, config=self.config)
        
        # Add security event handlers
        @app.middleware("http")
        async def security_context_middleware(request: Request, call_next):
            """Add security context to requests"""
            # Add request ID for tracking
            request_id = request.headers.get("X-Request-ID")
            if not request_id:
                import uuid
                request_id = str(uuid.uuid4())
            
            request.state.request_id = request_id
            request.state.security_manager = self
            
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            
            return response
        
        logger.info("FastAPI security configuration complete")
        return app
    
    async def run_security_tests(self, app: FastAPI) -> Dict[str, Any]:
        """Run comprehensive security tests"""
        if not self.initialized:
            raise RuntimeError("Security manager not initialized")
        
        logger.info("Running security tests")
        return await run_security_tests(app, self.redis_client)
    
    async def get_security_status(self) -> Dict[str, Any]:
        """Get current security system status"""
        status = {
            "initialized": self.initialized,
            "timestamp": str(asyncio.get_event_loop().time()),
            "components": {}
        }
        
        if self.initialized:
            try:
                # Check Redis connection
                await self.redis_client.ping()
                status["components"]["redis"] = "healthy"
            except Exception as e:
                status["components"]["redis"] = f"error: {str(e)}"
            
            # Check secrets manager
            if self.secrets_manager:
                key_count = await self.secrets_manager.get_key_count()
                status["components"]["secrets_manager"] = {
                    "status": "healthy",
                    "key_count": key_count
                }
            
            # Check RBAC manager
            if self.rbac_manager:
                status["components"]["rbac_manager"] = "healthy"
            
            # Check security auditor
            if self.security_auditor:
                # Get recent security metrics
                metrics = await self.security_auditor.get_security_metrics(24)
                status["components"]["security_auditor"] = {
                    "status": "healthy",
                    "recent_events": metrics.get("total_events", 0),
                    "recent_alerts": metrics.get("recent_alerts", 0)
                }
        
        return status

# Global security manager instance
_security_manager: Optional[SecurityManager] = None

def get_security_manager() -> Optional[SecurityManager]:
    """Get global security manager instance"""
    return _security_manager

async def init_security_system(
    redis_url: str = "redis://localhost:6379",
    jwt_secret: Optional[str] = None,
    config_overrides: Optional[Dict[str, Any]] = None
) -> SecurityManager:
    """Initialize global security system"""
    global _security_manager
    
    _security_manager = SecurityManager()
    success = await _security_manager.initialize(redis_url, jwt_secret, config_overrides)
    
    if not success:
        raise RuntimeError("Failed to initialize security system")
    
    logger.info("Global security system initialized")
    return _security_manager

async def shutdown_security_system():
    """Shutdown global security system"""
    global _security_manager
    
    if _security_manager:
        await _security_manager.shutdown()
        _security_manager = None
    
    logger.info("Global security system shutdown")

@asynccontextmanager
async def security_lifespan(app: FastAPI):
    """FastAPI lifespan context manager for security system"""
    
    # Startup
    try:
        security_manager = await init_security_system()
        security_manager.configure_fastapi_security(app)
        
        # Run initial security tests in background
        asyncio.create_task(log_security_test_results(app, security_manager))
        
        yield
        
    finally:
        # Shutdown
        await shutdown_security_system()

async def log_security_test_results(app: FastAPI, security_manager: SecurityManager):
    """Run security tests and log results"""
    try:
        # Wait a bit for app to be fully initialized
        await asyncio.sleep(5)
        
        logger.info("Running initial security tests")
        results = await security_manager.run_security_tests(app)
        
        logger.info("Security test results",
                   total_tests=results["test_summary"]["total_tests"],
                   passed=results["test_summary"]["passed_tests"],
                   security_score=results["test_summary"]["security_score"],
                   security_level=results["test_summary"]["security_level"])
        
        # Log any critical findings
        if results["risk_assessment"]["CRITICAL"] > 0:
            logger.critical("CRITICAL security issues found",
                          critical_issues=results["risk_assessment"]["CRITICAL"])
        
        if results["risk_assessment"]["HIGH"] > 0:
            logger.error("HIGH risk security issues found", 
                        high_risk_issues=results["risk_assessment"]["HIGH"])
        
    except Exception as e:
        logger.error("Failed to run security tests", error=str(e))

# Demo functions for testing security system
async def demo_security_system():
    """Demonstration of security system functionality"""
    
    logger.info("=== Security System Demo ===")
    
    try:
        # Initialize security system
        security_manager = await init_security_system()
        
        # Get security status
        status = await security_manager.get_security_status()
        logger.info("Security system status", status=status)
        
        # Test secrets management
        if security_manager.secrets_manager:
            await security_manager.secrets_manager.set_secret("demo_secret", "demo_value")
            secret_value = await security_manager.secrets_manager.get_secret("demo_secret")
            logger.info("Secrets management test", retrieved_value=secret_value)
        
        # Test RBAC system
        if security_manager.rbac_manager:
            from app.security.rbac import Role, Permission, UserPermissions
            
            # Create test user permissions
            test_permissions = UserPermissions(
                user_id="demo_user",
                organization_id="demo_org"
            )
            test_permissions.roles.add(Role.OPERATOR.value)
            test_permissions.permissions.add(Permission.VEHICLE_READ)
            
            # Store and retrieve permissions
            await security_manager.rbac_manager.store_user_permissions(test_permissions)
            retrieved_permissions = await security_manager.rbac_manager.get_user_permissions("demo_user")
            
            logger.info("RBAC system test", 
                       user_id=retrieved_permissions.user_id if retrieved_permissions else None,
                       roles=list(retrieved_permissions.roles) if retrieved_permissions else None)
        
        # Test security auditor
        if security_manager.security_auditor:
            from app.security.audit import SecurityEvent, SecurityEventType, SecurityEventSeverity
            
            # Create test security event
            test_event = SecurityEvent(
                event_id="demo_event",
                event_type=SecurityEventType.LOGIN_SUCCESS,
                severity=SecurityEventSeverity.INFO,
                timestamp=asyncio.get_event_loop().time(),
                user_id="demo_user",
                message="Demo security event"
            )
            
            # Log event
            success = await security_manager.security_auditor.log_security_event(test_event)
            logger.info("Security audit test", event_logged=success)
            
            # Get security metrics
            metrics = await security_manager.security_auditor.get_security_metrics(1)
            logger.info("Security metrics", metrics=metrics)
        
        logger.info("Security system demo completed successfully")
        
    except Exception as e:
        logger.error("Security system demo failed", error=str(e))
    
    finally:
        await shutdown_security_system()

if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_security_system())