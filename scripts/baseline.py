#!/usr/bin/env python3
"""
Database Baseline Script

Creates a clean baseline for the database by:
1. Backing up existing database
2. Creating fresh migration
3. Establishing baseline state

Usage:
    python scripts/baseline.py [--reset-migrations]
"""

import os
import sys
import argparse
import shutil
import glob
from datetime import datetime
from pathlib import Path

# Add backend path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker


class DatabaseBaseline:
    """Create database baseline with clean migration history."""
    
    def __init__(self, db_url: str = None):
        self.backend_path = backend_path
        self.db_url = db_url or os.getenv("DATABASE_URL", "sqlite:///./garagereg.db")
        self.engine = create_engine(self.db_url, echo=False)
        self.versions_dir = self.backend_path / "alembic" / "versions"
    
    def backup_database(self) -> str:
        """Create database backup."""
        if 'sqlite' not in self.db_url.lower():
            print("⚠️  Database backup only supported for SQLite")
            return None
        
        db_path = self.db_url.replace('sqlite:///', '')
        db_path = os.path.join(self.backend_path, db_path)
        
        if not os.path.exists(db_path):
            print(f"⚠️  Database file not found: {db_path}")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{db_path}.baseline_backup_{timestamp}"
        
        try:
            shutil.copy2(db_path, backup_path)
            print(f"✅ Database backed up to: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None
    
    def backup_migrations(self) -> str:
        """Backup existing migration files."""
        if not self.versions_dir.exists():
            print("⚠️  No migrations directory found")
            return None
        
        # Find existing migration files
        migration_files = glob.glob(str(self.versions_dir / "*.py"))
        if not migration_files:
            print("ℹ️  No existing migration files found")
            return None
        
        # Create backup directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.versions_dir.parent / f"migrations_backup_{timestamp}"
        backup_dir.mkdir(exist_ok=True)
        
        # Copy migration files
        for migration_file in migration_files:
            if "__pycache__" not in migration_file:
                shutil.copy2(migration_file, backup_dir)
        
        print(f"✅ Migration files backed up to: {backup_dir}")
        return str(backup_dir)
    
    def clear_migrations(self):
        """Remove existing migration files."""
        if not self.versions_dir.exists():
            return
        
        migration_files = glob.glob(str(self.versions_dir / "*.py"))
        for migration_file in migration_files:
            if "__pycache__" not in migration_file and os.path.basename(migration_file) != "__init__.py":
                os.remove(migration_file)
                print(f"🗑️  Removed: {os.path.basename(migration_file)}")
        
        # Clear pycache
        pycache_dir = self.versions_dir / "__pycache__"
        if pycache_dir.exists():
            shutil.rmtree(pycache_dir)
    
    def check_database_state(self) -> dict:
        """Check current database state."""
        try:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            # Check if alembic version table exists
            has_alembic_version = "alembic_version" in tables
            current_revision = None
            
            if has_alembic_version:
                with self.engine.connect() as conn:
                    try:
                        result = conn.execute(text("SELECT version_num FROM alembic_version"))
                        current_revision = result.scalar()
                    except Exception:
                        pass
            
            # Count records in key tables
            record_counts = {}
            key_tables = ["users", "organizations", "gates", "roles", "permissions"]
            
            for table in key_tables:
                if table in tables:
                    try:
                        with self.engine.connect() as conn:
                            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                            record_counts[table] = result.scalar()
                    except Exception:
                        record_counts[table] = 0
            
            return {
                "has_tables": len(tables) > 0,
                "table_count": len(tables),
                "tables": tables,
                "has_alembic_version": has_alembic_version,
                "current_revision": current_revision,
                "record_counts": record_counts,
                "has_data": any(count > 0 for count in record_counts.values())
            }
            
        except Exception as e:
            print(f"❌ Failed to check database state: {e}")
            return {"error": str(e)}
    
    def create_baseline_migration(self):
        """Create initial baseline migration."""
        print("📝 Creating baseline migration...")
        
        import subprocess
        
        cmd = [
            sys.executable, "-m", "alembic", "revision",
            "--autogenerate",
            "-m", "baseline_database_schema"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.backend_path,
                capture_output=True,
                text=True,
                check=True
            )
            print("✅ Baseline migration created")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create baseline migration: {e.stderr}")
            return False
    
    def stamp_database(self):
        """Stamp database with current head revision."""
        print("🏷️  Stamping database with baseline...")
        
        import subprocess
        
        cmd = [sys.executable, "-m", "alembic", "stamp", "head"]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.backend_path,
                capture_output=True,
                text=True,
                check=True
            )
            print("✅ Database stamped with baseline")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to stamp database: {e.stderr}")
            return False
    
    def create_baseline(self, reset_migrations: bool = False):
        """Create complete database baseline."""
        print("🏗️  Creating Database Baseline")
        print("=" * 40)
        
        # Check current state
        state = self.check_database_state()
        if "error" in state:
            print(f"❌ Cannot create baseline: {state['error']}")
            return False
        
        print(f"📊 Current database state:")
        print(f"  - Tables: {state['table_count']}")
        print(f"  - Has data: {'Yes' if state['has_data'] else 'No'}")
        print(f"  - Alembic managed: {'Yes' if state['has_alembic_version'] else 'No'}")
        
        if state['has_data']:
            print("\n⚠️  WARNING: Database contains data!")
            print("Creating baseline will mark current state as migration baseline.")
            confirm = input("Continue? (yes/no): ").lower().strip()
            if confirm != 'yes':
                print("❌ Baseline creation cancelled")
                return False
        
        # Backup database
        db_backup = self.backup_database()
        
        # Backup and optionally clear migrations
        if reset_migrations:
            migration_backup = self.backup_migrations()
            self.clear_migrations()
        
        # Create baseline migration if needed
        if reset_migrations or not state['has_alembic_version']:
            if not self.create_baseline_migration():
                return False
        
        # Stamp database if it has tables but no alembic version
        if state['has_tables'] and not state['has_alembic_version']:
            if not self.stamp_database():
                return False
        
        print("\n✅ Baseline creation completed successfully!")
        print("\n📋 Next steps:")
        print("1. Test migrations: python scripts/migrate.py status")
        print("2. Create new migrations: python scripts/migrate.py create 'description'")
        print("3. Apply migrations: python scripts/migrate.py upgrade")
        
        if db_backup:
            print(f"\n💾 Database backup available: {db_backup}")
        
        return True


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Create database baseline with clean migration history",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script creates a clean baseline for database migrations by:

1. Backing up the current database and migrations
2. Optionally clearing existing migration files
3. Creating a new baseline migration from current schema
4. Stamping the database with the baseline

Use --reset-migrations to start with a completely clean migration history.
        """
    )
    
    parser.add_argument(
        "--reset-migrations",
        action="store_true",
        help="Clear existing migration files and create fresh baseline"
    )
    parser.add_argument("--db-url", help="Database URL override")
    
    args = parser.parse_args()
    
    baseline = DatabaseBaseline(args.db_url)
    
    try:
        success = baseline.create_baseline(reset_migrations=args.reset_migrations)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()