"""
Document generation API endpoints.

Dokumentum generálási API végpontok.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.auth import User
from app.models.documents import Document, DocumentTemplate, DocumentSignature, DocumentType, SignatureType
from app.schemas.documents import (
    DocumentCreate, DocumentResponse, DocumentTemplateResponse,
    SignatureRequest, SignatureResponse, DocumentGenerationRequest,
    OperationalLogRequest, MaintenanceProtocolRequest, WorkSheetRequest
)
from app.services.document_service import DocumentGenerationService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/generate/operational-log", response_model=DocumentResponse)
async def generate_operational_log(
    request: OperationalLogRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate operational log (üzemeltetési napló) for a gate.
    
    Üzemeltetési napló generálása egy kapuhoz.
    """
    try:
        service = DocumentGenerationService(db)
        
        document = service.generate_operational_log(
            gate_id=request.gate_id,
            user_id=current_user.id,
            date_from=request.date_from,
            date_to=request.date_to,
            template_name=request.template_name,
            custom_data=request.custom_data
        )
        
        return DocumentResponse.from_orm(document)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate/maintenance-protocol", response_model=DocumentResponse)
async def generate_maintenance_protocol(
    request: MaintenanceProtocolRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate maintenance protocol (karbantartási jegyzőkönyv) for a work order.
    
    Karbantartási jegyzőkönyv generálása egy munkarendeléshez.
    """
    try:
        service = DocumentGenerationService(db)
        
        document = service.generate_maintenance_protocol(
            work_order_id=request.work_order_id,
            user_id=current_user.id,
            template_name=request.template_name,
            custom_data=request.custom_data
        )
        
        return DocumentResponse.from_orm(document)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate/work-sheet", response_model=DocumentResponse)
async def generate_work_sheet(
    request: WorkSheetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate work sheet (munkalap) for an inspection.
    
    Munkalap generálása egy ellenőrzéshez.
    """
    try:
        service = DocumentGenerationService(db)
        
        document = service.generate_work_sheet(
            inspection_id=request.inspection_id,
            user_id=current_user.id,
            template_name=request.template_name,
            custom_data=request.custom_data
        )
        
        return DocumentResponse.from_orm(document)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{document_id}/sign", response_model=SignatureResponse)
async def sign_document(
    document_id: int,
    request: SignatureRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add digital signature to a document.
    
    Digitális aláírás hozzáadása dokumentumhoz.
    """
    try:
        service = DocumentGenerationService(db)
        
        signature = service.add_digital_signature(
            document_id=document_id,
            signer_id=current_user.id,
            signature_type=request.signature_type,
            signature_data=request.signature_data
        )
        
        return SignatureResponse.from_orm(signature)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download a generated document.
    
    Generált dokumentum letöltése.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.org_id == current_user.org_id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Update download statistics
    document.download_count += 1
    document.last_downloaded_at = datetime.utcnow()
    db.commit()
    
    # In real implementation, return redirect to S3 signed URL
    return {
        "download_url": f"https://s3.amazonaws.com/garagereg-docs/{document.storage_key}",
        "filename": document.filename,
        "content_type": document.content_type,
        "file_size": document.file_size
    }


@router.get("/verify/{document_number}")
async def verify_document(
    document_number: str,
    db: Session = Depends(get_db)
):
    """
    Verify document authenticity via QR code.
    
    Dokumentum hitelességének ellenőrzése QR kóddal.
    """
    document = db.query(Document).filter(
        Document.document_number == document_number,
        Document.is_active == True
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "document_number": document.document_number,
        "title": document.title,
        "document_type": document.document_type,
        "generation_date": document.created_at,
        "is_signed": document.signature_type != SignatureType.NONE.value,
        "signature_type": document.signature_type,
        "signed_at": document.signed_at,
        "file_hash": document.file_hash,
        "status": "valid"
    }


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[int] = Query(None, description="Filter by entity ID"),
    signed_only: bool = Query(False, description="Show only signed documents"),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List generated documents with filtering.
    
    Generált dokumentumok listázása szűréssel.
    """
    query = db.query(Document).filter(
        Document.org_id == current_user.org_id,
        Document.is_active == True
    )
    
    if document_type:
        query = query.filter(Document.document_type == document_type)
    
    if entity_type:
        query = query.filter(Document.entity_type == entity_type)
    
    if entity_id:
        query = query.filter(Document.entity_id == entity_id)
    
    if signed_only:
        query = query.filter(Document.signature_type != SignatureType.NONE.value)
    
    documents = query.order_by(Document.created_at.desc()).offset(offset).limit(limit).all()
    
    return [DocumentResponse.from_orm(doc) for doc in documents]


@router.get("/templates/", response_model=List[DocumentTemplateResponse])
async def list_templates(
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    active_only: bool = Query(True, description="Show only active templates"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List available document templates.
    
    Elérhető dokumentum sablonok listázása.
    """
    query = db.query(DocumentTemplate).filter(
        DocumentTemplate.org_id == current_user.org_id
    )
    
    if document_type:
        query = query.filter(DocumentTemplate.document_type == document_type)
    
    if active_only:
        query = query.filter(DocumentTemplate.is_active == True)
    
    templates = query.order_by(DocumentTemplate.name).all()
    
    return [DocumentTemplateResponse.from_orm(template) for template in templates]


@router.get("/statistics")
async def get_document_statistics(
    days: int = Query(30, description="Number of days to include in statistics"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get document generation statistics.
    
    Dokumentum generálási statisztikák lekérdezése.
    """
    from sqlalchemy import func
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Total documents by type
    type_stats = db.query(
        Document.document_type,
        func.count(Document.id).label('count')
    ).filter(
        Document.org_id == current_user.org_id,
        Document.created_at >= cutoff_date,
        Document.is_active == True
    ).group_by(Document.document_type).all()
    
    # Signature statistics
    signature_stats = db.query(
        Document.signature_type,
        func.count(Document.id).label('count')
    ).filter(
        Document.org_id == current_user.org_id,
        Document.created_at >= cutoff_date,
        Document.is_active == True
    ).group_by(Document.signature_type).all()
    
    # Download statistics
    download_stats = db.query(
        func.sum(Document.download_count).label('total_downloads'),
        func.avg(Document.download_count).label('avg_downloads_per_doc')
    ).filter(
        Document.org_id == current_user.org_id,
        Document.created_at >= cutoff_date,
        Document.is_active == True
    ).first()
    
    return {
        "period_days": days,
        "total_documents": sum(stat.count for stat in type_stats),
        "by_type": {stat.document_type: stat.count for stat in type_stats},
        "by_signature": {stat.signature_type: stat.count for stat in signature_stats},
        "downloads": {
            "total": download_stats.total_downloads or 0,
            "average_per_document": float(download_stats.avg_downloads_per_doc or 0)
        }
    }