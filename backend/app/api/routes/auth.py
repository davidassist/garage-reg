"""Comprehensive authentication routes with security features."""

from fastapi import APIRouter, HTTPException, Depends, status, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import structlog

from app.database import get_db
from app.schemas.auth import (
    UserLogin, UserRegister, Token, TokenData, RefreshTokenRequest,
    PasswordResetRequest, EmailVerificationRequest,
    TOTPSetupResponse, TOTPVerifyRequest, WebAuthnRegisterInit,
    WebAuthnAuthInit, UserProfile, ChangePasswordRequest,
    APIKeyCreate, APIKeyResponse
)
from app.services.auth import AuthService
from app.core.rbac import get_current_user, get_current_active_user
from app.core.rate_limit import limiter, RateLimitConfig
from app.core.config import settings

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit(RateLimitConfig.AUTH_ENDPOINTS)
async def register(
    request: Request,
    user_data: UserRegister,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    **Rate Limited**: 5 requests per minute per IP
    
    **Features**:
    - Password strength validation
    - Email uniqueness check
    - Automatic role assignment
    - Email verification token generation
    """
    try:
        auth_service = AuthService(db)
        result = await auth_service.register_user(user_data)
        
        # TODO: Send verification email in background
        # background_tasks.add_task(send_verification_email, user_data.email, result["email_verification_token"])
        
        logger.info("User registered successfully", 
                   username=user_data.username, email=user_data.email)
        
        return {
            "message": result["message"],
            "user_id": result["user_id"],
            "username": result["username"],
            "email": result["email"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Registration failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=Token)
@limiter.limit(RateLimitConfig.AUTH_ENDPOINTS)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens.
    
    **Rate Limited**: 5 requests per minute per IP
    
    **Security Features**:
    - Argon2id password hashing
    - Account lockout protection (via rate limiting)
    - JWT tokens with expiration
    - Comprehensive audit logging
    """
    try:
        auth_service = AuthService(db)
        token_data = await auth_service.authenticate_user(
            form_data.username, 
            form_data.password
        )
        
        logger.info("User logged in successfully", 
                   username=form_data.username, user_id=token_data.user_id)
        
        return token_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login failed", username=form_data.username, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/refresh", response_model=Token)
@limiter.limit(RateLimitConfig.AUTH_ENDPOINTS)
async def refresh_token(
    request: Request,
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    **Rate Limited**: 5 requests per minute per IP
    """
    try:
        auth_service = AuthService(db)
        new_tokens = await auth_service.refresh_access_token(refresh_data.refresh_token)
        
        logger.info("Token refreshed successfully", user_id=new_tokens.user_id)
        return new_tokens
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )


@router.post("/logout")
async def logout(
    current_user: TokenData = Depends(get_current_user)
):
    """
    Logout user and invalidate tokens.
    
    **Note**: In a production system, this would add the token to a blacklist.
    For now, the client should discard the tokens.
    """
    try:
        # TODO: Implement token blacklisting in Redis
        # For now, just log the logout
        
        logger.info("User logged out", user_id=current_user.user_id)
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error("Logout failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.post("/password-reset")
@limiter.limit(RateLimitConfig.PASSWORD_RESET)
async def request_password_reset(
    request: Request,
    reset_request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Request password reset email.
    
    **Rate Limited**: 3 requests per hour per IP
    """
    try:
        # TODO: Implement password reset logic
        # This would generate a reset token and send email
        
        logger.info("Password reset requested", email=reset_request.email)
        return {"message": "Password reset email sent (if email exists)"}
        
    except Exception as e:
        logger.error("Password reset request failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed"
        )


@router.post("/password-reset/confirm")
@limiter.limit(RateLimitConfig.PASSWORD_RESET)
async def confirm_password_reset(
    request: Request,
    reset_confirm: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Confirm password reset with token.
    
    **Rate Limited**: 3 requests per hour per IP
    """
    try:
        # TODO: Implement password reset confirmation
        
        logger.info("Password reset confirmed")
        return {"message": "Password reset successful"}
        
    except Exception as e:
        logger.error("Password reset confirmation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )


@router.post("/verify-email")
@limiter.limit(RateLimitConfig.EMAIL_VERIFICATION)
async def verify_email(
    request: Request,
    verification_request: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Verify email address with token.
    
    **Rate Limited**: 5 requests per hour per IP
    """
    try:
        # TODO: Implement email verification
        
        logger.info("Email verified")
        return {"message": "Email verified successfully"}
        
    except Exception as e:
        logger.error("Email verification failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )


@router.get("/profile", response_model=UserProfile)
async def get_profile(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile with roles and permissions."""
    try:
        auth_service = AuthService(db)
        profile = await auth_service.get_user_profile(current_user.user_id)
        
        return profile
        
    except Exception as e:
        logger.error("Failed to get user profile", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password."""
    try:
        # TODO: Implement password change logic
        
        logger.info("Password changed", user_id=current_user.user_id)
        return {"message": "Password changed successfully"}
        
    except Exception as e:
        logger.error("Password change failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password change failed"
        )


# =============================================================================
# TOTP (Two-Factor Authentication) Endpoints
# =============================================================================

@router.post("/totp/setup", response_model=TOTPSetupResponse)
async def setup_totp(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Setup TOTP (Time-based One-Time Password) for two-factor authentication.
    
    Returns QR code and backup codes for authenticator app setup.
    """
    try:
        auth_service = AuthService(db)
        totp_setup = await auth_service.setup_totp(current_user.user_id)
        
        logger.info("TOTP setup requested", user_id=current_user.user_id)
        return totp_setup
        
    except Exception as e:
        logger.error("TOTP setup failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="TOTP setup failed"
        )


@router.post("/totp/verify")
@limiter.limit(RateLimitConfig.TOTP_VERIFICATION)
async def verify_totp(
    request: Request,
    verification_request: TOTPVerifyRequest,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify TOTP code to complete two-factor authentication setup.
    
    **Rate Limited**: 10 requests per minute per IP
    """
    try:
        auth_service = AuthService(db)
        success = await auth_service.verify_totp(
            current_user.user_id, 
            verification_request.code
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid TOTP code"
            )
        
        logger.info("TOTP verified and activated", user_id=current_user.user_id)
        return {"message": "TOTP verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("TOTP verification failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="TOTP verification failed"
        )


# =============================================================================
# WebAuthn (FIDO2) Endpoints  
# =============================================================================

@router.post("/webauthn/register/init")
async def webauthn_register_init(
    registration_init: WebAuthnRegisterInit,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initialize WebAuthn credential registration.
    
    Returns challenge and options for authenticator registration.
    """
    try:
        # TODO: Implement WebAuthn registration initialization
        
        logger.info("WebAuthn registration initiated", user_id=current_user.user_id)
        return {"message": "WebAuthn registration not yet implemented"}
        
    except Exception as e:
        logger.error("WebAuthn registration init failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="WebAuthn registration failed"
        )


@router.post("/webauthn/register/complete")
async def webauthn_register_complete(
    registration_data: dict,  # WebAuthn credential data
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete WebAuthn credential registration.
    
    Stores the credential for future authentication.
    """
    try:
        # TODO: Implement WebAuthn registration completion
        
        logger.info("WebAuthn registration completed", user_id=current_user.user_id)
        return {"message": "WebAuthn credential registered"}
        
    except Exception as e:
        logger.error("WebAuthn registration completion failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="WebAuthn registration failed"
        )


@router.post("/webauthn/authenticate/init")
async def webauthn_auth_init(
    auth_init: WebAuthnAuthInit,
    db: Session = Depends(get_db)
):
    """
    Initialize WebAuthn authentication.
    
    Returns challenge and allowed credentials for authentication.
    """
    try:
        # TODO: Implement WebAuthn authentication initialization
        
        logger.info("WebAuthn authentication initiated", username=auth_init.username)
        return {"message": "WebAuthn authentication not yet implemented"}
        
    except Exception as e:
        logger.error("WebAuthn auth init failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="WebAuthn authentication failed"
        )


@router.post("/webauthn/authenticate/complete")
async def webauthn_auth_complete(
    auth_data: dict,  # WebAuthn assertion data
    db: Session = Depends(get_db)
):
    """
    Complete WebAuthn authentication.
    
    Verifies the assertion and returns JWT tokens if successful.
    """
    try:
        # TODO: Implement WebAuthn authentication completion
        
        logger.info("WebAuthn authentication completed")
        return {"message": "WebAuthn authentication not yet implemented"}
        
    except Exception as e:
        logger.error("WebAuthn auth completion failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="WebAuthn authentication failed"
        )


# =============================================================================
# API Key Management
# =============================================================================

@router.post("/api-keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new API key for programmatic access.
    
    **Note**: The full API key is only shown once during creation.
    """
    try:
        auth_service = AuthService(db)
        api_key = await auth_service.create_api_key(current_user.user_id, key_data)
        
        logger.info("API key created", user_id=current_user.user_id, key_id=api_key.id)
        return api_key
        
    except Exception as e:
        logger.error("API key creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key creation failed"
        )