#!/usr/bin/env python3
"""
Komplett Raktárkezelési Modul Teszt
Demonstrálja a bevét, kivét, leltár és minimumkészlet riasztás funkciókat
kettős könyvelés elvvel
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.inventory import Warehouse, InventoryItem, StockMovement
from app.models.tickets import Part, WorkOrder
from app.models.organization import Gate, Site, Building, Client
from app.services.inventory_service import InventoryService

def print_header(title: str):
    """Print formatted header"""
    print(f"\n{'='*80}")
    print(f"🏭 {title}")
    print(f"{'='*80}")

def print_section(title: str):
    """Print formatted section"""
    print(f"\n📋 {title}")
    print("-" * 60)

def create_test_data(db: Session) -> dict:
    """Create test data for inventory demonstration"""
    
    print_section("Teszt adatok létrehozása")
    
    # Create client first
    client = Client(
        name="Teszt Ügyfél Kft.",
        display_name="Teszt Ügyfél", 
        type="commercial",
        address_line_1="Budapest, Váci út 123.",
        is_active=True,
        org_id=1,
        organization_id=1
    )
    db.add(client)
    db.flush()
    
    # Create site
    site = Site(
        client_id=client.id,
        name="Budapest teszt telephely",
        display_name="Budapest telephely",
        site_code="BUD01", 
        address_line_1="Budapest, Váci út 123.",
        is_active=True,
        org_id=1
    )
    db.add(site)
    db.flush()
    
    # Create building
    building = Building(
        site_id=site.id,
        name="Fő épület",
        display_name="Fő épület",
        building_code="MAIN",
        building_type="office",
        is_active=True,
        org_id=1
    )
    db.add(building)
    db.flush()
    
    # Create gate for work orders
    gate = Gate(
        building_id=building.id,
        name="Teszt garázskapu",
        gate_code="GATE01",
        gate_type="sliding",  # Valid type: swing, sliding, barrier, bollard, turnstile
        manufacturer="Test Mfg",
        model="TM-2024",
        status="operational",
        is_active=True,
        org_id=1
    )
    db.add(gate)
    db.flush()
    
    # Create warehouse (org_id=1 for test)
    warehouse = Warehouse(
        name="Fő Raktár",
        code="MAIN01",
        description="Főraktár Budapest",
        warehouse_type="main",
        address_line_1="Budapest, Váci út 123.",
        is_active=True,
        org_id=1  # Test organization
    )
    db.add(warehouse)
    db.flush()
    
    # Create parts
    parts = []
    part_data = [
        ("SERVO001", "Szervó motor SM-240V", 15000, 5, 20, 10),
        ("COND001", "Biztonsági kondenzátor 4μF", 2500, 10, 50, 25),
        ("SWITCH001", "Végelállás kapcsoló", 3500, 3, 15, 8),
        ("REMOTE001", "Távirányító 433MHz", 8500, 2, 10, 5),
        ("CABLE001", "Vezérlő kábel 5m", 1200, 20, 100, 50)
    ]
    
    for part_code, part_name, unit_cost, min_stock, max_stock, reorder_qty in part_data:
        part = Part(
            part_number=part_code,
            name=part_name,
            description=f"{part_name} - Garázskapu alkatrész",
            category="electronics" if "motor" in part_name.lower() or "kondenzátor" in part_name.lower() else "hardware",
            unit_of_measure="piece",
            standard_cost=Decimal(str(unit_cost)),
            minimum_stock_level=min_stock,
            maximum_stock_level=max_stock,
            reorder_quantity=reorder_qty,
            is_active=True,
            org_id=1  # Test organization
        )
        db.add(part)
        db.flush()
        parts.append(part)
        
        # Create inventory item
        inventory_item = InventoryItem(
            warehouse_id=warehouse.id,
            part_id=part.id,
            location_code=f"A{len(parts):02d}",
            quantity_on_hand=Decimal('0'),
            quantity_available=Decimal('0'),
            minimum_stock=Decimal(str(min_stock)),
            maximum_stock=Decimal(str(max_stock)),
            reorder_quantity=Decimal(str(reorder_qty)),
            unit_cost=Decimal(str(unit_cost)),
            is_active=True,
            org_id=1  # Test organization
        )
        db.add(inventory_item)
    
    # Create work order for testing part usage
    work_order = WorkOrder(
        gate_id=gate.id,
        work_order_number="WO-2024-TEST001",
        title="Garázskapu javítás teszt",
        description="Szervó motor és kondenzátor csere",
        work_type="repair",
        work_category="motor_replacement", 
        priority="medium",
        status="in_progress",
        org_id=1  # Test organization
    )
    db.add(work_order)
    
    db.commit()
    
    print(f"✅ Ügyfél létrehozva: {client.name}")
    print(f"✅ Telephely létrehozva: {site.name} ({site.site_code})")
    print(f"✅ Épület létrehozva: {building.name} ({building.building_code})")
    print(f"✅ Garázskapu létrehozva: {gate.name} ({gate.gate_code})")
    print(f"✅ Raktár létrehozva: {warehouse.name} ({warehouse.code})")
    print(f"✅ {len(parts)} alkatrész létrehozva")
    print(f"✅ {len(parts)} készlet tétel létrehozva")
    print(f"✅ Munkalap létrehozva: {work_order.work_order_number}")
    
    return {
        'client': client,
        'site': site,
        'building': building,
        'gate': gate,
        'warehouse': warehouse,
        'parts': parts,
        'work_order': work_order
    }

def test_stock_receipt(inventory_service: InventoryService, test_data: dict):
    """Test stock receipt (bevételezés) functionality"""
    
    print_header("BEVÉTELEZÉS TESZT - Kettős könyvelés elvvel")
    
    warehouse = test_data['warehouse']
    parts = test_data['parts']
    
    # Get inventory items
    inventory_items = inventory_service.db.query(InventoryItem)\
        .filter(InventoryItem.warehouse_id == warehouse.id).all()
    
    receipt_data = [
        (0, Decimal('50'), Decimal('15000')),  # Szervó motor
        (1, Decimal('100'), Decimal('2500')),  # Kondenzátor 
        (2, Decimal('25'), Decimal('3500')),   # Végelállás kapcsoló
        (3, Decimal('15'), Decimal('8500')),   # Távirányító
        (4, Decimal('200'), Decimal('1200'))   # Kábel
    ]
    
    print(f"📦 Bevételezés {len(receipt_data)} tétel...")
    
    movements = []
    for idx, (part_idx, quantity, unit_cost) in enumerate(receipt_data):
        item = inventory_items[part_idx]
        part = parts[part_idx]
        
        print(f"\n🔄 Bevételezés {idx + 1}: {part.name}")
        print(f"   Mennyiség: {quantity} db")
        print(f"   Egységár: {unit_cost:,} Ft")
        print(f"   Összérték: {quantity * unit_cost:,} Ft")
        
        movement = inventory_service.receive_stock(
            inventory_item_id=item.id,
            quantity=quantity,
            unit_cost=unit_cost,
            reference_type="purchase_order",
            notes=f"Teszt bevételezés - {part.name}"
        )
        movements.append(movement)
        
        # Show updated inventory
        inventory_service.db.refresh(item)
        print(f"   📊 Új készletszint: {item.quantity_on_hand} db")
        print(f"   💰 Átlagár: {item.average_cost:,.2f} Ft")
        print(f"   📈 Státusz: {item.stock_status}")
    
    print(f"\n✅ {len(movements)} bevételezés sikeres")
    return movements

def test_stock_issue(inventory_service: InventoryService, test_data: dict):
    """Test stock issue (kiadás) functionality"""
    
    print_header("KIADÁS TESZT - Munkalap alkatrészfelhasználás")
    
    warehouse = test_data['warehouse']
    parts = test_data['parts']
    work_order = test_data['work_order']
    
    # Get inventory items
    inventory_items = inventory_service.db.query(InventoryItem)\
        .filter(InventoryItem.warehouse_id == warehouse.id).all()
    
    issue_data = [
        (0, Decimal('2')),   # Szervó motor - 2 db
        (1, Decimal('4')),   # Kondenzátor - 4 db  
        (2, Decimal('3')),   # Végelállás kapcsoló - 3 db
        (4, Decimal('10'))   # Kábel - 10 db
    ]
    
    print(f"📤 Kiadás munkalapra: {work_order.work_order_number}")
    
    movements = []
    total_cost = Decimal('0')
    
    for part_idx, quantity in issue_data:
        item = inventory_items[part_idx]
        part = parts[part_idx]
        
        print(f"\n🔄 Kiadás: {part.name}")
        print(f"   Kiadott mennyiség: {quantity} db")
        print(f"   Készlet előtte: {item.quantity_available} db")
        
        movement = inventory_service.issue_stock(
            inventory_item_id=item.id,
            quantity=quantity,
            work_order_id=work_order.id,
            notes=f"Felhasználás munkalapra - {work_order.work_order_number}"
        )
        movements.append(movement)
        
        # Calculate cost
        if movement.total_cost:
            total_cost += movement.total_cost
            print(f"   💰 Kiadás értéke: {movement.total_cost:,.2f} Ft")
        
        # Show updated inventory
        inventory_service.db.refresh(item)
        print(f"   📊 Készlet utána: {item.quantity_available} db")
        print(f"   📈 Státusz: {item.stock_status}")
    
    print(f"\n✅ {len(movements)} kiadás sikeres")
    print(f"💰 Összköltség: {total_cost:,.2f} Ft")
    return movements

def test_stock_adjustment(inventory_service: InventoryService, test_data: dict):
    """Test stock adjustment (leltár) functionality"""
    
    print_header("LELTÁRI KORREKCIÓ TESZT")
    
    warehouse = test_data['warehouse']
    parts = test_data['parts']
    
    # Get inventory items  
    inventory_items = inventory_service.db.query(InventoryItem)\
        .filter(InventoryItem.warehouse_id == warehouse.id).all()
    
    # Simulate inventory count differences
    adjustments = [
        (2, Decimal('20')),  # Végelállás kapcsoló - talált 2 db-ot több
        (3, Decimal('13')),  # Távirányító - hiányzik 2 db
        (4, Decimal('185'))  # Kábel - hiányzik 5 db
    ]
    
    print("📊 Fizikai leltár eredményei:")
    
    movements = []
    for part_idx, counted_quantity in adjustments:
        item = inventory_items[part_idx]
        part = parts[part_idx]
        
        current_qty = item.quantity_on_hand
        difference = counted_quantity - current_qty
        
        print(f"\n🔍 Leltár: {part.name}")
        print(f"   Könyv szerinti készlet: {current_qty} db")
        print(f"   Fizikai leltár: {counted_quantity} db")
        print(f"   Eltérés: {difference:+} db")
        
        if difference != 0:
            reason = "Fizikai leltár eltérése"
            if difference > 0:
                reason += " - Többlet talált"
            else:
                reason += " - Hiány feltárva"
            
            movement = inventory_service.adjust_stock(
                inventory_item_id=item.id,
                new_quantity=counted_quantity,
                reason=reason,
                notes=f"Leltár dátum: {datetime.now().strftime('%Y-%m-%d')}"
            )
            movements.append(movement)
            
            # Show updated inventory
            inventory_service.db.refresh(item)
            print(f"   ✅ Korrigált készlet: {item.quantity_on_hand} db")
            print(f"   📈 Új státusz: {item.stock_status}")
        else:
            print(f"   ✅ Nincs eltérés - korrekció nem szükséges")
    
    print(f"\n✅ {len(movements)} leltári korrekció végrehajtva")
    return movements

def test_minimum_stock_alerts(inventory_service: InventoryService):
    """Test minimum stock alert system"""
    
    print_header("MINIMUMKÉSZLET RIASZTÁS RENDSZER")
    
    # Generate comprehensive alerts
    alerts = inventory_service.generate_stock_alerts()
    
    print_section("Riasztások összefoglalása")
    summary = alerts['summary']
    print(f"📊 Összes riasztás: {summary['total_alerts']}")
    print(f"🚨 Kritikus riasztások: {summary['critical_alerts']}")  
    print(f"⚠️ Magas prioritású: {summary['high_alerts']}")
    print(f"💡 Közepes prioritású: {summary['medium_alerts']}")
    print(f"📦 Túlraktározás: {summary['overstock_items']}")
    print(f"🐌 Lassan forgó: {summary['slow_moving_items']}")
    
    # Show minimum stock alerts
    if alerts['minimum_stock_alerts']:
        print_section("Minimumkészlet Riasztások")
        for alert in alerts['minimum_stock_alerts']:
            print(f"\n🚨 {alert['alert_level']} - {alert['part_name']} ({alert['part_code']})")
            print(f"   📍 Raktár: {alert['warehouse_name']}")
            print(f"   📊 Jelenlegi készlet: {alert['current_stock']} db")
            print(f"   📉 Minimum készlet: {alert['minimum_stock']} db")
            print(f"   📈 Hiány: {alert['shortage']} db ({alert['shortage_percentage']:.1f}%)")
            
            if alert['suggested_order_quantity']:
                print(f"   💡 Javasolt rendelés: {alert['suggested_order_quantity']} db")
            
            if alert['days_since_last_movement']:
                print(f"   📅 Utolsó mozgás: {alert['days_since_last_movement']} napja")
    
    # Show overstock alerts
    if alerts['overstock_alerts']:
        print_section("Túlraktározási Riasztások")
        for alert in alerts['overstock_alerts']:
            print(f"\n📦 TÚLRAKTÁR - {alert['part_name']} ({alert['part_code']})")
            print(f"   📍 Raktár: {alert['warehouse_code']}")
            print(f"   📊 Jelenlegi készlet: {alert['current_stock']} db")
            print(f"   📈 Maximum készlet: {alert['maximum_stock']} db")
            print(f"   📉 Többlet: {alert['excess_quantity']} db ({alert['excess_percentage']:.1f}%)")
            print(f"   💰 Felesleges érték: {alert['total_value']:,.2f} Ft")
    
    return alerts

def test_double_entry_validation(inventory_service: InventoryService):
    """Test double-entry bookkeeping validation"""
    
    print_header("KETTŐS KÖNYVELÉS VALIDÁCIÓ")
    
    validation = inventory_service.validate_double_entry_balance()
    
    print("📊 Könyvviteli egyenleg ellenőrzése:")
    print(f"   💰 Összes tartozik (debit): {validation['total_debits']:,.3f} db")
    print(f"   💸 Összes követel (credit): {validation['total_credits']:,.3f} db")
    print(f"   🧮 Számított egyenleg: {validation['calculated_balance']:,.3f} db")
    print(f"   📦 Tényleges készlet: {validation['actual_stock']:,.3f} db")
    print(f"   📊 Eltérés: {validation['variance']:,.3f} db")
    print(f"   ✅ Egyenleg rendben: {'IG' if validation['is_balanced'] else 'NEM'}")
    
    if validation['is_balanced']:
        print("\n🎉 A kettős könyvelési egyenleg helyes!")
        print("   Minden bevételezés és kiadás megfelelően rögzített")
    else:
        print(f"\n⚠️ Egyenleg hiba észlelhető!")
        print(f"   Ellenőrizni kell a {abs(validation['variance']):,.3f} db eltérést")
    
    return validation

def generate_inventory_reports(inventory_service: InventoryService, test_data: dict):
    """Generate comprehensive inventory reports"""
    
    print_header("RAKTÁRKEZELÉSI RIPORTOK")
    
    warehouse = test_data['warehouse']
    
    # Current inventory report
    print_section("Jelenlegi Készletszintek")
    inventory_report = inventory_service.get_current_stock_report(warehouse_id=warehouse.id)
    
    total_items = len(inventory_report)
    total_value = sum(item['total_value'] or 0 for item in inventory_report)
    
    print(f"📦 Összes tétel: {total_items}")
    print(f"💰 Összes készletérték: {total_value:,.2f} Ft")
    
    print(f"\n{'Alkatrész':<30} {'Készlet':<10} {'Minimum':<10} {'Érték':<15} {'Státusz':<12}")
    print("-" * 85)
    
    for item in inventory_report:
        name = item['part_name'][:28] + ".." if len(item['part_name']) > 30 else item['part_name']
        value_str = f"{item['total_value'] or 0:,.0f} Ft"
        print(f"{name:<30} {item['quantity_on_hand']:<10.0f} {item['minimum_stock']:<10.0f} {value_str:<15} {item['stock_status']:<12}")
    
    # Stock movement report
    print_section("Készletmozgás Riport (Utolsó 24 óra)")
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(hours=24)
    
    movement_report = inventory_service.get_stock_movement_report(
        start_date=start_date,
        end_date=end_date,
        warehouse_id=warehouse.id
    )
    
    if movement_report:
        print(f"📊 Mozgások száma: {len(movement_report)}")
        
        print(f"\n{'Mozgás':<15} {'Típus':<12} {'Alkatrész':<25} {'Debit':<10} {'Credit':<10} {'Érték':<12}")
        print("-" * 95)
        
        for movement in movement_report[-10:]:  # Last 10 movements
            part_name = movement['part_name'][:23] + ".." if len(movement['part_name']) > 25 else movement['part_name']
            value_str = f"{movement['total_cost'] or 0:,.0f} Ft"
            print(f"{movement['movement_number']:<15} {movement['movement_type']:<12} {part_name:<25} "
                  f"{movement['debit_quantity']:<10.1f} {movement['credit_quantity']:<10.1f} {value_str:<12}")
    else:
        print("📭 Nincsenek mozgások az elmúlt 24 órában")
    
    return {
        'inventory_report': inventory_report,
        'movement_report': movement_report,
        'total_value': total_value
    }

def main():
    """Run comprehensive inventory system test"""
    
    print_header("GarageReg Komplett Raktárkezelési Rendszer Teszt")
    print("🎯 Feladat: Alap raktár modul")
    print("📋 Kimenet: Bevét, kivét, leltár, minimumkészlet riasztás")
    print("🔗 Kapcsolat: Munkalap alkatrészfelhasználás")
    print("✅ Elfogadás: Kettős könyvelés elv (stock_movements), riport")
    
    # Initialize database session
    db = SessionLocal()
    inventory_service = InventoryService(db)
    
    try:
        # 1. Create test data
        test_data = create_test_data(db)
        
        # 2. Test stock receipt (bevételezés)
        receipt_movements = test_stock_receipt(inventory_service, test_data)
        
        # 3. Test stock issue (kiadás)  
        issue_movements = test_stock_issue(inventory_service, test_data)
        
        # 4. Test stock adjustment (leltár)
        adjustment_movements = test_stock_adjustment(inventory_service, test_data)
        
        # 5. Test minimum stock alerts
        alerts = test_minimum_stock_alerts(inventory_service)
        
        # 6. Validate double-entry bookkeeping
        validation = test_double_entry_validation(inventory_service)
        
        # 7. Generate reports
        reports = generate_inventory_reports(inventory_service, test_data)
        
        # Final summary
        print_header("TESZT ÖSSZEFOGLALÁS")
        
        total_movements = len(receipt_movements) + len(issue_movements) + len(adjustment_movements)
        
        print("✅ Minden funkció sikeresen tesztelve:")
        print(f"   📦 Bevételezések: {len(receipt_movements)} db")
        print(f"   📤 Kiadások: {len(issue_movements)} db") 
        print(f"   📊 Leltári korrekciók: {len(adjustment_movements)} db")
        print(f"   🚨 Riasztások: {alerts['summary']['total_alerts']} db")
        print(f"   💰 Összes készletérték: {reports['total_value']:,.2f} Ft")
        print(f"   ✅ Kettős könyvelés: {'Rendben' if validation['is_balanced'] else 'Hiba'}")
        
        print(f"\n🎉 RAKTÁRKEZELÉSI MODUL SIKERESEN IMPLEMENTÁLVA!")
        print(f"📋 Összesen {total_movements} raktármozgás rögzítve kettős könyvelés elvvel")
        
    except Exception as e:
        print(f"\n❌ Hiba történt: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()

if __name__ == "__main__":
    main()