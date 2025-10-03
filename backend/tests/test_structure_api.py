"""Tests for hierarchical structure CRUD operations."""

import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.orm import Session

from app.models.organization import Client, Site, Building, Gate
from app.schemas.structure import ClientType, BuildingType, GateType, GateStatus


class TestClientAPI:
    """Test client CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_client(self, client: AsyncClient, admin_token: str):
        """Test creating a new client."""
        client_data = {
            "name": "Test Client",
            "type": "commercial",
            "contact_person": "John Doe",
            "email": "john@test.com",
            "phone": "+36301234567",
            "city": "Budapest"
        }
        
        response = await client.post(
            "/api/v1/structure/clients",
            json=client_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == client_data["name"]
        assert data["type"] == client_data["type"]
        assert data["contact_person"] == client_data["contact_person"]
        assert "id" in data
        assert "created_at" in data
    
    @pytest.mark.asyncio
    async def test_get_client(self, client: AsyncClient, admin_token: str, test_client_id: int):
        """Test retrieving a client."""
        response = await client.get(
            f"/api/v1/structure/clients/{test_client_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_client_id
        assert "sites_count" in data
        assert "buildings_count" in data
        assert "gates_count" in data
    
    @pytest.mark.asyncio
    async def test_list_clients(self, client: AsyncClient, admin_token: str):
        """Test listing clients with pagination."""
        response = await client.get(
            "/api/v1/structure/clients?page=1&size=10",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
        assert data["page"] == 1
        assert data["size"] == 10
    
    @pytest.mark.asyncio
    async def test_search_clients(self, client: AsyncClient, admin_token: str):
        """Test searching clients."""
        response = await client.get(
            "/api/v1/structure/clients?query=test&type=commercial",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
    
    @pytest.mark.asyncio
    async def test_update_client(self, client: AsyncClient, admin_token: str, test_client_id: int):
        """Test updating a client."""
        update_data = {
            "contact_person": "Jane Doe",
            "email": "jane@test.com"
        }
        
        response = await client.put(
            f"/api/v1/structure/clients/{test_client_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["contact_person"] == update_data["contact_person"]
        assert data["email"] == update_data["email"]
    
    @pytest.mark.asyncio
    async def test_delete_client(self, client: AsyncClient, admin_token: str):
        """Test deleting a client."""
        # Create a client for deletion
        client_data = {
            "name": "Delete Test Client",
            "type": "residential"
        }
        
        create_response = await client.post(
            "/api/v1/structure/clients",
            json=client_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        client_id = create_response.json()["id"]
        
        # Delete the client
        response = await client.delete(
            f"/api/v1/structure/clients/{client_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()


class TestSiteAPI:
    """Test site CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_site(self, client: AsyncClient, admin_token: str, test_client_id: int):
        """Test creating a new site."""
        site_data = {
            "client_id": test_client_id,
            "name": "Test Site",
            "site_code": "TS001",
            "city": "Budapest",
            "latitude": "47.4979",
            "longitude": "19.0402"
        }
        
        response = await client.post(
            "/api/v1/structure/sites",
            json=site_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == site_data["name"]
        assert data["client_id"] == test_client_id
        assert data["site_code"] == site_data["site_code"]
    
    @pytest.mark.asyncio
    async def test_get_site_with_stats(self, client: AsyncClient, admin_token: str, test_site_id: int):
        """Test retrieving a site with statistics."""
        response = await client.get(
            f"/api/v1/structure/sites/{test_site_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_site_id
        assert "buildings_count" in data
        assert "gates_count" in data


class TestBuildingAPI:
    """Test building CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_building(self, client: AsyncClient, admin_token: str, test_site_id: int):
        """Test creating a new building."""
        building_data = {
            "site_id": test_site_id,
            "name": "Test Building",
            "building_code": "TB001",
            "building_type": "office",
            "floors": 3,
            "units": 12
        }
        
        response = await client.post(
            "/api/v1/structure/buildings",
            json=building_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == building_data["name"]
        assert data["site_id"] == test_site_id
        assert data["building_type"] == building_data["building_type"]
        assert data["floors"] == building_data["floors"]


class TestGateAPI:
    """Test gate CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_gate(self, client: AsyncClient, admin_token: str, test_building_id: int):
        """Test creating a new gate."""
        gate_data = {
            "building_id": test_building_id,
            "name": "Test Gate",
            "gate_code": "TG001",
            "gate_type": "sliding",
            "manufacturer": "Came",
            "model": "BXV-4",
            "serial_number": "SN123456",
            "width_cm": 400,
            "height_cm": 200,
            "status": "operational"
        }
        
        response = await client.post(
            "/api/v1/structure/gates",
            json=gate_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == gate_data["name"]
        assert data["building_id"] == test_building_id
        assert data["gate_type"] == gate_data["gate_type"]
        assert data["manufacturer"] == gate_data["manufacturer"]
    
    @pytest.mark.asyncio
    async def test_search_gates_by_manufacturer(self, client: AsyncClient, admin_token: str):
        """Test searching gates by manufacturer."""
        response = await client.get(
            "/api/v1/structure/gates?manufacturer=Came&status=operational",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
    
    @pytest.mark.asyncio
    async def test_update_gate_status(self, client: AsyncClient, admin_token: str, test_gate_id: int):
        """Test updating gate status."""
        update_data = {
            "status": "maintenance",
            "current_cycle_count": 5000
        }
        
        response = await client.put(
            f"/api/v1/structure/gates/{test_gate_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == update_data["status"]
        assert data["current_cycle_count"] == update_data["current_cycle_count"]


class TestHierarchicalValidation:
    """Test hierarchical relationship validation."""
    
    @pytest.mark.asyncio
    async def test_site_requires_valid_client(self, client: AsyncClient, admin_token: str):
        """Test that site creation requires valid client."""
        site_data = {
            "client_id": 99999,  # Non-existent client
            "name": "Invalid Site"
        }
        
        response = await client.post(
            "/api/v1/structure/sites",
            json=site_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Client not found" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_building_requires_valid_site(self, client: AsyncClient, admin_token: str):
        """Test that building creation requires valid site."""
        building_data = {
            "site_id": 99999,  # Non-existent site
            "name": "Invalid Building"
        }
        
        response = await client.post(
            "/api/v1/structure/buildings",
            json=building_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Site not found" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_gate_requires_valid_building(self, client: AsyncClient, admin_token: str):
        """Test that gate creation requires valid building."""
        gate_data = {
            "building_id": 99999,  # Non-existent building
            "name": "Invalid Gate",
            "gate_type": "swing"
        }
        
        response = await client.post(
            "/api/v1/structure/gates",
            json=gate_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Building not found" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_cannot_delete_client_with_active_sites(
        self, 
        client: AsyncClient, 
        admin_token: str, 
        test_client_with_sites_id: int
    ):
        """Test that client with active sites cannot be deleted."""
        response = await client.delete(
            f"/api/v1/structure/clients/{test_client_with_sites_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cannot delete client with active sites" in response.json()["detail"]


class TestPermissions:
    """Test RBAC permissions for structure endpoints."""
    
    @pytest.mark.asyncio
    async def test_client_role_cannot_manage_clients(self, client: AsyncClient, client_token: str):
        """Test that client role cannot create clients."""
        client_data = {
            "name": "Unauthorized Client",
            "type": "residential"
        }
        
        response = await client.post(
            "/api/v1/structure/clients",
            json=client_data,
            headers={"Authorization": f"Bearer {client_token}"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_technician_can_view_gates(self, client: AsyncClient, technician_token: str):
        """Test that technician can view gates."""
        response = await client.get(
            "/api/v1/structure/gates",
            headers={"Authorization": f"Bearer {technician_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK