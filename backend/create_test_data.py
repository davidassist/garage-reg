#!/usr/bin/env python3
"""Create basic test data for garage registration system."""

import sqlite3
from datetime import datetime
import hashlib

def create_basic_data():
    """Create organizations, users, and gates for testing."""
    print("🏗️ Creating basic test data...")
    
    conn = sqlite3.connect('garagereg.db')
    cursor = conn.cursor()
    
    try:
        now = datetime.now()
        
        # Create test organization
        org_data = {
            'name': 'Test Garage Company',
            'display_name': 'Test Garage Company Ltd.',
            'description': 'Test garage management company',
            'email': 'admin@testgarage.com',
            'phone': '+36-1-234-5678',
            'address_line_1': '1234 Budapest, Test utca 1.',
            'city': 'Budapest',
            'country': 'Hungary',
            'is_active': True,
            'is_deleted': False,
            'created_at': now.isoformat(),
            'updated_at': now.isoformat()
        }
        
        cursor.execute("""
            INSERT INTO organizations 
            (name, display_name, description, email, phone, address_line_1, city, country, 
             is_active, is_deleted, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            org_data['name'], org_data['display_name'], org_data['description'],
            org_data['email'], org_data['phone'], org_data['address_line_1'],
            org_data['city'], org_data['country'], org_data['is_active'], 
            org_data['is_deleted'], org_data['created_at'], org_data['updated_at']
        ))
        
        org_id = cursor.lastrowid
        print(f"✅ Created organization: {org_data['name']} (ID: {org_id})")
        
        # Create test user
        password_hash = hashlib.sha256("testpass123".encode()).hexdigest()  # Simple hash for testing
        
        user_data = {
            'org_id': org_id,
            'organization_id': org_id,
            'username': 'testuser',
            'email': 'test@testgarage.com',
            'first_name': 'Test',
            'last_name': 'User',
            'display_name': 'Test User',
            'password_hash': password_hash,
            'email_verified': True,
            'phone': '+36-30-123-4567',
            'job_title': 'Maintenance Manager',
            'department': 'Operations',
            'is_active': True,
            'is_superuser': False,
            'is_verified': True,
            'is_deleted': False,
            'login_count': 0,
            'failed_login_attempts': 0,
            'timezone': 'Europe/Budapest',
            'language': 'en',
            'theme': 'light',
            'created_at': now.isoformat(),
            'updated_at': now.isoformat()
        }
        
        cursor.execute("""
            INSERT INTO users
            (org_id, organization_id, username, email, first_name, last_name, display_name,
             password_hash, email_verified, phone, job_title, department, 
             is_active, is_superuser, is_verified, is_deleted, login_count, failed_login_attempts,
             timezone, language, theme, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_data['org_id'], user_data['organization_id'], user_data['username'], user_data['email'],
            user_data['first_name'], user_data['last_name'], user_data['display_name'],
            user_data['password_hash'], user_data['email_verified'], user_data['phone'],
            user_data['job_title'], user_data['department'], user_data['is_active'],
            user_data['is_superuser'], user_data['is_verified'], user_data['is_deleted'],
            user_data['login_count'], user_data['failed_login_attempts'], user_data['timezone'],
            user_data['language'], user_data['theme'], user_data['created_at'], user_data['updated_at']
        ))
        
        user_id = cursor.lastrowid
        print(f"✅ Created user: {user_data['username']} (ID: {user_id})")
        
        # Create test sites and gates
        sites_data = [
            {
                'organization_id': org_id,
                'name': 'Main Residential Complex',
                'code': 'SITE001',
                'address': '1234 Budapest, Lakópark utca 10.',
                'description': 'Main residential site with multiple gates',
                'is_active': True,
                'created_at': now.isoformat(),
                'updated_at': now.isoformat()
            },
            {
                'organization_id': org_id,
                'name': 'Office Building',
                'code': 'SITE002', 
                'address': '1234 Budapest, Irodaház tér 5.',
                'description': 'Commercial office building',
                'is_active': True,
                'created_at': now.isoformat(),
                'updated_at': now.isoformat()
            }
        ]
        
        site_ids = []
        for site_data in sites_data:
            cursor.execute("""
                INSERT INTO sites
                (organization_id, name, code, address, description, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                site_data['organization_id'], site_data['name'], site_data['code'],
                site_data['address'], site_data['description'], site_data['is_active'],
                site_data['created_at'], site_data['updated_at']
            ))
            site_id = cursor.lastrowid
            site_ids.append(site_id)
            print(f"✅ Created site: {site_data['name']} (ID: {site_id})")
        
        # Create test gates
        gates_data = [
            {
                'organization_id': org_id,
                'site_id': site_ids[0],
                'name': 'Main Entrance Gate',
                'code': 'GATE001',
                'gate_type': 'automatic',
                'manufacturer': 'CAME',
                'model': 'BX-78',
                'installation_date': '2023-01-15',
                'location': 'Main entrance, left side',
                'description': 'Main automatic sliding gate',
                'is_active': True,
                'created_at': now.isoformat(),
                'updated_at': now.isoformat()
            },
            {
                'organization_id': org_id,
                'site_id': site_ids[0],
                'name': 'Pedestrian Gate',
                'code': 'GATE002',
                'gate_type': 'electric',
                'manufacturer': 'BFT',
                'model': 'DEIMOS BT A400',
                'installation_date': '2023-02-10',
                'location': 'Main entrance, right side',
                'description': 'Electric pedestrian gate with card reader',
                'is_active': True,
                'created_at': now.isoformat(),
                'updated_at': now.isoformat()
            },
            {
                'organization_id': org_id,
                'site_id': site_ids[1],
                'name': 'Office Parking Gate',
                'code': 'GATE003',
                'gate_type': 'automatic',
                'manufacturer': 'NICE',
                'model': 'ROBUS 600',
                'installation_date': '2022-11-20',
                'location': 'Underground parking entrance',
                'description': 'Automatic barrier gate for parking access',
                'is_active': True,
                'created_at': now.isoformat(),
                'updated_at': now.isoformat()
            }
        ]
        
        gate_ids = []
        for gate_data in gates_data:
            cursor.execute("""
                INSERT INTO gates
                (organization_id, site_id, name, code, gate_type, manufacturer, model,
                 installation_date, location, description, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                gate_data['organization_id'], gate_data['site_id'], gate_data['name'],
                gate_data['code'], gate_data['gate_type'], gate_data['manufacturer'],
                gate_data['model'], gate_data['installation_date'], gate_data['location'],
                gate_data['description'], gate_data['is_active'], gate_data['created_at'],
                gate_data['updated_at']
            ))
            gate_id = cursor.lastrowid
            gate_ids.append(gate_id)
            print(f"✅ Created gate: {gate_data['name']} (ID: {gate_id})")
        
        conn.commit()
        
        print(f"\n🎉 Basic test data created successfully!")
        print(f"   Organization: {org_data['name']}")
        print(f"   User: {user_data['username']} / testpass123")
        print(f"   Sites: {len(sites_data)}")
        print(f"   Gates: {len(gates_data)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating basic data: {str(e)}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


def main():
    """Main function."""
    print("🚀 Garage Registration System - Basic Data Setup")
    print("=" * 50)
    
    success = create_basic_data()
    
    if success:
        print("\n📋 Next step: Run the maintenance planning test")
        print("   python test_simple_maintenance.py")
    else:
        print("\n❌ Setup failed. Please check the database.")


if __name__ == "__main__":
    main()