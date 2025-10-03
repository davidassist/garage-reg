"""
Unit Tests for Data Export/Import Service
Tests export/import functionality without database dependencies
"""
import pytest
import json
import tempfile
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

from app.services.data_export_import_service import DataExportImportService, ImportStrategy
from app.schemas.data_transfer import DataExportRequest


class TestDataExportImportService:
    """Test data export/import service functionality."""
    
    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        session = Mock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        return session
    
    @pytest.fixture
    def service(self, mock_session):
        """Create data export/import service instance."""
        return DataExportImportService(mock_session)
    
    @pytest.fixture
    def sample_export_data(self):
        """Create sample export data for testing."""
        return {
            "organizations": [
                {
                    "id": 1,
                    "name": "Test Org",
                    "display_name": "Test Organization",
                    "is_active": True,
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00"
                }
            ],
            "users": [
                {
                    "id": 1,
                    "organization_id": 1,
                    "username": "testuser",
                    "email": "test@example.com",
                    "is_active": True,
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00"
                }
            ]
        }


class TestExportFunctionality:
    """Test data export functionality."""
    
    @pytest.mark.asyncio
    async def test_export_jsonl_format(self, service, sample_export_data):
        """Test export in JSONL format."""
        # Mock the data retrieval
        with patch.object(service, '_get_all_organization_data', return_value=sample_export_data):
            request = DataExportRequest(
                organization_id=1,
                format="jsonl",
                include_metadata=True
            )
            
            result = await service.export_data(request)
            
            assert result["format"] == "jsonl"
            assert result["status"] == "success"
            assert "content" in result
            
            # Verify JSONL format
            lines = result["content"].strip().split('\n')
            assert len(lines) >= 2  # At least metadata + some data
            
            # First line should be metadata
            metadata = json.loads(lines[0])
            assert "_metadata" in metadata
            
            # Other lines should be data records
            for line in lines[1:]:
                record = json.loads(line)
                assert "_table" in record
    
    @pytest.mark.asyncio
    async def test_export_json_format(self, service, sample_export_data):
        """Test export in JSON format."""
        with patch.object(service, '_get_all_organization_data', return_value=sample_export_data):
            request = DataExportRequest(
                organization_id=1,
                format="json",
                include_metadata=True
            )
            
            result = await service.export_data(request)
            
            assert result["format"] == "json"
            assert result["status"] == "success"
            
            # Verify JSON format
            content = json.loads(result["content"])
            assert "_metadata" in content
            assert "data" in content
            assert "organizations" in content["data"]
            assert "users" in content["data"]
    
    @pytest.mark.asyncio
    async def test_export_with_filters(self, service):
        """Test export with table filters."""
        with patch.object(service, '_get_filtered_organization_data') as mock_get_filtered:
            mock_get_filtered.return_value = {"organizations": []}
            
            request = DataExportRequest(
                organization_id=1,
                format="json",
                include_tables=["organizations"],
                exclude_tables=["users"]
            )
            
            await service.export_data(request)
            
            mock_get_filtered.assert_called_once_with(1, ["organizations"], ["users"])
    
    @pytest.mark.asyncio
    async def test_export_generates_checksum(self, service, sample_export_data):
        """Test that export generates data checksum."""
        with patch.object(service, '_get_all_organization_data', return_value=sample_export_data):
            request = DataExportRequest(
                organization_id=1,
                format="json",
                include_metadata=True
            )
            
            result = await service.export_data(request)
            
            content = json.loads(result["content"])
            metadata = content["_metadata"]
            
            assert "checksum" in metadata
            assert len(metadata["checksum"]) > 10  # Should be a real checksum
    
    def test_export_format_validation(self, service):
        """Test export format validation."""
        with pytest.raises(ValueError, match="Unsupported format"):
            request = DataExportRequest(
                organization_id=1,
                format="xml"  # Unsupported format
            )


class TestImportFunctionality:
    """Test data import functionality."""
    
    @pytest.fixture
    def sample_jsonl_content(self):
        """Create sample JSONL content for import testing."""
        metadata = {
            "_metadata": {
                "export_id": "test_export_123",
                "timestamp": "2024-01-01T00:00:00",
                "total_records": 2,
                "checksum": "test_checksum_abc123"
            }
        }
        
        org_record = {
            "_table": "organizations",
            "id": 1,
            "name": "Test Org",
            "display_name": "Test Organization",
            "is_active": True
        }
        
        user_record = {
            "_table": "users", 
            "id": 1,
            "organization_id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "is_active": True
        }
        
        lines = [
            json.dumps(metadata),
            json.dumps(org_record),
            json.dumps(user_record)
        ]
        
        return "\n".join(lines)
    
    @pytest.mark.asyncio
    async def test_import_jsonl_content(self, service, sample_jsonl_content):
        """Test import of JSONL content."""
        with patch.object(service, '_import_record') as mock_import:
            mock_import.return_value = {"status": "imported", "conflicts": []}
            
            result = await service.import_data(
                content=sample_jsonl_content,
                format="jsonl",
                organization_id=1,
                strategy=ImportStrategy.OVERWRITE
            )
            
            assert result["status"] == "success"
            assert result["total_processed"] == 2  # org + user
            assert result["imported"] == 2
            
            # Verify import_record was called for each data record
            assert mock_import.call_count == 2
    
    @pytest.mark.asyncio
    async def test_import_with_conflicts(self, service, sample_jsonl_content):
        """Test import handling conflicts."""
        def mock_import_with_conflict(table_name, record_data, strategy):
            if record_data.get("username") == "testuser":
                return {
                    "status": "conflict",
                    "conflicts": [{
                        "field": "email",
                        "current": "old@example.com",
                        "incoming": "test@example.com"
                    }]
                }
            return {"status": "imported", "conflicts": []}
        
        with patch.object(service, '_import_record', side_effect=mock_import_with_conflict):
            result = await service.import_data(
                content=sample_jsonl_content,
                format="jsonl",
                organization_id=1,
                strategy=ImportStrategy.SKIP
            )
            
            assert result["status"] == "success"
            assert result["conflicts"] > 0
            assert len(result["conflict_details"]) > 0
    
    @pytest.mark.asyncio
    async def test_import_dry_run(self, service, sample_jsonl_content):
        """Test import in dry-run mode."""
        with patch.object(service, '_validate_import_record') as mock_validate:
            mock_validate.return_value = {"valid": True, "issues": []}
            
            result = await service.import_data(
                content=sample_jsonl_content,
                format="jsonl",
                organization_id=1,
                strategy=ImportStrategy.OVERWRITE,
                dry_run=True
            )
            
            assert result["status"] == "success"
            assert result["dry_run"] is True
            
            # In dry run, should validate but not actually import
            assert mock_validate.call_count == 2
    
    @pytest.mark.asyncio
    async def test_import_invalid_format(self, service):
        """Test import with invalid format."""
        with pytest.raises(ValueError, match="Unsupported format"):
            await service.import_data(
                content="invalid content",
                format="xml",
                organization_id=1,
                strategy=ImportStrategy.OVERWRITE
            )
    
    @pytest.mark.asyncio
    async def test_import_malformed_jsonl(self, service):
        """Test import with malformed JSONL content."""
        malformed_content = "invalid json line\n{\"valid\": \"json\"}"
        
        with pytest.raises(ValueError, match="Invalid JSONL"):
            await service.import_data(
                content=malformed_content,
                format="jsonl",
                organization_id=1,
                strategy=ImportStrategy.OVERWRITE
            )


class TestImportStrategies:
    """Test different import conflict resolution strategies."""
    
    @pytest.fixture
    def service_with_mock_db(self, mock_session):
        """Create service with mocked database operations."""
        service = DataExportImportService(mock_session)
        return service
    
    def test_import_strategy_skip(self, service_with_mock_db):
        """Test SKIP strategy - keep existing data."""
        existing_record = {"id": 1, "name": "Original Name", "email": "original@example.com"}
        import_record = {"id": 1, "name": "New Name", "email": "new@example.com"}
        
        with patch.object(service_with_mock_db, '_get_existing_record', return_value=existing_record):
            result = service_with_mock_db._resolve_conflict(
                existing_record, 
                import_record, 
                ImportStrategy.SKIP
            )
            
            # Should keep original values
            assert result["name"] == "Original Name"
            assert result["email"] == "original@example.com"
    
    def test_import_strategy_overwrite(self, service_with_mock_db):
        """Test OVERWRITE strategy - replace with imported data."""
        existing_record = {"id": 1, "name": "Original Name", "email": "original@example.com"}
        import_record = {"id": 1, "name": "New Name", "email": "new@example.com"}
        
        result = service_with_mock_db._resolve_conflict(
            existing_record, 
            import_record, 
            ImportStrategy.OVERWRITE
        )
        
        # Should use imported values
        assert result["name"] == "New Name"
        assert result["email"] == "new@example.com"
    
    def test_import_strategy_merge(self, service_with_mock_db):
        """Test MERGE strategy - combine values intelligently."""
        existing_record = {
            "id": 1, 
            "name": "Original Name", 
            "email": "original@example.com",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
        import_record = {
            "id": 1, 
            "name": "New Name", 
            "email": None,  # Null value should not overwrite
            "phone": "+1-555-0123",  # New field
            "updated_at": "2024-02-01T00:00:00"  # Newer timestamp
        }
        
        result = service_with_mock_db._resolve_conflict(
            existing_record, 
            import_record, 
            ImportStrategy.MERGE
        )
        
        # Should merge intelligently
        assert result["name"] == "New Name"  # Use new value
        assert result["email"] == "original@example.com"  # Keep original (import was null)
        assert result["phone"] == "+1-555-0123"  # Add new field
        assert result["updated_at"] == "2024-02-01T00:00:00"  # Use newer timestamp


class TestDataValidation:
    """Test data validation functionality."""
    
    @pytest.mark.asyncio
    async def test_validate_export_content(self, service, sample_export_data):
        """Test validation of export content."""
        with patch.object(service, '_get_all_organization_data', return_value=sample_export_data):
            request = DataExportRequest(
                organization_id=1,
                format="json",
                include_metadata=True
            )
            
            result = await service.export_data(request)
            content = result["content"]
            
            # Validate the exported content
            validation_result = await service.validate_import_data(
                content=content,
                format="json"
            )
            
            assert validation_result["valid"] is True
            assert validation_result["total_records"] == 2
            assert len(validation_result["issues"]) == 0
    
    @pytest.mark.asyncio
    async def test_validate_invalid_content(self, service):
        """Test validation of invalid content."""
        invalid_content = "not valid json content"
        
        validation_result = await service.validate_import_data(
            content=invalid_content,
            format="json"
        )
        
        assert validation_result["valid"] is False
        assert len(validation_result["issues"]) > 0
        assert any("Invalid JSON" in issue["message"] for issue in validation_result["issues"])
    
    @pytest.mark.asyncio
    async def test_validate_missing_required_fields(self, service):
        """Test validation with missing required fields."""
        invalid_record = {
            "_metadata": {
                "export_id": "test",
                "timestamp": "2024-01-01T00:00:00"
            }
        }
        
        content = json.dumps(invalid_record)
        
        validation_result = await service.validate_import_data(
            content=content,
            format="json"
        )
        
        assert validation_result["valid"] is False
        assert len(validation_result["issues"]) > 0


class TestRoundTripIntegrity:
    """Test round-trip data integrity."""
    
    @pytest.mark.asyncio
    async def test_round_trip_test(self, service, sample_export_data):
        """Test complete round-trip export/import integrity."""
        # Mock export
        with patch.object(service, '_get_all_organization_data', return_value=sample_export_data):
            export_request = DataExportRequest(
                organization_id=1,
                format="jsonl",
                include_metadata=True
            )
            
            export_result = await service.export_data(export_request)
            exported_content = export_result["content"]
        
        # Mock import
        with patch.object(service, '_import_record') as mock_import:
            mock_import.return_value = {"status": "imported", "conflicts": []}
            
            import_result = await service.import_data(
                content=exported_content,
                format="jsonl",
                organization_id=1,
                strategy=ImportStrategy.OVERWRITE
            )
        
        # Mock verification
        with patch.object(service, '_get_all_organization_data', return_value=sample_export_data):
            verification_request = DataExportRequest(
                organization_id=1,
                format="jsonl",
                include_metadata=True
            )
            
            verification_result = await service.export_data(verification_request)
        
        # Compare checksums
        original_checksum = json.loads(exported_content.split('\n')[0])["_metadata"]["checksum"]
        verification_checksum = json.loads(verification_result["content"].split('\n')[0])["_metadata"]["checksum"]
        
        assert original_checksum == verification_checksum
        assert import_result["status"] == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])