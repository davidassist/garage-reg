"""
Test Configuration and Fixtures
Comprehensive test setup for GarageReg backend testing
"""
import asyncio
import os
import tempfile
from typing import AsyncGenerator, Generator
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app.config import get_settings
from app.core.deps import get_current_user
from app.models.user import User
from app.models.organization import Organization
from app.models.client import Client
from app.models.site import Site
from app.models.building import Building


# Test database URL - use in-memory SQLite for speed
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
TEST_SYNC_DATABASE_URL = "sqlite:///:memory:"


# Test settings
@pytest.fixture(scope="session")
def test_settings():
    """Override settings for testing."""
    settings = get_settings()
    settings.database_url = TEST_DATABASE_URL
    settings.testing = True
    settings.secret_key = "test-secret-key-change-in-production"
    return settings


# Database fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for session scope."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_engine():
    """Create async database engine for testing."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
        },
        echo=False
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="session")
def sync_engine():
    """Create sync database engine for testing."""
    engine = create_engine(
        TEST_SYNC_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
        },
        echo=False
    )
    
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async database session for testing."""
    async_session_maker = async_sessionmaker(
        async_engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest.fixture
def sync_session(sync_engine) -> Generator:
    """Create sync database session for testing."""
    Session = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
    session = Session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


# HTTP client fixtures
@pytest.fixture
async def async_client(async_session) -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for testing."""
    
    async def get_test_db():
        yield async_session
    
    app.dependency_overrides[get_db] = get_test_db
    
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
async def authenticated_client(async_client, test_user) -> AsyncGenerator[AsyncClient, None]:
    """Create authenticated HTTP client for testing."""
    
    async def get_test_user():
        return test_user
    
    app.dependency_overrides[get_current_user] = get_test_user
    
    yield async_client
    
    app.dependency_overrides.clear()


# Test data fixtures
@pytest.fixture
async def test_organization(async_session) -> Organization:
    """Create test organization."""
    org = Organization(
        name="Test Organization",
        display_name="Test Org",
        description="Test organization for automated tests",
        organization_type="company",
        address_line_1="123 Test Street",
        city="Test City",
        country="Test Country",
        is_active=True
    )
    async_session.add(org)
    await async_session.commit()
    await async_session.refresh(org)
    return org


@pytest.fixture
async def test_user(async_session, test_organization) -> User:
    """Create test user."""
    user = User(
        organization_id=test_organization.id,
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        display_name="Test User",
        password_hash="$2b$12$test.hash.for.testing.only",
        email_verified=True,
        is_active=True
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest.fixture
async def test_admin_user(async_session, test_organization) -> User:
    """Create test admin user."""
    user = User(
        organization_id=test_organization.id,
        username="testadmin",
        email="admin@example.com",
        first_name="Test",
        last_name="Admin",
        display_name="Test Admin",
        password_hash="$2b$12$test.hash.for.testing.only",
        email_verified=True,
        is_active=True,
        is_superuser=True
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest.fixture
async def test_client_data(async_session, test_organization) -> Client:
    """Create test client."""
    client = Client(
        organization_id=test_organization.id,
        name="Test Client",
        display_name="Test Client Corp",
        client_code="TC001",
        client_type="commercial",
        contact_name="John Test",
        contact_email="john@testclient.com",
        contact_phone="+1-555-0123",
        is_active=True
    )
    async_session.add(client)
    await async_session.commit()
    await async_session.refresh(client)
    return client


@pytest.fixture
async def test_site_data(async_session, test_client_data) -> Site:
    """Create test site."""
    site = Site(
        client_id=test_client_data.id,
        org_id=test_client_data.organization_id,
        name="Test Site",
        display_name="Test Site Location",
        site_code="TS001",
        address_line_1="456 Test Avenue",
        city="Test Site City",
        country="Test Country",
        is_active=True
    )
    async_session.add(site)
    await async_session.commit()
    await async_session.refresh(site)
    return site


@pytest.fixture
async def test_building_data(async_session, test_site_data) -> Building:
    """Create test building."""
    building = Building(
        site_id=test_site_data.id,
        org_id=test_site_data.org_id,
        name="Test Building",
        display_name="Test Main Building",
        building_code="TB001",
        building_type="office",
        floors=3,
        units=50,
        year_built=2020,
        total_area_sqm=1500.0,
        is_active=True
    )
    async_session.add(building)
    await async_session.commit()
    await async_session.refresh(building)
    return building


# Utility fixtures
@pytest.fixture
def temp_file():
    """Create temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


# Markers and test configuration
pytest_plugins = ["pytest_asyncio"]

# Test markers configuration
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "auth: mark test as authentication related"
    )
    config.addinivalue_line(
        "markers", "rbac: mark test as RBAC related"
    )
    config.addinivalue_line(
        "markers", "api: mark test as API related"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security related"
    )


# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add unit marker to unit tests
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker to integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add e2e marker to e2e tests
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        
        # Add api marker to API tests
        if "api" in str(item.fspath):
            item.add_marker(pytest.mark.api)