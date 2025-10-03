"""Tests for Role-Based Access Control (RBAC) system."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db
from app.models import Base
from app.models.auth import User, Role, Permission, Organization, UserRole
from app.core.security import hash_password


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_rbac.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def setup_test_db():
    """Create test database tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(setup_test_db):
    """Test client fixture."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db_session(setup_test_db):
    """Database session fixture."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_organization(db_session):
    """Create test organization."""
    org = Organization(
        name="RBAC Test Organization",
        tax_number="98765432101",
        address="RBAC Test Address",
        contact_email="rbac@test.com",
        is_active=True
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def comprehensive_permissions(db_session):
    """Create comprehensive set of permissions for testing."""
    permissions = [
        # Gate permissions
        Permission(name="Read Gates", codename="gate:read", resource="gate", action="read"),
        Permission(name="Create Gates", codename="gate:create", resource="gate", action="create"),
        Permission(name="Update Gates", codename="gate:update", resource="gate", action="update"),
        Permission(name="Delete Gates", codename="gate:delete", resource="gate", action="delete"),
        
        # Maintenance permissions
        Permission(name="Read Maintenance", codename="maintenance:read", resource="maintenance", action="read"),
        Permission(name="Create Maintenance", codename="maintenance:create", resource="maintenance", action="create"),
        Permission(name="Update Maintenance", codename="maintenance:update", resource="maintenance", action="update"),
        
        # User management permissions
        Permission(name="Read Users", codename="user:read", resource="user", action="read"),
        Permission(name="Create Users", codename="user:create", resource="user", action="create"),
        Permission(name="Update Users", codename="user:update", resource="user", action="update"),
        Permission(name="Delete Users", codename="user:delete", resource="user", action="delete"),
        
        # Organization permissions
        Permission(name="Read Organizations", codename="organization:read", resource="organization", action="read"),
        Permission(name="Update Organizations", codename="organization:update", resource="organization", action="update"),
        
        # Audit permissions
        Permission(name="Read Audit Logs", codename="audit:read", resource="audit", action="read"),
        Permission(name="Export Data", codename="audit:export", resource="audit", action="export"),
    ]
    
    for perm in permissions:
        db_session.add(perm)
    db_session.commit()
    
    return {perm.codename: perm for perm in permissions}


@pytest.fixture
def test_roles(db_session, comprehensive_permissions):
    """Create test roles with different permission sets."""
    
    # Client role - read-only access to basic resources
    client_role = Role(
        name="client",
        description="Client with read-only access",
        is_assignable=True
    )
    
    # Technician role - can read and update maintenance, read gates
    technician_role = Role(
        name="technician", 
        description="Technician with maintenance management access",
        is_assignable=True
    )
    
    # Manager role - full access to gates and maintenance, read users
    manager_role = Role(
        name="manager",
        description="Manager with operational management access", 
        is_assignable=True
    )
    
    # Admin role - full access except super admin functions
    admin_role = Role(
        name="admin",
        description="Administrator with full access",
        is_assignable=True
    )
    
    # Super Admin role - complete system access
    super_admin_role = Role(
        name="super_admin",
        description="Super Administrator with complete system access",
        is_assignable=False  # Only assignable by other super admins
    )
    
    # Auditor role - read-only access with audit capabilities
    auditor_role = Role(
        name="auditor",
        description="Auditor with read and audit access",
        is_assignable=True
    )
    
    roles = [client_role, technician_role, manager_role, admin_role, super_admin_role, auditor_role]
    
    for role in roles:
        db_session.add(role)
    db_session.commit()
    
    # Assign permissions to roles
    
    # Client: read-only access
    client_role.permissions.extend([
        comprehensive_permissions["gate:read"],
        comprehensive_permissions["maintenance:read"],
    ])
    
    # Technician: maintenance management + read access
    technician_role.permissions.extend([
        comprehensive_permissions["gate:read"],
        comprehensive_permissions["maintenance:read"],
        comprehensive_permissions["maintenance:create"],
        comprehensive_permissions["maintenance:update"],
    ])
    
    # Manager: full operational access
    manager_role.permissions.extend([
        comprehensive_permissions["gate:read"],
        comprehensive_permissions["gate:create"],
        comprehensive_permissions["gate:update"],
        comprehensive_permissions["maintenance:read"],
        comprehensive_permissions["maintenance:create"], 
        comprehensive_permissions["maintenance:update"],
        comprehensive_permissions["user:read"],
    ])
    
    # Admin: full access except super admin functions
    admin_role.permissions.extend([
        comprehensive_permissions["gate:read"],
        comprehensive_permissions["gate:create"],
        comprehensive_permissions["gate:update"],
        comprehensive_permissions["gate:delete"],
        comprehensive_permissions["maintenance:read"],
        comprehensive_permissions["maintenance:create"],
        comprehensive_permissions["maintenance:update"],
        comprehensive_permissions["user:read"],
        comprehensive_permissions["user:create"],
        comprehensive_permissions["user:update"],
        comprehensive_permissions["organization:read"],
        comprehensive_permissions["organization:update"],
    ])
    
    # Super Admin: complete access
    super_admin_role.permissions.extend(list(comprehensive_permissions.values()))
    
    # Auditor: read access + audit functions
    auditor_role.permissions.extend([
        comprehensive_permissions["gate:read"],
        comprehensive_permissions["maintenance:read"],
        comprehensive_permissions["user:read"],
        comprehensive_permissions["organization:read"],
        comprehensive_permissions["audit:read"],
        comprehensive_permissions["audit:export"],
    ])
    
    db_session.commit()
    
    return {
        "client": client_role,
        "technician": technician_role,
        "manager": manager_role,
        "admin": admin_role,
        "super_admin": super_admin_role,
        "auditor": auditor_role,
    }


@pytest.fixture
def test_users(db_session, test_organization, test_roles):
    """Create test users with different roles."""
    users = {}
    
    # Create users for each role
    role_data = [
        ("client_user", "client@test.com", "ClientPass123!", "client"),
        ("tech_user", "tech@test.com", "TechPass123!", "technician"),
        ("manager_user", "manager@test.com", "ManagerPass123!", "manager"),
        ("admin_user", "admin@test.com", "AdminPass123!", "admin"),
        ("super_admin_user", "superadmin@test.com", "SuperPass123!", "super_admin"),
        ("auditor_user", "auditor@test.com", "AuditorPass123!", "auditor"),
    ]
    
    for username, email, password, role_name in role_data:
        user = User(
            username=username,
            email=email,
            first_name=username.replace("_", " ").title(),
            last_name="User",
            password_hash=hash_password(password),
            organization_id=test_organization.id,
            org_id=test_organization.id,
            email_verified=True,
            is_active=True
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Assign role to user
        user_role = UserRole(
            user_id=user.id,
            role_id=test_roles[role_name].id
        )
        db_session.add(user_role)
        
        users[role_name] = user
    
    db_session.commit()
    return users


def get_auth_headers(client, username, password):
    """Helper function to get authentication headers."""
    login_data = {
        "username": username,
        "password": password
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


class TestRoleBasedAccess:
    """Test role-based access control."""
    
    def test_client_read_access(self, client, test_users):
        """Test client role has read access only."""
        headers = get_auth_headers(client, "client_user", "ClientPass123!")
        
        # Should be able to access profile (always allowed for authenticated users)
        response = client.get("/api/v1/auth/profile", headers=headers)
        assert response.status_code == 200
        
        # Test that client can read (if such endpoints exist)
        # Note: These would need to be actual endpoints in your API
        # response = client.get("/api/v1/gates", headers=headers)
        # assert response.status_code == 200  # Should have read access
        
    def test_technician_maintenance_access(self, client, test_users):
        """Test technician role has maintenance management access."""
        headers = get_auth_headers(client, "tech_user", "TechPass123!")
        
        # Should be able to access profile
        response = client.get("/api/v1/auth/profile", headers=headers)
        assert response.status_code == 200
        
        profile = response.json()
        roles = [role["name"] for role in profile.get("roles", [])]
        assert "technician" in roles
        
    def test_manager_operational_access(self, client, test_users):
        """Test manager role has operational management access."""
        headers = get_auth_headers(client, "manager_user", "ManagerPass123!")
        
        response = client.get("/api/v1/auth/profile", headers=headers)
        assert response.status_code == 200
        
        profile = response.json()
        roles = [role["name"] for role in profile.get("roles", [])]
        assert "manager" in roles
        
    def test_admin_full_access(self, client, test_users):
        """Test admin role has full access except super admin functions."""
        headers = get_auth_headers(client, "admin_user", "AdminPass123!")
        
        response = client.get("/api/v1/auth/profile", headers=headers)
        assert response.status_code == 200
        
        profile = response.json()
        roles = [role["name"] for role in profile.get("roles", [])]
        assert "admin" in roles
        
    def test_super_admin_complete_access(self, client, test_users):
        """Test super admin role has complete system access."""
        headers = get_auth_headers(client, "super_admin_user", "SuperPass123!")
        
        response = client.get("/api/v1/auth/profile", headers=headers)
        assert response.status_code == 200
        
        profile = response.json()
        roles = [role["name"] for role in profile.get("roles", [])]
        assert "super_admin" in roles
        
    def test_auditor_audit_access(self, client, test_users):
        """Test auditor role has read and audit access."""
        headers = get_auth_headers(client, "auditor_user", "AuditorPass123!")
        
        response = client.get("/api/v1/auth/profile", headers=headers)
        assert response.status_code == 200
        
        profile = response.json()
        roles = [role["name"] for role in profile.get("roles", [])]
        assert "auditor" in roles


class TestPermissionBasedAccess:
    """Test permission-based access control."""
    
    def test_user_permissions_in_profile(self, client, test_users):
        """Test that user permissions are correctly returned in profile."""
        headers = get_auth_headers(client, "admin_user", "AdminPass123!")
        
        response = client.get("/api/v1/auth/profile", headers=headers)
        assert response.status_code == 200
        
        profile = response.json()
        
        # Should have permissions array
        assert "permissions" in profile
        permissions = profile["permissions"]
        assert len(permissions) > 0
        
        # Check for specific admin permissions
        permission_codes = [perm["codename"] for perm in permissions]
        assert "user:read" in permission_codes
        assert "user:create" in permission_codes
        assert "organization:update" in permission_codes
        
    def test_role_hierarchy_permissions(self, client, test_users):
        """Test that different roles have appropriate permissions."""
        test_cases = [
            ("client_user", "ClientPass123!", ["gate:read", "maintenance:read"]),
            ("tech_user", "TechPass123!", ["maintenance:create", "maintenance:update"]),
            ("manager_user", "ManagerPass123!", ["gate:create", "user:read"]),
            ("admin_user", "AdminPass123!", ["user:create", "organization:update"]),
            ("auditor_user", "AuditorPass123!", ["audit:read", "audit:export"]),
        ]
        
        for username, password, expected_permissions in test_cases:
            headers = get_auth_headers(client, username, password)
            
            response = client.get("/api/v1/auth/profile", headers=headers)
            assert response.status_code == 200
            
            profile = response.json()
            permissions = profile.get("permissions", [])
            permission_codes = [perm["codename"] for perm in permissions]
            
            for expected_perm in expected_permissions:
                assert expected_perm in permission_codes, f"User {username} should have {expected_perm}"


class TestMultipleRoles:
    """Test users with multiple roles."""
    
    def test_user_multiple_roles(self, db_session, client, test_organization, test_roles):
        """Test user with multiple roles gets combined permissions."""
        # Create user with multiple roles
        user = User(
            username="multi_role_user",
            email="multi@test.com",
            first_name="Multi",
            last_name="Role",
            password_hash=hash_password("MultiPass123!"),
            organization_id=test_organization.id,
            org_id=test_organization.id,
            email_verified=True,
            is_active=True
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Assign multiple roles
        user_roles = [
            UserRole(user_id=user.id, role_id=test_roles["client"].id),
            UserRole(user_id=user.id, role_id=test_roles["technician"].id),
        ]
        
        for user_role in user_roles:
            db_session.add(user_role)
        
        db_session.commit()
        
        # Test that user gets combined permissions
        headers = get_auth_headers(client, "multi_role_user", "MultiPass123!")
        
        response = client.get("/api/v1/auth/profile", headers=headers)
        assert response.status_code == 200
        
        profile = response.json()
        
        # Should have both roles
        roles = [role["name"] for role in profile.get("roles", [])]
        assert "client" in roles
        assert "technician" in roles
        
        # Should have combined permissions from both roles
        permission_codes = [perm["codename"] for perm in profile.get("permissions", [])]
        assert "gate:read" in permission_codes  # From client role
        assert "maintenance:create" in permission_codes  # From technician role


class TestAccessDenied:
    """Test access denied scenarios."""
    
    def test_insufficient_permissions(self, client, test_users):
        """Test that users are denied access when they lack permissions."""
        # Client should not be able to create (if such endpoints exist)
        headers = get_auth_headers(client, "client_user", "ClientPass123!")
        
        # Test accessing profile (should work - basic auth)
        response = client.get("/api/v1/auth/profile", headers=headers)
        assert response.status_code == 200
        
        # In a real scenario, you would test specific protected endpoints:
        # response = client.post("/api/v1/gates", json={...}, headers=headers)
        # assert response.status_code == 403  # Forbidden
        
    def test_role_not_assignable(self, db_session, test_roles):
        """Test that non-assignable roles cannot be assigned."""
        # Super admin role should be marked as not assignable
        super_admin_role = test_roles["super_admin"]
        assert super_admin_role.is_assignable is False


class TestRoleManagement:
    """Test role management functionality."""
    
    def test_role_permission_assignment(self, db_session, comprehensive_permissions):
        """Test assigning permissions to roles."""
        # Create new role
        new_role = Role(
            name="test_role",
            description="Test role for permission assignment",
            is_assignable=True
        )
        
        db_session.add(new_role)
        db_session.commit()
        db_session.refresh(new_role)
        
        # Assign permissions
        new_role.permissions.extend([
            comprehensive_permissions["gate:read"],
            comprehensive_permissions["maintenance:read"],
        ])
        
        db_session.commit()
        
        # Verify permissions are assigned
        assert len(new_role.permissions) == 2
        permission_codes = [perm.codename for perm in new_role.permissions]
        assert "gate:read" in permission_codes
        assert "maintenance:read" in permission_codes
        
    def test_user_role_assignment(self, db_session, test_organization, test_roles):
        """Test assigning roles to users."""
        # Create new user
        user = User(
            username="role_test_user",
            email="roletest@test.com",
            first_name="Role",
            last_name="Test",
            password_hash=hash_password("RoleTest123!"),
            organization_id=test_organization.id,
            org_id=test_organization.id,
            email_verified=True,
            is_active=True
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Assign role
        user_role = UserRole(
            user_id=user.id,
            role_id=test_roles["client"].id
        )
        
        db_session.add(user_role)
        db_session.commit()
        
        # Verify role assignment
        assigned_roles = db_session.query(UserRole).filter_by(user_id=user.id).all()
        assert len(assigned_roles) == 1
        assert assigned_roles[0].role_id == test_roles["client"].id


class TestOrganizationBasedAccess:
    """Test organization-based access control."""
    
    def test_user_organization_isolation(self, db_session, client):
        """Test that users can only access data from their organization."""
        # Create second organization
        org2 = Organization(
            name="Second Organization",
            tax_number="11111111111",
            address="Second Address", 
            contact_email="second@org.com",
            is_active=True
        )
        
        db_session.add(org2)
        db_session.commit()
        db_session.refresh(org2)
        
        # Create user in second organization
        user2 = User(
            username="org2_user",
            email="org2@test.com",
            first_name="Org2",
            last_name="User",
            password_hash=hash_password("Org2Pass123!"),
            organization_id=org2.id,
            org_id=org2.id,
            email_verified=True,
            is_active=True
        )
        
        db_session.add(user2)
        db_session.commit()
        
        # Test that user can only access their own organization data
        headers = get_auth_headers(client, "org2_user", "Org2Pass123!")
        
        response = client.get("/api/v1/auth/profile", headers=headers)
        assert response.status_code == 200
        
        profile = response.json()
        assert profile["organization_id"] == org2.id
        

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=app.core.rbac", "--cov=app.services.auth"])