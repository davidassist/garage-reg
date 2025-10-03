"""API routes for field forms and inspection state management."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.rbac import get_current_active_user, require_permission
from app.models.auth import User
from app.models.inspections import Inspection, InspectionPhoto
from app.schemas.field_forms import (
    InspectionStart,
    InspectionUpdate, 
    InspectionComplete,
    InspectionResponse,
    InspectionListResponse,
    PhotoUploadRequest,
    PhotoUploadResponse,
    PhotoResponse
)
from app.services.field_form_service import FieldFormService
from app.services.s3_photo_service import S3PhotoService, PhotoValidationService

router = APIRouter(tags=["Field Forms"])


@router.post("/test/inspections/start", response_model=InspectionResponse)
async def test_start_inspection(
    inspection_data: InspectionStart,
    db: Session = Depends(get_db)
):
    """Test endpoint without authentication - creates inspection with dummy user."""
    from app.services.field_form_service import FieldFormService
    
    # Create dummy user for testing
    class TestUser:
        def __init__(self):
            self.id = 1
            self.username = "testuser"
            self.email = "test@example.com"
            self.org_id = 1
            self.organization_id = 1
            self.full_name = "Test User"
            self.first_name = "Test"
            self.last_name = "User"
            self.display_name = "Test User"
    
    service = FieldFormService(db)
    inspection = service.start_inspection(inspection_data, TestUser())
    return inspection


@router.post("/inspections/start", response_model=InspectionResponse)
async def start_inspection(
    start_data: InspectionStart,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Start a new field inspection (POST /inspections/start).
    
    Creates a new inspection instance and initializes it with checklist items.
    Supports offline mode for mobile devices.
    """
    require_permission("inspection:write", current_user)
    
    service = FieldFormService(db)
    inspection = service.start_inspection(start_data, current_user)
    
    # Get inspection with statistics
    result = service.get_inspection_with_stats(inspection.id, current_user)
    
    return InspectionResponse(
        **inspection.__dict__,
        **result["stats"]
    )


@router.patch("/inspections/{inspection_id}", response_model=InspectionResponse)
async def update_inspection(
    inspection_id: int,
    update_data: InspectionUpdate,
    force_update: bool = Query(False, description="Force update even with conflicts"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update inspection data (PATCH /inspections/{id}).
    
    Supports partial updates of inspection data and items.
    Handles conflict detection for offline synchronization.
    """
    require_permission("inspection:write", current_user)
    
    service = FieldFormService(db)
    inspection = service.update_inspection(
        inspection_id, 
        update_data, 
        current_user, 
        force_update
    )
    
    # Get inspection with statistics
    result = service.get_inspection_with_stats(inspection.id, current_user)
    
    return InspectionResponse(
        **inspection.__dict__,
        **result["stats"]
    )


@router.post("/inspections/{inspection_id}/complete", response_model=InspectionResponse)
async def complete_inspection(
    inspection_id: int,
    complete_data: InspectionComplete,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Complete inspection (POST /inspections/{id}/complete).
    
    Finalizes the inspection, validates all requirements are met,
    and calculates final scores and status.
    """
    require_permission("inspection:write", current_user)
    
    service = FieldFormService(db)
    inspection = service.complete_inspection(inspection_id, complete_data, current_user)
    
    # Get final inspection with statistics
    result = service.get_inspection_with_stats(inspection.id, current_user)
    
    return InspectionResponse(
        **inspection.__dict__,
        **result["stats"]
    )


@router.get("/inspections/{inspection_id}", response_model=InspectionResponse)
async def get_inspection(
    inspection_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get inspection details with statistics.
    
    Returns full inspection data including progress statistics,
    completion requirements, and available actions.
    """
    require_permission("inspection:read", current_user)
    
    service = FieldFormService(db)
    result = service.get_inspection_with_stats(inspection_id, current_user)
    
    return InspectionResponse(
        **result["inspection"].__dict__,
        **result["stats"]
    )


@router.get("/inspections", response_model=InspectionListResponse)
async def list_inspections(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    state: Optional[str] = Query(None, description="Filter by inspection state"),
    gate_id: Optional[int] = Query(None, description="Filter by gate ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List inspections with filtering and pagination.
    
    Supports filtering by state, gate, and other criteria.
    Returns paginated results with statistics.
    """
    require_permission("inspection:read", current_user)
    
    # Build query
    query = db.query(Inspection).filter(
        Inspection.org_id == current_user.org_id,
        Inspection.is_active == True
    )
    
    if state:
        query = query.filter(Inspection.state == state)
    if gate_id:
        query = query.filter(Inspection.gate_id == gate_id)
    
    # Count total
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    inspections = query.offset(offset).limit(per_page).all()
    
    # Convert to response format with statistics
    service = FieldFormService(db)
    inspection_responses = []
    
    for inspection in inspections:
        stats = service._calculate_inspection_stats(inspection)
        inspection_responses.append(
            InspectionResponse(
                **inspection.__dict__,
                **stats
            )
        )
    
    return InspectionListResponse(
        inspections=inspection_responses,
        total=total,
        page=page,
        per_page=per_page,
        has_next=(page * per_page) < total,
        has_prev=page > 1
    )


# Photo Documentation APIs

@router.post("/inspections/{inspection_id}/photos/upload", response_model=PhotoUploadResponse)
async def request_photo_upload(
    inspection_id: int,
    photo_request: PhotoUploadRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Request pre-signed URL for photo upload to S3.
    
    Creates photo record and returns S3 upload URL for direct client upload.
    Supports GPS coordinates and device metadata.
    """
    require_permission("inspection:write", current_user)
    
    # Validate inspection exists
    inspection = db.query(Inspection).filter(
        Inspection.id == inspection_id,
        Inspection.org_id == current_user.org_id,
        Inspection.is_active == True
    ).first()
    
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    # Generate S3 upload URL
    s3_service = S3PhotoService()
    upload_response = s3_service.generate_upload_url(photo_request)
    
    # Create photo record in database
    photo = InspectionPhoto(
        org_id=current_user.org_id,
        inspection_id=inspection_id,
        inspection_item_id=photo_request.inspection_item_id,
        category=photo_request.metadata.category,
        title=photo_request.metadata.title,
        description=photo_request.metadata.description,
        s3_bucket=s3_service.bucket_name or 'local',
        s3_key=upload_response.s3_key,
        original_filename=photo_request.metadata.original_filename,
        file_size_bytes=photo_request.metadata.file_size_bytes,
        mime_type=photo_request.metadata.mime_type,
        width_pixels=photo_request.metadata.width_pixels,
        height_pixels=photo_request.metadata.height_pixels,
        gps_latitude=photo_request.metadata.gps_latitude,
        gps_longitude=photo_request.metadata.gps_longitude,
        location_accuracy_meters=photo_request.metadata.location_accuracy_meters,
        captured_at=photo_request.metadata.captured_at or datetime.utcnow(),
        captured_by_id=current_user.id,
        device_info=photo_request.metadata.device_info,
        upload_status='pending',
        is_required=photo_request.metadata.is_required
    )
    
    db.add(photo)
    db.commit()
    db.refresh(photo)
    
    # Update response with photo ID
    upload_response.photo_id = photo.id
    
    return upload_response


@router.post("/inspections/{inspection_id}/photos/{photo_id}/confirm")
async def confirm_photo_upload(
    inspection_id: int,
    photo_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Confirm photo upload completion and validate.
    
    Called by client after successful S3 upload to validate
    the file exists and update the photo record status.
    """
    require_permission("inspection:write", current_user)
    
    # Get photo record
    photo = db.query(InspectionPhoto).filter(
        InspectionPhoto.id == photo_id,
        InspectionPhoto.inspection_id == inspection_id,
        InspectionPhoto.org_id == current_user.org_id
    ).first()
    
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    # Validate upload in S3
    s3_service = S3PhotoService()
    validation_result = s3_service.validate_upload_completion(photo.s3_key)
    
    if validation_result.get('exists'):
        # Update photo record with successful upload
        photo.upload_status = 'completed'
        photo.uploaded_at = datetime.utcnow()
        photo.file_size_bytes = validation_result.get('size', photo.file_size_bytes)
        
        # Generate download URL
        photo.s3_url = s3_service.generate_download_url(photo.s3_key)
        
        db.commit()
        
        return {"status": "confirmed", "photo_id": photo_id}
    else:
        # Upload failed
        photo.upload_status = 'failed'
        photo.upload_error = "File not found in S3 after upload"
        db.commit()
        
        raise HTTPException(
            status_code=400, 
            detail="Photo upload validation failed"
        )


@router.get("/inspections/{inspection_id}/photos", response_model=List[PhotoResponse])
async def list_inspection_photos(
    inspection_id: int,
    category: Optional[str] = Query(None, description="Filter by photo category"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List photos for inspection.
    
    Returns all photos associated with an inspection,
    optionally filtered by category.
    """
    require_permission("inspection:read", current_user)
    
    # Validate inspection access
    inspection = db.query(Inspection).filter(
        Inspection.id == inspection_id,
        Inspection.org_id == current_user.org_id
    ).first()
    
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    # Query photos
    query = db.query(InspectionPhoto).filter(
        InspectionPhoto.inspection_id == inspection_id,
        InspectionPhoto.is_active == True
    )
    
    if category:
        query = query.filter(InspectionPhoto.category == category)
    
    photos = query.all()
    
    # Generate fresh download URLs
    s3_service = S3PhotoService()
    for photo in photos:
        if photo.upload_status == 'completed':
            photo.s3_url = s3_service.generate_download_url(photo.s3_key)
    
    return [PhotoResponse(**photo.__dict__) for photo in photos]


@router.delete("/inspections/{inspection_id}/photos/{photo_id}")
async def delete_inspection_photo(
    inspection_id: int,
    photo_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete inspection photo.
    
    Removes photo from both database and S3 storage.
    """
    require_permission("inspection:write", current_user)
    
    # Get photo record
    photo = db.query(InspectionPhoto).filter(
        InspectionPhoto.id == photo_id,
        InspectionPhoto.inspection_id == inspection_id,
        InspectionPhoto.org_id == current_user.org_id
    ).first()
    
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    # Delete from S3
    s3_service = S3PhotoService()
    s3_deleted = s3_service.delete_photo(photo.s3_key)
    
    # Soft delete from database
    photo.is_active = False
    db.commit()
    
    return {
        "status": "deleted",
        "photo_id": photo_id,
        "s3_deleted": s3_deleted
    }


# Conflict Resolution APIs

@router.post("/inspections/{inspection_id}/resolve-conflict")
async def resolve_inspection_conflict(
    inspection_id: int,
    resolution_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Resolve inspection synchronization conflict.
    
    Applies conflict resolution strategy and merges conflicting data.
    """
    require_permission("inspection:write", current_user)
    
    # Get inspection with conflict
    inspection = db.query(Inspection).filter(
        Inspection.id == inspection_id,
        Inspection.org_id == current_user.org_id,
        Inspection.sync_status == 'conflict'
    ).first()
    
    if not inspection:
        raise HTTPException(
            status_code=404, 
            detail="Inspection not found or no conflict exists"
        )
    
    merge_strategy = resolution_data.get('merge_strategy', 'latest_wins')
    
    if merge_strategy == 'latest_wins':
        # Apply client data as-is
        for key, value in resolution_data.get('client_data', {}).items():
            if hasattr(inspection, key):
                setattr(inspection, key, value)
    elif merge_strategy == 'manual':
        # Apply manually merged data
        for key, value in resolution_data.get('merged_data', {}).items():
            if hasattr(inspection, key):
                setattr(inspection, key, value)
    
    # Clear conflict
    inspection.sync_status = 'synced'
    inspection.conflict_data = None
    inspection.conflict_resolved_at = datetime.utcnow()
    inspection.conflict_resolved_by_id = current_user.id
    inspection.last_sync_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "status": "resolved",
        "merge_strategy": merge_strategy,
        "resolved_at": inspection.conflict_resolved_at
    }


# Validation and Requirements APIs

@router.get("/inspections/{inspection_id}/validation")
async def get_inspection_validation(
    inspection_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get inspection validation status and requirements.
    
    Returns current completion status, missing requirements,
    and actions needed before completion.
    """
    require_permission("inspection:read", current_user)
    
    service = FieldFormService(db)
    result = service.get_inspection_with_stats(inspection_id, current_user)
    
    inspection = result["inspection"]
    
    # Photo validation
    photo_validation = PhotoValidationService.validate_photo_requirements(
        inspection_id,
        inspection.photos,
        inspection.required_photos or []
    )
    
    return {
        "inspection_id": inspection_id,
        "can_complete": result["can_complete"],
        "required_actions": result["required_actions"],
        "completion_stats": result["stats"],
        "photo_validation": photo_validation,
        "state": inspection.state,
        "sync_status": inspection.sync_status
    }