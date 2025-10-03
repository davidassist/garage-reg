"""Simplified application configuration."""

from functools import lru_cache
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    APP_NAME: str = Field(default="GarageReg API")
    APP_VERSION: str = Field(default="1.0.0")
    APP_DESCRIPTION: str = Field(default="Garage Registration and Management System")
    APP_ENV: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    LOG_LEVEL: str = Field(default="DEBUG")
    LOG_FORMAT: str = Field(default="text")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return not self.DEBUG
    
    # Server
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    
    # API
    API_V1_STR: str = Field(default="/api/v1")
    DOCS_URL: Optional[str] = Field(default="/docs")
    REDOC_URL: Optional[str] = Field(default="/redoc")
    OPENAPI_URL: Optional[str] = Field(default="/openapi.json")
    
    # Security
    # JWT settings
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", alias="JWT_SECRET_KEY")
    JWT_SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15)
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    
    # Argon2 settings (from engineering handbook)
    ARGON2_MEMORY_COST: int = Field(default=65536, description="64 MiB")
    ARGON2_TIME_COST: int = Field(default=3, description="3 iterations")
    ARGON2_PARALLELISM: int = Field(default=4, description="4 threads")
    ARGON2_HASH_LENGTH: int = Field(default=32, description="32 bytes output")
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True)
    RATE_LIMIT_CALLS: int = Field(default=100)
    RATE_LIMIT_PERIOD: int = Field(default=60)
    
    # Email settings
    EMAIL_ENABLED: bool = Field(default=False)
    SMTP_HOST: Optional[str] = Field(default=None)
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: Optional[str] = Field(default=None)
    SMTP_PASSWORD: Optional[str] = Field(default=None)
    EMAIL_FROM: str = Field(default="noreply@garagereg.com")
    
    # WebAuthn settings
    WEBAUTHN_RP_ID: str = Field(default="localhost")
    WEBAUTHN_RP_NAME: str = Field(default="GarageReg")
    WEBAUTHN_ORIGIN: str = Field(default="http://localhost:3000")
    
    # CORS
    CORS_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:8080")
    
    # Frontend URL for QR/NFC links
    FRONTEND_URL: Optional[str] = Field(default="http://localhost:3000")
    
    # Database
    DATABASE_URL: str = Field(default="sqlite:///./garagereg.db")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, description="AWS Access Key ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, description="AWS Secret Access Key")
    AWS_REGION: str = Field(default="us-east-1", description="AWS Region")
    S3_PHOTOS_BUCKET: str = Field(default="garagereg-inspection-photos", description="S3 bucket for inspection photos")
    
    # Environment detection
    @property
    def ENVIRONMENT(self) -> str:
        """Get current environment."""
        return "production" if not self.DEBUG else "development"


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


settings = get_settings()