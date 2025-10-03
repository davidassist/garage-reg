"""Tests for bulk import functionality."""

import pytest
import io
import csv
from httpx import AsyncClient
from fastapi import status, UploadFile
from unittest.mock import Mock

from app.services.import_service import BulkImportService, validate_import_file
from app.schemas.structure import ImportResult


class TestImportValidation:
    """Test import file validation."""
    
    def test_validate_csv_file(self):
        """Test CSV file validation."""
        # Create mock CSV file
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "test.csv"
        mock_file.size = 1024
        
        errors = validate_import_file(mock_file, ["client_name", "site_name"])
        assert len(errors) == 0
    
    def test_validate_excel_file(self):
        """Test Excel file validation."""
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "test.xlsx"
        mock_file.size = 2048
        
        errors = validate_import_file(mock_file, ["client_name"])
        assert len(errors) == 0
    
    def test_reject_invalid_format(self):
        """Test rejection of invalid file formats."""
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "test.txt"
        
        errors = validate_import_file(mock_file, ["client_name"])
        assert len(errors) == 1
        assert "File must be CSV or Excel format" in errors[0]
    
    def test_reject_large_files(self):
        """Test rejection of large files."""
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "test.csv"
        mock_file.size = 20 * 1024 * 1024  # 20MB
        
        errors = validate_import_file(mock_file, ["client_name"])
        assert len(errors) == 1
        assert "File size must be less than 10MB" in errors[0]


class TestImportAPI:
    """Test import API endpoints."""
    
    @pytest.mark.asyncio
    async def test_hierarchical_import_success(self, client: AsyncClient, admin_token: str):
        """Test successful hierarchical import."""
        # Create test CSV data
        csv_data = """client_name,site_name,building_name,gate_name,gate_type
Test Import Client,Test Import Site,Test Import Building,Test Import Gate,swing"""
        
        # Create file-like object
        file_content = csv_data.encode('utf-8')
        
        response = await client.post(
            "/api/v1/import/hierarchical",
            files={"file": ("test.csv", io.BytesIO(file_content), "text/csv")},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["total_rows"] == 1
        assert data["processed_rows"] == 1
        assert data["skipped_rows"] == 0
        assert len(data["created_entities"]["clients"]) == 1
        assert len(data["created_entities"]["sites"]) == 1
        assert len(data["created_entities"]["buildings"]) == 1
        assert len(data["created_entities"]["gates"]) == 1
    
    @pytest.mark.asyncio
    async def test_import_with_missing_columns(self, client: AsyncClient, admin_token: str):
        """Test import with missing required columns."""
        # CSV missing gate_name column
        csv_data = """client_name,site_name,building_name
Test Client,Test Site,Test Building"""
        
        file_content = csv_data.encode('utf-8')
        
        response = await client.post(
            "/api/v1/import/hierarchical",
            files={"file": ("test.csv", io.BytesIO(file_content), "text/csv")},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is False
        assert data["skipped_rows"] == 1
        assert len(data["errors"]) > 0
        assert "Missing required fields" in data["errors"][0]
    
    @pytest.mark.asyncio
    async def test_import_with_invalid_types(self, client: AsyncClient, admin_token: str):
        """Test import with invalid enum values."""
        csv_data = """client_name,client_type,site_name,building_name,gate_name,gate_type
Test Client,invalid_type,Test Site,Test Building,Test Gate,invalid_gate_type"""
        
        file_content = csv_data.encode('utf-8')
        
        response = await client.post(
            "/api/v1/import/hierarchical",
            files={"file": ("test.csv", io.BytesIO(file_content), "text/csv")},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should still process but with errors
        assert data["skipped_rows"] >= 1 or len(data["errors"]) > 0
    
    @pytest.mark.asyncio
    async def test_clients_only_import(self, client: AsyncClient, admin_token: str):
        """Test importing only clients."""
        csv_data = """client_name,client_type,contact_person,email
Client Only 1,commercial,John Doe,john@test.com
Client Only 2,residential,Jane Smith,jane@test.com"""
        
        file_content = csv_data.encode('utf-8')
        
        response = await client.post(
            "/api/v1/import/clients",
            files={"file": ("clients.csv", io.BytesIO(file_content), "text/csv")},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_rows"] == 2
    
    @pytest.mark.asyncio
    async def test_duplicate_handling(self, client: AsyncClient, admin_token: str):
        """Test handling of duplicate entries."""
        # Import same data twice
        csv_data = """client_name,site_name,building_name,gate_name,gate_type
Duplicate Test,Duplicate Site,Duplicate Building,Duplicate Gate,swing"""
        
        file_content = csv_data.encode('utf-8')
        
        # First import
        response1 = await client.post(
            "/api/v1/import/hierarchical",
            files={"file": ("test1.csv", io.BytesIO(file_content), "text/csv")},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Second import (should handle duplicates)
        response2 = await client.post(
            "/api/v1/import/hierarchical",
            files={"file": ("test2.csv", io.BytesIO(file_content), "text/csv")},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        
        data2 = response2.json()
        # Should have warnings about existing entities
        assert len(data2.get("warnings", [])) > 0 or data2["skipped_rows"] > 0
    
    @pytest.mark.asyncio
    async def test_import_unauthorized(self, client: AsyncClient, client_token: str):
        """Test import without proper permissions."""
        csv_data = """client_name,site_name,building_name,gate_name,gate_type
Unauthorized,Unauthorized Site,Unauthorized Building,Unauthorized Gate,swing"""
        
        file_content = csv_data.encode('utf-8')
        
        response = await client.post(
            "/api/v1/import/hierarchical",
            files={"file": ("test.csv", io.BytesIO(file_content), "text/csv")},
            headers={"Authorization": f"Bearer {client_token}"}  # Client role, not admin
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_download_template(self, client: AsyncClient, admin_token: str):
        """Test downloading import templates."""
        response = await client.get(
            "/api/v1/import/template/hierarchical",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]
        
        # Check CSV content
        content = response.text
        lines = content.strip().split('\n')
        assert len(lines) >= 1  # At least header row
        headers = lines[0].split(',')
        assert "client_name" in headers
        assert "site_name" in headers
        assert "building_name" in headers
        assert "gate_name" in headers
    
    @pytest.mark.asyncio
    async def test_template_not_found(self, client: AsyncClient, admin_token: str):
        """Test requesting non-existent template."""
        response = await client.get(
            "/api/v1/import/template/invalid_type",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestBulkImportService:
    """Test the BulkImportService directly."""
    
    @pytest.mark.asyncio
    async def test_csv_parsing(self, db_session, test_org_id):
        """Test CSV file parsing."""
        service = BulkImportService(db_session, test_org_id)
        
        # Create mock CSV file
        csv_content = """client_name,site_name
Test CSV Client,Test CSV Site"""
        
        mock_file = Mock()
        mock_file.read.return_value = csv_content.encode('utf-8')
        
        data = await service._read_csv(mock_file)
        
        assert len(data) == 1
        assert data[0]["client_name"] == "Test CSV Client"
        assert data[0]["site_name"] == "Test CSV Site"
    
    @pytest.mark.asyncio
    async def test_client_creation(self, db_session, test_org_id):
        """Test client creation during import."""
        service = BulkImportService(db_session, test_org_id)
        
        row_data = {
            "client_name": "Service Test Client",
            "client_type": "commercial",
            "client_contact_person": "Test Contact",
            "client_email": "test@service.com"
        }
        
        result = ImportResult(
            success=True,
            total_rows=1,
            processed_rows=0,
            skipped_rows=0,
            created_entities={"clients": [], "sites": [], "buildings": [], "gates": []}
        )
        
        client_id = await service._ensure_client(row_data, result)
        
        assert client_id is not None
        assert len(result.created_entities["clients"]) == 1
        assert result.created_entities["clients"][0] == client_id
        
        # Verify client exists in database
        from app.models.organization import Client
        client = db_session.query(Client).filter(Client.id == client_id).first()
        assert client is not None
        assert client.name == "Service Test Client"
        assert client.type == "commercial"
    
    @pytest.mark.asyncio
    async def test_hierarchy_creation(self, db_session, test_org_id):
        """Test complete hierarchy creation."""
        service = BulkImportService(db_session, test_org_id)
        
        test_data = [{
            "client_name": "Hierarchy Test Client",
            "client_type": "residential",
            "site_name": "Hierarchy Test Site",
            "site_city": "Budapest",
            "building_name": "Hierarchy Test Building",
            "building_type": "residential",
            "gate_name": "Hierarchy Test Gate",
            "gate_type": "swing"
        }]
        
        result = await service._import_hierarchical(test_data)
        
        assert result.success is True
        assert result.processed_rows == 1
        assert len(result.created_entities["clients"]) == 1
        assert len(result.created_entities["sites"]) == 1
        assert len(result.created_entities["buildings"]) == 1
        assert len(result.created_entities["gates"]) == 1
        
        # Verify complete hierarchy in database
        from app.models.organization import Client, Site, Building, Gate
        
        client = db_session.query(Client).filter(
            Client.name == "Hierarchy Test Client"
        ).first()
        assert client is not None
        
        site = db_session.query(Site).filter(
            Site.client_id == client.id,
            Site.name == "Hierarchy Test Site"
        ).first()
        assert site is not None
        
        building = db_session.query(Building).filter(
            Building.site_id == site.id,
            Building.name == "Hierarchy Test Building"
        ).first()
        assert building is not None
        
        gate = db_session.query(Gate).filter(
            Gate.building_id == building.id,
            Gate.name == "Hierarchy Test Gate"
        ).first()
        assert gate is not None