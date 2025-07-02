#!/usr/bin/env python3
"""Simple test to create customer and order data directly"""

from app import create_app
from app.models import db, User, Order, OrderItem, MenuItem, Category
from datetime import datetime
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    try:
        print("Checking database...")
        
        # Ensure tables exist
        db.create_all()
        
        # Create test customer if doesn't exist
        customer = User.query.filter_by(email='test@customer.com').first()
        if not customer:
            customer = User(
                name='Test Customer',
                email='test@customer.com',
                password_hash=generate_password_hash('test123'),
                role='customer',
                phone='555-0123'
            )
            db.session.add(customer)
            db.session.commit()
            print(f"Created customer: {customer.user_id}")
        else:
            print(f"Customer exists: {customer.user_id}")
        
        # Create category and menu item if doesn't exist
        category = Category.query.first()
        if not category:
            category = Category(name='Test Category', is_active=True)
            db.session.add(category)
            db.session.commit()
        
        menu_item = MenuItem.query.first()
        if not menu_item:
            menu_item = MenuItem(
                name='Test Pizza',
                price=15.99,
                description='Delicious test pizza',
                category_id=category.category_id,
                status='available'
            )
            db.session.add(menu_item)
            db.session.commit()
        
        # Create test order
        existing_order = Order.query.filter_by(user_id=customer.user_id).first()
        if not existing_order:
            order = Order(
                user_id=customer.user_id,
                status='new',
                total_amount=31.98,
                notes='Test order for debugging'
            )
            db.session.add(order)
            db.session.flush()
            
            order_item = OrderItem(
                order_id=order.order_id,
                menu_item_id=menu_item.item_id,
                quantity=2,
                unit_price=menu_item.price
            )
            db.session.add(order_item)
            db.session.commit()
            print(f"Created order: {order.order_id}")
        else:
            print(f"Order exists: {existing_order.order_id}")
        
        # Verify data
        orders_count = Order.query.filter_by(user_id=customer.user_id).count()
        print(f"Total orders for customer: {orders_count}")
        
        print("✅ Test data created successfully!")
        print(f"Login with: test@customer.com / test123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
