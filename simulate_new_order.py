#!/usr/bin/env python3
"""
Script to simulate new orders for testing the notification system
"""

import random
from datetime import datetime
from app import create_app
from app.extensions import db
from app.models import User, MenuItem, Order, OrderItem, Table

def create_new_order():
    """Create a new order to test notifications"""
    app = create_app()
    
    with app.app_context():
        # Get a random customer
        customers = User.query.filter_by(role='customer').all()
        if not customers:
            print("No customers found. Please run generate_order_data.py first.")
            return
        
        customer = random.choice(customers)
        
        # Get a random table
        tables = Table.query.all()
        if not tables:
            print("No tables found. Please run generate_order_data.py first.")
            return
        
        table = random.choice(tables)
        
        # Get some random menu items
        menu_items = MenuItem.query.filter_by(status='available').all()
        if not menu_items:
            print("No menu items found. Please run init_db.py first.")
            return
        
        # Create new order
        order = Order(
            user_id=customer.user_id,
            table_id=table.table_id,
            order_time=datetime.utcnow(),
            status='new',  # This will trigger the notification
            total_amount=0,
            notes=random.choice(['', 'Please rush this order', 'Extra spicy', 'No onions'])
        )
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Add 1-3 items to the order
        num_items = random.randint(1, 3)
        total_amount = 0
        
        selected_items = random.sample(menu_items, min(num_items, len(menu_items)))
        
        for item in selected_items:
            quantity = random.randint(1, 2)
            
            order_item = OrderItem(
                order_id=order.order_id,
                item_id=item.item_id,
                quantity=quantity,
                unit_price=item.price,
                note=random.choice(['', 'Medium spice', 'Extra sauce', 'Well done'])
            )
            db.session.add(order_item)
            total_amount += float(item.price) * quantity
        
        # Add service charge
        total_amount += 2.00
        order.total_amount = total_amount
        
        try:
            db.session.commit()
            print(f"✅ New order created successfully!")
            print(f"   Order ID: {order.order_id}")
            print(f"   Customer: {customer.name}")
            print(f"   Table: #{table.table_number}")
            print(f"   Items: {num_items}")
            print(f"   Total: {total_amount:.2f} EGP")
            print(f"   Status: {order.status}")
            print(f"   Time: {order.order_time}")
            
            # Show current notification count
            new_orders_count = Order.query.filter(Order.status.in_(['new', 'processing'])).count()
            print(f"\n🔔 Total new/processing orders: {new_orders_count}")
            
        except Exception as e:
            print(f"❌ Error creating order: {e}")
            db.session.rollback()

def main():
    """Main function"""
    print("🚀 Creating a new order to test notifications...")
    create_new_order()
    print("\n💡 Check the admin dashboard to see the red notification badge!")
    print("   URL: http://127.0.0.1:5000/admin/dashboard")

if __name__ == "__main__":
    main()
