"""
ERP adapter interfaces and implementations for parts synchronization
ERP adapter interfészek és implementációk alkatrész szinkronizáláshoz
"""
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
import logging
from sqlalchemy.orm import Session
from dataclasses import dataclass

from ..models.integrations import ERPSyncLog, Integration
from ..models.inventory import InventoryItem, PartModel
from ..core.database import get_db

logger = logging.getLogger(__name__)


@dataclass
class ERPPartData:
    """
    Standardized part data structure for ERP systems
    Szabványosított alkatrész adat struktúra ERP rendszerekhez
    """
    part_number: str
    name: str
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    category: Optional[str] = None
    unit_price: Optional[float] = None
    currency: str = "HUF"
    stock_quantity: Optional[int] = None
    minimum_stock: Optional[int] = None
    lead_time_days: Optional[int] = None
    supplier_part_number: Optional[str] = None
    barcode: Optional[str] = None
    weight_kg: Optional[float] = None
    dimensions: Optional[Dict[str, float]] = None  # {"length": 10.5, "width": 5.0, "height": 2.0}
    custom_fields: Optional[Dict[str, Any]] = None
    
    # Metadata
    erp_id: Optional[str] = None  # External system ID
    last_updated: Optional[datetime] = None
    is_active: bool = True


@dataclass
class ERPSyncResult:
    """
    Result of ERP synchronization operation
    ERP szinkronizációs művelet eredménye
    """
    success: bool
    records_processed: int = 0
    records_successful: int = 0
    records_failed: int = 0
    errors: List[str] = None
    warnings: List[str] = None
    data: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class BaseERPAdapter(ABC):
    """
    Base abstract class for ERP system adapters
    Alap absztrakt osztály ERP rendszer adapterekhez
    """
    
    def __init__(self, integration: Integration, db: Session):
        self.integration = integration
        self.db = db
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to ERP system
        Kapcsolat tesztelése ERP rendszerhez
        """
        pass
    
    @abstractmethod
    async def sync_parts_from_erp(self, 
                                  part_numbers: Optional[List[str]] = None,
                                  modified_since: Optional[datetime] = None) -> ERPSyncResult:
        """
        Synchronize parts from ERP system to GarageReg
        Alkatrészek szinkronizálása ERP rendszerből GarageReg-be
        """
        pass
    
    @abstractmethod
    async def sync_parts_to_erp(self, 
                                part_numbers: Optional[List[str]] = None,
                                force_update: bool = False) -> ERPSyncResult:
        """
        Synchronize parts from GarageReg to ERP system
        Alkatrészek szinkronizálása GarageReg-ből ERP rendszerbe
        """
        pass
    
    @abstractmethod
    async def get_part_by_number(self, part_number: str) -> Optional[ERPPartData]:
        """
        Get single part data from ERP system
        Egy alkatrész adat lekérése ERP rendszerből
        """
        pass
    
    @abstractmethod
    async def create_part_in_erp(self, part_data: ERPPartData) -> Tuple[bool, str]:
        """
        Create new part in ERP system
        Új alkatrész létrehozása ERP rendszerben
        """
        pass
    
    @abstractmethod
    async def update_part_in_erp(self, part_data: ERPPartData) -> Tuple[bool, str]:
        """
        Update existing part in ERP system
        Meglévő alkatrész frissítése ERP rendszerben
        """
        pass
    
    def _log_sync_operation(self, 
                           sync_type: str,
                           operation: str,
                           result: ERPSyncResult,
                           entity_id: Optional[str] = None,
                           request_data: Optional[Dict] = None,
                           duration_seconds: Optional[int] = None) -> ERPSyncLog:
        """
        Log synchronization operation
        Szinkronizációs művelet naplózása
        """
        sync_log = ERPSyncLog(
            integration_id=self.integration.id,
            organization_id=self.integration.organization_id,
            sync_type=sync_type,
            operation=operation,
            entity_type="part",
            entity_id=entity_id,
            request_data=request_data,
            response_data=result.data,
            status="success" if result.success else "failed",
            error_message="; ".join(result.errors) if result.errors else None,
            records_processed=result.records_processed,
            records_successful=result.records_successful,
            records_failed=result.records_failed,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            duration_seconds=duration_seconds
        )
        
        self.db.add(sync_log)
        return sync_log
    
    def _convert_to_inventory_item(self, erp_part: ERPPartData) -> Dict[str, Any]:
        """
        Convert ERP part data to GarageReg inventory item format
        ERP alkatrész adat konvertálása GarageReg készletelem formátumba
        """
        return {
            "part_number": erp_part.part_number,
            "name": erp_part.name,
            "description": erp_part.description,
            "manufacturer": erp_part.manufacturer,
            "category": erp_part.category,
            "unit_price": erp_part.unit_price,
            "minimum_stock": erp_part.minimum_stock or 0,
            "lead_time_days": erp_part.lead_time_days,
            "supplier_part_number": erp_part.supplier_part_number,
            "barcode": erp_part.barcode,
            "weight_kg": erp_part.weight_kg,
            "dimensions": erp_part.dimensions,
            "is_active": erp_part.is_active,
            "metadata": {
                "erp_id": erp_part.erp_id,
                "last_erp_sync": erp_part.last_updated.isoformat() if erp_part.last_updated else None,
                "custom_fields": erp_part.custom_fields or {}
            }
        }
    
    def _convert_from_inventory_item(self, item: InventoryItem) -> ERPPartData:
        """
        Convert GarageReg inventory item to ERP part data format
        GarageReg készletelem konvertálása ERP alkatrész adat formátumba
        """
        metadata = item.metadata or {}
        
        return ERPPartData(
            part_number=item.part_number,
            name=item.name,
            description=item.description,
            manufacturer=item.manufacturer,
            category=item.category,
            unit_price=item.unit_price,
            stock_quantity=item.current_stock,
            minimum_stock=item.minimum_stock,
            lead_time_days=item.lead_time_days,
            supplier_part_number=item.supplier_part_number,
            barcode=item.barcode,
            weight_kg=item.weight_kg,
            dimensions=item.dimensions,
            erp_id=metadata.get("erp_id"),
            last_updated=item.updated_at,
            is_active=item.is_active,
            custom_fields=metadata.get("custom_fields", {})
        )


class DummyERPAdapter(BaseERPAdapter):
    """
    Dummy ERP adapter implementation for testing and demonstration
    Teszt ERP adapter implementáció teszteléshez és bemutatáshoz
    """
    
    def __init__(self, integration: Integration, db: Session):
        super().__init__(integration, db)
        self.dummy_parts_db = self._initialize_dummy_data()
    
    def _initialize_dummy_data(self) -> Dict[str, ERPPartData]:
        """Initialize dummy ERP data"""
        return {
            "GATE-MOTOR-001": ERPPartData(
                part_number="GATE-MOTOR-001",
                name="Gate Motor 24V 100W",
                description="Heavy duty gate motor for automatic gates",
                manufacturer="GateTech Inc.",
                category="Motors",
                unit_price=45000.0,
                currency="HUF",
                stock_quantity=15,
                minimum_stock=5,
                lead_time_days=7,
                supplier_part_number="GT-MOT-24V-100",
                barcode="8901234567890",
                weight_kg=5.2,
                dimensions={"length": 25.0, "width": 15.0, "height": 12.0},
                erp_id="ERP-GATE-MOTOR-001",
                last_updated=datetime.now(timezone.utc),
                is_active=True
            ),
            "GATE-REMOTE-001": ERPPartData(
                part_number="GATE-REMOTE-001",
                name="Remote Control 433MHz",
                description="4-button remote control for gate systems",
                manufacturer="RemoteTech Ltd.",
                category="Controllers",
                unit_price=8500.0,
                currency="HUF",
                stock_quantity=50,
                minimum_stock=10,
                lead_time_days=3,
                supplier_part_number="RT-REM-433-4B",
                barcode="8901234567891",
                weight_kg=0.1,
                dimensions={"length": 8.0, "width": 4.0, "height": 1.5},
                erp_id="ERP-GATE-REMOTE-001",
                last_updated=datetime.now(timezone.utc),
                is_active=True
            ),
            "GATE-SENSOR-001": ERPPartData(
                part_number="GATE-SENSOR-001",
                name="Safety Sensor Pair IR",
                description="Infrared safety sensor pair for gate protection",
                manufacturer="SafeGate Systems",
                category="Sensors",
                unit_price=12000.0,
                currency="HUF",
                stock_quantity=25,
                minimum_stock=8,
                lead_time_days=5,
                supplier_part_number="SG-SENS-IR-PAIR",
                barcode="8901234567892",
                weight_kg=0.8,
                dimensions={"length": 10.0, "width": 6.0, "height": 4.0},
                erp_id="ERP-GATE-SENSOR-001",
                last_updated=datetime.now(timezone.utc),
                is_active=True
            )
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test dummy ERP connection"""
        self.logger.info("Testing dummy ERP connection")
        
        return {
            "success": True,
            "status": "connected",
            "erp_system": "Dummy ERP System v1.0",
            "server": "dummy-erp.garagereg.local",
            "response_time_ms": 50,
            "available_endpoints": [
                "/api/parts",
                "/api/parts/{part_number}",
                "/api/inventory",
                "/api/sync"
            ],
            "last_sync": datetime.now(timezone.utc).isoformat()
        }
    
    async def sync_parts_from_erp(self,
                                  part_numbers: Optional[List[str]] = None,
                                  modified_since: Optional[datetime] = None) -> ERPSyncResult:
        """Sync parts from dummy ERP to GarageReg"""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Filter parts based on criteria
            parts_to_sync = {}
            
            if part_numbers:
                for pn in part_numbers:
                    if pn in self.dummy_parts_db:
                        parts_to_sync[pn] = self.dummy_parts_db[pn]
            else:
                parts_to_sync = self.dummy_parts_db.copy()
            
            if modified_since:
                parts_to_sync = {
                    pn: part for pn, part in parts_to_sync.items()
                    if part.last_updated and part.last_updated >= modified_since
                }
            
            successful = 0
            failed = 0
            errors = []
            
            for part_number, erp_part in parts_to_sync.items():
                try:
                    # Check if inventory item exists
                    existing_item = self.db.query(InventoryItem).filter(
                        InventoryItem.part_number == part_number,
                        InventoryItem.organization_id == self.integration.organization_id
                    ).first()
                    
                    item_data = self._convert_to_inventory_item(erp_part)
                    
                    if existing_item:
                        # Update existing item
                        for key, value in item_data.items():
                            if hasattr(existing_item, key):
                                setattr(existing_item, key, value)
                        existing_item.updated_at = datetime.now(timezone.utc)
                    else:
                        # Create new item
                        new_item = InventoryItem(
                            organization_id=self.integration.organization_id,
                            **item_data
                        )
                        self.db.add(new_item)
                    
                    successful += 1
                    
                except Exception as e:
                    failed += 1
                    errors.append(f"Failed to sync part {part_number}: {str(e)}")
                    self.logger.error(f"Error syncing part {part_number}: {e}")
            
            self.db.commit()
            
            duration = (datetime.now(timezone.utc) - start_time).seconds
            
            result = ERPSyncResult(
                success=failed == 0,
                records_processed=len(parts_to_sync),
                records_successful=successful,
                records_failed=failed,
                errors=errors,
                data={
                    "sync_type": "from_erp",
                    "parts_processed": list(parts_to_sync.keys()),
                    "duration_seconds": duration
                }
            )
            
            # Log the operation
            self._log_sync_operation(
                sync_type="parts_from_erp",
                operation="sync",
                result=result,
                duration_seconds=duration
            )
            
            self.logger.info(f"Synced {successful} parts from dummy ERP, {failed} failed")
            return result
            
        except Exception as e:
            self.logger.error(f"ERP sync failed: {e}")
            return ERPSyncResult(
                success=False,
                errors=[str(e)]
            )
    
    async def sync_parts_to_erp(self,
                                part_numbers: Optional[List[str]] = None,
                                force_update: bool = False) -> ERPSyncResult:
        """Sync parts from GarageReg to dummy ERP"""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Get inventory items to sync
            query = self.db.query(InventoryItem).filter(
                InventoryItem.organization_id == self.integration.organization_id,
                InventoryItem.is_active == True
            )
            
            if part_numbers:
                query = query.filter(InventoryItem.part_number.in_(part_numbers))
            
            items_to_sync = query.all()
            
            successful = 0
            failed = 0
            errors = []
            
            for item in items_to_sync:
                try:
                    erp_part = self._convert_from_inventory_item(item)
                    
                    # Simulate ERP update
                    if erp_part.part_number in self.dummy_parts_db:
                        # Update existing part in dummy ERP
                        self.dummy_parts_db[erp_part.part_number] = erp_part
                        operation = "updated"
                    else:
                        # Create new part in dummy ERP
                        erp_part.erp_id = f"ERP-{erp_part.part_number}"
                        self.dummy_parts_db[erp_part.part_number] = erp_part
                        operation = "created"
                    
                    # Update metadata in GarageReg
                    if not item.metadata:
                        item.metadata = {}
                    item.metadata["erp_id"] = erp_part.erp_id
                    item.metadata["last_erp_sync"] = datetime.now(timezone.utc).isoformat()
                    item.updated_at = datetime.now(timezone.utc)
                    
                    successful += 1
                    self.logger.info(f"Part {erp_part.part_number} {operation} in dummy ERP")
                    
                except Exception as e:
                    failed += 1
                    errors.append(f"Failed to sync part {item.part_number}: {str(e)}")
                    self.logger.error(f"Error syncing part {item.part_number}: {e}")
            
            self.db.commit()
            
            duration = (datetime.now(timezone.utc) - start_time).seconds
            
            result = ERPSyncResult(
                success=failed == 0,
                records_processed=len(items_to_sync),
                records_successful=successful,
                records_failed=failed,
                errors=errors,
                data={
                    "sync_type": "to_erp",
                    "parts_processed": [item.part_number for item in items_to_sync],
                    "duration_seconds": duration
                }
            )
            
            # Log the operation
            self._log_sync_operation(
                sync_type="parts_to_erp",
                operation="sync",
                result=result,
                duration_seconds=duration
            )
            
            self.logger.info(f"Synced {successful} parts to dummy ERP, {failed} failed")
            return result
            
        except Exception as e:
            self.logger.error(f"ERP sync failed: {e}")
            return ERPSyncResult(
                success=False,
                errors=[str(e)]
            )
    
    async def get_part_by_number(self, part_number: str) -> Optional[ERPPartData]:
        """Get single part from dummy ERP"""
        self.logger.info(f"Getting part {part_number} from dummy ERP")
        
        return self.dummy_parts_db.get(part_number)
    
    async def create_part_in_erp(self, part_data: ERPPartData) -> Tuple[bool, str]:
        """Create part in dummy ERP"""
        try:
            if part_data.part_number in self.dummy_parts_db:
                return False, f"Part {part_data.part_number} already exists in ERP"
            
            # Generate ERP ID
            part_data.erp_id = f"ERP-{part_data.part_number}"
            part_data.last_updated = datetime.now(timezone.utc)
            
            # Store in dummy database
            self.dummy_parts_db[part_data.part_number] = part_data
            
            self.logger.info(f"Created part {part_data.part_number} in dummy ERP")
            return True, f"Part created with ERP ID: {part_data.erp_id}"
            
        except Exception as e:
            self.logger.error(f"Failed to create part {part_data.part_number}: {e}")
            return False, str(e)
    
    async def update_part_in_erp(self, part_data: ERPPartData) -> Tuple[bool, str]:
        """Update part in dummy ERP"""
        try:
            if part_data.part_number not in self.dummy_parts_db:
                return False, f"Part {part_data.part_number} not found in ERP"
            
            # Update existing part
            part_data.last_updated = datetime.now(timezone.utc)
            self.dummy_parts_db[part_data.part_number] = part_data
            
            self.logger.info(f"Updated part {part_data.part_number} in dummy ERP")
            return True, "Part updated successfully"
            
        except Exception as e:
            self.logger.error(f"Failed to update part {part_data.part_number}: {e}")
            return False, str(e)


class ERPAdapterFactory:
    """
    Factory class for creating ERP adapter instances
    Factory osztály ERP adapter példányok létrehozásához
    """
    
    @staticmethod
    def create_adapter(integration: Integration, db: Session) -> BaseERPAdapter:
        """
        Create appropriate ERP adapter based on integration provider
        Megfelelő ERP adapter létrehozása integráció szolgáltató alapján
        """
        provider = integration.provider.lower()
        
        if provider == "dummy" or provider == "test":
            return DummyERPAdapter(integration, db)
        elif provider == "sap":
            # TODO: Implement SAP adapter
            raise NotImplementedError("SAP adapter not implemented yet")
        elif provider == "oracle":
            # TODO: Implement Oracle adapter
            raise NotImplementedError("Oracle adapter not implemented yet")
        elif provider == "microsoft":
            # TODO: Implement Microsoft Dynamics adapter
            raise NotImplementedError("Microsoft Dynamics adapter not implemented yet")
        else:
            raise ValueError(f"Unsupported ERP provider: {provider}")


class ERPSyncScheduler:
    """
    Scheduler for automatic ERP synchronization
    Ütemező automatikus ERP szinkronizáláshoz
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(f"{__name__}.ERPSyncScheduler")
    
    async def run_scheduled_sync(self, integration_id: int) -> ERPSyncResult:
        """
        Run scheduled synchronization for integration
        Ütemezett szinkronizálás futtatása integrációhoz
        """
        integration = self.db.query(Integration).filter(Integration.id == integration_id).first()
        
        if not integration:
            return ERPSyncResult(success=False, errors=[f"Integration {integration_id} not found"])
        
        if not integration.is_active:
            return ERPSyncResult(success=False, errors=[f"Integration {integration_id} is not active"])
        
        try:
            adapter = ERPAdapterFactory.create_adapter(integration, self.db)
            
            # Test connection first
            connection_test = await adapter.test_connection()
            if not connection_test.get("success", False):
                return ERPSyncResult(
                    success=False,
                    errors=["ERP connection test failed"]
                )
            
            # Run bidirectional sync
            from_erp_result = await adapter.sync_parts_from_erp()
            to_erp_result = await adapter.sync_parts_to_erp()
            
            # Combine results
            total_processed = from_erp_result.records_processed + to_erp_result.records_processed
            total_successful = from_erp_result.records_successful + to_erp_result.records_successful
            total_failed = from_erp_result.records_failed + to_erp_result.records_failed
            
            all_errors = from_erp_result.errors + to_erp_result.errors
            
            return ERPSyncResult(
                success=total_failed == 0,
                records_processed=total_processed,
                records_successful=total_successful,
                records_failed=total_failed,
                errors=all_errors,
                data={
                    "from_erp": from_erp_result.data,
                    "to_erp": to_erp_result.data
                }
            )
            
        except Exception as e:
            self.logger.error(f"Scheduled sync failed for integration {integration_id}: {e}")
            return ERPSyncResult(
                success=False,
                errors=[str(e)]
            )