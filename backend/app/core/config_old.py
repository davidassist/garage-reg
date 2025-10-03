"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import List, Optional
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
    
    # =============================================================================
    # APPLICATION SETTINGS
    # =============================================================================
    APP_NAME: str = Field(default="GarageReg API", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    APP_DESCRIPTION: str = Field(
        default="Garage Gate Management and Maintenance System API",
        description="Application description"
    )
    DEBUG: bool = Field(default=True, description="Debug mode")
    LOG_LEVEL: str = Field(default="DEBUG", description="Logging level")
    
    # =============================================================================
    # SERVER SETTINGS
    # =============================================================================
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    
    # =============================================================================
    # API SETTINGS
    # =============================================================================
    API_V1_STR: str = Field(default="/api/v1", description="API v1 prefix")
    DOCS_URL: Optional[str] = Field(default="/docs", description="Swagger UI URL")
    REDOC_URL: Optional[str] = Field(default="/redoc", description="ReDoc URL")
    
    # =============================================================================
    # SECURITY SETTINGS
    # =============================================================================
    JWT_SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT secret key"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="JWT access token expiration time in minutes"
    )
    
    # =============================================================================
    # CORS SETTINGS
    # =============================================================================
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins"
    )
    
    # =============================================================================
    # DATABASE SETTINGS (Basic for testing)
    # =============================================================================
    DATABASE_URL: str = Field(
        default="sqlite:///./garagereg.db",
        description="Database URL"
    )
    
    # =============================================================================
    # UTILITY PROPERTIES
    # =============================================================================
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.DEBUG
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.DEBUG


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Global settings instance
settings = get_settings()
    
    # =============================================================================
    # SECURITY SETTINGS
    # =============================================================================
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Secret key for session management"
    )
    JWT_SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="JWT signing secret"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=15, 
        description="Access token expiration in minutes"
    )
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7, 
        description="Refresh token expiration in days"
    )
    
    # Password hashing - Argon2id settings
    ARGON2_MEMORY_COST: int = Field(default=65536, description="Argon2 memory cost (64 MiB)")
    ARGON2_TIME_COST: int = Field(default=3, description="Argon2 time cost (iterations)")
    ARGON2_PARALLELISM: int = Field(default=4, description="Argon2 parallelism (threads)")
    ARGON2_HASH_LENGTH: int = Field(default=32, description="Argon2 hash length in bytes")
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = Field(
        default=[
            "http://localhost",
            "http://localhost:3000",
            "http://localhost:3001",
            "http://admin.localhost"
        ],
        description="CORS allowed origins"
    )
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # =============================================================================
    # DATABASE SETTINGS
    # =============================================================================
    DB_HOST: str = Field(default="localhost", description="Database host")
    DB_PORT: int = Field(default=5432, description="Database port")
    DB_NAME: str = Field(default="garagereg", description="Database name")
    DB_USER: str = Field(default="garagereg", description="Database user")
    DB_PASSWORD: str = Field(default="garagereg_dev_password", description="Database password")
    
    DATABASE_URL: Optional[str] = Field(default=None, description="Complete database URL")
    ASYNC_DATABASE_URL: Optional[str] = Field(default=None, description="Async database URL")
    
    @field_validator("DATABASE_URL", mode="before")
    def assemble_database_url(cls, v: Optional[str]) -> str:
        if isinstance(v, str):
            return v
        return (
            f"postgresql://{values.get('DB_USER')}:{values.get('DB_PASSWORD')}"
            f"@{values.get('DB_HOST')}:{values.get('DB_PORT')}/{values.get('DB_NAME')}"
        )
    
    @validator("ASYNC_DATABASE_URL", pre=True)
    def assemble_async_database_url(cls, v: Optional[str], values: dict[str, Any]) -> str:
        if isinstance(v, str):
            return v
        return (
            f"postgresql+asyncpg://{values.get('DB_USER')}:{values.get('DB_PASSWORD')}"
            f"@{values.get('DB_HOST')}:{values.get('DB_PORT')}/{values.get('DB_NAME')}"
        )
    
    # Database pool settings
    DB_POOL_SIZE: int = Field(default=10, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=20, description="Database max overflow connections")
    DB_POOL_PRE_PING: bool = Field(default=True, description="Enable pool pre ping")
    
    # =============================================================================
    # REDIS SETTINGS
    # =============================================================================
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    REDIS_DB: int = Field(default=0, description="Redis database number")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    REDIS_SSL: bool = Field(default=False, description="Use SSL for Redis connection")
    
    REDIS_URL: Optional[str] = Field(default=None, description="Complete Redis URL")
    
    @validator("REDIS_URL", pre=True)
    def assemble_redis_url(cls, v: Optional[str], values: dict[str, Any]) -> str:
        if isinstance(v, str):
            return v
        
        password_part = f":{values.get('REDIS_PASSWORD')}@" if values.get('REDIS_PASSWORD') else ""
        protocol = "rediss" if values.get('REDIS_SSL') else "redis"
        
        return (
            f"{protocol}://{password_part}{values.get('REDIS_HOST')}:"
            f"{values.get('REDIS_PORT')}/{values.get('REDIS_DB')}"
        )
    
    # =============================================================================
    # CELERY SETTINGS
    # =============================================================================
    CELERY_BROKER_URL: Optional[str] = Field(default=None, description="Celery broker URL")
    CELERY_RESULT_BACKEND: Optional[str] = Field(default=None, description="Celery result backend")
    
    @validator("CELERY_BROKER_URL", pre=True)
    def assemble_celery_broker(cls, v: Optional[str], values: dict[str, Any]) -> str:
        return v or values.get("REDIS_URL")
    
    @validator("CELERY_RESULT_BACKEND", pre=True)
    def assemble_celery_result_backend(cls, v: Optional[str], values: dict[str, Any]) -> str:
        return v or values.get("REDIS_URL")
    
    # =============================================================================
    # S3/MINIO SETTINGS
    # =============================================================================
    S3_ENDPOINT: str = Field(default="http://localhost:9000", description="S3 endpoint URL")
    S3_ACCESS_KEY: str = Field(default="minioadmin", description="S3 access key")
    S3_SECRET_KEY: str = Field(default="minioadmin", description="S3 secret key")
    S3_BUCKET: str = Field(default="garagereg", description="S3 bucket name")
    S3_REGION: str = Field(default="us-east-1", description="S3 region")
    S3_USE_SSL: bool = Field(default=False, description="Use SSL for S3 connection")
    S3_CREATE_BUCKET: bool = Field(default=True, description="Auto-create bucket if not exists")
    
    # =============================================================================
    # EMAIL SETTINGS
    # =============================================================================
    SMTP_HOST: str = Field(default="localhost", description="SMTP server host")
    SMTP_PORT: int = Field(default=1025, description="SMTP server port")
    SMTP_USER: Optional[str] = Field(default=None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(default=None, description="SMTP password")
    SMTP_TLS: bool = Field(default=False, description="Use TLS for SMTP")
    SMTP_SSL: bool = Field(default=False, description="Use SSL for SMTP")
    
    EMAIL_FROM: EmailStr = Field(
        default="noreply@garagereg.local", 
        description="Default sender email"
    )
    EMAIL_FROM_NAME: str = Field(
        default="GarageReg System", 
        description="Default sender name"
    )
    EMAIL_TEMPLATES_DIR: str = Field(
        default="app/templates/email", 
        description="Email templates directory"
    )
    
    # =============================================================================
    # RATE LIMITING
    # =============================================================================
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_STORAGE_URL: Optional[str] = Field(
        default=None, 
        description="Rate limit storage URL"
    )
    
    @validator("RATE_LIMIT_STORAGE_URL", pre=True)
    def assemble_rate_limit_storage(cls, v: Optional[str], values: dict[str, Any]) -> str:
        return v or values.get("REDIS_URL")
    
    # Rate limit configurations
    RATE_LIMIT_AUTH_WINDOW: int = Field(default=900, description="Auth rate limit window (seconds)")
    RATE_LIMIT_AUTH_MAX: int = Field(default=5, description="Max auth attempts per window")
    RATE_LIMIT_API_WINDOW: int = Field(default=60, description="API rate limit window (seconds)")
    RATE_LIMIT_API_MAX: int = Field(default=100, description="Max API calls per window")
    RATE_LIMIT_GATE_WINDOW: int = Field(default=60, description="Gate ops rate limit window")
    RATE_LIMIT_GATE_MAX: int = Field(default=10, description="Max gate operations per window")
    
    # =============================================================================
    # MONITORING & OBSERVABILITY
    # =============================================================================
    SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry DSN for error tracking")
    SENTRY_TRACES_SAMPLE_RATE: float = Field(
        default=0.1, 
        description="Sentry traces sample rate"
    )
    SENTRY_PROFILES_SAMPLE_RATE: float = Field(
        default=0.1, 
        description="Sentry profiles sample rate"
    )
    
    # Metrics
    METRICS_ENABLED: bool = Field(default=True, description="Enable Prometheus metrics")
    METRICS_ENDPOINT: str = Field(default="/metrics", description="Metrics endpoint")
    
    # Health checks
    HEALTH_CHECK_TIMEOUT: int = Field(default=30, description="Health check timeout (seconds)")
    
    # =============================================================================
    # DEVELOPMENT & TESTING
    # =============================================================================
    TESTING: bool = Field(default=False, description="Testing mode")
    
    @validator("DOCS_URL", pre=True)
    def validate_docs_url(cls, v: Optional[str], values: dict[str, Any]) -> Optional[str]:
        if values.get("APP_ENV") == "production":
            return None
        return v
    
    @validator("REDOC_URL", pre=True)
    def validate_redoc_url(cls, v: Optional[str], values: dict[str, Any]) -> Optional[str]:
        if values.get("APP_ENV") == "production":
            return None
        return v
    
    # =============================================================================
    # UTILITY PROPERTIES
    # =============================================================================
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.APP_ENV.lower() in ("development", "dev", "local")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.APP_ENV.lower() in ("production", "prod")
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.TESTING or self.APP_ENV.lower() in ("test", "testing")
    
    class Config:
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience function to get settings
settings = get_settings()