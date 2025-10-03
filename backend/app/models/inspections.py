"""Checklist and inspection models."""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Numeric, Index
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, Dict, Any
from datetime import datetime

from app.models import TenantModel


class ChecklistTemplate(TenantModel):
    """
    Checklist Templates - reusable inspection templates.
    
    Ellenőrzési lista sablonok (újrafelhasználható sablonok)
    """
    __tablename__ = "checklist_templates"
    
    # Basic information
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)  # 'safety', 'maintenance', 'installation', 'repair'
    
    # Template metadata
    version = Column(String(20), default='1.0', nullable=False)
    template_type = Column(String(50), nullable=False)  # 'general', 'gate_type_specific', 'manufacturer_specific'
    applicable_gate_types = Column(JSONB, nullable=True)  # Array of gate types this applies to
    applicable_manufacturers = Column(JSONB, nullable=True)  # Array of manufacturers this applies to
    
    # Timing and frequency
    estimated_duration_minutes = Column(Integer, nullable=True)
    recommended_frequency_days = Column(Integer, nullable=True)
    
    # Requirements and conditions
    required_tools = Column(JSONB, nullable=True)  # Array of required tools
    required_skills = Column(JSONB, nullable=True)  # Array of required skills/certifications
    weather_conditions = Column(String(200), nullable=True)  # Required weather conditions
    
    # Dynamic JSON schema for validation
    validation_schema = Column(JSONB, nullable=True)  # JSON Schema for dynamic validation
    
    # Conditional logic
    conditional_rules = Column(JSONB, nullable=True)  # Rules for conditional item display
    
    # EU Standards references
    standards_references = Column(JSONB, nullable=True)  # EN 13241, EN 12453, EN 12604 references
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    is_mandatory = Column(Boolean, default=False, nullable=False)
    settings = Column(JSONB, nullable=True, default=lambda: {})
    
    # Relationships
    items = relationship("ChecklistItem", back_populates="template", cascade="all, delete-orphan")
    inspections = relationship("Inspection", back_populates="checklist_template")
    
    # Indexes
    __table_args__ = (
        Index("idx_checklist_template_name", "name"),
        Index("idx_checklist_template_category", "category"),
        Index("idx_checklist_template_type", "template_type"),
        Index("idx_checklist_template_active", "is_active"),
        Index("idx_checklist_template_mandatory", "is_mandatory"),
    )


class ChecklistItem(TenantModel):
    """
    Checklist Items - individual items within a checklist template.
    
    Ellenőrzési lista tételek (egyes ellenőrzési pontok)
    """
    __tablename__ = "checklist_items"
    
    # Template reference
    template_id = Column(Integer, ForeignKey("checklist_templates.id"), nullable=False, index=True)
    
    # Item information
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    
    # Item characteristics - Enhanced with new measurement types
    item_type = Column(String(50), nullable=False)  # 'bool', 'enum', 'number', 'photo', 'note', 'visual', 'measurement'
    measurement_type = Column(String(50), nullable=True)  # 'boolean', 'enum', 'numeric_range', 'photo', 'text'
    category = Column(String(100), nullable=True)  # Group related items
    section = Column(String(200), nullable=True)  # Section within template (e.g., "Safety Systems", "Mechanical")
    order_index = Column(Integer, nullable=False, default=0)  # Order within template
    
    # Requirements - Enhanced
    is_required = Column(Boolean, default=True, nullable=False)  # Kötelező pont
    is_recommended = Column(Boolean, default=False, nullable=False)  # Ajánlott pont
    requires_photo = Column(Boolean, default=False, nullable=False)
    requires_measurement = Column(Boolean, default=False, nullable=False)
    requires_note = Column(Boolean, default=False, nullable=False)
    
    # Dynamic validation schema (JSON Schema)
    validation_schema = Column(JSONB, nullable=True)  # Full JSON Schema for complex validation
    
    # Enum options (for enum type items)
    enum_options = Column(JSONB, nullable=True)  # Array of allowed values for enum types
    
    # Measurement specifications - Enhanced
    measurement_unit = Column(String(20), nullable=True)  # 'N', 'kg', 'cm', 'seconds', 'A', 'V', etc.
    measurement_min = Column(Numeric(10, 3), nullable=True)  # Minimum acceptable value
    measurement_max = Column(Numeric(10, 3), nullable=True)  # Maximum acceptable value  
    measurement_target = Column(Numeric(10, 3), nullable=True)  # Target/ideal value
    measurement_tolerance = Column(Numeric(10, 3), nullable=True)  # Allowed deviation from target
    
    # Conditional logic
    depends_on_item_id = Column(Integer, ForeignKey("checklist_items.id"), nullable=True)  # Parent item for conditional logic
    conditional_rules = Column(JSONB, nullable=True)  # Rules when this item should be shown/required
    
    # Pass/fail criteria
    pass_criteria = Column(Text, nullable=True)
    fail_criteria = Column(Text, nullable=True)
    
    # Safety and importance
    safety_critical = Column(Boolean, default=False, nullable=False)
    severity_level = Column(String(20), default='medium', nullable=False)  # 'low', 'medium', 'high', 'critical'
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSONB, nullable=True, default=lambda: {})
    
    # Relationships
    template = relationship("ChecklistTemplate", back_populates="items")
    inspection_items = relationship("InspectionItem", back_populates="checklist_item")
    
    # Indexes
    __table_args__ = (
        Index("idx_checklist_item_template", "template_id"),
        Index("idx_checklist_item_type", "item_type"),
        Index("idx_checklist_item_category", "category"),
        Index("idx_checklist_item_order", "order_index"),
        Index("idx_checklist_item_required", "is_required"),
        Index("idx_checklist_item_safety", "safety_critical"),
        Index("idx_checklist_item_severity", "severity_level"),
    )
    
    @validates("item_type")
    def validate_item_type(self, key, value):
        valid_types = ['bool', 'enum', 'number', 'photo', 'note', 'visual', 'measurement', 'text', 'checkbox']
        if value not in valid_types:
            raise ValueError(f"Item type must be one of: {valid_types}")
        return value
    
    @validates("measurement_type")
    def validate_measurement_type(self, key, value):
        if value is None:
            return value
        valid_types = ['boolean', 'enum', 'numeric_range', 'photo', 'text']
        if value not in valid_types:
            raise ValueError(f"Measurement type must be one of: {valid_types}")
        return value
    
    @validates("severity_level")
    def validate_severity_level(self, key, value):
        valid_levels = ['low', 'medium', 'high', 'critical']
        if value not in valid_levels:
            raise ValueError(f"Severity level must be one of: {valid_levels}")
        return value


class Inspection(TenantModel):
    """
    Inspections - completed inspection instances.
    
    Elvégzett ellenőrzések (konkrét ellenőrzési események)
    """
    __tablename__ = "inspections"
    
    # Gate and template references
    gate_id = Column(Integer, ForeignKey("gates.id"), nullable=False, index=True)
    checklist_template_id = Column(Integer, ForeignKey("checklist_templates.id"), nullable=False, index=True)
    
    # Inspection metadata
    inspection_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    inspector_name = Column(String(200), nullable=False)
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Inspection context
    inspection_type = Column(String(50), nullable=False)  # 'routine', 'emergency', 'post_repair', 'warranty'
    reason = Column(String(500), nullable=True)
    
    # Weather and conditions
    weather_conditions = Column(String(200), nullable=True)
    temperature_celsius = Column(Integer, nullable=True)
    humidity_percentage = Column(Integer, nullable=True)
    
    # Results and status
    overall_status = Column(String(50), nullable=False)  # 'passed', 'failed', 'warning', 'incomplete'
    overall_score = Column(Numeric(5, 2), nullable=True)  # 0-100 percentage score
    
    # State machine for field forms
    state = Column(String(20), nullable=False, default='draft')  # 'draft', 'started', 'in_progress', 'completed', 'archived'
    
    # Time tracking
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Field form specific fields
    mobile_device_id = Column(String(100), nullable=True)  # Device identifier for offline sync
    offline_started_at = Column(DateTime, nullable=True)  # When started offline
    sync_status = Column(String(20), nullable=False, default='synced')  # 'synced', 'pending', 'conflict'
    last_sync_at = Column(DateTime, nullable=True)
    
    # Conflict resolution
    conflict_data = Column(JSONB, nullable=True)  # Store conflicting versions
    merge_strategy = Column(String(20), nullable=True)  # 'latest_wins', 'manual', 'field_priority'
    conflict_resolved_at = Column(DateTime, nullable=True)
    conflict_resolved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Photo documentation requirements
    required_photos = Column(JSONB, nullable=True)  # Required photo categories
    uploaded_photos = Column(JSONB, nullable=True)  # Uploaded photo metadata
    photo_validation_status = Column(String(20), nullable=False, default='pending')  # 'pending', 'complete', 'missing'
    
    # Follow-up actions
    requires_followup = Column(Boolean, default=False, nullable=False)
    followup_priority = Column(String(20), nullable=True)  # 'low', 'medium', 'high', 'urgent'
    followup_notes = Column(Text, nullable=True)
    next_inspection_date = Column(DateTime, nullable=True)
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSONB, nullable=True, default=lambda: {})
    
    # Relationships
    gate = relationship("Gate", back_populates="inspections")
    checklist_template = relationship("ChecklistTemplate", back_populates="inspections")
    inspector = relationship("User", foreign_keys=[inspector_id], back_populates="inspections")
    conflict_resolver = relationship("User", foreign_keys=[conflict_resolved_by_id])
    items = relationship("InspectionItem", back_populates="inspection", cascade="all, delete-orphan")
    measurements = relationship("Measurement", back_populates="inspection", cascade="all, delete-orphan")
    photos = relationship("InspectionPhoto", back_populates="inspection", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_inspection_gate", "gate_id"),
        Index("idx_inspection_template", "checklist_template_id"),
        Index("idx_inspection_date", "inspection_date"),
        Index("idx_inspection_inspector", "inspector_id"),
        Index("idx_inspection_type", "inspection_type"),
        Index("idx_inspection_status", "overall_status"),
        Index("idx_inspection_followup", "requires_followup"),
        Index("idx_inspection_next_date", "next_inspection_date"),
    )
    
    @validates("overall_status")
    def validate_overall_status(self, key, value):
        valid_statuses = ['passed', 'failed', 'warning', 'incomplete', 'in_progress']
        if value not in valid_statuses:
            raise ValueError(f"Overall status must be one of: {valid_statuses}")
        return value
    
    @validates("inspection_type")
    def validate_inspection_type(self, key, value):
        valid_types = ['routine', 'emergency', 'post_repair', 'warranty', 'installation', 'annual']
        if value not in valid_types:
            raise ValueError(f"Inspection type must be one of: {valid_types}")
        return value
    
    @property
    def is_completed(self) -> bool:
        """Check if inspection is completed."""
        return self.completed_at is not None
    
    @property
    def is_overdue(self) -> bool:
        """Check if inspection is overdue."""
        if self.next_inspection_date:
            return datetime.utcnow() > self.next_inspection_date
        return False


class InspectionItem(TenantModel):
    """
    Inspection Items - results for individual checklist items.
    
    Ellenőrzési tétel eredmények (egyes pontok eredményei)
    """
    __tablename__ = "inspection_items"
    
    # References
    inspection_id = Column(Integer, ForeignKey("inspections.id"), nullable=False, index=True)
    checklist_item_id = Column(Integer, ForeignKey("checklist_items.id"), nullable=False, index=True)
    
    # Results
    result = Column(String(20), nullable=False)  # 'pass', 'fail', 'warning', 'na', 'skip'
    value = Column(String(500), nullable=True)  # Text value or measurement result
    notes = Column(Text, nullable=True)
    
    # Time tracking
    checked_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    checker_name = Column(String(200), nullable=True)
    
    # Media references
    photo_path = Column(String(500), nullable=True)
    document_ids = Column(JSONB, nullable=True)  # Array of document IDs
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSONB, nullable=True, default=lambda: {})
    
    # Relationships
    inspection = relationship("Inspection", back_populates="items")
    checklist_item = relationship("ChecklistItem", back_populates="inspection_items")
    photos = relationship("InspectionPhoto", back_populates="inspection_item", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_inspection_item_inspection", "inspection_id"),
        Index("idx_inspection_item_checklist", "checklist_item_id"),
        Index("idx_inspection_item_result", "result"),
        Index("idx_inspection_item_date", "checked_at"),
    )
    
    @validates("result")
    def validate_result(self, key, value):
        valid_results = ['pass', 'fail', 'warning', 'na', 'skip', 'pending']
        if value not in valid_results:
            raise ValueError(f"Result must be one of: {valid_results}")
        return value


class Measurement(TenantModel):
    """
    Measurements - specific measurement values (force, distance, etc.).
    
    Mérési értékek (erőmérés, távolság mérés, stb.)
    """
    __tablename__ = "measurements"
    
    # References
    inspection_id = Column(Integer, ForeignKey("inspections.id"), nullable=False, index=True)
    gate_id = Column(Integer, ForeignKey("gates.id"), nullable=False, index=True)
    component_id = Column(Integer, ForeignKey("gate_components.id"), nullable=True, index=True)
    
    # Measurement information
    measurement_type = Column(String(100), nullable=False, index=True)  # 'force', 'speed', 'current', 'voltage', etc.
    measurement_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Measurement data
    value = Column(Numeric(15, 6), nullable=False)
    unit = Column(String(20), nullable=False)  # 'N', 'kg', 'A', 'V', 'm/s', etc.
    
    # Reference values
    target_value = Column(Numeric(15, 6), nullable=True)
    min_acceptable = Column(Numeric(15, 6), nullable=True)
    max_acceptable = Column(Numeric(15, 6), nullable=True)
    
    # Measurement context
    measurement_conditions = Column(Text, nullable=True)
    equipment_used = Column(String(200), nullable=True)
    calibration_date = Column(DateTime, nullable=True)
    
    # Results and analysis
    is_within_tolerance = Column(Boolean, nullable=True)
    deviation_percentage = Column(Numeric(10, 3), nullable=True)
    status = Column(String(50), default='normal', nullable=False)  # 'normal', 'warning', 'critical'
    
    # Time tracking
    measured_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    measured_by = Column(String(200), nullable=False)
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSONB, nullable=True, default=lambda: {})
    
    # Relationships
    inspection = relationship("Inspection", back_populates="measurements")
    gate = relationship("Gate")
    component = relationship("GateComponent")
    
    # Indexes
    __table_args__ = (
        Index("idx_measurement_inspection", "inspection_id"),
        Index("idx_measurement_gate", "gate_id"),
        Index("idx_measurement_component", "component_id"),
        Index("idx_measurement_type", "measurement_type"),
        Index("idx_measurement_date", "measured_at"),
        Index("idx_measurement_status", "status"),
    )
    
    @validates("status")
    def validate_status(self, key, value):
        valid_statuses = ['normal', 'warning', 'critical', 'out_of_range']
        if value not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        return value
    
    @property
    def deviation_from_target(self) -> Optional[float]:
        """Calculate deviation from target value."""
        if self.target_value and float(self.target_value) != 0:
            return ((float(self.value) - float(self.target_value)) / float(self.target_value)) * 100
        return None


class InspectionPhoto(TenantModel):
    """
    Inspection Photos - photo documentation for inspections.
    
    Ellenőrzési fotók - fotós dokumentálás az ellenőrzésekhez
    """
    __tablename__ = "inspection_photos"
    
    # References
    inspection_id = Column(Integer, ForeignKey("inspections.id"), nullable=False, index=True)
    inspection_item_id = Column(Integer, ForeignKey("inspection_items.id"), nullable=True, index=True)
    
    # Photo metadata
    category = Column(String(50), nullable=False)  # 'mandatory', 'evidence', 'damage', 'repair', 'before', 'after'
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Storage information (S3)
    s3_bucket = Column(String(100), nullable=False)
    s3_key = Column(String(500), nullable=False)  # Full S3 object key
    s3_url = Column(String(1000), nullable=True)  # Pre-signed URL (temporary)
    
    # File metadata
    original_filename = Column(String(255), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    # Image metadata
    width_pixels = Column(Integer, nullable=True)
    height_pixels = Column(Integer, nullable=True)
    
    # GPS and location data
    gps_latitude = Column(Numeric(10, 8), nullable=True)  # GPS coordinates
    gps_longitude = Column(Numeric(11, 8), nullable=True)
    location_accuracy_meters = Column(Numeric(10, 2), nullable=True)
    
    # Capture context
    captured_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    captured_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    device_info = Column(JSONB, nullable=True)  # Camera, device model, etc.
    
    # Upload tracking
    uploaded_at = Column(DateTime, nullable=True)
    upload_status = Column(String(20), nullable=False, default='pending')  # 'pending', 'uploading', 'completed', 'failed'
    upload_attempts = Column(Integer, default=0, nullable=False)
    upload_error = Column(Text, nullable=True)
    
    # Validation and requirements
    is_required = Column(Boolean, default=False, nullable=False)
    is_validated = Column(Boolean, default=False, nullable=False)
    validation_notes = Column(Text, nullable=True)
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSONB, nullable=True, default=lambda: {})
    
    # Relationships
    inspection = relationship("Inspection", back_populates="photos")
    inspection_item = relationship("InspectionItem", back_populates="photos")
    captured_by = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index("idx_inspection_photo_inspection", "inspection_id"),
        Index("idx_inspection_photo_item", "inspection_item_id"),
        Index("idx_inspection_photo_category", "category"),
        Index("idx_inspection_photo_captured", "captured_at"),
        Index("idx_inspection_photo_upload_status", "upload_status"),
    )