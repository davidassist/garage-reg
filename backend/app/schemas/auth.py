"""Authentication schemas."""

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime


class UserLogin(BaseModel):
    """User login request schema."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    remember_me: bool = Field(default=False)


class UserRegister(BaseModel):
    """User registration request schema."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    organization_id: int
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserResponse(BaseModel):
    """User registration response schema."""
    user_id: int
    username: str
    email: str
    first_name: str
    last_name: str
    organization_id: int
    message: str
    permissions: List[str] = []


class UserProfileResponse(BaseModel):
    """User profile response schema."""
    user_id: int
    username: str
    email: str
    first_name: str
    last_name: str
    organization_id: int
    permissions: List[str] = []


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int


class TokenData(BaseModel):
    """Token payload data."""
    user_id: int
    username: str
    email: str
    org_id: int
    permissions: List[str] = []
    exp: Optional[datetime] = None


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str


class EmailVerificationRequest(BaseModel):
    """Email verification request schema."""
    email: EmailStr


class PasswordResetRequest(BaseModel):
    """Password reset request schema."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class TOTPSetupResponse(BaseModel):
    """TOTP setup response schema."""
    secret: str
    qr_code_url: str
    backup_codes: List[str]


class TOTPVerifyRequest(BaseModel):
    """TOTP verification request schema."""
    code: str = Field(..., min_length=6, max_length=6)


class WebAuthnRegisterInit(BaseModel):
    """WebAuthn registration initialization request."""
    username: str = Field(..., min_length=3, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)


class WebAuthnRegisterComplete(BaseModel):
    """WebAuthn registration completion request."""
    credential: dict
    username: str


class WebAuthnAuthInit(BaseModel):
    """WebAuthn authentication initialization request."""
    username: str = Field(..., min_length=3, max_length=50)


class WebAuthnAuthComplete(BaseModel):
    """WebAuthn authentication completion request."""
    credential: dict
    username: str


class RoleInfo(BaseModel):
    """Role information schema."""
    id: int
    name: str
    description: str


class PermissionInfo(BaseModel):
    """Permission information schema."""
    id: int
    name: str
    codename: str
    resource: str
    action: str


class UserProfile(BaseModel):
    """User profile response schema."""
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    display_name: Optional[str]
    email_verified: bool
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime
    organization_id: int
    roles: List[RoleInfo] = []
    permissions: List[PermissionInfo] = []


class ChangePasswordRequest(BaseModel):
    """Change password request schema."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class APIKeyCreate(BaseModel):
    """API key creation request schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    expires_days: Optional[int] = Field(None, ge=1, le=365)


class APIKeyResponse(BaseModel):
    """API key response schema."""
    id: int
    name: str
    key_prefix: str
    api_key: Optional[str] = None  # Only shown during creation
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None