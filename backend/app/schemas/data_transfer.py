"""
Pydantic schemas for Data Export/Import API
Pydantic sémák az adatok export/import API-hoz
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

from app.services.data_export_import_service import ExportFormat, ImportStrategy, ConflictType


class DataExportRequest(BaseModel):
    """Request schema for data export."""
    format: ExportFormat = Field(default=ExportFormat.JSONL, description="Export format")
    organization_id: Optional[int] = Field(default=None, description="Organization ID for tenant filtering")
    tables: Optional[List[str]] = Field(default=None, description="Specific tables to export (all if not specified)")
    include_tenant_filter: bool = Field(default=True, description="Apply organization filtering")
    
    class Config:
        use_enum_values = True


class ExportMetadataResponse(BaseModel):
    """Export metadata response schema."""
    export_id: str
    timestamp: datetime
    format: ExportFormat
    total_records: int
    total_tables: int
    organization_id: Optional[int]
    exported_by: str
    version: str
    checksum: str
    
    class Config:
        use_enum_values = True


class DataExportResponse(BaseModel):
    """Response schema for data export."""
    success: bool
    export_id: str
    format: ExportFormat
    total_records: int
    total_tables: int
    checksum: str
    data: Optional[Union[str, bytes]] = Field(default=None, description="Export data (may be null for large exports)")
    metadata: ExportMetadataResponse
    message: Optional[str] = Field(default=None)
    
    class Config:
        use_enum_values = True


class ImportConflictResponse(BaseModel):
    """Import conflict response schema."""
    table: str
    record_id: str
    conflict_type: ConflictType
    message: str
    resolution: Optional[str] = None
    
    class Config:
        use_enum_values = True


class DataImportResponse(BaseModel):
    """Response schema for data import."""
    success: bool
    message: str
    total_records: int
    imported_records: int
    skipped_records: int
    error_records: int
    validation_errors: List[str] = Field(default_factory=list)
    conflicts: List[ImportConflictResponse] = Field(default_factory=list)
    processing_time: float
    
    @validator('processing_time')
    def round_processing_time(cls, v):
        return round(v, 3)


class TableComparisonResult(BaseModel):
    """Comparison result for a single table."""
    additions: int
    modifications: int
    deletions: int
    details: Optional[Dict[str, Any]] = None


class DataComparisonResponse(BaseModel):
    """Response schema for data comparison."""
    tables_compared: int
    total_additions: int
    total_modifications: int
    total_deletions: int
    tables: Dict[str, TableComparisonResult]


class DataValidationResponse(BaseModel):
    """Response schema for data validation."""
    valid: bool
    errors: List[str] = Field(default_factory=list)
    message: str


class ExportHistoryResponse(BaseModel):
    """Export history entry response schema."""
    export_id: str
    timestamp: datetime
    format: ExportFormat
    total_records: int
    total_tables: int
    organization_id: Optional[int]
    exported_by: str
    file_size: Optional[int] = None
    status: str = Field(default="completed")
    
    class Config:
        use_enum_values = True


class RoundTripTestRequest(BaseModel):
    """Request schema for round-trip integrity test."""
    tables: Optional[List[str]] = Field(default=None, description="Specific tables to test (all if not specified)")
    delete_data: bool = Field(default=False, description="Actually delete data during test (dangerous)")
    
    @validator('delete_data')
    def validate_delete_data(cls, v):
        if v:
            raise ValueError("Actual data deletion is not allowed for safety reasons")
        return v


class RoundTripTestResponse(BaseModel):
    """Response schema for round-trip integrity test."""
    test_passed: bool
    message: str
    original_checksum: str
    reimported_checksum: str
    checksums_match: bool
    export_metadata: Dict[str, Any]
    import_result: Dict[str, Any]
    comparison_summary: Dict[str, Any]
    detailed_differences: Dict[str, Any] = Field(default_factory=dict)
    test_details: Dict[str, Any]


# Bulk operation schemas
class BulkExportRequest(BaseModel):
    """Request schema for bulk organization export."""
    organization_ids: List[int]
    format: ExportFormat = Field(default=ExportFormat.JSONL)
    tables: Optional[List[str]] = None
    create_separate_files: bool = Field(default=True, description="Create separate files per organization")


class BulkImportRequest(BaseModel):
    """Request schema for bulk import operation."""
    files: List[str] = Field(description="List of file identifiers to import")
    strategy: ImportStrategy = Field(default=ImportStrategy.SKIP)
    organization_mapping: Optional[Dict[int, int]] = Field(default=None, description="Map source org IDs to target org IDs")


class BulkOperationStatus(BaseModel):
    """Status of a bulk operation."""
    operation_id: str
    status: str  # pending, running, completed, failed
    progress: float = Field(ge=0.0, le=1.0)
    total_items: int
    completed_items: int
    failed_items: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


# Advanced export/import schemas
class IncrementalExportRequest(BaseModel):
    """Request schema for incremental export (only changed data since timestamp)."""
    since_timestamp: datetime
    format: ExportFormat = Field(default=ExportFormat.JSONL)
    organization_id: Optional[int] = None
    tables: Optional[List[str]] = None


class DataTransformationRule(BaseModel):
    """Data transformation rule for import."""
    table: str
    field: str
    transformation: str  # e.g., "prefix:NEW_", "suffix:_MIGRATED", "replace:old,new"
    condition: Optional[str] = None  # Optional condition for applying rule


class AdvancedImportRequest(BaseModel):
    """Advanced import request with transformation rules."""
    file_data: bytes
    format: ExportFormat
    strategy: ImportStrategy = Field(default=ImportStrategy.SKIP)
    organization_id: Optional[int] = None
    transformation_rules: List[DataTransformationRule] = Field(default_factory=list)
    field_mappings: Dict[str, Dict[str, str]] = Field(default_factory=dict, description="Table.field -> new_field mappings")
    ignore_foreign_keys: bool = Field(default=False, description="Skip foreign key validation during import")


# Migration and sync schemas
class DataMigrationPlan(BaseModel):
    """Data migration plan schema."""
    migration_id: str
    source_organization_id: int
    target_organization_id: int
    tables: List[str]
    field_mappings: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    transformation_rules: List[DataTransformationRule] = Field(default_factory=list)
    strategy: ImportStrategy = Field(default=ImportStrategy.SKIP)
    validate_only: bool = Field(default=False)


class DataSyncRequest(BaseModel):
    """Request schema for data synchronization between organizations."""
    source_organization_id: int
    target_organization_id: int
    sync_direction: str = Field(default="bidirectional", regex="^(source_to_target|target_to_source|bidirectional)$")
    tables: Optional[List[str]] = None
    conflict_resolution: ImportStrategy = Field(default=ImportStrategy.SKIP)
    dry_run: bool = Field(default=True)


class DataIntegrityCheckRequest(BaseModel):
    """Request schema for data integrity check."""
    organization_id: Optional[int] = None
    tables: Optional[List[str]] = None
    check_foreign_keys: bool = Field(default=True)
    check_unique_constraints: bool = Field(default=True)
    check_data_types: bool = Field(default=True)
    fix_issues: bool = Field(default=False, description="Attempt to fix found issues")


class DataIntegrityCheckResponse(BaseModel):
    """Response schema for data integrity check."""
    success: bool
    total_records_checked: int
    issues_found: int
    issues_fixed: int
    details: Dict[str, Any]
    recommendations: List[str] = Field(default_factory=list)