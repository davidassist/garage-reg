"""Pytest configuration and fixtures for all tests."""

import pytest
import asyncio
from datetime import datetime
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi import FastAPI

from app.main import app
from app.database import get_db
from app.models import Base
from app.models.auth import User, Role, Permission
from app.models.organization import Organization
from app.models.organization import Client, Site, Building, Gate
from app.core.security import hash_password, create_access_token
from app.core.config import settings


# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_labels.db"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def setup_test_db():
    """Create test database tables."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session(setup_test_db) -> Session:
    """Provide a database session for testing."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        # Clean up after each test
        session.rollback()
        session.close()


@pytest.fixture
async def client() -> AsyncClient:
    """Provide an async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_org_id(db_session: Session) -> int:
    """Create a test organization and return its ID."""
    org = Organization(
        name="Test Organization",
        slug="test-org",
        email="test@example.com",
        plan="pro",
        is_active=True
    )
    db_session.add(org)
    db_session.commit()
    return org.id


@pytest.fixture
def test_admin_user(db_session: Session, test_org_id: int) -> User:
    """Create a test admin user."""
    # Create admin role if it doesn't exist
    admin_role = db_session.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        admin_role = Role(
            name="admin",
            display_name="Administrator",
            description="System administrator"
        )
        db_session.add(admin_role)
        db_session.commit()
    
    user = User(
        email="admin@test.com",
        username="testadmin",
        first_name="Test",
        last_name="Admin",
        hashed_password=hash_password("testpassword123"),
        is_active=True,
        is_verified=True,
        org_id=test_org_id,
        role_id=admin_role.id
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_client_user(db_session: Session, test_org_id: int) -> User:
    """Create a test client user."""
    # Create client role if it doesn't exist
    client_role = db_session.query(Role).filter(Role.name == "client").first()
    if not client_role:
        client_role = Role(
            name="client",
            display_name="Client User",
            description="Client user with limited access"
        )
        db_session.add(client_role)
        db_session.commit()
    
    user = User(
        email="client@test.com",
        username="testclient",
        first_name="Test",
        last_name="Client",
        hashed_password=hash_password("clientpassword123"),
        is_active=True,
        is_verified=True,
        org_id=test_org_id,
        role_id=client_role.id
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def admin_token(test_admin_user: User) -> str:
    """Create an access token for the admin user."""
    return create_access_token(subject=str(test_admin_user.id))


@pytest.fixture
def client_token(test_client_user: User) -> str:
    """Create an access token for the client user."""
    return create_access_token(subject=str(test_client_user.id))


@pytest.fixture
def test_client_id(db_session: Session, test_org_id: int) -> int:
    """Create a test client and return its ID."""
    client = Client(
        org_id=test_org_id,
        name="Test Client",
        client_code="TC001",
        contact_person="John Doe",
        email="john@testclient.com",
        phone="+1234567890",
        address="123 Test Street",
        is_active=True
    )
    db_session.add(client)
    db_session.commit()
    return client.id


@pytest.fixture
def test_site_id(db_session: Session, test_org_id: int, test_client_id: int) -> int:
    """Create a test site and return its ID."""
    site = Site(
        org_id=test_org_id,
        client_id=test_client_id,
        name="Test Site",
        site_code="TS001",
        address="456 Test Avenue",
        city="Test City",
        country="Test Country",
        is_active=True
    )
    db_session.add(site)
    db_session.commit()
    return site.id


@pytest.fixture
def test_building_id(db_session: Session, test_org_id: int, test_site_id: int) -> int:
    """Create a test building and return its ID."""
    building = Building(
        org_id=test_org_id,
        site_id=test_site_id,
        name="Test Building",
        building_code="TB001",
        floor_count=5,
        is_active=True
    )
    db_session.add(building)
    db_session.commit()
    return building.id


@pytest.fixture
def test_gate_id(db_session: Session, test_org_id: int, test_building_id: int) -> int:
    """Create a test gate and return its ID."""
    gate = Gate(
        org_id=test_org_id,
        building_id=test_building_id,
        name="Test Gate",
        gate_code="TG001",
        gate_type="swing",
        manufacturer="Test Manufacturer",
        model="Test Model",
        serial_number="SN123456789",
        status="operational",
        token_version=1
    )
    db_session.add(gate)
    db_session.commit()
    return gate.id


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()