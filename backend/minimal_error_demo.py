"""
Ultra-minimal FastAPI error demo without complex dependencies
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional, Any
from datetime import datetime
import json

# Simple error models (inline)
class FieldError(BaseModel):
    field: str
    message: str
    code: str
    value: Optional[Any] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: bool = True
    code: str
    message: str
    details: Optional[str] = None
    field_errors: Optional[List[FieldError]] = None
    path: Optional[str] = None
    method: Optional[str] = None
    timestamp: Optional[str] = None

# Error codes
class ErrorCodes:
    VALIDATION_ERROR = "VALIDATION_ERROR"
    REQUIRED_FIELD_MISSING = "REQUIRED_FIELD_MISSING"
    INVALID_INPUT = "INVALID_INPUT"
    INVALID_FORMAT = "INVALID_FORMAT"

# Test models
class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, description="Username (3-20 chars)")
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$', description="Valid email")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")
    age: int = Field(..., ge=13, le=120, description="Age (13-120)")

class ValidationTestModel(BaseModel):
    required_string: str = Field(..., description="Required field")
    positive_number: int = Field(..., gt=0, description="Must be positive")
    email_field: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$', description="Valid email")

# Create app
app = FastAPI(title="Error Handling Demo", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_error_response(request: Request, status_code: int, message: str, code: str, 
                         details: str = None, field_errors: List[FieldError] = None) -> ErrorResponse:
    return ErrorResponse(
        code=code,
        message=message,
        details=details,
        field_errors=field_errors,
        path=str(request.url.path),
        method=request.method,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )

def convert_validation_errors(validation_error: RequestValidationError) -> List[FieldError]:
    field_errors = []
    for error in validation_error.errors():
        field_path = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        if not field_path:
            field_path = "root"
        
        error_type = error["type"]
        code = ErrorCodes.VALIDATION_ERROR
        if "missing" in error_type:
            code = ErrorCodes.REQUIRED_FIELD_MISSING
        elif "value_error" in error_type:
            code = ErrorCodes.INVALID_INPUT
        elif "type_error" in error_type:
            code = ErrorCodes.INVALID_FORMAT
        
        field_error = FieldError(
            field=field_path,
            message=error["msg"],
            code=code,
            value=error.get("input")
        )
        field_errors.append(field_error)
    
    return field_errors

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    field_errors = convert_validation_errors(exc)
    error_response = create_error_response(
        request=request,
        status_code=400,
        message="Validation failed",
        code=ErrorCodes.VALIDATION_ERROR,
        details=f"Request validation failed with {len(field_errors)} field errors",
        field_errors=field_errors
    )
    return JSONResponse(status_code=400, content=error_response.model_dump(exclude_none=True))

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    error_response = create_error_response(
        request=request,
        status_code=exc.status_code,
        message=str(exc.detail),
        code="HTTP_ERROR"
    )
    return JSONResponse(status_code=exc.status_code, content=error_response.model_dump(exclude_none=True))

# Routes
@app.get("/")
async def root():
    return {
        "message": "Error Handling Demo API",
        "endpoints": {
            "test_validation": "POST /test/validation/user",
            "test_complex": "POST /test/validation/complex",
            "test_not_found": "GET /test/not-found",
            "test_server_error": "GET /test/server-error"
        }
    }

@app.post("/test/validation/user")
async def test_user_validation(user: UserCreateRequest):
    """Test user creation with validation errors."""
    # Simulate username conflict
    if user.username.lower() in ["admin", "test", "user"]:
        raise HTTPException(status_code=409, detail=f"Username '{user.username}' is already taken")
    
    return {"message": f"User '{user.username}' created successfully", "user": user.model_dump()}

@app.post("/test/validation/complex")
async def test_complex_validation(data: ValidationTestModel):
    """Test complex validation with multiple field errors."""
    return {"message": "Validation passed", "data": data.model_dump()}

@app.get("/test/not-found")
async def test_not_found():
    """Test 404 error."""
    raise HTTPException(status_code=404, detail="This resource does not exist")

@app.get("/test/server-error")
async def test_server_error():
    """Test 500 error."""
    raise HTTPException(status_code=500, detail="Internal server error occurred")

if __name__ == "__main__":
    import uvicorn
    print("Starting Error Handling Demo Server...")
    print("Visit http://127.0.0.1:8002/docs for interactive API documentation")
    uvicorn.run(app, host="127.0.0.1", port=8002)