#!/usr/bin/env python3
"""
Data Export/Import CLI Utility
CLI segédprogram az adatok export/import műveleteihez

Usage examples:
  python data_cli.py export --org-id 1 --format jsonl --output export.jsonl
  python data_cli.py import --file export.jsonl --format jsonl --org-id 1 --strategy skip
  python data_cli.py compare --file export.jsonl --org-id 1
  python data_cli.py round-trip --org-id 1
"""
import asyncio
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
import json

# Add parent directory to path to import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.data_export_import_service import (
    DataExportImportService,
    ExportFormat,
    ImportStrategy,
    export_organization_data,
    import_organization_data
)


def setup_parser():
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Data Export/Import CLI Utility for GarageReg",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export organization data
  %(prog)s export --org-id 1 --format jsonl --output backup.jsonl
  
  # Import data with skip strategy
  %(prog)s import --file backup.jsonl --format jsonl --org-id 1 --strategy skip
  
  # Compare import file with database
  %(prog)s compare --file backup.jsonl --org-id 1
  
  # Run round-trip integrity test
  %(prog)s round-trip --org-id 1
  
  # Validate import file
  %(prog)s validate --file backup.jsonl --format jsonl
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export data from database')
    export_parser.add_argument('--org-id', type=int, help='Organization ID (optional for full export)')
    export_parser.add_argument('--format', choices=['jsonl', 'json', 'csv'], default='jsonl', help='Export format')
    export_parser.add_argument('--output', '-o', required=True, help='Output file path')
    export_parser.add_argument('--tables', nargs='*', help='Specific tables to export')
    export_parser.add_argument('--exported-by', default='cli_user', help='User identifier for export')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import data into database')
    import_parser.add_argument('--file', '-f', required=True, help='Import file path')
    import_parser.add_argument('--format', choices=['jsonl', 'json', 'csv'], default='jsonl', help='Import format')
    import_parser.add_argument('--org-id', type=int, help='Target organization ID')
    import_parser.add_argument('--strategy', choices=['skip', 'overwrite', 'merge', 'error'], 
                             default='skip', help='Conflict resolution strategy')
    import_parser.add_argument('--dry-run', action='store_true', help='Validate only, do not actually import')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare import file with database')
    compare_parser.add_argument('--file', '-f', required=True, help='Import file path')
    compare_parser.add_argument('--org-id', type=int, help='Organization ID for comparison')
    compare_parser.add_argument('--output', '-o', help='Save comparison report to file')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate import file structure')
    validate_parser.add_argument('--file', '-f', required=True, help='File to validate')
    validate_parser.add_argument('--format', choices=['jsonl', 'json', 'csv'], default='jsonl', help='File format')
    
    # Round-trip test command
    roundtrip_parser = subparsers.add_parser('round-trip', help='Run round-trip integrity test')
    roundtrip_parser.add_argument('--org-id', type=int, required=True, help='Organization ID to test')
    roundtrip_parser.add_argument('--tables', nargs='*', help='Specific tables to test')
    roundtrip_parser.add_argument('--actual-delete', action='store_true', 
                                help='Actually delete data (DANGEROUS - use with caution)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available organizations and tables')
    list_parser.add_argument('--type', choices=['orgs', 'tables'], default='orgs', 
                           help='List organizations or tables')
    
    return parser


async def cmd_export(args):
    """Handle export command."""
    print(f"🚀 Exporting data...")
    print(f"   Organization ID: {args.org_id or 'All'}")
    print(f"   Format: {args.format}")
    print(f"   Output: {args.output}")
    
    db = SessionLocal()
    try:
        service = DataExportImportService(db)
        
        # Determine export format
        export_format = ExportFormat(args.format)
        
        # Perform export
        export_data, metadata = await service.export_data(
            format=export_format,
            organization_id=args.org_id,
            tables=args.tables,
            exported_by=args.exported_by
        )
        
        # Write to file
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if export_format == ExportFormat.CSV:
            # For CSV, write binary data (ZIP file)
            with open(output_path, 'wb') as f:
                f.write(export_data)
        else:
            # For JSONL/JSON, write text data
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(export_data)
        
        print(f"✅ Export completed successfully!")
        print(f"   Export ID: {metadata.export_id}")
        print(f"   Records: {metadata.total_records}")
        print(f"   Tables: {metadata.total_tables}")
        print(f"   Checksum: {metadata.checksum}")
        print(f"   File: {output_path}")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return 1
    finally:
        db.close()
    
    return 0


async def cmd_import(args):
    """Handle import command."""
    print(f"🔄 Importing data...")
    print(f"   File: {args.file}")
    print(f"   Format: {args.format}")
    print(f"   Strategy: {args.strategy}")
    print(f"   Organization ID: {args.org_id or 'Auto-detect'}")
    print(f"   Dry run: {args.dry_run}")
    
    # Check if file exists
    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        return 1
    
    db = SessionLocal()
    try:
        service = DataExportImportService(db)
        
        # Read import file
        import_format = ExportFormat(args.format)
        
        if import_format == ExportFormat.CSV:
            with open(args.file, 'rb') as f:
                import_data = f.read()
        else:
            with open(args.file, 'r', encoding='utf-8') as f:
                import_data = f.read()
        
        # Validate first
        print("   🔍 Validating import data...")
        validation_errors = await service.validate_import_data(import_data, import_format)
        
        if validation_errors:
            print(f"❌ Validation failed with {len(validation_errors)} errors:")
            for error in validation_errors[:5]:  # Show first 5 errors
                print(f"   - {error}")
            if len(validation_errors) > 5:
                print(f"   ... and {len(validation_errors) - 5} more errors")
            return 1
        
        print("   ✅ Validation passed")
        
        # Perform import
        import_strategy = ImportStrategy(args.strategy)
        
        result = await service.import_data(
            import_data=import_data,
            format=import_format,
            strategy=import_strategy,
            organization_id=args.org_id,
            dry_run=args.dry_run
        )
        
        # Display results
        if result.success:
            print(f"✅ Import {'simulation' if args.dry_run else 'completed'} successfully!")
        else:
            print(f"❌ Import failed!")
        
        print(f"   Total records: {result.total_records}")
        print(f"   Imported: {result.imported_records}")
        print(f"   Skipped: {result.skipped_records}")
        print(f"   Errors: {result.error_records}")
        print(f"   Conflicts: {len(result.conflicts)}")
        print(f"   Processing time: {result.processing_time:.2f} seconds")
        
        if result.conflicts:
            print(f"\n   ⚠️ Conflicts found:")
            for conflict in result.conflicts[:5]:  # Show first 5 conflicts
                print(f"      - {conflict.table} ID {conflict.record_id}: {conflict.message}")
            if len(result.conflicts) > 5:
                print(f"      ... and {len(result.conflicts) - 5} more conflicts")
        
        return 0 if result.success else 1
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return 1
    finally:
        db.close()


async def cmd_compare(args):
    """Handle compare command."""
    print(f"🔍 Comparing data...")
    print(f"   File: {args.file}")
    print(f"   Organization ID: {args.org_id or 'Auto-detect'}")
    
    # Check if file exists
    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        return 1
    
    db = SessionLocal()
    try:
        service = DataExportImportService(db)
        
        # Read comparison file
        with open(args.file, 'r', encoding='utf-8') as f:
            source_data = f.read()
        
        # Perform comparison
        comparison = await service.compare_datasets(
            source_data=source_data,
            target_organization_id=args.org_id
        )
        
        # Display results
        print(f"📊 Comparison Results:")
        print(f"   Tables compared: {comparison['summary']['tables_compared']}")
        print(f"   Total additions: {comparison['summary']['total_additions']}")
        print(f"   Total modifications: {comparison['summary']['total_modifications']}")
        print(f"   Total deletions: {comparison['summary']['total_deletions']}")
        
        if comparison['summary']['total_additions'] + comparison['summary']['total_modifications'] + comparison['summary']['total_deletions'] == 0:
            print("   ✅ Data is identical - no differences found!")
        else:
            print("\n   📋 Table-by-table breakdown:")
            for table_name, table_diff in comparison['tables'].items():
                summary = table_diff['summary']
                if summary['additions'] + summary['modifications'] + summary['deletions'] > 0:
                    print(f"      {table_name}: +{summary['additions']} ~{summary['modifications']} -{summary['deletions']}")
        
        # Save detailed report if requested
        if args.output:
            report_path = Path(args.output)
            report_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(comparison, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"   📄 Detailed report saved to: {report_path}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Comparison failed: {e}")
        return 1
    finally:
        db.close()


async def cmd_validate(args):
    """Handle validate command."""
    print(f"🔍 Validating import file...")
    print(f"   File: {args.file}")
    print(f"   Format: {args.format}")
    
    # Check if file exists
    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        return 1
    
    db = SessionLocal()
    try:
        service = DataExportImportService(db)
        
        # Read file
        file_format = ExportFormat(args.format)
        
        if file_format == ExportFormat.CSV:
            with open(args.file, 'rb') as f:
                file_data = f.read()
        else:
            with open(args.file, 'r', encoding='utf-8') as f:
                file_data = f.read()
        
        # Validate
        validation_errors = await service.validate_import_data(file_data, file_format)
        
        if validation_errors:
            print(f"❌ Validation failed with {len(validation_errors)} errors:")
            for error in validation_errors:
                print(f"   - {error}")
            return 1
        else:
            print("✅ Validation passed - file is valid for import!")
            return 0
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return 1
    finally:
        db.close()


async def cmd_round_trip(args):
    """Handle round-trip test command."""
    print(f"🔄 Running round-trip integrity test...")
    print(f"   Organization ID: {args.org_id}")
    print(f"   Tables: {args.tables or 'All'}")
    print(f"   Actual delete: {args.actual_delete}")
    
    if args.actual_delete:
        response = input("⚠️  WARNING: This will actually delete data! Are you sure? (type 'DELETE' to confirm): ")
        if response != 'DELETE':
            print("❌ Operation cancelled")
            return 1
    
    db = SessionLocal()
    try:
        service = DataExportImportService(db)
        
        # Step 1: Export original data
        print("   1️⃣ Exporting original data...")
        original_export, original_metadata = await service.export_data(
            format=ExportFormat.JSONL,
            organization_id=args.org_id,
            tables=args.tables,
            exported_by="round_trip_cli"
        )
        
        original_checksum = service._calculate_checksum(original_export)
        print(f"      ✅ Exported {original_metadata.total_records} records")
        
        if not args.actual_delete:
            # Safe mode: just test import without deletion
            print("   2️⃣ Testing import (dry run)...")
            import_result = await service.import_data(
                import_data=original_export,
                format=ExportFormat.JSONL,
                strategy=ImportStrategy.OVERWRITE,
                organization_id=args.org_id,
                dry_run=True
            )
            
            if import_result.success:
                print("   ✅ Round-trip test completed successfully (dry run mode)")
                print(f"      Would import {import_result.imported_records} records")
                print("      Use --actual-delete to perform full test with real data deletion")
            else:
                print("   ❌ Round-trip test failed in dry run")
                print(f"      Errors: {import_result.error_records}")
                print(f"      Conflicts: {len(import_result.conflicts)}")
            
            return 0 if import_result.success else 1
        
        else:
            # Full test mode with actual deletion (dangerous!)
            print("   2️⃣ Deleting data...")
            # Implementation would go here - similar to test script
            # For safety, we'll skip this in CLI for now
            print("   ⚠️ Actual deletion not implemented in CLI for safety")
            print("      Use test_complete_export_import.py for full round-trip testing")
            return 1
        
    except Exception as e:
        print(f"❌ Round-trip test failed: {e}")
        return 1
    finally:
        db.close()


async def cmd_list(args):
    """Handle list command."""
    db = SessionLocal()
    try:
        service = DataExportImportService(db)
        
        if args.type == 'orgs':
            print("📋 Available Organizations:")
            
            # Query organizations
            from app.models.organization import Organization
            orgs = db.query(Organization).filter(Organization.is_active == True).all()
            
            if not orgs:
                print("   No active organizations found")
            else:
                for org in orgs:
                    print(f"   {org.id}: {org.name} ({org.display_name})")
        
        elif args.type == 'tables':
            print("📋 Available Tables:")
            
            for table_name, model_class in service.model_registry.items():
                is_tenant = issubclass(model_class, service.db.query(model_class).first().__class__.__bases__[0], TenantModel) if service.db.query(model_class).first() else False
                tenant_info = " (tenant-aware)" if is_tenant else ""
                print(f"   {table_name}{tenant_info}")
        
        return 0
        
    except Exception as e:
        print(f"❌ List command failed: {e}")
        return 1
    finally:
        db.close()


async def main():
    """Main CLI entry point."""
    parser = setup_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    print(f"🔧 GarageReg Data Export/Import CLI")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # Route to appropriate command handler
    if args.command == 'export':
        return await cmd_export(args)
    elif args.command == 'import':
        return await cmd_import(args)
    elif args.command == 'compare':
        return await cmd_compare(args)
    elif args.command == 'validate':
        return await cmd_validate(args)
    elif args.command == 'round-trip':
        return await cmd_round_trip(args)
    elif args.command == 'list':
        return await cmd_list(args)
    else:
        print(f"❌ Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)