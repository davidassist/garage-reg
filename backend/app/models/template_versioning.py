"""
Enhanced document template models with versioning and WYSIWYG support
Fejlett dokumentum sablon modellek verziókezeléssel és WYSIWYG támogatással
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.orm import relationship, validates
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any, List

from app.models import TenantModel


class TemplateChangeType(str, Enum):
    """Template change types for changelog"""
    CREATED = "created"
    UPDATED = "updated"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    RESTORED = "restored"
    CLONED = "cloned"


class TemplateStatus(str, Enum):
    """Template status enumeration"""
    DRAFT = "draft"
    PUBLISHED = "published" 
    ARCHIVED = "archived"


class DocumentTemplateVersion(TenantModel):
    """
    Document template versions for WYSIWYG editing with full history
    Dokumentum sablon verziók WYSIWYG szerkesztéshez teljes történettel
    """
    __tablename__ = "document_template_versions"
    
    # Template reference
    template_id = Column(Integer, ForeignKey("document_templates.id"), nullable=False, index=True)
    
    # Version information
    version_number = Column(String(20), nullable=False)  # "1.0", "1.1", "2.0"
    version_name = Column(String(100), nullable=True)  # Optional version name
    
    # Template content (versioned)
    html_template = Column(Text, nullable=False)  # WYSIWYG generated HTML
    css_styles = Column(Text, nullable=True)  # Custom CSS
    header_template = Column(Text, nullable=True)  # Page header
    footer_template = Column(Text, nullable=True)  # Page footer
    
    # WYSIWYG editor specific data
    editor_content = Column(JSON, nullable=True)  # Raw editor state (TinyMCE/CKEditor)
    preview_image_url = Column(String(500), nullable=True)  # Generated preview image
    
    # Template metadata (versioned)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuration (versioned)
    page_size = Column(String(20), default='A4', nullable=False)
    orientation = Column(String(20), default='portrait', nullable=False)
    margins = Column(JSON, nullable=True)  # Margins configuration
    
    # QR and logo settings (versioned)
    include_qr_code = Column(Boolean, default=True, nullable=False)
    qr_code_position = Column(String(50), default='top_right', nullable=False)
    qr_code_size = Column(Integer, default=100, nullable=False)
    include_logo = Column(Boolean, default=True, nullable=False)
    logo_position = Column(String(50), default='top_left', nullable=False)
    
    # Data schema (versioned)
    required_fields = Column(JSON, nullable=True)
    optional_fields = Column(JSON, nullable=True)
    sample_data = Column(JSON, nullable=True)  # Sample data for preview
    
    # Version status
    status = Column(SQLEnum(TemplateStatus), default=TemplateStatus.DRAFT, nullable=False)
    is_current = Column(Boolean, default=False, nullable=False)  # Current active version
    
    # Change tracking
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    published_at = Column(DateTime, nullable=True)
    published_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Generated files
    preview_pdf_path = Column(String(500), nullable=True)  # Preview PDF file path
    
    # Relationships
    template = relationship("DocumentTemplate", back_populates="versions")
    created_by = relationship("User", foreign_keys=[created_by_id])
    published_by = relationship("User", foreign_keys=[published_by_id])
    
    # Indexes
    __table_args__ = (
        Index("idx_template_version", "template_id", "version_number"),
        Index("idx_template_current", "template_id", "is_current"),
        Index("idx_template_status", "status"),
        Index("idx_template_published", "published_at"),
    )
    
    def increment_version(self, version_type: str = "minor") -> str:
        """Generate next version number"""
        if not self.version_number:
            return "1.0"
        
        try:
            parts = self.version_number.split('.')
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
            
            if version_type == "major":
                return f"{major + 1}.0"
            else:  # minor
                return f"{major}.{minor + 1}"
        except:
            return "1.0"


class DocumentTemplateChangeLog(TenantModel):
    """
    Change log for document template modifications
    Dokumentum sablon módosítások változásnaplója
    """
    __tablename__ = "document_template_change_logs"
    
    # Template reference
    template_id = Column(Integer, ForeignKey("document_templates.id"), nullable=False, index=True)
    version_id = Column(Integer, ForeignKey("document_template_versions.id"), nullable=True, index=True)
    
    # Change details
    change_type = Column(SQLEnum(TemplateChangeType), nullable=False, index=True)
    change_summary = Column(String(500), nullable=False)  # Brief description
    change_details = Column(JSON, nullable=True)  # Detailed changes
    
    # User information
    changed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    change_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Change context
    ip_address = Column(String(45), nullable=True)  # User IP address
    user_agent = Column(String(500), nullable=True)  # Browser info
    session_id = Column(String(100), nullable=True)  # Session identifier
    
    # Before/after data for comparisons
    old_data = Column(JSON, nullable=True)  # Previous state
    new_data = Column(JSON, nullable=True)  # New state
    
    # Approval workflow
    requires_approval = Column(Boolean, default=False, nullable=False)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approval_notes = Column(Text, nullable=True)
    
    # Relationships
    template = relationship("DocumentTemplate")
    version = relationship("DocumentTemplateVersion")
    changed_by = relationship("User", foreign_keys=[changed_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    
    # Indexes
    __table_args__ = (
        Index("idx_changelog_template_type", "template_id", "change_type"),
        Index("idx_changelog_timestamp", "change_timestamp"),
        Index("idx_changelog_user", "changed_by_id"),
        Index("idx_changelog_approval", "requires_approval", "approved_at"),
    )


class DocumentTemplateField(TenantModel):
    """
    Template field definitions for WYSIWYG editor
    Sablon mező definíciók WYSIWYG szerkesztőhöz
    """
    __tablename__ = "document_template_fields"
    
    # Template reference
    template_id = Column(Integer, ForeignKey("document_templates.id"), nullable=False, index=True)
    
    # Field definition
    field_name = Column(String(100), nullable=False)  # Variable name in template
    display_name = Column(String(200), nullable=False)  # User-friendly name
    field_type = Column(String(50), nullable=False)  # text, number, date, boolean, image, table
    
    # Field configuration
    is_required = Column(Boolean, default=False, nullable=False)
    default_value = Column(String(500), nullable=True)
    validation_rules = Column(JSON, nullable=True)  # Validation constraints
    
    # WYSIWYG editor properties
    editor_widget = Column(String(100), nullable=True)  # textbox, richtext, datepicker, etc.
    widget_config = Column(JSON, nullable=True)  # Widget-specific configuration
    
    # Display properties
    order_index = Column(Integer, default=0, nullable=False)
    group_name = Column(String(100), nullable=True)  # Field grouping
    help_text = Column(String(1000), nullable=True)  # User guidance
    
    # Data source configuration
    data_source = Column(String(100), nullable=True)  # Static, dynamic, computed
    source_query = Column(Text, nullable=True)  # SQL query or API endpoint
    
    # Relationships
    template = relationship("DocumentTemplate", back_populates="fields")
    
    # Indexes
    __table_args__ = (
        Index("idx_field_template_order", "template_id", "order_index"),
        Index("idx_field_name", "field_name"),
        Index("idx_field_type", "field_type"),
    )


class DocumentPreviewSession(TenantModel):
    """
    Preview sessions for template editing
    Előnézeti munkamenetek sablon szerkesztéshez
    """
    __tablename__ = "document_preview_sessions"
    
    # Session identification
    session_token = Column(String(100), unique=True, nullable=False, index=True)
    template_id = Column(Integer, ForeignKey("document_templates.id"), nullable=False)
    version_id = Column(Integer, ForeignKey("document_template_versions.id"), nullable=True)
    
    # Session details
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = Column(DateTime, nullable=False)  # Session expiry
    
    # Preview configuration
    preview_data = Column(JSON, nullable=True)  # Data used for preview generation
    preview_options = Column(JSON, nullable=True)  # Preview rendering options
    
    # Generated preview files
    html_preview_path = Column(String(500), nullable=True)
    pdf_preview_path = Column(String(500), nullable=True)
    preview_image_path = Column(String(500), nullable=True)
    
    # Session status
    is_active = Column(Boolean, default=True, nullable=False)
    generation_status = Column(String(50), default='pending', nullable=False)  # pending, generating, ready, failed
    error_message = Column(Text, nullable=True)
    
    # Relationships
    template = relationship("DocumentTemplate")
    version = relationship("DocumentTemplateVersion")
    created_by = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index("idx_preview_token", "session_token"),
        Index("idx_preview_template", "template_id"),
        Index("idx_preview_expires", "expires_at"),
        Index("idx_preview_status", "generation_status"),
    )


# Enhanced DocumentTemplate with version support
class DocumentTemplateEnhanced(TenantModel):
    """
    Enhanced document template with WYSIWYG and versioning support
    Fejlett dokumentum sablon WYSIWYG és verziókezelés támogatással
    """
    __tablename__ = "document_templates_enhanced"
    
    # Basic template information
    name = Column(String(100), nullable=False, index=True)
    document_type = Column(String(50), nullable=False, index=True)
    language = Column(String(5), default='hu', nullable=False)
    
    # Current version reference
    current_version_id = Column(Integer, ForeignKey("document_template_versions.id"), nullable=True)
    
    # Template status and settings
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    
    # WYSIWYG editor configuration
    editor_type = Column(String(50), default='tinymce', nullable=False)  # tinymce, ckeditor, quill
    editor_config = Column(JSON, nullable=True)  # Editor-specific configuration
    
    # Template categories and tags
    category = Column(String(100), nullable=True)  # Template category
    tags = Column(JSON, nullable=True)  # Array of tags for searchability
    
    # Usage statistics
    usage_count = Column(Integer, default=0, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    last_generated_at = Column(DateTime, nullable=True)
    
    # Approval workflow settings
    requires_approval = Column(Boolean, default=False, nullable=False)
    approval_users = Column(JSON, nullable=True)  # Array of user IDs who can approve
    
    # Company and branding
    company_info = Column(JSON, nullable=True)  # Company details for templates
    
    # Relationships
    versions = relationship("DocumentTemplateVersion", back_populates="template", cascade="all, delete-orphan")
    fields = relationship("DocumentTemplateField", back_populates="template", cascade="all, delete-orphan")
    current_version = relationship("DocumentTemplateVersion", foreign_keys=[current_version_id])
    
    # Indexes
    __table_args__ = (
        Index("idx_template_type_active", "document_type", "is_active"),
        Index("idx_template_default", "is_default"),
        Index("idx_template_category", "category"),
        Index("idx_template_usage", "usage_count"),
    )
    
    def create_new_version(self, user_id: int, version_type: str = "minor") -> 'DocumentTemplateVersion':
        """Create new version from current version"""
        current = self.current_version
        if current:
            new_version_number = current.increment_version(version_type)
        else:
            new_version_number = "1.0"
        
        # Create new version
        new_version = DocumentTemplateVersion(
            template_id=self.id,
            organization_id=self.organization_id,
            version_number=new_version_number,
            html_template=current.html_template if current else "",
            css_styles=current.css_styles if current else None,
            header_template=current.header_template if current else None,
            footer_template=current.footer_template if current else None,
            editor_content=current.editor_content if current else None,
            title=current.title if current else self.name,
            description=current.description if current else None,
            page_size=current.page_size if current else "A4",
            orientation=current.orientation if current else "portrait",
            margins=current.margins if current else None,
            include_qr_code=current.include_qr_code if current else True,
            qr_code_position=current.qr_code_position if current else "top_right",
            qr_code_size=current.qr_code_size if current else 100,
            include_logo=current.include_logo if current else True,
            logo_position=current.logo_position if current else "top_left",
            required_fields=current.required_fields if current else None,
            optional_fields=current.optional_fields if current else None,
            sample_data=current.sample_data if current else None,
            status=TemplateStatus.DRAFT,
            created_by_id=user_id
        )
        
        return new_version