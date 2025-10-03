"""Health check routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import time
import psutil
import structlog
import asyncio

from app.database import get_db
from app.core.config import get_settings

router = APIRouter()
logger = structlog.get_logger(__name__)
settings = get_settings()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "garagereg-api",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "timestamp": int(time.time()),
    }


async def check_database_health(db: Session) -> Dict[str, Any]:
    """Check database health."""
    try:
        # Test basic connection
        db.execute("SELECT 1")
        
        # Test application tables (when they exist)
        # For now, just test the health_check table from init script
        result = db.execute("SELECT status FROM health_check ORDER BY last_check DESC LIMIT 1")
        row = result.fetchone()
        
        return {
            "status": "healthy",
            "error": None,
            "last_check_status": row[0] if row else "unknown",
            "connection_pool": "active"
        }
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return {
            "status": "unhealthy", 
            "error": str(e),
            "connection_pool": "failed"
        }


async def check_redis_health() -> Dict[str, Any]:
    """Check Redis health."""
    try:
        import redis.asyncio as redis
        
        # Create Redis client
        redis_client = redis.from_url(settings.REDIS_URL)
        
        # Test connection
        await redis_client.ping()
        
        # Get info
        info = await redis_client.info()
        
        await redis_client.close()
        
        return {
            "status": "healthy",
            "error": None,
            "version": info.get("redis_version", "unknown"),
            "memory_used": info.get("used_memory_human", "unknown"),
            "connected_clients": info.get("connected_clients", 0)
        }
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with system and service information."""
    start_time = time.time()
    
    # Run health checks
    db_health = await check_database_health(db)
    redis_health = await check_redis_health()
    
    # Get system metrics
    try:
        cpu_usage = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        system_health = {
            "status": "healthy",
            "cpu_usage_percent": round(cpu_usage, 2),
            "memory_usage_percent": round(memory.percent, 2),
            "memory_available_mb": round(memory.available / (1024**2), 2),
            "disk_usage_percent": round(disk.percent, 2),
            "disk_free_gb": round(disk.free / (1024**3), 2),
        }
    except Exception as e:
        logger.error("System health check failed", error=str(e))
        system_health = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Determine overall status
    checks = {
        "database": db_health,
        "redis": redis_health,
        "system": system_health
    }
    
    overall_status = "healthy"
    if any(check["status"] == "unhealthy" for check in checks.values()):
        overall_status = "unhealthy"
    elif any(check["status"] == "degraded" for check in checks.values()):
        overall_status = "degraded"
    
    check_duration = round((time.time() - start_time) * 1000, 2)  # ms
    
    response = {
        "status": overall_status,
        "service": "garagereg-api", 
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "timestamp": int(time.time()),
        "check_duration_ms": check_duration,
        "checks": checks
    }
    
    # Log health check result
    logger.info(
        "Health check completed",
        status=overall_status,
        duration_ms=check_duration,
        database_status=db_health["status"],
        redis_status=redis_health["status"]
    )
    
    return response


@router.get("/health/live")
async def liveness_probe():
    """Liveness probe for Kubernetes."""
    return {
        "status": "alive",
        "service": "garagereg-api",
        "timestamp": int(time.time())
    }


@router.get("/health/ready")
async def readiness_probe(db: Session = Depends(get_db)):
    """Readiness probe for Kubernetes."""
    try:
        # Quick database check
        db.execute("SELECT 1")
        
        # Quick Redis check (if available)
        try:
            import redis.asyncio as redis
            redis_client = redis.from_url(settings.REDIS_URL)
            await redis_client.ping()
            await redis_client.close()
        except Exception:
            # Redis not critical for readiness in this simple check
            pass
        
        return {
            "status": "ready",
            "service": "garagereg-api",
            "timestamp": int(time.time())
        }
    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "error": str(e),
                "timestamp": int(time.time())
            }
        )