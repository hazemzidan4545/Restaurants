#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_schema_compatibility():
    """Test if the model definitions are compatible with the database schema"""
    
    try:
        from app import create_app
        from app.models import db, User, MenuItem, Order, OrderItem, Table
        
        app = create_app()
        
        with app.app_context():
            print("🔍 Testing database schema compatibility...")
            
            # Test basic queries to ensure models work
            try:
                user_count = User.query.count()
                print(f"✅ Users table accessible: {user_count} users")
            except Exception as e:
                print(f"❌ Users table error: {e}")
                return False
                
            try:
                menu_count = MenuItem.query.count()
                print(f"✅ Menu items table accessible: {menu_count} items")
            except Exception as e:
                print(f"❌ Menu items table error: {e}")
                return False
                
            try:
                order_count = Order.query.count()
                print(f"✅ Orders table accessible: {order_count} orders")
            except Exception as e:
                print(f"❌ Orders table error: {e}")
                return False
                
            try:
                order_item_count = OrderItem.query.count()
                print(f"✅ Order items table accessible: {order_item_count} order items")
            except Exception as e:
                print(f"❌ Order items table error: {e}")
                return False
            
            # Test if we can query relationships
            try:
                # Test if the relationship works both ways
                if menu_count > 0:
                    menu_item = MenuItem.query.first()
                    order_items_for_menu = menu_item.order_items.count()
                    print(f"✅ MenuItem->OrderItem relationship works: {order_items_for_menu} order items")
                    
                if order_item_count > 0:
                    order_item = OrderItem.query.first()
                    menu_item_name = order_item.menu_item.name if order_item.menu_item else "None"
                    print(f"✅ OrderItem->MenuItem relationship works: menu item '{menu_item_name}'")
                    
            except Exception as e:
                print(f"❌ Relationship test failed: {e}")
                return False
            
            print("🎉 All schema compatibility tests passed!")
            return True
            
    except Exception as e:
        print(f"❌ Failed to initialize app or models: {e}")
        return False

if __name__ == "__main__":
    success = test_schema_compatibility()
    if success:
        print("\n✅ Schema is compatible - order creation should work now!")
    else:
        print("\n❌ Schema compatibility issues remain")
