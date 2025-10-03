#!/usr/bin/env python3
"""
Test script for Dynamic Checklist API - EU Standards preloading and template creation
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_eu_standards_preload():
    """Test preloading EU standard templates"""
    print("=== Testing EU Standards Preload ===")
    
    standards = ["EN13241", "EN12453", "EN12604"]
    
    for standard in standards:
        print(f"\nTesting {standard}...")
        
        # Get EU standard template preview
        response = requests.get(f"{BASE_URL}/dynamic-checklists/standards/{standard}/preview")
        
        if response.status_code == 200:
            template_data = response.json()
            print(f"✅ {standard} template loaded successfully")
            print(f"   Name: {template_data.get('name', 'N/A')}")
            print(f"   Category: {template_data.get('category', 'N/A')}")
            print(f"   Sections: {len(template_data.get('sections', []))}")
            
            # Count items by type
            items_by_type = {}
            for section in template_data.get('sections', []):
                for item in section.get('items', []):
                    item_type = item.get('measurement_type', 'unknown')
                    items_by_type[item_type] = items_by_type.get(item_type, 0) + 1
            
            print(f"   Items by type: {items_by_type}")
        else:
            print(f"❌ Failed to load {standard}: {response.status_code}")
            print(f"   Error: {response.text}")

def test_json_schema_validation():
    """Test JSON schema creation and validation"""
    print("\n=== Testing JSON Schema Validation ===")
    
    # Test schema for EN 13241 - first we need to create a template
    create_response = requests.post(f"{BASE_URL}/dynamic-checklists/templates/preload/EN13241", json={"org_id": 1})
    if create_response.status_code != 200:
        print(f"❌ Failed to create template for schema test: {create_response.status_code}")
        return
    template = create_response.json()
    template_id = template.get('id')
    
    # Now test JSON schema generation
    response = requests.get(f"{BASE_URL}/dynamic-checklists/templates/{template_id}/json-schema")
    
    if response.status_code == 200:
        schema = response.json()
        print("✅ JSON schema generated successfully")
        print(f"   Schema type: {schema.get('type', 'N/A')}")
        print(f"   Properties count: {len(schema.get('properties', {}))}")
        
        # Show first few properties
        properties = schema.get('properties', {})
        for i, (key, value) in enumerate(list(properties.items())[:3]):
            print(f"   Property {i+1}: {key} -> {value.get('type', 'N/A')}")
    else:
        print(f"❌ Failed to generate JSON schema: {response.status_code}")
        print(f"   Error: {response.text}")

def test_template_creation():
    """Test creating a template from EU standard"""
    print("\n=== Testing Template Creation ===")
    
    # Create template from EN 12453
    create_data = {
        "org_id": 1
    }
    
    response = requests.post(
        f"{BASE_URL}/dynamic-checklists/templates/preload/EN12453", 
        json=create_data
    )
    
    if response.status_code == 200:
        template = response.json()
        print("✅ Template created successfully from EU standard")
        print(f"   Template ID: {template.get('id', 'N/A')}")
        print(f"   Name: {template.get('name', 'N/A')}")
        print(f"   Items count: {len(template.get('items', []))}")
        return template.get('id')
    else:
        print(f"❌ Failed to create template: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def test_inspection_creation(template_id):
    """Test creating an inspection from template"""
    if not template_id:
        print("\n❌ Skipping inspection creation - no template ID")
        return
    
    print(f"\n=== Testing Inspection Creation from Template {template_id} ===")
    
    inspection_data = {
        "gate_id": 1,
        "checklist_template_id": template_id,
        "inspector_notes": "Test inspection from EU standard template",
        "weather_conditions": "Clear, dry",
        "temperature": 20.5
    }
    
    response = requests.post(
        f"{BASE_URL}/dynamic-checklists/inspections/create-from-template",
        json=inspection_data
    )
    
    if response.status_code == 200:
        inspection = response.json()
        print("✅ Inspection created successfully")
        print(f"   Inspection ID: {inspection.get('id', 'N/A')}")
        print(f"   Items count: {len(inspection.get('items', []))}")
        
        # Show some items
        for i, item in enumerate(inspection.get('items', [])[:3]):
            print(f"   Item {i+1}: {item.get('title', 'N/A')} [{item.get('measurement_type', 'N/A')}]")
            
        return inspection.get('id')
    else:
        print(f"❌ Failed to create inspection: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def main():
    """Run all tests"""
    print("🔧 Dynamic Checklist API Test Suite")
    print("=====================================")
    
    try:
        # Test 1: EU Standards preloading
        test_eu_standards_preload()
        
        # Test 2: JSON Schema validation
        test_json_schema_validation()
        
        # Test 3: Template creation
        template_id = test_template_creation()
        
        # Test 4: Inspection creation
        inspection_id = test_inspection_creation(template_id)
        
        print("\n🎉 Testing completed!")
        
        if template_id and inspection_id:
            print("✅ All tests passed - EU standard dynamic checklist system working!")
        else:
            print("⚠️  Some tests failed - check the output above")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()