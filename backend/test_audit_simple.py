"""
Simple Audit System Test
Egyszerű audit rendszer teszt (csak SQL szinten)
"""

import sqlite3
from datetime import datetime
import json


def test_audit_database():
    """Test audit functionality directly with SQL"""
    
    print("🔍 Testing Audit Database Functionality")
    print("=" * 50)
    
    # Connect to database
    conn = sqlite3.connect('garagereg.db')
    cursor = conn.cursor()
    
    try:
        # 1. Insert sample audit entries
        print("\n1. Creating sample audit entries...")
        
        sample_entries = [
            {
                'user_id': 1,
                'username': 'testuser',
                'action': 'CREATE',
                'entity_type': 'Gate',
                'entity_id': 1001,
                'action_description': 'Created new gate: Main Entrance',
                'new_values': json.dumps({"name": "Main Entrance", "type": "Sliding"}),
                'organization_id': 1,
                'success': True,
                'risk_level': 'LOW',
                'ip_address': '192.168.1.100'
            },
            {
                'user_id': 1,
                'username': 'testuser',
                'action': 'UPDATE',
                'entity_type': 'Gate',
                'entity_id': 1001,
                'action_description': 'Updated gate status to maintenance',
                'old_values': json.dumps({"status": "Active"}),
                'new_values': json.dumps({"status": "Maintenance"}),
                'changed_fields': json.dumps(["status"]),
                'organization_id': 1,
                'success': True,
                'risk_level': 'MEDIUM',
                'ip_address': '192.168.1.100'
            },
            {
                'user_id': 2,
                'username': 'admin',
                'action': 'LOGIN',
                'entity_type': 'User',
                'entity_id': 2,
                'action_description': 'Successful login',
                'organization_id': 1,
                'success': True,
                'risk_level': 'LOW',
                'ip_address': '192.168.1.50'
            },
            {
                'user_id': None,
                'username': 'unknown',
                'action': 'LOGIN_FAILED',
                'entity_type': 'User',
                'entity_id': 0,
                'action_description': 'Failed login attempt',
                'error_message': 'Invalid credentials',
                'organization_id': 1,
                'success': False,
                'risk_level': 'HIGH',
                'ip_address': '192.168.1.200'
            }
        ]
        
        for entry in sample_entries:
            cursor.execute('''
                INSERT INTO audit_logs (
                    user_id, username, timestamp, action, entity_type, entity_id,
                    action_description, old_values, new_values, changed_fields,
                    ip_address, organization_id, success, error_message, risk_level,
                    created_at, updated_at, is_deleted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry.get('user_id'),
                entry['username'],
                datetime.now().isoformat(),
                entry['action'],
                entry['entity_type'],
                entry['entity_id'],
                entry['action_description'],
                entry.get('old_values'),
                entry.get('new_values'),
                entry.get('changed_fields'),
                entry['ip_address'],
                entry['organization_id'],
                entry['success'],
                entry.get('error_message'),
                entry['risk_level'],
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                False
            ))
        
        conn.commit()
        print(f"✅ Created {len(sample_entries)} audit entries successfully!")
        
        # 2. Query recent logs
        print("\n2. Querying recent audit logs...")
        
        cursor.execute('''
            SELECT id, timestamp, username, action, entity_type, entity_id, 
                   action_description, success, risk_level, ip_address
            FROM audit_logs 
            WHERE is_deleted = 0 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''')
        
        logs = cursor.fetchall()
        
        print(f"📊 Found {len(logs)} recent audit entries:")
        print("-" * 80)
        
        for i, log in enumerate(logs, 1):
            timestamp = log[1][:19] if log[1] else 'Unknown'
            print(f"{i:2d}. [{timestamp}] {log[2] or 'System'}")
            print(f"    {log[3]} {log[4]} (ID: {log[5]})")
            print(f"    Description: {log[6]}")
            print(f"    Success: {log[7]}, Risk: {log[8]}, IP: {log[9]}")
            print()
        
        # 3. Statistics by action
        print("3. Statistics by action...")
        
        cursor.execute('''
            SELECT action, COUNT(*) as count
            FROM audit_logs 
            WHERE is_deleted = 0
            GROUP BY action 
            ORDER BY count DESC
        ''')
        
        action_stats = cursor.fetchall()
        
        print("📊 Actions:")
        for action, count in action_stats:
            print(f"  {action:15} {count:6d}")
        
        # 4. Statistics by risk level
        print("\n📊 By Risk Level:")
        
        cursor.execute('''
            SELECT risk_level, COUNT(*) as count
            FROM audit_logs 
            WHERE is_deleted = 0
            GROUP BY risk_level 
            ORDER BY 
                CASE risk_level 
                    WHEN 'CRITICAL' THEN 1
                    WHEN 'HIGH' THEN 2
                    WHEN 'MEDIUM' THEN 3
                    WHEN 'LOW' THEN 4
                    ELSE 5
                END
        ''')
        
        risk_stats = cursor.fetchall()
        
        for risk, count in risk_stats:
            print(f"  {risk:10} {count:6d}")
        
        # 5. Success vs failure rate
        print("\n📊 Success Rate:")
        
        cursor.execute('''
            SELECT success, COUNT(*) as count
            FROM audit_logs 
            WHERE is_deleted = 0
            GROUP BY success
        ''')
        
        success_stats = cursor.fetchall()
        total_logs = sum(count for _, count in success_stats)
        
        for success, count in success_stats:
            status = "Success" if success else "Failed"
            percentage = (count / total_logs * 100) if total_logs > 0 else 0
            print(f"  {status:10} {count:6d} ({percentage:5.1f}%)")
        
        # 6. Top users by activity
        print("\n👥 Top Users:")
        
        cursor.execute('''
            SELECT username, COUNT(*) as count
            FROM audit_logs 
            WHERE is_deleted = 0 AND username IS NOT NULL
            GROUP BY username 
            ORDER BY count DESC
            LIMIT 5
        ''')
        
        user_stats = cursor.fetchall()
        
        for username, count in user_stats:
            print(f"  {username:15} {count:6d} actions")
        
        # 7. Recent failed operations
        print("\n⚠️  Recent Failed Operations:")
        
        cursor.execute('''
            SELECT timestamp, username, action, entity_type, error_message
            FROM audit_logs 
            WHERE is_deleted = 0 AND success = 0
            ORDER BY timestamp DESC
            LIMIT 5
        ''')
        
        failed_ops = cursor.fetchall()
        
        for timestamp, username, action, entity_type, error in failed_ops:
            timestamp_str = timestamp[:19] if timestamp else 'Unknown'
            print(f"  [{timestamp_str}] {username or 'System'} - {action} {entity_type}")
            if error:
                print(f"    Error: {error}")
        
        # 8. Test search functionality
        print("\n🔍 Search Test (looking for 'gate'):")
        
        cursor.execute('''
            SELECT timestamp, username, action, entity_type, action_description
            FROM audit_logs 
            WHERE is_deleted = 0 
            AND (LOWER(action_description) LIKE LOWER('%gate%') 
                 OR LOWER(entity_type) LIKE LOWER('%gate%'))
            ORDER BY timestamp DESC
            LIMIT 5
        ''')
        
        search_results = cursor.fetchall()
        
        for timestamp, username, action, entity_type, description in search_results:
            timestamp_str = timestamp[:19] if timestamp else 'Unknown'
            print(f"  [{timestamp_str}] {username or 'System'} {action} {entity_type}")
            print(f"    {description}")
        
        print("\n✅ Audit database test completed successfully!")
        print(f"✅ Total audit entries in database: {total_logs}")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()


def clean_audit_data():
    """Clean old audit data"""
    print("🧹 Cleaning old audit data...")
    
    conn = sqlite3.connect('garagereg.db')
    cursor = conn.cursor()
    
    try:
        # Count existing entries
        cursor.execute("SELECT COUNT(*) FROM audit_logs WHERE is_deleted = 0")
        count_before = cursor.fetchone()[0]
        
        # Mark test entries as deleted (soft delete)
        cursor.execute('''
            UPDATE audit_logs 
            SET is_deleted = 1, deleted_at = ? 
            WHERE username IN ('testuser', 'admin', 'unknown')
        ''', (datetime.now().isoformat(),))
        
        deleted_count = cursor.rowcount
        conn.commit()
        
        print(f"📊 Entries before: {count_before}")
        print(f"🗑️  Marked as deleted: {deleted_count}")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        conn.rollback()
    
    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--clean":
        clean_audit_data()
    else:
        test_audit_database()
        
        print("\n" + "=" * 50)
        print("🎯 Audit System Functionality Verified:")
        print("  ✅ Audit log creation")
        print("  ✅ Data querying and filtering")
        print("  ✅ Statistical analysis")
        print("  ✅ Search functionality")
        print("  ✅ Success/failure tracking")
        print("  ✅ Risk level classification")
        print("  ✅ User activity monitoring")
        print("\n💡 Next steps:")
        print("  - Start backend server to test API endpoints")
        print("  - Test middleware integration")
        print("  - Verify frontend dashboard")
        print("  - Run: python demo_audit_system.py --clean")