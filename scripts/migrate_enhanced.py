#!/usr/bin/env python3
"""
Enhanced Alembic Migration Management with Safety Measures

This script provides comprehensive database migration management with:
- Pre-migration safety checks
- Automatic database backups
- Rollback capabilities
- Migration validation
- Baseline creation for existing databases

Usage:
    python scripts/migrate_enhanced.py --help
    python scripts/migrate_enhanced.py --baseline
    python scripts/migrate_enhanced.py --migrate
    python scripts/migrate_enhanced.py --reset --confirm
"""

import os
import sys
import shutil
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add backend to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory


class MigrationManager:
    """Enhanced Alembic migration manager with safety measures."""
    
    def __init__(self, database_url: str = None):
        self.backend_path = Path(__file__).parent.parent / "backend"
        self.alembic_ini = self.backend_path / "alembic.ini"
        self.database_url = database_url or os.getenv("DATABASE_URL", "sqlite:///./garagereg.db")
        
        # Create Alembic config
        self.config = Config(str(self.alembic_ini))
        if database_url:
            self.config.set_main_option("sqlalchemy.url", database_url)
        
        # Database setup
        self.engine = create_engine(self.database_url, echo=False)
        
    def backup_database(self, suffix: str = None) -> Optional[Path]:
        """Create database backup before migrations."""
        try:
            if not suffix:
                suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if self.database_url.startswith("sqlite"):
                # Extract SQLite file path
                db_file = self.database_url.split("///")[-1]
                db_path = Path(db_file)
                
                if not db_path.exists():
                    print("⚠️  Database file does not exist yet")
                    return None
                
                backup_path = db_path.with_suffix(f".backup_{suffix}.db")
                shutil.copy2(db_path, backup_path)
                print(f"💾 Database backed up to: {backup_path}")
                return backup_path
            else:
                print("⚠️  Backup not implemented for non-SQLite databases")
                return None
                
        except Exception as e:
            print(f"❌ Failed to backup database: {e}")
            return None
    
    def check_database_exists(self) -> bool:
        """Check if database exists and is accessible."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except OperationalError:
            return False
    
    def get_current_revision(self) -> Optional[str]:
        """Get current database revision."""
        try:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            if 'alembic_version' not in tables:
                return None
                
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version_num FROM alembic_version")).fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"⚠️  Could not determine current revision: {e}")
            return None
    
    def get_available_revisions(self) -> List[str]:
        """Get list of available migration revisions."""
        try:
            script_dir = ScriptDirectory.from_config(self.config)
            revisions = []
            for revision in script_dir.walk_revisions():
                revisions.append(revision.revision)
            return list(reversed(revisions))
        except Exception as e:
            print(f"❌ Could not get available revisions: {e}")
            return []
    
    def validate_migration_safety(self) -> Dict[str, Any]:
        """Perform safety checks before migration."""
        checks = {
            "database_exists": self.check_database_exists(),
            "current_revision": self.get_current_revision(),
            "available_revisions": self.get_available_revisions(),
            "backup_created": False,
            "safe_to_migrate": True,
            "warnings": [],
            "errors": []
        }
        
        # Check if backup is needed
        if checks["database_exists"]:
            backup_path = self.backup_database()
            checks["backup_created"] = backup_path is not None
            if not backup_path:
                checks["warnings"].append("Could not create database backup")
        
        # Check for pending migrations
        if checks["current_revision"] and checks["available_revisions"]:
            current_index = -1
            try:
                current_index = checks["available_revisions"].index(checks["current_revision"])
            except ValueError:
                checks["errors"].append(f"Current revision {checks['current_revision']} not found in available revisions")
                checks["safe_to_migrate"] = False
            
            if current_index == len(checks["available_revisions"]) - 1:
                checks["warnings"].append("Database is already at latest revision")
        
        return checks
    
    def create_baseline(self) -> bool:
        """Create baseline for existing database."""
        print("🏗️  Creating baseline for existing database...")
        
        try:
            # Check if database has tables but no alembic_version
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            if tables and 'alembic_version' not in tables:
                print(f"📊 Found {len(tables)} existing tables, creating baseline...")
                
                # Stamp with the latest revision
                revisions = self.get_available_revisions()
                if revisions:
                    latest_revision = revisions[-1]
                    command.stamp(self.config, latest_revision)
                    print(f"✅ Baseline created with revision: {latest_revision}")
                    return True
                else:
                    print("❌ No revisions available for baseline")
                    return False
            elif 'alembic_version' in tables:
                current = self.get_current_revision()
                print(f"ℹ️  Database already has alembic tracking (revision: {current})")
                return True
            else:
                print("ℹ️  Database is empty, no baseline needed")
                return True
                
        except Exception as e:
            print(f"❌ Failed to create baseline: {e}")
            return False
    
    def run_migrations(self, target_revision: str = "head", dry_run: bool = False) -> bool:
        """Run database migrations with safety checks."""
        print("🔄 Starting migration process...")
        
        # Perform safety checks
        safety_checks = self.validate_migration_safety()
        
        print("\\n🔍 Pre-migration safety checks:")
        print(f"   Database exists: {'✅' if safety_checks['database_exists'] else '❌'}")
        print(f"   Current revision: {safety_checks['current_revision'] or 'None'}")
        print(f"   Available revisions: {len(safety_checks['available_revisions'])}")
        print(f"   Backup created: {'✅' if safety_checks['backup_created'] else '⚠️'}")
        
        # Display warnings
        for warning in safety_checks["warnings"]:
            print(f"   ⚠️  {warning}")
        
        # Display errors
        for error in safety_checks["errors"]:
            print(f"   ❌ {error}")
        
        if not safety_checks["safe_to_migrate"]:
            print("\\n❌ Migration aborted due to safety concerns")
            return False
        
        if dry_run:
            print("\\n🧪 DRY RUN - Would execute migrations to:", target_revision)
            return True
        
        try:
            print(f"\\n⬆️  Upgrading database to: {target_revision}")
            command.upgrade(self.config, target_revision)
            print("✅ Migration completed successfully!")
            
            # Verify final state
            final_revision = self.get_current_revision()
            print(f"📊 Final revision: {final_revision}")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            print("\\n🔙 Consider rolling back using:")
            print(f"   alembic downgrade {safety_checks['current_revision']}")
            return False
    
    def rollback_migration(self, target_revision: str) -> bool:
        """Rollback to specific revision."""
        print(f"🔙 Rolling back to revision: {target_revision}")
        
        try:
            command.downgrade(self.config, target_revision)
            print("✅ Rollback completed successfully!")
            return True
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False
    
    def generate_migration(self, message: str, autogenerate: bool = True) -> bool:
        """Generate new migration."""
        print(f"📝 Generating migration: {message}")
        
        try:
            command.revision(self.config, message=message, autogenerate=autogenerate)
            print("✅ Migration generated successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to generate migration: {e}")
            return False
    
    def show_migration_history(self):
        """Display migration history."""
        print("📜 Migration History:")
        
        try:
            command.history(self.config, verbose=True)
        except Exception as e:
            print(f"❌ Could not display history: {e}")
    
    def reset_database(self, confirm: bool = False) -> bool:
        """Reset database (dangerous operation)."""
        if not confirm:
            print("❌ Database reset requires --confirm flag for safety")
            return False
        
        print("🚨 RESETTING DATABASE - ALL DATA WILL BE LOST!")
        
        try:
            # Drop all tables
            if self.check_database_exists():
                backup_path = self.backup_database("before_reset")
                if backup_path:
                    print(f"💾 Emergency backup created: {backup_path}")
            
            # Reset alembic
            command.downgrade(self.config, "base")
            print("✅ Database reset completed!")
            return True
            
        except Exception as e:
            print(f"❌ Reset failed: {e}")
            return False


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Enhanced Alembic Migration Management",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--database-url", 
        help="Database URL (default: from env or SQLite)"
    )
    
    # Actions (mutually exclusive)
    action_group = parser.add_mutually_exclusive_group(required=True)
    
    action_group.add_argument(
        "--baseline",
        action="store_true",
        help="Create baseline for existing database"
    )
    
    action_group.add_argument(
        "--migrate",
        action="store_true", 
        help="Run pending migrations"
    )
    
    action_group.add_argument(
        "--rollback",
        metavar="REVISION",
        help="Rollback to specific revision"
    )
    
    action_group.add_argument(
        "--generate",
        metavar="MESSAGE",
        help="Generate new migration"
    )
    
    action_group.add_argument(
        "--history",
        action="store_true",
        help="Show migration history"
    )
    
    action_group.add_argument(
        "--reset",
        action="store_true",
        help="Reset database (requires --confirm)"
    )
    
    # Options
    parser.add_argument(
        "--target",
        default="head",
        help="Target revision for migrations (default: head)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without executing"
    )
    
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Confirm dangerous operations"
    )
    
    parser.add_argument(
        "--no-autogenerate",
        action="store_true",
        help="Disable autogenerate for new migrations"
    )
    
    args = parser.parse_args()
    
    # Create migration manager
    manager = MigrationManager(args.database_url)
    
    print("🔧 Enhanced Alembic Migration Manager")
    print("=" * 40)
    
    # Execute requested action
    success = False
    
    if args.baseline:
        success = manager.create_baseline()
    elif args.migrate:
        success = manager.run_migrations(args.target, args.dry_run)
    elif args.rollback:
        success = manager.rollback_migration(args.rollback)
    elif args.generate:
        success = manager.generate_migration(args.generate, not args.no_autogenerate)
    elif args.history:
        manager.show_migration_history()
        success = True
    elif args.reset:
        success = manager.reset_database(args.confirm)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()