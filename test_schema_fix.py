#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, User, MenuItem, Order, OrderItem, Table
from app.extensions import db as db_ext

def test_order_creation():
    """Test if we can create orders without schema errors"""
    app = create_app()
    
    with app.app_context():
        print("🧪 Testing order creation...")
        
        # Get a customer
        customer = User.query.filter_by(role='customer').first()
        if not customer:
            print("❌ No customer found")
            return False
            
        # Get a menu item
        menu_item = MenuItem.query.filter_by(status='available').first()
        if not menu_item:
            print("❌ No available menu items found")
            return False
            
        # Get a table
        table = Table.query.first()
        if not table:
            print("❌ No tables found")
            return False
            
        print(f"✅ Found customer: {customer.name}")
        print(f"✅ Found menu item: {menu_item.name} (ID: {menu_item.item_id})")
        print(f"✅ Found table: {table.table_number}")
        
        try:
            # Create order
            order = Order(
                customer_id=customer.user_id,
                table_id=table.table_id,
                status='new',
                order_type='dine_in',
                total_amount=0
            )
            db.session.add(order)
            db.session.flush()  # Get order_id
            
            print(f"✅ Created order: {order.order_id}")
            
            # Create order item using item_id (not menu_item_id)
            order_item = OrderItem(
                order_id=order.order_id,
                item_id=menu_item.item_id,  # This should match the database schema
                quantity=2,
                note='Test item',
                unit_price=menu_item.price
            )
            db.session.add(order_item)
            
            # Update total
            order.total_amount = menu_item.price * 2
            
            db.session.commit()
            print(f"✅ Successfully created order item with item_id: {menu_item.item_id}")
            print(f"✅ Order total: ${order.total_amount}")
            
            # Verify the relationship works
            print(f"✅ Order has {len(list(order.order_items))} items")
            print(f"✅ Menu item has {len(list(menu_item.order_items))} order items")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating order: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = test_order_creation()
    if success:
        print("\n🎉 Order creation test PASSED!")
    else:
        print("\n💥 Order creation test FAILED!")
        sys.exit(1)
