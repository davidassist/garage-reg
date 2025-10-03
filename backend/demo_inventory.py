"""
Demo script for Inventory Management System with Double-Entry Bookkeeping
Bemutató script a kettős könyvelés elvű raktárkezelési rendszerhez
"""

import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.services.inventory_service import InventoryService
from app.models.inventory import Warehouse, InventoryItem, StockMovement, StockAlert
from app.models.tickets import Part


def print_header(title: str):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"🏭 {title}")
    print(f"{'='*60}")


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n📋 {title}")
    print("-" * 50)


def demo_inventory_system():
    """Comprehensive demonstration of inventory management system"""
    
    print_header("GarageReg Raktárkezelési Rendszer Bemutató")
    print("Implementált funkciók:")
    print("✅ Kettős könyvelés elv (Debit/Credit)")
    print("✅ Bevételezés, Kiadás, Leltári korrekció")
    print("✅ Minimumkészlet riasztások")
    print("✅ Munkalap alkatrész felhasználás integráció")
    print("✅ Készletegyenleg és mozgás riportok")
    
    # Initialize database session
    db: Session = SessionLocal()
    inventory_service = InventoryService(db)
    
    try:
        # 1. Setup Demo Data
        print_section("1. Demo Adatok Előkészítése")
        
        # Check if demo warehouse exists
        demo_warehouse = db.query(Warehouse).filter_by(code="DEMO_WH").first()
        if not demo_warehouse:
            demo_warehouse = Warehouse(
                code="DEMO_WH",
                name="Demo Raktár",
                warehouse_type="main",
                is_active=True,
                description="Bemutató raktár a teszteléshez"
            )
            db.add(demo_warehouse)
            db.commit()
        
        print(f"✅ Raktár: {demo_warehouse.name} ({demo_warehouse.code})")
        
        # Check if demo part exists
        demo_part = db.query(Part).filter_by(part_number="DEMO_PART_001").first()
        if not demo_part:
            demo_part = Part(
                part_number="DEMO_PART_001",
                name="Demo Alkatrész",
                description="Bemutató alkatrész a teszteléshez",
                category="Elektronika",
                manufacturer="Demo Gyártó",
                unit_of_measure="db",
                is_active=True
            )
            db.add(demo_part)
            db.commit()
        
        print(f"✅ Alkatrész: {demo_part.name} ({demo_part.part_number})")
        
        # Check if inventory item exists
        demo_inventory = db.query(InventoryItem).filter_by(
            warehouse_id=demo_warehouse.id,
            part_id=demo_part.id
        ).first()
        
        if not demo_inventory:
            demo_inventory = InventoryItem(
                warehouse_id=demo_warehouse.id,
                part_id=demo_part.id,
                location_code="A-01-01",
                zone="A",
                quantity_on_hand=Decimal('0'),
                quantity_reserved=Decimal('0'),
                quantity_available=Decimal('0'),
                minimum_stock=Decimal('10'),
                reorder_point=Decimal('15'),
                reorder_quantity=Decimal('50'),
                is_active=True
            )
            db.add(demo_inventory)
            db.commit()
        
        print(f"✅ Készlet tétel: {demo_inventory.location_code}")
        
        # 2. Stock Receipt Demo (Bevételezés)
        print_section("2. Bevételezés (Stock Receipt)")
        
        print("Bevételezés: 100 db @ 1500 Ft/db")
        receipt_movement = inventory_service.receive_stock(
            inventory_item_id=demo_inventory.id,
            quantity=Decimal('100'),
            unit_cost=Decimal('1500.00'),
            reference_type="purchase_order",
            reference_id=12345,
            notes="Kezdeti készlet feltöltés",
            user_id=1
        )
        
        print(f"✅ Mozgás szám: {receipt_movement.movement_number}")
        print(f"   Debit: {receipt_movement.debit_quantity} db")
        print(f"   Credit: {receipt_movement.credit_quantity} db")
        print(f"   Készlet után: {receipt_movement.quantity_after} db")
        
        # Refresh inventory item
        db.refresh(demo_inventory)
        print(f"   Jelenlegi készlet: {demo_inventory.quantity_on_hand} db")
        print(f"   Átlagár: {demo_inventory.average_cost} Ft")
        print(f"   Készlet érték: {demo_inventory.total_value} Ft")
        
        # 3. Stock Issue Demo (Kiadás)
        print_section("3. Kiadás (Stock Issue)")
        
        print("Kiadás: 25 db (munkalap felhasználás)")
        issue_movement, part_usage = inventory_service.issue_stock(
            inventory_item_id=demo_inventory.id,
            quantity=Decimal('25'),
            work_order_id=None,  # Demo purposes - no actual work order
            reference_type="manual_issue",
            notes="Demo kiadás tesztelés céljából",
            user_id=1
        )
        
        print(f"✅ Mozgás szám: {issue_movement.movement_number}")
        print(f"   Debit: {issue_movement.debit_quantity} db")
        print(f"   Credit: {issue_movement.credit_quantity} db")
        print(f"   Készlet után: {issue_movement.quantity_after} db")
        
        # Refresh inventory item
        db.refresh(demo_inventory)
        print(f"   Jelenlegi készlet: {demo_inventory.quantity_on_hand} db")
        
        # 4. Stock Adjustment Demo (Leltári korrekció)
        print_section("4. Leltári Korrekció (Stock Adjustment)")
        
        print("Leltár eredménye: 70 db (5 db hiány)")
        adjustment_movement = inventory_service.adjust_stock(
            inventory_item_id=demo_inventory.id,
            new_quantity=Decimal('70'),
            reason="Fizikai leltár eltérése",
            notes="Cikkszámlálás során feltárt eltérés",
            user_id=1
        )
        
        print(f"✅ Mozgás szám: {adjustment_movement.movement_number}")
        print(f"   Debit: {adjustment_movement.debit_quantity} db")
        print(f"   Credit: {adjustment_movement.credit_quantity} db") 
        print(f"   Készlet után: {adjustment_movement.quantity_after} db")
        
        # 5. Low Stock Alert Demo (Minimumkészlet riasztás)
        print_section("5. Minimumkészlet Riasztás")
        
        # Issue more stock to trigger low stock alert
        print("További kiadás: 65 db (minimumkészlet alá)")
        low_stock_movement, _ = inventory_service.issue_stock(
            inventory_item_id=demo_inventory.id,
            quantity=Decimal('65'),
            reference_type="demo_issue",
            notes="Alacsony készlet riasztás tesztelése",
            user_id=1
        )
        
        # Check for alerts
        alerts = db.query(StockAlert).filter_by(
            inventory_item_id=demo_inventory.id,
            status="active"
        ).all()
        
        print(f"✅ Készlet: {demo_inventory.quantity_on_hand} db")
        print(f"   Minimumkészlet: {demo_inventory.minimum_stock} db")
        print(f"   Aktív riasztások: {len(alerts)}")
        
        for alert in alerts:
            print(f"   🚨 {alert.alert_type.upper()}: {alert.message}")
            print(f"      Súlyosság: {alert.severity}")
            print(f"      Akció: {alert.action_required}")
        
        # 6. Stock Balance Report (Készletegyenleg riport)
        print_section("6. Készletegyenleg Riport")
        
        balance_report = inventory_service.get_stock_balance_report(
            warehouse_id=demo_warehouse.id,
            include_zero_stock=True
        )
        
        print("📊 Készletegyenleg:")
        for item in balance_report:
            print(f"   {item['part_code']}: {item['quantity_on_hand']} {item['part_name']}")
            print(f"      Raktár: {item['warehouse_name']} ({item['location_code']})")
            print(f"      Elérhető: {item['quantity_available']} | Min: {item['minimum_stock']}")
            print(f"      Érték: {item['total_value']} Ft")
        
        # 7. Stock Movement Report (Készletmozgás riport)
        print_section("7. Készletmozgás Riport")
        
        movement_report = inventory_service.get_stock_movement_report(
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now(),
            warehouse_id=demo_warehouse.id
        )
        
        print("📈 Készletmozgások (utolsó 24 óra):")
        print(f"{'Mozgás szám':<15} {'Típus':<12} {'Debit':<8} {'Credit':<8} {'Egyenleg':<10}")
        print("-" * 60)
        
        for movement in movement_report:
            print(f"{movement['movement_number']:<15} "
                  f"{movement['movement_type']:<12} "
                  f"{movement['debit_quantity']:<8} "
                  f"{movement['credit_quantity']:<8} "
                  f"{movement['quantity_after']:<10}")
        
        # 8. Double-Entry Validation (Kettős könyvelés ellenőrzés)
        print_section("8. Kettős Könyvelés Ellenőrzés")
        
        validation = inventory_service.validate_double_entry_balance()
        
        print("🔍 Könyvviteli egyenleg ellenőrzés:")
        print(f"   Összes Debit: {validation['total_debits']}")
        print(f"   Összes Credit: {validation['total_credits']}")
        print(f"   Számított egyenleg: {validation['calculated_balance']}")
        print(f"   Tényleges készlet: {validation['actual_stock']}")
        print(f"   Eltérés: {validation['variance']}")
        print(f"   Egyensúly: {'✅ RENDBEN' if validation['is_balanced'] else '❌ ELTÉRÉS'}")
        
        # 9. System Summary
        print_section("9. Rendszer Összefoglalás")
        
        total_movements = db.query(StockMovement).count()
        total_alerts = db.query(StockAlert).filter_by(status="active").count()
        
        print("🎉 Raktárkezelési rendszer állapot:")
        print(f"   📦 Összes raktár: {db.query(Warehouse).count()}")
        print(f"   🏷️  Készlet tételek: {db.query(InventoryItem).count()}")
        print(f"   📊 Készletmozgások: {total_movements}")
        print(f"   🚨 Aktív riasztások: {total_alerts}")
        print(f"   ✅ Kettős könyvelés: {'Balanced' if validation['is_balanced'] else 'Unbalanced'}")
        
        print_header("Raktárkezelési Rendszer Sikeresen Demonstrálva! 🏭")
        
    except Exception as e:
        print(f"❌ Hiba történt: {e}")
        db.rollback()
    
    finally:
        db.close()


if __name__ == "__main__":
    demo_inventory_system()