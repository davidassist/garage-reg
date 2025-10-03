#!/usr/bin/env python3
"""Test script for advanced maintenance planning system."""

import asyncio
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dateutil.rrule import rrule, YEARLY, MONTHLY, WEEKLY

from app.models.maintenance_advanced import MaintenancePlan, ScheduledMaintenanceJob, MaintenanceCalendar
from app.models.auth import User
from app.models.organization import Organization, Gate
from app.services.maintenance_scheduler import MaintenanceSchedulerService
from app.services.notification_service import NotificationService

# Database setup
DATABASE_URL = "sqlite:///./garagereg.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def create_test_data():
    """Create test maintenance plans and generate jobs."""
    print("🔧 Creating test maintenance planning data...")
    
    db = SessionLocal()
    try:
        # Check if we already have test data
        existing_plan = db.query(MaintenancePlan).filter(MaintenancePlan.name.like("Test%")).first()
        if existing_plan:
            print("✅ Test data already exists, skipping creation")
            return existing_plan.id
        
        # Get first organization and gate for testing
        org = db.query(Organization).first()
        if not org:
            print("❌ No organizations found. Please create an organization first.")
            return None
            
        gate = db.query(Gate).first()
        if not gate:
            print("❌ No gates found. Please create a gate first.")
            return None
            
        user = db.query(User).first()
        if not user:
            print("❌ No users found. Please create a user first.")
            return None

        print(f"📍 Using organization: {org.name}")
        print(f"🚪 Using gate: {gate.name}")
        print(f"👤 Using user: {user.username}")
        
        # Create test maintenance plans
        plans = [
            {
                "name": "Test Annual Gate Inspection",
                "description": "Yearly comprehensive gate inspection and maintenance",
                "rrule": "FREQ=YEARLY;BYMONTH=3;BYMONTHDAY=15",  # March 15th every year
                "gate_filter": {
                    "gate_types": ["electric", "automatic"],
                    "manufacturers": ["CAME", "BFT", "NICE"]
                },
                "task_template": {
                    "title": "Annual Gate Inspection - {gate_name}",
                    "description": "Comprehensive yearly maintenance and safety inspection",
                    "estimated_duration_minutes": 120,
                    "priority": "high",
                    "instructions": "1. Visual inspection\n2. Lubricate moving parts\n3. Test safety systems\n4. Check electrical connections",
                    "required_tools": ["multimeter", "lubricant", "screwdriver_set"],
                    "required_skills": ["electrical_work", "mechanical_work"]
                }
            },
            {
                "name": "Test Quarterly Safety Check", 
                "description": "Quarterly safety system verification",
                "rrule": "FREQ=MONTHLY;INTERVAL=3;BYMONTHDAY=1",  # Every 3 months on 1st
                "gate_filter": {
                    "gate_types": ["automatic"],
                    "min_installation_year": 2020
                },
                "task_template": {
                    "title": "Quarterly Safety Check - {gate_name}",
                    "description": "Safety system verification and testing",
                    "estimated_duration_minutes": 45,
                    "priority": "medium",
                    "instructions": "1. Test emergency stop\n2. Check safety sensors\n3. Verify backup power",
                    "required_tools": ["test_equipment"],
                    "required_skills": ["safety_systems"]
                }
            },
            {
                "name": "Test Monthly Motor Check",
                "description": "Monthly motor and drive system inspection", 
                "rrule": "FREQ=MONTHLY;BYMONTHDAY=15",  # 15th of every month
                "gate_filter": {
                    "gate_types": ["electric", "automatic"]
                },
                "task_template": {
                    "title": "Monthly Motor Check - {gate_name}",
                    "description": "Motor performance and wear inspection",
                    "estimated_duration_minutes": 30,
                    "priority": "low",
                    "instructions": "1. Listen for unusual noises\n2. Check motor temperature\n3. Inspect drive chain/belt",
                    "required_tools": ["thermometer", "lubricant"],
                    "required_skills": ["mechanical_work"]
                }
            }
        ]
        
        created_plans = []
        for plan_data in plans:
            plan = MaintenancePlan(
                org_id=org.id,
                name=plan_data["name"],
                description=plan_data["description"],
                rrule=plan_data["rrule"],
                gate_filter=plan_data["gate_filter"],
                task_template=plan_data["task_template"],
                is_active=True,
                created_by_id=user.id,
                updated_by_id=user.id
            )
            db.add(plan)
            created_plans.append(plan)
            
        db.commit()
        print(f"✅ Created {len(created_plans)} test maintenance plans")
        
        # Create a test calendar for the user
        calendar = MaintenanceCalendar(
            user_id=user.id,
            name="My Maintenance Calendar",
            description="Personal maintenance schedule",
            is_default=True,
            color="#28a745",
            filter_config={
                "show_completed": False,
                "priority_filter": ["high", "medium"],
                "assigned_only": True
            },
            timezone="Europe/Budapest"
        )
        db.add(calendar)
        db.commit()
        
        print(f"✅ Created test calendar for user {user.username}")
        return created_plans[0].id
        
    except Exception as e:
        print(f"❌ Error creating test data: {str(e)}")
        db.rollback()
        return None
    finally:
        db.close()


async def test_job_generation():
    """Test automatic job generation from maintenance plans."""
    print("\n📅 Testing job generation...")
    
    db = SessionLocal()
    try:
        scheduler = MaintenanceSchedulerService()
        
        # Generate jobs for the next 6 months
        end_date = datetime.now() + timedelta(days=180)
        jobs_created = await scheduler.generate_jobs_for_plans(
            db=db,
            end_date=end_date
        )
        
        print(f"✅ Generated {jobs_created} maintenance jobs")
        
        # Show some generated jobs
        jobs = db.query(ScheduledMaintenanceJob).order_by(ScheduledMaintenanceJob.scheduled_date).limit(5).all()
        
        print("\n📋 Upcoming maintenance jobs:")
        for job in jobs:
            print(f"  • {job.scheduled_date.strftime('%Y-%m-%d')} - {job.title}")
            print(f"    Status: {job.status}, Priority: {job.priority}")
            if job.gate:
                print(f"    Gate: {job.gate.name} ({job.gate.location})")
            print()
            
    except Exception as e:
        print(f"❌ Error generating jobs: {str(e)}")
    finally:
        db.close()


async def test_notifications():
    """Test email notification system."""
    print("\n📧 Testing notification system...")
    
    db = SessionLocal()
    try:
        notification_service = NotificationService()
        
        # Get a test job
        job = db.query(ScheduledMaintenanceJob).filter(
            ScheduledMaintenanceJob.status == 'scheduled'
        ).first()
        
        if not job:
            print("⚠️ No scheduled jobs found for notification testing")
            return
            
        user = db.query(User).first()
        if not user:
            print("⚠️ No users found for notification testing")
            return
            
        # Send test reminder notification
        await notification_service.send_job_reminder(
            db=db,
            job_id=job.id,
            user_id=user.id,
            reminder_type="due_soon"
        )
        
        print(f"✅ Test reminder notification sent for job: {job.title}")
        
    except Exception as e:
        print(f"❌ Error testing notifications: {str(e)}")
    finally:
        db.close()


async def test_calendar_export():
    """Test ICS calendar export."""
    print("\n📅 Testing calendar export...")
    
    db = SessionLocal()
    try:
        notification_service = NotificationService()
        
        user = db.query(User).first()
        if not user:
            print("⚠️ No users found for calendar testing")
            return
            
        # Generate ICS calendar
        ics_content = await notification_service.generate_user_calendar(
            db=db,
            user_id=user.id,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=90)
        )
        
        # Save to file for inspection
        with open("test_calendar.ics", "w", encoding="utf-8") as f:
            f.write(ics_content)
            
        print(f"✅ ICS calendar exported to test_calendar.ics")
        print(f"   Calendar size: {len(ics_content)} characters")
        
    except Exception as e:
        print(f"❌ Error testing calendar export: {str(e)}")
    finally:
        db.close()


async def main():
    """Run all tests."""
    print("🚀 Advanced Maintenance Planning System Test")
    print("=" * 50)
    
    # Create test data
    plan_id = await create_test_data()
    if not plan_id:
        print("❌ Failed to create test data, stopping tests")
        return
    
    # Test job generation
    await test_job_generation()
    
    # Test notifications
    await test_notifications()
    
    # Test calendar export
    await test_calendar_export()
    
    print("\n🏁 Test completed!")
    print("\n📋 Next steps:")
    print("  1. Check Mailhog at http://localhost:8025 for test emails")
    print("  2. Review generated test_calendar.ics file")
    print("  3. Check database for created maintenance jobs")
    print("  4. Start Celery worker to process background tasks:")
    print("     celery -A app.core.celery_app worker --loglevel=info")


if __name__ == "__main__":
    asyncio.run(main())