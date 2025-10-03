"""Documents and media management models."""

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Index, LargeBinary
from sqlalchemy.orm import relationship, validates
from sqlalchemy import JSON
from typing import Optional, List, Dict, Any
from datetime import datetime
import hashlib
from enum import Enum

from app.models import TenantModel


class DocumentType(str, Enum):
    """Document types for PDF generation."""
    OPERATIONAL_LOG = "operational_log"       # Üzemeltetési napló
    MAINTENANCE_PROTOCOL = "maintenance_protocol"  # Karbantartási jegyzőkönyv  
    WORK_SHEET = "work_sheet"                # Munkalap
    INSPECTION_REPORT = "inspection_report"   # Ellenőrzési jelentés
    CERTIFICATE = "certificate"              # Tanúsítvány
    MANUAL = "manual"                       # Kézikönyv
    PHOTO = "photo"                         # Fénykép
    OTHER = "other"                         # Egyéb


class DocumentStatus(str, Enum):
    """Document status."""
    DRAFT = "draft"
    GENERATED = "generated"
    SIGNED = "signed"
    ARCHIVED = "archived"
    EXPIRED = "expired"


class SignatureType(str, Enum):
    """Digital signature types."""
    NONE = "none"
    BASIC_STAMP = "basic_stamp"      # "Aláírt példány" pecsét demóhoz
    ETSI_PADES_B = "etsi_pades_b"    # ETSI PAdES-B-B alapszintű jelzés


class Document(TenantModel):
    """
    Documents - document management and metadata.
    
    Dokumentumok (dokumentum kezelés és metaadatok)
    """
    __tablename__ = "documents"
    
    # References (polymorphic - can belong to different entities)
    entity_type = Column(String(50), nullable=False, index=True)  # 'gate', 'inspection', 'ticket', 'work_order', etc.
    entity_id = Column(Integer, nullable=False, index=True)
    
    # Document information
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    title = Column(String(300), nullable=True)
    description = Column(Text, nullable=True)
    
    # File metadata
    content_type = Column(String(200), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    file_hash = Column(String(64), nullable=False, index=True)  # SHA-256 hash
    
    # Storage information
    storage_backend = Column(String(50), default='s3', nullable=False)  # 's3', 'local', 'azure'
    storage_key = Column(String(1000), nullable=False)  # S3 key or file path
    storage_bucket = Column(String(200), nullable=True)  # S3 bucket name
    
    # Document categorization
    category = Column(String(100), nullable=False, index=True)  # 'manual', 'photo', 'report', 'certificate', etc.
    tags = Column(JSON, nullable=True)  # Array of tags for search
    
    # Access control
    is_public = Column(Boolean, default=False, nullable=False)
    access_level = Column(String(50), default='organization', nullable=False)  # 'public', 'organization', 'restricted'
    
    # Upload information
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Version control
    version = Column(String(20), default='1.0', nullable=False)
    previous_version_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    is_current_version = Column(Boolean, default=True, nullable=False)
    
    # Document processing status
    processing_status = Column(String(50), default='uploaded', nullable=False)  # 'uploaded', 'processing', 'processed', 'failed'
    ocr_text = Column(Text, nullable=True)  # Extracted text from OCR
    
    # Expiration and retention
    expires_at = Column(DateTime, nullable=True)
    retention_period_days = Column(Integer, nullable=True)
    
    # PDF Generation specific fields
    document_number = Column(String(50), nullable=True, index=True)  # Generated document number
    document_type = Column(String(50), nullable=True, index=True)  # DocumentType enum values
    template_id = Column(Integer, ForeignKey("document_templates.id"), nullable=True)  # Reference to DocumentTemplate
    template_name = Column(String(100), nullable=True)  # HTML template used
    template_data = Column(JSON, nullable=True)  # Data used for template rendering
    html_content = Column(Text, nullable=True)  # Rendered HTML content
    
    # QR code for document identification  
    qr_code_data = Column(String(500), nullable=True)  # QR code content
    qr_code_image_path = Column(String(500), nullable=True)  # QR code image path
    
    # Approval workflow
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Digital signature
    signature_type = Column(String(20), default=SignatureType.NONE.value, nullable=False)
    signature_data = Column(JSON, nullable=True)  # Signature metadata
    signature_file_path = Column(String(500), nullable=True)  # Signed PDF path
    signed_at = Column(DateTime, nullable=True)
    signed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Download tracking
    download_count = Column(Integer, default=0, nullable=False)
    last_downloaded_at = Column(DateTime, nullable=True)
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSON, nullable=True, default=lambda: {})
    
    # Relationships
    uploaded_by_user = relationship("User", foreign_keys=[uploaded_by])
    approved_by_user = relationship("User", foreign_keys=[approved_by_id])
    signed_by_user = relationship("User", foreign_keys=[signed_by_id])
    previous_version = relationship("Document", remote_side="Document.id")
    template = relationship("DocumentTemplate", back_populates="documents")
    media_objects = relationship("MediaObject", back_populates="document", cascade="all, delete-orphan")
    signatures = relationship("DocumentSignature", back_populates="document", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_document_entity", "entity_type", "entity_id"),
        Index("idx_document_category", "category"),
        Index("idx_document_uploaded", "uploaded_at"),
        Index("idx_document_uploader", "uploaded_by"),
        Index("idx_document_hash", "file_hash"),
        Index("idx_document_current", "is_current_version"),
        Index("idx_document_access", "access_level"),
        Index("idx_document_expires", "expires_at"),
        Index("idx_document_number", "document_number"),
        Index("idx_document_type_status", "document_type", "processing_status"),
        Index("idx_document_signature", "signature_type", "signed_at"),
    )
    
    @validates("processing_status")
    def validate_processing_status(self, key, value):
        valid_statuses = ['uploaded', 'processing', 'processed', 'failed', 'quarantined']
        if value not in valid_statuses:
            raise ValueError(f"Processing status must be one of: {valid_statuses}")
        return value
    
    @validates("category")
    def validate_category(self, key, value):
        valid_categories = [
            'manual', 'photo', 'report', 'certificate', 'invoice', 'contract',
            'diagram', 'schematic', 'specification', 'warranty', 'log', 'other',
            'operational_log', 'maintenance_protocol', 'work_sheet'
        ]
        if value not in valid_categories:
            raise ValueError(f"Category must be one of: {valid_categories}")
        return value
    
    @validates('document_type')
    def validate_document_type(self, key, value):
        if value and value not in [t.value for t in DocumentType]:
            raise ValueError(f"Invalid document type: {value}")
        return value
    
    @validates('signature_type')
    def validate_signature_type(self, key, value):
        if value not in [s.value for s in SignatureType]:
            raise ValueError(f"Invalid signature type: {value}")
        return value
    
    @property
    def file_size_mb(self) -> float:
        """Get file size in megabytes."""
        return self.file_size / (1024 * 1024)
    
    @property
    def is_expired(self) -> bool:
        """Check if document is expired."""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    @classmethod
    def generate_storage_key(cls, org_id: int, entity_type: str, filename: str) -> str:
        """Generate a unique storage key for the file."""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        hash_suffix = hashlib.md5(f"{org_id}_{entity_type}_{filename}_{timestamp}".encode()).hexdigest()[:8]
        return f"org_{org_id}/{entity_type}/{timestamp}_{hash_suffix}_{filename}"


class MediaObject(TenantModel):
    """
    Media Objects - rich media files with processing metadata.
    
    Média objektumok (gazdag média fájlok feldolgozási metaadatokkal)
    """
    __tablename__ = "media_objects"
    
    # Document reference
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    
    # Media information
    media_type = Column(String(50), nullable=False, index=True)  # 'image', 'video', 'audio', 'pdf'
    mime_type = Column(String(200), nullable=False)
    
    # Original file metadata
    original_width = Column(Integer, nullable=True)
    original_height = Column(Integer, nullable=True)
    duration_seconds = Column(Integer, nullable=True)  # For video/audio
    frame_rate = Column(String(20), nullable=True)  # For video
    
    # Processing metadata
    thumbnail_key = Column(String(1000), nullable=True)  # S3 key for thumbnail
    preview_key = Column(String(1000), nullable=True)    # S3 key for preview/compressed version
    
    # Image-specific metadata
    exif_data = Column(JSON, nullable=True)  # EXIF data from images
    gps_latitude = Column(String(20), nullable=True)
    gps_longitude = Column(String(20), nullable=True)
    camera_make = Column(String(100), nullable=True)
    camera_model = Column(String(100), nullable=True)
    taken_at = Column(DateTime, nullable=True)  # When photo/video was taken
    
    # Processing information
    processing_status = Column(String(50), default='pending', nullable=False)
    processed_at = Column(DateTime, nullable=True)
    processing_errors = Column(Text, nullable=True)
    
    # Quality and analysis
    quality_score = Column(Integer, nullable=True)  # 1-100 quality assessment
    blur_detection = Column(Boolean, nullable=True)
    contains_text = Column(Boolean, nullable=True)
    extracted_text = Column(Text, nullable=True)  # OCR results
    
    # AI/ML analysis results
    object_detection = Column(JSON, nullable=True)  # Detected objects and their confidence
    classification_tags = Column(JSON, nullable=True)  # Auto-generated classification tags
    
    # Status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSON, nullable=True, default=lambda: {})
    
    # Relationships
    document = relationship("Document", back_populates="media_objects")
    
    # Indexes
    __table_args__ = (
        Index("idx_media_document", "document_id"),
        Index("idx_media_type", "media_type"),
        Index("idx_media_processing", "processing_status"),
        Index("idx_media_taken", "taken_at"),
        Index("idx_media_gps", "gps_latitude", "gps_longitude"),
    )
    
    @validates("media_type")
    def validate_media_type(self, key, value):
        valid_types = ['image', 'video', 'audio', 'pdf', 'document']
        if value not in valid_types:
            raise ValueError(f"Media type must be one of: {valid_types}")
        return value
    
    @validates("processing_status")
    def validate_processing_status(self, key, value):
        valid_statuses = ['pending', 'processing', 'completed', 'failed', 'skipped']
        if value not in valid_statuses:
            raise ValueError(f"Processing status must be one of: {valid_statuses}")
        return value
    
    @property
    def has_gps_location(self) -> bool:
        """Check if media has GPS coordinates."""
        return self.gps_latitude is not None and self.gps_longitude is not None
    
    @property
    def aspect_ratio(self) -> Optional[float]:
        """Calculate aspect ratio for images/videos."""
        if self.original_width and self.original_height and self.original_height > 0:
            return self.original_width / self.original_height
        return None
    
    @property
    def is_landscape(self) -> Optional[bool]:
        """Check if image/video is landscape oriented."""
        ratio = self.aspect_ratio
        if ratio:
            return ratio > 1.0
        return None


class Integration(TenantModel):
    """
    Integrations - external system integrations configuration.
    
    Integrációk (külső rendszer integráció konfigurációk)
    """
    __tablename__ = "integrations"
    
    # Integration information
    name = Column(String(200), nullable=False, index=True)
    integration_type = Column(String(100), nullable=False, index=True)  # 'webhook', 'api', 'file_sync', 'email'
    provider = Column(String(100), nullable=False, index=True)  # 'slack', 'teams', 'zapier', 'custom'
    
    # Configuration
    endpoint_url = Column(String(1000), nullable=True)
    authentication_type = Column(String(50), nullable=True)  # 'none', 'api_key', 'oauth', 'basic'
    credentials = Column(JSON, nullable=True)  # Encrypted credentials
    
    # Settings and mapping
    settings = Column(JSON, nullable=True, default=lambda: {})
    field_mappings = Column(JSON, nullable=True)  # Field mapping configurations
    
    # Status and health
    is_active = Column(Boolean, default=True, nullable=False)
    last_sync_at = Column(DateTime, nullable=True)
    last_success_at = Column(DateTime, nullable=True)
    last_error_at = Column(DateTime, nullable=True)
    last_error_message = Column(Text, nullable=True)
    health_status = Column(String(50), default='unknown', nullable=False)  # 'healthy', 'warning', 'error', 'unknown'
    
    # Usage statistics
    total_requests = Column(Integer, default=0, nullable=False)
    successful_requests = Column(Integer, default=0, nullable=False)
    failed_requests = Column(Integer, default=0, nullable=False)
    
    # Relationships
    webhooks = relationship("Webhook", back_populates="integration", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_integration_name", "name"),
        Index("idx_integration_type", "integration_type"),
        Index("idx_integration_provider", "provider"),
        Index("idx_integration_active", "is_active"),
        Index("idx_integration_health", "health_status"),
    )
    
    @validates("health_status")
    def validate_health_status(self, key, value):
        valid_statuses = ['healthy', 'warning', 'error', 'unknown', 'disabled']
        if value not in valid_statuses:
            raise ValueError(f"Health status must be one of: {valid_statuses}")
        return value


class Webhook(TenantModel):
    """
    Webhooks - webhook endpoint configurations and logs.
    
    Webhookok (webhook végpont konfigurációk és naplók)
    """
    __tablename__ = "webhooks"
    
    # Integration reference
    integration_id = Column(Integer, ForeignKey("integrations.id"), nullable=False, index=True)
    
    # Webhook configuration
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    endpoint_url = Column(String(1000), nullable=False)
    
    # Event configuration
    events = Column(JSON, nullable=False)  # Array of event types to listen for
    filters = Column(JSON, nullable=True)  # Filters to apply before sending
    
    # Security
    secret = Column(String(200), nullable=True)  # Webhook signing secret
    verify_ssl = Column(Boolean, default=True, nullable=False)
    
    # Retry configuration
    max_retries = Column(Integer, default=3, nullable=False)
    retry_delay_seconds = Column(Integer, default=60, nullable=False)
    timeout_seconds = Column(Integer, default=30, nullable=False)
    
    # Status and health
    is_active = Column(Boolean, default=True, nullable=False)
    last_triggered_at = Column(DateTime, nullable=True)
    last_success_at = Column(DateTime, nullable=True)
    last_failure_at = Column(DateTime, nullable=True)
    
    # Statistics
    total_triggers = Column(Integer, default=0, nullable=False)
    successful_deliveries = Column(Integer, default=0, nullable=False)
    failed_deliveries = Column(Integer, default=0, nullable=False)
    
    # Relationships
    integration = relationship("Integration", back_populates="webhooks")
    
    # Indexes
    __table_args__ = (
        Index("idx_webhook_integration", "integration_id"),
        Index("idx_webhook_active", "is_active"),
        Index("idx_webhook_last_triggered", "last_triggered_at"),
    )


class DocumentTemplate(TenantModel):
    """
    HTML templates for document generation.
    
    HTML sablonok dokumentum generáláshoz.
    """
    __tablename__ = "document_templates"
    
    # Template identification
    name = Column(String(100), nullable=False, unique=True, index=True)
    document_type = Column(String(50), nullable=False, index=True)  # DocumentType enum values
    version = Column(String(20), default='1.0', nullable=False)
    
    # Template metadata
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    language = Column(String(5), default='hu', nullable=False)  # 'hu', 'en'
    
    # Template content
    html_template = Column(Text, nullable=False)  # Jinja2 template
    css_styles = Column(Text, nullable=True)  # CSS styles
    
    # Header and footer templates
    header_template = Column(Text, nullable=True)  # Page header template
    footer_template = Column(Text, nullable=True)  # Page footer template
    
    # Template configuration
    page_size = Column(String(20), default='A4', nullable=False)  # A4, A3, Letter
    orientation = Column(String(20), default='portrait', nullable=False)  # portrait, landscape
    margins = Column(JSON, nullable=True)  # {top: 20, right: 20, bottom: 20, left: 20}
    
    # Data schema for validation
    required_fields = Column(JSON, nullable=True)  # Required data fields
    optional_fields = Column(JSON, nullable=True)  # Optional data fields
    
    # QR code configuration
    include_qr_code = Column(Boolean, default=True, nullable=False)
    qr_code_position = Column(String(50), default='top_right', nullable=False)
    qr_code_size = Column(Integer, default=100, nullable=False)  # pixels
    
    # Logo and branding
    include_logo = Column(Boolean, default=True, nullable=False)
    logo_position = Column(String(50), default='top_left', nullable=False)
    company_info = Column(JSON, nullable=True)  # Company details for header/footer
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)  # Default template for type
    
    # Relationships
    documents = relationship("Document", back_populates="template")
    
    # Indexes
    __table_args__ = (
        Index("idx_template_type", "document_type"),
        Index("idx_template_active", "is_active"),
        Index("idx_template_default", "is_default"),
    )
    
    @validates('document_type')
    def validate_document_type(self, key, value):
        if value not in [t.value for t in DocumentType]:
            raise ValueError(f"Invalid document type: {value}")
        return value


class DocumentSignature(TenantModel):
    """
    Document signature records for audit trail.
    
    Dokumentum aláírási rekordok audit nyomvonalhoz.
    """
    __tablename__ = "document_signatures"
    
    # Related document
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    
    # Signature details
    signature_type = Column(String(20), nullable=False)  # SignatureType enum values
    signer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    signed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Signature data
    signature_hash = Column(String(128), nullable=True)  # Signature hash
    certificate_info = Column(JSON, nullable=True)  # Certificate details for ETSI
    signature_image_path = Column(String(500), nullable=True)  # Signature image
    
    # Verification
    verification_status = Column(String(20), default='pending', nullable=False)
    verification_data = Column(JSON, nullable=True)  # Verification results
    verified_at = Column(DateTime, nullable=True)
    
    # IP and location for audit
    signer_ip_address = Column(String(45), nullable=True)  # IPv6 support
    signer_location = Column(String(200), nullable=True)
    signer_device = Column(String(200), nullable=True)
    
    # Relationships
    document = relationship("Document", back_populates="signatures")
    signer = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index("idx_signature_document", "document_id"),
        Index("idx_signature_signer", "signer_id"),
        Index("idx_signature_date", "signed_at"),
        Index("idx_signature_status", "verification_status"),
    )
    
    @validates('signature_type')
    def validate_signature_type(self, key, value):
        if value not in [s.value for s in SignatureType]:
            raise ValueError(f"Invalid signature type: {value}")
        return value
