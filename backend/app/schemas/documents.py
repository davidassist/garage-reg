"""
Pydantic schemas for document generation.

Pydantic sémák dokumentum generáláshoz.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from enum import Enum

from app.models.documents import DocumentType, DocumentStatus, SignatureType


class DocumentTypeEnum(str, Enum):
    """Document types for API."""
    OPERATIONAL_LOG = "operational_log"
    MAINTENANCE_PROTOCOL = "maintenance_protocol" 
    WORK_SHEET = "work_sheet"
    INSPECTION_REPORT = "inspection_report"
    CERTIFICATE = "certificate"
    MANUAL = "manual"
    PHOTO = "photo"
    OTHER = "other"


class SignatureTypeEnum(str, Enum):
    """Signature types for API."""
    NONE = "none"
    BASIC_STAMP = "basic_stamp"
    ETSI_PADES_B = "etsi_pades_b"


# Base request schemas
class DocumentGenerationRequest(BaseModel):
    """Base document generation request."""
    template_name: Optional[str] = None
    custom_data: Optional[Dict[str, Any]] = None


class OperationalLogRequest(DocumentGenerationRequest):
    """Request to generate operational log."""
    gate_id: int = Field(..., description="ID of the gate")
    date_from: date = Field(..., description="Start date for the log period")
    date_to: date = Field(..., description="End date for the log period")
    
    @validator('date_to')
    def validate_date_range(cls, v, values):
        if 'date_from' in values and v < values['date_from']:
            raise ValueError('date_to must be after date_from')
        return v


class MaintenanceProtocolRequest(DocumentGenerationRequest):
    """Request to generate maintenance protocol."""
    work_order_id: int = Field(..., description="ID of the work order")


class WorkSheetRequest(DocumentGenerationRequest):
    """Request to generate work sheet."""
    inspection_id: int = Field(..., description="ID of the inspection")


# Signature schemas
class SignatureRequest(BaseModel):
    """Request to add digital signature."""
    signature_type: SignatureTypeEnum = Field(SignatureTypeEnum.BASIC_STAMP, description="Type of signature to apply")
    signature_data: Optional[Dict[str, Any]] = Field(None, description="Additional signature data")


class SignatureResponse(BaseModel):
    """Response for signature operations."""
    id: int
    document_id: int
    signature_type: str
    signer_id: int
    signed_at: datetime
    verification_status: str
    signature_hash: Optional[str]
    
    class Config:
        orm_mode = True


# Document schemas
class DocumentBase(BaseModel):
    """Base document schema."""
    title: str
    description: Optional[str] = None
    category: str


class DocumentCreate(DocumentBase):
    """Schema for creating documents."""
    entity_type: str
    entity_id: int
    filename: str
    content_type: str
    file_size: int
    storage_key: str


class DocumentResponse(BaseModel):
    """Response schema for documents."""
    id: int
    entity_type: str
    entity_id: int
    filename: str
    original_filename: str
    title: str
    description: Optional[str]
    content_type: str
    file_size: int
    file_hash: str
    storage_key: str
    category: str
    document_number: Optional[str]
    document_type: Optional[str]
    template_name: Optional[str]
    qr_code_data: Optional[str]
    processing_status: str
    signature_type: str
    signed_at: Optional[datetime]
    signed_by_id: Optional[int]
    download_count: int
    last_downloaded_at: Optional[datetime]
    uploaded_by: Optional[int]
    uploaded_at: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # File size in MB for convenience
    @property
    def file_size_mb(self) -> float:
        return self.file_size / (1024 * 1024)
    
    class Config:
        orm_mode = True


# Template schemas
class DocumentTemplateBase(BaseModel):
    """Base template schema."""
    name: str
    document_type: DocumentTypeEnum
    title: str
    description: Optional[str] = None
    language: str = "hu"


class DocumentTemplateCreate(DocumentTemplateBase):
    """Schema for creating templates."""
    html_template: str
    css_styles: Optional[str] = None
    header_template: Optional[str] = None
    footer_template: Optional[str] = None
    page_size: str = "A4"
    orientation: str = "portrait"
    margins: Optional[Dict[str, int]] = None
    required_fields: Optional[List[str]] = None
    optional_fields: Optional[List[str]] = None
    include_qr_code: bool = True
    qr_code_position: str = "top_right"
    qr_code_size: int = 100
    include_logo: bool = True
    logo_position: str = "top_left"
    company_info: Optional[Dict[str, Any]] = None
    is_default: bool = False


class DocumentTemplateUpdate(BaseModel):
    """Schema for updating templates."""
    name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    html_template: Optional[str] = None
    css_styles: Optional[str] = None
    header_template: Optional[str] = None
    footer_template: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class DocumentTemplateResponse(BaseModel):
    """Response schema for templates."""
    id: int
    name: str
    document_type: str
    version: str
    title: str
    description: Optional[str]
    language: str
    page_size: str
    orientation: str
    margins: Optional[Dict[str, int]]
    include_qr_code: bool
    qr_code_position: str
    qr_code_size: int
    include_logo: bool
    logo_position: str
    company_info: Optional[Dict[str, Any]]
    is_active: bool
    is_default: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


# Verification schemas
class DocumentVerificationResponse(BaseModel):
    """Response for document verification."""
    document_number: str
    title: str
    document_type: str
    generation_date: datetime
    is_signed: bool
    signature_type: str
    signed_at: Optional[datetime]
    file_hash: str
    status: str


# Statistics schemas
class DocumentStatistics(BaseModel):
    """Document generation statistics."""
    period_days: int
    total_documents: int
    by_type: Dict[str, int]
    by_signature: Dict[str, int]
    downloads: Dict[str, Any]