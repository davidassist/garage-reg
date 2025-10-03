"""Service for field forms and inspection state management."""

import uuid
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException

from app.models.auth import User
from app.models.inspections import Inspection, InspectionItem, InspectionPhoto, ChecklistTemplate
from app.schemas.field_forms import (
    InspectionState, SyncStatus, PhotoValidationStatus, MergeStrategy,
    InspectionStart, InspectionUpdate, InspectionComplete, ConflictData,
    PhotoUploadRequest, MeasurementValue
)


class InspectionStateMachine:
    """
    Manages inspection state transitions for field forms.
    
    State flow: draft -> started -> in_progress -> completed -> archived
    """
    
    VALID_TRANSITIONS = {
        InspectionState.DRAFT: [InspectionState.STARTED],
        InspectionState.STARTED: [InspectionState.IN_PROGRESS, InspectionState.DRAFT],
        InspectionState.IN_PROGRESS: [InspectionState.COMPLETED, InspectionState.STARTED],
        InspectionState.COMPLETED: [InspectionState.ARCHIVED, InspectionState.IN_PROGRESS],
        InspectionState.ARCHIVED: []  # Terminal state
    }
    
    @classmethod
    def can_transition(cls, from_state: InspectionState, to_state: InspectionState) -> bool:
        """Check if state transition is valid."""
        return to_state in cls.VALID_TRANSITIONS.get(from_state, [])
    
    @classmethod
    def validate_transition(cls, from_state: InspectionState, to_state: InspectionState):
        """Validate and raise exception if transition is invalid."""
        if not cls.can_transition(from_state, to_state):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid state transition from {from_state} to {to_state}"
            )


class FieldFormService:
    """Service for managing field inspection forms."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def start_inspection(
        self, 
        start_data: InspectionStart, 
        current_user: User
    ) -> Inspection:
        """
        Start a new inspection (POST /inspections/start).
        
        Args:
            start_data: Inspection start parameters
            current_user: Current authenticated user
            
        Returns:
            Created inspection instance
            
        Raises:
            HTTPException: If template not found or validation fails
        """
        # Validate checklist template exists
        template = self.db.query(ChecklistTemplate).filter(
            ChecklistTemplate.id == start_data.checklist_template_id,
            ChecklistTemplate.org_id == current_user.org_id,
            ChecklistTemplate.is_active == True
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=404,
                detail="Checklist template not found"
            )
        
        # Create inspection record
        inspection = Inspection(
            org_id=current_user.org_id,
            gate_id=start_data.gate_id,
            checklist_template_id=start_data.checklist_template_id,
            state=InspectionState.STARTED,
            inspection_date=datetime.utcnow(),
            inspector_name=current_user.full_name or current_user.username,
            inspector_id=current_user.id,
            inspection_type=start_data.inspection_type,
            reason=start_data.reason,
            overall_status='incomplete',
            started_at=datetime.utcnow(),
            mobile_device_id=start_data.mobile_device_id,
            sync_status=SyncStatus.SYNCED if not start_data.offline_mode else SyncStatus.PENDING,
            weather_conditions=start_data.weather_conditions,
            temperature_celsius=start_data.temperature_celsius,
            humidity_percentage=start_data.humidity_percentage
        )
        
        if start_data.offline_mode:
            inspection.offline_started_at = datetime.utcnow()
        
        self.db.add(inspection)
        self.db.commit()
        self.db.refresh(inspection)
        
        # Create inspection items from template
        self._create_inspection_items(inspection, template)
        
        # Determine required photos
        self._analyze_photo_requirements(inspection)
        
        return inspection
    
    def update_inspection(
        self,
        inspection_id: int,
        update_data: InspectionUpdate,
        current_user: User,
        force_update: bool = False
    ) -> Inspection:
        """
        Update inspection (PATCH /inspections/{id}).
        
        Args:
            inspection_id: Inspection ID to update
            update_data: Update data
            current_user: Current authenticated user
            force_update: Force update even if conflicts exist
            
        Returns:
            Updated inspection instance
            
        Raises:
            HTTPException: If inspection not found or conflicts exist
        """
        inspection = self._get_inspection(inspection_id, current_user)
        
        # Check for conflicts if offline sync
        if update_data.mobile_device_id and not force_update:
            conflicts = self._detect_conflicts(inspection, update_data)
            if conflicts:
                self._handle_conflicts(inspection, update_data, conflicts)
                return inspection
        
        # Validate state transition if requested
        if update_data.state and update_data.state != inspection.state:
            InspectionStateMachine.validate_transition(
                InspectionState(inspection.state), 
                update_data.state
            )
            inspection.state = update_data.state
        
        # Update basic fields
        if update_data.overall_status:
            inspection.overall_status = update_data.overall_status
        if update_data.weather_conditions:
            inspection.weather_conditions = update_data.weather_conditions
        if update_data.temperature_celsius is not None:
            inspection.temperature_celsius = update_data.temperature_celsius
        if update_data.humidity_percentage is not None:
            inspection.humidity_percentage = update_data.humidity_percentage
        
        # Update items if provided
        if update_data.items:
            self._update_inspection_items(inspection, update_data.items)
        
        # Update sync metadata
        inspection.last_sync_at = datetime.utcnow()
        if update_data.mobile_device_id:
            inspection.mobile_device_id = update_data.mobile_device_id
            
        # Auto-transition to in_progress if items are being updated
        if update_data.items and inspection.state == InspectionState.STARTED:
            inspection.state = InspectionState.IN_PROGRESS
        
        self.db.commit()
        self.db.refresh(inspection)
        
        return inspection
    
    def complete_inspection(
        self,
        inspection_id: int,
        complete_data: InspectionComplete,
        current_user: User
    ) -> Inspection:
        """
        Complete inspection (POST /inspections/{id}/complete).
        
        Args:
            inspection_id: Inspection ID to complete
            complete_data: Completion data
            current_user: Current authenticated user
            
        Returns:
            Completed inspection instance
            
        Raises:
            HTTPException: If validation fails or required items missing
        """
        inspection = self._get_inspection(inspection_id, current_user)
        
        # Validate current state allows completion
        InspectionStateMachine.validate_transition(
            InspectionState(inspection.state),
            InspectionState.COMPLETED
        )
        
        # Validate completion requirements
        validation_errors = self._validate_completion_requirements(
            inspection, complete_data
        )
        if validation_errors:
            raise HTTPException(
                status_code=400,
                detail={"message": "Completion validation failed", "errors": validation_errors}
            )
        
        # Update final item results
        if complete_data.items:
            self._update_inspection_items(inspection, complete_data.items)
        
        # Update completion data
        inspection.state = InspectionState.COMPLETED
        inspection.overall_status = complete_data.overall_status
        inspection.completed_at = datetime.utcnow()
        inspection.requires_followup = complete_data.requires_followup
        inspection.followup_priority = complete_data.followup_priority
        inspection.followup_notes = complete_data.followup_notes
        inspection.next_inspection_date = complete_data.next_inspection_date
        
        if inspection.started_at:
            duration = datetime.utcnow() - inspection.started_at
            inspection.duration_minutes = int(duration.total_seconds() / 60)
        
        # Calculate overall score
        inspection.overall_score = self._calculate_overall_score(inspection)
        
        # Update photo validation status
        inspection.photo_validation_status = (
            PhotoValidationStatus.COMPLETE if complete_data.all_required_photos
            else PhotoValidationStatus.MISSING
        )
        
        inspection.sync_status = SyncStatus.SYNCED
        inspection.last_sync_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(inspection)
        
        return inspection
    
    def get_inspection_with_stats(
        self, 
        inspection_id: int, 
        current_user: User
    ) -> Dict[str, Any]:
        """
        Get inspection with statistics for mobile app.
        
        Args:
            inspection_id: Inspection ID
            current_user: Current authenticated user
            
        Returns:
            Inspection with statistics
        """
        inspection = self._get_inspection(inspection_id, current_user)
        
        # Calculate statistics
        stats = self._calculate_inspection_stats(inspection)
        
        return {
            "inspection": inspection,
            "stats": stats,
            "can_complete": self._can_complete_inspection(inspection),
            "required_actions": self._get_required_actions(inspection)
        }
    
    def _get_inspection(self, inspection_id: int, current_user: User) -> Inspection:
        """Get inspection by ID with access validation."""
        inspection = self.db.query(Inspection).filter(
            Inspection.id == inspection_id,
            Inspection.org_id == current_user.org_id,
            Inspection.is_active == True
        ).first()
        
        if not inspection:
            raise HTTPException(
                status_code=404,
                detail="Inspection not found"
            )
        
        return inspection
    
    def _create_inspection_items(self, inspection: Inspection, template: ChecklistTemplate):
        """Create inspection items from template."""
        for template_item in template.items:
            inspection_item = InspectionItem(
                org_id=inspection.org_id,
                inspection_id=inspection.id,
                checklist_item_id=template_item.id,
                result='skip',  # Default state
                checked_at=datetime.utcnow()
            )
            self.db.add(inspection_item)
        
        self.db.commit()
    
    def _update_inspection_items(
        self, 
        inspection: Inspection, 
        item_updates: List[Any]
    ):
        """Update inspection items with new data."""
        for update in item_updates:
            # Find corresponding inspection item
            item = next(
                (item for item in inspection.items 
                 if item.checklist_item_id == update.get('checklist_item_id')),
                None
            )
            
            if not item:
                continue
            
            # Update item data
            item.result = update.get('result', item.result)
            item.value = update.get('value', item.value)
            item.notes = update.get('notes', item.notes)
            item.checked_at = datetime.utcnow()
    
    def _analyze_photo_requirements(self, inspection: Inspection):
        """Analyze and set photo requirements."""
        required_photos = []
        
        for item in inspection.items:
            if item.checklist_item.requires_photo:
                required_photos.append({
                    "item_id": item.id,
                    "category": "mandatory",
                    "title": f"Photo for: {item.checklist_item.title}"
                })
        
        inspection.required_photos = required_photos
        inspection.photo_validation_status = (
            PhotoValidationStatus.COMPLETE if not required_photos
            else PhotoValidationStatus.PENDING
        )
    
    def _detect_conflicts(
        self, 
        inspection: Inspection, 
        update_data: InspectionUpdate
    ) -> Optional[List[str]]:
        """Detect conflicts between server and client versions."""
        conflicts = []
        
        # Check if inspection was modified after client's last sync
        client_last_sync = update_data.last_modified_at
        if (client_last_sync and 
            inspection.updated_at > client_last_sync + timedelta(seconds=30)):
            conflicts.append("inspection_modified_on_server")
        
        return conflicts if conflicts else None
    
    def _handle_conflicts(
        self, 
        inspection: Inspection, 
        update_data: InspectionUpdate, 
        conflicts: List[str]
    ):
        """Handle detected conflicts."""
        conflict_data = ConflictData(
            server_version={
                "updated_at": inspection.updated_at.isoformat(),
                "overall_status": inspection.overall_status,
                "state": inspection.state
            },
            client_version={
                "last_modified_at": update_data.last_modified_at.isoformat() if update_data.last_modified_at else None,
                "overall_status": update_data.overall_status,
                "state": update_data.state
            },
            conflict_fields=conflicts,
            merge_strategy=MergeStrategy.LATEST_WINS  # Default strategy
        )
        
        inspection.sync_status = SyncStatus.CONFLICT
        inspection.conflict_data = conflict_data.dict()
        
        self.db.commit()
        
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Conflict detected",
                "conflict_data": conflict_data.dict(),
                "resolution_required": True
            }
        )
    
    def _validate_completion_requirements(
        self, 
        inspection: Inspection, 
        complete_data: InspectionComplete
    ) -> List[str]:
        """Validate requirements for completion."""
        errors = []
        
        # Check required items are completed
        for item in inspection.items:
            if (item.checklist_item.is_required and 
                item.result in ['skip', 'na']):
                errors.append(f"Required item not completed: {item.checklist_item.title}")
        
        # Check required photos
        if not complete_data.all_required_photos:
            missing_photos = self._get_missing_required_photos(inspection)
            if missing_photos:
                errors.append(f"Missing required photos: {len(missing_photos)} photos")
        
        # Check required measurements
        if not complete_data.all_measurements_complete:
            missing_measurements = self._get_missing_measurements(inspection)
            if missing_measurements:
                errors.append(f"Missing measurements: {len(missing_measurements)} items")
        
        return errors
    
    def _calculate_overall_score(self, inspection: Inspection) -> float:
        """Calculate overall inspection score (0-100)."""
        if not inspection.items:
            return 0.0
        
        total_weight = 0
        weighted_score = 0
        
        for item in inspection.items:
            weight = 2.0 if item.checklist_item.safety_critical else 1.0
            total_weight += weight
            
            if item.result == 'pass':
                weighted_score += weight * 100
            elif item.result == 'warning':
                weighted_score += weight * 70
            elif item.result == 'fail':
                weighted_score += weight * 0
            # 'skip' and 'na' don't contribute to score
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _calculate_inspection_stats(self, inspection: Inspection) -> Dict[str, Any]:
        """Calculate inspection statistics."""
        total_items = len(inspection.items)
        completed_items = len([
            item for item in inspection.items 
            if item.result not in ['skip']
        ])
        required_photos = len(inspection.required_photos or [])
        uploaded_photos = len([
            photo for photo in inspection.photos 
            if photo.upload_status == 'completed'
        ])
        
        return {
            "total_items": total_items,
            "completed_items": completed_items,
            "completion_percentage": (completed_items / total_items * 100) if total_items > 0 else 0,
            "required_photos": required_photos,
            "uploaded_photos": uploaded_photos,
            "photos_complete": uploaded_photos >= required_photos
        }
    
    def _can_complete_inspection(self, inspection: Inspection) -> bool:
        """Check if inspection can be completed."""
        if inspection.state not in [InspectionState.IN_PROGRESS]:
            return False
        
        # Check if all required items are completed
        for item in inspection.items:
            if item.checklist_item.is_required and item.result in ['skip']:
                return False
        
        return True
    
    def _get_required_actions(self, inspection: Inspection) -> List[str]:
        """Get list of actions required before completion."""
        actions = []
        
        # Check incomplete required items
        incomplete_required = [
            item for item in inspection.items
            if item.checklist_item.is_required and item.result in ['skip']
        ]
        if incomplete_required:
            actions.append(f"Complete {len(incomplete_required)} required items")
        
        # Check missing photos
        missing_photos = self._get_missing_required_photos(inspection)
        if missing_photos:
            actions.append(f"Upload {len(missing_photos)} required photos")
        
        return actions
    
    def _get_missing_required_photos(self, inspection: Inspection) -> List[Dict[str, Any]]:
        """Get list of missing required photos."""
        required_photos = inspection.required_photos or []
        uploaded_photos = {
            photo.inspection_item_id: photo 
            for photo in inspection.photos 
            if photo.upload_status == 'completed'
        }
        
        missing = []
        for req_photo in required_photos:
            item_id = req_photo.get('item_id')
            if item_id not in uploaded_photos:
                missing.append(req_photo)
        
        return missing
    
    def _get_missing_measurements(self, inspection: Inspection) -> List[InspectionItem]:
        """Get list of items with missing measurements."""
        missing = []
        
        for item in inspection.items:
            if (item.checklist_item.requires_measurement and 
                not item.value):
                missing.append(item)
        
        return missing