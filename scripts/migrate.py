#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alembic Migration Management Script with Enhanced Safety Features

This script provides enhanced database migration management with:
- Pre-migration safety checks
- Automatic database backups
- Migration validation
- Rollback capabilities
- Production safeguards

Usage:
    python scripts/migrate.py --help
    python scripts/migrate.py upgrade head
    python scripts/migrate.py downgrade -1
    python scripts/migrate.py create "add_new_field"
    python scripts/migrate.py status
    python scripts/migrate.py backup
"""

import os
import sys
import argparse
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Add backend path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker


class MigrationManager:
    """Enhanced Alembic migration manager with safety features."""
    
    def __init__(self, db_url: str = None):
        self.backend_path = backend_path
        self.db_url = db_url or os.getenv("DATABASE_URL", "sqlite:///./garagereg.db")
        self.engine = create_engine(self.db_url, echo=False)
        
    def run_alembic_command(self, command: List[str], capture_output: bool = False) -> Optional[str]:
        """Run an alembic command with proper environment."""
        cmd = ["python", "-m", "alembic"] + command
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.backend_path,
                capture_output=capture_output,
                text=True,
                check=True
            )
            return result.stdout if capture_output else None
        except subprocess.CalledProcessError as e:
            print(f"❌ Alembic command failed: {' '.join(cmd)}")
            print(f"Error: {e.stderr}")
            sys.exit(1)
    
    def backup_database(self) -> Optional[str]:
        """Create a backup of the database."""
        if 'sqlite' not in self.db_url.lower():
            print("⚠️  Database backup only supported for SQLite databases")
            return None
        
        # Extract database path
        db_path = self.db_url.replace('sqlite:///', '')
        db_path = os.path.join(self.backend_path, db_path)
        
        if not os.path.exists(db_path):
            print(f"⚠️  Database file not found: {db_path}")
            return None
        
        # Create backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{db_path}.backup_{timestamp}"
        
        try:
            shutil.copy2(db_path, backup_path)
            print(f"✅ Database backed up to: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None
    
    def check_migration_status(self) -> dict:
        """Check current migration status."""
        try:
            # Get current revision
            current_output = self.run_alembic_command(["current"], capture_output=True)
            current_rev = current_output.strip().split('\n')[-1] if current_output.strip() else "None"
            
            # Get head revision
            heads_output = self.run_alembic_command(["heads"], capture_output=True)
            head_rev = heads_output.strip().split('\n')[-1] if heads_output.strip() else "None"
            
            # Check if database exists and has tables
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            return {
                "current_revision": current_rev,
                "head_revision": head_rev,
                "is_up_to_date": current_rev == head_rev,
                "has_tables": len(tables) > 0,
                "table_count": len(tables)
            }
        except Exception as e:
            print(f"❌ Failed to check migration status: {e}")
            return {}
    
    def show_migration_history(self):
        """Show migration history."""
        print("📜 Migration History:")
        try:
            self.run_alembic_command(["history", "--verbose"])
        except Exception as e:
            print(f"❌ Failed to show history: {e}")
    
    def validate_migration(self, target_revision: str = "head") -> bool:
        """Validate migration before applying."""
        print("🔍 Validating migration...")
        
        try:
            # Check what changes would be made
            if target_revision == "head":
                print("📋 Checking for pending migrations...")
                status = self.check_migration_status()
                
                if status.get("is_up_to_date"):
                    print("✅ Database is already up to date")
                    return True
                
                # Show what migrations would be applied
                self.run_alembic_command(["show", status.get("head_revision", "head")])
            
            return True
        except Exception as e:
            print(f"❌ Migration validation failed: {e}")
            return False
    
    def create_migration(self, message: str, autogenerate: bool = True):
        """Create a new migration."""
        print(f"📝 Creating migration: {message}")
        
        # Safety check - ensure we're not creating duplicate migrations
        status = self.check_migration_status()
        if not status.get("is_up_to_date"):
            print("⚠️  Warning: There are pending migrations. Apply them first.")
            confirm = input("Continue anyway? (y/N): ").lower().strip()
            if confirm != 'y':
                print("❌ Migration creation cancelled")
                return
        
        cmd = ["revision", "-m", message]
        if autogenerate:
            cmd.append("--autogenerate")
        
        self.run_alembic_command(cmd)
        print("✅ Migration created successfully")
    
    def upgrade_database(self, revision: str = "head", backup: bool = True):
        """Upgrade database to specified revision."""
        print(f"Upgrading database to: {revision}")
        
        # Validate migration
        if not self.validate_migration(revision):
            return
        
        # Create backup
        if backup:
            backup_path = self.backup_database()
            if backup_path is None and 'sqlite' in self.db_url.lower():
                confirm = input("⚠️  Backup failed. Continue anyway? (y/N): ").lower().strip()
                if confirm != 'y':
                    print("❌ Migration cancelled")
                    return
        
        # Apply migration
        try:
            self.run_alembic_command(["upgrade", revision])
            print("✅ Database upgrade completed successfully")
            
            # Show new status
            status = self.check_migration_status()
            print(f"📊 Current revision: {status.get('current_revision', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            if backup and 'sqlite' in self.db_url.lower():
                print("💡 You can restore from backup if needed")
    
    def downgrade_database(self, revision: str, backup: bool = True):
        """Downgrade database to specified revision."""
        print(f"⬇️  Downgrading database to: {revision}")
        
        # Get current status
        status = self.check_migration_status()
        current = status.get("current_revision", "None")
        
        if current == "None":
            print("❌ No migrations to downgrade from")
            return
        
        # Warning for downgrade
        print("⚠️  WARNING: Database downgrade may cause data loss!")
        confirm = input("Are you sure you want to proceed? (yes/no): ").lower().strip()
        if confirm != 'yes':
            print("❌ Downgrade cancelled")
            return
        
        # Create backup
        if backup:
            backup_path = self.backup_database()
            if backup_path is None and 'sqlite' in self.db_url.lower():
                confirm = input("⚠️  Backup failed. Continue anyway? (y/N): ").lower().strip()
                if confirm != 'y':
                    print("❌ Downgrade cancelled")
                    return
        
        # Apply downgrade
        try:
            self.run_alembic_command(["downgrade", revision])
            print("✅ Database downgrade completed")
            
            # Show new status
            status = self.check_migration_status()
            print(f"📊 Current revision: {status.get('current_revision', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Downgrade failed: {e}")
    
    def show_status(self):
        """Show comprehensive migration status."""
        print("📊 Database Migration Status")
        print("=" * 40)
        
        status = self.check_migration_status()
        
        print(f"Database URL: {self.db_url}")
        print(f"Current Revision: {status.get('current_revision', 'Unknown')}")
        print(f"Head Revision: {status.get('head_revision', 'Unknown')}")
        print(f"Up to Date: {'Yes' if status.get('is_up_to_date') else 'No'}")
        print(f"Has Tables: {'Yes' if status.get('has_tables') else 'No'}")
        print(f"Table Count: {status.get('table_count', 0)}")
        
        if not status.get('is_up_to_date'):
            print("\n⚠️  Pending migrations detected!")
            print("Run 'python scripts/migrate.py upgrade' to apply them.")
    
    def init_database(self):
        """Initialize database with first migration."""
        print("🏗️  Initializing database...")
        
        status = self.check_migration_status()
        
        if status.get('has_tables'):
            print("⚠️  Database already contains tables.")
            confirm = input("Mark current state as baseline? (y/N): ").lower().strip()
            if confirm == 'y':
                # Stamp with current head
                self.run_alembic_command(["stamp", "head"])
                print("✅ Database marked as up to date")
            return
        
        # Run first migration
        self.upgrade_database("head", backup=False)


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Enhanced Alembic migration management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/migrate.py status              # Show current status
  python scripts/migrate.py upgrade             # Upgrade to latest
  python scripts/migrate.py upgrade +1          # Upgrade one revision
  python scripts/migrate.py downgrade -1        # Downgrade one revision
  python scripts/migrate.py create "add field"  # Create new migration
  python scripts/migrate.py backup              # Backup database only
  python scripts/migrate.py init                # Initialize fresh database
  python scripts/migrate.py history             # Show migration history
        """
    )
    
    parser.add_argument("command", help="Migration command")
    parser.add_argument("revision", nargs="?", help="Target revision")
    parser.add_argument("--no-backup", action="store_true", help="Skip backup creation")
    parser.add_argument("--db-url", help="Database URL override")
    
    args = parser.parse_args()
    
    manager = MigrationManager(args.db_url)
    
    try:
        if args.command == "status":
            manager.show_status()
            
        elif args.command == "upgrade":
            revision = args.revision or "head"
            manager.upgrade_database(revision, backup=not args.no_backup)
            
        elif args.command == "downgrade":
            if not args.revision:
                print("❌ Downgrade requires a target revision")
                sys.exit(1)
            manager.downgrade_database(args.revision, backup=not args.no_backup)
            
        elif args.command == "create":
            if not args.revision:
                print("❌ Create requires a migration message")
                sys.exit(1)
            manager.create_migration(args.revision)
            
        elif args.command == "backup":
            manager.backup_database()
            
        elif args.command == "init":
            manager.init_database()
            
        elif args.command == "history":
            manager.show_migration_history()
            
        else:
            print(f"❌ Unknown command: {args.command}")
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
        except Exception as e:
            print(f"ERROR: Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
if __name__ == "__main__":
    main()