"""Pydantic schemas for field forms and inspection state management."""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from decimal import Decimal
from enum import Enum


class InspectionState(str, Enum):
    """Inspection state machine states."""
    DRAFT = "draft"
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class SyncStatus(str, Enum):
    """Sync status for offline forms."""
    SYNCED = "synced"
    PENDING = "pending"
    CONFLICT = "conflict"


class PhotoValidationStatus(str, Enum):
    """Photo validation status."""
    PENDING = "pending"
    COMPLETE = "complete"
    MISSING = "missing"


class MergeStrategy(str, Enum):
    """Conflict merge strategies."""
    LATEST_WINS = "latest_wins"
    MANUAL = "manual"
    FIELD_PRIORITY = "field_priority"


class UploadStatus(str, Enum):
    """Photo upload status."""
    PENDING = "pending"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"


# Photo schemas
class PhotoMetadata(BaseModel):
    """Photo metadata for upload."""
    category: str = Field(..., description="Photo category (mandatory, evidence, damage, etc.)")
    title: str = Field(..., max_length=200, description="Photo title")
    description: Optional[str] = Field(None, description="Photo description")
    original_filename: Optional[str] = Field(None, max_length=255)
    mime_type: Optional[str] = Field(None, max_length=100)
    file_size_bytes: Optional[int] = Field(None, gt=0)
    width_pixels: Optional[int] = Field(None, gt=0)
    height_pixels: Optional[int] = Field(None, gt=0)
    gps_latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    gps_longitude: Optional[Decimal] = Field(None, ge=-180, le=180)
    location_accuracy_meters: Optional[Decimal] = Field(None, ge=0)
    captured_at: Optional[datetime] = Field(None, description="When photo was captured")
    device_info: Optional[Dict[str, Any]] = Field(None, description="Camera/device information")
    is_required: bool = Field(False, description="Is this photo required")

    class Config:
        from_attributes = True


class PhotoUploadRequest(BaseModel):
    """Request for photo upload to S3."""
    inspection_id: int = Field(..., gt=0)
    inspection_item_id: Optional[int] = Field(None, gt=0)
    metadata: PhotoMetadata
    
    class Config:
        from_attributes = True


class PhotoUploadResponse(BaseModel):
    """Response for photo upload request."""
    photo_id: int = Field(..., description="Created photo record ID")
    upload_url: str = Field(..., description="Pre-signed S3 upload URL")
    s3_key: str = Field(..., description="S3 object key")
    expires_at: datetime = Field(..., description="Upload URL expiration")
    
    class Config:
        from_attributes = True


class PhotoResponse(BaseModel):
    """Photo information response."""
    id: int
    inspection_id: int
    inspection_item_id: Optional[int]
    category: str
    title: str
    description: Optional[str]
    s3_bucket: str
    s3_key: str
    s3_url: Optional[str]
    original_filename: Optional[str]
    file_size_bytes: Optional[int]
    mime_type: Optional[str]
    width_pixels: Optional[int]
    height_pixels: Optional[int]
    gps_latitude: Optional[Decimal]
    gps_longitude: Optional[Decimal]
    location_accuracy_meters: Optional[Decimal]
    captured_at: datetime
    captured_by_id: Optional[int]
    uploaded_at: Optional[datetime]
    upload_status: UploadStatus
    is_required: bool
    is_validated: bool
    validation_notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Measurement schemas
class MeasurementValue(BaseModel):
    """Measurement value with unit and validation."""
    value: Union[float, int, str] = Field(..., description="Measured value")
    unit: str = Field(..., max_length=20, description="Measurement unit (N, m/s, etc.)")
    tolerance: Optional[float] = Field(None, description="Acceptable tolerance")
    min_value: Optional[float] = Field(None, description="Minimum acceptable value")
    max_value: Optional[float] = Field(None, description="Maximum acceptable value")
    target_value: Optional[float] = Field(None, description="Target/ideal value")
    
    @validator('value')
    def validate_numeric_value(cls, v, values):
        """Validate numeric measurements."""
        if isinstance(v, (int, float)):
            return v
        # Try to convert string to number
        try:
            return float(v)
        except (ValueError, TypeError):
            # Non-numeric values are allowed (e.g., enum selections)
            return v
    
    class Config:
        from_attributes = True


class InspectionItemUpdate(BaseModel):
    """Update data for inspection item."""
    result: str = Field(..., description="Item result (pass, fail, warning, na, skip)")
    value: Optional[str] = Field(None, max_length=500, description="Text value or measurement")
    measurement: Optional[MeasurementValue] = Field(None, description="Structured measurement")
    notes: Optional[str] = Field(None, description="Inspector notes")
    photo_required: bool = Field(False, description="Photo documentation required")
    
    @validator('result')
    def validate_result(cls, v):
        valid_results = ['pass', 'fail', 'warning', 'na', 'skip']
        if v not in valid_results:
            raise ValueError(f"Result must be one of: {valid_results}")
        return v
    
    class Config:
        from_attributes = True


# Inspection schemas  
class InspectionStart(BaseModel):
    """Data to start an inspection."""
    gate_id: int = Field(..., gt=0, description="Gate ID to inspect")
    checklist_template_id: int = Field(..., gt=0, description="Checklist template to use")
    inspection_type: str = Field("routine", description="Type of inspection")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for inspection")
    mobile_device_id: Optional[str] = Field(None, max_length=100, description="Mobile device identifier")
    offline_mode: bool = Field(False, description="Started in offline mode")
    
    # Environmental conditions
    weather_conditions: Optional[str] = Field(None, max_length=200)
    temperature_celsius: Optional[int] = Field(None, ge=-50, le=60)
    humidity_percentage: Optional[int] = Field(None, ge=0, le=100)
    
    class Config:
        from_attributes = True


class InspectionUpdate(BaseModel):
    """Partial update data for inspection."""
    state: Optional[InspectionState] = Field(None, description="New inspection state")
    overall_status: Optional[str] = Field(None, description="Overall status")
    weather_conditions: Optional[str] = Field(None, max_length=200)
    temperature_celsius: Optional[int] = Field(None, ge=-50, le=60)
    humidity_percentage: Optional[int] = Field(None, ge=0, le=100)
    inspector_notes: Optional[str] = Field(None, description="Inspector notes")
    
    # Item updates
    items: Optional[List[InspectionItemUpdate]] = Field(None, description="Item updates")
    
    # Sync metadata
    mobile_device_id: Optional[str] = Field(None, max_length=100)
    last_modified_at: Optional[datetime] = Field(None, description="Client-side modification time")
    
    class Config:
        from_attributes = True


class InspectionComplete(BaseModel):
    """Data to complete an inspection."""
    overall_status: str = Field(..., description="Final overall status")
    inspector_notes: Optional[str] = Field(None, description="Final inspector notes")
    requires_followup: bool = Field(False, description="Requires follow-up action")
    followup_priority: Optional[str] = Field(None, description="Follow-up priority level")
    followup_notes: Optional[str] = Field(None, description="Follow-up notes")
    next_inspection_date: Optional[datetime] = Field(None, description="Next recommended inspection")
    
    # Final item states
    items: List[InspectionItemUpdate] = Field([], description="Final item results")
    
    # Quality assurance
    all_required_photos: bool = Field(True, description="All required photos captured")
    all_measurements_complete: bool = Field(True, description="All measurements completed")
    
    class Config:
        from_attributes = True


class ConflictData(BaseModel):
    """Conflict resolution data."""
    server_version: Dict[str, Any] = Field(..., description="Current server version")
    client_version: Dict[str, Any] = Field(..., description="Conflicting client version")
    conflict_fields: List[str] = Field(..., description="Fields with conflicts")
    merge_strategy: Optional[MergeStrategy] = Field(None, description="Preferred merge strategy")
    
    class Config:
        from_attributes = True


class InspectionResponse(BaseModel):
    """Full inspection response."""
    id: int
    gate_id: int
    checklist_template_id: int
    state: InspectionState
    inspection_date: datetime
    inspector_name: str
    inspector_id: Optional[int]
    inspection_type: str
    reason: Optional[str]
    weather_conditions: Optional[str]
    temperature_celsius: Optional[int]
    humidity_percentage: Optional[int]
    overall_status: str
    overall_score: Optional[Decimal]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_minutes: Optional[int]
    mobile_device_id: Optional[str]
    offline_started_at: Optional[datetime]
    sync_status: SyncStatus
    last_sync_at: Optional[datetime]
    photo_validation_status: PhotoValidationStatus
    requires_followup: bool
    followup_priority: Optional[str]
    followup_notes: Optional[str]
    next_inspection_date: Optional[datetime]
    conflict_data: Optional[ConflictData]
    created_at: datetime
    updated_at: datetime
    
    # Counts and status
    total_items: int = Field(0, description="Total checklist items")
    completed_items: int = Field(0, description="Completed items")
    required_photos: int = Field(0, description="Required photos count") 
    uploaded_photos: int = Field(0, description="Uploaded photos count")
    
    class Config:
        from_attributes = True


class InspectionListResponse(BaseModel):
    """Paginated inspection list response."""
    inspections: List[InspectionResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool
    
    class Config:
        from_attributes = True