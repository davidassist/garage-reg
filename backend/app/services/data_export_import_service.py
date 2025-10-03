"""
Comprehensive Data Export/Import Service
Teljes adatkör export/import szolgáltatás JSONL/CSV támogatással
"""
import json
import csv
import io
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from pathlib import Path
import tempfile
import zipfile
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio

from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError
import structlog

from app.models import Base, BaseModel, TenantModel
from app.models import *  # Import all models
from app.database import get_db


logger = structlog.get_logger(__name__)


class ExportFormat(str, Enum):
    """Export format options."""
    JSONL = "jsonl"
    CSV = "csv"
    JSON = "json"


class ImportStrategy(str, Enum):
    """Import strategy for handling conflicts."""
    SKIP = "skip"           # Skip conflicting records
    OVERWRITE = "overwrite" # Overwrite existing records
    MERGE = "merge"         # Merge with existing records
    ERROR = "error"         # Raise error on conflicts


class ConflictType(str, Enum):
    """Types of import conflicts."""
    DUPLICATE_ID = "duplicate_id"
    DUPLICATE_UNIQUE = "duplicate_unique"
    FOREIGN_KEY = "foreign_key_missing"
    VALIDATION = "validation_error"
    DATA_TYPE = "data_type_error"


@dataclass
class ExportMetadata:
    """Metadata for exported data."""
    export_id: str
    timestamp: datetime
    format: ExportFormat
    total_records: int
    total_tables: int
    organization_id: Optional[int]
    exported_by: str
    version: str = "1.0"
    checksum: str = ""


@dataclass
class ImportConflict:
    """Represents a data import conflict."""
    table: str
    record_id: Any
    conflict_type: ConflictType
    message: str
    current_data: Dict[str, Any]
    incoming_data: Dict[str, Any]
    resolution: Optional[str] = None


@dataclass
class ImportResult:
    """Result of an import operation."""
    success: bool
    total_records: int
    imported_records: int
    skipped_records: int
    error_records: int
    conflicts: List[ImportConflict]
    processing_time: float
    message: str


class DataExportImportService:
    """Comprehensive data export/import service."""
    
    # Define export order to handle foreign key dependencies
    EXPORT_ORDER = [
        'organizations',
        'users', 'roles', 'permissions', 'role_permissions', 'role_assignments',
        'clients', 'sites', 'buildings', 'gates', 'gate_components',
        'warehouses', 'inventory_items', 'parts',
        'checklist_templates', 'checklist_items',
        'maintenance_plans', 'reminders',
        'inspections', 'inspection_items', 'measurements',
        'tickets', 'work_orders', 'work_order_items', 'part_usages',
        'maintenance_jobs',
        'documents', 'media_objects',
        'integrations', 'webhooks',
        'stock_movements', 'stock_alerts', 'stock_takes', 'stock_take_lines',
        'events', 'audit_logs',
        'api_keys', 'totp_secrets', 'webauthn_credentials'
    ]
    
    # Define which tables should be excluded from export/import
    EXCLUDED_TABLES = {
        'alembic_version',           # Migration metadata
        'webauthn_credentials',      # Security sensitive
        'totp_secrets',             # Security sensitive
        'api_keys'                  # Security sensitive (can be optionally included)
    }
    
    def __init__(self, db: Session):
        """Initialize the service."""
        self.db = db
        self.model_registry = self._build_model_registry()
    
    def _build_model_registry(self) -> Dict[str, Any]:
        """Build registry of all SQLAlchemy models."""
        registry = {}
        
        for model_class in Base.registry._class_registry.values():
            if hasattr(model_class, '__tablename__'):
                table_name = model_class.__tablename__
                if table_name not in self.EXCLUDED_TABLES:
                    registry[table_name] = model_class
        
        return registry
    
    def _calculate_checksum(self, data: str) -> str:
        """Calculate MD5 checksum for data integrity."""
        return hashlib.md5(data.encode('utf-8')).hexdigest()
    
    def _serialize_value(self, value: Any) -> Any:
        """Serialize complex values for export."""
        if isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, (dict, list)):
            return json.dumps(value) if isinstance(value, dict) else value
        elif value is None:
            return None
        else:
            return str(value)
    
    def _deserialize_value(self, value: Any, column_type: str) -> Any:
        """Deserialize values during import."""
        if value is None or value == "":
            return None
        
        # Handle datetime fields
        if 'datetime' in column_type.lower() or 'timestamp' in column_type.lower():
            if isinstance(value, str):
                try:
                    return datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    return None
        
        # Handle JSON fields
        if 'json' in column_type.lower():
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
        
        # Handle boolean fields
        if 'boolean' in column_type.lower():
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            return bool(value)
        
        # Handle integer fields
        if 'integer' in column_type.lower():
            try:
                return int(value)
            except (ValueError, TypeError):
                return None
        
        return value
    
    async def export_data(
        self,
        format: ExportFormat = ExportFormat.JSONL,
        organization_id: Optional[int] = None,
        tables: Optional[List[str]] = None,
        exported_by: str = "system"
    ) -> Tuple[str, ExportMetadata]:
        """
        Export all data from database.
        
        Args:
            format: Export format (JSONL, CSV, JSON)
            organization_id: Optional organization filter for tenant isolation
            tables: Optional list of specific tables to export
            exported_by: User identifier who performed the export
            
        Returns:
            Tuple of (export_data, metadata)
        """
        start_time = datetime.now()
        export_id = f"export_{start_time.strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(str(start_time).encode()).hexdigest()[:8]}"
        
        logger.info("Starting data export", 
                   export_id=export_id, 
                   format=format.value,
                   organization_id=organization_id)
        
        export_data = {}
        total_records = 0
        tables_to_export = tables or [t for t in self.EXPORT_ORDER if t in self.model_registry]
        
        # Export each table
        for table_name in tables_to_export:
            if table_name not in self.model_registry:
                logger.warning(f"Table {table_name} not found in model registry")
                continue
                
            model_class = self.model_registry[table_name]
            
            try:
                # Build query with optional organization filter
                query = self.db.query(model_class)
                
                # Apply tenant filtering if model supports it and organization_id is specified
                if organization_id and issubclass(model_class, TenantModel):
                    query = query.filter(model_class.org_id == organization_id)
                
                # Execute query
                records = query.all()
                
                # Serialize records
                table_data = []
                for record in records:
                    record_dict = {}
                    for column in inspect(model_class).columns:
                        value = getattr(record, column.name)
                        record_dict[column.name] = self._serialize_value(value)
                    
                    table_data.append(record_dict)
                
                export_data[table_name] = table_data
                total_records += len(table_data)
                
                logger.info(f"Exported {len(table_data)} records from {table_name}")
                
            except Exception as e:
                logger.error(f"Error exporting table {table_name}", error=str(e))
                raise
        
        # Create metadata
        metadata = ExportMetadata(
            export_id=export_id,
            timestamp=start_time,
            format=format,
            total_records=total_records,
            total_tables=len(export_data),
            organization_id=organization_id,
            exported_by=exported_by
        )
        
        # Format output based on requested format
        if format == ExportFormat.JSONL:
            output_lines = []
            # Add metadata as first line
            output_lines.append(json.dumps({"_metadata": asdict(metadata)}))
            
            # Add each table's data
            for table_name, records in export_data.items():
                for record in records:
                    line_data = {"_table": table_name, **record}
                    output_lines.append(json.dumps(line_data, ensure_ascii=False))
            
            output = "\n".join(output_lines)
            
        elif format == ExportFormat.JSON:
            full_export = {
                "_metadata": asdict(metadata),
                "data": export_data
            }
            output = json.dumps(full_export, indent=2, ensure_ascii=False)
            
        elif format == ExportFormat.CSV:
            # For CSV, create a ZIP file with one CSV per table
            output = await self._create_csv_export(export_data, metadata)
        
        # Calculate checksum
        metadata.checksum = self._calculate_checksum(output)
        
        logger.info("Data export completed",
                   export_id=export_id,
                   total_records=total_records,
                   tables=len(export_data),
                   processing_time=(datetime.now() - start_time).total_seconds())
        
        return output, metadata
    
    async def _create_csv_export(self, export_data: Dict[str, List[Dict]], metadata: ExportMetadata) -> str:
        """Create CSV export as ZIP file."""
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add metadata file
            metadata_content = json.dumps(asdict(metadata), indent=2)
            zip_file.writestr("_metadata.json", metadata_content)
            
            # Add CSV file for each table
            for table_name, records in export_data.items():
                if not records:
                    continue
                
                csv_buffer = io.StringIO()
                if records:
                    fieldnames = records[0].keys()
                    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(records)
                
                csv_content = csv_buffer.getvalue()
                zip_file.writestr(f"{table_name}.csv", csv_content)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
    
    async def import_data(
        self,
        import_data: Union[str, bytes],
        format: ExportFormat = ExportFormat.JSONL,
        strategy: ImportStrategy = ImportStrategy.SKIP,
        organization_id: Optional[int] = None,
        dry_run: bool = False
    ) -> ImportResult:
        """
        Import data into database with conflict resolution.
        
        Args:
            import_data: Data to import (string or bytes)
            format: Format of import data
            strategy: Strategy for handling conflicts
            organization_id: Organization ID for tenant isolation
            dry_run: If True, validate but don't actually import
            
        Returns:
            ImportResult with detailed information about the import
        """
        start_time = datetime.now()
        
        logger.info("Starting data import",
                   format=format.value,
                   strategy=strategy.value,
                   dry_run=dry_run,
                   organization_id=organization_id)
        
        conflicts = []
        total_records = 0
        imported_records = 0
        skipped_records = 0
        error_records = 0
        
        try:
            # Parse import data based on format
            if format == ExportFormat.JSONL:
                parsed_data = await self._parse_jsonl_import(import_data)
            elif format == ExportFormat.JSON:
                parsed_data = await self._parse_json_import(import_data)
            elif format == ExportFormat.CSV:
                parsed_data = await self._parse_csv_import(import_data)
            else:
                raise ValueError(f"Unsupported import format: {format}")
            
            metadata = parsed_data.get("_metadata", {})
            tables_data = parsed_data.get("data", {})
            
            # Import each table in dependency order
            for table_name in self.EXPORT_ORDER:
                if table_name not in tables_data:
                    continue
                
                if table_name not in self.model_registry:
                    logger.warning(f"Skipping unknown table: {table_name}")
                    continue
                
                model_class = self.model_registry[table_name]
                records = tables_data[table_name]
                
                logger.info(f"Importing {len(records)} records to {table_name}")
                
                for record_data in records:
                    total_records += 1
                    
                    try:
                        result = await self._import_single_record(
                            model_class, record_data, strategy, organization_id, dry_run
                        )
                        
                        if result["status"] == "imported":
                            imported_records += 1
                        elif result["status"] == "skipped":
                            skipped_records += 1
                        elif result["status"] == "conflict":
                            conflicts.append(result["conflict"])
                            skipped_records += 1
                        
                    except Exception as e:
                        error_records += 1
                        logger.error(f"Error importing record from {table_name}", 
                                   error=str(e), record_id=record_data.get('id'))
            
            # Commit transaction if not dry run
            if not dry_run and error_records == 0:
                self.db.commit()
                success = True
                message = f"Import completed successfully: {imported_records} imported, {skipped_records} skipped"
            elif dry_run:
                self.db.rollback()
                success = True
                message = f"Dry run completed: {imported_records} would be imported, {skipped_records} would be skipped"
            else:
                self.db.rollback()
                success = False
                message = f"Import failed with {error_records} errors"
            
        except Exception as e:
            self.db.rollback()
            success = False
            message = f"Import failed: {str(e)}"
            logger.error("Import failed", error=str(e))
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        result = ImportResult(
            success=success,
            total_records=total_records,
            imported_records=imported_records,
            skipped_records=skipped_records,
            error_records=error_records,
            conflicts=conflicts,
            processing_time=processing_time,
            message=message
        )
        
        logger.info("Data import completed",
                   success=success,
                   total_records=total_records,
                   imported=imported_records,
                   skipped=skipped_records,
                   errors=error_records,
                   conflicts=len(conflicts),
                   processing_time=processing_time)
        
        return result
    
    async def _parse_jsonl_import(self, data: Union[str, bytes]) -> Dict[str, Any]:
        """Parse JSONL format import data."""
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        
        lines = data.strip().split('\n')
        parsed_data = {"data": {}}
        
        for line in lines:
            if not line.strip():
                continue
            
            try:
                record = json.loads(line)
                
                # Handle metadata
                if "_metadata" in record:
                    parsed_data["_metadata"] = record["_metadata"]
                    continue
                
                # Handle table data
                table_name = record.pop("_table", None)
                if table_name:
                    if table_name not in parsed_data["data"]:
                        parsed_data["data"][table_name] = []
                    parsed_data["data"][table_name].append(record)
                
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSONL line: {line[:100]}...", error=str(e))
        
        return parsed_data
    
    async def _parse_json_import(self, data: Union[str, bytes]) -> Dict[str, Any]:
        """Parse JSON format import data."""
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        
        return json.loads(data)
    
    async def _parse_csv_import(self, data: bytes) -> Dict[str, Any]:
        """Parse CSV ZIP format import data."""
        parsed_data = {"data": {}}
        
        with zipfile.ZipFile(io.BytesIO(data), 'r') as zip_file:
            # Read metadata
            if "_metadata.json" in zip_file.namelist():
                metadata_content = zip_file.read("_metadata.json").decode('utf-8')
                parsed_data["_metadata"] = json.loads(metadata_content)
            
            # Read CSV files
            for filename in zip_file.namelist():
                if filename.endswith('.csv'):
                    table_name = filename.replace('.csv', '')
                    csv_content = zip_file.read(filename).decode('utf-8')
                    
                    csv_reader = csv.DictReader(io.StringIO(csv_content))
                    parsed_data["data"][table_name] = list(csv_reader)
        
        return parsed_data
    
    async def _import_single_record(
        self,
        model_class: Any,
        record_data: Dict[str, Any],
        strategy: ImportStrategy,
        organization_id: Optional[int],
        dry_run: bool
    ) -> Dict[str, Any]:
        """Import a single record with conflict resolution."""
        
        # Validate and prepare record data
        prepared_data = {}
        for column in inspect(model_class).columns:
            column_name = column.name
            if column_name in record_data:
                value = record_data[column_name]
                prepared_data[column_name] = self._deserialize_value(value, str(column.type))
        
        # Apply organization filter if needed
        if organization_id and issubclass(model_class, TenantModel):
            prepared_data['org_id'] = organization_id
        
        # Check for existing record
        record_id = prepared_data.get('id')
        existing_record = None
        
        if record_id:
            existing_record = self.db.query(model_class).filter(model_class.id == record_id).first()
        
        # Handle conflicts based on strategy
        if existing_record:
            if strategy == ImportStrategy.SKIP:
                return {"status": "skipped", "message": "Record already exists"}
            
            elif strategy == ImportStrategy.ERROR:
                conflict = ImportConflict(
                    table=model_class.__tablename__,
                    record_id=record_id,
                    conflict_type=ConflictType.DUPLICATE_ID,
                    message="Record with this ID already exists",
                    current_data={c.name: getattr(existing_record, c.name) for c in inspect(model_class).columns},
                    incoming_data=prepared_data
                )
                return {"status": "conflict", "conflict": conflict}
            
            elif strategy == ImportStrategy.OVERWRITE:
                if not dry_run:
                    # Update existing record
                    for key, value in prepared_data.items():
                        if hasattr(existing_record, key):
                            setattr(existing_record, key, value)
                    self.db.flush()
                return {"status": "imported", "message": "Record updated"}
            
            elif strategy == ImportStrategy.MERGE:
                # Merge only non-null values
                if not dry_run:
                    for key, value in prepared_data.items():
                        if value is not None and hasattr(existing_record, key):
                            setattr(existing_record, key, value)
                    self.db.flush()
                return {"status": "imported", "message": "Record merged"}
        
        else:
            # Create new record
            if not dry_run:
                try:
                    new_record = model_class(**prepared_data)
                    self.db.add(new_record)
                    self.db.flush()
                except IntegrityError as e:
                    self.db.rollback()
                    conflict = ImportConflict(
                        table=model_class.__tablename__,
                        record_id=record_id,
                        conflict_type=ConflictType.DUPLICATE_UNIQUE,
                        message=f"Integrity constraint violation: {str(e)}",
                        current_data={},
                        incoming_data=prepared_data
                    )
                    return {"status": "conflict", "conflict": conflict}
            
            return {"status": "imported", "message": "New record created"}
    
    async def compare_datasets(
        self,
        source_data: str,
        target_organization_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Compare import data with current database state.
        Generates diff report showing additions, modifications, and deletions.
        """
        logger.info("Starting dataset comparison")
        
        # Parse source data
        if source_data.startswith('{'):
            parsed_data = json.loads(source_data)
        else:
            parsed_data = await self._parse_jsonl_import(source_data)
        
        source_tables = parsed_data.get("data", {})
        
        comparison_result = {
            "summary": {
                "tables_compared": 0,
                "total_additions": 0,
                "total_modifications": 0,
                "total_deletions": 0
            },
            "tables": {}
        }
        
        # Compare each table
        for table_name, source_records in source_tables.items():
            if table_name not in self.model_registry:
                continue
            
            model_class = self.model_registry[table_name]
            
            # Get current data from database
            query = self.db.query(model_class)
            if target_organization_id and issubclass(model_class, TenantModel):
                query = query.filter(model_class.org_id == target_organization_id)
            
            current_records = query.all()
            
            # Convert to dictionaries for comparison
            current_dict = {}
            for record in current_records:
                record_data = {}
                for column in inspect(model_class).columns:
                    value = getattr(record, column.name)
                    record_data[column.name] = self._serialize_value(value)
                current_dict[record.id] = record_data
            
            source_dict = {record['id']: record for record in source_records if 'id' in record}
            
            # Find differences
            current_ids = set(current_dict.keys())
            source_ids = set(source_dict.keys())
            
            additions = source_ids - current_ids
            deletions = current_ids - source_ids
            potential_modifications = current_ids & source_ids
            
            modifications = []
            for record_id in potential_modifications:
                current_record = current_dict[record_id]
                source_record = source_dict[record_id]
                
                # Compare field by field
                changes = {}
                for field, source_value in source_record.items():
                    current_value = current_record.get(field)
                    if current_value != source_value:
                        changes[field] = {
                            "current": current_value,
                            "source": source_value
                        }
                
                if changes:
                    modifications.append({
                        "id": record_id,
                        "changes": changes
                    })
            
            table_result = {
                "additions": [source_dict[rid] for rid in additions],
                "modifications": modifications,
                "deletions": [current_dict[rid] for rid in deletions],
                "summary": {
                    "additions": len(additions),
                    "modifications": len(modifications),
                    "deletions": len(deletions)
                }
            }
            
            comparison_result["tables"][table_name] = table_result
            comparison_result["summary"]["tables_compared"] += 1
            comparison_result["summary"]["total_additions"] += len(additions)
            comparison_result["summary"]["total_modifications"] += len(modifications)
            comparison_result["summary"]["total_deletions"] += len(deletions)
        
        logger.info("Dataset comparison completed",
                   tables=comparison_result["summary"]["tables_compared"],
                   additions=comparison_result["summary"]["total_additions"],
                   modifications=comparison_result["summary"]["total_modifications"],
                   deletions=comparison_result["summary"]["total_deletions"])
        
        return comparison_result
    
    async def validate_import_data(self, import_data: Union[str, bytes], format: ExportFormat) -> List[str]:
        """
        Validate import data structure and integrity.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        try:
            if format == ExportFormat.JSONL:
                parsed_data = await self._parse_jsonl_import(import_data)
            elif format == ExportFormat.JSON:
                parsed_data = await self._parse_json_import(import_data)
            elif format == ExportFormat.CSV:
                parsed_data = await self._parse_csv_import(import_data)
            else:
                errors.append(f"Unsupported format: {format}")
                return errors
            
            # Validate structure
            if "data" not in parsed_data:
                errors.append("Missing 'data' section in import file")
                return errors
            
            # Validate each table
            for table_name, records in parsed_data["data"].items():
                if table_name not in self.model_registry:
                    errors.append(f"Unknown table: {table_name}")
                    continue
                
                model_class = self.model_registry[table_name]
                required_columns = {col.name for col in inspect(model_class).columns if not col.nullable and col.default is None}
                
                for i, record in enumerate(records):
                    missing_required = required_columns - set(record.keys())
                    if missing_required:
                        errors.append(f"Table {table_name}, record {i}: missing required fields: {missing_required}")
            
        except Exception as e:
            errors.append(f"Failed to parse import data: {str(e)}")
        
        return errors


# Convenience functions for direct usage
async def export_organization_data(
    db: Session,
    organization_id: int,
    format: ExportFormat = ExportFormat.JSONL,
    exported_by: str = "system"
) -> Tuple[str, ExportMetadata]:
    """Export data for a specific organization."""
    service = DataExportImportService(db)
    return await service.export_data(format, organization_id, None, exported_by)


async def import_organization_data(
    db: Session,
    import_data: Union[str, bytes],
    organization_id: int,
    format: ExportFormat = ExportFormat.JSONL,
    strategy: ImportStrategy = ImportStrategy.SKIP,
    dry_run: bool = False
) -> ImportResult:
    """Import data for a specific organization."""
    service = DataExportImportService(db)
    return await service.import_data(import_data, format, strategy, organization_id, dry_run)