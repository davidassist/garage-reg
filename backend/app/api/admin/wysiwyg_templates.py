"""
WYSIWYG Template Admin API Endpoints
WYSIWYG Sablon Admin API végpontok
"""
import os
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ...core.database import get_db
from ...core.auth import get_current_user
from ...models.auth import User
from ...models.template_versioning import DocumentTemplateVersion, TemplateStatus
from ...services.wysiwyg_template_service import WYSIWYGTemplateService

router = APIRouter(prefix="/api/admin/wysiwyg-templates", tags=["WYSIWYG Templates"])


class TemplateVersionRequest(BaseModel):
    """Template version creation/update request"""
    html_content: str
    css_styles: Optional[str] = None
    editor_content: Optional[Dict[str, Any]] = None
    version_type: str = "minor"  # major, minor
    version_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class TemplateUpdateRequest(BaseModel):
    """Template version update request"""
    html_content: Optional[str] = None
    css_styles: Optional[str] = None
    editor_content: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class PreviewSessionRequest(BaseModel):
    """Preview session creation request"""
    sample_data: Optional[Dict[str, Any]] = None
    preview_options: Optional[Dict[str, Any]] = None


class TemplatePublishRequest(BaseModel):
    """Template publish request"""
    approval_notes: Optional[str] = None


@router.post("/templates/{template_id}/versions")
async def create_template_version(
    template_id: int,
    request: TemplateVersionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create new template version with WYSIWYG content
    Új sablon verzió létrehozása WYSIWYG tartalommal
    """
    try:
        service = WYSIWYGTemplateService(db)
        
        version = service.create_template_version(
            template_id=template_id,
            user_id=current_user.id,
            html_content=request.html_content,
            css_styles=request.css_styles,
            editor_content=request.editor_content,
            version_type=request.version_type,
            version_name=request.version_name,
            metadata=request.metadata
        )
        
        return {
            "success": True,
            "version": {
                "id": version.id,
                "version_number": version.version_number,
                "version_name": version.version_name,
                "status": version.status.value,
                "created_at": version.created_at.isoformat(),
                "preview_image_url": version.preview_image_url
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create version: {e}")


@router.put("/versions/{version_id}")
async def update_template_version(
    version_id: int,
    request: TemplateUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update existing template version
    Meglévő sablon verzió frissítése
    """
    try:
        service = WYSIWYGTemplateService(db)
        
        version = service.update_template_version(
            version_id=version_id,
            user_id=current_user.id,
            html_content=request.html_content,
            css_styles=request.css_styles,
            editor_content=request.editor_content,
            metadata=request.metadata
        )
        
        return {
            "success": True,
            "version": {
                "id": version.id,
                "version_number": version.version_number,
                "status": version.status.value,
                "updated_at": version.updated_at.isoformat(),
                "preview_image_url": version.preview_image_url
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update version: {e}")


@router.post("/versions/{version_id}/publish")
async def publish_template_version(
    version_id: int,
    request: TemplatePublishRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Publish template version (make it active)
    Sablon verzió publikálása (aktívvá tétel)
    """
    try:
        service = WYSIWYGTemplateService(db)
        
        version = service.publish_template_version(
            version_id=version_id,
            user_id=current_user.id,
            approval_notes=request.approval_notes
        )
        
        return {
            "success": True,
            "version": {
                "id": version.id,
                "version_number": version.version_number,
                "status": version.status.value,
                "published_at": version.published_at.isoformat(),
                "published_by": version.published_by.display_name if version.published_by else None
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish version: {e}")


@router.get("/templates/{template_id}/versions")
async def get_template_versions(
    template_id: int,
    include_drafts: bool = True,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get template version history
    Sablon verzió történet lekérése
    """
    try:
        service = WYSIWYGTemplateService(db)
        versions = service.get_template_versions(
            template_id=template_id,
            include_drafts=include_drafts,
            limit=limit
        )
        
        return {
            "success": True,
            "versions": [
                {
                    "id": v.id,
                    "version_number": v.version_number,
                    "version_name": v.version_name,
                    "title": v.title,
                    "description": v.description,
                    "status": v.status.value,
                    "is_current": v.is_current,
                    "created_at": v.created_at.isoformat(),
                    "updated_at": v.updated_at.isoformat() if v.updated_at else None,
                    "published_at": v.published_at.isoformat() if v.published_at else None,
                    "created_by": v.created_by.display_name if v.created_by else None,
                    "published_by": v.published_by.display_name if v.published_by else None,
                    "preview_image_url": v.preview_image_url
                }
                for v in versions
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get versions: {e}")


@router.get("/versions/{version_id}")
async def get_template_version_details(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed template version information
    Részletes sablon verzió információ lekérése
    """
    try:
        version = db.query(DocumentTemplateVersion).filter(
            DocumentTemplateVersion.id == version_id
        ).first()
        
        if not version:
            raise HTTPException(status_code=404, detail="Template version not found")
        
        return {
            "success": True,
            "version": {
                "id": version.id,
                "template_id": version.template_id,
                "version_number": version.version_number,
                "version_name": version.version_name,
                "title": version.title,
                "description": version.description,
                "html_template": version.html_template,
                "css_styles": version.css_styles,
                "editor_content": version.editor_content,
                "page_size": version.page_size,
                "orientation": version.orientation,
                "margins": version.margins,
                "include_qr_code": version.include_qr_code,
                "qr_code_position": version.qr_code_position,
                "qr_code_size": version.qr_code_size,
                "include_logo": version.include_logo,
                "logo_position": version.logo_position,
                "required_fields": version.required_fields,
                "optional_fields": version.optional_fields,
                "sample_data": version.sample_data,
                "status": version.status.value,
                "is_current": version.is_current,
                "created_at": version.created_at.isoformat(),
                "updated_at": version.updated_at.isoformat() if version.updated_at else None,
                "published_at": version.published_at.isoformat() if version.published_at else None,
                "created_by": version.created_by.display_name if version.created_by else None,
                "published_by": version.published_by.display_name if version.published_by else None,
                "preview_image_url": version.preview_image_url,
                "preview_pdf_path": version.preview_pdf_path
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get version: {e}")


@router.post("/versions/{version_id}/preview")
async def create_preview_session(
    version_id: int,
    request: PreviewSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create preview session for template version
    Előnézeti munkamenet létrehozása sablon verzióhoz
    """
    try:
        service = WYSIWYGTemplateService(db)
        
        session = service.create_preview_session(
            version_id=version_id,
            user_id=current_user.id,
            sample_data=request.sample_data,
            preview_options=request.preview_options
        )
        
        return {
            "success": True,
            "session": {
                "session_token": session.session_token,
                "expires_at": session.expires_at.isoformat(),
                "generation_status": session.generation_status
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create preview: {e}")


@router.get("/preview/{session_token}/status")
async def get_preview_status(
    session_token: str,
    db: Session = Depends(get_db)
):
    """
    Get preview generation status
    Előnézet generálás állapot lekérése
    """
    try:
        from ...models.template_versioning import DocumentPreviewSession
        
        session = db.query(DocumentPreviewSession).filter(
            DocumentPreviewSession.session_token == session_token
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Preview session not found")
        
        # Check if expired
        if session.expires_at < datetime.now(timezone=None):
            raise HTTPException(status_code=410, detail="Preview session expired")
        
        return {
            "success": True,
            "status": session.generation_status,
            "error_message": session.error_message,
            "ready": session.generation_status == 'ready',
            "has_html": bool(session.html_preview_path),
            "has_pdf": bool(session.pdf_preview_path),
            "has_image": bool(session.preview_image_path)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get preview status: {e}")


@router.get("/preview/{session_token}/html")
async def get_preview_html(
    session_token: str,
    db: Session = Depends(get_db)
):
    """
    Get HTML preview
    HTML előnézet lekérése
    """
    try:
        from ...models.template_versioning import DocumentPreviewSession
        
        session = db.query(DocumentPreviewSession).filter(
            DocumentPreviewSession.session_token == session_token
        ).first()
        
        if not session or not session.html_preview_path:
            raise HTTPException(status_code=404, detail="HTML preview not found")
        
        return FileResponse(
            session.html_preview_path,
            media_type="text/html",
            filename=f"template_preview_{session_token}.html"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get HTML preview: {e}")


@router.get("/preview/{session_token}/pdf")
async def get_preview_pdf(
    session_token: str,
    db: Session = Depends(get_db)
):
    """
    Get PDF preview
    PDF előnézet lekérése
    """
    try:
        from ...models.template_versioning import DocumentPreviewSession
        
        session = db.query(DocumentPreviewSession).filter(
            DocumentPreviewSession.session_token == session_token
        ).first()
        
        if not session or not session.pdf_preview_path:
            raise HTTPException(status_code=404, detail="PDF preview not found")
        
        return FileResponse(
            session.pdf_preview_path,
            media_type="application/pdf",
            filename=f"template_preview_{session_token}.pdf"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get PDF preview: {e}")


@router.get("/preview/{session_token}/image")
async def get_preview_image(
    session_token: str,
    db: Session = Depends(get_db)
):
    """
    Get preview image (PNG)
    Előnézet kép lekérése (PNG)
    """
    try:
        from ...models.template_versioning import DocumentPreviewSession
        
        session = db.query(DocumentPreviewSession).filter(
            DocumentPreviewSession.session_token == session_token
        ).first()
        
        if not session or not session.preview_image_path:
            raise HTTPException(status_code=404, detail="Preview image not found")
        
        return FileResponse(
            session.preview_image_path,
            media_type="image/png",
            filename=f"template_preview_{session_token}.png"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get preview image: {e}")


@router.get("/templates/{template_id}/changelog")
async def get_template_changelog(
    template_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get template change history
    Sablon változás történet lekérése
    """
    try:
        service = WYSIWYGTemplateService(db)
        changelog = service.get_template_changelog(
            template_id=template_id,
            limit=limit
        )
        
        return {
            "success": True,
            "changes": [
                {
                    "id": change.id,
                    "version_id": change.version_id,
                    "change_type": change.change_type.value,
                    "change_summary": change.change_summary,
                    "change_details": change.change_details,
                    "change_timestamp": change.change_timestamp.isoformat(),
                    "changed_by": change.changed_by.display_name if change.changed_by else None,
                    "old_data": change.old_data,
                    "new_data": change.new_data
                }
                for change in changelog
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get changelog: {e}")


@router.get("/versions/{version_id_1}/compare/{version_id_2}")
async def compare_template_versions(
    version_id_1: int,
    version_id_2: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Compare two template versions
    Két sablon verzió összehasonlítása
    """
    try:
        service = WYSIWYGTemplateService(db)
        comparison = service.compare_template_versions(version_id_1, version_id_2)
        
        return {
            "success": True,
            "comparison": comparison
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compare versions: {e}")


@router.post("/upload/editor-asset")
async def upload_editor_asset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload asset for WYSIWYG editor (images, etc.)
    Asset feltöltés WYSIWYG szerkesztőhöz (képek, stb.)
    """
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Validate file size (5MB max)
        max_size = 5 * 1024 * 1024  # 5MB
        content = await file.read()
        if len(content) > max_size:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB")
        
        # Generate filename
        import uuid
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        new_filename = f"editor_asset_{uuid.uuid4().hex[:8]}.{file_extension}"
        
        # Save file
        asset_dir = "/var/garagereg/editor_assets"
        os.makedirs(asset_dir, exist_ok=True)
        
        file_path = os.path.join(asset_dir, new_filename)
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Generate URL
        asset_url = f"https://garagereg.local/api/assets/editor/{new_filename}"
        
        return {
            "success": True,
            "asset": {
                "filename": new_filename,
                "url": asset_url,
                "size": len(content),
                "content_type": file.content_type
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload asset: {e}")


@router.get("/editor-config")
async def get_editor_config(
    current_user: User = Depends(get_current_user)
):
    """
    Get WYSIWYG editor configuration
    WYSIWYG szerkesztő konfiguráció lekérése
    """
    try:
        # TinyMCE configuration
        tinymce_config = {
            "height": 600,
            "plugins": [
                "advlist", "autolink", "lists", "link", "image", "charmap", "preview",
                "anchor", "searchreplace", "visualblocks", "code", "fullscreen",
                "insertdatetime", "media", "table", "help", "wordcount", "template",
                "pagebreak", "nonbreaking", "emoticons", "codesample"
            ],
            "toolbar": [
                "undo redo | styles | bold italic underline strikethrough | alignleft aligncenter alignright alignjustify",
                "bullist numlist outdent indent | link image media table | forecolor backcolor | code preview fullscreen help"
            ],
            "menubar": "file edit view insert format tools table help",
            "content_style": "body { font-family: Helvetica, Arial, sans-serif; font-size: 14px }",
            "images_upload_url": "/api/admin/wysiwyg-templates/upload/editor-asset",
            "automatic_uploads": True,
            "file_picker_types": "image",
            "templates": [
                {
                    "title": "Alapértelmezett sablon",
                    "description": "Alapértelmezett dokumentum sablon",
                    "content": """
                    <div class="document-header">
                        <h1>{{document_title}}</h1>
                        <p>Dokumentum száma: {{document_number}}</p>
                        <p>Dátum: {{generation.date}}</p>
                    </div>
                    <div class="document-content">
                        <p>Dokumentum tartalma...</p>
                    </div>
                    """
                },
                {
                    "title": "Ellenőrzési jegyzőkönyv",
                    "description": "Kapu ellenőrzési jegyzőkönyv sablon",
                    "content": """
                    <div class="inspection-report">
                        <h2>Ellenőrzési Jegyzőkönyv</h2>
                        <table>
                            <tr><td>Kapu azonosító:</td><td>{{gate.id}}</td></tr>
                            <tr><td>Kapu neve:</td><td>{{gate.name}}</td></tr>
                            <tr><td>Ellenőrzés típusa:</td><td>{{inspection.type}}</td></tr>
                            <tr><td>Ellenőrzés dátuma:</td><td>{{inspection.date}}</td></tr>
                            <tr><td>Eredmény:</td><td>{{inspection.result}}</td></tr>
                        </table>
                    </div>
                    """
                }
            ]
        }
        
        return {
            "success": True,
            "editor_config": {
                "tinymce": tinymce_config,
                "available_variables": {
                    "document": [
                        "document_number", "document_title", "generation.date", 
                        "generation.generated_by"
                    ],
                    "organization": [
                        "organization.name", "organization.address", 
                        "organization.tax_number", "organization.registration_number"
                    ],
                    "gate": [
                        "gate.id", "gate.name", "gate.location", "gate.type"
                    ],
                    "inspector": [
                        "inspector.name", "inspector.display_name", 
                        "inspector.license_number"
                    ],
                    "inspection": [
                        "inspection.id", "inspection.type", "inspection.date", 
                        "inspection.result"
                    ]
                },
                "css_classes": [
                    "document-header", "document-content", "document-footer",
                    "inspection-report", "gate-details", "inspector-details",
                    "highlight", "important", "warning", "success"
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get editor config: {e}")