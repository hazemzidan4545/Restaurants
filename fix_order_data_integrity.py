#!/usr/bin/env python3
"""
Fix order failure: Menu item 1751552825116 not found
This script will:
1. Check for orphaned order items that reference non-existent menu items
2. Fix or remove these problematic order items
3. Ensure data consistency
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import Order, OrderItem, MenuItem
from sqlalchemy import text

def check_orphaned_order_items():
    """Check for order items that reference non-existent menu items"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Checking for orphaned order items...")
        
        # Find order items that reference non-existent menu items
        orphaned_items = db.session.execute(text("""
            SELECT oi.order_item_id, oi.order_id, oi.item_id, oi.quantity, oi.unit_price
            FROM order_items oi
            LEFT JOIN menu_items mi ON oi.item_id = mi.item_id
            WHERE mi.item_id IS NULL
        """)).fetchall()
        
        if orphaned_items:
            print(f"❌ Found {len(orphaned_items)} orphaned order items:")
            for item in orphaned_items:
                print(f"   - Order Item ID: {item.order_item_id}, Order ID: {item.order_id}, Missing Menu Item ID: {item.item_id}")
            return orphaned_items
        else:
            print("✅ No orphaned order items found")
            return []

def check_specific_menu_item(item_id):
    """Check if a specific menu item exists"""
    app = create_app()
    
    with app.app_context():
        menu_item = MenuItem.query.filter_by(item_id=item_id).first()
        if menu_item:
            print(f"✅ Menu item {item_id} exists: {menu_item.name}")
            return True
        else:
            print(f"❌ Menu item {item_id} not found")
            return False

def fix_orphaned_order_items():
    """Fix orphaned order items by either removing them or replacing with a default item"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Fixing orphaned order items...")
        
        # Get a default menu item to replace orphaned items
        default_item = MenuItem.query.first()
        if not default_item:
            print("❌ No menu items available to use as replacement")
            return False
        
        print(f"📝 Using default item: {default_item.name} (ID: {default_item.item_id})")
        
        # Find and fix orphaned order items
        orphaned_items = db.session.execute(text("""
            SELECT oi.order_item_id, oi.order_id, oi.item_id, oi.quantity, oi.unit_price
            FROM order_items oi
            LEFT JOIN menu_items mi ON oi.item_id = mi.item_id
            WHERE mi.item_id IS NULL
        """)).fetchall()
        
        if not orphaned_items:
            print("✅ No orphaned order items to fix")
            return True
        
        print(f"🔧 Fixing {len(orphaned_items)} orphaned order items...")
        
        # Option 1: Remove orphaned order items
        print("Removing orphaned order items...")
        for item in orphaned_items:
            order_item = OrderItem.query.get(item.order_item_id)
            if order_item:
                print(f"   Removing order item {item.order_item_id} (missing menu item {item.item_id})")
                db.session.delete(order_item)
        
        # Commit changes
        try:
            db.session.commit()
            print("✅ Successfully fixed orphaned order items")
            return True
        except Exception as e:
            print(f"❌ Error fixing orphaned order items: {e}")
            db.session.rollback()
            return False

def verify_orders_integrity():
    """Verify that all orders have valid items"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Verifying order integrity...")
        
        # Check for orders with no items
        orders_without_items = db.session.execute(text("""
            SELECT o.order_id, o.order_number, o.total_amount
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            WHERE oi.order_id IS NULL
        """)).fetchall()
        
        if orders_without_items:
            print(f"⚠️ Found {len(orders_without_items)} orders without items:")
            for order in orders_without_items:
                print(f"   - Order {order.order_id} ({order.order_number})")
        else:
            print("✅ All orders have items")
        
        # Check for orders with invalid total amounts
        orders_with_invalid_totals = db.session.execute(text("""
            SELECT o.order_id, o.order_number, o.total_amount, 
                   COALESCE(SUM(oi.quantity * oi.unit_price), 0) as calculated_total
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY o.order_id, o.order_number, o.total_amount
            HAVING ABS(o.total_amount - COALESCE(SUM(oi.quantity * oi.unit_price), 0)) > 0.01
        """)).fetchall()
        
        if orders_with_invalid_totals:
            print(f"⚠️ Found {len(orders_with_invalid_totals)} orders with incorrect totals:")
            for order in orders_with_invalid_totals:
                print(f"   - Order {order.order_id}: Stored: {order.total_amount}, Calculated: {order.calculated_total}")
        else:
            print("✅ All order totals are correct")

def main():
    print("🛠️ ORDER DATA INTEGRITY FIX")
    print("=" * 50)
    
    # Check specific problematic item
    print("\n1. Checking specific menu item 1751552825116:")
    check_specific_menu_item(1751552825116)
    
    # Check for orphaned order items
    print("\n2. Checking for orphaned order items:")
    orphaned_items = check_orphaned_order_items()
    
    if orphaned_items:
        print("\n3. Fixing orphaned order items:")
        success = fix_orphaned_order_items()
        
        if success:
            print("\n4. Re-checking after fix:")
            check_orphaned_order_items()
    
    # Verify overall order integrity
    print("\n5. Verifying order integrity:")
    verify_orders_integrity()
    
    print("\n" + "=" * 50)
    print("✅ Order data integrity check complete!")

if __name__ == "__main__":
    main()
