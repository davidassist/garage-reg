"""
Secrets Management System
Implements 12-Factor App methodology for secure secrets handling
"""

import os
import json
import base64
import secrets
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import redis.asyncio as redis
import structlog

logger = structlog.get_logger(__name__)

class SecretsManager:
    """Centralized secrets management with encryption and rotation"""
    
    def __init__(self, redis_client: redis.Redis, master_key: Optional[str] = None):
        self.redis = redis_client
        self.master_key = master_key or os.getenv("SECRETS_MASTER_KEY")
        if not self.master_key:
            raise ValueError("Master key required for secrets encryption")
        
        self.fernet = self._create_fernet_key()
        self.rotation_schedule: Dict[str, int] = {}  # days until rotation
    
    def _create_fernet_key(self) -> Fernet:
        """Create Fernet encryption key from master key"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'garagereg_salt_2024',  # Use a consistent salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        return Fernet(key)
    
    async def store_secret(
        self, 
        key: str, 
        value: Union[str, Dict[str, Any]], 
        ttl: Optional[int] = None,
        rotation_days: Optional[int] = None
    ) -> bool:
        """Store encrypted secret in Redis"""
        try:
            # Prepare secret data
            secret_data = {
                "value": value,
                "created_at": datetime.utcnow().isoformat(),
                "version": 1,
                "metadata": {
                    "rotation_days": rotation_days,
                    "last_accessed": None,
                    "access_count": 0
                }
            }
            
            # Encrypt the secret
            encrypted_data = self.fernet.encrypt(json.dumps(secret_data).encode())
            
            # Store in Redis
            redis_key = f"secret:{key}"
            await self.redis.set(redis_key, encrypted_data, ex=ttl)
            
            # Schedule rotation if specified
            if rotation_days:
                self.rotation_schedule[key] = rotation_days
                await self._schedule_rotation(key, rotation_days)
            
            logger.info("Secret stored successfully", key=key, ttl=ttl)
            return True
            
        except Exception as e:
            logger.error("Failed to store secret", key=key, error=str(e))
            return False
    
    async def get_secret(self, key: str) -> Optional[Union[str, Dict[str, Any]]]:
        """Retrieve and decrypt secret from Redis"""
        try:
            redis_key = f"secret:{key}"
            encrypted_data = await self.redis.get(redis_key)
            
            if not encrypted_data:
                logger.warning("Secret not found", key=key)
                return None
            
            # Decrypt the secret
            decrypted_data = self.fernet.decrypt(encrypted_data)
            secret_data = json.loads(decrypted_data.decode())
            
            # Update access metadata
            secret_data["metadata"]["last_accessed"] = datetime.utcnow().isoformat()
            secret_data["metadata"]["access_count"] += 1
            
            # Re-encrypt and store updated metadata
            updated_encrypted = self.fernet.encrypt(json.dumps(secret_data).encode())
            await self.redis.set(redis_key, updated_encrypted, keepttl=True)
            
            logger.info("Secret accessed successfully", key=key)
            return secret_data["value"]
            
        except Exception as e:
            logger.error("Failed to retrieve secret", key=key, error=str(e))
            return None
    
    async def delete_secret(self, key: str) -> bool:
        """Securely delete a secret"""
        try:
            redis_key = f"secret:{key}"
            result = await self.redis.delete(redis_key)
            
            # Remove from rotation schedule
            if key in self.rotation_schedule:
                del self.rotation_schedule[key]
                await self._unschedule_rotation(key)
            
            logger.info("Secret deleted successfully", key=key)
            return bool(result)
            
        except Exception as e:
            logger.error("Failed to delete secret", key=key, error=str(e))
            return False
    
    async def rotate_secret(self, key: str, new_value: Union[str, Dict[str, Any]]) -> bool:
        """Rotate a secret with versioning"""
        try:
            # Get current secret
            current_secret = await self.get_secret(key)
            if not current_secret:
                logger.warning("Cannot rotate non-existent secret", key=key)
                return False
            
            # Store old version
            old_version_key = f"{key}_old_v{int(datetime.utcnow().timestamp())}"
            await self.store_secret(old_version_key, current_secret, ttl=86400)  # Keep old version for 24h
            
            # Store new version
            rotation_days = self.rotation_schedule.get(key)
            success = await self.store_secret(key, new_value, rotation_days=rotation_days)
            
            if success:
                logger.info("Secret rotated successfully", key=key)
                await self._notify_rotation(key)
            
            return success
            
        except Exception as e:
            logger.error("Failed to rotate secret", key=key, error=str(e))
            return False
    
    async def list_secrets(self, pattern: str = "secret:*") -> List[str]:
        """List all secret keys matching pattern"""
        try:
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                # Remove prefix and decode
                clean_key = key.decode().replace("secret:", "")
                if not clean_key.endswith("_old_v"):  # Exclude old versions
                    keys.append(clean_key)
            
            return sorted(keys)
            
        except Exception as e:
            logger.error("Failed to list secrets", error=str(e))
            return []
    
    async def get_secret_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Get secret metadata without exposing the value"""
        try:
            redis_key = f"secret:{key}"
            encrypted_data = await self.redis.get(redis_key)
            
            if not encrypted_data:
                return None
            
            decrypted_data = self.fernet.decrypt(encrypted_data)
            secret_data = json.loads(decrypted_data.decode())
            
            # Return metadata without the actual value
            return {
                "created_at": secret_data["created_at"],
                "version": secret_data["version"],
                "metadata": secret_data["metadata"],
                "key": key
            }
            
        except Exception as e:
            logger.error("Failed to get secret metadata", key=key, error=str(e))
            return None
    
    async def _schedule_rotation(self, key: str, rotation_days: int):
        """Schedule automatic secret rotation"""
        rotation_time = datetime.utcnow() + timedelta(days=rotation_days)
        rotation_key = f"rotation:{key}"
        
        await self.redis.setex(
            rotation_key,
            rotation_days * 86400,  # Convert days to seconds
            rotation_time.isoformat()
        )
    
    async def _unschedule_rotation(self, key: str):
        """Remove rotation schedule for a key"""
        rotation_key = f"rotation:{key}"
        await self.redis.delete(rotation_key)
    
    async def _notify_rotation(self, key: str):
        """Notify about secret rotation (implement your notification logic)"""
        logger.info("Secret rotation notification", key=key, timestamp=datetime.utcnow().isoformat())
        # Implement notification to security team, Slack, etc.
    
    async def check_rotations_due(self) -> List[str]:
        """Check for secrets that need rotation"""
        due_rotations = []
        
        try:
            # Scan for rotation schedules
            async for rotation_key in self.redis.scan_iter(match="rotation:*"):
                key = rotation_key.decode().replace("rotation:", "")
                
                # Check if rotation is due
                rotation_time_str = await self.redis.get(rotation_key)
                if rotation_time_str:
                    rotation_time = datetime.fromisoformat(rotation_time_str.decode())
                    if datetime.utcnow() >= rotation_time:
                        due_rotations.append(key)
            
            if due_rotations:
                logger.warning("Secrets require rotation", keys=due_rotations)
            
            return due_rotations
            
        except Exception as e:
            logger.error("Failed to check rotation schedule", error=str(e))
            return []

class EnvironmentSecretsLoader:
    """Load secrets from environment variables following 12-Factor methodology"""
    
    REQUIRED_SECRETS = [
        "DATABASE_URL",
        "REDIS_URL", 
        "SECRET_KEY",
        "JWT_ALGORITHM",
    ]
    
    OPTIONAL_SECRETS = [
        "SMTP_PASSWORD",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "STRIPE_SECRET_KEY",
        "GITHUB_TOKEN",
    ]
    
    @classmethod
    def load_secrets(cls) -> Dict[str, Any]:
        """Load all secrets from environment"""
        secrets_dict = {}
        missing_required = []
        
        # Load required secrets
        for secret_name in cls.REQUIRED_SECRETS:
            value = os.getenv(secret_name)
            if value:
                secrets_dict[secret_name] = value
            else:
                missing_required.append(secret_name)
        
        # Load optional secrets
        for secret_name in cls.OPTIONAL_SECRETS:
            value = os.getenv(secret_name)
            if value:
                secrets_dict[secret_name] = value
        
        # Validate required secrets
        if missing_required:
            raise ValueError(f"Missing required environment variables: {missing_required}")
        
        logger.info("Environment secrets loaded", 
                   required_count=len(cls.REQUIRED_SECRETS),
                   optional_count=len([s for s in cls.OPTIONAL_SECRETS if s in secrets_dict]))
        
        return secrets_dict
    
    @classmethod
    def validate_secret_format(cls, name: str, value: str) -> bool:
        """Validate secret format requirements"""
        validators = {
            "DATABASE_URL": lambda v: v.startswith(("postgresql://", "mysql://", "sqlite://")),
            "REDIS_URL": lambda v: v.startswith("redis://"),
            "SECRET_KEY": lambda v: len(v) >= 32,
            "JWT_ALGORITHM": lambda v: v in ["HS256", "RS256", "ES256"],
        }
        
        validator = validators.get(name)
        if validator:
            return validator(value)
        
        return True  # No specific validation for this secret

class KeyRotationManager:
    """Automated key rotation management"""
    
    def __init__(self, secrets_manager: SecretsManager):
        self.secrets_manager = secrets_manager
        self.generators = {
            "jwt_secret": self._generate_jwt_secret,
            "api_key": self._generate_api_key,
            "encryption_key": self._generate_encryption_key,
            "csrf_token": self._generate_csrf_token,
        }
    
    async def rotate_key(self, key_type: str, key_name: str) -> bool:
        """Rotate a specific key"""
        generator = self.generators.get(key_type)
        if not generator:
            logger.error("Unknown key type for rotation", key_type=key_type)
            return False
        
        try:
            # Generate new key
            new_key = generator()
            
            # Store new key
            success = await self.secrets_manager.rotate_secret(key_name, new_key)
            
            if success:
                logger.info("Key rotated successfully", key_type=key_type, key_name=key_name)
                await self._notify_key_rotation(key_type, key_name)
            
            return success
            
        except Exception as e:
            logger.error("Key rotation failed", key_type=key_type, key_name=key_name, error=str(e))
            return False
    
    def _generate_jwt_secret(self) -> str:
        """Generate a secure JWT secret"""
        return secrets.token_urlsafe(64)
    
    def _generate_api_key(self) -> str:
        """Generate a secure API key"""
        return f"grgapi_{secrets.token_urlsafe(32)}"
    
    def _generate_encryption_key(self) -> str:
        """Generate a secure encryption key"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    
    def _generate_csrf_token(self) -> str:
        """Generate a CSRF token"""
        return secrets.token_hex(32)
    
    async def _notify_key_rotation(self, key_type: str, key_name: str):
        """Notify about key rotation"""
        logger.info("Key rotation notification", 
                   key_type=key_type, 
                   key_name=key_name, 
                   timestamp=datetime.utcnow().isoformat())
        # Implement notification logic here

class SecretsAuditor:
    """Audit secrets access and management"""
    
    def __init__(self, secrets_manager: SecretsManager):
        self.secrets_manager = secrets_manager
    
    async def audit_secret_access(self) -> Dict[str, Any]:
        """Generate audit report for secret access"""
        secrets_list = await self.secrets_manager.list_secrets()
        audit_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_secrets": len(secrets_list),
            "secrets_analysis": []
        }
        
        for secret_key in secrets_list:
            metadata = await self.secrets_manager.get_secret_metadata(secret_key)
            if metadata:
                # Analyze access patterns
                last_accessed = metadata["metadata"].get("last_accessed")
                access_count = metadata["metadata"].get("access_count", 0)
                created_at = metadata["created_at"]
                
                analysis = {
                    "key": secret_key,
                    "created_at": created_at,
                    "last_accessed": last_accessed,
                    "access_count": access_count,
                    "age_days": (datetime.utcnow() - datetime.fromisoformat(created_at)).days,
                    "is_stale": self._is_secret_stale(last_accessed),
                    "needs_rotation": await self._needs_rotation(secret_key)
                }
                
                audit_report["secrets_analysis"].append(analysis)
        
        return audit_report
    
    def _is_secret_stale(self, last_accessed: Optional[str]) -> bool:
        """Check if secret is stale (not accessed in 30 days)"""
        if not last_accessed:
            return True
        
        last_access_time = datetime.fromisoformat(last_accessed)
        return (datetime.utcnow() - last_access_time).days > 30
    
    async def _needs_rotation(self, key: str) -> bool:
        """Check if secret needs rotation"""
        rotations_due = await self.secrets_manager.check_rotations_due()
        return key in rotations_due

# Global secrets manager instance
_secrets_manager: Optional[SecretsManager] = None

def get_secrets_manager() -> Optional[SecretsManager]:
    """Get global secrets manager instance"""
    return _secrets_manager

def init_secrets_manager(redis_client: redis.Redis, master_key: Optional[str] = None) -> SecretsManager:
    """Initialize global secrets manager"""
    global _secrets_manager
    _secrets_manager = SecretsManager(redis_client, master_key)
    logger.info("Secrets manager initialized")
    return _secrets_manager

# Convenience functions
async def store_secret(key: str, value: Union[str, Dict[str, Any]], **kwargs) -> bool:
    """Store a secret using global manager"""
    manager = get_secrets_manager()
    if not manager:
        raise RuntimeError("Secrets manager not initialized")
    return await manager.store_secret(key, value, **kwargs)

async def get_secret(key: str) -> Optional[Union[str, Dict[str, Any]]]:
    """Get a secret using global manager"""
    manager = get_secrets_manager()
    if not manager:
        raise RuntimeError("Secrets manager not initialized")
    return await manager.get_secret(key)