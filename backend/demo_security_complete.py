"""
Security System Integration Demo
Demonstrates the complete security framework implementation
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
import structlog

# Import security components
from app.security import (
    init_security_system, 
    shutdown_security_system,
    get_security_manager,
    security_lifespan
)
from app.security.rbac import (
    Permission, Role, UserPermissions,
    get_current_user_permissions,
    require_permission, 
    require_role
)
from app.security.audit import (
    SecurityEvent, SecurityEventType, SecurityEventSeverity,
    create_security_event_from_request
)

logger = structlog.get_logger(__name__)

# Create FastAPI app with security lifespan
app = FastAPI(
    title="Garage Registration Security Demo",
    description="Demonstrates comprehensive OWASP ASVS L1/L2 security implementation",
    version="1.0.0",
    lifespan=security_lifespan
)

# Security endpoints
@app.get("/security/status")
async def get_security_status():
    """Get current security system status"""
    security_manager = get_security_manager()
    if not security_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Security system not initialized"
        )
    
    status = await security_manager.get_security_status()
    return JSONResponse(content=status)

@app.get("/security/test")
@require_permission(Permission.ADMIN_SYSTEM)
async def run_security_tests(user_permissions: UserPermissions = Depends(get_current_user_permissions)):
    """Run comprehensive security tests (admin only)"""
    security_manager = get_security_manager()
    if not security_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="Security system not initialized"
        )
    
    try:
        results = await security_manager.run_security_tests(app)
        return JSONResponse(content=results)
    except Exception as e:
        logger.error("Security tests failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Security tests failed"
        )

@app.get("/security/metrics")
@require_permission(Permission.ADMIN_AUDIT)
async def get_security_metrics(
    hours: int = 24,
    user_permissions: UserPermissions = Depends(get_current_user_permissions)
):
    """Get security metrics (requires audit permission)"""
    security_manager = get_security_manager()
    if not security_manager or not security_manager.security_auditor:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Security auditor not available"
        )
    
    try:
        metrics = await security_manager.security_auditor.get_security_metrics(hours)
        return JSONResponse(content=metrics)
    except Exception as e:
        logger.error("Failed to get security metrics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve security metrics"
        )

@app.get("/security/events")
@require_permission(Permission.ADMIN_AUDIT)
async def get_security_events(
    limit: int = 100,
    event_type: str = None,
    user_permissions: UserPermissions = Depends(get_current_user_permissions)
):
    """Get recent security events (requires audit permission)"""
    security_manager = get_security_manager()
    if not security_manager or not security_manager.security_auditor:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Security auditor not available"
        )
    
    try:
        # Parse event type filter if provided
        event_types = None
        if event_type:
            try:
                event_types = [SecurityEventType(event_type)]
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid event type: {event_type}"
                )
        
        events = await security_manager.security_auditor.get_security_events(
            limit=limit,
            event_types=event_types
        )
        
        return JSONResponse(content={"events": events, "count": len(events)})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get security events", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve security events"
        )

@app.get("/security/alerts")  
@require_permission(Permission.ADMIN_AUDIT)
async def get_security_alerts(
    limit: int = 50,
    user_permissions: UserPermissions = Depends(get_current_user_permissions)
):
    """Get recent security alerts (requires audit permission)"""
    security_manager = get_security_manager()
    if not security_manager or not security_manager.security_auditor:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Security auditor not available"
        )
    
    try:
        alerts = await security_manager.security_auditor.get_security_alerts(limit)
        return JSONResponse(content={"alerts": alerts, "count": len(alerts)})
        
    except Exception as e:
        logger.error("Failed to get security alerts", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve security alerts"
        )

# Demo authentication endpoints
@app.post("/auth/login")
async def login(request: Request, credentials: Dict[str, str]):
    """Demo login endpoint"""
    security_manager = get_security_manager()
    
    username = credentials.get("username")
    password = credentials.get("password") 
    
    # Create security event
    if security_manager and security_manager.security_auditor:
        event = create_security_event_from_request(
            SecurityEventType.LOGIN_SUCCESS,
            request,
            user_id=username,
            message=f"User login: {username}",
            severity=SecurityEventSeverity.INFO
        )
        await security_manager.security_auditor.log_security_event(event)
    
    # Demo: Create access token (simplified)
    if security_manager and security_manager.rbac_manager:
        # Create demo user permissions
        user_permissions = UserPermissions(
            user_id=username,
            organization_id="demo_org"
        )
        
        # Assign role based on username
        if "admin" in username.lower():
            user_permissions.roles.add(Role.SUPER_ADMIN.value)
        elif "manager" in username.lower():
            user_permissions.roles.add(Role.MANAGER.value)
        else:
            user_permissions.roles.add(Role.OPERATOR.value)
        
        # Get permissions for roles
        all_permissions = security_manager.rbac_manager.auth_matrix.get_user_permissions(user_permissions.roles)
        user_permissions.permissions = all_permissions
        
        # Store permissions
        await security_manager.rbac_manager.store_user_permissions(user_permissions)
        
        # Create token
        token = security_manager.rbac_manager.create_access_token(username, user_permissions)
        
        return JSONResponse(content={
            "access_token": token,
            "token_type": "bearer",
            "user_id": username,
            "roles": list(user_permissions.roles),
            "permissions": [p.value for p in user_permissions.permissions]
        })
    
    return JSONResponse(content={"message": "Login successful (demo mode)"})

@app.get("/auth/me")
async def get_current_user(user_permissions: UserPermissions = Depends(get_current_user_permissions)):
    """Get current user information"""
    return JSONResponse(content={
        "user_id": user_permissions.user_id,
        "organization_id": user_permissions.organization_id,
        "roles": list(user_permissions.roles),
        "permissions": [p.value for p in user_permissions.permissions],
        "expires_at": user_permissions.expires_at.isoformat() if user_permissions.expires_at else None
    })

# Demo protected endpoints
@app.get("/admin/users")
@require_permission(Permission.ADMIN_USERS)
async def get_users(user_permissions: UserPermissions = Depends(get_current_user_permissions)):
    """Admin endpoint - requires user management permission"""
    return JSONResponse(content={
        "message": "Admin users endpoint accessed",
        "accessed_by": user_permissions.user_id,
        "users": ["demo_user1", "demo_user2", "demo_admin"]
    })

@app.get("/vehicles")
@require_permission(Permission.VEHICLE_LIST)
async def get_vehicles(user_permissions: UserPermissions = Depends(get_current_user_permissions)):
    """Vehicle listing endpoint"""
    return JSONResponse(content={
        "message": "Vehicle listing accessed",
        "accessed_by": user_permissions.user_id,
        "vehicles": [
            {"id": 1, "make": "Toyota", "model": "Camry"},
            {"id": 2, "make": "Honda", "model": "Civic"}
        ]
    })

@app.post("/vehicles")
@require_permission(Permission.VEHICLE_CREATE)
async def create_vehicle(
    request: Request,
    vehicle_data: Dict[str, Any],
    user_permissions: UserPermissions = Depends(get_current_user_permissions)
):
    """Create vehicle endpoint"""
    security_manager = get_security_manager()
    
    # Log security event
    if security_manager and security_manager.security_auditor:
        event = create_security_event_from_request(
            SecurityEventType.DATA_CREATE,
            request,
            user_id=user_permissions.user_id,
            message=f"Vehicle created by {user_permissions.user_id}",
            severity=SecurityEventSeverity.INFO,
            additional_details={"resource_type": "vehicle", "data": vehicle_data}
        )
        await security_manager.security_auditor.log_security_event(event)
    
    return JSONResponse(content={
        "message": "Vehicle created successfully",
        "created_by": user_permissions.user_id,
        "vehicle_data": vehicle_data
    })

# Demo input validation endpoint
@app.post("/test/input-validation")
async def test_input_validation(request: Request, data: Dict[str, Any]):
    """Test input validation functionality"""
    security_manager = get_security_manager()
    
    if not security_manager or not security_manager.input_validator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Input validator not available"
        )
    
    try:
        # Test various input validation scenarios
        results = {}
        
        # Test SQL injection detection
        if "username" in data:
            sql_injection_detected = security_manager.input_validator.detect_sql_injection(str(data["username"]))
            results["sql_injection_check"] = {
                "input": data["username"],
                "detected": sql_injection_detected
            }
        
        # Test XSS detection
        if "message" in data:
            xss_detected = security_manager.input_validator.detect_xss(str(data["message"]))
            results["xss_check"] = {
                "input": data["message"],
                "detected": xss_detected
            }
        
        # Test path traversal detection
        if "filepath" in data:
            path_traversal_detected = security_manager.input_validator.detect_path_traversal(str(data["filepath"]))
            results["path_traversal_check"] = {
                "input": data["filepath"],
                "detected": path_traversal_detected
            }
        
        # Log suspicious activity if detected
        if any(check.get("detected") for check in results.values()):
            if security_manager.security_auditor:
                event = create_security_event_from_request(
                    SecurityEventType.SUSPICIOUS_ACTIVITY,
                    request,
                    message="Suspicious input detected in validation test",
                    severity=SecurityEventSeverity.HIGH,
                    additional_details={"validation_results": results, "input_data": data}
                )
                await security_manager.security_auditor.log_security_event(event)
        
        return JSONResponse(content={
            "message": "Input validation test completed",
            "results": results
        })
        
    except Exception as e:
        logger.error("Input validation test failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Input validation test failed"
        )

# Root endpoint with security headers demo
@app.get("/")
async def root():
    """Root endpoint demonstrating security headers"""
    return JSONResponse(content={
        "message": "Garage Registration Security Demo API",
        "version": "1.0.0",
        "security_features": [
            "OWASP ASVS L1/L2 compliance",
            "Comprehensive security headers",
            "Input validation and sanitization", 
            "Role-based access control (RBAC)",
            "Rate limiting and brute force protection",
            "Security event logging and monitoring",
            "Encrypted secrets management",
            "Automated security testing"
        ],
        "endpoints": {
            "/security/status": "Security system status",
            "/security/test": "Run security tests (admin only)",
            "/security/metrics": "Security metrics (audit permission required)",
            "/security/events": "Security events (audit permission required)",
            "/security/alerts": "Security alerts (audit permission required)",
            "/auth/login": "Demo login endpoint",
            "/auth/me": "Current user info",
            "/admin/users": "Admin users (admin permission required)",
            "/vehicles": "Vehicle listing (vehicle read permission required)",
            "/test/input-validation": "Input validation testing"
        }
    })

async def demo_security_complete():
    """Complete security system demonstration"""
    
    logger.info("=== Complete Security System Demo ===")
    
    try:
        # Initialize the security system
        logger.info("Initializing security system...")
        security_manager = await init_security_system()
        
        # Configure FastAPI with security
        logger.info("Configuring FastAPI security...")
        security_manager.configure_fastapi_security(app)
        
        # Get security status
        status = await security_manager.get_security_status()
        logger.info("Security system status", **status)
        
        # Run security tests
        logger.info("Running security tests...")
        test_results = await security_manager.run_security_tests(app)
        
        logger.info("Security test results",
                   total_tests=test_results["test_summary"]["total_tests"],
                   passed=test_results["test_summary"]["passed_tests"],
                   security_score=test_results["test_summary"]["security_score"],
                   security_level=test_results["test_summary"]["security_level"])
        
        # Demonstrate RBAC functionality
        logger.info("Testing RBAC system...")
        if security_manager.rbac_manager:
            # Create test user with different roles
            test_users = [
                {"id": "admin_user", "role": Role.SUPER_ADMIN.value},
                {"id": "manager_user", "role": Role.MANAGER.value},
                {"id": "operator_user", "role": Role.OPERATOR.value}
            ]
            
            for user in test_users:
                user_permissions = UserPermissions(
                    user_id=user["id"],
                    organization_id="demo_org"
                )
                user_permissions.roles.add(user["role"])
                
                # Get permissions for role
                all_permissions = security_manager.rbac_manager.auth_matrix.get_user_permissions(user_permissions.roles)
                user_permissions.permissions = all_permissions
                
                # Store permissions
                await security_manager.rbac_manager.store_user_permissions(user_permissions)
                
                logger.info("User created",
                           user_id=user["id"],
                           role=user["role"], 
                           permission_count=len(user_permissions.permissions))
        
        # Demonstrate security auditing
        logger.info("Testing security auditing...")
        if security_manager.security_auditor:
            # Create sample security events
            from app.security.audit import SecurityEvent
            
            sample_events = [
                SecurityEvent(
                    event_id="demo_login",
                    event_type=SecurityEventType.LOGIN_SUCCESS,
                    severity=SecurityEventSeverity.INFO,
                    timestamp=datetime.utcnow(),
                    user_id="demo_user",
                    source_ip="192.168.1.100",
                    message="Demo login event"
                ),
                SecurityEvent(
                    event_id="demo_access",
                    event_type=SecurityEventType.ACCESS_GRANTED,
                    severity=SecurityEventSeverity.INFO,
                    timestamp=datetime.utcnow(),
                    user_id="demo_user",
                    endpoint="/vehicles",
                    message="Demo access granted event"
                )
            ]
            
            for event in sample_events:
                await security_manager.security_auditor.log_security_event(event)
            
            # Get security metrics
            metrics = await security_manager.security_auditor.get_security_metrics(24)
            logger.info("Security metrics", **metrics)
        
        # Demonstrate secrets management
        logger.info("Testing secrets management...")
        if security_manager.secrets_manager:
            # Store and retrieve demo secrets
            demo_secrets = {
                "api_key": "demo_api_key_12345",
                "db_password": "demo_db_password",
                "webhook_secret": "demo_webhook_secret"
            }
            
            for key, value in demo_secrets.items():
                await security_manager.secrets_manager.set_secret(key, value)
                retrieved = await security_manager.secrets_manager.get_secret(key)
                logger.info("Secret test", key=key, stored_and_retrieved=retrieved == value)
        
        logger.info("=== Security System Demo Completed Successfully ===")
        
        # Generate final compliance report
        compliance_report = {
            "owasp_asvs_level": "L1/L2",
            "security_score": test_results["test_summary"]["security_score"],
            "compliance_status": "COMPLIANT" if test_results["test_summary"]["security_score"] >= 90 else "NON_COMPLIANT",
            "implemented_controls": [
                "Authentication and session management",
                "Role-based access control (RBAC)",
                "Input validation and sanitization",
                "Security headers (Helmet-style)",
                "Rate limiting and brute force protection",
                "SQL injection prevention",
                "XSS protection",
                "CSRF protection",
                "Encrypted secrets management",
                "Security event logging and monitoring",
                "Real-time alerting system",
                "Automated security testing",
                "CORS configuration",
                "Error handling without information disclosure"
            ],
            "security_features": {
                "middleware_stack": "Complete security middleware implementation",
                "input_validation": "Comprehensive validation with threat detection",
                "secrets_management": "12-Factor compliant with encryption and rotation",
                "audit_system": "Real-time security event logging and alerting",
                "rbac_system": "Fine-grained role and permission management",
                "testing_framework": "Automated OWASP ASVS compliance testing"
            }
        }
        
        logger.info("=== OWASP ASVS L1/L2 Compliance Report ===", **compliance_report)
        
        return compliance_report
        
    except Exception as e:
        logger.error("Security system demo failed", error=str(e))
        raise
    
    finally:
        await shutdown_security_system()

if __name__ == "__main__":
    # Run the complete security demonstration
    asyncio.run(demo_security_complete())