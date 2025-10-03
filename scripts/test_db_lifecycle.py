#!/usr/bin/env python3
"""
Database Migration and Seed Test Script

Tests the complete database lifecycle:
1. Fresh database creation
2. Migration application
3. Seed data insertion
4. Application functionality validation

Usage:
    python scripts/test_db_lifecycle.py [--cleanup]
"""

import os
import sys
import argparse
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add backend path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker


class DatabaseLifecycleTest:
    """Test complete database lifecycle from fresh DB to working application."""
    
    def __init__(self, cleanup: bool = False):
        self.cleanup = cleanup
        self.test_db_path = None
        self.original_db_path = None
        self.test_results = {
            "migration": False,
            "seed": False,
            "validation": False,
            "app_startup": False
        }
    
    def setup_test_database(self):
        """Create a temporary database for testing."""
        print("🧪 Setting up test database...")
        
        # Create temporary database
        temp_dir = tempfile.mkdtemp(prefix="garagereg_test_")
        self.test_db_path = os.path.join(temp_dir, "test_garagereg.db")
        
        # Backup original database if it exists
        original_db = os.path.join(backend_path, "garagereg.db")
        if os.path.exists(original_db):
            self.original_db_path = f"{original_db}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(original_db, self.original_db_path)
            print(f"📦 Original database backed up to: {self.original_db_path}")
        
        # Set environment variable for test database
        os.environ["DATABASE_URL"] = f"sqlite:///{self.test_db_path}"
        
        print(f"✅ Test database created: {self.test_db_path}")
        
    def cleanup_test_database(self):
        """Clean up test database and restore original if needed."""
        if self.cleanup and self.test_db_path:
            print("🧹 Cleaning up test database...")
            
            # Remove test database directory
            test_dir = os.path.dirname(self.test_db_path)
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)
                print("✅ Test database cleaned up")
            
            # Restore original database
            if self.original_db_path:
                original_db = os.path.join(backend_path, "garagereg.db")
                shutil.move(self.original_db_path, original_db)
                print("✅ Original database restored")
    
    def test_migration(self) -> bool:
        """Test database migration from scratch."""
        print("\n🔄 Testing database migration...")
        
        try:
            # Run migration script
            migrate_script = Path(__file__).parent / "migrate_simple.py"
            cmd = [sys.executable, str(migrate_script), "upgrade", "head"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=backend_path,
                env=os.environ.copy()
            )
            
            if result.returncode != 0:
                print(f"❌ Migration failed: {result.stderr}")
                return False
            
            # Verify database was created and has tables
            engine = create_engine(os.environ["DATABASE_URL"])
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            expected_tables = [
                "users", "roles", "permissions", "organizations", 
                "sites", "buildings", "gates", "checklist_templates"
            ]
            
            missing_tables = [table for table in expected_tables if table not in tables]
            if missing_tables:
                print(f"❌ Missing expected tables: {missing_tables}")
                return False
            
            print(f"✅ Migration successful - Created {len(tables)} tables")
            self.test_results["migration"] = True
            return True
            
        except Exception as e:
            print(f"❌ Migration test failed: {e}")
            return False
    
    def test_seed(self) -> bool:
        """Test database seeding."""
        print("\n🌱 Testing database seeding...")
        
        try:
            # Run seed script
            seed_script = Path(__file__).parent / "seed_simple.py"
            cmd = [
                sys.executable, str(seed_script),
                "--org-name", "Test Organization",
                "--gates", "3"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=os.environ.copy()
            )
            
            if result.returncode != 0:
                print(f"❌ Seeding failed: {result.stderr}")
                return False
            
            print("✅ Seeding completed successfully")
            self.test_results["seed"] = True
            return True
            
        except Exception as e:
            print(f"❌ Seed test failed: {e}")
            return False
    
    def test_data_validation(self) -> bool:
        """Validate seeded data integrity."""
        print("\n🔍 Validating seeded data...")
        
        try:
            engine = create_engine(os.environ["DATABASE_URL"])
            
            with engine.connect() as conn:
                # Check organizations
                org_result = conn.execute(text("SELECT COUNT(*) FROM organizations"))
                org_count = org_result.scalar()
                
                if org_count < 1:
                    print("❌ No organizations found")
                    return False
                
                # Check users
                user_result = conn.execute(text("SELECT COUNT(*) FROM users"))
                user_count = user_result.scalar()
                
                if user_count < 3:  # Should have at least admin, manager, technician
                    print(f"❌ Insufficient users: {user_count}")
                    return False
                
                # Check gates
                gate_result = conn.execute(text("SELECT COUNT(*) FROM gates"))
                gate_count = gate_result.scalar()
                
                if gate_count < 1:
                    print("❌ No gates found")
                    return False
                
                # Check templates
                template_result = conn.execute(text("SELECT COUNT(*) FROM checklist_templates"))
                template_count = template_result.scalar()
                
                if template_count < 1:
                    print("❌ No checklist templates found")
                    return False
                
                # Check data relationships
                gate_building_result = conn.execute(text("""
                    SELECT COUNT(*) FROM gates g 
                    JOIN buildings b ON g.building_id = b.id 
                    JOIN sites s ON b.site_id = s.id
                """))
                relationship_count = gate_building_result.scalar()
                
                if relationship_count != gate_count:
                    print("❌ Gate-building relationships broken")
                    return False
                
                print(f"✅ Data validation successful:")
                print(f"  - Organizations: {org_count}")
                print(f"  - Users: {user_count}")
                print(f"  - Gates: {gate_count}")
                print(f"  - Templates: {template_count}")
                print(f"  - Relationships: OK")
                
                self.test_results["validation"] = True
                return True
                
        except Exception as e:
            print(f"❌ Data validation failed: {e}")
            return False
    
    def test_app_startup(self) -> bool:
        """Test that the application can start with the database."""
        print("\n🚀 Testing application startup...")
        
        try:
            # Try to import and initialize the main app
            from app.main import app
            from app.database import engine
            from sqlalchemy import text
            
            # Test database connection
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                if result.scalar() != 1:
                    print("❌ Database connection test failed")
                    return False
            
            # Test model imports
            from app.models.auth import User
            from app.models.organization import Organization, Gate
            from app.models.inspections import ChecklistTemplate
            
            print("✅ Application startup test successful")
            self.test_results["app_startup"] = True
            return True
            
        except Exception as e:
            print(f"❌ Application startup test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_full_test(self):
        """Run complete database lifecycle test."""
        print("🧪 Starting Database Lifecycle Test")
        print("=" * 50)
        
        try:
            # Setup
            self.setup_test_database()
            
            # Run tests in sequence
            tests = [
                ("Migration", self.test_migration),
                ("Seeding", self.test_seed),
                ("Data Validation", self.test_data_validation),
                ("App Startup", self.test_app_startup)
            ]
            
            all_passed = True
            for test_name, test_func in tests:
                if not test_func():
                    all_passed = False
                    break
            
            # Results summary
            print(f"\n📊 Test Results Summary")
            print("=" * 30)
            
            for test_name, result in self.test_results.items():
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{test_name.title():15} {status}")
            
            if all_passed:
                print("\n🎉 All tests passed! Database lifecycle is working correctly.")
                print("\nNext steps:")
                print("1. Start the application: python backend/complete_openapi.py")
                print("2. Access the API docs: http://localhost:8004/docs")
                print("3. Login with sample credentials from seed script")
                return True
            else:
                print("\n❌ Some tests failed. Check the output above for details.")
                return False
                
        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.cleanup_test_database()


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Test complete database lifecycle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script tests the complete database lifecycle:
1. Creates a fresh test database
2. Applies all migrations
3. Seeds with sample data
4. Validates data integrity
5. Tests application startup

The test uses a temporary database and cleans up automatically.
        """
    )
    
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Clean up test database after completion (default: keep for inspection)"
    )
    
    args = parser.parse_args()
    
    tester = DatabaseLifecycleTest(cleanup=args.cleanup)
    
    try:
        success = tester.run_full_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
        sys.exit(1)


if __name__ == "__main__":
    main()