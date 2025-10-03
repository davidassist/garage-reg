"""
API Tests for Core Endpoints
Tests REST API functionality with comprehensive coverage
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestOrganizationAPI:
    """Test organization management API endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_organizations(self, authenticated_client: AsyncClient, test_organization):
        """Test getting list of organizations."""
        response = await authenticated_client.get("/api/v1/organizations")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Find our test organization
        test_org = next((org for org in data if org["id"] == test_organization.id), None)
        assert test_org is not None
        assert test_org["name"] == test_organization.name
        assert test_org["display_name"] == test_organization.display_name
    
    @pytest.mark.asyncio
    async def test_get_organization_by_id(self, authenticated_client: AsyncClient, test_organization):
        """Test getting specific organization by ID."""
        response = await authenticated_client.get(f"/api/v1/organizations/{test_organization.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == test_organization.id
        assert data["name"] == test_organization.name
        assert data["display_name"] == test_organization.display_name
        assert data["organization_type"] == test_organization.organization_type
    
    @pytest.mark.asyncio
    async def test_create_organization(self, authenticated_client: AsyncClient):
        """Test creating new organization."""
        org_data = {
            "name": "New Test Org",
            "display_name": "New Test Organization",
            "description": "Test organization created via API",
            "organization_type": "company",
            "address_line_1": "123 API Street",
            "city": "API City",
            "country": "Test Country"
        }
        
        response = await authenticated_client.post("/api/v1/organizations", json=org_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == org_data["name"]
        assert data["display_name"] == org_data["display_name"]
        assert data["organization_type"] == org_data["organization_type"]
        assert "id" in data
        assert data["is_active"] is True
    
    @pytest.mark.asyncio
    async def test_update_organization(self, authenticated_client: AsyncClient, test_organization):
        """Test updating organization."""
        update_data = {
            "display_name": "Updated Organization Name",
            "description": "Updated description"
        }
        
        response = await authenticated_client.put(
            f"/api/v1/organizations/{test_organization.id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == test_organization.id
        assert data["display_name"] == update_data["display_name"]
        assert data["description"] == update_data["description"]
    
    @pytest.mark.asyncio
    async def test_delete_organization(self, authenticated_client: AsyncClient, async_session: AsyncSession):
        """Test soft deleting organization."""
        # Create organization to delete
        from app.models.organization import Organization
        
        org_to_delete = Organization(
            name="Delete Test Org",
            display_name="Organization to Delete",
            organization_type="company",
            is_active=True
        )
        async_session.add(org_to_delete)
        await async_session.commit()
        await async_session.refresh(org_to_delete)
        
        response = await authenticated_client.delete(f"/api/v1/organizations/{org_to_delete.id}")
        
        assert response.status_code == 204
        
        # Verify organization is soft deleted
        get_response = await authenticated_client.get(f"/api/v1/organizations/{org_to_delete.id}")
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_organization_validation(self, authenticated_client: AsyncClient):
        """Test organization data validation."""
        # Missing required fields
        invalid_data = {
            "display_name": "Missing Name"
        }
        
        response = await authenticated_client.post("/api/v1/organizations", json=invalid_data)
        assert response.status_code == 422
        
        # Invalid organization type
        invalid_type_data = {
            "name": "Test Org",
            "display_name": "Test Org",
            "organization_type": "invalid_type"
        }
        
        response = await authenticated_client.post("/api/v1/organizations", json=invalid_type_data)
        assert response.status_code == 422


class TestUserAPI:
    """Test user management API endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_users(self, authenticated_client: AsyncClient, test_user):
        """Test getting list of users."""
        response = await authenticated_client.get("/api/v1/users")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Find our test user
        user = next((u for u in data if u["id"] == test_user.id), None)
        assert user is not None
        assert user["username"] == test_user.username
        assert user["email"] == test_user.email
        assert "password" not in user  # Password should never be returned
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, authenticated_client: AsyncClient, test_user):
        """Test getting specific user by ID."""
        response = await authenticated_client.get(f"/api/v1/users/{test_user.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert data["first_name"] == test_user.first_name
        assert data["last_name"] == test_user.last_name
        assert "password" not in data
    
    @pytest.mark.asyncio
    async def test_create_user(self, authenticated_client: AsyncClient, test_organization):
        """Test creating new user."""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "securepassword123",
            "organization_id": test_organization.id
        }
        
        response = await authenticated_client.post("/api/v1/users", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["first_name"] == user_data["first_name"]
        assert data["last_name"] == user_data["last_name"]
        assert "password" not in data
        assert data["is_active"] is True
        assert data["email_verified"] is False  # Should default to False
    
    @pytest.mark.asyncio
    async def test_update_user(self, authenticated_client: AsyncClient, test_user):
        """Test updating user."""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "display_name": "Updated User Name"
        }
        
        response = await authenticated_client.put(
            f"/api/v1/users/{test_user.id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == test_user.id
        assert data["first_name"] == update_data["first_name"]
        assert data["last_name"] == update_data["last_name"]
        assert data["display_name"] == update_data["display_name"]
    
    @pytest.mark.asyncio
    async def test_user_validation(self, authenticated_client: AsyncClient, test_organization):
        """Test user data validation."""
        # Invalid email format
        invalid_email_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "password123",
            "organization_id": test_organization.id
        }
        
        response = await authenticated_client.post("/api/v1/users", json=invalid_email_data)
        assert response.status_code == 422
        
        # Weak password
        weak_password_data = {
            "username": "testuser2",
            "email": "test2@example.com",
            "password": "123",  # Too weak
            "organization_id": test_organization.id
        }
        
        response = await authenticated_client.post("/api/v1/users", json=weak_password_data)
        assert response.status_code == 422


class TestClientAPI:
    """Test client management API endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_clients(self, authenticated_client: AsyncClient, test_client_data):
        """Test getting list of clients."""
        response = await authenticated_client.get("/api/v1/clients")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Find our test client
        client = next((c for c in data if c["id"] == test_client_data.id), None)
        assert client is not None
        assert client["name"] == test_client_data.name
        assert client["client_code"] == test_client_data.client_code
    
    @pytest.mark.asyncio
    async def test_create_client(self, authenticated_client: AsyncClient, test_organization):
        """Test creating new client."""
        client_data = {
            "name": "New Test Client",
            "display_name": "New Test Client Corp",
            "client_code": "NTC001",
            "client_type": "commercial",
            "contact_name": "John New",
            "contact_email": "john@newtestclient.com",
            "contact_phone": "+1-555-0199",
            "organization_id": test_organization.id
        }
        
        response = await authenticated_client.post("/api/v1/clients", json=client_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == client_data["name"]
        assert data["client_code"] == client_data["client_code"]
        assert data["client_type"] == client_data["client_type"]
        assert data["contact_name"] == client_data["contact_name"]
        assert data["is_active"] is True
    
    @pytest.mark.asyncio
    async def test_client_code_uniqueness(self, authenticated_client: AsyncClient, test_client_data):
        """Test client code uniqueness constraint."""
        duplicate_client = {
            "name": "Duplicate Client",
            "client_code": test_client_data.client_code,  # Duplicate code
            "client_type": "commercial",
            "organization_id": test_client_data.organization_id
        }
        
        response = await authenticated_client.post("/api/v1/clients", json=duplicate_client)
        
        assert response.status_code == 400
        data = response.json()
        assert "client_code" in data["detail"].lower()


class TestSiteAPI:
    """Test site management API endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_sites(self, authenticated_client: AsyncClient, test_site_data):
        """Test getting list of sites."""
        response = await authenticated_client.get("/api/v1/sites")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Find our test site
        site = next((s for s in data if s["id"] == test_site_data.id), None)
        assert site is not None
        assert site["name"] == test_site_data.name
        assert site["site_code"] == test_site_data.site_code
    
    @pytest.mark.asyncio
    async def test_create_site(self, authenticated_client: AsyncClient, test_client_data):
        """Test creating new site."""
        site_data = {
            "name": "New Test Site",
            "display_name": "New Test Site Location",
            "site_code": "NTS001",
            "address_line_1": "789 New Test Avenue",
            "city": "New Test City",
            "country": "Test Country",
            "client_id": test_client_data.id
        }
        
        response = await authenticated_client.post("/api/v1/sites", json=site_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == site_data["name"]
        assert data["site_code"] == site_data["site_code"]
        assert data["client_id"] == test_client_data.id
        assert data["is_active"] is True
    
    @pytest.mark.asyncio
    async def test_get_sites_by_client(self, authenticated_client: AsyncClient, test_client_data, test_site_data):
        """Test getting sites filtered by client."""
        response = await authenticated_client.get(f"/api/v1/clients/{test_client_data.id}/sites")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        # All returned sites should belong to the client
        for site in data:
            assert site["client_id"] == test_client_data.id


class TestBuildingAPI:
    """Test building management API endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_buildings(self, authenticated_client: AsyncClient, test_building_data):
        """Test getting list of buildings."""
        response = await authenticated_client.get("/api/v1/buildings")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Find our test building
        building = next((b for b in data if b["id"] == test_building_data.id), None)
        assert building is not None
        assert building["name"] == test_building_data.name
        assert building["building_code"] == test_building_data.building_code
    
    @pytest.mark.asyncio
    async def test_create_building(self, authenticated_client: AsyncClient, test_site_data):
        """Test creating new building."""
        building_data = {
            "name": "New Test Building",
            "display_name": "New Test Building",
            "building_code": "NTB001",
            "building_type": "warehouse",
            "floors": 2,
            "units": 25,
            "year_built": 2022,
            "total_area_sqm": 2500.0,
            "site_id": test_site_data.id
        }
        
        response = await authenticated_client.post("/api/v1/buildings", json=building_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == building_data["name"]
        assert data["building_code"] == building_data["building_code"]
        assert data["building_type"] == building_data["building_type"]
        assert data["floors"] == building_data["floors"]
        assert data["site_id"] == test_site_data.id
    
    @pytest.mark.asyncio
    async def test_get_buildings_by_site(self, authenticated_client: AsyncClient, test_site_data, test_building_data):
        """Test getting buildings filtered by site."""
        response = await authenticated_client.get(f"/api/v1/sites/{test_site_data.id}/buildings")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        # All returned buildings should belong to the site
        for building in data:
            assert building["site_id"] == test_site_data.id


class TestAPIErrorHandling:
    """Test API error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_resource(self, authenticated_client: AsyncClient):
        """Test getting non-existent resources returns 404."""
        endpoints = [
            "/api/v1/organizations/99999",
            "/api/v1/users/99999",
            "/api/v1/clients/99999",
            "/api/v1/sites/99999",
            "/api/v1/buildings/99999"
        ]
        
        for endpoint in endpoints:
            response = await authenticated_client.get(endpoint)
            assert response.status_code == 404
            
            data = response.json()
            assert "detail" in data
            assert "not found" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_invalid_json_payload(self, authenticated_client: AsyncClient):
        """Test handling of invalid JSON payloads."""
        # Send invalid JSON
        response = await authenticated_client.post(
            "/api/v1/organizations",
            content="invalid json content",
            headers={"content-type": "application/json"}
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_missing_content_type(self, authenticated_client: AsyncClient):
        """Test handling of missing content type header."""
        response = await authenticated_client.post(
            "/api/v1/organizations",
            content='{"name": "test"}',
            headers={}  # No content-type header
        )
        
        # Should handle gracefully
        assert response.status_code in [422, 415]  # Unprocessable Entity or Unsupported Media Type
    
    @pytest.mark.asyncio
    async def test_method_not_allowed(self, authenticated_client: AsyncClient):
        """Test method not allowed responses."""
        # Try PATCH on endpoint that doesn't support it
        response = await authenticated_client.patch("/api/v1/organizations")
        
        assert response.status_code == 405
        
        # Verify Allow header is present
        assert "allow" in response.headers


class TestAPIPagination:
    """Test API pagination functionality."""
    
    @pytest.mark.asyncio
    async def test_pagination_parameters(self, authenticated_client: AsyncClient, async_session: AsyncSession, test_organization):
        """Test pagination with skip and limit parameters."""
        # Create multiple clients for pagination testing
        from app.models.client import Client
        
        clients = []
        for i in range(25):
            client = Client(
                organization_id=test_organization.id,
                name=f"Pagination Client {i}",
                client_code=f"PAG{i:03d}",
                client_type="commercial",
                is_active=True
            )
            clients.append(client)
        
        async_session.add_all(clients)
        await async_session.commit()
        
        # Test first page
        response = await authenticated_client.get("/api/v1/clients?skip=0&limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) <= 10
        
        # Test second page
        response = await authenticated_client.get("/api/v1/clients?skip=10&limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) <= 10
    
    @pytest.mark.asyncio
    async def test_pagination_limits(self, authenticated_client: AsyncClient):
        """Test pagination parameter limits."""
        # Test maximum limit
        response = await authenticated_client.get("/api/v1/clients?limit=1000")
        assert response.status_code == 200
        
        # Should be capped at reasonable maximum
        data = response.json()
        assert len(data) <= 100  # Assuming 100 is max limit
        
        # Test negative parameters
        response = await authenticated_client.get("/api/v1/clients?skip=-1&limit=-1")
        assert response.status_code in [422, 400]  # Should validate parameters


class TestAPIFiltering:
    """Test API filtering functionality."""
    
    @pytest.mark.asyncio
    async def test_filter_by_active_status(self, authenticated_client: AsyncClient, async_session: AsyncSession, test_organization):
        """Test filtering by active status."""
        from app.models.client import Client
        
        # Create active and inactive clients
        active_client = Client(
            organization_id=test_organization.id,
            name="Active Client",
            client_code="ACT001",
            client_type="commercial",
            is_active=True
        )
        
        inactive_client = Client(
            organization_id=test_organization.id,
            name="Inactive Client",
            client_code="INA001",
            client_type="commercial",
            is_active=False
        )
        
        async_session.add_all([active_client, inactive_client])
        await async_session.commit()
        
        # Filter for active clients only
        response = await authenticated_client.get("/api/v1/clients?is_active=true")
        assert response.status_code == 200
        
        data = response.json()
        for client in data:
            assert client["is_active"] is True
        
        # Filter for inactive clients only
        response = await authenticated_client.get("/api/v1/clients?is_active=false")
        assert response.status_code == 200
        
        data = response.json()
        for client in data:
            assert client["is_active"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])