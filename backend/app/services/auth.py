"""Authentication service with comprehensive security features."""

import secrets
import pyotp
import qrcode
import io
import base64
from typing import Optional, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
import structlog

from app.models.auth import User, Role, Permission, RoleAssignment, TOTPSecret, APIKey
from app.schemas.auth import (
    UserRegister, Token, TokenData, TOTPSetupResponse, 
    APIKeyCreate, APIKeyResponse, UserProfile
)
from app.core.security import (
    hash_password, verify_password, create_access_token, 
    create_refresh_token, verify_token, generate_secure_random_string,
    generate_email_verification_token, generate_password_reset_token
)
from app.core.config import settings

logger = structlog.get_logger(__name__)


class AuthService:
    """Comprehensive authentication service."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def register_user(self, user_data: UserRegister) -> dict:
        """
        Register a new user.
        
        Args:
            user_data: User registration data
            
        Returns:
            Registration result with verification token
            
        Raises:
            HTTPException: If registration fails
        """
        # Check if user already exists
        existing_user = self.db.query(User).filter(
            and_(
                User.is_deleted == False,
                (User.email == user_data.email) | (User.username == user_data.username)
            )
        ).first()
        
        if existing_user:
            if existing_user.email == user_data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Create new user
        try:
            hashed_password = hash_password(user_data.password)
            email_token = generate_secure_random_string(32)
            
            user = User(
                username=user_data.username,
                email=user_data.email,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                password_hash=hashed_password,
                organization_id=user_data.organization_id,
                org_id=user_data.organization_id,  # For tenant filtering
                email_verification_token=email_token,
                email_verified=False,
                is_active=True
            )
            
            self.db.add(user)
            self.db.flush()  # Get user ID
            
            # Assign default role (client role)
            await self._assign_default_role(user.id, user_data.organization_id)
            
            self.db.commit()
            
            # Generate email verification token
            verification_token = generate_email_verification_token(user.email)
            
            logger.info("User registered successfully", 
                       user_id=user.id, username=user.username, email=user.email)
            
            return {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "email_verification_token": verification_token,
                "message": "Registration successful. Please verify your email."
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error("User registration failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed"
            )
    
    async def authenticate_user(self, username: str, password: str) -> Token:
        """
        Authenticate user and return JWT tokens.
        
        Args:
            username: Username or email
            password: Plain text password
            
        Returns:
            JWT tokens and user info
            
        Raises:
            HTTPException: If authentication fails
        """
        # Find user by username or email
        user = self.db.query(User).filter(
            and_(
                User.is_deleted == False,
                User.is_active == True,
                (User.username == username) | (User.email == username)
            )
        ).first()
        
        if not user or not verify_password(password, user.password_hash):
            logger.warning("Authentication failed", username=username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        if not user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not verified"
            )
        
        # Check for account lockout (if implemented)
        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        # Get user permissions
        permissions = await self._get_user_permissions(user.id)
        
        # Create tokens
        access_token = create_access_token(
            subject=user.id,
            additional_claims={
                "username": user.username,
                "org_id": user.org_id,
                "permissions": permissions
            }
        )
        
        refresh_token = create_refresh_token(subject=user.id)
        
        logger.info("User authenticated successfully", 
                   user_id=user.id, username=user.username)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=user.id,
            permissions=permissions
        )
    
    async def refresh_access_token(self, refresh_token: str) -> Token:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access and refresh tokens
            
        Raises:
            HTTPException: If refresh fails
        """
        # Verify refresh token
        payload = verify_token(refresh_token, token_type="refresh")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get user
        user = self.db.query(User).filter(
            and_(User.id == user_id, User.is_deleted == False, User.is_active == True)
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Get user permissions
        permissions = await self._get_user_permissions(user.id)
        
        # Create new tokens
        new_access_token = create_access_token(
            subject=user.id,
            additional_claims={
                "username": user.username,
                "org_id": user.org_id,
                "permissions": permissions
            }
        )
        
        new_refresh_token = create_refresh_token(subject=user.id)
        
        logger.info("Token refreshed successfully", user_id=user.id)
        
        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=user.id,
            permissions=permissions
        )
    
    async def setup_totp(self, user_id: int) -> TOTPSetupResponse:
        """
        Setup TOTP (Time-based One-Time Password) for user.
        
        Args:
            user_id: User ID
            
        Returns:
            TOTP setup information
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Generate secret
        secret = pyotp.random_base32()
        
        # Create TOTP
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name=settings.WEBAUTHN_RP_NAME
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        
        qr_code_b64 = base64.b64encode(buf.getvalue()).decode()
        qr_code_url = f"data:image/png;base64,{qr_code_b64}"
        
        # Generate backup codes
        backup_codes = [generate_secure_random_string(8) for _ in range(10)]
        
        # Store TOTP secret (not verified yet)
        existing_totp = self.db.query(TOTPSecret).filter(
            TOTPSecret.user_id == user_id
        ).first()
        
        if existing_totp:
            existing_totp.secret = secret
            existing_totp.is_verified = False
            existing_totp.backup_codes = backup_codes
        else:
            totp_secret = TOTPSecret(
                user_id=user_id,
                org_id=user.org_id,
                secret=secret,
                is_verified=False,
                backup_codes=backup_codes
            )
            self.db.add(totp_secret)
        
        self.db.commit()
        
        logger.info("TOTP setup initiated", user_id=user_id)
        
        return TOTPSetupResponse(
            secret=secret,
            qr_code_url=qr_code_url,
            backup_codes=backup_codes
        )
    
    async def verify_totp(self, user_id: int, code: str) -> bool:
        """
        Verify TOTP code and activate 2FA.
        
        Args:
            user_id: User ID
            code: TOTP code
            
        Returns:
            True if verification successful
        """
        totp_secret = self.db.query(TOTPSecret).filter(
            TOTPSecret.user_id == user_id
        ).first()
        
        if not totp_secret:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="TOTP not set up"
            )
        
        # Verify TOTP code
        totp = pyotp.TOTP(totp_secret.secret)
        if not totp.verify(code, valid_window=2):  # Allow 2 windows for clock drift
            logger.warning("TOTP verification failed", user_id=user_id)
            return False
        
        # Mark as verified
        totp_secret.is_verified = True
        totp_secret.is_active = True
        self.db.commit()
        
        logger.info("TOTP verified and activated", user_id=user_id)
        return True
    
    async def create_api_key(self, user_id: int, key_data: APIKeyCreate) -> APIKeyResponse:
        """
        Create API key for user.
        
        Args:
            user_id: User ID
            key_data: API key creation data
            
        Returns:
            Created API key information
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Generate API key
        api_key = generate_secure_random_string(40)
        key_prefix = api_key[:8]
        key_hash = hash_password(api_key)
        
        # Calculate expiration
        expires_at = None
        if key_data.expires_days:
            expires_at = datetime.utcnow() + timedelta(days=key_data.expires_days)
        
        # Create API key record
        db_key = APIKey(
            user_id=user_id,
            org_id=user.org_id,
            name=key_data.name,
            description=key_data.description,
            key_prefix=key_prefix,
            key_hash=key_hash,
            expires_at=expires_at,
            is_active=True
        )
        
        self.db.add(db_key)
        self.db.commit()
        
        logger.info("API key created", user_id=user_id, key_id=db_key.id)
        
        return APIKeyResponse(
            id=db_key.id,
            name=db_key.name,
            key_prefix=key_prefix,
            api_key=f"gr_{api_key}",  # Only show full key on creation
            created_at=db_key.created_at,
            expires_at=db_key.expires_at,
            last_used_at=db_key.last_used_at,
            is_active=db_key.is_active
        )
    
    async def get_user_profile(self, user_id: int) -> UserProfile:
        """Get user profile with roles and permissions."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        roles = await self._get_user_roles(user_id)
        permissions = await self._get_user_permissions(user_id)
        
        return UserProfile(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            display_name=user.display_name,
            email_verified=user.email_verified,
            is_active=user.is_active,
            last_login=user.last_login,
            created_at=user.created_at,
            organization_id=user.organization_id,
            roles=roles,
            permissions=permissions
        )
    
    async def _assign_default_role(self, user_id: int, org_id: int):
        """Assign default role to new user."""
        # Find default "client" role
        default_role = self.db.query(Role).filter(
            Role.name == "client"
        ).first()
        
        if default_role:
            role_assignment = RoleAssignment(
                user_id=user_id,
                role_id=default_role.id,
                org_id=org_id,
                scope_type="organization",
                scope_id=org_id,
                is_active=True
            )
            self.db.add(role_assignment)
    
    async def _get_user_roles(self, user_id: int) -> List[dict]:
        """Get user roles."""
        roles = self.db.query(Role).join(
            RoleAssignment, RoleAssignment.role_id == Role.id
        ).filter(
            and_(
                RoleAssignment.user_id == user_id,
                RoleAssignment.is_active == True,
                RoleAssignment.is_deleted == False
            )
        ).all()
        
        return [
            {
                "id": role.id,
                "name": role.name,
                "description": role.description
            }
            for role in roles
        ]
    
    async def _get_user_permissions(self, user_id: int) -> List[dict]:
        """Get user permissions through roles."""
        permissions = self.db.query(Permission).join(
            Role.permissions
        ).join(
            RoleAssignment, RoleAssignment.role_id == Role.id
        ).filter(
            and_(
                RoleAssignment.user_id == user_id,
                RoleAssignment.is_active == True,
                RoleAssignment.is_deleted == False
            )
        ).distinct().all()
        
        return [
            {
                "id": perm.id,
                "name": perm.name,
                "codename": perm.codename,
                "resource": perm.resource,
                "action": perm.action
            }
            for perm in permissions
        ]