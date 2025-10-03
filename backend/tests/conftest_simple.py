"""Simple test for labels functionality without complex models."""

import pytest
import asyncio
from datetime import datetime
from httpx import AsyncClient
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import StaticPool
from fastapi import FastAPI

from app.core.config import settings

# Simple test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_labels_simple.db"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Simple test models (minimal without JSONB)
TestBase = declarative_base()

class TestOrganization(TestBase):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    email = Column(String(320), nullable=False)
    plan = Column(String(50), nullable=False, default="free")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class TestGate(TestBase):
    __tablename__ = "gates"
    
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, nullable=False)
    building_id = Column(Integer, nullable=False)
    name = Column(String(200), nullable=False)
    gate_code = Column(String(50))
    gate_type = Column(String(50), nullable=False)
    manufacturer = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100))
    status = Column(String(50), default="operational")
    token_version = Column(Integer, default=1)
    last_token_rotation = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


@pytest.fixture(scope="session")
def setup_simple_test_db():
    """Create simple test database tables."""
    TestBase.metadata.create_all(bind=test_engine)
    yield
    TestBase.metadata.drop_all(bind=test_engine)


@pytest.fixture
def simple_db_session(setup_simple_test_db) -> Session:
    """Provide a simple database session for testing."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        # Clean up after each test
        session.rollback()
        session.close()


@pytest.fixture
def simple_test_org_id(simple_db_session: Session) -> int:
    """Create a simple test organization and return its ID."""
    org = TestOrganization(
        name="Test Organization",
        slug="test-org",
        email="test@example.com",
        plan="pro",
        is_active=True
    )
    simple_db_session.add(org)
    simple_db_session.commit()
    return org.id


@pytest.fixture
def simple_test_gate_id(simple_db_session: Session, simple_test_org_id: int) -> int:
    """Create a simple test gate and return its ID."""
    gate = TestGate(
        org_id=simple_test_org_id,
        building_id=1,
        name="Test Gate",
        gate_code="TG001",
        gate_type="swing",
        manufacturer="Test Manufacturer",
        model="Test Model",
        serial_number="SN123456789",
        status="operational",
        token_version=1
    )
    simple_db_session.add(gate)
    simple_db_session.commit()
    return gate.id


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()