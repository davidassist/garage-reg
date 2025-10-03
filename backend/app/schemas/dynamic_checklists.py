"""Pydantic schemas for dynamic checklist templates and inspections."""

from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


# Enums for validation
class ItemType(str, Enum):
    BOOL = "bool"
    ENUM = "enum" 
    NUMBER = "number"
    PHOTO = "photo"
    NOTE = "note"
    TEXT = "text"
    VISUAL = "visual"
    MEASUREMENT = "measurement"
    CHECKBOX = "checkbox"


class MeasurementType(str, Enum):
    BOOLEAN = "boolean"
    ENUM = "enum"
    NUMERIC_RANGE = "numeric_range"
    PHOTO = "photo"
    TEXT = "text"


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"


class InspectionResult(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    NA = "na"
    SKIP = "skip"
    PENDING = "pending"


# Base schemas
class ChecklistItemBase(BaseModel):
    """Base schema for checklist items."""
    title: str = Field(..., max_length=300)
    description: Optional[str] = None
    instructions: Optional[str] = None
    item_type: ItemType
    measurement_type: Optional[MeasurementType] = None
    section: Optional[str] = None
    category: Optional[str] = None
    order_index: int = Field(0, ge=0)
    
    # Requirements
    is_required: bool = True
    is_recommended: bool = False
    requires_photo: bool = False
    requires_measurement: bool = False
    requires_note: bool = False
    
    # Enum options for enum type items
    enum_options: Optional[List[str]] = None
    
    # Measurement specifications
    measurement_unit: Optional[str] = Field(None, max_length=20)
    measurement_min: Optional[float] = None
    measurement_max: Optional[float] = None
    measurement_target: Optional[float] = None
    measurement_tolerance: Optional[float] = None
    
    # Validation and rules
    validation_schema: Optional[Dict[str, Any]] = None
    conditional_rules: Optional[Dict[str, Any]] = None
    
    # Criteria
    pass_criteria: Optional[str] = None
    fail_criteria: Optional[str] = None
    
    # Safety
    safety_critical: bool = False
    severity_level: SeverityLevel = SeverityLevel.MEDIUM
    
    # Dependencies
    depends_on_item_id: Optional[int] = None
    
    @validator('enum_options')
    def validate_enum_options(cls, v, values):
        if values.get('item_type') == ItemType.ENUM and not v:
            raise ValueError('enum_options required for enum type items')
        return v
    
    @validator('measurement_unit')
    def validate_measurement_unit(cls, v, values):
        if values.get('item_type') == ItemType.NUMBER and values.get('requires_measurement') and not v:
            raise ValueError('measurement_unit required for number type items with measurement')
        return v


class ChecklistItemCreate(ChecklistItemBase):
    """Schema for creating checklist items."""
    template_id: Optional[int] = None  # Will be set when creating from template


class ChecklistItemUpdate(BaseModel):
    """Schema for updating checklist items."""
    title: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = None
    instructions: Optional[str] = None
    item_type: Optional[ItemType] = None
    measurement_type: Optional[MeasurementType] = None
    section: Optional[str] = None
    category: Optional[str] = None
    order_index: Optional[int] = Field(None, ge=0)
    is_required: Optional[bool] = None
    is_recommended: Optional[bool] = None
    requires_photo: Optional[bool] = None
    requires_measurement: Optional[bool] = None
    requires_note: Optional[bool] = None
    enum_options: Optional[List[str]] = None
    measurement_unit: Optional[str] = Field(None, max_length=20)
    measurement_min: Optional[float] = None
    measurement_max: Optional[float] = None
    measurement_target: Optional[float] = None
    measurement_tolerance: Optional[float] = None
    validation_schema: Optional[Dict[str, Any]] = None
    conditional_rules: Optional[Dict[str, Any]] = None
    pass_criteria: Optional[str] = None
    fail_criteria: Optional[str] = None
    safety_critical: Optional[bool] = None
    severity_level: Optional[SeverityLevel] = None
    depends_on_item_id: Optional[int] = None


class ChecklistItemResponse(ChecklistItemBase):
    """Schema for checklist item responses."""
    id: int
    template_id: int
    org_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


# Template schemas
class ChecklistTemplateBase(BaseModel):
    """Base schema for checklist templates."""
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    version: str = Field("1.0", max_length=20)
    template_type: str = Field(..., max_length=50)
    applicable_gate_types: Optional[List[str]] = None
    applicable_manufacturers: Optional[List[str]] = None
    estimated_duration_minutes: Optional[int] = Field(None, ge=1)
    recommended_frequency_days: Optional[int] = Field(None, ge=1)
    required_tools: Optional[List[str]] = None
    required_skills: Optional[List[str]] = None
    weather_conditions: Optional[str] = Field(None, max_length=200)
    
    # Dynamic validation
    validation_schema: Optional[Dict[str, Any]] = None
    conditional_rules: Optional[Dict[str, Any]] = None
    standards_references: Optional[Dict[str, Any]] = None
    
    is_mandatory: bool = False
    settings: Optional[Dict[str, Any]] = None


class ChecklistTemplateCreate(ChecklistTemplateBase):
    """Schema for creating checklist templates."""
    items: Optional[List[ChecklistItemCreate]] = []


class ChecklistTemplateUpdate(BaseModel):
    """Schema for updating checklist templates."""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    version: Optional[str] = Field(None, max_length=20)
    template_type: Optional[str] = Field(None, max_length=50)
    applicable_gate_types: Optional[List[str]] = None
    applicable_manufacturers: Optional[List[str]] = None
    estimated_duration_minutes: Optional[int] = Field(None, ge=1)
    recommended_frequency_days: Optional[int] = Field(None, ge=1)
    required_tools: Optional[List[str]] = None
    required_skills: Optional[List[str]] = None
    weather_conditions: Optional[str] = Field(None, max_length=200)
    validation_schema: Optional[Dict[str, Any]] = None
    conditional_rules: Optional[Dict[str, Any]] = None
    standards_references: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_mandatory: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None


class ChecklistTemplateResponse(ChecklistTemplateBase):
    """Schema for checklist template responses."""
    id: int
    org_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    items: List[ChecklistItemResponse] = []
    
    class Config:
        orm_mode = True


# Section-based template schema
class ChecklistSectionSchema(BaseModel):
    """Schema for template sections."""
    name: str
    description: Optional[str] = None
    order_index: int = 0
    items: List[ChecklistItemCreate] = []


class DynamicTemplateSchema(BaseModel):
    """Schema for creating templates with sections."""
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    version: str = Field("1.0", max_length=20)
    template_type: str = Field(..., max_length=50)
    applicable_gate_types: Optional[List[str]] = None
    applicable_manufacturers: Optional[List[str]] = None
    estimated_duration_minutes: Optional[int] = Field(None, ge=1)
    recommended_frequency_days: Optional[int] = Field(None, ge=1)
    required_tools: Optional[List[str]] = None
    required_skills: Optional[List[str]] = None
    
    # Dynamic validation
    validation_schema: Optional[Dict[str, Any]] = None
    conditional_rules: Optional[Dict[str, Any]] = None
    standards_references: Optional[Dict[str, Any]] = None
    
    # Sections containing items
    sections: List[ChecklistSectionSchema] = []
    
    is_mandatory: bool = False
    settings: Optional[Dict[str, Any]] = None


# Inspection schemas
class InspectionItemValueSchema(BaseModel):
    """Schema for inspection item values."""
    item_id: int
    value: Optional[Union[str, float, bool, List[str]]] = None
    result: Optional[InspectionResult] = None
    notes: Optional[str] = None
    photo_paths: Optional[List[str]] = None
    measured_at: Optional[datetime] = None
    checker_name: Optional[str] = None


class InspectionDataSchema(BaseModel):
    """Schema for inspection data submission."""
    gate_id: int
    template_id: int
    inspection_type: str = Field(..., max_length=50)
    inspector_name: str = Field(..., max_length=200)
    reason: Optional[str] = Field(None, max_length=500)
    weather_conditions: Optional[str] = Field(None, max_length=200)
    temperature_celsius: Optional[int] = Field(None, ge=-50, le=60)
    humidity_percentage: Optional[int] = Field(None, ge=0, le=100)
    
    # Item results
    items: List[InspectionItemValueSchema] = []
    
    # Additional notes
    general_notes: Optional[str] = None
    followup_required: bool = False
    followup_notes: Optional[str] = None


class InspectionValidationResult(BaseModel):
    """Schema for inspection validation results."""
    is_valid: bool
    errors: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    conditional_items: List[Dict[str, Any]] = []
    completion_percentage: float = Field(0.0, ge=0.0, le=100.0)
    missing_required_items: List[int] = []


class InspectionResponse(BaseModel):
    """Schema for inspection responses."""
    id: int
    gate_id: int
    template_id: int
    inspection_date: datetime
    inspector_name: str
    inspector_id: Optional[int] = None
    inspection_type: str
    reason: Optional[str] = None
    weather_conditions: Optional[str] = None
    temperature_celsius: Optional[int] = None
    humidity_percentage: Optional[int] = None
    overall_status: str
    overall_score: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    requires_followup: bool
    followup_priority: Optional[str] = None
    followup_notes: Optional[str] = None
    next_inspection_date: Optional[datetime] = None
    
    class Config:
        orm_mode = True


# EU Standards preload schema
class EUStandardPreloadRequest(BaseModel):
    """Schema for preloading EU standard templates."""
    standard: Literal["EN13241", "EN12453", "EN12604"]
    customize: bool = False
    customizations: Optional[Dict[str, Any]] = None


class TemplateJsonSchemaResponse(BaseModel):
    """Schema for template JSON schema responses."""
    template_id: int
    schema: Dict[str, Any]
    sections: List[Dict[str, Any]]
    validation_rules: Dict[str, Any]
    conditional_logic: Dict[str, Any]