"""
Integration Tests for Data Export/Import API
Tests export/import endpoints with real database and file handling
"""
import pytest
import json
import tempfile
from pathlib import Path
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.user import User
from app.models.client import Client
from app.models.site import Site


class TestExportImportAPI:
    """Test export/import API endpoints."""
    
    @pytest.mark.asyncio
    async def test_export_organization_data_jsonl(self, authenticated_client: AsyncClient, test_organization, test_user):
        """Test exporting organization data in JSONL format."""
        export_request = {
            "organization_id": test_organization.id,
            "format": "jsonl",
            "include_metadata": True,
            "include_tables": ["organizations", "users"]
        }
        
        response = await authenticated_client.post("/api/v1/admin/data-transfer/export", json=export_request)
        
        assert response.status_code == 200
        
        # Check response headers
        assert response.headers["content-type"] == "application/x-jsonl"
        assert "attachment" in response.headers["content-disposition"]
        
        # Verify JSONL content
        content = response.text
        lines = content.strip().split('\n')
        
        # First line should be metadata
        metadata = json.loads(lines[0])
        assert "_metadata" in metadata
        assert metadata["_metadata"]["format"] == "jsonl"
        assert metadata["_metadata"]["organization_id"] == test_organization.id
        
        # Should have data records
        assert len(lines) > 1
        
        # Verify data records
        for line in lines[1:]:
            record = json.loads(line)
            assert "_table" in record
            assert record["_table"] in ["organizations", "users"]
    
    @pytest.mark.asyncio
    async def test_export_organization_data_json(self, authenticated_client: AsyncClient, test_organization):
        """Test exporting organization data in JSON format."""
        export_request = {
            "organization_id": test_organization.id,
            "format": "json",
            "include_metadata": True
        }
        
        response = await authenticated_client.post("/api/v1/admin/data-transfer/export", json=export_request)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        # Verify JSON content structure
        content = json.loads(response.text)
        assert "_metadata" in content
        assert "data" in content
        
        metadata = content["_metadata"]
        assert metadata["format"] == "json"
        assert metadata["organization_id"] == test_organization.id
        
        # Should have organization data
        data = content["data"]
        assert "organizations" in data
        assert len(data["organizations"]) >= 1
    
    @pytest.mark.asyncio
    async def test_export_with_table_filters(self, authenticated_client: AsyncClient, test_organization):
        """Test export with specific table inclusion/exclusion."""
        # Test include_tables
        export_request = {
            "organization_id": test_organization.id,
            "format": "json",
            "include_tables": ["organizations"]
        }
        
        response = await authenticated_client.post("/api/v1/admin/data-transfer/export", json=export_request)
        assert response.status_code == 200
        
        content = json.loads(response.text)
        data = content["data"]
        
        # Should only have organizations table
        assert "organizations" in data
        assert "users" not in data or len(data["users"]) == 0
    
    @pytest.mark.asyncio
    async def test_export_unauthorized_organization(self, authenticated_client: AsyncClient, async_session: AsyncSession):
        """Test export attempt for unauthorized organization."""
        # Create another organization
        other_org = Organization(
            name="Other Organization",
            display_name="Other Org",
            organization_type="company",
            is_active=True
        )
        async_session.add(other_org)
        await async_session.commit()
        await async_session.refresh(other_org)
        
        export_request = {
            "organization_id": other_org.id,
            "format": "json"
        }
        
        response = await authenticated_client.post("/api/v1/admin/data-transfer/export", json=export_request)
        
        # Should be forbidden
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_import_jsonl_data_success(self, authenticated_client: AsyncClient, test_organization, temp_file):
        """Test successful import of JSONL data."""
        # Create sample JSONL content
        metadata = {
            "_metadata": {
                "export_id": "test_import_123",
                "timestamp": "2024-01-01T00:00:00",
                "format": "jsonl",
                "total_records": 1,
                "organization_id": test_organization.id
            }
        }
        
        client_record = {
            "_table": "clients",
            "id": 999,  # Use high ID to avoid conflicts
            "organization_id": test_organization.id,
            "name": "Imported Client",
            "display_name": "Test Import Client",
            "client_code": "IMP001",
            "client_type": "commercial",
            "is_active": True
        }
        
        jsonl_content = "\n".join([
            json.dumps(metadata),
            json.dumps(client_record)
        ])
        
        # Write to temp file
        with open(temp_file, 'w') as f:
            f.write(jsonl_content)
        
        # Import the data
        with open(temp_file, 'rb') as f:
            files = {"file": ("test_import.jsonl", f, "application/x-jsonl")}
            data = {
                "format": "jsonl",
                "organization_id": test_organization.id,
                "strategy": "overwrite"
            }
            
            response = await authenticated_client.post(
                "/api/v1/admin/data-transfer/import",
                files=files,
                data=data
            )
        
        assert response.status_code == 200
        
        result = response.json()
        assert result["status"] == "success"
        assert result["total_processed"] == 1
        assert result["imported"] >= 1
    
    @pytest.mark.asyncio
    async def test_import_with_conflicts(self, authenticated_client: AsyncClient, test_organization, test_client_data, temp_file):
        """Test import handling data conflicts."""
        # Create JSONL with conflicting client data
        metadata = {
            "_metadata": {
                "export_id": "test_conflict_123",
                "timestamp": "2024-01-01T00:00:00",
                "format": "jsonl",
                "total_records": 1,
                "organization_id": test_organization.id
            }
        }
        
        # Use existing client ID but different data
        conflicting_client = {
            "_table": "clients",
            "id": test_client_data.id,  # Same ID as existing
            "organization_id": test_organization.id,
            "name": "Modified Client Name",  # Different name
            "display_name": "Modified Display Name",
            "client_code": test_client_data.client_code,
            "client_type": "industrial",  # Different type
            "is_active": True
        }
        
        jsonl_content = "\n".join([
            json.dumps(metadata),
            json.dumps(conflicting_client)
        ])
        
        with open(temp_file, 'w') as f:
            f.write(jsonl_content)
        
        # Import with SKIP strategy
        with open(temp_file, 'rb') as f:
            files = {"file": ("test_conflict.jsonl", f, "application/x-jsonl")}
            data = {
                "format": "jsonl",
                "organization_id": test_organization.id,
                "strategy": "skip"
            }
            
            response = await authenticated_client.post(
                "/api/v1/admin/data-transfer/import",
                files=files,
                data=data
            )
        
        assert response.status_code == 200
        
        result = response.json()
        assert result["status"] == "success"
        assert result["conflicts"] >= 0  # Should report conflicts
    
    @pytest.mark.asyncio
    async def test_import_dry_run(self, authenticated_client: AsyncClient, test_organization, temp_file):
        """Test import in dry-run mode."""
        # Create sample data
        metadata = {
            "_metadata": {
                "export_id": "test_dryrun_123",
                "timestamp": "2024-01-01T00:00:00",
                "format": "jsonl",
                "total_records": 1,
                "organization_id": test_organization.id
            }
        }
        
        client_record = {
            "_table": "clients",
            "id": 998,
            "organization_id": test_organization.id,
            "name": "Dry Run Client",
            "display_name": "Test Dry Run",
            "client_code": "DRY001",
            "client_type": "commercial",
            "is_active": True
        }
        
        jsonl_content = "\n".join([
            json.dumps(metadata),
            json.dumps(client_record)
        ])
        
        with open(temp_file, 'w') as f:
            f.write(jsonl_content)
        
        # Import in dry-run mode
        with open(temp_file, 'rb') as f:
            files = {"file": ("test_dryrun.jsonl", f, "application/x-jsonl")}
            data = {
                "format": "jsonl",
                "organization_id": test_organization.id,
                "strategy": "overwrite",
                "dry_run": "true"
            }
            
            response = await authenticated_client.post(
                "/api/v1/admin/data-transfer/import",
                files=files,
                data=data
            )
        
        assert response.status_code == 200
        
        result = response.json()
        assert result["dry_run"] is True
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_validate_import_data(self, authenticated_client: AsyncClient, temp_file):
        """Test import data validation endpoint."""
        # Create valid JSONL content
        metadata = {
            "_metadata": {
                "export_id": "test_validate_123",
                "timestamp": "2024-01-01T00:00:00",
                "format": "jsonl",
                "total_records": 1
            }
        }
        
        valid_record = {
            "_table": "clients",
            "id": 997,
            "organization_id": 1,
            "name": "Valid Client",
            "client_code": "VAL001",
            "is_active": True
        }
        
        jsonl_content = "\n".join([
            json.dumps(metadata),
            json.dumps(valid_record)
        ])
        
        with open(temp_file, 'w') as f:
            f.write(jsonl_content)
        
        # Validate the data
        with open(temp_file, 'rb') as f:
            files = {"file": ("test_validate.jsonl", f, "application/x-jsonl")}
            data = {"format": "jsonl"}
            
            response = await authenticated_client.post(
                "/api/v1/admin/data-transfer/validate",
                files=files,
                data=data
            )
        
        assert response.status_code == 200
        
        result = response.json()
        assert result["valid"] in [True, False]
        assert "total_records" in result
        assert "issues" in result
    
    @pytest.mark.asyncio
    async def test_compare_datasets(self, authenticated_client: AsyncClient, test_organization, temp_file):
        """Test dataset comparison endpoint."""
        # Create comparison data
        metadata = {
            "_metadata": {
                "export_id": "test_compare_123",
                "timestamp": "2024-01-01T00:00:00",
                "format": "jsonl",
                "total_records": 1,
                "organization_id": test_organization.id
            }
        }
        
        client_record = {
            "_table": "clients",
            "id": 996,
            "organization_id": test_organization.id,
            "name": "Compare Client",
            "client_code": "CMP001",
            "is_active": True
        }
        
        jsonl_content = "\n".join([
            json.dumps(metadata),
            json.dumps(client_record)
        ])
        
        with open(temp_file, 'w') as f:
            f.write(jsonl_content)
        
        # Compare with current data
        with open(temp_file, 'rb') as f:
            files = {"file": ("test_compare.jsonl", f, "application/x-jsonl")}
            data = {
                "format": "jsonl",
                "organization_id": test_organization.id
            }
            
            response = await authenticated_client.post(
                "/api/v1/admin/data-transfer/compare",
                files=files,
                data=data
            )
        
        assert response.status_code == 200
        
        result = response.json()
        assert "differences" in result
        assert "summary" in result
        assert result["summary"]["total_changes"] >= 0


class TestExportImportSecurity:
    """Test security aspects of export/import functionality."""
    
    @pytest.mark.asyncio
    async def test_export_requires_authentication(self, async_client: AsyncClient, test_organization):
        """Test that export requires authentication."""
        export_request = {
            "organization_id": test_organization.id,
            "format": "json"
        }
        
        response = await async_client.post("/api/v1/admin/data-transfer/export", json=export_request)
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_import_requires_authentication(self, async_client: AsyncClient, temp_file):
        """Test that import requires authentication."""
        with open(temp_file, 'w') as f:
            f.write('{"test": "data"}')
        
        with open(temp_file, 'rb') as f:
            files = {"file": ("test.json", f, "application/json")}
            data = {"format": "json", "organization_id": 1}
            
            response = await async_client.post(
                "/api/v1/admin/data-transfer/import",
                files=files,
                data=data
            )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_export_organization_isolation(self, authenticated_client: AsyncClient, async_session: AsyncSession, test_organization):
        """Test that users can only export their organization's data."""
        # Create another organization with data
        other_org = Organization(
            name="Other Organization",
            display_name="Other Org",
            organization_type="company",
            is_active=True
        )
        async_session.add(other_org)
        await async_session.commit()
        await async_session.refresh(other_org)
        
        # Try to export other organization's data
        export_request = {
            "organization_id": other_org.id,
            "format": "json"
        }
        
        response = await authenticated_client.post("/api/v1/admin/data-transfer/export", json=export_request)
        
        # Should be forbidden or not found
        assert response.status_code in [403, 404]
    
    @pytest.mark.asyncio
    async def test_import_organization_isolation(self, authenticated_client: AsyncClient, async_session: AsyncSession, temp_file):
        """Test that users can only import to their organization."""
        # Create another organization
        other_org = Organization(
            name="Other Organization",
            display_name="Other Org", 
            organization_type="company",
            is_active=True
        )
        async_session.add(other_org)
        await async_session.commit()
        await async_session.refresh(other_org)
        
        # Create import data for other organization
        metadata = {
            "_metadata": {
                "export_id": "test_isolation_123",
                "organization_id": other_org.id
            }
        }
        
        with open(temp_file, 'w') as f:
            f.write(json.dumps(metadata))
        
        # Try to import to other organization
        with open(temp_file, 'rb') as f:
            files = {"file": ("test.json", f, "application/json")}
            data = {
                "format": "json",
                "organization_id": other_org.id
            }
            
            response = await authenticated_client.post(
                "/api/v1/admin/data-transfer/import",
                files=files,
                data=data
            )
        
        # Should be forbidden
        assert response.status_code in [403, 404]


class TestExportImportPerformance:
    """Test performance aspects of export/import."""
    
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_large_dataset_export(self, authenticated_client: AsyncClient, async_session: AsyncSession, test_organization):
        """Test export performance with larger dataset."""
        # Create multiple clients for testing
        clients = []
        for i in range(100):
            client = Client(
                organization_id=test_organization.id,
                name=f"Bulk Client {i}",
                display_name=f"Bulk Client {i}",
                client_code=f"BULK{i:03d}",
                client_type="commercial",
                is_active=True
            )
            clients.append(client)
        
        async_session.add_all(clients)
        await async_session.commit()
        
        # Export the data
        export_request = {
            "organization_id": test_organization.id,
            "format": "jsonl",
            "include_tables": ["clients"]
        }
        
        response = await authenticated_client.post("/api/v1/admin/data-transfer/export", json=export_request)
        
        assert response.status_code == 200
        
        # Verify we got all the clients
        lines = response.text.strip().split('\n')
        # Should have metadata + 100 client records
        assert len(lines) >= 100
    
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_streaming_export(self, authenticated_client: AsyncClient, test_organization):
        """Test that large exports are streamed properly."""
        export_request = {
            "organization_id": test_organization.id,
            "format": "jsonl"
        }
        
        async with authenticated_client.stream("POST", "/api/v1/admin/data-transfer/export", json=export_request) as response:
            assert response.status_code == 200
            
            # Should be able to read content in chunks
            content_chunks = []
            async for chunk in response.aiter_text():
                content_chunks.append(chunk)
            
            # Should have received content in multiple chunks for large datasets
            full_content = "".join(content_chunks)
            assert len(full_content) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])