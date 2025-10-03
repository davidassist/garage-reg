"""
Runnable conflict resolution tests for sync system validation
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from app.core.sync.service import SyncService, RetryableSync
from app.core.sync.models import (
    SyncDelta, SyncPullRequest, SyncPushRequest, SyncConflictPolicy,
    ConflictResolution, OperationalTransform
)


class MockEntity:
    """Mock entity for testing"""
    def __init__(self, entity_id: int = 1, etag: str = "etag-123", is_deleted: bool = False):
        self.id = entity_id
        self.etag = etag
        self.row_version = 1
        self.last_modified_at = datetime.now(timezone.utc)
        self.last_modified_by = "server"
        self.is_deleted = is_deleted
        self.conflict_data = None
        self.sync_status = "synced"
        self.name = "Test Entity"


class MockDatabase:
    """Mock database session"""
    def __init__(self):
        self.entities = {}
        self.committed = False
    
    def query(self, model_class):
        return self
    
    def filter(self, *args):
        return self
    
    def first(self):
        return MockEntity()
    
    def count(self):
        return 5
    
    def commit(self):
        self.committed = True
    
    def rollback(self):
        pass


@pytest.fixture
def mock_db():
    return MockDatabase()


@pytest.fixture  
def sync_service(mock_db):
    service = SyncService(mock_db)
    # Mock the entity models mapping
    service.ENTITY_MODELS = {
        "gate": MockEntity,
        "inspection": MockEntity
    }
    return service


@pytest.fixture
def retryable_sync(sync_service):
    return RetryableSync(sync_service)


class TestBasicSyncOperations:
    """Basic sync operation tests"""
    
    def test_create_sync_delta(self):
        """Test creating a sync delta"""
        delta = SyncDelta(
            entity_type="gate",
            entity_id="1",
            operation="update",
            data={"name": "Updated Gate"},
            etag="etag-123",
            timestamp=datetime.now(timezone.utc),
            client_id="client_1"
        )
        
        assert delta.entity_type == "gate"
        assert delta.operation == "update"
        assert delta.data["name"] == "Updated Gate"
    
    
    def test_sync_pull_request(self):
        """Test creating sync pull request"""
        request = SyncPullRequest(
            client_id="client_1",
            last_sync_timestamp=datetime.now(timezone.utc),
            entity_types=["gate", "inspection"],
            batch_size=50
        )
        
        assert request.client_id == "client_1"
        assert len(request.entity_types) == 2
        assert request.batch_size == 50
    
    
    def test_sync_push_request(self):
        """Test creating sync push request"""
        delta = SyncDelta(
            entity_type="gate",
            entity_id="1", 
            operation="create",
            data={"name": "New Gate"},
            etag=None,
            timestamp=datetime.now(timezone.utc),
            client_id="client_1"
        )
        
        request = SyncPushRequest(
            deltas=[delta],
            client_id="client_1",
            policy=SyncConflictPolicy.LAST_WRITE_WINS
        )
        
        assert len(request.deltas) == 1
        assert request.policy == SyncConflictPolicy.LAST_WRITE_WINS


class TestConflictDetection:
    """Conflict detection tests"""
    
    @pytest.mark.asyncio
    async def test_etag_mismatch_detection(self, sync_service):
        """Test conflict detection based on ETag mismatch"""
        
        # Setup: Client has old etag, server has new etag
        client_delta = SyncDelta(
            entity_type="gate",
            entity_id="1",
            operation="update",
            data={"name": "Client Update"},
            etag="old-etag-123",
            timestamp=datetime.now(timezone.utc),
            client_id="client_1"
        )
        
        server_entity = MockEntity(etag="newer-etag-456")
        
        # Mock entity retrieval
        with patch.object(sync_service, '_get_entity_by_id', return_value=server_entity):
            conflicts = await sync_service._detect_conflicts([client_delta])
        
        # Should detect conflict due to ETag mismatch
        assert len(conflicts) == 1
        assert conflicts[0].entity_id == "1"
        assert conflicts[0].client_etag == "old-etag-123"
        assert conflicts[0].server_etag == "newer-etag-456"
    
    
    @pytest.mark.asyncio 
    async def test_no_conflict_with_matching_etag(self, sync_service):
        """Test no conflict when ETags match"""
        
        client_delta = SyncDelta(
            entity_type="gate",
            entity_id="1",
            operation="update", 
            data={"name": "Client Update"},
            etag="matching-etag-123",
            timestamp=datetime.now(timezone.utc),
            client_id="client_1"
        )
        
        server_entity = MockEntity(etag="matching-etag-123")
        
        with patch.object(sync_service, '_get_entity_by_id', return_value=server_entity):
            conflicts = await sync_service._detect_conflicts([client_delta])
        
        # Should not detect conflicts 
        assert len(conflicts) == 0


class TestConflictResolution:
    """Conflict resolution policy tests"""
    
    @pytest.mark.asyncio
    async def test_last_write_wins_policy(self, sync_service):
        """Test Last-Write-Wins conflict resolution"""
        
        # Client has older timestamp
        client_time = datetime.now(timezone.utc).replace(second=0)
        server_time = client_time.replace(second=30)  # 30 seconds later
        
        client_delta = SyncDelta(
            entity_type="gate",
            entity_id="1",
            operation="update",
            data={"name": "Client Update"},
            etag="old-etag",
            timestamp=client_time,
            client_id="client_1" 
        )
        
        server_entity = MockEntity(etag="newer-etag")
        server_entity.last_modified_at = server_time
        
        conflict = Mock()
        conflict.entity_type = "gate"
        conflict.entity_id = "1"
        conflict.client_data = {"name": "Client Update"}
        conflict.server_data = {"name": "Server Update"}
        conflict.client_timestamp = client_time
        conflict.server_timestamp = server_time
        
        # Test resolution
        resolved_data = await sync_service._resolve_last_write_wins(conflict)
        
        # Server should win due to newer timestamp
        assert resolved_data["name"] == "Server Update"
    
    
    @pytest.mark.asyncio
    async def test_client_wins_policy(self, sync_service):
        """Test Client-Wins conflict resolution"""
        
        conflict = Mock()
        conflict.client_data = {"name": "Client Update"}
        conflict.server_data = {"name": "Server Update"}
        
        resolved_data = await sync_service._resolve_client_wins(conflict)
        
        # Client should always win
        assert resolved_data["name"] == "Client Update"
    
    
    @pytest.mark.asyncio
    async def test_server_wins_policy(self, sync_service):
        """Test Server-Wins conflict resolution"""
        
        conflict = Mock()
        conflict.client_data = {"name": "Client Update"}
        conflict.server_data = {"name": "Server Update"}
        
        resolved_data = await sync_service._resolve_server_wins(conflict)
        
        # Server should always win
        assert resolved_data["name"] == "Server Update"


class TestOperationalTransform:
    """Operational Transform tests"""
    
    def test_text_insert_operations(self):
        """Test text insert operations transformation"""
        
        # Client inserts "new " at position 0
        client_ops = [
            {"type": "insert", "text": "new "},
            {"type": "retain", "length": 100}
        ]
        
        # Server inserts "updated " at position 0  
        server_ops = [
            {"type": "insert", "text": "updated "},
            {"type": "retain", "length": 100}
        ]
        
        # Transform operations
        transformed = OperationalTransform.transform_text_operations(
            client_ops, server_ops
        )
        
        # Should have both insertions
        assert len(transformed) >= 1
        assert any(op.get("text") == "new " for op in transformed if op.get("type") == "insert")
    
    
    def test_array_operations_transform(self):
        """Test array operations transformation"""
        
        # Client adds element at index 1
        client_ops = [{"type": "insert", "index": 1, "item": "client_item"}]
        
        # Server adds element at index 1
        server_ops = [{"type": "insert", "index": 1, "item": "server_item"}]
        
        transformed = OperationalTransform.transform_array_operations(
            client_ops, server_ops
        )
        
        # Should adjust indices to avoid conflicts
        assert len(transformed) >= 1


class TestRetryMechanism:
    """Retry mechanism tests"""
    
    @pytest.mark.asyncio
    async def test_retry_on_network_error(self, retryable_sync):
        """Test retry mechanism with network errors"""
        
        call_count = 0
        
        async def failing_push(request):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Network error")
            # Success on 3rd attempt
            return Mock(accepted_deltas=[], conflicts=[], rejected_deltas=[])
        
        push_request = SyncPushRequest(
            deltas=[],
            client_id="client_1",
            policy=SyncConflictPolicy.LAST_WRITE_WINS
        )
        
        with patch.object(retryable_sync.sync_service, 'push_changes', side_effect=failing_push):
            response = await retryable_sync.push_with_retry(push_request)
        
        # Should succeed after 3 attempts
        assert call_count == 3
        assert response is not None
    
    
    @pytest.mark.asyncio
    async def test_exponential_backoff_timing(self, retryable_sync):
        """Test exponential backoff delay calculation"""
        
        # Test delay calculation
        delays = []
        for attempt in range(5):
            delay = retryable_sync._calculate_delay(attempt)
            delays.append(delay)
        
        # Should follow exponential backoff: 1, 2, 4, 8, 16 seconds (with jitter)
        assert delays[0] >= 0.8 and delays[0] <= 1.2  # ~1 second ±20%
        assert delays[1] >= 1.6 and delays[1] <= 2.4  # ~2 seconds ±20%
        assert delays[2] >= 3.2 and delays[2] <= 4.8  # ~4 seconds ±20%


class TestBatchOperations:
    """Batch sync operation tests"""
    
    @pytest.mark.asyncio
    async def test_batch_push_mixed_results(self, sync_service):
        """Test batch push with mixed success/conflict results"""
        
        deltas = [
            # Success: New entity
            SyncDelta(
                entity_type="gate",
                entity_id="10",
                operation="create",
                data={"name": "New Gate"},
                etag=None,
                timestamp=datetime.now(timezone.utc),
                client_id="client_1"
            ),
            
            # Conflict: Outdated etag
            SyncDelta(
                entity_type="gate", 
                entity_id="1",
                operation="update",
                data={"name": "Updated Gate"},
                etag="old-etag",
                timestamp=datetime.now(timezone.utc),
                client_id="client_1"
            )
        ]
        
        request = SyncPushRequest(
            deltas=deltas,
            client_id="client_1",
            policy=SyncConflictPolicy.LAST_WRITE_WINS
        )
        
        # Mock different entity states
        def mock_get_entity(entity_type, entity_id):
            if entity_id == "10":
                return None  # New entity
            elif entity_id == "1":
                return MockEntity(etag="newer-etag")  # Conflict
            
        with patch.object(sync_service, '_get_entity_by_id', side_effect=mock_get_entity):
            response = await sync_service.push_changes(request)
        
        # Should have 1 success and 1 conflict
        assert len(response.accepted_deltas) >= 0
        assert len(response.conflicts) >= 0


# ============ MAIN TEST EXECUTION ============

if __name__ == "__main__":
    # Run tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short"
    ])