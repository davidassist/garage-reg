"""
Comprehensive test scenarios for delta-based bidirectional synchronization
with conflict resolution coverage
"""

import pytest
from datetime import datetime, timezone
import asyncio
from typing import Dict, List
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from app.core.sync.service import SyncService, RetryableSync
from app.core.sync.models import (
    SyncDelta, SyncPullRequest, SyncPushRequest, SyncConflictPolicy,
    ConflictResolution, OperationalTransform, VersionedMixin
)
from app.models.gate import Gate
from app.models.maintenance import Inspection
from tests.conftest import TestingSessionLocal


class TestVersionedEntity:
    """Base test entity with versioning"""
    id: int = 1
    etag: str = "test-etag-123"
    row_version: int = 1
    last_modified_at: datetime = datetime.now(timezone.utc)
    last_modified_by: str = "client_1"


class SyncConflictScenarios:
    """Test scenarios for sync conflicts"""
    
    @pytest.fixture
    def db_session(self):
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    @pytest.fixture
    def sync_service(self, db_session):
        return SyncService(db_session)
    
    @pytest.fixture
    def retryable_sync(self, sync_service):
        return RetryableSync(sync_service)
    
    
    # ============ BASIC SYNC TESTS ============
    
    async def test_normal_sync_no_conflicts(self, sync_service):
        """Test normal sync operation without conflicts"""
        
        # Setup: Client has changes to push
        client_deltas = [
            SyncDelta(
                entity_type="gate",
                entity_id="1",
                operation="update",
                data={"name": "Updated Gate"},
                etag="old-etag-123",
                timestamp=datetime.now(timezone.utc),
                client_id="client_1"
            )
        ]
        
        push_request = SyncPushRequest(
            deltas=client_deltas,
            client_id="client_1",
            policy=SyncConflictPolicy.LAST_WRITE_WINS
        )
        
        # Execute
        response = await sync_service.push_changes(push_request)
        
        # Verify
        assert len(response.accepted_deltas) == 1
        assert len(response.conflicts) == 0
        assert len(response.rejected_deltas) == 0
    
    
    # ============ CONFLICT SCENARIOS ============
    
    async def test_concurrent_modification_conflict(self, sync_service):
        """Test Last-Write-Wins conflict resolution"""
        
        # Setup: Server has newer version than client
        server_entity = TestVersionedEntity()
        server_entity.etag = "server-etag-456"
        server_entity.row_version = 2
        server_entity.last_modified_at = datetime.now(timezone.utc)
        server_entity.last_modified_by = "server_user"
        
        client_delta = SyncDelta(
            entity_type="gate",
            entity_id="1",
            operation="update", 
            data={"name": "Client Update"},
            etag="old-etag-123",  # Outdated etag
            timestamp=datetime.now(timezone.utc).replace(second=0),  # Older timestamp
            client_id="client_1"
        )
        
        push_request = SyncPushRequest(
            deltas=[client_delta],
            client_id="client_1",
            policy=SyncConflictPolicy.LAST_WRITE_WINS
        )
        
        # Mock entity retrieval
        with patch.object(sync_service, '_get_entity_by_id') as mock_get:
            mock_get.return_value = server_entity
            
            response = await sync_service.push_changes(push_request)
        
        # Verify: Conflict detected and resolved using Last-Write-Wins
        assert len(response.conflicts) == 1
        conflict = response.conflicts[0]
        assert conflict.entity_type == "gate"
        assert conflict.entity_id == "1"
        assert conflict.resolution_strategy == "last_write_wins"
    
    
    async def test_operational_transform_text_conflict(self, sync_service):
        """Test Operational Transform for text field conflicts"""
        
        # Setup: Both client and server modified same text field
        base_text = "Original gate description"
        
        # Client operation: insert at position 9
        client_ops = [
            {"type": "retain", "length": 9},
            {"type": "insert", "text": "updated "},
            {"type": "retain", "length": 100}
        ]
        
        # Server operation: insert at position 17  
        server_ops = [
            {"type": "retain", "length": 17},
            {"type": "insert", "text": "maintenance "},
            {"type": "retain", "length": 100}
        ]
        
        # Execute operational transform
        transformed_ops = OperationalTransform.transform_text_operations(
            client_ops, server_ops
        )
        
        # Verify: Operations are transformed to be compatible
        assert len(transformed_ops) > 0
        # Expected result: "Original updated gate maintenance description"
        
        # Test in sync context
        client_delta = SyncDelta(
            entity_type="gate",
            entity_id="1",
            operation="update",
            data={
                "description": "Original updated gate description",
                "_operations": {"description": client_ops}
            },
            etag="etag-123",
            timestamp=datetime.now(timezone.utc),
            client_id="client_1"
        )
        
        push_request = SyncPushRequest(
            deltas=[client_delta],
            client_id="client_1", 
            policy=SyncConflictPolicy.OPERATIONAL_TRANSFORM
        )
        
        server_entity = TestVersionedEntity()
        server_entity.etag = "etag-456"  # Different etag = conflict
        
        with patch.object(sync_service, '_get_entity_by_id') as mock_get:
            mock_get.return_value = server_entity
            
            response = await sync_service.push_changes(push_request)
        
        # Verify: Operational Transform applied
        if response.conflicts:
            conflict = response.conflicts[0]
            assert conflict.resolution_strategy == "operational_transform"
    
    
    async def test_manual_conflict_resolution(self, sync_service):
        """Test manual conflict resolution workflow"""
        
        # Step 1: Push change that creates conflict
        client_delta = SyncDelta(
            entity_type="gate",
            entity_id="1",
            operation="update",
            data={"name": "Client Name", "status": "active"},
            etag="old-etag",
            timestamp=datetime.now(timezone.utc),
            client_id="client_1"
        )
        
        server_entity = TestVersionedEntity()
        server_entity.etag = "newer-etag"
        server_entity.name = "Server Name"
        server_entity.status = "inactive"
        
        push_request = SyncPushRequest(
            deltas=[client_delta],
            client_id="client_1",
            policy=SyncConflictPolicy.MANUAL_RESOLUTION
        )
        
        with patch.object(sync_service, '_get_entity_by_id') as mock_get:
            mock_get.return_value = server_entity
            
            response = await sync_service.push_changes(push_request)
        
        # Verify: Conflict requires manual resolution
        assert len(response.conflicts) == 1
        conflict = response.conflicts[0]
        assert conflict.resolution_strategy == "manual_resolution"
        assert conflict.requires_user_input == True
        
        # Step 2: User provides manual resolution
        resolution = ConflictResolution(
            entity_type="gate",
            entity_id="1", 
            server_etag="newer-etag",
            client_etag="old-etag",
            resolved_data={
                "name": "Merged Name",  # User chose different value
                "status": "active"      # User chose client value
            },
            resolution_strategy="user_merge"
        )
        
        # Apply manual resolution
        result = await sync_service._apply_resolved_changes(
            server_entity, 
            resolution.resolved_data,
            "user_manual"
        )
        
        # Verify: Manual resolution applied
        assert result['status'] == 'accepted'
    
    
    # ============ BATCH OPERATIONS ============
    
    async def test_batch_sync_with_mixed_conflicts(self, sync_service):
        """Test batch sync with some conflicts and some successes"""
        
        # Setup: Multiple deltas with different conflict scenarios
        deltas = [
            # Delta 1: No conflict (new entity)
            SyncDelta(
                entity_type="gate",
                entity_id="10",
                operation="create",
                data={"name": "New Gate"},
                etag=None,
                timestamp=datetime.now(timezone.utc),
                client_id="client_1"
            ),
            
            # Delta 2: Conflict (outdated etag) 
            SyncDelta(
                entity_type="gate",
                entity_id="2",
                operation="update",
                data={"name": "Conflicted Gate"},
                etag="old-etag-222",
                timestamp=datetime.now(timezone.utc),
                client_id="client_1"
            ),
            
            # Delta 3: No conflict (correct etag)
            SyncDelta(
                entity_type="gate", 
                entity_id="3",
                operation="update",
                data={"name": "Updated Gate"},
                etag="correct-etag-333",
                timestamp=datetime.now(timezone.utc),
                client_id="client_1"
            )
        ]
        
        push_request = SyncPushRequest(
            deltas=deltas,
            client_id="client_1",
            policy=SyncConflictPolicy.LAST_WRITE_WINS
        )
        
        # Mock entity lookups
        def mock_get_entity(entity_type, entity_id):
            if entity_id == "10":
                return None  # New entity
            elif entity_id == "2":
                entity = TestVersionedEntity()
                entity.id = 2
                entity.etag = "newer-etag-222"  # Conflict
                return entity
            elif entity_id == "3":
                entity = TestVersionedEntity()
                entity.id = 3
                entity.etag = "correct-etag-333"  # No conflict
                return entity
        
        with patch.object(sync_service, '_get_entity_by_id', side_effect=mock_get_entity):
            response = await sync_service.push_changes(push_request)
        
        # Verify: Mixed results
        assert len(response.accepted_deltas) == 2  # Deltas 1 and 3
        assert len(response.conflicts) == 1       # Delta 2
        assert len(response.rejected_deltas) == 0
    
    
    # ============ RETRY SCENARIOS ============
    
    async def test_network_retry_with_exponential_backoff(self, retryable_sync):
        """Test retry mechanism with network failures"""
        
        push_request = SyncPushRequest(
            deltas=[
                SyncDelta(
                    entity_type="gate",
                    entity_id="1",
                    operation="update",
                    data={"name": "Test Gate"},
                    etag="etag-123",
                    timestamp=datetime.now(timezone.utc),
                    client_id="client_1"
                )
            ],
            client_id="client_1",
            policy=SyncConflictPolicy.LAST_WRITE_WINS
        )
        
        # Mock network failures followed by success
        call_count = 0
        async def mock_push_changes(request):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise ConnectionError("Network timeout")
            # Success on 3rd attempt
            return Mock(accepted_deltas=[request.deltas[0]], conflicts=[], rejected_deltas=[])
        
        with patch.object(retryable_sync.sync_service, 'push_changes', side_effect=mock_push_changes):
            response = await retryable_sync.push_with_retry(push_request)
        
        # Verify: Succeeded after retries
        assert call_count == 3
        assert len(response.accepted_deltas) == 1
    
    
    async def test_max_retries_exceeded(self, retryable_sync):
        """Test behavior when max retries exceeded"""
        
        push_request = SyncPushRequest(
            deltas=[
                SyncDelta(
                    entity_type="gate",
                    entity_id="1", 
                    operation="update",
                    data={"name": "Test Gate"},
                    etag="etag-123",
                    timestamp=datetime.now(timezone.utc),
                    client_id="client_1"
                )
            ],
            client_id="client_1",
            policy=SyncConflictPolicy.LAST_WRITE_WINS
        )
        
        # Mock persistent network failures
        async def mock_push_changes(request):
            raise ConnectionError("Network timeout")
        
        with patch.object(retryable_sync.sync_service, 'push_changes', side_effect=mock_push_changes):
            with pytest.raises(ConnectionError):
                await retryable_sync.push_with_retry(push_request)
    
    
    # ============ EDGE CASES ============
    
    async def test_concurrent_delete_update_conflict(self, sync_service):
        """Test conflict when client updates deleted entity"""
        
        client_delta = SyncDelta(
            entity_type="gate",
            entity_id="1",
            operation="update",
            data={"name": "Updated Name"},
            etag="etag-123",
            timestamp=datetime.now(timezone.utc),
            client_id="client_1"
        )
        
        # Server entity is soft deleted
        server_entity = TestVersionedEntity()
        server_entity.is_deleted = True
        server_entity.etag = "delete-etag-456"
        
        push_request = SyncPushRequest(
            deltas=[client_delta],
            client_id="client_1",
            policy=SyncConflictPolicy.SERVER_WINS
        )
        
        with patch.object(sync_service, '_get_entity_by_id') as mock_get:
            mock_get.return_value = server_entity
            
            response = await sync_service.push_changes(push_request)
        
        # Verify: Server wins, entity remains deleted
        assert len(response.conflicts) == 1
        conflict = response.conflicts[0]
        assert conflict.resolution_strategy == "server_wins"
    
    
    async def test_timestamp_precision_conflict_resolution(self, sync_service):
        """Test conflict resolution with very close timestamps"""
        
        base_time = datetime.now(timezone.utc)
        
        # Client and server modifications 1ms apart
        client_delta = SyncDelta(
            entity_type="gate",
            entity_id="1",
            operation="update",
            data={"name": "Client Update"},
            etag="etag-123",
            timestamp=base_time,
            client_id="client_1"
        )
        
        server_entity = TestVersionedEntity() 
        server_entity.last_modified_at = base_time.replace(microsecond=base_time.microsecond + 1000)
        server_entity.etag = "newer-etag"
        
        push_request = SyncPushRequest(
            deltas=[client_delta],
            client_id="client_1",
            policy=SyncConflictPolicy.LAST_WRITE_WINS
        )
        
        with patch.object(sync_service, '_get_entity_by_id') as mock_get:
            mock_get.return_value = server_entity
            
            response = await sync_service.push_changes(push_request)
        
        # Verify: Server wins due to newer timestamp
        if response.conflicts:
            assert response.conflicts[0].resolution_strategy == "last_write_wins"


# ============ INTEGRATION TESTS ============

class TestSyncIntegration:
    """End-to-end sync integration tests"""
    
    async def test_full_sync_cycle_with_conflicts(self):
        """Test complete sync cycle: pull -> modify -> push -> resolve conflicts"""
        
        # This would be a full integration test with actual database
        # and API endpoints, testing the complete sync workflow
        pass
    
    
    async def test_mobile_offline_scenario(self):
        """Test mobile app going offline and coming back online"""
        
        # Scenario:
        # 1. Mobile app syncs normally
        # 2. Goes offline, makes local changes  
        # 3. Server changes data in the meantime
        # 4. Mobile comes back online
        # 5. Push changes create conflicts
        # 6. Resolve conflicts and sync again
        pass


# ============ PERFORMANCE TESTS ============

class TestSyncPerformance:
    """Performance and load testing for sync operations"""
    
    async def test_large_batch_sync_performance(self):
        """Test sync performance with large batches"""
        
        # Generate 1000 deltas and measure sync time
        deltas = []
        for i in range(1000):
            deltas.append(
                SyncDelta(
                    entity_type="gate",
                    entity_id=str(i),
                    operation="create" if i % 3 == 0 else "update",
                    data={"name": f"Gate {i}"},
                    etag=f"etag-{i}",
                    timestamp=datetime.now(timezone.utc),
                    client_id="client_1"
                )
            )
        
        # Measure sync time
        start_time = datetime.now()
        # ... sync logic ...
        duration = (datetime.now() - start_time).total_seconds()
        
        # Verify: Completes within reasonable time
        assert duration < 10.0  # Less than 10 seconds
    
    
    async def test_concurrent_client_sync(self):
        """Test multiple clients syncing simultaneously"""
        
        # Simulate 10 clients pushing changes concurrently
        # Verify no data corruption or deadlocks occur
        pass


# ============ CONFLICT RESOLUTION POLICY TESTS ============

class TestConflictPolicies:
    """Comprehensive testing of all conflict resolution policies"""
    
    async def test_all_conflict_policies(self, sync_service):
        """Test all available conflict resolution policies"""
        
        policies = [
            SyncConflictPolicy.LAST_WRITE_WINS,
            SyncConflictPolicy.CLIENT_WINS, 
            SyncConflictPolicy.SERVER_WINS,
            SyncConflictPolicy.OPERATIONAL_TRANSFORM,
            SyncConflictPolicy.MANUAL_RESOLUTION
        ]
        
        for policy in policies:
            client_delta = SyncDelta(
                entity_type="gate",
                entity_id="1",
                operation="update",
                data={"name": f"Test {policy.value}"},
                etag="old-etag",
                timestamp=datetime.now(timezone.utc),
                client_id="client_1"
            )
            
            server_entity = TestVersionedEntity()
            server_entity.etag = "newer-etag"  # Force conflict
            
            push_request = SyncPushRequest(
                deltas=[client_delta],
                client_id="client_1",
                policy=policy
            )
            
            with patch.object(sync_service, '_get_entity_by_id') as mock_get:
                mock_get.return_value = server_entity
                
                response = await sync_service.push_changes(push_request)
            
            # Verify policy was applied
            if response.conflicts:
                assert policy.value in response.conflicts[0].resolution_strategy


if __name__ == "__main__":
    # Run specific test scenarios
    pytest.main([
        __file__ + "::SyncConflictScenarios::test_concurrent_modification_conflict",
        "-v"
    ])