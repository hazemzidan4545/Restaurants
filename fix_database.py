#!/usr/bin/env python3
"""Fix database schema and create test data"""

from app import create_app
from app.models import db, User, Order, OrderItem, MenuItem, Category, Payment
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        print("=== FIXING DATABASE SCHEMA ===")
        
        # Drop and recreate tables to fix schema issues
        print("Dropping all tables...")
        db.drop_all()
        
        print("Creating all tables...")
        db.create_all()
        
        print("=== CREATING TEST DATA ===")
        
        # Create test customer
        customer = User(
            name='Test Customer',
            email='customer@test.com',
            password_hash=generate_password_hash('test123'),
            role='customer',
            phone='555-0123'
        )
        db.session.add(customer)
        
        # Create admin user
        admin = User(
            name='Admin User',
            email='admin@test.com',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            phone='555-0124'
        )
        db.session.add(admin)
        
        # Create waiter user
        waiter = User(
            name='Waiter User',
            email='waiter@test.com',
            password_hash=generate_password_hash('waiter123'),
            role='waiter',
            phone='555-0125'
        )
        db.session.add(waiter)
        
        db.session.commit()
        print(f"Created users: Customer({customer.user_id}), Admin({admin.user_id}), Waiter({waiter.user_id})")
        
        # Create categories
        categories_data = [
            {'name': 'Main Dishes', 'description': 'Hearty main courses'},
            {'name': 'Appetizers', 'description': 'Start your meal right'},
            {'name': 'Desserts', 'description': 'Sweet endings'},
            {'name': 'Beverages', 'description': 'Drinks and refreshments'}
        ]
        
        categories = []
        for i, cat_data in enumerate(categories_data):
            category = Category(
                name=cat_data['name'],
                description=cat_data['description'],
                is_active=True,
                display_order=i+1
            )
            db.session.add(category)
            categories.append(category)
        
        db.session.commit()
        print(f"Created {len(categories)} categories")
        
        # Create menu items
        menu_items_data = [
            {'name': 'Grilled Chicken', 'price': 25.99, 'description': 'Delicious grilled chicken breast', 'category': 0},
            {'name': 'Beef Burger', 'price': 18.50, 'description': 'Juicy beef burger with fries', 'category': 0},
            {'name': 'Caesar Salad', 'price': 12.99, 'description': 'Fresh caesar salad with croutons', 'category': 1},
            {'name': 'Chicken Wings', 'price': 16.99, 'description': 'Spicy buffalo chicken wings', 'category': 1},
            {'name': 'Chocolate Cake', 'price': 8.99, 'description': 'Rich chocolate cake slice', 'category': 2},
            {'name': 'Coffee', 'price': 3.99, 'description': 'Freshly brewed coffee', 'category': 3}
        ]
        
        menu_items = []
        for item_data in menu_items_data:
            item = MenuItem(
                name=item_data['name'],
                price=item_data['price'],
                description=item_data['description'],
                category_id=categories[item_data['category']].category_id,
                status='available',
                stock=100
            )
            db.session.add(item)
            menu_items.append(item)
        
        db.session.commit()
        print(f"Created {len(menu_items)} menu items")
        
        # Create test orders with items
        import random
        orders_data = [
            {'status': 'completed', 'days_ago': 5},
            {'status': 'processing', 'days_ago': 1},
            {'status': 'new', 'days_ago': 0}
        ]
        
        created_orders = []
        for i, order_data in enumerate(orders_data):
            order_time = datetime.utcnow() - timedelta(days=order_data['days_ago'])
            
            order = Order(
                user_id=customer.user_id,
                status=order_data['status'],
                order_time=order_time,
                notes=f'Test order {i+1} for debugging',
                total_amount=0  # Will be calculated
            )
            db.session.add(order)
            db.session.flush()  # Get order ID
            
            # Add 1-3 random items to each order
            num_items = random.randint(1, 3)
            total = 0
            
            for j in range(num_items):
                menu_item = random.choice(menu_items)
                quantity = random.randint(1, 2)
                
                order_item = OrderItem(
                    order_id=order.order_id,
                    menu_item_id=menu_item.item_id,  # Use item_id from MenuItem
                    quantity=quantity,
                    unit_price=menu_item.price
                )
                db.session.add(order_item)
                total += quantity * menu_item.price
            
            order.total_amount = total
            created_orders.append(order)
            
            # Create a payment for completed orders
            if order.status == 'completed':
                payment = Payment(
                    order_id=order.order_id,
                    amount=total,
                    payment_type='card',
                    status='completed'
                )
                db.session.add(payment)
        
        db.session.commit()
        print(f"Created {len(created_orders)} orders with items and payments")
        
        # Verify the data
        print("\n=== VERIFICATION ===")
        print(f"Total users: {User.query.count()}")
        print(f"Total categories: {Category.query.count()}")
        print(f"Total menu items: {MenuItem.query.count()}")
        print(f"Total orders: {Order.query.count()}")
        print(f"Total order items: {OrderItem.query.count()}")
        print(f"Total payments: {Payment.query.count()}")
        
        # Test customer orders specifically
        customer_orders = Order.query.filter_by(user_id=customer.user_id).all()
        print(f"Customer orders: {len(customer_orders)}")
        for order in customer_orders:
            items = order.order_items.all()
            payments = order.payments.all()
            print(f"  Order {order.order_id}: {order.status}, {len(items)} items, {len(payments)} payments")
        
        print("\n✅ Database setup complete!")
        print("Login credentials:")
        print("  Customer: customer@test.com / test123")
        print("  Admin: admin@test.com / admin123")
        print("  Waiter: waiter@test.com / waiter123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
