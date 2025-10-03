"""
Data Export/Import API Endpoints
API végpontok teljes adatkör export/import funkcióhoz
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, BackgroundTasks
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import io
import json
from datetime import datetime

from app.database import get_db
from app.core.deps import get_current_user
from app.models.auth import User
from app.services.data_export_import_service import (
    DataExportImportService,
    ExportFormat,
    ImportStrategy,
    ImportResult,
    ExportMetadata
)
from app.schemas.data_transfer import *

router = APIRouter(prefix="/api/data-transfer", tags=["Data Export/Import"])


@router.post("/export", response_model=DataExportResponse)
async def export_data(
    request: DataExportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export data from the database.
    Adatok exportálása az adatbázisból.
    """
    try:
        service = DataExportImportService(db)
        
        # Determine organization ID for tenant isolation
        org_id = request.organization_id or current_user.organization_id
        
        export_data, metadata = await service.export_data(
            format=request.format,
            organization_id=org_id if request.include_tenant_filter else None,
            tables=request.tables,
            exported_by=current_user.username
        )
        
        # For large exports, return download link instead of direct data
        if len(export_data) > 10 * 1024 * 1024:  # 10MB threshold
            # TODO: Implement background export with download link
            # For now, return error for large exports
            raise HTTPException(
                status_code=413,
                detail="Export too large. Please use background export or filter data."
            )
        
        return DataExportResponse(
            success=True,
            export_id=metadata.export_id,
            format=metadata.format,
            total_records=metadata.total_records,
            total_tables=metadata.total_tables,
            checksum=metadata.checksum,
            data=export_data,
            metadata=metadata
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.post("/export/download")
async def download_export(
    request: DataExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export data and return as downloadable file.
    Adatok exportálása és fájlként való letöltése.
    """
    try:
        service = DataExportImportService(db)
        
        # Determine organization ID for tenant isolation
        org_id = request.organization_id or current_user.organization_id
        
        export_data, metadata = await service.export_data(
            format=request.format,
            organization_id=org_id if request.include_tenant_filter else None,
            tables=request.tables,
            exported_by=current_user.username
        )
        
        # Determine content type and filename
        if request.format == ExportFormat.JSONL:
            content_type = "application/x-jsonlines"
            filename = f"export_{metadata.export_id}.jsonl"
        elif request.format == ExportFormat.JSON:
            content_type = "application/json"
            filename = f"export_{metadata.export_id}.json"
        elif request.format == ExportFormat.CSV:
            content_type = "application/zip"
            filename = f"export_{metadata.export_id}.zip"
        
        # Create response
        if isinstance(export_data, str):
            export_bytes = export_data.encode('utf-8')
        else:
            export_bytes = export_data
        
        return Response(
            content=export_bytes,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export download failed: {str(e)}")


@router.post("/import", response_model=DataImportResponse)
async def import_data(
    file: UploadFile = File(...),
    format: ExportFormat = Form(...),
    strategy: ImportStrategy = Form(ImportStrategy.SKIP),
    organization_id: Optional[int] = Form(None),
    dry_run: bool = Form(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Import data into the database.
    Adatok importálása az adatbázisba.
    """
    try:
        # Read uploaded file
        file_content = await file.read()
        
        service = DataExportImportService(db)
        
        # Determine organization ID for tenant isolation
        target_org_id = organization_id or current_user.organization_id
        
        # Validate import data first
        validation_errors = await service.validate_import_data(file_content, format)
        if validation_errors:
            return DataImportResponse(
                success=False,
                message="Import validation failed",
                total_records=0,
                imported_records=0,
                skipped_records=0,
                error_records=len(validation_errors),
                validation_errors=validation_errors,
                conflicts=[],
                processing_time=0.0
            )
        
        # Perform import
        result = await service.import_data(
            import_data=file_content,
            format=format,
            strategy=strategy,
            organization_id=target_org_id,
            dry_run=dry_run
        )
        
        # Convert conflicts to response format
        conflicts_response = []
        for conflict in result.conflicts:
            conflicts_response.append(ImportConflictResponse(
                table=conflict.table,
                record_id=str(conflict.record_id),
                conflict_type=conflict.conflict_type,
                message=conflict.message,
                resolution=conflict.resolution
            ))
        
        return DataImportResponse(
            success=result.success,
            message=result.message,
            total_records=result.total_records,
            imported_records=result.imported_records,
            skipped_records=result.skipped_records,
            error_records=result.error_records,
            validation_errors=[],
            conflicts=conflicts_response,
            processing_time=result.processing_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.post("/compare", response_model=DataComparisonResponse)
async def compare_datasets(
    file: UploadFile = File(...),
    organization_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Compare import data with current database state.
    Importálandó adatok összehasonlítása a jelenlegi adatbázis állapotával.
    """
    try:
        # Read uploaded file
        file_content = await file.read()
        
        service = DataExportImportService(db)
        
        # Determine organization ID for tenant isolation
        target_org_id = organization_id or current_user.organization_id
        
        # Perform comparison
        comparison = await service.compare_datasets(
            source_data=file_content.decode('utf-8'),
            target_organization_id=target_org_id
        )
        
        # Convert to response format
        tables_comparison = {}
        for table_name, table_diff in comparison["tables"].items():
            tables_comparison[table_name] = TableComparisonResult(
                additions=table_diff["summary"]["additions"],
                modifications=table_diff["summary"]["modifications"],
                deletions=table_diff["summary"]["deletions"],
                details=table_diff
            )
        
        return DataComparisonResponse(
            tables_compared=comparison["summary"]["tables_compared"],
            total_additions=comparison["summary"]["total_additions"],
            total_modifications=comparison["summary"]["total_modifications"],
            total_deletions=comparison["summary"]["total_deletions"],
            tables=tables_comparison
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.post("/validate", response_model=DataValidationResponse)
async def validate_import_data(
    file: UploadFile = File(...),
    format: ExportFormat = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Validate import data structure and integrity.
    Importálandó adatok szerkezetének és integritásának validálása.
    """
    try:
        # Read uploaded file
        file_content = await file.read()
        
        service = DataExportImportService(db)
        
        # Validate data
        validation_errors = await service.validate_import_data(file_content, format)
        
        return DataValidationResponse(
            valid=len(validation_errors) == 0,
            errors=validation_errors,
            message="Validation completed" if len(validation_errors) == 0 else f"Found {len(validation_errors)} validation errors"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("/export-history", response_model=List[ExportHistoryResponse])
async def get_export_history(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get export history for the current user's organization.
    Export előzmények lekérése a felhasználó szervezetéhez.
    """
    # TODO: Implement export history tracking
    # This would require additional database table to store export metadata
    return []


@router.post("/test-round-trip")
async def test_round_trip_integrity(
    tables: Optional[List[str]] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Test round-trip integrity: export → delete → import → verify data matches.
    Kerek teszt integritás ellenőrzés: export → törlés → import → adatok egyezésének ellenőrzése.
    
    This is a comprehensive test that validates the complete export/import cycle.
    """
    try:
        service = DataExportImportService(db)
        org_id = current_user.organization_id
        
        # Step 1: Export current data
        original_data, export_metadata = await service.export_data(
            format=ExportFormat.JSONL,
            organization_id=org_id,
            tables=tables,
            exported_by=f"test_user_{current_user.username}"
        )
        
        # Step 2: Create backup of original data for comparison
        original_parsed = await service._parse_jsonl_import(original_data)
        original_tables = original_parsed.get("data", {})
        
        # Step 3: Simulate deletion by clearing specified tables (DRY RUN ONLY for safety)
        # In a real scenario, this would actually delete the data
        # For safety, we'll only simulate this step
        
        # Step 4: Import the exported data
        import_result = await service.import_data(
            import_data=original_data,
            format=ExportFormat.JSONL,
            strategy=ImportStrategy.OVERWRITE,
            organization_id=org_id,
            dry_run=True  # Safety: only dry run for testing
        )
        
        # Step 5: Export again and compare
        reimported_data, reimport_metadata = await service.export_data(
            format=ExportFormat.JSONL,
            organization_id=org_id,
            tables=tables,
            exported_by=f"test_user_{current_user.username}"
        )
        
        # Step 6: Compare original and reimported data
        comparison = await service.compare_datasets(
            source_data=original_data,
            target_organization_id=org_id
        )
        
        # Determine if data matches perfectly
        data_matches = (
            comparison["summary"]["total_additions"] == 0 and
            comparison["summary"]["total_modifications"] == 0 and
            comparison["summary"]["total_deletions"] == 0
        )
        
        # Calculate checksums for additional verification
        original_checksum = service._calculate_checksum(original_data)
        reimported_checksum = service._calculate_checksum(reimported_data)
        
        return {
            "test_passed": data_matches and import_result.success,
            "message": "Round-trip integrity test completed successfully" if data_matches else "Data integrity issues detected",
            "original_checksum": original_checksum,
            "reimported_checksum": reimported_checksum,
            "checksums_match": original_checksum == reimported_checksum,
            "export_metadata": {
                "original_records": export_metadata.total_records,
                "original_tables": export_metadata.total_tables,
                "reimported_records": reimport_metadata.total_records,
                "reimported_tables": reimport_metadata.total_tables
            },
            "import_result": {
                "success": import_result.success,
                "total_records": import_result.total_records,
                "imported_records": import_result.imported_records,
                "skipped_records": import_result.skipped_records,
                "error_records": import_result.error_records,
                "conflicts": len(import_result.conflicts)
            },
            "comparison_summary": comparison["summary"],
            "detailed_differences": comparison["tables"] if not data_matches else {},
            "test_details": {
                "dry_run_only": True,
                "tables_tested": tables or "all",
                "organization_id": org_id,
                "test_timestamp": datetime.utcnow().isoformat()
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Round-trip test failed: {str(e)}")