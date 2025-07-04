#!/usr/bin/env python3
"""
Check database schema and fix the order integrity issue
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import Order, OrderItem, MenuItem
from sqlalchemy import text, inspect

def check_database_schema():
    """Check the database schema to understand table structure"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Checking database schema...")
        
        inspector = inspect(db.engine)
        
        # Check orders table
        print("\n📊 Orders table columns:")
        orders_columns = inspector.get_columns('orders')
        for col in orders_columns:
            print(f"   - {col['name']}: {col['type']}")
        
        # Check order_items table
        print("\n📊 Order Items table columns:")
        order_items_columns = inspector.get_columns('order_items')
        for col in order_items_columns:
            print(f"   - {col['name']}: {col['type']}")
        
        # Check menu_items table
        print("\n📊 Menu Items table columns:")
        menu_items_columns = inspector.get_columns('menu_items')
        for col in menu_items_columns:
            print(f"   - {col['name']}: {col['type']}")
        
        return orders_columns, order_items_columns, menu_items_columns

def check_orphaned_order_items_fixed():
    """Check for order items that reference non-existent menu items with correct column names"""
    app = create_app()
    
    with app.app_context():
        print("\n🔍 Checking for orphaned order items...")
        
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
    """Fix orphaned order items by removing them"""
    app = create_app()
    
    with app.app_context():
        print("\n🔧 Fixing orphaned order items...")
        
        # Find orphaned order items
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
        
        # Remove orphaned order items
        for item in orphaned_items:
            order_item = OrderItem.query.get(item.order_item_id)
            if order_item:
                print(f"   Removing order item {item.order_item_id} (missing menu item {item.item_id})")
                db.session.delete(order_item)
        
        # Commit changes
        try:
            db.session.commit()
            print("✅ Successfully removed orphaned order items")
            return True
        except Exception as e:
            print(f"❌ Error fixing orphaned order items: {e}")
            db.session.rollback()
            return False

def verify_orders_integrity_fixed():
    """Verify that all orders have valid items using correct column names"""
    app = create_app()
    
    with app.app_context():
        print("\n🔍 Verifying order integrity...")
        
        # Check for orders with no items
        orders_without_items = db.session.execute(text("""
            SELECT o.order_id, o.total_amount
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            WHERE oi.order_id IS NULL
        """)).fetchall()
        
        if orders_without_items:
            print(f"⚠️ Found {len(orders_without_items)} orders without items:")
            for order in orders_without_items:
                print(f"   - Order {order.order_id}")
        else:
            print("✅ All orders have items")
        
        # Check for orders with invalid total amounts
        orders_with_invalid_totals = db.session.execute(text("""
            SELECT o.order_id, o.total_amount, 
                   COALESCE(SUM(oi.quantity * oi.unit_price), 0) as calculated_total
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY o.order_id, o.total_amount
            HAVING ABS(o.total_amount - COALESCE(SUM(oi.quantity * oi.unit_price), 0)) > 0.01
        """)).fetchall()
        
        if orders_with_invalid_totals:
            print(f"⚠️ Found {len(orders_with_invalid_totals)} orders with incorrect totals:")
            for order in orders_with_invalid_totals:
                print(f"   - Order {order.order_id}: Stored: {order.total_amount}, Calculated: {order.calculated_total}")
        else:
            print("✅ All order totals are correct")

def count_current_data():
    """Count current data in key tables"""
    app = create_app()
    
    with app.app_context():
        print("\n📊 Current data counts:")
        
        orders_count = Order.query.count()
        print(f"   - Orders: {orders_count}")
        
        order_items_count = OrderItem.query.count()
        print(f"   - Order Items: {order_items_count}")
        
        menu_items_count = MenuItem.query.count()
        print(f"   - Menu Items: {menu_items_count}")

def main():
    print("🛠️ ORDER DATA INTEGRITY FIX (UPDATED)")
    print("=" * 50)
    
    # Check database schema first
    check_database_schema()
    
    # Count current data
    count_current_data()
    
    # Check specific problematic item
    print("\n1. Checking specific menu item 1751552825116:")
    check_specific_menu_item(1751552825116)
    
    # Check for orphaned order items
    print("\n2. Checking for orphaned order items:")
    orphaned_items = check_orphaned_order_items_fixed()
    
    if orphaned_items:
        print("\n3. Fixing orphaned order items:")
        success = fix_orphaned_order_items()
        
        if success:
            print("\n4. Re-checking after fix:")
            check_orphaned_order_items_fixed()
    
    # Verify overall order integrity
    print("\n5. Verifying order integrity:")
    verify_orders_integrity_fixed()
    
    print("\n" + "=" * 50)
    print("✅ Order data integrity check complete!")

if __name__ == "__main__":
    main()
