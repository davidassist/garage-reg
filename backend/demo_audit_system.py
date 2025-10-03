"""
Audit System Demo Script
Audit rendszer demonstrációs script
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import get_db
from app.services.audit_service import AuditService
from app.models.audit_logs import AuditAction, AuditResourceType
from datetime import datetime
import json


def demo_audit_system():
    """Demonstrate audit system functionality"""
    
    print("🔍 Audit System Demo")
    print("=" * 50)
    
    # Get database session
    db = next(get_db())
    audit_service = AuditService(db)
    
    try:
        # 1. Log some sample operations
        print("\n1. Creating sample audit entries...")
        
        # Sample gate creation
        audit_service.log_create(
            entity_type=AuditResourceType.GATE,
            entity_id=1001,
            resource_data={
                "name": "Main Entrance Gate",
                "type": "Sliding Gate",
                "location": "Building A - Main Entrance"
            },
            user_id=1,
            username="testuser",
            organization_id=1
        )
        
        # Sample gate update
        audit_service.log_update(
            entity_type=AuditResourceType.GATE,
            entity_id=1001,
            old_data={
                "name": "Main Entrance Gate",
                "status": "Active"
            },
            new_data={
                "name": "Main Entrance Gate",
                "status": "Under Maintenance"
            },
            user_id=1,
            username="testuser",
            organization_id=1
        )
        
        # Sample login success
        audit_service.log_login(
            user_id=1,
            username="testuser",
            success=True,
            organization_id=1
        )
        
        # Sample login failure
        audit_service.log_login(
            user_id=2,
            username="wronguser",
            success=False,
            organization_id=1,
            error_message="Invalid credentials"
        )
        
        # Sample maintenance operation
        audit_service.log_action(
            action=AuditAction.MAINTENANCE_SCHEDULED,
            entity_type=AuditResourceType.MAINTENANCE,
            entity_id=501,
            user_id=1,
            username="testuser",
            description="Scheduled monthly maintenance for gate 1001",
            new_values={
                "gate_id": 1001,
                "maintenance_type": "Preventive",
                "scheduled_date": "2024-11-01"
            },
            organization_id=1,
            risk_level="LOW"
        )
        
        print("✅ Sample audit entries created successfully!")
        
        # 2. Query audit logs
        print("\n2. Querying audit logs...")
        
        result = audit_service.get_audit_logs(
            organization_id=1,
            page=1,
            per_page=10
        )
        
        print(f"📊 Found {result['pagination']['total']} total audit entries")
        print(f"📄 Showing page {result['pagination']['page']} of {result['pagination']['total_pages']}")
        
        # Display recent logs
        print("\n📋 Recent Audit Entries:")
        for i, log in enumerate(result['logs'][:5], 1):
            print(f"  {i}. [{log['timestamp'][:19]}] {log['username']} {log['action']} {log['entity_type']} ID:{log['entity_id']}")
            if log['action_description']:
                print(f"      Description: {log['action_description']}")
            print(f"      Risk Level: {log['risk_level']}, Success: {log['success']}")
            print()
        
        # 3. Get statistics
        print("3. Getting audit statistics...")
        
        stats = audit_service.get_audit_statistics(organization_id=1)
        
        print(f"📈 Total Logs: {stats['total_logs']}")
        
        print("\n📊 By Action:")
        for item in stats['by_action']:
            print(f"  - {item['action']}: {item['count']}")
        
        print("\n📊 By Entity Type:")
        for item in stats['by_entity_type']:
            print(f"  - {item['entity_type']}: {item['count']}")
        
        print("\n📊 By Risk Level:")
        for item in stats['by_risk_level']:
            print(f"  - {item['risk_level']}: {item['count']}")
        
        print("\n👥 Top Users:")
        for item in stats['top_users']:
            print(f"  - {item['username']}: {item['count']} actions")
        
        # 4. Search functionality
        print("\n4. Testing search functionality...")
        
        search_result = audit_service.get_audit_logs(
            organization_id=1,
            search_term="gate",
            per_page=5
        )
        
        print(f"🔍 Search for 'gate' found {search_result['pagination']['total']} results:")
        for log in search_result['logs']:
            print(f"  - {log['action']} {log['entity_type']} - {log['action_description']}")
        
        # 5. Export test
        print("\n5. Testing CSV export...")
        
        csv_data = audit_service.export_audit_logs_csv(organization_id=1)
        
        print(f"📄 Generated CSV export with {len(csv_data)} bytes")
        print(f"📄 CSV preview (first 200 chars):")
        print(csv_data.decode('utf-8-sig')[:200] + "...")
        
        print("\n✅ Audit system demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        raise
    
    finally:
        db.close()


def show_audit_menu():
    """Show interactive audit menu"""
    
    print("\n🔍 Audit System Management")
    print("=" * 40)
    print("1. Run full demo")
    print("2. View recent logs")
    print("3. Search logs")
    print("4. Show statistics")
    print("5. Export CSV")
    print("0. Exit")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == "1":
        demo_audit_system()
    elif choice == "2":
        show_recent_logs()
    elif choice == "3":
        search_logs()
    elif choice == "4":
        show_statistics()
    elif choice == "5":
        export_csv()
    elif choice == "0":
        print("👋 Goodbye!")
        return False
    else:
        print("❌ Invalid option")
    
    return True


def show_recent_logs():
    """Show recent audit logs"""
    db = next(get_db())
    audit_service = AuditService(db)
    
    try:
        result = audit_service.get_audit_logs(page=1, per_page=10)
        
        print(f"\n📋 Last 10 Audit Entries (Total: {result['pagination']['total']}):")
        print("-" * 80)
        
        for i, log in enumerate(result['logs'], 1):
            print(f"{i:2d}. [{log['timestamp'][:19]}] {log['username'] or 'System'}")
            print(f"    {log['action']} {log['entity_type']} (ID: {log['entity_id']})")
            if log['action_description']:
                print(f"    Description: {log['action_description']}")
            print(f"    Risk: {log['risk_level']}, Success: {log['success']}")
            if log['ip_address']:
                print(f"    IP: {log['ip_address']}")
            print()
    
    finally:
        db.close()


def search_logs():
    """Search audit logs"""
    search_term = input("Enter search term: ").strip()
    
    if not search_term:
        print("❌ Search term required")
        return
    
    db = next(get_db())
    audit_service = AuditService(db)
    
    try:
        result = audit_service.get_audit_logs(
            search_term=search_term,
            per_page=20
        )
        
        print(f"\n🔍 Search results for '{search_term}' ({result['pagination']['total']} found):")
        print("-" * 80)
        
        for log in result['logs']:
            print(f"[{log['timestamp'][:19]}] {log['username'] or 'System'}")
            print(f"  {log['action']} {log['entity_type']} - {log['action_description']}")
            print()
    
    finally:
        db.close()


def show_statistics():
    """Show audit statistics"""
    db = next(get_db())
    audit_service = AuditService(db)
    
    try:
        stats = audit_service.get_audit_statistics()
        
        print(f"\n📈 Audit Statistics")
        print("=" * 40)
        print(f"Total Logs: {stats['total_logs']}")
        
        print(f"\n📊 By Action ({len(stats['by_action'])} types):")
        for item in sorted(stats['by_action'], key=lambda x: x['count'], reverse=True):
            print(f"  {item['action']:20} {item['count']:6d}")
        
        print(f"\n📊 By Entity Type ({len(stats['by_entity_type'])} types):")
        for item in sorted(stats['by_entity_type'], key=lambda x: x['count'], reverse=True):
            print(f"  {item['entity_type']:20} {item['count']:6d}")
        
        print(f"\n⚠️  By Risk Level ({len(stats['by_risk_level'])} levels):")
        for item in sorted(stats['by_risk_level'], key=lambda x: x['count'], reverse=True):
            print(f"  {item['risk_level']:20} {item['count']:6d}")
    
    finally:
        db.close()


def export_csv():
    """Export audit logs to CSV"""
    db = next(get_db())
    audit_service = AuditService(db)
    
    try:
        csv_data = audit_service.export_audit_logs_csv()
        
        filename = f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'wb') as f:
            f.write(csv_data)
        
        print(f"📄 Audit logs exported to: {filename}")
        print(f"📄 File size: {len(csv_data)} bytes")
    
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Starting Audit System Demo...")
    
    # Check if we want interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_audit_system()
    else:
        # Interactive menu
        while show_audit_menu():
            input("\nPress Enter to continue...")