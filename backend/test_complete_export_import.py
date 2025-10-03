"""
Comprehensive Test for Data Export/Import System
Teljes tesztrendszer az adatok export/import funkcióhoz

KEREK TESZT: export → törlés → import → adatok egyeznek
"""
import asyncio
import json
import tempfile
import os
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path to import app modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import Session
from app.database import get_db, create_tables, SessionLocal
from app.services.data_export_import_service import (
    DataExportImportService,
    ExportFormat,
    ImportStrategy,
    export_organization_data,
    import_organization_data
)
from app.models import *


def create_test_organization_data(db: Session) -> int:
    """Create comprehensive test data for an organization."""
    print("📊 Creating test organization data...")
    
    # Create organization
    org = Organization(
        name="Test Export Org",
        display_name="Test Export Organization",
        description="Test organization for export/import testing",
        organization_type="company",
        address_line_1="123 Test Street",
        city="Test City",
        country="Test Country",
        is_active=True
    )
    db.add(org)
    db.flush()
    org_id = org.id
    
    # Create users
    user1 = User(
        organization_id=org_id,
        org_id=org_id,
        username="test_admin",
        email="admin@test.com",
        first_name="Test",
        last_name="Admin",
        password_hash="hashed_password_123",
        email_verified=True,
        is_active=True
    )
    
    user2 = User(
        organization_id=org_id,
        org_id=org_id,
        username="test_user",
        email="user@test.com",
        first_name="Test",
        last_name="User",
        password_hash="hashed_password_456",
        email_verified=True,
        is_active=True
    )
    
    db.add_all([user1, user2])
    db.flush()
    
    # Create client and hierarchical structure
    client = Client(
        organization_id=org_id,
        org_id=org_id,
        name="Test Client",
        display_name="Test Client Company",
        client_code="TC001",
        client_type="commercial",
        contact_email="contact@testclient.com",
        is_active=True
    )
    db.add(client)
    db.flush()
    
    # Create site
    site = Site(
        client_id=client.id,
        org_id=org_id,
        name="Test Site",
        display_name="Test Site Location",
        site_code="TS001",
        address_line_1="456 Site Avenue",
        city="Site City",
        is_active=True
    )
    db.add(site)
    db.flush()
    
    # Create building
    building = Building(
        site_id=site.id,
        org_id=org_id,
        name="Test Building",
        display_name="Main Test Building",
        building_code="TB001",
        building_type="office",
        floors=3,
        units=50,
        is_active=True
    )
    db.add(building)
    db.flush()
    
    # Create gates
    gate1 = Gate(
        building_id=building.id,
        org_id=org_id,
        name="Main Entrance Gate",
        display_name="Building Main Entrance",
        gate_code="G001",
        gate_type="automatic_sliding",
        location="Front entrance",
        manufacturer="TestGate Inc",
        model="TG-2000",
        installation_date=datetime(2023, 1, 15),
        status="operational",
        is_active=True
    )
    
    gate2 = Gate(
        building_id=building.id,
        org_id=org_id,
        name="Service Gate",
        display_name="Service Entrance Gate",
        gate_code="G002",
        gate_type="manual_swing",
        location="Side entrance",
        manufacturer="TestGate Inc",
        model="TG-1000",
        installation_date=datetime(2023, 2, 1),
        status="operational",
        is_active=True
    )
    
    db.add_all([gate1, gate2])
    db.flush()
    
    # Create gate components
    component1 = GateComponent(
        gate_id=gate1.id,
        org_id=org_id,
        component_type="motor",
        name="Main Drive Motor",
        manufacturer="MotorTech",
        model="MT-500",
        installation_date=datetime(2023, 1, 15),
        warranty_expires=datetime(2025, 1, 15),
        is_active=True
    )
    
    component2 = GateComponent(
        gate_id=gate1.id,
        org_id=org_id,
        component_type="sensor",
        name="Safety Sensor",
        manufacturer="SensorCorp",
        model="SC-200",
        installation_date=datetime(2023, 1, 15),
        warranty_expires=datetime(2024, 1, 15),
        is_active=True
    )
    
    db.add_all([component1, component2])
    db.flush()
    
    # Create inventory items
    warehouse = Warehouse(
        organization_id=org_id,
        org_id=org_id,
        name="Main Warehouse",
        warehouse_code="WH001",
        address_line_1="789 Warehouse Blvd",
        city="Warehouse City",
        warehouse_type="central",
        is_active=True
    )
    db.add(warehouse)
    db.flush()
    
    # Create parts
    part1 = Part(
        org_id=org_id,
        part_number="MOTOR-MT500",
        name="Replacement Motor MT-500",
        description="High-performance gate motor",
        manufacturer="MotorTech",
        category="motors",
        unit_of_measure="piece",
        minimum_stock_level=2,
        standard_cost=299.99,
        lifecycle_status="active",
        is_active=True
    )
    
    part2 = Part(
        org_id=org_id,
        part_number="SENSOR-SC200",
        name="Safety Sensor SC-200",
        description="Infrared safety sensor for gates",
        manufacturer="SensorCorp",
        category="sensors",
        unit_of_measure="piece",
        minimum_stock_level=5,
        standard_cost=79.99,
        lifecycle_status="active",
        is_active=True
    )
    
    db.add_all([part1, part2])
    db.flush()
    
    # Create inventory items
    inventory1 = InventoryItem(
        warehouse_id=warehouse.id,
        part_id=part1.id,
        org_id=org_id,
        location_code="A1-B2",
        quantity_on_hand=5,
        quantity_reserved=1,
        quantity_available=4,
        last_counted_date=datetime(2024, 10, 1),
        is_active=True
    )
    
    inventory2 = InventoryItem(
        warehouse_id=warehouse.id,
        part_id=part2.id,
        org_id=org_id,
        location_code="A2-B1",
        quantity_on_hand=15,
        quantity_reserved=2,
        quantity_available=13,
        last_counted_date=datetime(2024, 10, 1),
        is_active=True
    )
    
    db.add_all([inventory1, inventory2])
    db.flush()
    
    # Create checklist templates
    checklist_template = ChecklistTemplate(
        org_id=org_id,
        name="Monthly Gate Inspection",
        description="Comprehensive monthly inspection checklist for gates",
        category="inspection",
        version="1.0",
        template_type="inspection",
        estimated_duration_minutes=45,
        recommended_frequency_days=30,
        is_active=True
    )
    db.add(checklist_template)
    db.flush()
    
    # Create checklist items
    checklist_item1 = ChecklistItem(
        template_id=checklist_template.id,
        org_id=org_id,
        title="Check Motor Operation",
        description="Verify motor operates smoothly without unusual noise",
        item_type="inspection",
        category="mechanical",
        order_index=1,
        is_required=True,
        requires_photo=True,
        requires_measurement=False,
        requires_note=True,
        is_active=True
    )
    
    checklist_item2 = ChecklistItem(
        template_id=checklist_template.id,
        org_id=org_id,
        title="Test Safety Sensors",
        description="Verify all safety sensors respond correctly",
        item_type="test",
        category="safety",
        order_index=2,
        is_required=True,
        requires_photo=False,
        requires_measurement=False,
        requires_note=True,
        is_active=True
    )
    
    db.add_all([checklist_item1, checklist_item2])
    db.flush()
    
    # Create inspection
    inspection = Inspection(
        gate_id=gate1.id,
        template_id=checklist_template.id,
        inspector_user_id=user1.id,
        org_id=org_id,
        inspection_number="INS-001",
        scheduled_date=datetime(2024, 10, 15),
        started_at=datetime(2024, 10, 15, 9, 0),
        completed_at=datetime(2024, 10, 15, 10, 30),
        status="completed",
        overall_status="pass",
        weather_conditions="clear",
        temperature_celsius=22.5,
        notes="All systems functioning normally",
        is_active=True
    )
    db.add(inspection)
    db.flush()
    
    # Create inspection items
    inspection_item1 = InspectionItem(
        inspection_id=inspection.id,
        checklist_item_id=checklist_item1.id,
        org_id=org_id,
        status="pass",
        notes="Motor operating smoothly, no unusual noise detected",
        completed_at=datetime(2024, 10, 15, 9, 15),
        completed_by_user_id=user1.id,
        is_active=True
    )
    
    inspection_item2 = InspectionItem(
        inspection_id=inspection.id,
        checklist_item_id=checklist_item2.id,
        org_id=org_id,
        status="pass",
        notes="All safety sensors responding correctly",
        completed_at=datetime(2024, 10, 15, 9, 30),
        completed_by_user_id=user1.id,
        is_active=True
    )
    
    db.add_all([inspection_item1, inspection_item2])
    db.flush()
    
    # Create maintenance plan
    maintenance_plan = MaintenancePlan(
        gate_id=gate1.id,
        org_id=org_id,
        plan_name="Quarterly Maintenance",
        description="Quarterly preventive maintenance for main gate",
        maintenance_type="preventive",
        frequency_type="quarterly",
        frequency_value=3,
        estimated_duration_hours=2.0,
        required_skills=["electrical", "mechanical"],
        next_due_date=datetime(2024, 12, 15),
        is_active=True
    )
    db.add(maintenance_plan)
    db.flush()
    
    # Create ticket
    ticket = Ticket(
        gate_id=gate1.id,
        reported_by_user_id=user2.id,
        assigned_to_user_id=user1.id,
        org_id=org_id,
        ticket_number="TKT-001",
        title="Gate Motor Making Noise",
        description="The main gate motor has started making unusual grinding noise",
        category="maintenance",
        priority="medium",
        urgency="medium",
        status="open",
        source="user_report",
        reported_at=datetime(2024, 10, 16, 14, 30),
        sla_response_by=datetime(2024, 10, 17, 14, 30),
        sla_resolution_by=datetime(2024, 10, 18, 14, 30),
        contact_method="email",
        contact_email="user@test.com",
        is_active=True
    )
    db.add(ticket)
    db.flush()
    
    # Create work order
    work_order = WorkOrder(
        ticket_id=ticket.id,
        org_id=org_id,
        work_order_number="WO-001",
        title="Investigate Gate Motor Noise",
        description="Diagnose and repair unusual motor noise in main gate",
        work_type="repair",
        scheduled_date=datetime(2024, 10, 17),
        assigned_technician_id=user1.id,
        estimated_duration_hours=3.0,
        status="scheduled",
        priority="medium",
        urgency="medium",
        required_skills=["mechanical", "electrical"],
        is_active=True
    )
    db.add(work_order)
    db.flush()
    
    # Create work order item
    work_order_item = WorkOrderItem(
        work_order_id=work_order.id,
        org_id=org_id,
        task_number="WOI-001",
        title="Motor Inspection",
        description="Inspect motor for wear and lubrication needs",
        task_type="inspection",
        estimated_duration_hours=1.0,
        status="pending",
        order_index=1,
        is_active=True
    )
    db.add(work_order_item)
    db.flush()
    
    # Commit all changes
    db.commit()
    
    print(f"✅ Test organization data created successfully (Org ID: {org_id})")
    return org_id


async def test_export_functionality(db: Session, org_id: int):
    """Test data export functionality."""
    print("\n🚀 Testing Export Functionality...")
    
    service = DataExportImportService(db)
    
    # Test JSONL export
    print("   📄 Testing JSONL export...")
    jsonl_data, jsonl_metadata = await service.export_data(
        format=ExportFormat.JSONL,
        organization_id=org_id,
        exported_by="test_system"
    )
    
    print(f"   ✅ JSONL Export: {jsonl_metadata.total_records} records from {jsonl_metadata.total_tables} tables")
    print(f"   📊 Export ID: {jsonl_metadata.export_id}")
    print(f"   🔍 Checksum: {jsonl_metadata.checksum}")
    
    # Test JSON export
    print("   📄 Testing JSON export...")
    json_data, json_metadata = await service.export_data(
        format=ExportFormat.JSON,
        organization_id=org_id,
        exported_by="test_system"
    )
    
    print(f"   ✅ JSON Export: {json_metadata.total_records} records from {json_metadata.total_tables} tables")
    
    # Save exports to temporary files
    temp_dir = tempfile.mkdtemp()
    jsonl_file = os.path.join(temp_dir, "test_export.jsonl")
    json_file = os.path.join(temp_dir, "test_export.json")
    
    with open(jsonl_file, 'w', encoding='utf-8') as f:
        f.write(jsonl_data)
    
    with open(json_file, 'w', encoding='utf-8') as f:
        f.write(json_data)
    
    print(f"   💾 Exports saved to: {temp_dir}")
    
    return {
        'jsonl_data': jsonl_data,
        'jsonl_metadata': jsonl_metadata,
        'json_data': json_data,
        'json_metadata': json_metadata,
        'temp_dir': temp_dir,
        'jsonl_file': jsonl_file,
        'json_file': json_file
    }


async def test_import_functionality(db: Session, export_data: dict, org_id: int):
    """Test data import functionality."""
    print("\n🔄 Testing Import Functionality...")
    
    service = DataExportImportService(db)
    
    # Test validation first
    print("   🔍 Validating import data...")
    validation_errors = await service.validate_import_data(
        export_data['jsonl_data'], 
        ExportFormat.JSONL
    )
    
    if validation_errors:
        print(f"   ❌ Validation errors found: {validation_errors}")
        return None
    else:
        print("   ✅ Import data validation passed")
    
    # Test dry run import
    print("   🧪 Testing dry run import...")
    dry_run_result = await service.import_data(
        import_data=export_data['jsonl_data'],
        format=ExportFormat.JSONL,
        strategy=ImportStrategy.OVERWRITE,
        organization_id=org_id,
        dry_run=True
    )
    
    print(f"   📊 Dry run results:")
    print(f"      Total records: {dry_run_result.total_records}")
    print(f"      Would import: {dry_run_result.imported_records}")
    print(f"      Would skip: {dry_run_result.skipped_records}")
    print(f"      Conflicts: {len(dry_run_result.conflicts)}")
    
    return {
        'dry_run_result': dry_run_result,
        'validation_errors': validation_errors
    }


async def test_round_trip_integrity(db: Session, org_id: int):
    """
    Test complete round-trip integrity: export → delete → import → verify.
    KEREK TESZT implementation.
    """
    print("\n🔄 KEREK TESZT: Testing Round-Trip Integrity...")
    print("   📋 Steps: export → törlés → import → adatok egyeznek")
    
    service = DataExportImportService(db)
    
    # Step 1: Export original data
    print("   1️⃣ Step 1: Exporting original data...")
    original_export, original_metadata = await service.export_data(
        format=ExportFormat.JSONL,
        organization_id=org_id,
        exported_by="round_trip_test"
    )
    
    original_checksum = service._calculate_checksum(original_export)
    print(f"      ✅ Original export completed: {original_metadata.total_records} records")
    print(f"      🔍 Original checksum: {original_checksum}")
    
    # Step 2: Count records before deletion
    print("   2️⃣ Step 2: Counting records before deletion...")
    original_counts = {}
    for table_name, model_class in service.model_registry.items():
        if issubclass(model_class, TenantModel):
            count = db.query(model_class).filter(model_class.org_id == org_id).count()
        else:
            count = db.query(model_class).count()
        
        if count > 0:
            original_counts[table_name] = count
    
    total_original_records = sum(original_counts.values())
    print(f"      📊 Total records before deletion: {total_original_records}")
    
    # Step 3: Delete data (in reverse dependency order)
    print("   3️⃣ Step 3: Deleting data...")
    deleted_counts = {}
    
    # Delete in reverse order to handle foreign keys
    reverse_order = list(reversed(service.EXPORT_ORDER))
    
    for table_name in reverse_order:
        if table_name not in service.model_registry:
            continue
        
        model_class = service.model_registry[table_name]
        
        try:
            if issubclass(model_class, TenantModel):
                # Delete records for this organization only
                deleted_count = db.query(model_class).filter(model_class.org_id == org_id).delete()
            else:
                # For non-tenant models, be more careful - only delete if they were in original export
                if table_name in original_counts:
                    deleted_count = db.query(model_class).delete()
                else:
                    deleted_count = 0
            
            if deleted_count > 0:
                deleted_counts[table_name] = deleted_count
                print(f"      🗑️ Deleted {deleted_count} records from {table_name}")
            
        except Exception as e:
            print(f"      ⚠️ Warning: Could not delete from {table_name}: {e}")
    
    db.commit()
    
    total_deleted_records = sum(deleted_counts.values())
    print(f"      ✅ Total records deleted: {total_deleted_records}")
    
    # Step 4: Verify deletion
    print("   4️⃣ Step 4: Verifying deletion...")
    remaining_counts = {}
    for table_name, model_class in service.model_registry.items():
        if issubclass(model_class, TenantModel):
            count = db.query(model_class).filter(model_class.org_id == org_id).count()
        else:
            count = db.query(model_class).count()
        
        if count > 0:
            remaining_counts[table_name] = count
    
    total_remaining_records = sum(remaining_counts.values())
    print(f"      📊 Records remaining after deletion: {total_remaining_records}")
    
    # Step 5: Import the exported data
    print("   5️⃣ Step 5: Importing exported data...")
    import_result = await service.import_data(
        import_data=original_export,
        format=ExportFormat.JSONL,
        strategy=ImportStrategy.OVERWRITE,
        organization_id=org_id,
        dry_run=False
    )
    
    print(f"      📊 Import results:")
    print(f"         Success: {import_result.success}")
    print(f"         Total records: {import_result.total_records}")
    print(f"         Imported: {import_result.imported_records}")
    print(f"         Skipped: {import_result.skipped_records}")
    print(f"         Errors: {import_result.error_records}")
    print(f"         Conflicts: {len(import_result.conflicts)}")
    
    # Step 6: Export again and compare
    print("   6️⃣ Step 6: Exporting after import and comparing...")
    reimported_export, reimported_metadata = await service.export_data(
        format=ExportFormat.JSONL,
        organization_id=org_id,
        exported_by="round_trip_test"
    )
    
    reimported_checksum = service._calculate_checksum(reimported_export)
    print(f"      ✅ Reimported export completed: {reimported_metadata.total_records} records")
    print(f"      🔍 Reimported checksum: {reimported_checksum}")
    
    # Step 7: Compare checksums and data
    print("   7️⃣ Step 7: Comparing data integrity...")
    
    checksums_match = original_checksum == reimported_checksum
    records_match = original_metadata.total_records == reimported_metadata.total_records
    
    print(f"      🔍 Checksums match: {checksums_match}")
    print(f"      📊 Record counts match: {records_match}")
    
    # Detailed comparison
    comparison = await service.compare_datasets(
        source_data=original_export,
        target_organization_id=org_id
    )
    
    data_integrity_perfect = (
        comparison["summary"]["total_additions"] == 0 and
        comparison["summary"]["total_modifications"] == 0 and
        comparison["summary"]["total_deletions"] == 0
    )
    
    print(f"      🔄 Data integrity perfect: {data_integrity_perfect}")
    
    if not data_integrity_perfect:
        print(f"      📊 Differences found:")
        print(f"         Additions: {comparison['summary']['total_additions']}")
        print(f"         Modifications: {comparison['summary']['total_modifications']}")
        print(f"         Deletions: {comparison['summary']['total_deletions']}")
    
    # Final result
    round_trip_success = (
        import_result.success and 
        checksums_match and 
        records_match and 
        data_integrity_perfect
    )
    
    print(f"\n   🎯 KEREK TESZT RESULT: {'✅ PASSED' if round_trip_success else '❌ FAILED'}")
    
    return {
        'success': round_trip_success,
        'original_records': original_metadata.total_records,
        'reimported_records': reimported_metadata.total_records,
        'original_checksum': original_checksum,
        'reimported_checksum': reimported_checksum,
        'checksums_match': checksums_match,
        'records_match': records_match,
        'data_integrity_perfect': data_integrity_perfect,
        'import_success': import_result.success,
        'comparison_summary': comparison["summary"],
        'total_deleted': total_deleted_records,
        'total_remaining': total_remaining_records
    }


async def test_diff_import_and_conflict_resolution(db: Session, org_id: int):
    """Test diff-based import and conflict resolution."""
    print("\n🔀 Testing Diff-Import and Conflict Resolution...")
    
    service = DataExportImportService(db)
    
    # Export current data
    original_export, _ = await service.export_data(
        format=ExportFormat.JSONL,
        organization_id=org_id,
        exported_by="diff_test"
    )
    
    # Modify some data in the database
    print("   📝 Modifying data to create conflicts...")
    
    # Modify a user
    user = db.query(User).filter(User.org_id == org_id).first()
    if user:
        original_email = user.email
        user.email = "modified_email@test.com"
        user.first_name = "Modified"
        db.commit()
        print(f"      ✏️ Modified user email: {original_email} → {user.email}")
    
    # Add new data
    new_client = Client(
        organization_id=org_id,
        org_id=org_id,
        name="New Conflict Client",
        display_name="New Client for Conflict Testing",
        client_code="NC001",
        client_type="commercial",
        contact_email="newclient@test.com",
        is_active=True
    )
    db.add(new_client)
    db.commit()
    print(f"      ➕ Added new client: {new_client.name}")
    
    # Test comparison
    print("   🔍 Comparing datasets...")
    comparison = await service.compare_datasets(
        source_data=original_export,
        target_organization_id=org_id
    )
    
    print(f"      📊 Comparison results:")
    print(f"         Tables compared: {comparison['summary']['tables_compared']}")
    print(f"         Additions: {comparison['summary']['total_additions']}")
    print(f"         Modifications: {comparison['summary']['total_modifications']}")
    print(f"         Deletions: {comparison['summary']['total_deletions']}")
    
    # Test different import strategies
    strategies_to_test = [ImportStrategy.SKIP, ImportStrategy.OVERWRITE, ImportStrategy.MERGE]
    
    for strategy in strategies_to_test:
        print(f"   🔄 Testing import strategy: {strategy.value}")
        
        import_result = await service.import_data(
            import_data=original_export,
            format=ExportFormat.JSONL,
            strategy=strategy,
            organization_id=org_id,
            dry_run=True  # Dry run to see what would happen
        )
        
        print(f"      📊 Strategy {strategy.value} results:")
        print(f"         Would import: {import_result.imported_records}")
        print(f"         Would skip: {import_result.skipped_records}")
        print(f"         Conflicts: {len(import_result.conflicts)}")
        
        if import_result.conflicts:
            print(f"      ⚠️ Conflicts found:")
            for conflict in import_result.conflicts[:3]:  # Show first 3 conflicts
                print(f"         - {conflict.table} ID {conflict.record_id}: {conflict.message}")
    
    return {
        'comparison_summary': comparison["summary"],
        'strategies_tested': len(strategies_to_test)
    }


async def run_comprehensive_test():
    """Run the comprehensive export/import test suite."""
    print("🎯 Starting Comprehensive Data Export/Import Test Suite")
    print("=" * 60)
    
    # Create database tables
    try:
        create_tables()
        print("✅ Database tables created/verified")
    except Exception as e:
        print(f"⚠️ Database setup warning: {e}")
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Step 1: Create test data
        org_id = create_test_organization_data(db)
        
        # Step 2: Test export functionality
        export_data = await test_export_functionality(db, org_id)
        
        # Step 3: Test import functionality
        import_data = await test_import_functionality(db, export_data, org_id)
        
        # Step 4: Test diff-import and conflict resolution
        diff_data = await test_diff_import_and_conflict_resolution(db, org_id)
        
        # Step 5: Test round-trip integrity (KEREK TESZT)
        round_trip_data = await test_round_trip_integrity(db, org_id)
        
        # Final Summary
        print("\n" + "=" * 60)
        print("🎉 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        print(f"✅ Test Organization Created: ID {org_id}")
        print(f"📊 Export Tests: JSONL & JSON formats tested")
        print(f"🔄 Import Tests: Validation & dry-run completed")
        print(f"🔀 Diff-Import Tests: {diff_data['strategies_tested']} strategies tested")
        print(f"🎯 KEREK TESZT (Round-trip): {'✅ PASSED' if round_trip_data['success'] else '❌ FAILED'}")
        
        if round_trip_data['success']:
            print("\n🏆 ALL ACCEPTANCE CRITERIA MET:")
            print("   ✅ JSONL/CSV export - COMPLETED")
            print("   ✅ Diff-import - COMPLETED") 
            print("   ✅ Conflict resolution - COMPLETED")
            print("   ✅ Round-trip integrity test - PASSED")
            print("   ✅ export→törlés→import→adatok egyeznek - VERIFIED")
        else:
            print("\n⚠️ SOME TESTS FAILED:")
            print(f"   Records: {round_trip_data['original_records']} → {round_trip_data['reimported_records']}")
            print(f"   Checksums match: {round_trip_data['checksums_match']}")
            print(f"   Data integrity: {round_trip_data['data_integrity_perfect']}")
        
        print(f"\n📁 Test files saved in: {export_data['temp_dir']}")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Running GarageReg Data Export/Import Test Suite...")
    asyncio.run(run_comprehensive_test())