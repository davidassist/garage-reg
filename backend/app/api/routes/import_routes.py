"""Import API endpoints for bulk data upload."""

import csv
import io
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.rbac import require_permissions, RBACPermission
from app.core.rbac import get_current_active_user
from app.models.auth import User
from app.services.import_service import BulkImportService, validate_import_file
from app.schemas.structure import ImportResult

router = APIRouter(prefix="/api/v1/import", tags=["import"])


@router.post("/hierarchical", response_model=ImportResult)
@require_permissions([RBACPermission.MANAGE_CLIENTS, RBACPermission.MANAGE_SITES, 
                     RBACPermission.MANAGE_BUILDINGS, RBACPermission.MANAGE_GATES])
async def import_hierarchical_data(
    file: UploadFile = File(..., description="CSV or XLSX file with hierarchical data"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Import hierarchical data (Client → Site → Building → Gate).
    
    Expected columns:
    - client_name (required)
    - client_type (optional: residential, commercial, industrial, mixed)
    - client_contact_person (optional)
    - client_email (optional)
    - client_phone (optional)
    - client_city (optional)
    - site_name (required)
    - site_code (optional)
    - site_city (optional)
    - site_latitude (optional)
    - site_longitude (optional)
    - building_name (required)
    - building_type (optional: residential, office, warehouse, retail, mixed, other)
    - building_floors (optional)
    - building_units (optional)
    - gate_name (required)
    - gate_type (optional: swing, sliding, barrier, bollard, turnstile)
    - manufacturer (optional)
    - model (optional)
    - serial_number (optional)
    - installation_date (optional: YYYY-MM-DD format)
    """
    # Validate file
    required_columns = ['client_name', 'site_name', 'building_name', 'gate_name']
    errors = validate_import_file(file, required_columns)
    if errors:
        raise HTTPException(status_code=400, detail=f"File validation failed: {'; '.join(errors)}")
    
    # Perform import
    import_service = BulkImportService(db, current_user.organization_id)
    result = await import_service.import_from_file(file, "hierarchical")
    
    return result


@router.post("/clients", response_model=ImportResult)
@require_permissions([RBACPermission.MANAGE_CLIENTS])
async def import_clients(
    file: UploadFile = File(..., description="CSV or XLSX file with client data"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Import only client data.
    
    Expected columns:
    - client_name (required)
    - client_type (optional: residential, commercial, industrial, mixed)
    - contact_person (optional)
    - email (optional)
    - phone (optional)
    - address_line_1 (optional)
    - address_line_2 (optional)
    - city (optional)
    - state (optional)
    - postal_code (optional)
    - country (optional)
    - contract_number (optional)
    """
    # Validate file
    required_columns = ['client_name']
    errors = validate_import_file(file, required_columns)
    if errors:
        raise HTTPException(status_code=400, detail=f"File validation failed: {'; '.join(errors)}")
    
    # Perform import
    import_service = BulkImportService(db, current_user.organization_id)
    result = await import_service.import_from_file(file, "clients")
    
    return result


@router.post("/sites", response_model=ImportResult)
@require_permissions([RBACPermission.MANAGE_SITES])
async def import_sites(
    file: UploadFile = File(..., description="CSV or XLSX file with site data"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Import only site data (requires existing clients).
    
    Expected columns:
    - client_name (required) - must match existing client
    - site_name (required)
    - site_code (optional)
    - address_line_1 (optional)
    - address_line_2 (optional)
    - city (optional)
    - state (optional)
    - postal_code (optional)
    - country (optional)
    - latitude (optional)
    - longitude (optional)
    - area_sqm (optional)
    - emergency_contact (optional)
    - emergency_phone (optional)
    """
    # Validate file
    required_columns = ['client_name', 'site_name']
    errors = validate_import_file(file, required_columns)
    if errors:
        raise HTTPException(status_code=400, detail=f"File validation failed: {'; '.join(errors)}")
    
    # Perform import
    import_service = BulkImportService(db, current_user.organization_id)
    result = await import_service.import_from_file(file, "sites")
    
    return result


@router.post("/buildings", response_model=ImportResult)
@require_permissions([RBACPermission.MANAGE_BUILDINGS])
async def import_buildings(
    file: UploadFile = File(..., description="CSV or XLSX file with building data"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Import only building data (requires existing sites).
    
    Expected columns:
    - client_name (required) - must match existing client
    - site_name (required) - must match existing site
    - building_name (required)
    - building_code (optional)
    - building_type (optional: residential, office, warehouse, retail, mixed, other)
    - floors (optional)
    - units (optional)
    - year_built (optional)
    - address_suffix (optional)
    """
    # Validate file
    required_columns = ['client_name', 'site_name', 'building_name']
    errors = validate_import_file(file, required_columns)
    if errors:
        raise HTTPException(status_code=400, detail=f"File validation failed: {'; '.join(errors)}")
    
    # Perform import
    import_service = BulkImportService(db, current_user.organization_id)
    result = await import_service.import_from_file(file, "buildings")
    
    return result


@router.post("/gates", response_model=ImportResult)
@require_permissions([RBACPermission.MANAGE_GATES])
async def import_gates(
    file: UploadFile = File(..., description="CSV or XLSX file with gate data"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Import only gate data (requires existing buildings).
    
    Expected columns:
    - client_name (required) - must match existing client
    - site_name (required) - must match existing site
    - building_name (required) - must match existing building
    - gate_name (required)
    - gate_code (optional)
    - gate_type (optional: swing, sliding, barrier, bollard, turnstile)
    - manufacturer (optional)
    - model (optional)
    - serial_number (optional)
    - installation_date (optional: YYYY-MM-DD format)
    - installer (optional)
    - width_cm (optional)
    - height_cm (optional)
    - weight_kg (optional)
    - material (optional)
    - max_cycles_per_day (optional)
    - current_cycle_count (optional)
    - status (optional: operational, maintenance, broken, decommissioned)
    """
    # Validate file
    required_columns = ['client_name', 'site_name', 'building_name', 'gate_name']
    errors = validate_import_file(file, required_columns)
    if errors:
        raise HTTPException(status_code=400, detail=f"File validation failed: {'; '.join(errors)}")
    
    # Perform import
    import_service = BulkImportService(db, current_user.organization_id)
    result = await import_service.import_from_file(file, "gates")
    
    return result


@router.get("/template/{import_type}")
async def download_import_template(
    import_type: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Download CSV template for import.
    
    Args:
        import_type: Type of template (hierarchical, clients, sites, buildings, gates)
    """
    from fastapi.responses import Response
    import io
    
    templates = {
        "hierarchical": [
            "client_name", "client_type", "client_contact_person", "client_email", "client_phone", "client_city",
            "site_name", "site_code", "site_city", "site_latitude", "site_longitude",
            "building_name", "building_type", "building_floors", "building_units",
            "gate_name", "gate_type", "manufacturer", "model", "serial_number", "installation_date"
        ],
        "clients": [
            "client_name", "client_type", "contact_person", "email", "phone", "address_line_1",
            "address_line_2", "city", "state", "postal_code", "country", "contract_number"
        ],
        "sites": [
            "client_name", "site_name", "site_code", "address_line_1", "address_line_2", "city",
            "state", "postal_code", "country", "latitude", "longitude", "area_sqm",
            "emergency_contact", "emergency_phone"
        ],
        "buildings": [
            "client_name", "site_name", "building_name", "building_code", "building_type",
            "floors", "units", "year_built", "address_suffix"
        ],
        "gates": [
            "client_name", "site_name", "building_name", "gate_name", "gate_code", "gate_type",
            "manufacturer", "model", "serial_number", "installation_date", "installer",
            "width_cm", "height_cm", "weight_kg", "material", "max_cycles_per_day",
            "current_cycle_count", "status"
        ]
    }
    
    if import_type not in templates:
        raise HTTPException(status_code=404, detail=f"Template not found for type: {import_type}")
    
    # Generate CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(templates[import_type])
    
    # Add example row for hierarchical template
    if import_type == "hierarchical":
        writer.writerow([
            "ABC Company", "commercial", "John Doe", "john@abc.com", "+36301234567", "Budapest",
            "Main Site", "MS001", "Budapest", "47.4979", "19.0402",
            "Building A", "office", "3", "12",
            "Gate 1", "sliding", "Came", "BXV-4", "SN123456", "2024-01-15"
        ])
    
    csv_content = output.getvalue()
    output.close()
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={import_type}_template.csv"}
    )