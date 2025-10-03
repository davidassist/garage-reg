"""Database configuration and connection management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

# Create database engine
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite configuration
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.DEBUG
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error("Database session error", error=str(e))
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    from app.models import Base
    logger.info("Creating database tables")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def drop_tables():
    """Drop all database tables."""
    from app.models import Base
    logger.warning("Dropping all database tables")
    Base.metadata.drop_all(bind=engine)
    logger.warning("All database tables dropped")


def create_tables():
    """Create all tables in the database."""
    logger.info("Creating database tables")
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all tables in the database."""
    logger.warning("Dropping database tables")
    Base.metadata.drop_all(bind=engine)