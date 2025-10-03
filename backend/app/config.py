"""Configuration management for GarageReg API."""

from functools import lru_cache
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Application settings
    app_name: str = Field(default="GarageReg", description="Application name")
    app_env: str = Field(default="development", description="Application environment")
    app_debug: bool = Field(default=False, description="Debug mode")
    app_url: str = Field(default="http://localhost", description="Application URL")
    
    # API settings
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_prefix: str = Field(default="/api/v1", description="API prefix")
    
    # Database settings
    database_url: str = Field(
        default="postgresql://garagereg:garagereg_dev_password@localhost:5432/garagereg",
        description="Database URL"
    )
    async_database_url: Optional[str] = Field(
        default=None,
        description="Async database URL"
    )
    
    # Redis settings
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis URL"
    )
    
    # Celery settings
    celery_broker_url: Optional[str] = Field(default=None, description="Celery broker URL")
    celery_result_backend: Optional[str] = Field(default=None, description="Celery result backend")
    
    # JWT settings
    jwt_secret_key: str = Field(
        default="your-super-secret-jwt-key-change-this",
        description="JWT secret key"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_access_token_expire_minutes: int = Field(
        default=15,
        description="JWT access token expiration in minutes"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7,
        description="JWT refresh token expiration in days"
    )
    
    # Security settings
    argon2_memory_cost: int = Field(default=65536, description="Argon2 memory cost")
    argon2_time_cost: int = Field(default=3, description="Argon2 time cost")
    argon2_parallelism: int = Field(default=4, description="Argon2 parallelism")
    argon2_hash_length: int = Field(default=32, description="Argon2 hash length")
    
    csrf_secret_key: str = Field(
        default="your-csrf-secret-key-change-this",
        description="CSRF secret key"
    )
    
    # CORS settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        description="CORS allowed origins"
    )
    
    # Trusted hosts (for production)
    allowed_hosts: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        description="Allowed hosts"
    )
    
    # S3/MinIO settings
    s3_endpoint: str = Field(
        default="http://localhost:9000",
        description="S3 endpoint"
    )
    s3_access_key: str = Field(default="minioadmin", description="S3 access key")
    s3_secret_key: str = Field(default="minioadmin", description="S3 secret key")
    s3_bucket: str = Field(default="garagereg", description="S3 bucket name")
    s3_secure: bool = Field(default=False, description="Use HTTPS for S3")
    
    # Email settings
    smtp_host: str = Field(default="localhost", description="SMTP host")
    smtp_port: int = Field(default=1025, description="SMTP port")
    smtp_user: str = Field(default="", description="SMTP username")
    smtp_password: str = Field(default="", description="SMTP password")
    smtp_tls: bool = Field(default=False, description="Use TLS for SMTP")
    smtp_ssl: bool = Field(default=False, description="Use SSL for SMTP")
    
    email_from: str = Field(
        default="noreply@garagereg.local",
        description="Default email from address"
    )
    email_from_name: str = Field(
        default="GarageReg System",
        description="Default email from name"
    )
    
    # Monitoring and logging
    log_level: str = Field(default="INFO", description="Log level")
    log_format: str = Field(default="json", description="Log format")
    
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN")
    sentry_traces_sample_rate: float = Field(
        default=0.1,
        description="Sentry traces sample rate"
    )
    
    # Documentation
    docs_enabled: bool = Field(default=True, description="Enable API documentation")
    redoc_enabled: bool = Field(default=True, description="Enable ReDoc documentation")
    
    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_storage_url: Optional[str] = Field(
        default=None,
        description="Rate limit storage URL"
    )
    
    @validator("async_database_url", always=True)
    def set_async_database_url(cls, v, values):
        """Set async database URL based on database URL if not provided."""
        if v is None:
            db_url = values.get("database_url", "")
            if db_url.startswith("postgresql://"):
                return db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v
    
    @validator("celery_broker_url", always=True)
    def set_celery_broker_url(cls, v, values):
        """Set Celery broker URL based on Redis URL if not provided."""
        return v or values.get("redis_url")
    
    @validator("celery_result_backend", always=True)
    def set_celery_result_backend(cls, v, values):
        """Set Celery result backend based on Redis URL if not provided."""
        return v or values.get("redis_url")
    
    @validator("rate_limit_storage_url", always=True)
    def set_rate_limit_storage_url(cls, v, values):
        """Set rate limit storage URL based on Redis URL if not provided."""
        return v or values.get("redis_url")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()