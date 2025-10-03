#!/usr/bin/env python3
"""
Simple Alembic Migration Management Script

Usage:
    python scripts/migrate_simple.py upgrade
    python scripts/migrate_simple.py downgrade -1  
    python scripts/migrate_simple.py status
"""

import os
import sys
import subprocess
from pathlib import Path

# Add backend path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))


def run_alembic_command(command_args):
    """Run an alembic command."""
    cmd = ["python", "-m", "alembic"] + command_args
    
    try:
        result = subprocess.run(
            cmd,
            cwd=backend_path,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Alembic command failed: {e}")
        return False


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/migrate_simple.py <command> [args]")
        print("Commands: upgrade, downgrade, status, current, history")
        sys.exit(1)
    
    command = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    if command == "upgrade":
        target = args[0] if args else "head"
        print(f"Upgrading database to: {target}")
        success = run_alembic_command(["upgrade", target])
        
    elif command == "downgrade":
        if not args:
            print("Downgrade requires a target revision")
            sys.exit(1)
        target = args[0]
        print(f"Downgrading database to: {target}")
        success = run_alembic_command(["downgrade", target])
        
    elif command == "status":
        print("Migration status:")
        success = run_alembic_command(["current"]) and run_alembic_command(["heads"])
        
    elif command == "current":
        success = run_alembic_command(["current"])
        
    elif command == "history":
        success = run_alembic_command(["history"])
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
    
    if success:
        print("Command completed successfully")
    else:
        print("Command failed")
        sys.exit(1)


if __name__ == "__main__":
    main()