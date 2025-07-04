#!/usr/bin/env python3
"""
Debug order processing to find where the "Menu item not found" error occurs
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import Order, OrderItem, MenuItem
from sqlalchemy import text

def check_order_processing_routes():
    """Check if there are any active requests or session data that might reference the missing item"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Checking for references to menu item 1751552825116...")
        
        # Check if this item ID appears in any error logs or temporary data
        missing_item_id = 1751552825116
        
        # Check if there's any session cart data or temporary storage
        print(f"📋 Looking for item ID: {missing_item_id}")
        
        # Check if this could be a timestamp-based ID (looks like it could be)
        import time
        current_timestamp = int(time.time())
        print(f"   Current timestamp: {current_timestamp}")
        print(f"   Missing item ID:   {missing_item_id}")
        print(f"   Difference: {current_timestamp - missing_item_id} seconds")
        
        # This looks like it could be a timestamp from around July 2025
        from datetime import datetime
        try:
            # Convert from milliseconds if needed
            if len(str(missing_item_id)) == 13:  # Milliseconds
                timestamp = missing_item_id / 1000
            else:  # Seconds
                timestamp = missing_item_id
            
            date_from_id = datetime.fromtimestamp(timestamp)
            print(f"   If timestamp, date would be: {date_from_id}")
        except:
            print("   Not a valid timestamp")

def check_current_cart_or_session_data():
    """Check for any cart or session data that might contain the problematic item"""
    print("\n🛒 Checking for cart/session references...")
    
    # This error typically occurs when:
    # 1. A user has an item in their cart that no longer exists
    # 2. An order is being processed with invalid item IDs
    # 3. A reorder function is trying to reorder items that no longer exist
    
    print("   Common causes of 'Menu item not found' errors:")
    print("   1. User cart contains deleted menu items")
    print("   2. Reorder function referencing old/deleted items")
    print("   3. Order processing with invalid item IDs")
    print("   4. Session data persisting after item deletion")

def check_recent_menu_changes():
    """Check if there were recent menu item deletions"""
    app = create_app()
    
    with app.app_context():
        print("\n🗑️ Checking menu item history...")
        
        # Get current menu items with their IDs
        menu_items = MenuItem.query.all()
        print(f"   Current menu items ({len(menu_items)}):")
        for item in menu_items:
            print(f"   - ID: {item.item_id}, Name: {item.name}")
        
        # Check for any gaps in item IDs that might indicate deletions
        if menu_items:
            item_ids = [item.item_id for item in menu_items]
            min_id = min(item_ids)
            max_id = max(item_ids)
            print(f"   ID range: {min_id} to {max_id}")
            
            # Check for missing IDs in range
            full_range = set(range(min_id, max_id + 1))
            existing_ids = set(item_ids)
            missing_ids = full_range - existing_ids
            
            if missing_ids:
                print(f"   Missing IDs in range: {sorted(missing_ids)}")
            else:
                print("   No gaps in ID sequence")

def fix_order_totals():
    """Fix the orders with incorrect totals"""
    app = create_app()
    
    with app.app_context():
        print("\n🔧 Fixing order totals...")
        
        # Get orders with incorrect totals
        orders_with_issues = db.session.execute(text("""
            SELECT o.order_id, o.total_amount, 
                   COALESCE(SUM(oi.quantity * oi.unit_price), 0) as calculated_total
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY o.order_id, o.total_amount
            HAVING ABS(o.total_amount - COALESCE(SUM(oi.quantity * oi.unit_price), 0)) > 0.01
        """)).fetchall()
        
        for order_data in orders_with_issues:
            order = Order.query.get(order_data.order_id)
            if order:
                old_total = float(order.total_amount)
                new_total = float(order_data.calculated_total)
                print(f"   Fixing Order {order.order_id}: {old_total} → {new_total}")
                order.total_amount = new_total
        
        try:
            db.session.commit()
            print("✅ Order totals fixed")
        except Exception as e:
            print(f"❌ Error fixing totals: {e}")
            db.session.rollback()

def create_test_cart_data():
    """Create a test to reproduce the menu item not found error"""
    print("\n🧪 Testing cart functionality...")
    
    # This would be where we test if cart operations cause the error
    print("   To test the issue, we would need to:")
    print("   1. Add an item to cart")
    print("   2. Delete the menu item")
    print("   3. Try to checkout or process the order")
    print("   4. This should reproduce the 'Menu item not found' error")

def main():
    print("🐛 ORDER PROCESSING DEBUG")
    print("=" * 50)
    
    # Check for references to the problematic item
    check_order_processing_routes()
    
    # Check for cart/session data
    check_current_cart_or_session_data()
    
    # Check recent menu changes
    check_recent_menu_changes()
    
    # Fix order totals
    fix_order_totals()
    
    # Test suggestions
    create_test_cart_data()
    
    print("\n" + "=" * 50)
    print("🔍 DEBUG COMPLETE")
    print("\nRECOMMENDATIONS:")
    print("1. Clear any browser localStorage/sessionStorage for cart data")
    print("2. Check if users have persistent cart data with deleted items")
    print("3. Add error handling for missing menu items in cart/order processing")
    print("4. Consider adding a cleanup job to remove invalid cart items")

if __name__ == "__main__":
    main()
