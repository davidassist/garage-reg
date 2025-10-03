"""Services for organizational hierarchy CRUD operations."""

from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models.organization import Client, Site, Building, Gate
from app.schemas.structure import (
    ClientCreate, ClientUpdate, ClientSearchParams,
    SiteCreate, SiteUpdate, SiteSearchParams,
    BuildingCreate, BuildingUpdate, BuildingSearchParams,
    GateCreate, GateUpdate, GateSearchParams,
    PaginationParams
)


class BaseHierarchyService:
    """Base service for hierarchy entities."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _apply_pagination(self, query, pagination: PaginationParams):
        """Apply pagination to query."""
        offset = (pagination.page - 1) * pagination.size
        return query.offset(offset).limit(pagination.size)
    
    def _get_total_count(self, query) -> int:
        """Get total count for pagination."""
        return query.count()


class ClientService(BaseHierarchyService):
    """Client CRUD service."""
    
    def create_client(self, org_id: int, client_data: ClientCreate) -> Client:
        """Create a new client."""
        try:
            client = Client(
                organization_id=org_id,
                **client_data.model_dump()
            )
            self.db.add(client)
            self.db.commit()
            self.db.refresh(client)
            return client
        except IntegrityError as e:
            self.db.rollback()
            if "name" in str(e):
                raise HTTPException(
                    status_code=400,
                    detail="Client name already exists in this organization"
                )
            raise HTTPException(status_code=400, detail="Client creation failed")
    
    def get_client(self, org_id: int, client_id: int) -> Optional[Client]:
        """Get client by ID."""
        return self.db.query(Client).filter(
            and_(
                Client.id == client_id,
                Client.organization_id == org_id
            )
        ).first()
    
    def get_clients(
        self, 
        org_id: int,
        search: ClientSearchParams,
        pagination: PaginationParams
    ) -> Tuple[List[Client], int]:
        """Get clients with search and pagination."""
        query = self.db.query(Client).filter(Client.organization_id == org_id)
        
        # Apply search filters
        if search.query:
            search_filter = or_(
                Client.name.ilike(f"%{search.query}%"),
                Client.display_name.ilike(f"%{search.query}%"),
                Client.contact_person.ilike(f"%{search.query}%"),
                Client.email.ilike(f"%{search.query}%"),
                Client.city.ilike(f"%{search.query}%")
            )
            query = query.filter(search_filter)
        
        if search.type is not None:
            query = query.filter(Client.type == search.type)
        
        if search.city is not None:
            query = query.filter(Client.city.ilike(f"%{search.city}%"))
        
        if search.is_active is not None:
            query = query.filter(Client.is_active == search.is_active)
        
        # Get total count
        total = self._get_total_count(query)
        
        # Apply pagination and ordering
        query = query.order_by(asc(Client.name))
        items = self._apply_pagination(query, pagination).all()
        
        return items, total
    
    def update_client(
        self, 
        org_id: int, 
        client_id: int, 
        client_data: ClientUpdate
    ) -> Optional[Client]:
        """Update client."""
        client = self.get_client(org_id, client_id)
        if not client:
            return None
        
        try:
            update_data = client_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(client, field, value)
            
            self.db.commit()
            self.db.refresh(client)
            return client
        except IntegrityError as e:
            self.db.rollback()
            if "name" in str(e):
                raise HTTPException(
                    status_code=400,
                    detail="Client name already exists in this organization"
                )
            raise HTTPException(status_code=400, detail="Client update failed")
    
    def delete_client(self, org_id: int, client_id: int) -> bool:
        """Delete client (soft delete)."""
        client = self.get_client(org_id, client_id)
        if not client:
            return False
        
        # Check if client has active sites
        active_sites = self.db.query(Site).filter(
            and_(Site.client_id == client_id, Site.is_active == True)
        ).count()
        
        if active_sites > 0:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete client with active sites"
            )
        
        client.is_active = False
        self.db.commit()
        return True
    
    def get_client_stats(self, org_id: int, client_id: int) -> Dict[str, int]:
        """Get client statistics."""
        stats = {}
        
        # Count sites
        stats['sites_count'] = self.db.query(Site).filter(
            and_(Site.client_id == client_id, Site.org_id == org_id)
        ).count()
        
        # Count buildings
        stats['buildings_count'] = self.db.query(Building).join(Site).filter(
            and_(Site.client_id == client_id, Building.org_id == org_id)
        ).count()
        
        # Count gates
        stats['gates_count'] = self.db.query(Gate).join(Building).join(Site).filter(
            and_(Site.client_id == client_id, Gate.org_id == org_id)
        ).count()
        
        return stats


class SiteService(BaseHierarchyService):
    """Site CRUD service."""
    
    def create_site(self, org_id: int, site_data: SiteCreate) -> Site:
        """Create a new site."""
        # Verify client exists and belongs to organization
        client = self.db.query(Client).filter(
            and_(
                Client.id == site_data.client_id,
                Client.organization_id == org_id
            )
        ).first()
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        try:
            site_dict = site_data.model_dump()
            site = Site(
                org_id=org_id,
                **site_dict
            )
            self.db.add(site)
            self.db.commit()
            self.db.refresh(site)
            return site
        except IntegrityError as e:
            self.db.rollback()
            if "name" in str(e):
                raise HTTPException(
                    status_code=400,
                    detail="Site name already exists for this client"
                )
            raise HTTPException(status_code=400, detail="Site creation failed")
    
    def get_site(self, org_id: int, site_id: int) -> Optional[Site]:
        """Get site by ID."""
        return self.db.query(Site).filter(
            and_(Site.id == site_id, Site.org_id == org_id)
        ).first()
    
    def get_sites(
        self,
        org_id: int,
        search: SiteSearchParams,
        pagination: PaginationParams
    ) -> Tuple[List[Site], int]:
        """Get sites with search and pagination."""
        query = self.db.query(Site).filter(Site.org_id == org_id)
        
        # Apply search filters
        if search.query:
            search_filter = or_(
                Site.name.ilike(f"%{search.query}%"),
                Site.display_name.ilike(f"%{search.query}%"),
                Site.site_code.ilike(f"%{search.query}%"),
                Site.city.ilike(f"%{search.query}%"),
                Site.address_line_1.ilike(f"%{search.query}%")
            )
            query = query.filter(search_filter)
        
        if search.client_id is not None:
            query = query.filter(Site.client_id == search.client_id)
        
        if search.city is not None:
            query = query.filter(Site.city.ilike(f"%{search.city}%"))
        
        if search.is_active is not None:
            query = query.filter(Site.is_active == search.is_active)
        
        # Get total count
        total = self._get_total_count(query)
        
        # Apply pagination and ordering
        query = query.order_by(asc(Site.name))
        items = self._apply_pagination(query, pagination).all()
        
        return items, total
    
    def update_site(
        self,
        org_id: int,
        site_id: int,
        site_data: SiteUpdate
    ) -> Optional[Site]:
        """Update site."""
        site = self.get_site(org_id, site_id)
        if not site:
            return None
        
        try:
            update_data = site_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(site, field, value)
            
            self.db.commit()
            self.db.refresh(site)
            return site
        except IntegrityError as e:
            self.db.rollback()
            if "name" in str(e):
                raise HTTPException(
                    status_code=400,
                    detail="Site name already exists for this client"
                )
            raise HTTPException(status_code=400, detail="Site update failed")
    
    def delete_site(self, org_id: int, site_id: int) -> bool:
        """Delete site (soft delete)."""
        site = self.get_site(org_id, site_id)
        if not site:
            return False
        
        # Check if site has active buildings
        active_buildings = self.db.query(Building).filter(
            and_(Building.site_id == site_id, Building.is_active == True)
        ).count()
        
        if active_buildings > 0:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete site with active buildings"
            )
        
        site.is_active = False
        self.db.commit()
        return True
    
    def get_site_stats(self, org_id: int, site_id: int) -> Dict[str, int]:
        """Get site statistics."""
        stats = {}
        
        # Count buildings
        stats['buildings_count'] = self.db.query(Building).filter(
            and_(Building.site_id == site_id, Building.org_id == org_id)
        ).count()
        
        # Count gates
        stats['gates_count'] = self.db.query(Gate).join(Building).filter(
            and_(Building.site_id == site_id, Gate.org_id == org_id)
        ).count()
        
        return stats


class BuildingService(BaseHierarchyService):
    """Building CRUD service."""
    
    def create_building(self, org_id: int, building_data: BuildingCreate) -> Building:
        """Create a new building."""
        # Verify site exists and belongs to organization
        site = self.db.query(Site).filter(
            and_(
                Site.id == building_data.site_id,
                Site.org_id == org_id
            )
        ).first()
        
        if not site:
            raise HTTPException(status_code=404, detail="Site not found")
        
        try:
            building_dict = building_data.model_dump()
            building = Building(
                org_id=org_id,
                **building_dict
            )
            self.db.add(building)
            self.db.commit()
            self.db.refresh(building)
            return building
        except IntegrityError as e:
            self.db.rollback()
            if "name" in str(e):
                raise HTTPException(
                    status_code=400,
                    detail="Building name already exists for this site"
                )
            raise HTTPException(status_code=400, detail="Building creation failed")
    
    def get_building(self, org_id: int, building_id: int) -> Optional[Building]:
        """Get building by ID."""
        return self.db.query(Building).filter(
            and_(Building.id == building_id, Building.org_id == org_id)
        ).first()
    
    def get_buildings(
        self,
        org_id: int,
        search: BuildingSearchParams,
        pagination: PaginationParams
    ) -> Tuple[List[Building], int]:
        """Get buildings with search and pagination."""
        query = self.db.query(Building).filter(Building.org_id == org_id)
        
        # Apply search filters
        if search.query:
            search_filter = or_(
                Building.name.ilike(f"%{search.query}%"),
                Building.display_name.ilike(f"%{search.query}%"),
                Building.building_code.ilike(f"%{search.query}%"),
                Building.address_suffix.ilike(f"%{search.query}%")
            )
            query = query.filter(search_filter)
        
        if search.site_id is not None:
            query = query.filter(Building.site_id == search.site_id)
        
        if search.building_type is not None:
            query = query.filter(Building.building_type == search.building_type)
        
        if search.is_active is not None:
            query = query.filter(Building.is_active == search.is_active)
        
        # Get total count
        total = self._get_total_count(query)
        
        # Apply pagination and ordering
        query = query.order_by(asc(Building.name))
        items = self._apply_pagination(query, pagination).all()
        
        return items, total
    
    def update_building(
        self,
        org_id: int,
        building_id: int,
        building_data: BuildingUpdate
    ) -> Optional[Building]:
        """Update building."""
        building = self.get_building(org_id, building_id)
        if not building:
            return None
        
        try:
            update_data = building_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(building, field, value)
            
            self.db.commit()
            self.db.refresh(building)
            return building
        except IntegrityError as e:
            self.db.rollback()
            if "name" in str(e):
                raise HTTPException(
                    status_code=400,
                    detail="Building name already exists for this site"
                )
            raise HTTPException(status_code=400, detail="Building update failed")
    
    def delete_building(self, org_id: int, building_id: int) -> bool:
        """Delete building (soft delete)."""
        building = self.get_building(org_id, building_id)
        if not building:
            return False
        
        # Check if building has active gates
        active_gates = self.db.query(Gate).filter(
            and_(Gate.building_id == building_id, Gate.is_active == True)
        ).count()
        
        if active_gates > 0:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete building with active gates"
            )
        
        building.is_active = False
        self.db.commit()
        return True
    
    def get_building_stats(self, org_id: int, building_id: int) -> Dict[str, int]:
        """Get building statistics."""
        stats = {}
        
        # Count gates
        stats['gates_count'] = self.db.query(Gate).filter(
            and_(Gate.building_id == building_id, Gate.org_id == org_id)
        ).count()
        
        return stats


class GateService(BaseHierarchyService):
    """Gate CRUD service."""
    
    def create_gate(self, org_id: int, gate_data: GateCreate) -> Gate:
        """Create a new gate."""
        # Verify building exists and belongs to organization
        building = self.db.query(Building).filter(
            and_(
                Building.id == gate_data.building_id,
                Building.org_id == org_id
            )
        ).first()
        
        if not building:
            raise HTTPException(status_code=404, detail="Building not found")
        
        try:
            gate_dict = gate_data.model_dump()
            gate = Gate(
                org_id=org_id,
                **gate_dict
            )
            self.db.add(gate)
            self.db.commit()
            self.db.refresh(gate)
            return gate
        except IntegrityError as e:
            self.db.rollback()
            if "name" in str(e):
                raise HTTPException(
                    status_code=400,
                    detail="Gate name already exists for this building"
                )
            raise HTTPException(status_code=400, detail="Gate creation failed")
    
    def get_gate(self, org_id: int, gate_id: int) -> Optional[Gate]:
        """Get gate by ID."""
        return self.db.query(Gate).filter(
            and_(Gate.id == gate_id, Gate.org_id == org_id)
        ).first()
    
    def get_gates(
        self,
        org_id: int,
        search: GateSearchParams,
        pagination: PaginationParams
    ) -> Tuple[List[Gate], int]:
        """Get gates with search and pagination."""
        query = self.db.query(Gate).filter(Gate.org_id == org_id)
        
        # Apply search filters
        if search.query:
            search_filter = or_(
                Gate.name.ilike(f"%{search.query}%"),
                Gate.display_name.ilike(f"%{search.query}%"),
                Gate.gate_code.ilike(f"%{search.query}%"),
                Gate.manufacturer.ilike(f"%{search.query}%"),
                Gate.model.ilike(f"%{search.query}%"),
                Gate.serial_number.ilike(f"%{search.query}%")
            )
            query = query.filter(search_filter)
        
        if search.building_id is not None:
            query = query.filter(Gate.building_id == search.building_id)
        
        if search.gate_type is not None:
            query = query.filter(Gate.gate_type == search.gate_type)
        
        if search.status is not None:
            query = query.filter(Gate.status == search.status)
        
        if search.manufacturer is not None:
            query = query.filter(Gate.manufacturer.ilike(f"%{search.manufacturer}%"))
        
        if search.is_active is not None:
            query = query.filter(Gate.is_active == search.is_active)
        
        # Get total count
        total = self._get_total_count(query)
        
        # Apply pagination and ordering
        query = query.order_by(asc(Gate.name))
        items = self._apply_pagination(query, pagination).all()
        
        return items, total
    
    def update_gate(
        self,
        org_id: int,
        gate_id: int,
        gate_data: GateUpdate
    ) -> Optional[Gate]:
        """Update gate."""
        gate = self.get_gate(org_id, gate_id)
        if not gate:
            return None
        
        try:
            update_data = gate_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(gate, field, value)
            
            self.db.commit()
            self.db.refresh(gate)
            return gate
        except IntegrityError as e:
            self.db.rollback()
            if "name" in str(e):
                raise HTTPException(
                    status_code=400,
                    detail="Gate name already exists for this building"
                )
            raise HTTPException(status_code=400, detail="Gate update failed")
    
    def delete_gate(self, org_id: int, gate_id: int) -> bool:
        """Delete gate (soft delete)."""
        gate = self.get_gate(org_id, gate_id)
        if not gate:
            return False
        
        gate.is_active = False
        self.db.commit()
        return True