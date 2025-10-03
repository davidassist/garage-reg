"""Comprehensive authentication routes with security features."""

from fastapi import APIRouter, HTTPException, Depends, status, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import structlog

from app.database import get_db
from app.schemas.auth import (
    UserLogin, UserRegister, Token, TokenData, RefreshTokenRequest,
    PasswordResetRequest, PasswordResetConfirm, EmailVerificationRequest,
    TOTPSetupResponse, TOTPVerificationRequest, WebAuthnRegistrationInit,
    WebAuthnAuthenticationInit, UserProfile, ChangePasswordRequest,
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


@router.post("/register", response_model=User)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register new user."""
    try:
        user_service = UserService(db)
        
        # Check if user already exists
        if user_service.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        if user_service.get_user_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create new user
        user = user_service.create_user(user_data)
        logger.info("New user registered", username=user.username, email=user.email)
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Registration failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenData,
    db: Session = Depends(get_db)
):
    """Refresh access token."""
    try:
        auth_service = AuthService(db)
        new_token_data = await auth_service.refresh_access_token(token_data.refresh_token)
        
        logger.info("Token refreshed", user_id=new_token_data.get("user_id"))
        return new_token_data
        
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
async def logout(
    token_data: TokenData,
    db: Session = Depends(get_db)
):
    """Logout endpoint to revoke tokens."""
    try:
        auth_service = AuthService(db)
        await auth_service.revoke_token(token_data.access_token)
        
        logger.info("User logged out")
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error("Logout failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )