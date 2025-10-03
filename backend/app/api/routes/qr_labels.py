"""
QR címkék API endpoints
"""
import io
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.deps import get_db, get_current_active_user
from app.core.rbac import require_permission, RBACPermission, Resources, PermissionActions
from app.models.auth import User
from app.services.qr_labels import QRLabelService
from app.models.organization import Gate

router = APIRouter(prefix="/qr-labels", tags=["qr-labels"])


class BulkLabelRequest(BaseModel):
    """Tömeges címke generálás kérés"""
    gate_ids: Optional[List[int]] = None
    building_ids: Optional[List[int]] = None
    site_ids: Optional[List[int]] = None
    client_ids: Optional[List[int]] = None
    include_inactive: bool = False
    labels_per_row: int = 3
    labels_per_page: int = 9


class FactoryQRImportResult(BaseModel):
    """Gyári QR import eredmény"""
    success_count: int
    error_count: int
    errors: List[str]
    batch_name: str


class QRMappingRequest(BaseModel):
    """Gyári QR mapping generálás kérés"""
    gate_count: int
    batch_name: Optional[str] = None


@router.post("/bulk-pdf", response_class=Response)
@require_permission(Resource.GATES, Permission.READ)
async def generate_bulk_labels_pdf(
    request: BulkLabelRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Tömeges QR címke PDF generálása
    """
    qr_service = QRLabelService()
    
    # Kapuk lekérdezése
    gates = qr_service.get_gates_for_labels(
        db=db,
        gate_ids=request.gate_ids,
        building_ids=request.building_ids,
        site_ids=request.site_ids,
        client_ids=request.client_ids,
        include_inactive=request.include_inactive
    )
    
    if not gates:
        raise HTTPException(
            status_code=404,
            detail="Nem találhatók kapuk a megadott szűrőkkel"
        )
    
    # PDF generálása
    pdf_data = qr_service.create_bulk_labels_pdf(
        gates=gates,
        labels_per_row=request.labels_per_row,
        labels_per_page=request.labels_per_page
    )
    
    return Response(
        content=pdf_data,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=qr_labels_{len(gates)}_gates.pdf"
        }
    )


@router.get("/sample-pdf", response_class=Response)
@require_permission(Resource.GATES, Permission.READ)
async def generate_sample_labels(
    count: int = Query(6, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Minta QR címkék generálása
    """
    qr_service = QRLabelService()
    
    pdf_data = qr_service.create_sample_labels(db=db, count=count)
    
    return Response(
        content=pdf_data,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=sample_qr_labels_{count}.pdf"
        }
    )


@router.post("/factory-qr/import", response_model=FactoryQRImportResult)
@require_permission(Resource.GATES, Permission.UPDATE)
async def import_factory_qr_csv(
    file: UploadFile = File(...),
    batch_name: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Gyári QR CSV import
    
    Várható CSV formátum:
    - gate_id,factory_qr
    - gate_code,factory_qr  
    - kapu_id,qr_token
    """
    # Fájl típus ellenőrzés
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Csak CSV fájlok támogatottak"
        )
    
    # CSV tartalom beolvasása
    try:
        csv_content = (await file.read()).decode('utf-8')
    except UnicodeDecodeError:
        try:
            csv_content = (await file.read()).decode('iso-8859-1')
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Nem sikerült beolvasni a CSV fájlt: {str(e)}"
            )
    
    # Import végrehajtása
    qr_service = QRLabelService()
    success_count, error_count, errors = qr_service.import_factory_qr_csv(
        db=db,
        csv_content=csv_content,
        batch_name=batch_name
    )
    
    return FactoryQRImportResult(
        success_count=success_count,
        error_count=error_count,
        errors=errors,
        batch_name=batch_name or f"import_{file.filename}"
    )


@router.post("/factory-qr/generate-mapping")
@require_permission(Resource.GATES, Permission.CREATE)  
async def generate_factory_qr_mapping(
    request: QRMappingRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Gyári QR mapping CSV generálása
    """
    if request.gate_count <= 0 or request.gate_count > 10000:
        raise HTTPException(
            status_code=400,
            detail="A kapuk száma 1 és 10000 között kell legyen"
        )
    
    qr_service = QRLabelService()
    csv_content = qr_service.generate_factory_qr_mapping(
        gate_count=request.gate_count,
        batch_name=request.batch_name
    )
    
    # CSV válasz
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=factory_qr_mapping_{request.gate_count}.csv"
        }
    )


@router.get("/gates/eligible")
@require_permission(Resource.GATES, Permission.READ)
async def get_eligible_gates(
    building_id: Optional[int] = Query(None),
    site_id: Optional[int] = Query(None),
    client_id: Optional[int] = Query(None),
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Címkézésre alkalmas kapuk listázása
    """
    qr_service = QRLabelService()
    
    gates = qr_service.get_gates_for_labels(
        db=db,
        building_ids=[building_id] if building_id else None,
        site_ids=[site_id] if site_id else None,
        client_ids=[client_id] if client_id else None,
        include_inactive=include_inactive
    )
    
    gate_list = []
    for gate in gates:
        gate_info = {
            "id": gate.id,
            "name": gate.name,
            "display_name": gate.display_name,
            "gate_code": gate.gate_code,
            "gate_type": gate.gate_type,
            "has_factory_qr": bool(gate.factory_qr_token),
            "factory_qr_batch": gate.factory_qr_batch,
            "building": {
                "id": gate.building.id,
                "name": gate.building.display_name or gate.building.name
            } if gate.building else None,
            "site": {
                "id": gate.building.site.id if gate.building and gate.building.site else None,
                "name": gate.building.site.display_name or gate.building.site.name if gate.building and gate.building.site else None
            },
            "client": {
                "id": gate.building.site.client.id if gate.building and gate.building.site and gate.building.site.client else None,
                "name": gate.building.site.client.display_name or gate.building.site.client.name if gate.building and gate.building.site and gate.building.site.client else None
            }
        }
        gate_list.append(gate_info)
    
    return {
        "gates": gate_list,
        "total": len(gate_list)
    }


@router.get("/factory-qr/stats")
@require_permission(Resource.GATES, Permission.READ)
async def get_factory_qr_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Gyári QR statisztikák
    """
    from sqlalchemy import func
    
    # Összes kapu
    total_gates = db.query(func.count(Gate.id)).scalar() or 0
    
    # Gyári QR-rel rendelkező kapuk
    gates_with_factory_qr = db.query(func.count(Gate.id)).filter(
        Gate.factory_qr_token.isnot(None)
    ).scalar() or 0
    
    # Batch statisztikák
    batch_stats = db.query(
        Gate.factory_qr_batch,
        func.count(Gate.id).label('count')
    ).filter(
        Gate.factory_qr_batch.isnot(None)
    ).group_by(Gate.factory_qr_batch).all()
    
    return {
        "total_gates": total_gates,
        "gates_with_factory_qr": gates_with_factory_qr,
        "gates_without_factory_qr": total_gates - gates_with_factory_qr,
        "factory_qr_coverage": round(gates_with_factory_qr / total_gates * 100, 2) if total_gates > 0 else 0,
        "batches": [
            {
                "batch_name": batch[0],
                "gate_count": batch[1]
            }
            for batch in batch_stats
        ]
    }