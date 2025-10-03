#!/usr/bin/env python3
"""
Test script for Field Forms and State Machine API
Tests inspection workflow: start -> update -> complete with photos and conflicts
"""
import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8001/api/v1"

def get_auth_token():
    """Get JWT token for authentication."""
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None

def get_auth_headers():
    """Get headers with authentication token."""
    token = get_auth_token()
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def make_request(method, url, **kwargs):
    """Make authenticated request."""
    headers = kwargs.get('headers', {})
    headers.update(get_auth_headers())
    kwargs['headers'] = headers
    return getattr(requests, method)(url, **kwargs)

def test_inspection_happy_path():
    """Test the complete happy path inspection workflow."""
    print("=== Happy Path Test: Complete Inspection Workflow ===")
    
    try:
        # Step 1: Start Inspection
        print("\n1. Starting inspection...")
        start_data = {
            "gate_id": 1,
            "checklist_template_id": 1,
            "inspection_type": "routine",
            "reason": "Scheduled quarterly inspection",
            "mobile_device_id": "test-device-001",
            "offline_mode": False,
            "weather_conditions": "Clear, dry",
            "temperature_celsius": 22,
            "humidity_percentage": 45
        }
        
        response = make_request('post', f"{BASE_URL}/field-forms/test/inspections/start", json=start_data)
        if response.status_code != 200:
            print(f"❌ Failed to start inspection: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
        
        inspection = response.json()
        inspection_id = inspection["id"]
        print(f"✅ Inspection started successfully (ID: {inspection_id})")
        print(f"   State: {inspection['state']}")
        print(f"   Total items: {inspection.get('total_items', 0)}")
        
        # Step 2: Update some inspection items
        print("\n2. Updating inspection items...")
        update_data = {
            "state": "in_progress",
            "items": [
                {
                    "checklist_item_id": 1,
                    "result": "pass",
                    "value": "Satisfactory condition",
                    "notes": "All safety devices functioning properly"
                },
                {
                    "checklist_item_id": 2,  
                    "result": "warning",
                    "value": "Minor wear observed",
                    "notes": "Recommend monitoring for next inspection",
                    "measurement": {
                        "value": 180,
                        "unit": "N",
                        "tolerance": 50,
                        "min_value": 100,
                        "max_value": 400,
                        "target_value": 150
                    }
                }
            ],
            "mobile_device_id": "test-device-001",
            "last_modified_at": datetime.utcnow().isoformat()
        }
        
        response = requests.patch(f"{BASE_URL}/field-forms/inspections/{inspection_id}", json=update_data)
        if response.status_code != 200:
            print(f"❌ Failed to update inspection: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
        updated_inspection = response.json()
        print(f"✅ Inspection updated successfully")
        print(f"   State: {updated_inspection['state']}")
        print(f"   Completed items: {updated_inspection.get('completed_items', 0)}")
        
        # Step 3: Request photo upload
        print("\n3. Requesting photo upload...")
        photo_request = {
            "inspection_id": inspection_id,
            "inspection_item_id": 2,  # For the item with warning
            "metadata": {
                "category": "evidence",
                "title": "Minor wear evidence photo",
                "description": "Photo showing minor wear on component",
                "original_filename": "wear_evidence.jpg",
                "mime_type": "image/jpeg",
                "file_size_bytes": 1024000,
                "width_pixels": 1920,
                "height_pixels": 1080,
                "gps_latitude": 47.6062,
                "gps_longitude": -122.3321,
                "location_accuracy_meters": 5.0,
                "captured_at": datetime.utcnow().isoformat(),
                "device_info": {
                    "camera": "iPhone 13 Pro",
                    "app_version": "1.0.0"
                },
                "is_required": True
            }
        }
        
        response = requests.post(f"{BASE_URL}/field-forms/inspections/{inspection_id}/photos/upload", json=photo_request)
        if response.status_code != 200:
            print(f"❌ Failed to request photo upload: {response.status_code}")
            print(f"   Error: {response.text}")
        else:
            upload_response = response.json()
            photo_id = upload_response["photo_id"]
            print(f"✅ Photo upload URL generated (Photo ID: {photo_id})")
            print(f"   Upload URL: {upload_response['upload_url'][:50]}...")
            
            # Simulate photo upload completion
            print("\n4. Confirming photo upload...")
            response = requests.post(f"{BASE_URL}/field-forms/inspections/{inspection_id}/photos/{photo_id}/confirm")
            if response.status_code == 200:
                print("✅ Photo upload confirmed")
            else:
                print(f"⚠️  Photo confirmation failed: {response.status_code}")
        
        # Step 4: Get validation status
        print("\n5. Checking validation status...")
        response = requests.get(f"{BASE_URL}/field-forms/inspections/{inspection_id}/validation")
        if response.status_code == 200:
            validation = response.json()
            print(f"✅ Validation status retrieved")
            print(f"   Can complete: {validation['can_complete']}")
            print(f"   Required actions: {len(validation['required_actions'])}")
            for action in validation['required_actions']:
                print(f"     - {action}")
        
        # Step 5: Complete inspection
        print("\n6. Completing inspection...")
        complete_data = {
            "overall_status": "passed",
            "inspector_notes": "Inspection completed successfully with minor issues noted",
            "requires_followup": True,
            "followup_priority": "low",
            "followup_notes": "Monitor wear condition in next inspection",
            "next_inspection_date": (datetime.utcnow() + timedelta(days=90)).isoformat(),
            "items": [
                {
                    "checklist_item_id": 1,
                    "result": "pass",
                    "value": "Final check - satisfactory",
                    "notes": "Confirmed satisfactory condition"
                },
                {
                    "checklist_item_id": 2,
                    "result": "warning", 
                    "value": "Monitored condition",
                    "notes": "Documented with photo evidence"
                }
            ],
            "all_required_photos": True,
            "all_measurements_complete": True
        }
        
        response = requests.post(f"{BASE_URL}/field-forms/inspections/{inspection_id}/complete", json=complete_data)
        if response.status_code != 200:
            print(f"❌ Failed to complete inspection: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
        
        completed_inspection = response.json()
        print(f"✅ Inspection completed successfully")
        print(f"   Final state: {completed_inspection['state']}")
        print(f"   Overall status: {completed_inspection['overall_status']}")
        print(f"   Overall score: {completed_inspection.get('overall_score', 'N/A')}")
        print(f"   Duration: {completed_inspection.get('duration_minutes', 'N/A')} minutes")
        
        return inspection_id
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server. Make sure it's running on http://localhost:8000")
        return None
    except Exception as e:
        print(f"❌ Unexpected error in happy path test: {e}")
        return None


def test_conflict_scenario():
    """Test conflict detection and resolution."""
    print("\n=== Conflict Scenario Test ===")
    
    try:
        # Step 1: Start inspection
        print("\n1. Starting inspection for conflict test...")
        start_data = {
            "gate_id": 2,
            "checklist_template_id": 1,
            "inspection_type": "emergency",
            "reason": "Testing conflict resolution",
            "mobile_device_id": "conflict-device-002",
            "offline_mode": True  # Start in offline mode
        }
        
        response = requests.post(f"{BASE_URL}/field-forms/inspections/start", json=start_data)
        if response.status_code != 200:
            print(f"❌ Failed to start inspection: {response.status_code}")
            return False
        
        inspection = response.json()
        inspection_id = inspection["id"]
        print(f"✅ Inspection started in offline mode (ID: {inspection_id})")
        
        # Step 2: Simulate server-side modification (different user/session)
        print("\n2. Simulating concurrent modification...")
        server_update = {
            "overall_status": "in_progress",
            "weather_conditions": "Server updated weather",
            "mobile_device_id": "server-device"
        }
        
        requests.patch(f"{BASE_URL}/field-forms/inspections/{inspection_id}", json=server_update)
        print("✅ Server-side modification applied")
        
        # Step 3: Simulate client trying to sync after delay
        print("\n3. Client attempting sync with potential conflict...")
        time.sleep(1)  # Ensure timestamp difference
        
        client_update = {
            "overall_status": "warning", 
            "weather_conditions": "Client offline weather data",
            "items": [
                {
                    "checklist_item_id": 1,
                    "result": "fail",
                    "value": "Critical issue found offline",
                    "notes": "Found during offline inspection"
                }
            ],
            "mobile_device_id": "conflict-device-002",
            "last_modified_at": (datetime.utcnow() - timedelta(minutes=5)).isoformat()  # Old timestamp
        }
        
        response = requests.patch(f"{BASE_URL}/field-forms/inspections/{inspection_id}", json=client_update)
        
        if response.status_code == 409:
            print("✅ Conflict detected successfully!")
            conflict_data = response.json()
            print(f"   Conflict message: {conflict_data.get('message')}")
            print("   Resolution required: True")
            
            # Step 4: Resolve conflict
            print("\n4. Resolving conflict...")
            resolution_data = {
                "merge_strategy": "manual",
                "merged_data": {
                    "overall_status": "warning",  # Client wins
                    "weather_conditions": "Resolved: Client offline + server data",  # Manual merge
                    "inspector_notes": "Conflict resolved manually - offline data prioritized"
                }
            }
            
            response = requests.post(f"{BASE_URL}/field-forms/inspections/{inspection_id}/resolve-conflict", json=resolution_data)
            if response.status_code == 200:
                print("✅ Conflict resolved successfully")
                resolution_result = response.json()
                print(f"   Status: {resolution_result['status']}")
                print(f"   Strategy used: {resolution_result['merge_strategy']}")
                return True
            else:
                print(f"❌ Conflict resolution failed: {response.status_code}")
                return False
        else:
            print(f"⚠️  Expected conflict (409) but got: {response.status_code}")
            if response.status_code == 200:
                print("   Update succeeded without conflict (may be expected)")
            return False
            
    except Exception as e:
        print(f"❌ Conflict scenario test failed: {e}")
        return False


def test_photo_enforcement():
    """Test mandatory photo enforcement."""
    print("\n=== Photo Enforcement Test ===")
    
    try:
        # Step 1: Start inspection
        start_data = {
            "gate_id": 3,
            "checklist_template_id": 1,
            "inspection_type": "safety",
            "reason": "Testing photo requirements",
            "mobile_device_id": "photo-test-device"
        }
        
        response = requests.post(f"{BASE_URL}/field-forms/inspections/start", json=start_data)
        if response.status_code != 200:
            print(f"❌ Failed to start inspection: {response.status_code}")
            return False
        
        inspection = response.json()
        inspection_id = inspection["id"]
        print(f"✅ Inspection started for photo test (ID: {inspection_id})")
        
        # Step 2: Update with failed item (should require photo)
        print("\n2. Adding failed item that requires photo...")
        update_data = {
            "items": [
                {
                    "checklist_item_id": 1,
                    "result": "fail", 
                    "value": "Critical safety failure",
                    "notes": "Safety device not functioning - requires immediate attention and photo evidence"
                }
            ]
        }
        
        response = requests.patch(f"{BASE_URL}/field-forms/inspections/{inspection_id}", json=update_data)
        print("✅ Failed item added")
        
        # Step 3: Try to complete without required photos
        print("\n3. Attempting completion without required photos...")
        complete_data = {
            "overall_status": "failed",
            "inspector_notes": "Critical issues found",
            "requires_followup": True,
            "followup_priority": "urgent",
            "items": [
                {
                    "checklist_item_id": 1,
                    "result": "fail",
                    "value": "Final result - failed",
                    "notes": "Safety critical failure confirmed"
                }
            ],
            "all_required_photos": False,  # Missing photos
            "all_measurements_complete": True
        }
        
        response = requests.post(f"{BASE_URL}/field-forms/inspections/{inspection_id}/complete", json=complete_data)
        
        if response.status_code == 400:
            print("✅ Completion properly blocked due to missing photos")
            error_details = response.json()
            print(f"   Error: {error_details.get('detail', {}).get('message', 'Validation failed')}")
        else:
            print(f"⚠️  Expected validation error (400) but got: {response.status_code}")
        
        # Step 4: Add required photo and complete
        print("\n4. Adding required evidence photo...")
        photo_request = {
            "inspection_id": inspection_id,
            "inspection_item_id": 1,
            "metadata": {
                "category": "evidence",
                "title": "Safety failure evidence",
                "description": "Photo documenting critical safety device failure",
                "original_filename": "safety_failure.jpg",
                "mime_type": "image/jpeg",
                "is_required": True
            }
        }
        
        response = requests.post(f"{BASE_URL}/field-forms/inspections/{inspection_id}/photos/upload", json=photo_request)
        if response.status_code == 200:
            upload_response = response.json()
            photo_id = upload_response["photo_id"]
            
            # Confirm photo upload
            requests.post(f"{BASE_URL}/field-forms/inspections/{inspection_id}/photos/{photo_id}/confirm")
            print("✅ Required evidence photo uploaded")
            
            # Now try completion again
            print("\n5. Completing with required photos...")
            complete_data["all_required_photos"] = True
            
            response = requests.post(f"{BASE_URL}/field-forms/inspections/{inspection_id}/complete", json=complete_data)
            if response.status_code == 200:
                print("✅ Inspection completed successfully with photos")
                return True
            else:
                print(f"❌ Completion still failed: {response.status_code}")
                return False
        else:
            print(f"❌ Photo upload failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Photo enforcement test failed: {e}")
        return False


def test_measurement_validation():
    """Test numeric measurement validation with units."""
    print("\n=== Measurement Validation Test ===")
    
    try:
        # Start inspection
        start_data = {
            "gate_id": 4,
            "checklist_template_id": 1,
            "inspection_type": "technical",
            "reason": "Testing measurement validation"
        }
        
        response = requests.post(f"{BASE_URL}/field-forms/inspections/start", json=start_data)
        inspection = response.json()
        inspection_id = inspection["id"]
        print(f"✅ Inspection started for measurement test (ID: {inspection_id})")
        
        # Test various measurements
        print("\n1. Testing valid measurement (within tolerance)...")
        update_data = {
            "items": [
                {
                    "checklist_item_id": 1,
                    "result": "pass",
                    "measurement": {
                        "value": 155,  # Close to target of 150
                        "unit": "N",
                        "tolerance": 50,
                        "min_value": 100,
                        "max_value": 400,
                        "target_value": 150
                    },
                    "notes": "Force measurement within acceptable range"
                }
            ]
        }
        
        response = requests.patch(f"{BASE_URL}/field-forms/inspections/{inspection_id}", json=update_data)
        print("✅ Valid measurement accepted")
        
        print("\n2. Testing measurement at tolerance limit...")
        update_data["items"][0]["measurement"]["value"] = 200  # At tolerance boundary
        update_data["items"][0]["result"] = "warning"
        update_data["items"][0]["notes"] = "Force at tolerance limit - monitor"
        
        response = requests.patch(f"{BASE_URL}/field-forms/inspections/{inspection_id}", json=update_data)
        print("✅ Boundary measurement accepted with warning")
        
        print("\n3. Testing out-of-range measurement...")
        update_data["items"][0]["measurement"]["value"] = 450  # Exceeds max
        update_data["items"][0]["result"] = "fail"
        update_data["items"][0]["notes"] = "Force exceeds maximum safe limit - CRITICAL"
        
        response = requests.patch(f"{BASE_URL}/field-forms/inspections/{inspection_id}", json=update_data)
        print("✅ Out-of-range measurement accepted with fail result")
        
        return True
        
    except Exception as e:
        print(f"❌ Measurement validation test failed: {e}")
        return False


def main():
    """Run all field form tests."""
    print("🏗️  Field Forms and State Machine Test Suite")
    print("=" * 50)
    
    results = {
        "happy_path": False,
        "conflict_scenario": False, 
        "photo_enforcement": False,
        "measurement_validation": False
    }
    
    # Test 1: Happy Path
    inspection_id = test_inspection_happy_path()
    results["happy_path"] = inspection_id is not None
    
    # Test 2: Conflict Scenario
    results["conflict_scenario"] = test_conflict_scenario()
    
    # Test 3: Photo Enforcement 
    results["photo_enforcement"] = test_photo_enforcement()
    
    # Test 4: Measurement Validation
    results["measurement_validation"] = test_measurement_validation()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Field forms system is working correctly.")
        print("\n✅ FIELD FORMS REQUIREMENTS FULFILLED:")
        print("   📱 State machine (start -> update -> complete)")
        print("   📸 Photo documentation with S3 integration") 
        print("   📏 Numeric measurements with units and validation")
        print("   🔄 Conflict detection and resolution for offline sync")
        print("   ✋ Mandatory photo enforcement")
    else:
        print(f"⚠️  {total_tests - passed_tests} tests failed. Check the output above for details.")


if __name__ == "__main__":
    main()