#!/usr/bin/env python3
"""Create test order data"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, User, Order, OrderItem, MenuItem, Category
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

def create_test_data():
    app = create_app()
    
    with app.app_context():
        try:
            # Check if we have a customer user
            customer = User.query.filter_by(role='customer').first()
            if not customer:
                print("Creating test customer...")
                customer = User(
                    name='Test Customer',
                    email='customer@test.com',
                    password_hash=generate_password_hash('password'),
                    role='customer',
                    phone='1234567890'
                )
                db.session.add(customer)
                db.session.commit()
                print(f"Created customer: {customer.user_id}")
            
            # Check if we have menu items
            menu_items = MenuItem.query.filter_by(status='available').all()
            if not menu_items:
                print("Creating test menu items...")
                # Create a category first
                category = Category.query.first()
                if not category:
                    category = Category(name='Main Dishes', is_active=True, display_order=1)
                    db.session.add(category)
                    db.session.commit()
                
                # Create menu items
                items_data = [
                    {'name': 'Grilled Chicken', 'price': 25.99, 'description': 'Delicious grilled chicken'},
                    {'name': 'Beef Burger', 'price': 18.50, 'description': 'Juicy beef burger'},
                    {'name': 'Caesar Salad', 'price': 12.99, 'description': 'Fresh caesar salad'}
                ]
                
                for item_data in items_data:
                    item = MenuItem(
                        name=item_data['name'],
                        price=item_data['price'],
                        description=item_data['description'],
                        category_id=category.category_id,
                        status='available'
                    )
                    db.session.add(item)
                
                db.session.commit()
                menu_items = MenuItem.query.filter_by(status='available').all()
                print(f"Created {len(menu_items)} menu items")
            
            # Create test orders
            orders = Order.query.filter_by(user_id=customer.user_id).all()
            if not orders:
                print("Creating test orders...")
                
                # Create 3 test orders with different statuses
                orders_data = [
                    {'status': 'completed', 'days_ago': 5},
                    {'status': 'processing', 'days_ago': 1},
                    {'status': 'new', 'days_ago': 0}
                ]
                
                for i, order_data in enumerate(orders_data):
                    order_time = datetime.utcnow() - timedelta(days=order_data['days_ago'])
                    
                    order = Order(
                        user_id=customer.user_id,
                        status=order_data['status'],
                        order_time=order_time,
                        notes=f'Test order {i+1}',
                        total_amount=0  # Will be calculated
                    )
                    db.session.add(order)
                    db.session.flush()  # Get order ID
                    
                    # Add 1-3 random items to each order
                    import random
                    num_items = random.randint(1, 3)
                    total = 0
                    
                    for j in range(num_items):
                        menu_item = random.choice(menu_items)
                        quantity = random.randint(1, 2)
                        
                        order_item = OrderItem(
                            order_id=order.order_id,
                            menu_item_id=menu_item.item_id,
                            quantity=quantity,
                            unit_price=menu_item.price
                        )
                        db.session.add(order_item)
                        total += quantity * menu_item.price
                    
                    order.total_amount = total
                
                db.session.commit()
                print("Created test orders successfully")
            
            # Print summary
            print(f"\n=== DATABASE SUMMARY ===")
            print(f"Customers: {User.query.filter_by(role='customer').count()}")
            print(f"Menu items: {MenuItem.query.filter_by(status='available').count()}")
            print(f"Orders: {Order.query.count()}")
            print(f"Orders for test customer: {Order.query.filter_by(user_id=customer.user_id).count()}")
            
        except Exception as e:
            print(f"Error creating test data: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    create_test_data()
