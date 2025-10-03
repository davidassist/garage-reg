"""
Delta-based synchronization service with conflict resolution
"""
import json
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, text, desc
import asyncio
import logging

from .models import (
    SyncDelta, SyncPullRequest, SyncPullResponse, SyncPushRequest, SyncPushResponse,
    ConflictResolution, SyncConflictPolicy, SyncOperation, OperationalTransform,
    SyncMetrics
)
from ...models.organization import Gate
from ...models.inspections import Inspection, InspectionItem
from ...models.auth import User

logger = logging.getLogger(__name__)


class SyncService:
    """
    Delta-based bidirectional synchronization service
    
    Features:
    - ETag-based optimistic locking
    - Row version tracking
    - Conflict detection and resolution
    - Batch operations with retry logic
    - Exponential backoff for network failures
    """
    
    # Entity type mapping
    ENTITY_MODELS = {
        'gate': Gate,
        'inspection': Inspection,
        'inspection_item': InspectionItem,
    }
    
    def __init__(self, db: Session):
        self.db = db
        self.retry_delays = [1, 2, 4, 8, 16, 30]  # Exponential backoff seconds
    
    async def pull_changes(self, request: SyncPullRequest) -> SyncPullResponse:
        """
        Pull changes from server since last sync
        
        Returns deltas with conflict detection
        """
        start_time = datetime.now()
        
        try:
            # Get changes since last sync timestamp
            deltas = await self._get_changes_since(
                request.last_sync_timestamp,
                request.entity_types,
                request.batch_size,
                request.include_deleted
            )
            
            # Detect potential conflicts
            conflicts = await self._detect_pull_conflicts(deltas, request.client_id)
            
            server_timestamp = datetime.now(timezone.utc)
            
            # Check if there are more changes
            has_more = len(deltas) >= request.batch_size
            next_cursor = None
            if has_more and deltas:
                next_cursor = f"{deltas[-1].last_modified_at.isoformat()}_{deltas[-1].entity_id}"
            
            logger.info(
                f"Pull sync completed: {len(deltas)} deltas, {len(conflicts)} conflicts",
                extra={
                    'client_id': request.client_id,
                    'delta_count': len(deltas),
                    'conflict_count': len(conflicts),
                    'duration_ms': (datetime.now() - start_time).total_seconds() * 1000
                }
            )
            
            return SyncPullResponse(
                deltas=deltas,
                server_timestamp=server_timestamp,
                has_more=has_more,
                next_cursor=next_cursor,
                conflicts=conflicts
            )
            
        except Exception as e:
            logger.error(f"Pull sync failed: {str(e)}", extra={'client_id': request.client_id})
            raise
    
    async def push_changes(self, request: SyncPushRequest) -> SyncPushResponse:
        """
        Push client changes to server with conflict resolution
        """
        start_time = datetime.now()
        accepted_deltas = []
        rejected_deltas = []
        conflicts = []
        
        try:
            for delta in request.deltas:
                try:
                    result = await self._process_push_delta(delta, request.client_id)
                    
                    if result['status'] == 'accepted':
                        accepted_deltas.append(delta.etag)
                    elif result['status'] == 'rejected':
                        rejected_deltas.append({
                            'etag': delta.etag,
                            'reason': result['reason'],
                            'details': result.get('details')
                        })
                    elif result['status'] == 'conflict':
                        conflicts.append(result['server_delta'])
                        
                except Exception as e:
                    logger.error(
                        f"Failed to process delta {delta.etag}: {str(e)}",
                        extra={'client_id': request.client_id, 'delta_etag': delta.etag}
                    )
                    rejected_deltas.append({
                        'etag': delta.etag,
                        'reason': 'processing_error',
                        'details': str(e)
                    })
            
            # Commit all accepted changes
            self.db.commit()
            
            server_timestamp = datetime.now(timezone.utc)
            
            logger.info(
                f"Push sync completed: {len(accepted_deltas)} accepted, "
                f"{len(rejected_deltas)} rejected, {len(conflicts)} conflicts",
                extra={
                    'client_id': request.client_id,
                    'accepted_count': len(accepted_deltas),
                    'rejected_count': len(rejected_deltas),
                    'conflict_count': len(conflicts),
                    'duration_ms': (datetime.now() - start_time).total_seconds() * 1000
                }
            )
            
            return SyncPushResponse(
                accepted_deltas=accepted_deltas,
                rejected_deltas=rejected_deltas,
                conflicts=conflicts,
                server_timestamp=server_timestamp
            )
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Push sync failed: {str(e)}", extra={'client_id': request.client_id})
            raise
    
    async def _get_changes_since(
        self,
        since_timestamp: Optional[datetime],
        entity_types: Optional[List[str]],
        batch_size: int,
        include_deleted: bool
    ) -> List[SyncDelta]:
        """
        Get entity changes since timestamp
        """
        deltas = []
        
        # Default to 1 hour ago if no timestamp provided
        if since_timestamp is None:
            since_timestamp = datetime.now(timezone.utc).replace(hour=datetime.now().hour - 1)
        
        for entity_type, model_class in self.ENTITY_MODELS.items():
            if entity_types and entity_type not in entity_types:
                continue
            
            # Build query conditions
            conditions = [model_class.last_modified_at > since_timestamp]
            
            if not include_deleted:
                conditions.append(model_class.is_deleted == False)
            
            # Query entities with changes
            query = (
                self.db.query(model_class)
                .filter(and_(*conditions))
                .order_by(model_class.last_modified_at, model_class.id)
                .limit(batch_size)
            )
            
            entities = query.all()
            
            for entity in entities:
                operation = SyncOperation.DELETE if entity.is_deleted else (
                    SyncOperation.CREATE if entity.row_version == 1 else SyncOperation.UPDATE
                )
                
                delta = SyncDelta(
                    entity_type=entity_type,
                    entity_id=str(entity.id),
                    operation=operation,
                    etag=entity.etag,
                    row_version=entity.row_version,
                    last_modified_at=entity.last_modified_at,
                    last_modified_by=entity.last_modified_by,
                    data=self._serialize_entity(entity) if not entity.is_deleted else None,
                    conflict_data=json.loads(entity.conflict_data) if entity.conflict_data else None
                )
                
                deltas.append(delta)
                
                if len(deltas) >= batch_size:
                    break
            
            if len(deltas) >= batch_size:
                break
        
        return sorted(deltas, key=lambda d: (d.last_modified_at, d.entity_id))
    
    async def _detect_pull_conflicts(self, deltas: List[SyncDelta], client_id: str) -> List[SyncDelta]:
        """
        Detect conflicts between server deltas and client state
        """
        conflicts = []
        
        # In a real implementation, you would check client-side ETags
        # For now, we'll return conflicts marked on the server
        for delta in deltas:
            if delta.conflict_data:
                conflicts.append(delta)
        
        return conflicts
    
    async def _process_push_delta(self, delta: SyncDelta, client_id: str) -> Dict[str, Any]:
        """
        Process a single push delta with conflict detection
        """
        model_class = self.ENTITY_MODELS.get(delta.entity_type)
        if not model_class:
            return {
                'status': 'rejected',
                'reason': 'unknown_entity_type',
                'details': f'Entity type {delta.entity_type} not supported'
            }
        
        try:
            # Find existing entity
            existing_entity = self.db.query(model_class).filter(
                model_class.id == int(delta.entity_id)
            ).first()
            
            if delta.operation == SyncOperation.CREATE:
                return await self._process_create_delta(delta, model_class, existing_entity, client_id)
            elif delta.operation == SyncOperation.UPDATE:
                return await self._process_update_delta(delta, model_class, existing_entity, client_id)
            elif delta.operation == SyncOperation.DELETE:
                return await self._process_delete_delta(delta, model_class, existing_entity, client_id)
            else:
                return {
                    'status': 'rejected',
                    'reason': 'unknown_operation',
                    'details': f'Operation {delta.operation} not supported'
                }
                
        except Exception as e:
            logger.error(f"Error processing delta {delta.etag}: {str(e)}")
            return {
                'status': 'rejected',
                'reason': 'processing_error',
                'details': str(e)
            }
    
    async def _process_create_delta(
        self, 
        delta: SyncDelta, 
        model_class, 
        existing_entity,
        client_id: str
    ) -> Dict[str, Any]:
        """Process CREATE operation"""
        
        if existing_entity and not existing_entity.is_deleted:
            # Entity already exists - conflict
            server_delta = self._create_server_delta(existing_entity, delta.entity_type)
            return {
                'status': 'conflict',
                'server_delta': server_delta,
                'reason': 'entity_already_exists'
            }
        
        # Create new entity
        try:
            entity_data = delta.data.copy()
            entity_data.update({
                'etag': str(uuid.uuid4()),
                'row_version': 1,
                'last_modified_at': datetime.now(timezone.utc),
                'last_modified_by': f'client_{client_id}',
                'sync_status': 'synced',
                'is_deleted': False
            })
            
            new_entity = model_class(**entity_data)
            self.db.add(new_entity)
            self.db.flush()  # Get ID without committing
            
            return {'status': 'accepted'}
            
        except Exception as e:
            return {
                'status': 'rejected',
                'reason': 'create_failed',
                'details': str(e)
            }
    
    async def _process_update_delta(
        self,
        delta: SyncDelta,
        model_class,
        existing_entity,
        client_id: str
    ) -> Dict[str, Any]:
        """Process UPDATE operation with conflict detection"""
        
        if not existing_entity or existing_entity.is_deleted:
            return {
                'status': 'rejected',
                'reason': 'entity_not_found',
                'details': f'Entity {delta.entity_id} not found or deleted'
            }
        
        # Check for conflicts using ETag
        if existing_entity.etag != delta.etag:
            # ETag mismatch - conflict detected
            server_delta = self._create_server_delta(existing_entity, delta.entity_type)
            
            # Attempt automatic conflict resolution
            resolution_result = await self._resolve_conflict(
                delta, 
                server_delta, 
                SyncConflictPolicy.LAST_WRITE_WINS  # Default policy
            )
            
            if resolution_result['status'] == 'resolved':
                # Apply resolved changes
                return await self._apply_resolved_changes(
                    existing_entity, 
                    resolution_result['resolved_data'],
                    f'client_{client_id}'
                )
            else:
                # Manual resolution required
                return {
                    'status': 'conflict',
                    'server_delta': server_delta,
                    'reason': 'etag_mismatch'
                }
        
        # No conflict - apply changes
        try:
            for key, value in delta.data.items():
                if hasattr(existing_entity, key) and key not in ['id', 'etag', 'row_version']:
                    setattr(existing_entity, key, value)
            
            # Update sync metadata
            existing_entity.etag = str(uuid.uuid4())
            existing_entity.row_version += 1
            existing_entity.last_modified_at = datetime.now(timezone.utc)
            existing_entity.last_modified_by = f'client_{client_id}'
            existing_entity.sync_status = 'synced'
            
            return {'status': 'accepted'}
            
        except Exception as e:
            return {
                'status': 'rejected',
                'reason': 'update_failed',
                'details': str(e)
            }
    
    async def _process_delete_delta(
        self,
        delta: SyncDelta,
        model_class,
        existing_entity,
        client_id: str
    ) -> Dict[str, Any]:
        """Process DELETE operation"""
        
        if not existing_entity:
            # Already deleted or never existed
            return {'status': 'accepted'}
        
        if existing_entity.is_deleted:
            # Already deleted
            return {'status': 'accepted'}
        
        # Check for conflicts
        if existing_entity.etag != delta.etag:
            server_delta = self._create_server_delta(existing_entity, delta.entity_type)
            return {
                'status': 'conflict',
                'server_delta': server_delta,
                'reason': 'etag_mismatch'
            }
        
        # Perform soft delete
        try:
            existing_entity.is_deleted = True
            existing_entity.etag = str(uuid.uuid4())
            existing_entity.row_version += 1
            existing_entity.last_modified_at = datetime.now(timezone.utc)
            existing_entity.last_modified_by = f'client_{client_id}'
            existing_entity.sync_status = 'synced'
            
            return {'status': 'accepted'}
            
        except Exception as e:
            return {
                'status': 'rejected',
                'reason': 'delete_failed',
                'details': str(e)
            }
    
    async def _resolve_conflict(
        self,
        client_delta: SyncDelta,
        server_delta: SyncDelta,
        policy: SyncConflictPolicy
    ) -> Dict[str, Any]:
        """
        Resolve conflict using specified policy
        """
        
        if policy == SyncConflictPolicy.LAST_WRITE_WINS:
            if client_delta.last_modified_at > server_delta.last_modified_at:
                return {
                    'status': 'resolved',
                    'resolved_data': client_delta.data,
                    'winner': 'client'
                }
            else:
                return {
                    'status': 'resolved',
                    'resolved_data': server_delta.data,
                    'winner': 'server'
                }
        
        elif policy == SyncConflictPolicy.CLIENT_WINS:
            return {
                'status': 'resolved',
                'resolved_data': client_delta.data,
                'winner': 'client'
            }
        
        elif policy == SyncConflictPolicy.SERVER_WINS:
            return {
                'status': 'resolved',
                'resolved_data': server_delta.data,
                'winner': 'server'
            }
        
        elif policy == SyncConflictPolicy.OPERATIONAL_TRANSFORM:
            # Simplified OT implementation
            try:
                base_data = {}  # In real implementation, get common ancestor
                merged_data, conflicts = OperationalTransform.merge_object_changes(
                    client_delta.data,
                    server_delta.data,
                    base_data
                )
                
                if not conflicts:
                    return {
                        'status': 'resolved',
                        'resolved_data': merged_data,
                        'winner': 'merged'
                    }
                else:
                    return {
                        'status': 'manual_required',
                        'conflicts': conflicts,
                        'suggested_data': merged_data
                    }
                    
            except Exception as e:
                logger.error(f"OT resolution failed: {str(e)}")
                return {
                    'status': 'manual_required',
                    'reason': 'ot_failed',
                    'error': str(e)
                }
        
        else:  # MANUAL_RESOLUTION
            return {
                'status': 'manual_required',
                'reason': 'manual_policy'
            }
    
    async def _apply_resolved_changes(
        self,
        entity,
        resolved_data: Dict[str, Any],
        modified_by: str
    ) -> Dict[str, Any]:
        """Apply resolved conflict changes to entity"""
        
        try:
            for key, value in resolved_data.items():
                if hasattr(entity, key) and key not in ['id', 'etag', 'row_version']:
                    setattr(entity, key, value)
            
            # Update sync metadata
            entity.etag = str(uuid.uuid4())
            entity.row_version += 1
            entity.last_modified_at = datetime.now(timezone.utc)
            entity.last_modified_by = modified_by
            entity.sync_status = 'synced'
            entity.conflict_data = None  # Clear conflict data
            
            return {'status': 'accepted'}
            
        except Exception as e:
            return {
                'status': 'rejected',
                'reason': 'resolution_failed',
                'details': str(e)
            }
    
    def _create_server_delta(self, entity, entity_type: str) -> SyncDelta:
        """Create SyncDelta from server entity"""
        
        operation = SyncOperation.DELETE if entity.is_deleted else (
            SyncOperation.CREATE if entity.row_version == 1 else SyncOperation.UPDATE
        )
        
        return SyncDelta(
            entity_type=entity_type,
            entity_id=str(entity.id),
            operation=operation,
            etag=entity.etag,
            row_version=entity.row_version,
            last_modified_at=entity.last_modified_at,
            last_modified_by=entity.last_modified_by,
            data=self._serialize_entity(entity) if not entity.is_deleted else None,
            conflict_data=json.loads(entity.conflict_data) if entity.conflict_data else None
        )
    
    def _serialize_entity(self, entity) -> Dict[str, Any]:
        """Serialize entity to dictionary for sync"""
        
        # Get all columns except sync metadata
        exclude_fields = {
            'etag', 'row_version', 'last_modified_at', 'last_modified_by',
            'sync_status', 'conflict_data', 'is_deleted'
        }
        
        data = {}
        for column in entity.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(entity, column.name)
                if isinstance(value, datetime):
                    value = value.isoformat()
                data[column.name] = value
        
        return data
    
    async def get_sync_metrics(self, client_id: str, since: datetime) -> SyncMetrics:
        """Get sync operation metrics"""
        
        # This would query sync audit logs in a real implementation
        return SyncMetrics(
            total_deltas=0,
            successful_syncs=0,
            conflicts=0,
            errors=0,
            sync_duration_ms=0,
            network_retries=0
        )


class RetryableSync:
    """
    Wrapper for sync operations with exponential backoff retry logic
    """
    
    def __init__(self, sync_service: SyncService):
        self.sync_service = sync_service
        self.max_retries = 5
        self.base_delay = 1.0  # Base delay in seconds
        self.max_delay = 300.0  # Max delay in seconds
        self.backoff_multiplier = 2.0
    
    async def pull_with_retry(self, request: SyncPullRequest) -> SyncPullResponse:
        """Pull changes with exponential backoff retry"""
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await self.sync_service.pull_changes(request)
                
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = min(
                        self.base_delay * (self.backoff_multiplier ** attempt),
                        self.max_delay
                    )
                    
                    logger.warning(
                        f"Pull sync attempt {attempt + 1} failed, retrying in {delay}s: {str(e)}",
                        extra={'client_id': request.client_id, 'attempt': attempt + 1}
                    )
                    
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"Pull sync failed after {self.max_retries + 1} attempts",
                        extra={'client_id': request.client_id}
                    )
                    break
        
        raise last_exception
    
    async def push_with_retry(self, request: SyncPushRequest) -> SyncPushResponse:
        """Push changes with exponential backoff retry"""
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await self.sync_service.push_changes(request)
                
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = min(
                        self.base_delay * (self.backoff_multiplier ** attempt),
                        self.max_delay
                    )
                    
                    logger.warning(
                        f"Push sync attempt {attempt + 1} failed, retrying in {delay}s: {str(e)}",
                        extra={'client_id': request.client_id, 'attempt': attempt + 1}
                    )
                    
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"Push sync failed after {self.max_retries + 1} attempts",
                        extra={'client_id': request.client_id}
                    )
                    break
        
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay"""
        return min(
            self.base_delay * (self.backoff_multiplier ** attempt),
            self.max_delay
        )