"""API routes for organizational hierarchy (Client/Site/Building/Gate structure)."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.rbac import require_permissions, RBACPermission
from app.core.rbac import get_current_active_user
from app.models.auth import User
from app.services.structure import ClientService, SiteService, BuildingService, GateService
from app.schemas.structure import (
    # Client schemas
    ClientCreate, ClientUpdate, ClientResponse, ClientSearchParams, ClientWithStats,
    # Site schemas  
    SiteCreate, SiteUpdate, SiteResponse, SiteSearchParams, SiteWithStats,
    # Building schemas
    BuildingCreate, BuildingUpdate, BuildingResponse, BuildingSearchParams, BuildingWithStats,
    # Gate schemas
    GateCreate, GateUpdate, GateResponse, GateSearchParams,
    # Common schemas
    PaginationParams, PaginatedResponse
)

router = APIRouter(prefix="/api/v1/structure", tags=["structure"])


# Client endpoints
@router.post("/clients", response_model=ClientResponse)
@require_permissions([RBACPermission.MANAGE_CLIENTS])
async def create_client(
    client_data: ClientCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new client."""
    service = ClientService(db)
    return service.create_client(current_user.organization_id, client_data)


@router.get("/clients/{client_id}", response_model=ClientWithStats)
@require_permissions([RBACPermission.VIEW_CLIENTS])
async def get_client(
    client_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get client by ID with statistics."""
    service = ClientService(db)
    client = service.get_client(current_user.organization_id, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Add statistics
    stats = service.get_client_stats(current_user.organization_id, client_id)
    client_dict = client.__dict__.copy()
    client_dict.update(stats)
    
    return ClientWithStats(**client_dict)


@router.get("/clients", response_model=PaginatedResponse)
@require_permissions([RBACPermission.VIEW_CLIENTS])
async def get_clients(
    # Search parameters
    query: str = Query(None, description="Search query"),
    type: str = Query(None, description="Client type filter"),
    city: str = Query(None, description="City filter"),
    is_active: bool = Query(None, description="Active status filter"),
    # Pagination parameters
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get clients with search and pagination."""
    search_params = ClientSearchParams(
        query=query, type=type, city=city, is_active=is_active
    )
    pagination_params = PaginationParams(page=page, size=size)
    
    service = ClientService(db)
    clients, total = service.get_clients(
        current_user.organization_id, search_params, pagination_params
    )
    
    pages = (total + size - 1) // size
    
    return PaginatedResponse(
        items=[ClientResponse.model_validate(client) for client in clients],
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.put("/clients/{client_id}", response_model=ClientResponse)
@require_permissions([RBACPermission.MANAGE_CLIENTS])
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update client."""
    service = ClientService(db)
    client = service.update_client(current_user.organization_id, client_id, client_data)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.delete("/clients/{client_id}")
@require_permissions([RBACPermission.MANAGE_CLIENTS])
async def delete_client(
    client_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete client (soft delete)."""
    service = ClientService(db)
    success = service.delete_client(current_user.organization_id, client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Client deleted successfully"}


# Site endpoints
@router.post("/sites", response_model=SiteResponse)
@require_permissions([RBACPermission.MANAGE_SITES])
async def create_site(
    site_data: SiteCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new site."""
    service = SiteService(db)
    return service.create_site(current_user.organization_id, site_data)


@router.get("/sites/{site_id}", response_model=SiteWithStats)
@require_permissions([RBACPermission.VIEW_SITES])
async def get_site(
    site_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get site by ID with statistics."""
    service = SiteService(db)
    site = service.get_site(current_user.organization_id, site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    # Add statistics
    stats = service.get_site_stats(current_user.organization_id, site_id)
    site_dict = site.__dict__.copy()
    site_dict.update(stats)
    
    return SiteWithStats(**site_dict)


@router.get("/sites", response_model=PaginatedResponse)
@require_permissions([RBACPermission.VIEW_SITES])
async def get_sites(
    # Search parameters
    query: str = Query(None, description="Search query"),
    client_id: int = Query(None, description="Client ID filter"),
    city: str = Query(None, description="City filter"),
    is_active: bool = Query(None, description="Active status filter"),
    # Pagination parameters
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get sites with search and pagination."""
    search_params = SiteSearchParams(
        query=query, client_id=client_id, city=city, is_active=is_active
    )
    pagination_params = PaginationParams(page=page, size=size)
    
    service = SiteService(db)
    sites, total = service.get_sites(
        current_user.organization_id, search_params, pagination_params
    )
    
    pages = (total + size - 1) // size
    
    return PaginatedResponse(
        items=[SiteResponse.model_validate(site) for site in sites],
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.put("/sites/{site_id}", response_model=SiteResponse)
@require_permissions([RBACPermission.MANAGE_SITES])
async def update_site(
    site_id: int,
    site_data: SiteUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update site."""
    service = SiteService(db)
    site = service.update_site(current_user.organization_id, site_id, site_data)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site


@router.delete("/sites/{site_id}")
@require_permissions([RBACPermission.MANAGE_SITES])
async def delete_site(
    site_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete site (soft delete)."""
    service = SiteService(db)
    success = service.delete_site(current_user.organization_id, site_id)
    if not success:
        raise HTTPException(status_code=404, detail="Site not found")
    return {"message": "Site deleted successfully"}


# Building endpoints
@router.post("/buildings", response_model=BuildingResponse)
@require_permissions([RBACPermission.MANAGE_BUILDINGS])
async def create_building(
    building_data: BuildingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new building."""
    service = BuildingService(db)
    return service.create_building(current_user.organization_id, building_data)


@router.get("/buildings/{building_id}", response_model=BuildingWithStats)
@require_permissions([RBACPermission.VIEW_BUILDINGS])
async def get_building(
    building_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get building by ID with statistics."""
    service = BuildingService(db)
    building = service.get_building(current_user.organization_id, building_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    
    # Add statistics
    stats = service.get_building_stats(current_user.organization_id, building_id)
    building_dict = building.__dict__.copy()
    building_dict.update(stats)
    
    return BuildingWithStats(**building_dict)


@router.get("/buildings", response_model=PaginatedResponse)
@require_permissions([RBACPermission.VIEW_BUILDINGS])
async def get_buildings(
    # Search parameters
    query: str = Query(None, description="Search query"),
    site_id: int = Query(None, description="Site ID filter"),
    building_type: str = Query(None, description="Building type filter"),
    is_active: bool = Query(None, description="Active status filter"),
    # Pagination parameters
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get buildings with search and pagination."""
    search_params = BuildingSearchParams(
        query=query, site_id=site_id, building_type=building_type, is_active=is_active
    )
    pagination_params = PaginationParams(page=page, size=size)
    
    service = BuildingService(db)
    buildings, total = service.get_buildings(
        current_user.organization_id, search_params, pagination_params
    )
    
    pages = (total + size - 1) // size
    
    return PaginatedResponse(
        items=[BuildingResponse.model_validate(building) for building in buildings],
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.put("/buildings/{building_id}", response_model=BuildingResponse)
@require_permissions([RBACPermission.MANAGE_BUILDINGS])
async def update_building(
    building_id: int,
    building_data: BuildingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update building."""
    service = BuildingService(db)
    building = service.update_building(current_user.organization_id, building_id, building_data)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    return building


@router.delete("/buildings/{building_id}")
@require_permissions([RBACPermission.MANAGE_BUILDINGS])
async def delete_building(
    building_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete building (soft delete)."""
    service = BuildingService(db)
    success = service.delete_building(current_user.organization_id, building_id)
    if not success:
        raise HTTPException(status_code=404, detail="Building not found")
    return {"message": "Building deleted successfully"}


# Gate endpoints
@router.post("/gates", response_model=GateResponse)
@require_permissions([RBACPermission.MANAGE_GATES])
async def create_gate(
    gate_data: GateCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new gate."""
    service = GateService(db)
    return service.create_gate(current_user.organization_id, gate_data)


@router.get("/gates/{gate_id}", response_model=GateResponse)
@require_permissions([RBACPermission.VIEW_GATES])
async def get_gate(
    gate_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get gate by ID."""
    service = GateService(db)
    gate = service.get_gate(current_user.organization_id, gate_id)
    if not gate:
        raise HTTPException(status_code=404, detail="Gate not found")
    return gate


@router.get("/gates", response_model=PaginatedResponse)
@require_permissions([RBACPermission.VIEW_GATES])
async def get_gates(
    # Search parameters
    query: str = Query(None, description="Search query"),
    building_id: int = Query(None, description="Building ID filter"),
    gate_type: str = Query(None, description="Gate type filter"),
    status: str = Query(None, description="Status filter"),
    manufacturer: str = Query(None, description="Manufacturer filter"),
    is_active: bool = Query(None, description="Active status filter"),
    # Pagination parameters
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get gates with search and pagination."""
    search_params = GateSearchParams(
        query=query,
        building_id=building_id,
        gate_type=gate_type,
        status=status,
        manufacturer=manufacturer,
        is_active=is_active
    )
    pagination_params = PaginationParams(page=page, size=size)
    
    service = GateService(db)
    gates, total = service.get_gates(
        current_user.organization_id, search_params, pagination_params
    )
    
    pages = (total + size - 1) // size
    
    return PaginatedResponse(
        items=[GateResponse.model_validate(gate) for gate in gates],
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.put("/gates/{gate_id}", response_model=GateResponse)
@require_permissions([RBACPermission.MANAGE_GATES])
async def update_gate(
    gate_id: int,
    gate_data: GateUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update gate."""
    service = GateService(db)
    gate = service.update_gate(current_user.organization_id, gate_id, gate_data)
    if not gate:
        raise HTTPException(status_code=404, detail="Gate not found")
    return gate


@router.delete("/gates/{gate_id}")
@require_permissions([RBACPermission.MANAGE_GATES])
async def delete_gate(
    gate_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete gate (soft delete)."""
    service = GateService(db)
    success = service.delete_gate(current_user.organization_id, gate_id)
    if not success:
        raise HTTPException(status_code=404, detail="Gate not found")
    return {"message": "Gate deleted successfully"}