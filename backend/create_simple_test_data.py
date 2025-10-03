#!/usr/bin/env python3
"""Create simple test data for maintenance system."""

import sqlite3
from datetime import datetime
import hashlib

def create_test_data():
    """Create minimal test data."""
    print("🔧 Creating minimal test data...")
    
    conn = sqlite3.connect('garagereg.db')
    cursor = conn.cursor()
    
    try:
        now = datetime.now()
        
        # Create organization
        cursor.execute("""
            INSERT INTO organizations (name, display_name, is_active, is_deleted, created_at, updated_at)
            VALUES ('Test Organization', 'Test Org', 1, 0, ?, ?)
        """, (now.isoformat(), now.isoformat()))
        org_id = cursor.lastrowid
        print(f"✅ Created organization (ID: {org_id})")
        
        # Create user
        password_hash = hashlib.sha256("test123".encode()).hexdigest()
        cursor.execute("""
            INSERT INTO users (org_id, organization_id, username, email, first_name, last_name,
                              password_hash, email_verified, is_active, is_superuser, is_verified, 
                              is_deleted, login_count, failed_login_attempts, timezone, language, theme,
                              created_at, updated_at)
            VALUES (?, ?, 'testuser', 'test@example.com', 'Test', 'User', ?, 1, 1, 0, 1, 0, 0, 0, 
                   'UTC', 'en', 'light', ?, ?)
        """, (org_id, org_id, password_hash, now.isoformat(), now.isoformat()))
        user_id = cursor.lastrowid
        print(f"✅ Created user (ID: {user_id})")
        
        # Create client (needed for sites)
        cursor.execute("""
            INSERT INTO clients (org_id, organization_id, name, display_name, type, is_active, is_deleted, created_at, updated_at)
            VALUES (?, ?, 'Test Client', 'Test Client Co.', 'corporate', 1, 0, ?, ?)
        """, (org_id, org_id, now.isoformat(), now.isoformat()))
        client_id = cursor.lastrowid
        print(f"✅ Created client (ID: {client_id})")
        
        # Create site
        cursor.execute("""
            INSERT INTO sites (org_id, client_id, name, display_name, is_active, is_deleted, created_at, updated_at)
            VALUES (?, ?, 'Test Site', 'Test Site Location', 1, 0, ?, ?)
        """, (org_id, client_id, now.isoformat(), now.isoformat()))
        site_id = cursor.lastrowid  
        print(f"✅ Created site (ID: {site_id})")
        
        # Create building (needed for gates)
        cursor.execute("""
            INSERT INTO buildings (org_id, site_id, name, display_name, is_active, is_deleted, created_at, updated_at)
            VALUES (?, ?, 'Test Building', 'Test Building A', 1, 0, ?, ?)
        """, (org_id, site_id, now.isoformat(), now.isoformat()))
        building_id = cursor.lastrowid
        print(f"✅ Created building (ID: {building_id})")
        
        # Create gate
        cursor.execute("""
            INSERT INTO gates (org_id, building_id, name, display_name, gate_type, status,
                              is_active, is_deleted, current_cycle_count, created_at, updated_at,
                              token_version)
            VALUES (?, ?, 'Test Gate', 'Main Entrance Gate', 'automatic', 'operational',
                   1, 0, 0, ?, ?, 1)
        """, (org_id, building_id, now.isoformat(), now.isoformat()))
        gate_id = cursor.lastrowid
        print(f"✅ Created gate (ID: {gate_id})")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()


def main():
    print("🚀 Creating Test Data")
    print("=" * 30)
    
    if create_test_data():
        print("\n✅ Test data created successfully!")
        print("Now run: python test_simple_maintenance.py")
    else:
        print("\n❌ Failed to create test data")


if __name__ == "__main__":
    main()