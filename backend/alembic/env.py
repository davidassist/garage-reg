import os
import sys
import warnings
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool, inspect
from sqlalchemy.engine import Connection
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# Add the app directory to Python path
app_path = Path(__file__).parents[1]
sys.path.insert(0, str(app_path))

from app.models import Base
# Import all models so they are registered with SQLAlchemy
from app.models.auth import User, Role, Permission, APIKey
from app.models.organization import Organization, Client, Site, Building, Gate
from app.models.maintenance_advanced import AdvancedMaintenancePlan, ScheduledMaintenanceJob, MaintenanceCalendar, MaintenanceNotification
from app.models.inspections import ChecklistTemplate, ChecklistItem, Inspection, InspectionItem


# Safety configurations
PRODUCTION_SAFEGUARDS = True  # Set to False only for testing
BACKUP_BEFORE_MIGRATE = True
REQUIRE_CONFIRMATION = True


def backup_database(connection: Connection) -> bool:
    """Create database backup before migration in production."""
    if not BACKUP_BEFORE_MIGRATE:
        return True
        
    try:
        import shutil
        from datetime import datetime
        
        # Get database URL
        db_url = str(connection.engine.url)
        if 'sqlite' in db_url:
            db_path = db_url.replace('sqlite:///', '')
            if os.path.exists(db_path):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{db_path}.backup_{timestamp}"
                shutil.copy2(db_path, backup_path)
                print(f"Database backed up to: {backup_path}")
                return True
        else:
            print("⚠️  Database backup not implemented for non-SQLite databases")
            
    except Exception as e:
        print(f"Failed to create backup: {e}")
        return False
    
    return True


def check_migration_safety(connection: Connection) -> bool:
    """Perform safety checks before migration."""
    if not PRODUCTION_SAFEGUARDS:
        return True
        
    try:
        # Check if database has data
        inspector = inspect(connection.engine)
        tables = inspector.get_table_names()
        
        if tables:
            # Count records in key tables
            critical_tables = ['users', 'organizations', 'gates', 'tickets']
            data_exists = False
            
            for table in critical_tables:
                if table in tables:
                    try:
                        result = connection.execute(f"SELECT COUNT(*) FROM {table}")
                        count = result.scalar()
                        if count > 0:
                            print(f"📊 Found {count} records in {table}")
                            data_exists = True
                    except Exception:
                        pass  # Table might not exist yet
            
            if data_exists and REQUIRE_CONFIRMATION:
                print("\n⚠️  PRODUCTION DATA DETECTED!")
                print("This migration will modify a database with existing data.")
                confirm = input("Type 'yes' to continue: ").strip().lower()
                if confirm != 'yes':
                    print("Migration cancelled by user")
                    return False
        
        return True
        
    except Exception as e:
        print(f"Safety check failed: {e}")
        return False


def compare_metadata_with_db(connection: Connection) -> dict:
    """Compare current metadata with database schema."""
    try:
        from alembic.migration import MigrationContext
        from alembic.operations import ops
        from alembic.autogenerate import compare_metadata
        
        migration_ctx = MigrationContext.configure(connection)
        diff = compare_metadata(migration_ctx, Base.metadata)
        
        changes = {
            'new_tables': [],
            'removed_tables': [], 
            'modified_tables': [],
            'new_columns': [],
            'removed_columns': [],
            'modified_columns': []
        }
        
        for change in diff:
            if isinstance(change, ops.CreateTableOp):
                changes['new_tables'].append(change.table_name)
            elif isinstance(change, ops.DropTableOp):
                changes['removed_tables'].append(change.table_name)
            elif isinstance(change, ops.AddColumnOp):
                changes['new_columns'].append(f"{change.table_name}.{change.column.name}")
            elif isinstance(change, ops.DropColumnOp):
                changes['removed_columns'].append(f"{change.table_name}.{change.column_name}")
            elif isinstance(change, ops.AlterColumnOp):
                changes['modified_columns'].append(f"{change.table_name}.{change.column_name}")
                
        return changes
        
    except Exception as e:
        print(f"⚠️  Could not compare schemas: {e}")
        return {}

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    
    # Safety check for offline mode
    if PRODUCTION_SAFEGUARDS:
        print("🔒 Running in PRODUCTION SAFEGUARDS mode")
        print("📝 Generating SQL script only (offline mode)")
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode with safety checks.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Override database URL from environment or config
    try:
        from app.core.config import settings
        configuration = config.get_section(config.config_ini_section, {})
        configuration['sqlalchemy.url'] = settings.DATABASE_URL
    except ImportError:
        configuration = config.get_section(config.config_ini_section, {})
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Perform safety checks
        print("Performing pre-migration safety checks...")
        
        if not check_migration_safety(connection):
            print("Safety checks failed. Migration aborted.")
            return
        
        # Create backup if needed
        if not backup_database(connection):
            print("Backup failed. Migration aborted.")
            return
        
        # Show schema comparison
        changes = compare_metadata_with_db(connection)
        if changes and any(changes.values()):
            print("\n📋 Detected schema changes:")
            for change_type, items in changes.items():
                if items:
                    print(f"  {change_type}: {items}")
        
        print("Starting migration...")
        
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            # Include object filters if needed
            include_object=lambda obj, name, type_, reflected, compare_to: True,
        )

        with context.begin_transaction():
            context.run_migrations()
            
        print("Migration completed successfully!")


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
