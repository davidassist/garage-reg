"""
API endpoints for delta-based synchronization
"""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Header, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_user
from app.core.rbac import require_permission, PermissionActions, Resources
from app.models.auth import User
from app.core.sync.service import SyncService, RetryableSync
from app.core.sync.models import (
    SyncPullRequest, SyncPullResponse, SyncPushRequest, SyncPushResponse,
    ConflictResolution, SyncConflictPolicy, SyncMetrics
)

router = APIRouter(prefix="/sync", tags=["synchronization"])


@router.post("/pull", response_model=SyncPullResponse)
@require_permission(Resources.SYNC, PermissionActions.READ)
async def pull_changes(
    request: SyncPullRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    user_agent: Optional[str] = Header(None)
):
    """
    Pull changes from server since last sync
    
    Supports:
    - Delta-based incremental sync
    - Batch operations with pagination
    - Conflict detection
    - Entity type filtering
    - Soft delete handling
    """
    sync_service = SyncService(db)
    retryable_sync = RetryableSync(sync_service)
    
    try:
        # Add user context to request
        request.client_id = f"{current_user.id}_{request.client_id}"
        
        response = await retryable_sync.pull_with_retry(request)
        
        # Log sync activity
        await _log_sync_activity(
            db, current_user.id, "pull", 
            len(response.deltas), len(response.conflicts),
            user_agent
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sync pull failed: {str(e)}"
        )


@router.post("/push", response_model=SyncPushResponse)
@require_permission(Resources.SYNC, PermissionActions.UPDATE)
async def push_changes(
    request: SyncPushRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    user_agent: Optional[str] = Header(None)
):
    """
    Push client changes to server
    
    Features:
    - Optimistic locking with ETag validation
    - Automatic conflict resolution
    - Batch processing with partial success
    - Transactional consistency
    """
    sync_service = SyncService(db)
    retryable_sync = RetryableSync(sync_service)
    
    try:
        # Add user context to request
        request.client_id = f"{current_user.id}_{request.client_id}"
        
        response = await retryable_sync.push_with_retry(request)
        
        # Log sync activity
        await _log_sync_activity(
            db, current_user.id, "push",
            len(request.deltas), len(response.conflicts),
            user_agent
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sync push failed: {str(e)}"
        )


@router.post("/resolve-conflict")
@require_permission(Resources.SYNC, PermissionActions.UPDATE)
async def resolve_conflict(
    resolution: ConflictResolution,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Manually resolve a sync conflict
    
    Applies user-provided conflict resolution and updates the entity
    """
    sync_service = SyncService(db)
    
    try:
        # Get the conflicted entity
        model_class = sync_service.ENTITY_MODELS.get(resolution.entity_type)
        if not model_class:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown entity type: {resolution.entity_type}"
            )
        
        entity = db.query(model_class).filter(
            model_class.id == int(resolution.entity_id)
        ).first()
        
        if not entity:
            raise HTTPException(
                status_code=404,
                detail=f"Entity {resolution.entity_id} not found"
            )
        
        # Verify the conflict still exists
        if entity.etag != resolution.server_etag:
            raise HTTPException(
                status_code=409,
                detail="Conflict already resolved or entity changed"
            )
        
        # Apply the resolution
        result = await sync_service._apply_resolved_changes(
            entity,
            resolution.resolved_data,
            f"user_{current_user.id}"
        )
        
        if result['status'] == 'accepted':
            db.commit()
            return {"message": "Conflict resolved successfully"}
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to apply resolution: {result.get('details')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Conflict resolution failed: {str(e)}"
        )


@router.get("/status")
@require_permission(Resources.SYNC, PermissionActions.READ)
async def get_sync_status(
    entity_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get sync status and statistics
    """
    sync_service = SyncService(db)
    
    try:
        # Get basic stats
        stats = {
            "server_timestamp": datetime.now(),
            "user_id": current_user.id,
            "sync_policies": {
                "default_conflict_policy": SyncConflictPolicy.LAST_WRITE_WINS.value,
                "available_policies": [policy.value for policy in SyncConflictPolicy]
            }
        }
        
        # Entity-specific stats
        if entity_type:
            model_class = sync_service.ENTITY_MODELS.get(entity_type)
            if model_class:
                total_entities = db.query(model_class).count()
                pending_sync = db.query(model_class).filter(
                    model_class.sync_status == 'pending'
                ).count()
                conflicts = db.query(model_class).filter(
                    model_class.conflict_data.isnot(None)
                ).count()
                
                stats["entity_stats"] = {
                    "entity_type": entity_type,
                    "total_entities": total_entities,
                    "pending_sync": pending_sync,
                    "conflicts": conflicts
                }
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sync status: {str(e)}"
        )


@router.get("/conflicts")
@require_permission(Resources.SYNC, PermissionActions.READ)
async def get_conflicts(
    entity_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get list of unresolved conflicts
    """
    sync_service = SyncService(db)
    
    try:
        conflicts = []
        
        for entity_type_key, model_class in sync_service.ENTITY_MODELS.items():
            if entity_type and entity_type != entity_type_key:
                continue
            
            conflicted_entities = db.query(model_class).filter(
                model_class.conflict_data.isnot(None)
            ).offset(offset).limit(limit).all()
            
            for entity in conflicted_entities:
                conflict_info = {
                    "entity_type": entity_type_key,
                    "entity_id": str(entity.id),
                    "etag": entity.etag,
                    "last_modified_at": entity.last_modified_at,
                    "last_modified_by": entity.last_modified_by,
                    "conflict_data": entity.conflict_data
                }
                conflicts.append(conflict_info)
        
        return {
            "conflicts": conflicts,
            "total": len(conflicts),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get conflicts: {str(e)}"
        )


@router.post("/batch/pull", response_model=List[SyncPullResponse])
@require_permission(Resources.SYNC, PermissionActions.READ)
async def batch_pull_changes(
    requests: List[SyncPullRequest],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Batch pull multiple entity types or time ranges
    """
    sync_service = SyncService(db)
    retryable_sync = RetryableSync(sync_service)
    
    responses = []
    
    for request in requests:
        try:
            request.client_id = f"{current_user.id}_{request.client_id}"
            response = await retryable_sync.pull_with_retry(request)
            responses.append(response)
        except Exception as e:
            # Continue with other requests even if one fails
            error_response = SyncPullResponse(
                deltas=[],
                server_timestamp=datetime.now(),
                has_more=False,
                conflicts=[]
            )
            responses.append(error_response)
    
    return responses


@router.post("/batch/push", response_model=List[SyncPushResponse])
@require_permission(Resources.SYNC, PermissionActions.UPDATE)
async def batch_push_changes(
    requests: List[SyncPushRequest],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Batch push multiple change sets
    """
    sync_service = SyncService(db)
    retryable_sync = RetryableSync(sync_service)
    
    responses = []
    
    for request in requests:
        try:
            request.client_id = f"{current_user.id}_{request.client_id}"
            response = await retryable_sync.push_with_retry(request)
            responses.append(response)
        except Exception as e:
            # Continue with other requests even if one fails
            error_response = SyncPushResponse(
                accepted_deltas=[],
                rejected_deltas=[{
                    'etag': delta.etag,
                    'reason': 'batch_error',
                    'details': str(e)
                } for delta in request.deltas],
                conflicts=[],
                server_timestamp=datetime.now()
            )
            responses.append(error_response)
    
    return responses


@router.get("/metrics")
@require_permission(Resources.SYNC, PermissionActions.READ)
async def get_sync_metrics(
    client_id: Optional[str] = None,
    since_hours: int = 24,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get sync performance metrics
    """
    sync_service = SyncService(db)
    
    since_timestamp = datetime.now().replace(
        hour=datetime.now().hour - since_hours
    )
    
    full_client_id = f"{current_user.id}_{client_id}" if client_id else None
    
    metrics = await sync_service.get_sync_metrics(
        full_client_id or f"user_{current_user.id}",
        since_timestamp
    )
    
    return metrics


async def _log_sync_activity(
    db: Session,
    user_id: int,
    operation: str,
    delta_count: int,
    conflict_count: int,
    user_agent: Optional[str]
):
    """
    Log sync activity for monitoring and analytics
    """
    # In a real implementation, this would insert into an audit log table
    pass


# Background task for cleaning up old tombstone records
@router.post("/cleanup")
@require_permission(Resources.SYNC, PermissionActions.ADMIN)
async def cleanup_tombstones(
    background_tasks: BackgroundTasks,
    older_than_days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Clean up old tombstone records (soft deleted items)
    
    Removes records that have been soft deleted for more than specified days
    """
    def cleanup_task():
        sync_service = SyncService(db)
        
        cutoff_date = datetime.now().replace(
            day=datetime.now().day - older_than_days
        )
        
        total_cleaned = 0
        
        for entity_type, model_class in sync_service.ENTITY_MODELS.items():
            deleted_count = db.query(model_class).filter(
                model_class.is_deleted == True,
                model_class.last_modified_at < cutoff_date
            ).delete()
            
            total_cleaned += deleted_count
        
        db.commit()
        
        return {"cleaned_records": total_cleaned}
    
    background_tasks.add_task(cleanup_task)
    
    return {"message": f"Cleanup task scheduled for records older than {older_than_days} days"}