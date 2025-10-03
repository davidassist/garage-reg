"""
Input Validation and Sanitization Module
Comprehensive input validation following OWASP guidelines
"""

import re
import html
import bleach
import validators
from typing import Any, Dict, List, Optional, Union, Type
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from pydantic import BaseModel, validator, Field
from pydantic.validators import str_validator
import structlog

logger = structlog.get_logger(__name__)

class SecurityValidationError(Exception):
    """Custom exception for security validation failures"""
    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.message = message
        self.value = value
        super().__init__(f"Security validation failed for {field}: {message}")

class InputValidator:
    """Comprehensive input validation and sanitization"""
    
    # Regular expressions for validation
    PATTERNS = {
        "email": re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"),
        "phone": re.compile(r"^\+?[\d\s\-\(\)]{10,20}$"),
        "vin": re.compile(r"^[A-HJ-NPR-Z0-9]{17}$"),
        "license_plate": re.compile(r"^[A-Z0-9\-\s]{2,10}$"),
        "username": re.compile(r"^[a-zA-Z0-9_]{3,30}$"),
        "slug": re.compile(r"^[a-z0-9\-_]{1,50}$"),
        "uuid": re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"),
        "color_hex": re.compile(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"),
    }
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        re.compile(pattern, re.IGNORECASE) for pattern in [
            r"\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b",
            r"[\'\"];\s*(union|select|insert|update|delete)",
            r"\b(or|and)\s+\d+\s*=\s*\d+",
            r"[\'\"].*[\'\"]",
            r"\-\-",
            r"/\*.*\*/",
        ]
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        re.compile(pattern, re.IGNORECASE) for pattern in [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*=",
            r"onmouseover\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
        ]
    ]
    
    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        re.compile(pattern) for pattern in [
            r"\.\./",
            r"\.\.\\",
            r"%2e%2e%2f",
            r"%2e%2e\\",
            r"~",
        ]
    ]
    
    @classmethod
    def sanitize_string(cls, value: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            raise SecurityValidationError("string", "Input must be a string", value)
        
        # Check length
        if len(value) > max_length:
            raise SecurityValidationError("string", f"Input exceeds maximum length of {max_length}", len(value))
        
        # Check for SQL injection
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if pattern.search(value):
                logger.warning("SQL injection attempt detected", input=value[:100])
                raise SecurityValidationError("string", "Potential SQL injection detected", value)
        
        # Check for XSS
        for pattern in cls.XSS_PATTERNS:
            if pattern.search(value):
                logger.warning("XSS attempt detected", input=value[:100])
                raise SecurityValidationError("string", "Potential XSS detected", value)
        
        # Check for path traversal
        for pattern in cls.PATH_TRAVERSAL_PATTERNS:
            if pattern.search(value):
                logger.warning("Path traversal attempt detected", input=value[:100])
                raise SecurityValidationError("string", "Path traversal attempt detected", value)
        
        # HTML sanitization
        sanitized = html.escape(value)
        
        # Clean with bleach for additional safety
        sanitized = bleach.clean(sanitized, tags=[], attributes={}, strip=True)
        
        return sanitized.strip()
    
    @classmethod
    def validate_email(cls, email: str) -> str:
        """Validate and sanitize email address"""
        email = cls.sanitize_string(email, 255).lower()
        
        if not cls.PATTERNS["email"].match(email):
            raise SecurityValidationError("email", "Invalid email format", email)
        
        if not validators.email(email):
            raise SecurityValidationError("email", "Invalid email address", email)
        
        return email
    
    @classmethod
    def validate_phone(cls, phone: str) -> str:
        """Validate and sanitize phone number"""
        phone = cls.sanitize_string(phone, 20)
        
        if not cls.PATTERNS["phone"].match(phone):
            raise SecurityValidationError("phone", "Invalid phone format", phone)
        
        return phone
    
    @classmethod
    def validate_vin(cls, vin: str) -> str:
        """Validate Vehicle Identification Number"""
        vin = cls.sanitize_string(vin, 17).upper()
        
        if not cls.PATTERNS["vin"].match(vin):
            raise SecurityValidationError("vin", "Invalid VIN format", vin)
        
        # Additional VIN checksum validation could be added here
        return vin
    
    @classmethod
    def validate_license_plate(cls, plate: str) -> str:
        """Validate license plate number"""
        plate = cls.sanitize_string(plate, 10).upper()
        
        if not cls.PATTERNS["license_plate"].match(plate):
            raise SecurityValidationError("license_plate", "Invalid license plate format", plate)
        
        return plate
    
    @classmethod
    def validate_username(cls, username: str) -> str:
        """Validate username"""
        username = cls.sanitize_string(username, 30).lower()
        
        if not cls.PATTERNS["username"].match(username):
            raise SecurityValidationError("username", "Username must be 3-30 characters, alphanumeric and underscore only", username)
        
        # Check against reserved usernames
        reserved = ["admin", "root", "administrator", "system", "api", "null", "undefined"]
        if username in reserved:
            raise SecurityValidationError("username", "Username is reserved", username)
        
        return username
    
    @classmethod
    def validate_password(cls, password: str) -> str:
        """Validate password strength"""
        if not isinstance(password, str):
            raise SecurityValidationError("password", "Password must be a string")
        
        # Length check
        if len(password) < 8:
            raise SecurityValidationError("password", "Password must be at least 8 characters long")
        
        if len(password) > 128:
            raise SecurityValidationError("password", "Password is too long (max 128 characters)")
        
        # Complexity requirements
        has_lower = bool(re.search(r"[a-z]", password))
        has_upper = bool(re.search(r"[A-Z]", password))
        has_digit = bool(re.search(r"\d", password))
        has_special = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))
        
        complexity_score = sum([has_lower, has_upper, has_digit, has_special])
        
        if complexity_score < 3:
            raise SecurityValidationError(
                "password", 
                "Password must contain at least 3 of: lowercase, uppercase, digits, special characters"
            )
        
        # Check for common patterns
        common_patterns = [
            r"123456", r"password", r"qwerty", r"admin", r"letmein",
            r"(.)\1{3,}",  # Repeated characters
            r"(012|123|234|345|456|567|678|789|890)",  # Sequential numbers
            r"(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)",  # Sequential letters
        ]
        
        for pattern in common_patterns:
            if re.search(pattern, password.lower()):
                raise SecurityValidationError("password", "Password contains common patterns or sequences")
        
        return password
    
    @classmethod
    def validate_integer(cls, value: Any, min_val: int = None, max_val: int = None) -> int:
        """Validate integer input"""
        try:
            if isinstance(value, str):
                # Remove any non-digit characters except minus
                cleaned = re.sub(r"[^\d\-]", "", value)
                if not cleaned or cleaned == "-":
                    raise ValueError("Invalid integer")
                value = int(cleaned)
            elif not isinstance(value, int):
                value = int(value)
        except (ValueError, TypeError):
            raise SecurityValidationError("integer", "Invalid integer format", value)
        
        if min_val is not None and value < min_val:
            raise SecurityValidationError("integer", f"Value must be at least {min_val}", value)
        
        if max_val is not None and value > max_val:
            raise SecurityValidationError("integer", f"Value must be at most {max_val}", value)
        
        return value
    
    @classmethod
    def validate_decimal(cls, value: Any, max_digits: int = 10, decimal_places: int = 2) -> Decimal:
        """Validate decimal input"""
        try:
            if isinstance(value, str):
                # Remove non-numeric characters except decimal point and minus
                cleaned = re.sub(r"[^\d\.\-]", "", value)
                value = Decimal(cleaned)
            elif not isinstance(value, Decimal):
                value = Decimal(str(value))
        except (ValueError, TypeError, InvalidOperation):
            raise SecurityValidationError("decimal", "Invalid decimal format", value)
        
        # Check precision
        sign, digits, exponent = value.as_tuple()
        if len(digits) > max_digits:
            raise SecurityValidationError("decimal", f"Too many digits (max {max_digits})", value)
        
        if exponent < -decimal_places:
            raise SecurityValidationError("decimal", f"Too many decimal places (max {decimal_places})", value)
        
        return value
    
    @classmethod
    def validate_url(cls, url: str) -> str:
        """Validate URL"""
        url = cls.sanitize_string(url, 2048)
        
        if not validators.url(url):
            raise SecurityValidationError("url", "Invalid URL format", url)
        
        # Check for allowed schemes
        allowed_schemes = ["http", "https"]
        if not any(url.startswith(f"{scheme}://") for scheme in allowed_schemes):
            raise SecurityValidationError("url", "URL must use http or https protocol", url)
        
        return url
    
    @classmethod
    def validate_json_depth(cls, data: Any, max_depth: int = 10) -> Any:
        """Validate JSON depth to prevent recursive attacks"""
        def check_depth(obj, current_depth=0):
            if current_depth > max_depth:
                raise SecurityValidationError("json", f"JSON depth exceeds maximum of {max_depth}")
            
            if isinstance(obj, dict):
                for value in obj.values():
                    check_depth(value, current_depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    check_depth(item, current_depth + 1)
        
        check_depth(data)
        return data

# Custom Pydantic validators
def secure_string_validator(max_length: int = 1000):
    """Create a secure string validator for Pydantic"""
    def validator_func(v):
        if v is None:
            return v
        return InputValidator.sanitize_string(v, max_length)
    return validator_func

def secure_email_validator(v):
    """Secure email validator for Pydantic"""
    if v is None:
        return v
    return InputValidator.validate_email(v)

def secure_password_validator(v):
    """Secure password validator for Pydantic"""
    if v is None:
        return v
    return InputValidator.validate_password(v)

# Base models with built-in validation
class SecureBaseModel(BaseModel):
    """Base model with security validations"""
    
    class Config:
        # Prevent extra fields
        extra = "forbid"
        # Validate on assignment
        validate_assignment = True
        # Use enum values
        use_enum_values = True
        # Strict validation
        anystr_strip_whitespace = True
        max_anystr_length = 1000

class SecureUserInput(SecureBaseModel):
    """Secure user input validation"""
    
    email: Optional[str] = Field(None, validator=secure_email_validator)
    password: Optional[str] = Field(None, validator=secure_password_validator)
    full_name: Optional[str] = Field(None, max_length=100, validator=secure_string_validator(100))
    phone: Optional[str] = Field(None, max_length=20)
    
    @validator("phone")
    def validate_phone_format(cls, v):
        if v is None:
            return v
        return InputValidator.validate_phone(v)

class SecureVehicleInput(SecureBaseModel):
    """Secure vehicle input validation"""
    
    make: str = Field(..., max_length=50, validator=secure_string_validator(50))
    model: str = Field(..., max_length=50, validator=secure_string_validator(50))
    year: int = Field(..., ge=1900, le=2030)
    vin: Optional[str] = Field(None, max_length=17)
    license_plate: Optional[str] = Field(None, max_length=10)
    color: Optional[str] = Field(None, max_length=30, validator=secure_string_validator(30))
    mileage: Optional[int] = Field(None, ge=0, le=9999999)
    
    @validator("vin")
    def validate_vin_format(cls, v):
        if v is None:
            return v
        return InputValidator.validate_vin(v)
    
    @validator("license_plate") 
    def validate_plate_format(cls, v):
        if v is None:
            return v
        return InputValidator.validate_license_plate(v)

class FileUploadValidator:
    """File upload security validation"""
    
    ALLOWED_EXTENSIONS = {
        "image": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
        "document": [".pdf", ".doc", ".docx", ".txt"],
        "spreadsheet": [".xls", ".xlsx", ".csv"],
    }
    
    MIME_TYPES = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg", 
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".pdf": "application/pdf",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".txt": "text/plain",
        ".xls": "application/vnd.ms-excel",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".csv": "text/csv",
    }
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @classmethod
    def validate_filename(cls, filename: str) -> str:
        """Validate and sanitize filename"""
        if not filename:
            raise SecurityValidationError("filename", "Filename cannot be empty")
        
        # Sanitize filename
        filename = InputValidator.sanitize_string(filename, 255)
        
        # Remove path components
        filename = filename.split("/")[-1].split("\\")[-1]
        
        # Check for dangerous patterns
        dangerous_patterns = ["../", "..\\", "~", "$", "`", "|", "&", ";"]
        for pattern in dangerous_patterns:
            if pattern in filename:
                raise SecurityValidationError("filename", f"Filename contains dangerous pattern: {pattern}")
        
        # Validate extension
        extension = "." + filename.lower().split(".")[-1] if "." in filename else ""
        if extension not in cls.MIME_TYPES:
            raise SecurityValidationError("filename", f"File type not allowed: {extension}")
        
        return filename
    
    @classmethod
    def validate_file_content(cls, content: bytes, filename: str) -> bytes:
        """Validate file content"""
        # Check file size
        if len(content) > cls.MAX_FILE_SIZE:
            raise SecurityValidationError("file_size", f"File too large (max {cls.MAX_FILE_SIZE} bytes)")
        
        # Check file signature (magic bytes)
        extension = "." + filename.lower().split(".")[-1]
        if not cls._validate_file_signature(content, extension):
            raise SecurityValidationError("file_content", "File content doesn't match extension")
        
        return content
    
    @classmethod
    def _validate_file_signature(cls, content: bytes, extension: str) -> bool:
        """Validate file signature matches extension"""
        if len(content) < 10:
            return False
        
        signatures = {
            ".jpg": [b"\xff\xd8\xff"],
            ".jpeg": [b"\xff\xd8\xff"],
            ".png": [b"\x89PNG\r\n\x1a\n"],
            ".gif": [b"GIF87a", b"GIF89a"],
            ".pdf": [b"%PDF-"],
            ".doc": [b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"],
            ".docx": [b"PK\x03\x04"],
            ".xls": [b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"],
            ".xlsx": [b"PK\x03\x04"],
        }
        
        if extension not in signatures:
            return True  # Allow unknown extensions to pass through
        
        return any(content.startswith(sig) for sig in signatures[extension])