"""Acceptance test for hierarchical import functionality."""

import pytest
import io
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.models.organization import Client, Site, Building, Gate


@pytest.mark.asyncio
async def test_complete_hierarchical_import_acceptance(
    client: AsyncClient, 
    admin_token: str, 
    db: Session
):
    """
    Acceptance test: Import hierarchical data and verify relational chain.
    
    This test verifies the complete acceptance criteria:
    - Example import runs successfully
    - Relational chain is verifiable
    - All entities are created with proper relationships
    """
    
    # Step 1: Prepare test data (real-world scenario)
    csv_data = """client_name,client_type,client_contact_person,client_email,client_phone,client_city,site_name,site_code,site_city,site_latitude,site_longitude,building_name,building_type,building_floors,building_units,gate_name,gate_type,manufacturer,model,serial_number,installation_date
Green Valley Residence,residential,Anna Manager,anna@greenvalley.hu,+36301234567,Budapest,Main Complex,GV-MC,Budapest,47.4979,19.0402,Building A,residential,4,16,Main Gate,sliding,Came,BXV-4,SN123456,2024-01-15
Green Valley Residence,residential,Anna Manager,anna@greenvalley.hu,+36301234567,Budapest,Main Complex,GV-MC,Budapest,47.4979,19.0402,Building A,residential,4,16,Parking Gate,swing,Nice,ROBO500,SN789012,2024-01-20
Green Valley Residence,residential,Anna Manager,anna@greenvalley.hu,+36301234567,Budapest,Main Complex,GV-MC,Budapest,47.4979,19.0402,Building B,residential,3,12,Entrance Gate,turnstile,Kaba,R550,SN345678,2024-02-01
Tech Hub Office,commercial,John Director,john@techhub.com,+36209876543,Szeged,Headquarters,TH-HQ,Szeged,46.2530,20.1414,Office Tower,office,8,40,Reception Gate,barrier,Faac,620 SR,SN901234,2024-03-01
Tech Hub Office,commercial,John Director,john@techhub.com,+36209876543,Szeged,Headquarters,TH-HQ,Szeged,46.2530,20.1414,Office Tower,office,8,40,Parking Barrier,sliding,Ditec,CROSS15,SN567890,2024-03-15
Industrial Works Ltd,industrial,Mike Supervisor,mike@industrial.hu,+36205555123,Debrecen,Production Site,IW-PS,Debrecen,47.5316,21.6273,Factory Hall,warehouse,1,1,Loading Gate,sliding,Hormann,V4015,SN111222,2024-04-01"""
    
    # Step 2: Execute import
    file_content = csv_data.encode('utf-8')
    
    response = await client.post(
        "/api/v1/import/hierarchical",
        files={"file": ("acceptance_test.csv", io.BytesIO(file_content), "text/csv")},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Step 3: Verify import success
    assert response.status_code == 200
    import_result = response.json()
    
    print(f"Import Result: {import_result}")
    
    assert import_result["success"] is True
    assert import_result["total_rows"] == 6
    assert import_result["processed_rows"] == 6
    assert import_result["skipped_rows"] == 0
    assert len(import_result["errors"]) == 0
    
    # Verify entity counts
    assert len(import_result["created_entities"]["clients"]) == 3  # 3 unique clients
    assert len(import_result["created_entities"]["sites"]) == 3    # 3 unique sites  
    assert len(import_result["created_entities"]["buildings"]) == 4  # 4 unique buildings
    assert len(import_result["created_entities"]["gates"]) == 6     # 6 gates
    
    # Step 4: Verify relational chain in database
    
    # Get organization ID from admin user
    from app.core.security import get_current_active_user
    # We'll get it from the first created client
    first_client = db.query(Client).filter(
        Client.name == "Green Valley Residence"
    ).first()
    
    assert first_client is not None
    org_id = first_client.organization_id
    
    # Verify Client → Site → Building → Gate chain for Green Valley Residence
    print("\n=== Verifying Green Valley Residence Chain ===")
    
    # 1. Client level
    green_valley_client = db.query(Client).filter(
        Client.name == "Green Valley Residence",
        Client.organization_id == org_id
    ).first()
    
    assert green_valley_client is not None
    assert green_valley_client.type == "residential"
    assert green_valley_client.contact_person == "Anna Manager"
    assert green_valley_client.email == "anna@greenvalley.hu"
    print(f"✓ Client: {green_valley_client.name} (ID: {green_valley_client.id})")
    
    # 2. Site level
    main_complex_site = db.query(Site).filter(
        Site.name == "Main Complex",
        Site.client_id == green_valley_client.id
    ).first()
    
    assert main_complex_site is not None
    assert main_complex_site.site_code == "GV-MC"
    assert main_complex_site.city == "Budapest"
    assert main_complex_site.latitude == "47.4979"
    assert main_complex_site.longitude == "19.0402"
    print(f"✓ Site: {main_complex_site.name} (ID: {main_complex_site.id}) → Client ID: {main_complex_site.client_id}")
    
    # 3. Building level
    buildings = db.query(Building).filter(
        Building.site_id == main_complex_site.id
    ).all()
    
    assert len(buildings) == 2  # Building A and Building B
    
    building_a = next((b for b in buildings if b.name == "Building A"), None)
    building_b = next((b for b in buildings if b.name == "Building B"), None)
    
    assert building_a is not None
    assert building_a.building_type == "residential"
    assert building_a.floors == 4
    assert building_a.units == 16
    print(f"✓ Building A: {building_a.name} (ID: {building_a.id}) → Site ID: {building_a.site_id}")
    
    assert building_b is not None
    assert building_b.building_type == "residential"
    assert building_b.floors == 3
    assert building_b.units == 12
    print(f"✓ Building B: {building_b.name} (ID: {building_b.id}) → Site ID: {building_b.site_id}")
    
    # 4. Gate level
    gates_a = db.query(Gate).filter(
        Gate.building_id == building_a.id
    ).all()
    
    gates_b = db.query(Gate).filter(
        Gate.building_id == building_b.id
    ).all()
    
    assert len(gates_a) == 2  # Main Gate and Parking Gate
    assert len(gates_b) == 1  # Entrance Gate
    
    # Verify specific gates
    main_gate = next((g for g in gates_a if g.name == "Main Gate"), None)
    parking_gate = next((g for g in gates_a if g.name == "Parking Gate"), None)
    entrance_gate = next((g for g in gates_b if g.name == "Entrance Gate"), None)
    
    assert main_gate is not None
    assert main_gate.gate_type == "sliding"
    assert main_gate.manufacturer == "Came"
    assert main_gate.model == "BXV-4"
    assert main_gate.serial_number == "SN123456"
    print(f"✓ Main Gate: {main_gate.name} (ID: {main_gate.id}) → Building ID: {main_gate.building_id}")
    
    assert parking_gate is not None
    assert parking_gate.gate_type == "swing"
    assert parking_gate.manufacturer == "Nice"
    print(f"✓ Parking Gate: {parking_gate.name} (ID: {parking_gate.id}) → Building ID: {parking_gate.building_id}")
    
    assert entrance_gate is not None
    assert entrance_gate.gate_type == "turnstile"
    assert entrance_gate.manufacturer == "Kaba"
    print(f"✓ Entrance Gate: {entrance_gate.name} (ID: {entrance_gate.id}) → Building ID: {entrance_gate.building_id}")
    
    # Step 5: Verify cross-client isolation
    print("\n=== Verifying Other Clients ===")
    
    # Tech Hub Office
    tech_hub_client = db.query(Client).filter(
        Client.name == "Tech Hub Office",
        Client.organization_id == org_id
    ).first()
    
    assert tech_hub_client is not None
    assert tech_hub_client.type == "commercial"
    print(f"✓ Client: {tech_hub_client.name} (ID: {tech_hub_client.id})")
    
    # Industrial Works Ltd
    industrial_client = db.query(Client).filter(
        Client.name == "Industrial Works Ltd",
        Client.organization_id == org_id
    ).first()
    
    assert industrial_client is not None  
    assert industrial_client.type == "industrial"
    print(f"✓ Client: {industrial_client.name} (ID: {industrial_client.id})")
    
    # Step 6: Verify complete relational chain can be traversed
    print("\n=== Verifying Complete Chain Traversal ===")
    
    # Start from gate and traverse up to client
    test_gate = main_gate
    test_building = db.query(Building).filter(Building.id == test_gate.building_id).first()
    test_site = db.query(Site).filter(Site.id == test_building.site_id).first()
    test_client = db.query(Client).filter(Client.id == test_site.client_id).first()
    
    assert test_client.name == "Green Valley Residence"
    assert test_site.name == "Main Complex"
    assert test_building.name == "Building A"
    assert test_gate.name == "Main Gate"
    
    print(f"✓ Upward chain: {test_gate.name} → {test_building.name} → {test_site.name} → {test_client.name}")
    
    # Traverse down from client
    client_sites = db.query(Site).filter(Site.client_id == test_client.id).all()
    site_buildings = []
    for site in client_sites:
        buildings = db.query(Building).filter(Building.site_id == site.id).all()
        site_buildings.extend(buildings)
    
    building_gates = []
    for building in site_buildings:
        gates = db.query(Gate).filter(Gate.building_id == building.id).all()
        building_gates.extend(gates)
    
    assert len(client_sites) == 1  # Green Valley has 1 site
    assert len(site_buildings) == 2  # Main Complex has 2 buildings
    assert len(building_gates) == 3  # Buildings have 3 total gates
    
    print(f"✓ Downward chain: {test_client.name} → {len(client_sites)} sites → {len(site_buildings)} buildings → {len(building_gates)} gates")
    
    # Step 7: Test API retrieval of imported data
    print("\n=== Verifying API Access to Imported Data ===")
    
    # Get client with statistics
    client_response = await client.get(
        f"/api/v1/structure/clients/{green_valley_client.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert client_response.status_code == 200
    client_data = client_response.json()
    assert client_data["name"] == "Green Valley Residence"
    assert client_data["sites_count"] == 1
    assert client_data["buildings_count"] == 2
    assert client_data["gates_count"] == 3
    
    print(f"✓ API Client stats: {client_data['sites_count']} sites, {client_data['buildings_count']} buildings, {client_data['gates_count']} gates")
    
    # Get gates for the client's buildings
    gates_response = await client.get(
        f"/api/v1/structure/gates?building_id={building_a.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert gates_response.status_code == 200
    gates_data = gates_response.json()
    assert gates_data["total"] == 2  # Building A has 2 gates
    
    print(f"✓ API Gates query: Found {gates_data['total']} gates for Building A")
    
    print("\n🎉 ACCEPTANCE TEST PASSED!")
    print("✅ Example import completed successfully")
    print("✅ Relational chain is fully verifiable")
    print("✅ All entities created with proper relationships")
    print("✅ API access works for imported data")
    print("✅ Cross-client isolation maintained")
    print("✅ Complete hierarchy traversal verified")


@pytest.mark.asyncio
async def test_import_error_handling_acceptance(
    client: AsyncClient,
    admin_token: str
):
    """
    Acceptance test for import error handling.
    Verifies that import gracefully handles various error conditions.
    """
    
    # Test data with intentional errors
    csv_data = """client_name,client_type,client_contact_person,site_name,building_name,gate_name,gate_type
Valid Client,commercial,John Doe,Valid Site,Valid Building,Valid Gate,swing
,invalid_type,Jane Smith,Missing Client Name,Building 2,Gate 2,sliding
Invalid Client 2,residential,Bob Wilson,Valid Site 2,,Gate 3,barrier
Invalid Client 3,commercial,Alice Brown,Valid Site 3,Valid Building 3,Gate 4,invalid_gate_type"""
    
    file_content = csv_data.encode('utf-8')
    
    response = await client.post(
        "/api/v1/import/hierarchical",
        files={"file": ("error_test.csv", io.BytesIO(file_content), "text/csv")},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    result = response.json()
    
    # Should process some rows but have errors for others
    assert result["total_rows"] == 4
    assert result["processed_rows"] >= 1  # At least the valid row
    assert result["skipped_rows"] >= 1    # At least one error row
    assert len(result["errors"]) > 0      # Should have error messages
    
    print(f"\n=== Error Handling Test Results ===")
    print(f"Total rows: {result['total_rows']}")
    print(f"Processed: {result['processed_rows']}")
    print(f"Skipped: {result['skipped_rows']}")
    print(f"Errors: {len(result['errors'])}")
    
    for error in result["errors"]:
        print(f"  - {error}")
    
    print("✅ Error handling acceptance test passed!")


if __name__ == "__main__":
    # This allows running the test directly for manual verification
    pytest.main([__file__, "-v"])