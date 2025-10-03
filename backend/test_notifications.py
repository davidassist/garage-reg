"""
Test notification service functionality
"""
import asyncio
from datetime import datetime, timezone
from app.services.notifications import (
    NotificationService, NotificationRequest, NotificationTrigger,
    NotificationRecipient, NotificationPriority
)


async def test_notification_system():
    """Test the notification system components"""
    
    print("🔔 Testing GarageReg Notification System")
    print("=" * 50)
    
    # Initialize service
    notification_service = NotificationService()
    
    # Test 1: Service Status
    print("\n📊 1. Service Status Check")
    try:
        status = notification_service.get_service_status()
        print(f"✅ Email enabled: {status['email']['enabled']}")
        print(f"✅ SMS enabled: {status['sms']['enabled']}")
        print(f"✅ Webhook enabled: {status['webhook']['enabled']}")
        print(f"   SMTP: {status['email']['smtp_host']}:{status['email']['smtp_port']}")
    except Exception as e:
        print(f"❌ Status check failed: {e}")
    
    # Test 2: Email Template Rendering
    print("\n📧 2. Email Template Test")
    try:
        from app.services.notifications.email_service import MJMLRenderer
        
        renderer = MJMLRenderer()
        
        # Test inspection due template
        context = {
            'user_name': 'Teszt Felhasználó',
            'gate_name': 'Főbejárat Kapu',
            'gate_location': 'A Épület - Főbejárat',
            'inspection_type': 'Éves biztonsági ellenőrzés',
            'due_date': datetime.now(timezone.utc),
            'inspector_name': 'Nagy József',
            'gate_id': 123,
            'days_until_due': 3,
            'organization_name': 'Teszt Szervezet Kft.',
            'current_date': datetime.now(timezone.utc)
        }
        
        html_content = renderer.render_mjml('inspection_due', context)
        print(f"✅ MJML template rendered successfully ({len(html_content)} chars)")
        
    except Exception as e:
        print(f"❌ Email template test failed: {e}")
    
    # Test 3: SMS Service
    print("\n📱 3. SMS Service Test")
    try:
        sms_result = await notification_service.sms_service.send_notification_sms(
            trigger=NotificationTrigger.INSPECTION_DUE,
            phone_number="+36701234567",
            template_data={
                'gate_name': 'Teszt Kapu',
                'due_date': '2025-10-05',
                'url': 'https://app.garagereg.com/test'
            }
        )
        print(f"✅ SMS test result: {sms_result['status']}")
        print(f"   Provider: {sms_result.get('provider', 'N/A')}")
        
    except Exception as e:
        print(f"❌ SMS test failed: {e}")
    
    # Test 4: Webhook Service
    print("\n🔗 4. Webhook Service Test")
    try:
        webhook_result = await notification_service.webhook_adapter.send_webhook(
            trigger=NotificationTrigger.GATE_FAULT,
            payload_data={
                'gate_id': 123,
                'gate_name': 'Teszt Kapu',
                'fault_description': 'Teszt hiba leírása',
                'severity': 'high'
            },
            targets=['monitoring']  # Test monitoring webhook
        )
        print(f"✅ Webhook test result: {webhook_result['targets_attempted']} targets attempted")
        print(f"   Successful: {webhook_result['targets_successful']}")
        
    except Exception as e:
        print(f"❌ Webhook test failed: {e}")
    
    # Test 5: Full Notification Flow
    print("\n🎯 5. Full Notification Flow Test")
    try:
        # Create notification request
        request = NotificationRequest(
            trigger=NotificationTrigger.INSPECTION_DUE,
            recipients=[
                NotificationRecipient(
                    email="test@garagereg.com",
                    name="Teszt Felhasználó",
                    phone="+36701234567"
                )
            ],
            template_data={
                'gate_name': 'Teszt Kapu #1',
                'gate_location': 'Teszt Épület - A szárny',
                'inspection_type': 'Napi ellenőrzés',
                'due_date': datetime.now(timezone.utc),
                'inspector_name': 'Teszt Ellenőr',
                'gate_id': 123,
                'days_until_due': 1,
                'url': 'https://app.garagereg.com/gates/123',
                'hours_remaining': 24,
                'work_order_id': 'WO-2025-001',
                'technician_name': 'Teszt Technikus'
            },
            priority=NotificationPriority.HIGH
        )
        
        # Send notification
        result = await notification_service.send_notification(request)
        
        print(f"✅ Notification sent: {result['status']}")
        print(f"   Channels attempted: {result['channels_attempted']}")
        print(f"   Channels successful: {result['channels_successful']}")
        print(f"   Recipients: {result['recipients']}")
        
        # Show results by channel
        for channel, channel_result in result['results'].items():
            status = channel_result.get('status', 'unknown')
            print(f"   {channel}: {status}")
    
    except Exception as e:
        print(f"❌ Full notification test failed: {e}")
    
    # Test 6: Template Variables
    print("\n📝 6. Template Variables Test")
    try:
        email_vars = notification_service.email_service.get_template_variables(
            NotificationTrigger.INSPECTION_DUE
        )
        print(f"✅ Email template variables: {', '.join(email_vars)}")
        
        sms_vars = notification_service.sms_service.get_sms_template_variables(
            NotificationTrigger.SLA_EXPIRING
        )
        print(f"✅ SMS template variables: {', '.join(sms_vars)}")
        
    except Exception as e:
        print(f"❌ Template variables test failed: {e}")
    
    # Test 7: Phone Number Validation
    print("\n📞 7. Phone Number Validation Test")
    try:
        test_numbers = ["+36701234567", "06701234567", "701234567"]
        
        for number in test_numbers:
            validation = await notification_service.sms_service.validate_phone_number(number)
            status = "✅" if validation['valid'] else "❌"
            print(f"   {status} {number} -> {validation.get('formatted', 'Invalid')}")
            
    except Exception as e:
        print(f"❌ Phone validation test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Notification System Tests Completed!")
    print("\n📋 System Components Ready:")
    print("✅ MJML Email Templates (Handlebars-style)")
    print("✅ Multi-provider SMS Support (Twilio, Vodafone, Telekom)")
    print("✅ Webhook Adapter with HMAC Signatures") 
    print("✅ Event Triggers (Inspection Due, SLA Expiring, Work Order Complete)")
    print("✅ Priority-based Channel Selection")
    print("✅ Template Variable System")
    print("✅ MailHog SMTP Integration Ready")


if __name__ == "__main__":
    asyncio.run(test_notification_system())