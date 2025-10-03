"""
Delta-based bidirectional sync system with conflict resolution
"""
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean
from sqlalchemy.ext.declarative import declared_attr


class SyncConflictPolicy(str, Enum):
    """Conflict resolution policies"""
    LAST_WRITE_WINS = "last_write_wins"
    OPERATIONAL_TRANSFORM = "operational_transform"
    MANUAL_RESOLUTION = "manual_resolution"
    CLIENT_WINS = "client_wins"
    SERVER_WINS = "server_wins"


class SyncOperation(str, Enum):
    """Sync operation types"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    RESTORE = "restore"


class VersionedMixin:
    """
    Mixin for entities that support delta sync
    
    Provides:
    - ETag for optimistic locking
    - Row version for change tracking  
    - Last modified timestamp with timezone
    - Sync metadata
    """
    
    @declared_attr
    def etag(cls):
        """Entity tag for optimistic locking (UUID-based)"""
        return Column(String(36), nullable=False, index=True)
    
    @declared_attr 
    def row_version(cls):
        """Row version counter for change detection"""
        return Column(Integer, nullable=False, default=1, index=True)
    
    @declared_attr
    def last_modified_at(cls):
        """Last modification timestamp (UTC)"""
        return Column(DateTime(timezone=True), nullable=False, 
                     default=lambda: datetime.now(timezone.utc), 
                     index=True)
    
    @declared_attr
    def last_modified_by(cls):
        """User who last modified this record"""
        return Column(String(100), nullable=True)
    
    @declared_attr
    def sync_status(cls):
        """Sync status: synced, pending, conflict, deleted"""
        return Column(String(20), nullable=False, default='synced', index=True)
    
    @declared_attr
    def conflict_data(cls):
        """JSON data for conflict resolution"""
        return Column(Text, nullable=True)
    
    @declared_attr
    def is_deleted(cls):
        """Soft delete flag for tombstone records"""
        return Column(Boolean, nullable=False, default=False, index=True)


# Sync Delta Models
class SyncDelta(BaseModel):
    """
    Represents a single change in the sync delta
    """
    entity_type: str
    entity_id: str
    operation: SyncOperation
    etag: Optional[str] = None
    row_version: Optional[int] = None
    last_modified_at: Optional[datetime] = None
    last_modified_by: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    conflict_data: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    client_id: Optional[str] = None


class SyncPullRequest(BaseModel):
    """
    Client request for pulling changes from server
    """
    client_id: str
    last_sync_timestamp: Optional[datetime] = None
    entity_types: Optional[List[str]] = None  # Filter specific entities
    batch_size: int = 100
    include_deleted: bool = True


class SyncPullResponse(BaseModel):
    """
    Server response with changes to pull
    """
    deltas: List[SyncDelta]
    server_timestamp: datetime
    has_more: bool = False
    next_cursor: Optional[str] = None
    conflicts: List[SyncDelta] = []


class SyncPushRequest(BaseModel):
    """
    Client request for pushing changes to server
    """
    client_id: str
    deltas: List[SyncDelta]
    client_timestamp: Optional[datetime] = None
    policy: Optional[SyncConflictPolicy] = SyncConflictPolicy.LAST_WRITE_WINS


class SyncPushResponse(BaseModel):
    """
    Server response to push request
    """
    accepted_deltas: List[str]  # ETags of accepted changes
    rejected_deltas: List[Dict[str, Any]]  # ETags with rejection reasons
    conflicts: List[SyncDelta]  # Server versions that conflict
    server_timestamp: datetime


class ConflictResolution(BaseModel):
    """
    Conflict resolution data
    """
    entity_type: str
    entity_id: str
    client_etag: str
    server_etag: str
    resolution_policy: SyncConflictPolicy
    resolved_data: Dict[str, Any]
    resolved_by: str
    resolved_at: datetime


class SyncMetrics(BaseModel):
    """
    Sync operation metrics
    """
    total_deltas: int
    successful_syncs: int
    conflicts: int
    errors: int
    sync_duration_ms: int
    network_retries: int


# Operational Transform Functions
class OperationalTransform:
    """
    Operational Transform implementation for conflict resolution
    
    Supports:
    - Text field transforms (insert, delete, retain)
    - Array field transforms (insert, remove, move) 
    - Object field transforms (set, unset, merge)
    """
    
    @staticmethod
    def transform_text_operations(client_ops: List[Dict], server_ops: List[Dict]) -> List[Dict]:
        """
        Transform text operations using operational transform
        
        Operations format:
        - retain(n): keep n characters
        - insert(str): insert string
        - delete(n): delete n characters
        """
        # Simplified OT implementation
        # In production, use a library like ShareJS or Yjs
        
        transformed_ops = []
        client_pos = 0
        server_pos = 0
        
        for client_op in client_ops:
            if client_op['type'] == 'retain':
                transformed_ops.append(client_op)
                client_pos += client_op['length']
            elif client_op['type'] == 'insert':
                # Insert operations are preserved
                transformed_ops.append(client_op)
            elif client_op['type'] == 'delete':
                # Delete operations may need adjustment
                # Check for conflicts with server operations
                conflict_adjusted = client_op.copy()
                for server_op in server_ops:
                    if (server_op['type'] == 'insert' and 
                        server_pos <= client_pos <= server_pos + len(server_op.get('text', ''))):
                        # Adjust delete position
                        conflict_adjusted['offset'] = client_op.get('offset', 0) + len(server_op.get('text', ''))
                
                transformed_ops.append(conflict_adjusted)
                client_pos += client_op.get('length', 0)
        
        return transformed_ops
    
    @staticmethod
    def transform_array_operations(client_ops: List[Dict], server_ops: List[Dict]) -> List[Dict]:
        """
        Transform array operations
        
        Operations format:
        - insert(index, items): insert items at index
        - remove(index, count): remove count items at index  
        - move(from, to, count): move count items from index to index
        """
        transformed_ops = []
        
        for client_op in client_ops:
            transformed_op = client_op.copy()
            
            # Adjust indices based on server operations
            for server_op in server_ops:
                if server_op['type'] == 'insert':
                    server_index = server_op['index']
                    client_index = client_op.get('index', 0)
                    
                    if server_index <= client_index:
                        transformed_op['index'] = client_index + len(server_op.get('items', []))
                
                elif server_op['type'] == 'remove':
                    server_index = server_op['index']
                    server_count = server_op.get('count', 1)
                    client_index = client_op.get('index', 0)
                    
                    if server_index < client_index:
                        # Adjust for removed items
                        adjustment = min(server_count, client_index - server_index)
                        transformed_op['index'] = max(server_index, client_index - adjustment)
            
            transformed_ops.append(transformed_op)
        
        return transformed_ops
    
    @staticmethod
    def merge_object_changes(client_data: Dict, server_data: Dict, base_data: Dict) -> Dict:
        """
        Three-way merge for object changes
        """
        merged = base_data.copy()
        
        # Apply non-conflicting changes from both sides
        for key, value in client_data.items():
            if key not in server_data or server_data[key] == base_data.get(key):
                merged[key] = value
        
        for key, value in server_data.items():
            if key not in client_data or client_data[key] == base_data.get(key):
                merged[key] = value
        
        # Handle conflicts (both sides changed the same field)
        conflicts = []
        for key in set(client_data.keys()) & set(server_data.keys()):
            if (client_data[key] != base_data.get(key) and 
                server_data[key] != base_data.get(key) and
                client_data[key] != server_data[key]):
                
                conflicts.append({
                    'field': key,
                    'client_value': client_data[key],
                    'server_value': server_data[key],
                    'base_value': base_data.get(key)
                })
                
                # Default to server wins for conflicts
                merged[key] = server_data[key]
        
        return merged, conflicts


# Sync Policies Documentation
SYNC_POLICIES_DOC = """
# Sync Conflict Resolution Policies

## 1. Last Write Wins (LWW)
- **Policy**: `LAST_WRITE_WINS`  
- **Description**: The change with the latest timestamp wins
- **Use Case**: Simple scenarios where temporal ordering is sufficient
- **Pros**: Simple, deterministic, no user intervention needed
- **Cons**: May lose valid concurrent changes

## 2. Operational Transform (OT)
- **Policy**: `OPERATIONAL_TRANSFORM`
- **Description**: Merge concurrent changes using operational transformation
- **Use Case**: Collaborative editing, complex data structures
- **Pros**: Preserves all changes, mathematically sound
- **Cons**: Complex implementation, may need user guidance

## 3. Manual Resolution
- **Policy**: `MANUAL_RESOLUTION`
- **Description**: Present conflicts to user for manual resolution
- **Use Case**: Critical data where accuracy is paramount
- **Pros**: User has full control, preserves data integrity
- **Cons**: Requires user intervention, may block sync

## 4. Client Wins
- **Policy**: `CLIENT_WINS`
- **Description**: Client changes always override server changes
- **Use Case**: Offline-first scenarios, user preference priority
- **Pros**: Respects user intent, good for mobile apps
- **Cons**: May overwrite important server-side changes

## 5. Server Wins  
- **Policy**: `SERVER_WINS`
- **Description**: Server changes always override client changes
- **Use Case**: Server-authoritative scenarios, data validation
- **Pros**: Ensures server consistency, good for validation
- **Cons**: May discard user work, poor offline experience

## Field-Level Resolution Matrix

| Field Type | Default Policy | Alternative Policies |
|------------|----------------|---------------------|
| Text Content | Operational Transform | Last Write Wins, Manual |
| Numbers/Dates | Last Write Wins | Manual, Server Wins |
| Status Fields | Server Wins | Last Write Wins, Manual |
| User Preferences | Client Wins | Last Write Wins |
| System Fields | Server Wins | - |

## Implementation Guidelines

### Timestamp Comparison
```python
def is_newer(timestamp1: datetime, timestamp2: datetime) -> bool:
    # Use microsecond precision for tie-breaking
    return timestamp1 > timestamp2

def resolve_lw_conflict(client_delta: SyncDelta, server_delta: SyncDelta) -> SyncDelta:
    if client_delta.last_modified_at > server_delta.last_modified_at:
        return client_delta
    elif client_delta.last_modified_at < server_delta.last_modified_at:
        return server_delta
    else:
        # Tie-breaker: use entity ID lexicographic order
        return client_delta if client_delta.entity_id < server_delta.entity_id else server_delta
```

### Operational Transform Flow
```python
def resolve_ot_conflict(client_delta: SyncDelta, server_delta: SyncDelta, base_data: Dict) -> SyncDelta:
    # Extract operations from deltas
    client_ops = extract_operations(base_data, client_delta.data)
    server_ops = extract_operations(base_data, server_delta.data)
    
    # Transform operations
    transformed_ops = OperationalTransform.transform_operations(client_ops, server_ops)
    
    # Apply transformed operations
    merged_data = apply_operations(base_data, transformed_ops)
    
    # Create resolved delta
    return create_resolved_delta(client_delta, server_delta, merged_data)
```
"""


class SyncMetrics(BaseModel):
    """Sync performance metrics"""
    client_id: str
    total_pulls: int
    total_pushes: int
    total_conflicts: int
    resolved_conflicts: int
    average_pull_time: float  # seconds
    average_push_time: float  # seconds
    last_sync_timestamp: Optional[datetime]
    error_count: int
    retry_count: int