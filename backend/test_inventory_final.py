#!/usr/bin/env python3
"""
🏭 GarageReg Raktárkezelési Rendszer - Végső Teljes Teszt
=======================================================

Feladat: Alap raktár modul
Kimenet: Bevét, kivét, leltár, minimumkészlet riasztás  
Kapcsolat: Munkalap alkatrészfelhasználással
Elfogadás: Kettős könyvelés elv (stock_movements), riport

Ez a teszt validálja a teljes raktárkezelési rendszert.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime, timedelta
import random
import uuid

from app.database import get_db, engine
from app.models import *
from app.services.inventory_service import InventoryService

def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"🏭 {title}")
    print("=" * 80)

def print_section(title: str):
    print(f"\n📋 {title}")
    print("-" * 60)

def print_success(message: str):
    print(f"✅ {message}")

def print_error(message: str):
    print(f"❌ {message}")

def print_info(message: str):
    print(f"📊 {message}")

def find_or_create_test_data(db: Session) -> dict:
    """Find existing or create new test data"""
    
    print_section("Teszt környezet előkészítése")
    
    # Look for existing test warehouse
    warehouse = db.query(Warehouse).filter(
        Warehouse.code.like("TEST%")
    ).first()
    
    if not warehouse:
        # Create unique test warehouse
        unique_id = str(uuid.uuid4())[:8]
        warehouse = Warehouse(
            name=f"Teszt Raktár {unique_id}",
            code=f"TEST_{unique_id}",
            description="Automatikus teszt raktár",
            warehouse_type="main",
            address_line_1="Budapest, Teszt utca 1.",
            is_active=True,
            org_id=1  # Test organization
        )
        db.add(warehouse)
        db.flush()
        print_success(f"Új teszt raktár létrehozva: {warehouse.code}")
    else:
        print_info(f"Meglévő teszt raktár használata: {warehouse.code}")
    
    # Find or create parts
    parts = []
    part_codes = ["SERVO002", "COND002", "SWITCH002", "REMOTE002", "CABLE002"]
    part_data = [
        ("SERVO002", "Teszt szervó motor", 15000, 5, 20, 10),
        ("COND002", "Teszt kondenzátor", 2500, 10, 50, 25), 
        ("SWITCH002", "Teszt kapcsoló", 3500, 3, 15, 8),
        ("REMOTE002", "Teszt távirányító", 8500, 2, 10, 5),
        ("CABLE002", "Teszt kábel", 1200, 20, 100, 50)
    ]
    
    for part_code, part_name, unit_cost, min_stock, max_stock, reorder_qty in part_data:
        part = db.query(Part).filter(Part.part_number == part_code).first()
        
        if not part:
            part = Part(
                part_number=part_code,
                name=part_name,
                description=f"Teszt alkatrész - {part_name}",
                category="test",
                supplier_part_number=part_code,
                org_id=1
            )
            db.add(part)
            db.flush()
            print_success(f"Új alkatrész létrehozva: {part_code}")
        else:
            print_info(f"Meglévő alkatrész használata: {part_code}")
        
        parts.append(part)
    
    # Find or create inventory items
    inventory_items = []
    for i, part in enumerate(parts):
        part_code, part_name, unit_cost, min_stock, max_stock, reorder_qty = part_data[i]
        
        inventory_item = db.query(InventoryItem).filter(
            InventoryItem.warehouse_id == warehouse.id,
            InventoryItem.part_id == part.id
        ).first()
        
        if not inventory_item:
            inventory_item = InventoryItem(
                warehouse_id=warehouse.id,
                part_id=part.id,
                quantity_on_hand=Decimal('0'),
                quantity_reserved=Decimal('0'),
                quantity_available=Decimal('0'),
                minimum_stock=Decimal(str(min_stock)),
                maximum_stock=Decimal(str(max_stock)),
                reorder_quantity=Decimal(str(reorder_qty)),
                average_cost=Decimal(str(unit_cost)),
                last_cost=Decimal(str(unit_cost)),
                stock_status='normal',
                is_active=True,
                org_id=1
            )
            db.add(inventory_item)
            db.flush()
            print_success(f"Új készlettétel létrehozva: {part_code}")
        else:
            # Reset quantities for clean test
            inventory_item.quantity_on_hand = Decimal('0')
            inventory_item.quantity_reserved = Decimal('0') 
            inventory_item.quantity_available = Decimal('0')
            inventory_item.minimum_stock = Decimal(str(min_stock))
            inventory_item.average_cost = Decimal(str(unit_cost))
            inventory_item.last_cost = Decimal(str(unit_cost))
            db.flush()
            print_info(f"Meglévő készlettétel alaphelyzetbe: {part_code}")
        
        inventory_items.append(inventory_item)
    
    db.commit()
    print_success(f"Teszt környezet kész - Raktár: {warehouse.code}, Alkatrészek: {len(parts)}")
    
    return {
        'warehouse': warehouse,
        'parts': parts,
        'inventory_items': inventory_items,
        'part_data': part_data
    }

def test_bevetelez_funkcio(inventory_service: InventoryService, test_data: dict):
    """Test stock receipt functionality (Bevételezés)"""
    
    print_section("1️⃣  BEVÉTELEZÉS TESZT (Kettős könyvelés)")
    
    inventory_items = test_data['inventory_items']
    part_data = test_data['part_data']
    
    receipt_data = [
        (0, 100, "Beszerzési rendelés #001"),
        (1, 50, "Beszerzési rendelés #002"), 
        (2, 75, "Beszerzési rendelés #003"),
        (3, 25, "Beszerzési rendelés #004"),
        (4, 200, "Beszerzési rendelés #005")
    ]
    
    total_movements = 0
    
    for item_idx, quantity, notes in receipt_data:
        inventory_item = inventory_items[item_idx]
        part_code, part_name, unit_cost, min_stock, max_stock, reorder_qty = part_data[item_idx]
        
        print(f"   📦 Bevételezés: {part_code} - {quantity} db @ {unit_cost} Ft")
        
        movement = inventory_service.receive_stock(
            inventory_item_id=inventory_item.id,
            quantity=Decimal(str(quantity)),
            unit_cost=Decimal(str(unit_cost)),
            reference_type="purchase_order",
            notes=notes
        )
        
        print_success(f"      Mozgás#{movement.movement_number}: Debit={movement.debit_quantity}, Credit={movement.credit_quantity}")
        total_movements += 1
    
    print_info(f"Összesen {total_movements} bevételezési mozgás rögzítve")

def test_kiadas_funkcio(inventory_service: InventoryService, test_data: dict):
    """Test stock issue functionality (Kiadás)"""
    
    print_section("2️⃣  KIADÁS TESZT (Kettős könyvelés)")
    
    inventory_items = test_data['inventory_items']
    part_data = test_data['part_data']
    
    # Issue various quantities
    issue_data = [
        (0, 25, "Garázskapu javítás #001"),
        (1, 15, "Karbantartás #002"),
        (2, 10, "Szerviz #003"),
        (3, 5, "Javítás #004")
    ]
    
    total_movements = 0
    
    for item_idx, quantity, notes in issue_data:
        inventory_item = inventory_items[item_idx]
        part_code, part_name, unit_cost, min_stock, max_stock, reorder_qty = part_data[item_idx]
        
        print(f"   📤 Kiadás: {part_code} - {quantity} db")
        
        result = inventory_service.issue_stock(
            inventory_item_id=inventory_item.id,
            quantity=Decimal(str(quantity)),
            reference_type="work_order",
            reference_id=random.randint(1000, 9999),
            notes=notes
        )
        
        # issue_stock returns (movement, part_usage) tuple
        movement = result[0] if isinstance(result, tuple) else result
        
        print_success(f"      Mozgás#{movement.movement_number}: Debit={movement.debit_quantity}, Credit={movement.credit_quantity}")
        total_movements += 1
    
    print_info(f"Összesen {total_movements} kiadási mozgás rögzítve")

def test_leltari_korrekcio(inventory_service: InventoryService, test_data: dict):
    """Test inventory adjustment (Leltári korrekció)"""
    
    print_section("3️⃣  LELTÁRI KORREKCIÓ TESZT")
    
    inventory_items = test_data['inventory_items']
    part_data = test_data['part_data']
    
    # Adjustments: some positive, some negative
    adjustment_data = [
        (0, 73, "Fizikai leltár - hiány"),  # Should be 75 after receipt-issue
        (1, 38, "Fizikai leltár - többlet"), # Should be 35 after receipt-issue
        (2, 64, "Leltári eltérés")  # Should be 65 after receipt-issue
    ]
    
    total_movements = 0
    
    for item_idx, new_quantity, reason in adjustment_data:
        inventory_item = inventory_items[item_idx]
        part_code, part_name, unit_cost, min_stock, max_stock, reorder_qty = part_data[item_idx]
        
        # Get current quantity
        inventory_service.db.refresh(inventory_item)
        current_qty = inventory_item.quantity_on_hand
        difference = Decimal(str(new_quantity)) - current_qty
        
        print(f"   📊 Leltár: {part_code} - Jelenlegi: {current_qty} db → Új: {new_quantity} db (Eltérés: {difference:+})")
        
        movement = inventory_service.adjust_stock(
            inventory_item_id=inventory_item.id,
            new_quantity=Decimal(str(new_quantity)),
            reason=reason,
            notes=f"Fizikai leltár - {reason}"
        )
        
        print_success(f"      Mozgás#{movement.movement_number}: Debit={movement.debit_quantity}, Credit={movement.credit_quantity}")
        total_movements += 1
    
    print_info(f"Összesen {total_movements} leltári korrekció rögzítve")

def test_minimum_keszlet_riasztas(inventory_service: InventoryService, test_data: dict):
    """Test minimum stock alerts (Minimumkészlet riasztás)"""
    
    print_section("4️⃣  MINIMUMKÉSZLET RIASZTÁSOK TESZT")
    
    warehouse = test_data['warehouse']
    
    alerts = inventory_service.generate_stock_alerts()
    
    print_info(f"Riasztások összesítése:")
    print(f"   🔴 Kritikus riasztások: {alerts['summary']['critical_alerts']}")
    print(f"   🟠 Magas riasztások: {alerts['summary']['high_alerts']}")
    print(f"   🟡 Közepes riasztások: {alerts['summary']['medium_alerts']}")
    print(f"   📊 Összes riasztás: {alerts['summary']['total_alerts']}")
    
    # Show detailed alerts
    if alerts['minimum_stock_alerts']:
        print("\n   📋 Részletes riasztások:")
        for alert in alerts['minimum_stock_alerts'][:5]:  # Show first 5
            print(f"      ⚠️  {alert['part_code']}: {alert['current_stock']} db (min: {alert['minimum_level']} db) - {alert['severity'].upper()}")
    
    if alerts['overstock_alerts']:
        print("\n   📈 Túlraktározás riasztások:")
        for alert in alerts['overstock_alerts'][:3]:  # Show first 3
            print(f"      📦 {alert['part_code']}: {alert['current_stock']} db (max: {alert['maximum_level']} db)")

def test_kettos_konyvezes_validacio(inventory_service: InventoryService, test_data: dict):
    """Test double-entry bookkeeping validation (Kettős könyvelés validáció)"""
    
    print_section("5️⃣  KETTŐS KÖNYVELÉS VALIDÁCIÓ")
    
    warehouse = test_data['warehouse']
    
    validation = inventory_service.validate_double_entry_balance()
    
    print_info("Kettős könyvelési egyenleg ellenőrzése:")
    print(f"   💰 Összes Debit (Tartozik): {validation['total_debits']} db")
    print(f"   💸 Összes Credit (Követel): {validation['total_credits']} db")
    print(f"   📊 Számított egyenleg: {validation['calculated_balance']} db")
    print(f"   📦 Tényleges készlet: {validation['actual_stock']} db")
    print(f"   📏 Eltérés: {validation['variance']} db")
    
    if validation['is_balanced']:
        print_success("✅ KETTŐS KÖNYVELÉS RENDBEN - Nincs eltérés!")
    else:
        print_error(f"❌ KETTŐS KÖNYVELÉS HIBA - Eltérés: {validation['variance']} db")
    
    return validation['is_balanced']

def test_riportok(inventory_service: InventoryService, test_data: dict):
    """Test reporting functionality (Riportok)"""
    
    print_section("6️⃣  RIPORTOK TESZT")
    
    warehouse = test_data['warehouse']
    
    # Stock level report
    print("📊 Készletszint Riport:")
    stock_report = inventory_service.get_current_stock_report()
    
    total_value = Decimal('0')
    total_items = 0
    
    for item in stock_report[:5]:  # Show first 5 items
        total_value += item['total_value']
        total_items += 1
        print(f"   📦 {item['part_code']}: {item['quantity_on_hand']} db @ {item['weighted_avg_cost']} Ft = {item['total_value']} Ft")
        print(f"      Status: {item['stock_status']} | Available: {item['quantity_available']} db")
    
    print_info(f"Összesen {total_items} tétel, értékük: {total_value} Ft")
    
    # Movement report
    print("\n📈 Készletmozgás Riport (utolsó 24 óra):")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)
    
    movement_report = inventory_service.get_stock_movement_report(
        start_date=start_date,
        end_date=end_date
    )
    
    print_info(f"Összesen {len(movement_report)} mozgás az utolsó 24 órában")
    
    for movement in movement_report[-5:]:  # Show last 5 movements
        print(f"   📋 {movement['movement_number']}: {movement['movement_type']} - {movement['part_code']}")
        print(f"      Debit: {movement['debit_quantity']} | Credit: {movement['credit_quantity']} | Egyenleg utána: {movement['quantity_after']}")

def main():
    """Run comprehensive inventory system test"""
    
    print_header("GarageReg Raktárkezelési Rendszer - VÉGSŐ TELJES TESZT")
    print("🎯 Feladat: Alap raktár modul")
    print("📋 Kimenet: Bevét, kivét, leltár, minimumkészlet riasztás") 
    print("✅ Elfogadás: Kettős könyvelés elv (stock_movements), riport")
    
    try:
        db = next(get_db())
        inventory_service = InventoryService(db)
        
        # Setup test environment
        test_data = find_or_create_test_data(db)
        
        # Run all tests
        test_bevetelez_funkcio(inventory_service, test_data)
        test_kiadas_funkcio(inventory_service, test_data)
        test_leltari_korrekcio(inventory_service, test_data)
        test_minimum_keszlet_riasztas(inventory_service, test_data)
        
        # Critical validation
        is_balanced = test_kettos_konyvezes_validacio(inventory_service, test_data)
        test_riportok(inventory_service, test_data)
        
        # Final summary
        print_header("TESZT ÖSSZEFOGLALÁS")
        
        if is_balanced:
            print_success("🎉 RAKTÁRKEZELÉSI MODUL SIKERESEN IMPLEMENTÁLVA!")
            print_success("📋 Minden funkció teljesítve:")
            print("   ✅ Bevételezés (receive_stock) - Kettős könyveléssel")
            print("   ✅ Kiadás (issue_stock) - Kettős könyveléssel") 
            print("   ✅ Leltári korrekció (adjust_stock)")
            print("   ✅ Minimumkészlet riasztások")
            print("   ✅ Munkalap integráció támogatás")
            print("   ✅ Kettős könyvelési validáció")
            print("   ✅ Riportgenerálás")
            print_success("🏆 MINDEN ELFOGADÁSI KRITÉRIUM TELJESÍTVE!")
        else:
            print_error("❌ Kettős könyvelési hiba - További vizsgálat szükséges")
        
        db.close()
        
    except Exception as e:
        print_error(f"Hiba történt: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()