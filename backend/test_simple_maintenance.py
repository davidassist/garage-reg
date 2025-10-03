#!/usr/bin/env python3
"""Simple test script for maintenance planning system."""

import sqlite3
from datetime import datetime, timedelta

def create_sample_data():
    """Create sample maintenance plans and jobs directly in database."""
    print("🔧 Creating sample maintenance data...")
    
    conn = sqlite3.connect('garagereg.db')
    cursor = conn.cursor()
    
    try:
        # Check if we have organizations and users
        cursor.execute("SELECT COUNT(*) FROM organizations")
        org_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users") 
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM gates")
        gate_count = cursor.fetchone()[0]
        
        print(f"📊 Database status:")
        print(f"   Organizations: {org_count}")
        print(f"   Users: {user_count}")
        print(f"   Gates: {gate_count}")
        
        if org_count == 0 or user_count == 0:
            print("❌ Missing required data. Please create organizations and users first.")
            return False
            
        # Get first org and user
        cursor.execute("SELECT id FROM organizations LIMIT 1")
        org_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT id FROM users LIMIT 1")
        user_id = cursor.fetchone()[0]
        
        # Create sample maintenance plan
        now = datetime.now()
        plan_data = {
            'org_id': org_id,
            'name': 'Test Yearly Gate Inspection',
            'description': 'Annual comprehensive gate maintenance',
            'rrule': 'FREQ=YEARLY;BYMONTH=3;BYMONTHDAY=15',
            'gate_filter': '{"gate_types": ["electric", "automatic"]}',
            'task_template': '{"title": "Annual Inspection", "priority": "high", "estimated_duration_minutes": 120}',
            'is_active': True,
            'created_at': now.isoformat(),
            'updated_at': now.isoformat(),
            'created_by_id': user_id,
            'updated_by_id': user_id
        }
        
        cursor.execute("""
            INSERT INTO advanced_maintenance_plans 
            (org_id, name, description, rrule, gate_filter, task_template, is_active, 
             created_at, updated_at, created_by_id, updated_by_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            plan_data['org_id'], plan_data['name'], plan_data['description'],
            plan_data['rrule'], plan_data['gate_filter'], plan_data['task_template'],
            plan_data['is_active'], plan_data['created_at'], plan_data['updated_at'],
            plan_data['created_by_id'], plan_data['updated_by_id']
        ))
        
        plan_id = cursor.lastrowid
        
        # Create sample scheduled job if we have gates
        if gate_count > 0:
            cursor.execute("SELECT id FROM gates LIMIT 1")
            gate_id = cursor.fetchone()[0]
            
            job_data = {
                'org_id': org_id,
                'plan_id': plan_id,
                'gate_id': gate_id,
                'title': 'Annual Gate Inspection - Sample Gate',
                'description': 'Yearly comprehensive maintenance and inspection',
                'scheduled_date': (now + timedelta(days=30)).isoformat(),
                'due_date': (now + timedelta(days=37)).isoformat(),
                'status': 'scheduled',
                'priority': 'high',
                'estimated_duration_minutes': 120,
                'instructions': 'Complete annual inspection checklist',
                'required_tools': '["multimeter", "lubricant", "screwdriver_set"]',
                'required_skills': '["electrical_work", "mechanical_work"]',
                'created_at': now.isoformat(),
                'updated_at': now.isoformat()
            }
            
            cursor.execute("""
                INSERT INTO advanced_scheduled_jobs
                (org_id, plan_id, gate_id, title, description, scheduled_date, due_date,
                 status, priority, estimated_duration_minutes, instructions, 
                 required_tools, required_skills, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_data['org_id'], job_data['plan_id'], job_data['gate_id'],
                job_data['title'], job_data['description'], job_data['scheduled_date'],
                job_data['due_date'], job_data['status'], job_data['priority'],
                job_data['estimated_duration_minutes'], job_data['instructions'],
                job_data['required_tools'], job_data['required_skills'],
                job_data['created_at'], job_data['updated_at']
            ))
        
        # Create sample calendar
        calendar_data = {
            'user_id': user_id,
            'name': 'My Maintenance Calendar',
            'description': 'Personal maintenance schedule view',
            'is_default': True,
            'color': '#28a745',
            'filter_config': '{"show_completed": false, "priority_filter": ["high", "medium"]}',
            'timezone': 'Europe/Budapest',
            'created_at': now.isoformat(),
            'updated_at': now.isoformat()
        }
        
        cursor.execute("""
            INSERT INTO advanced_maintenance_calendars
            (user_id, name, description, is_default, color, filter_config, timezone, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            calendar_data['user_id'], calendar_data['name'], calendar_data['description'],
            calendar_data['is_default'], calendar_data['color'], calendar_data['filter_config'],
            calendar_data['timezone'], calendar_data['created_at'], calendar_data['updated_at']
        ))
        
        conn.commit()
        
        print("✅ Sample data created successfully!")
        print(f"   • Maintenance plan: {plan_data['name']}")
        if gate_count > 0:
            print(f"   • Scheduled job: {job_data['title']}")
        print(f"   • Calendar: {calendar_data['name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


def show_data_summary():
    """Show summary of created data."""
    print("\n📋 Database summary:")
    
    conn = sqlite3.connect('garagereg.db')
    cursor = conn.cursor()
    
    try:
        # Count maintenance plans
        cursor.execute("SELECT COUNT(*) FROM advanced_maintenance_plans")
        plans_count = cursor.fetchone()[0]
        
        # Count scheduled jobs
        cursor.execute("SELECT COUNT(*) FROM advanced_scheduled_jobs")
        jobs_count = cursor.fetchone()[0]
        
        # Count calendars
        cursor.execute("SELECT COUNT(*) FROM advanced_maintenance_calendars")
        calendars_count = cursor.fetchone()[0]
        
        # Count notifications
        cursor.execute("SELECT COUNT(*) FROM advanced_maintenance_notifications")
        notifications_count = cursor.fetchone()[0]
        
        print(f"   Maintenance Plans: {plans_count}")
        print(f"   Scheduled Jobs: {jobs_count}")
        print(f"   Calendars: {calendars_count}")
        print(f"   Notifications: {notifications_count}")
        
        # Show recent jobs
        if jobs_count > 0:
            print(f"\n📅 Upcoming jobs:")
            cursor.execute("""
                SELECT title, scheduled_date, status, priority 
                FROM advanced_scheduled_jobs 
                ORDER BY scheduled_date 
                LIMIT 5
            """)
            
            for title, scheduled_date, status, priority in cursor.fetchall():
                print(f"   • {scheduled_date[:10]} - {title} ({status}, {priority})")
                
    except Exception as e:
        print(f"❌ Error reading data: {str(e)}")
        
    finally:
        conn.close()


def main():
    """Main test function."""
    print("🚀 Advanced Maintenance Planning System - Simple Test")
    print("=" * 55)
    
    # Create sample data
    success = create_sample_data()
    
    if success:
        # Show summary
        show_data_summary()
        
        print("\n🎉 Test completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Start the FastAPI server to access the maintenance planning API")
        print("   2. Start Celery worker for background job processing:")
        print("      celery -A app.core.celery_app worker --loglevel=info")
        print("   3. Start Mailhog for email testing:")
        print("      mailhog")
        print("   4. Access maintenance planning endpoints at /api/maintenance-planning/")
        
    else:
        print("\n❌ Test failed. Please check your database setup.")


if __name__ == "__main__":
    main()