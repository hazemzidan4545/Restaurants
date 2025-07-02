#!/usr/bin/env python3
"""
Create test data and verify payment system
"""

from app import create_app
from app.models import User, Order, Payment, MenuItem, OrderItem, Category, db
from datetime import datetime

def create_test_payment_data():
    app = create_app()
    
    with app.app_context():
        print("=== CREATING TEST PAYMENT DATA ===\n")
        
        # Find or create a customer user
        customer = User.query.filter_by(role='customer').first()
        if not customer:
            print("Creating test customer...")
            customer = User(
                username='john_customer',
                name='John Customer',
                email='john@customer.com',
                role='customer',
                phone='555-0123'
            )
            customer.set_password('password')
            db.session.add(customer)
            db.session.flush()
            print(f"✓ Created customer: {customer.username}")
        else:
            print(f"Found existing customer: {customer.username}")
        
        # Find or create a menu item
        menu_item = MenuItem.query.first()
        if not menu_item:
            print("Creating test menu item...")
            category = Category.query.first()
            if not category:
                category = Category(name='Main Courses', description='Main dishes')
                db.session.add(category)
                db.session.flush()
            
            menu_item = MenuItem(
                name='Test Burger',
                description='Delicious test burger',
                price=15.99,
                category_id=category.category_id,
                status='available'
            )
            db.session.add(menu_item)
            db.session.flush()
            print(f"✓ Created menu item: {menu_item.name}")
        else:
            print(f"Found existing menu item: {menu_item.name}")
        
        # Create test orders with payments
        print(f"\nCreating test orders for {customer.username}...")
        
        # Order 1: Card payment
        order1 = Order(
            user_id=customer.user_id,
            status='completed',
            total_amount=23.98,
            notes='Test order 1 - Card payment',
            order_time=datetime.utcnow()
        )
        db.session.add(order1)
        db.session.flush()
        
        # Add order item
        order_item1 = OrderItem(
            order_id=order1.order_id,
            item_id=menu_item.item_id,
            quantity=1,
            unit_price=15.99,
            note='Extra cheese'
        )
        db.session.add(order_item1)
        
        # Add payment
        payment1 = Payment(
            order_id=order1.order_id,
            amount=23.98,
            payment_type='card',
            status='completed',
            transaction_id='card_txn_001',
            timestamp=datetime.utcnow()
        )
        db.session.add(payment1)
        
        # Order 2: Cash payment
        order2 = Order(
            user_id=customer.user_id,
            status='completed',
            total_amount=31.98,
            notes='Test order 2 - Cash payment',
            order_time=datetime.utcnow()
        )
        db.session.add(order2)
        db.session.flush()
        
        # Add order item
        order_item2 = OrderItem(
            order_id=order2.order_id,
            item_id=menu_item.item_id,
            quantity=2,
            unit_price=15.99,
            note='No pickles'
        )
        db.session.add(order_item2)
        
        # Add payment
        payment2 = Payment(
            order_id=order2.order_id,
            amount=31.98,
            payment_type='cash',
            status='completed',
            transaction_id='cash_txn_001',
            timestamp=datetime.utcnow()
        )
        db.session.add(payment2)
        
        # Order 3: Wallet payment (pending)
        order3 = Order(
            user_id=customer.user_id,
            status='new',
            total_amount=15.99,
            notes='Test order 3 - Wallet payment pending',
            order_time=datetime.utcnow()
        )
        db.session.add(order3)
        db.session.flush()
        
        # Add order item
        order_item3 = OrderItem(
            order_id=order3.order_id,
            item_id=menu_item.item_id,
            quantity=1,
            unit_price=15.99,
            note='Standard'
        )
        db.session.add(order_item3)
        
        # Add payment
        payment3 = Payment(
            order_id=order3.order_id,
            amount=15.99,
            payment_type='wallet',
            status='pending',
            transaction_id='wallet_txn_001',
            timestamp=datetime.utcnow()
        )
        db.session.add(payment3)
        
        db.session.commit()
        
        print(f"✓ Created 3 orders with payments:")
        print(f"  - Order #{order1.order_id}: ${payment1.amount} ({payment1.payment_type}, {payment1.status})")
        print(f"  - Order #{order2.order_id}: ${payment2.amount} ({payment2.payment_type}, {payment2.status})")
        print(f"  - Order #{order3.order_id}: ${payment3.amount} ({payment3.payment_type}, {payment3.status})")
        
        # Test the payment history query
        print(f"\nTesting payment history for {customer.username}...")
        payments = Payment.query.join(Order).filter(
            Order.user_id == customer.user_id
        ).order_by(Payment.timestamp.desc()).all()
        
        print(f"✓ Found {len(payments)} payments in history")
        for payment in payments:
            print(f"  - Payment #{payment.payment_id}: ${payment.amount} via {payment.payment_type} ({payment.status})")
        
        print(f"\n=== TEST DATA CREATED SUCCESSFULLY ===")
        print(f"Login as customer '{customer.username}' (password: 'password') to see payment history")
        print(f"Customer ID: {customer.user_id}")

if __name__ == "__main__":
    create_test_payment_data()
