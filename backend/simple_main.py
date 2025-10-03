"""
Simple FastAPI application for error handling demo
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ValidationError
import structlog

# Create structured logger
logger = structlog.get_logger(__name__)

# Import our error models
from app.core.error_models import (
    ErrorResponse, 
    FieldError, 
    APIException, 
    ValidationException,
    NotFoundError,
    ConflictError,
    api_exception_handler,
    validation_exception_handler,
    http_exception_handler
)

# Import test error endpoints
from app.api.test_errors import router as test_router

# Create FastAPI app
app = FastAPI(
    title="GarageReg Error Handling Demo",
    description="Demonstration of consistent API error models and handling",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register error handlers
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

# Include test routes
app.include_router(test_router, prefix="/api/test", tags=["error-testing"])

@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "message": "GarageReg Error Handling Demo API",
        "version": "1.0.0",
        "endpoints": {
            "test_errors": "/api/test/",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "garagereg-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)