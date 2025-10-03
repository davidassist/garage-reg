"""FastAPI application for GarageReg."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import structlog
import time
import sys
import logging
from typing import Union

from app.core.config import get_settings
from app.core.security import get_cors_origins, get_security_headers
from app.api.main import api_router


# Get settings instance
settings = get_settings()

# Configure structured logging
def configure_logging():
    """Configure structured JSON logging."""
    
    # Configure standard library logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format="%(message)s",
        stream=sys.stdout,
    )
    
    # Configure structlog processors based on format preference
    if settings.LOG_FORMAT.lower() == "json":
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(indent=None if settings.is_production else 2)
        ]
    else:
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer()
        ]
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

# Initialize logging
configure_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info(
        "Starting GarageReg API",
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        debug=settings.DEBUG,
        log_level=settings.LOG_LEVEL
    )
    
    # Initialize services here if needed
    # Example: await initialize_database()
    # Example: await initialize_s3_client()
    
    yield
    
    # Shutdown
    logger.info("Shutting down GarageReg API")
    # Cleanup resources here if needed


# Import error handlers
from app.core.error_models import (
    APIException,
    ValidationException,
    api_exception_handler,
    validation_exception_handler as validation_handler,
    http_exception_handler,
    general_exception_handler
)

# Create FastAPI application
def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOC_URL,
        openapi_url=settings.OPENAPI_URL if settings.DOCS_URL else None,
        lifespan=lifespan,
    )

    # Add standardized error handlers
    app.add_exception_handler(APIException, api_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_origins(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
    )

    # Configure trusted hosts for production
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure this properly in production
        )

    # Add request timing and security headers middleware
    @app.middleware("http")
    async def add_process_time_and_security_headers(request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Add security headers
        security_headers = get_security_headers()
        for header_name, header_value in security_headers.items():
            response.headers[header_name] = header_value
        
        # Log request (only for non-health endpoints to reduce noise)
        if not request.url.path.startswith("/healthz"):
            logger.info(
                "Request processed",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                process_time=round(process_time * 1000, 2),  # Convert to ms
                user_agent=request.headers.get("user-agent", "")[:100],  # Truncate
                remote_addr=request.client.host if request.client else "unknown",
                content_length=response.headers.get("content-length", "0"),
            )
        
        return response

    # Include API routes
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Health check endpoint (without prefix)
    @app.get("/healthz", tags=["Health"], include_in_schema=False)
    async def health_check():
        """Health check endpoint for load balancers and monitoring."""
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "service": "garagereg-api",
                "version": settings.APP_VERSION,
                "environment": settings.APP_ENV,
                "timestamp": int(time.time()),
            }
        )

    # Liveness probe
    @app.get("/health/live", tags=["Health"], include_in_schema=False)
    async def liveness_check():
        """Kubernetes liveness probe."""
        return {"status": "alive", "timestamp": int(time.time())}

    # Readiness probe  
    @app.get("/health/ready", tags=["Health"], include_in_schema=False)
    async def readiness_check():
        """Kubernetes readiness probe."""
        # TODO: Add actual health checks (database, redis, etc.)
        return {"status": "ready", "timestamp": int(time.time())}

    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with basic API information."""
        return {
            "message": settings.APP_NAME,
            "description": settings.APP_DESCRIPTION,
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
            "api_version": settings.API_V1_STR,
            "docs_url": settings.DOCS_URL,
            "health_check": "/healthz",
            "timestamp": int(time.time()),
        }

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD or settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
        workers=1,  # Use 1 worker for development
        access_log=not settings.is_production,  # Disable access log in production (we have our own)
    )