#!/usr/bin/env python3
"""Test order creation with fixed schema"""

from app import create_app
from app.models import db, User, Order, OrderItem, MenuItem, Category
from datetime import datetime
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    try:
        print("=== TESTING ORDER CREATION ===")
        
        # Ensure we have a customer
        customer = User.query.filter_by(email='customer@test.com').first()
        if not customer:
            customer = User(
                name='Test Customer',
                email='customer@test.com',
                password_hash=generate_password_hash('test123'),
                role='customer',
                phone='555-0123'
            )
            db.session.add(customer)
            db.session.commit()
            print(f"✅ Created customer: {customer.user_id}")
        
        # Ensure we have a menu item
        menu_item = MenuItem.query.filter_by(status='available').first()
        if not menu_item:
            # Create category first
            category = Category.query.first()
            if not category:
                category = Category(name='Test Category', is_active=True)
                db.session.add(category)
                db.session.commit()
            
            menu_item = MenuItem(
                name='Test Pizza',
                price=15.99,
                description='Delicious test pizza',
                category_id=category.category_id,
                status='available',
                stock=100
            )
            db.session.add(menu_item)
            db.session.commit()
            print(f"✅ Created menu item: {menu_item.item_id}")
        
        # Test creating an order
        print(f"Testing order creation...")
        print(f"Customer ID: {customer.user_id}")
        print(f"Menu item ID: {menu_item.item_id}")
        
        order = Order(
            user_id=customer.user_id,
            status='new',
            total_amount=31.98,
            notes='Test order for schema verification'
        )
        db.session.add(order)
        db.session.flush()  # Get order ID
        print(f"✅ Created order: {order.order_id}")
        
        # Test creating an order item with the correct field
        order_item = OrderItem(
            order_id=order.order_id,
            menu_item_id=menu_item.item_id,  # This should work now
            quantity=2,
            unit_price=menu_item.price
        )
        db.session.add(order_item)
        db.session.commit()
        print(f"✅ Created order item: {order_item.order_item_id}")
        
        # Verify the relationships work
        test_order = Order.query.get(order.order_id)
        items = test_order.order_items.all()
        print(f"✅ Order has {len(items)} items")
        
        if items:
            item = items[0]
            print(f"✅ Item: {item.menu_item.name} x{item.quantity} = ${item.unit_price * item.quantity}")
        
        print("\n🎉 Order creation test PASSED!")
        print("The schema is now fixed and orders should work properly.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
