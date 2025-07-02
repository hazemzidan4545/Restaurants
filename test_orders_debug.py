#!/usr/bin/env python3
"""Debug script to test orders display"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, User, Order, OrderItem, MenuItem, Category, Payment
from datetime import datetime

def debug_orders():
    app = create_app()
    
    with app.app_context():
        print("=== ORDER DEBUG INFORMATION ===")
        
        # Check if we have users
        users = User.query.filter_by(role='customer').all()
        print(f"Total customer users: {len(users)}")
        
        if users:
            test_user = users[0]
            print(f"Test user: {test_user.name} (ID: {test_user.user_id})")
            
            # Check orders for this user
            orders = Order.query.filter_by(user_id=test_user.user_id).all()
            print(f"Orders for user {test_user.user_id}: {len(orders)}")
            
            for order in orders:
                print(f"  Order {order.order_id}: {order.status}, ${order.total_amount}")
                items = order.order_items.all()
                print(f"    Items: {len(items)}")
                payments = order.payments.all()
                print(f"    Payments: {len(payments)}")
                for payment in payments:
                    print(f"      Payment {payment.payment_id}: {payment.status}, ${payment.amount}")
        
        # Check if we have any orders at all
        all_orders = Order.query.all()
        print(f"Total orders in database: {len(all_orders)}")
        
        # Check menu items
        menu_items = MenuItem.query.filter_by(status='available').all()
        print(f"Available menu items: {len(menu_items)}")
        
        # Create a test order if none exist
        if len(all_orders) == 0 and len(users) > 0 and len(menu_items) > 0:
            print("Creating test order...")
            test_user = users[0]
            test_item = menu_items[0]
            
            order = Order(
                user_id=test_user.user_id,
                status='new',
                total_amount=test_item.price * 2,
                notes='Test order for debugging'
            )
            db.session.add(order)
            db.session.flush()  # Get the order ID
            
            order_item = OrderItem(
                order_id=order.order_id,
                menu_item_id=test_item.item_id,
                quantity=2,
                unit_price=test_item.price
            )
            db.session.add(order_item)
            
            db.session.commit()
            print(f"Created test order {order.order_id}")

if __name__ == '__main__':
    debug_orders()
