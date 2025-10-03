"""Pydantic schemas for QR/NFC label generation and field access."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class QRCodeResponse(BaseModel):
    """Response for QR code generation."""
    gate_id: int
    gate_name: str
    token: str
    url: str
    expires_hours: int
    qr_image_url: str


class NFCDataResponse(BaseModel):
    """Response for NFC data generation."""
    gate_id: int
    nfc_data: Dict[str, Any]
    expires_hours: int


class TokenRotationResponse(BaseModel):
    """Response for token rotation."""
    gate_id: int
    token_version: int
    qr_token: str
    nfc_token: str
    qr_expires_hours: int
    nfc_expires_hours: int
    rotated_at: str


class LabelGenerationRequest(BaseModel):
    """Request for label generation."""
    gate_id: int
    label_type: str = Field(default="standard", description="Label type: standard, compact, zebra, brother")
    width: int = Field(default=400, ge=200, le=1200, description="Label width in pixels")
    height: int = Field(default=300, ge=150, le=900, description="Label height in pixels") 
    include_printer_templates: bool = Field(default=False, description="Include printer-specific templates")


class GateFieldAccessResponse(BaseModel):
    """Response for gate field access via token."""
    # Gate information
    gate_id: int
    gate_name: str
    gate_code: Optional[str] = None
    gate_type: str
    status: str
    
    # Technical details
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    
    # Dates
    installation_date: Optional[datetime] = None
    last_maintenance_date: Optional[datetime] = None
    next_maintenance_date: Optional[datetime] = None
    
    # Operational data
    current_cycle_count: int = 0
    
    # Hierarchy information
    building_name: Optional[str] = None
    site_name: Optional[str] = None
    client_name: Optional[str] = None
    
    # Token information
    token_expires_at: int  # Unix timestamp
    access_granted_at: int  # Unix timestamp
    
    class Config:
        from_attributes = True


class LabelTemplateResponse(BaseModel):
    """Response for label template generation."""
    gate_id: int
    gate_name: str
    label_type: str
    width: int
    height: int
    image_base64: Optional[str] = None
    download_url: str
    printer_templates: Optional[Dict[str, str]] = None


class FieldTokenInfo(BaseModel):
    """Information about a field access token."""
    gate_id: int
    org_id: int
    token_type: str = "field_access"
    expires_at: datetime
    issued_at: datetime
    token_id: str  # JWT ID for revocation