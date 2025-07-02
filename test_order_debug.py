#!/usr/bin/env python3
"""
Simple test to debug the reorder issue
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.models import Order, OrderItem, MenuItem, Category
from flask import session

def test_order_loading():
    """Test loading orders and items"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Testing order loading...")
        
        # Get a sample order
        order = Order.query.first()
        if not order:
            print("❌ No orders found in database")
            return
        
        print(f"✅ Found order {order.order_id}")
        print(f"   Status: {order.status}")
        print(f"   User ID: {order.user_id}")
        
        # Get order items
        order_items = order.order_items.all()
        print(f"✅ Found {len(order_items)} order items")
        
        for item in order_items:
            print(f"   Item ID: {item.item_id}, Quantity: {item.quantity}")
            
            # Test loading menu item
            menu_item = MenuItem.query.get(item.item_id)
            if menu_item:
                print(f"     Menu item: {menu_item.name}")
                print(f"     Status: {menu_item.status}")
                print(f"     Category ID: {menu_item.category_id}")
                
                # Test loading with category
                menu_item_with_cat = MenuItem.query.options(db.joinedload(MenuItem.category)).get(item.item_id)
                if menu_item_with_cat and menu_item_with_cat.category:
                    print(f"     Category: {menu_item_with_cat.category.name}")
                else:
                    print(f"     ❌ Could not load category")
            else:
                print(f"     ❌ Menu item not found")

def test_session_cart():
    """Test session-based cart functionality"""
    app = create_app()
    
    with app.test_request_context():
        print("\n🔍 Testing session cart...")
        
        # Initialize session cart
        session['cart'] = []
        
        # Test adding item to cart
        test_item = {
            'id': 1,
            'name': 'Test Item',
            'price': 25.0,
            'quantity': 2,
            'image': 'test.jpg',
            'specialInstructions': '',
            'category': 'Test Category'
        }
        
        session['cart'].append(test_item)
        session.modified = True
        
        print(f"✅ Added item to cart: {test_item}")
        print(f"   Cart length: {len(session['cart'])}")

if __name__ == "__main__":
    # Import db after setting up path
    from app.models import db
    
    test_order_loading()
    test_session_cart()
    
    print("\n✅ Basic tests completed")
