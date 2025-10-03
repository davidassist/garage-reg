"""API routes for QR/NFC label generation and gate field access."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from app.database import get_db
from app.core.rbac import require_permissions, RBACPermission
from app.core.rbac import get_current_active_user
from app.models.auth import User
from app.models.organization import Gate
from app.services.label_service import LabelService
from app.schemas.labels import (
    QRCodeResponse, NFCDataResponse, TokenRotationResponse, 
    GateFieldAccessResponse, LabelGenerationRequest
)

router = APIRouter(prefix="/api/v1/labels", tags=["labels"])


@router.get("/qr/{gate_id}.png")
@require_permissions([RBACPermission.VIEW_GATES])
async def generate_qr_code(
    gate_id: int,
    size: int = Query(200, ge=50, le=1000, description="QR code size in pixels"),
    expires_hours: int = Query(168, ge=1, le=720, description="Token expiration in hours (max 30 days)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate QR code for gate field access.
    
    Returns PNG image data for the QR code containing a signed field token.
    Default expiration is 7 days (168 hours).
    """
    label_service = LabelService(db)
    
    try:
        qr_data = label_service.generate_qr_code(
            gate_id=gate_id,
            org_id=current_user.organization_id,
            size=size,
            expires_hours=expires_hours
        )
        
        return Response(
            content=qr_data,
            media_type="image/png",
            headers={
                "Content-Disposition": f"inline; filename=gate_{gate_id}_qr.png",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/qr/{gate_id}", response_model=QRCodeResponse)
@require_permissions([RBACPermission.VIEW_GATES])
async def get_qr_code_info(
    gate_id: int,
    expires_hours: int = Query(168, ge=1, le=720, description="Token expiration in hours"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get QR code information without generating the image.
    
    Returns the token and URL that would be embedded in the QR code.
    """
    label_service = LabelService(db)
    
    try:
        # Generate token
        token = label_service.generate_field_token(
            gate_id=gate_id,
            org_id=current_user.organization_id,
            expires_hours=expires_hours
        )
        
        # Get gate info
        gate = db.query(Gate).filter(
            Gate.id == gate_id,
            Gate.org_id == current_user.organization_id
        ).first()
        
        if not gate:
            raise HTTPException(status_code=404, detail="Gate not found")
        
        from app.core.config import get_settings
        settings = get_settings()
        base_url = settings.FRONTEND_URL or "https://garagereg.example.com"
        
        return QRCodeResponse(
            gate_id=gate_id,
            gate_name=gate.name,
            token=token,
            url=f"{base_url}/field/{token}",
            expires_hours=expires_hours,
            qr_image_url=f"/api/v1/labels/qr/{gate_id}.png?expires_hours={expires_hours}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nfc/{gate_id}", response_model=NFCDataResponse)
@require_permissions([RBACPermission.VIEW_GATES])
async def generate_nfc_data(
    gate_id: int,
    expires_hours: int = Query(720, ge=1, le=8760, description="Token expiration in hours (max 1 year)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate NFC tag data for gate field access.
    
    Returns NFC NDEF data structure for programming NFC tags.
    Default expiration is 30 days (720 hours).
    """
    label_service = LabelService(db)
    
    try:
        nfc_data = label_service.generate_nfc_data(
            gate_id=gate_id,
            org_id=current_user.organization_id,
            expires_hours=expires_hours
        )
        
        return NFCDataResponse(
            gate_id=gate_id,
            nfc_data=nfc_data,
            expires_hours=expires_hours
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rotate/{gate_id}", response_model=TokenRotationResponse)
@require_permissions([RBACPermission.MANAGE_GATES])
async def rotate_gate_tokens(
    gate_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Rotate all tokens for a gate (invalidates existing QR/NFC tokens).
    
    Use this when tokens are compromised or need to be refreshed.
    Returns new token information.
    """
    label_service = LabelService(db)
    
    try:
        result = label_service.rotate_gate_tokens(
            gate_id=gate_id,
            org_id=current_user.organization_id
        )
        
        return TokenRotationResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=dict)
@require_permissions([RBACPermission.VIEW_GATES])
async def generate_label_image(
    request: LabelGenerationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate printable label with QR code and gate information.
    
    Supports different label formats for Zebra, Brother, and standard printers.
    """
    label_service = LabelService(db)
    
    try:
        # Generate label image
        label_data = label_service.generate_label_image(
            gate_id=request.gate_id,
            org_id=current_user.organization_id,
            label_type=request.label_type,
            width=request.width,
            height=request.height
        )
        
        # Get gate for additional info
        gate = db.query(Gate).filter(
            Gate.id == request.gate_id,
            Gate.org_id == current_user.organization_id
        ).first()
        
        if not gate:
            raise HTTPException(status_code=404, detail="Gate not found")
        
        response_data = {
            "gate_id": request.gate_id,
            "gate_name": gate.name,
            "label_type": request.label_type,
            "width": request.width,
            "height": request.height,
            "image_base64": label_data.hex() if isinstance(label_data, bytes) else label_data,
            "download_url": f"/api/v1/labels/download/{request.gate_id}?type={request.label_type}&width={request.width}&height={request.height}"
        }
        
        # Add printer-specific templates if requested
        if request.include_printer_templates:
            from app.services.label_service import create_zebra_zpl_template, create_brother_ptouch_template
            
            templates = {}
            
            if request.label_type in ["zebra", "standard"]:
                templates["zebra_zpl"] = create_zebra_zpl_template(
                    gate.name,
                    gate.gate_code or f"G{gate.id:04d}",
                    "QR_DATA_PLACEHOLDER"  # Would need actual ZPL QR encoding
                )
            
            if request.label_type in ["brother", "standard"]:
                templates["brother_ptouch"] = create_brother_ptouch_template(
                    gate.name,
                    gate.gate_code or f"G{gate.id:04d}"
                )
            
            response_data["printer_templates"] = templates
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{gate_id}")
@require_permissions([RBACPermission.VIEW_GATES])
async def download_label_image(
    gate_id: int,
    label_type: str = Query("standard", description="Label type"),
    width: int = Query(400, ge=200, le=1200),
    height: int = Query(300, ge=150, le=900),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Download printable label image as PNG file.
    """
    label_service = LabelService(db)
    
    try:
        label_data = label_service.generate_label_image(
            gate_id=gate_id,
            org_id=current_user.organization_id,
            label_type=label_type,
            width=width,
            height=height
        )
        
        return Response(
            content=label_data,
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename=gate_{gate_id}_label_{label_type}.png"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Public gate field access endpoint (no authentication required)
@router.get("/field/{token}", response_model=GateFieldAccessResponse)
async def access_gate_by_token(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Access gate information using QR/NFC field token.
    
    This endpoint is used by mobile devices scanning QR codes or NFC tags.
    No authentication required - the token provides the authorization.
    """
    label_service = LabelService(db)
    
    try:
        # Verify token and get payload
        payload = label_service.verify_field_token(token)
        
        gate_id = payload["gate_id"]
        org_id = payload["org_id"]
        
        # Get gate information
        gate = db.query(Gate).filter(
            Gate.id == gate_id,
            Gate.org_id == org_id,
            Gate.is_active == True
        ).first()
        
        if not gate:
            raise HTTPException(status_code=404, detail="Gate not found or inactive")
        
        # Get related information (building, site, client)
        from app.models.organization import Building, Site, Client
        
        building = db.query(Building).filter(Building.id == gate.building_id).first()
        site = db.query(Site).filter(Site.id == building.site_id).first() if building else None
        client = db.query(Client).filter(Client.id == site.client_id).first() if site else None
        
        return GateFieldAccessResponse(
            gate_id=gate.id,
            gate_name=gate.name,
            gate_code=gate.gate_code,
            gate_type=gate.gate_type,
            status=gate.status,
            manufacturer=gate.manufacturer,
            model=gate.model,
            serial_number=gate.serial_number,
            installation_date=gate.installation_date,
            last_maintenance_date=gate.last_maintenance_date,
            next_maintenance_date=gate.next_maintenance_date,
            current_cycle_count=gate.current_cycle_count,
            building_name=building.name if building else None,
            site_name=site.name if site else None,
            client_name=client.name if client else None,
            token_expires_at=payload["exp"],
            access_granted_at=payload["iat"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Field access failed: {str(e)}")


# Alternative endpoint for backwards compatibility
@router.get("/gates/{qr_or_nfc_token}", response_model=GateFieldAccessResponse)
async def get_gate_by_token(
    qr_or_nfc_token: str,
    db: Session = Depends(get_db)
):
    """
    Legacy endpoint: GET /gates/{qr_or_nfc_token} — eszközlap kinyitása token alapján.
    
    Redirects to the new field access endpoint for backwards compatibility.
    """
    return await access_gate_by_token(qr_or_nfc_token, db)