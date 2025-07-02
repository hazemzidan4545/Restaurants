#!/usr/bin/env python3
"""
Comprehensive payment data creation and user analysis
"""

from app import create_app
from app.models import User, Order, Payment, MenuItem, OrderItem, Category, db
from datetime import datetime, timedelta

def analyze_and_create_payment_data():
    app = create_app()
    
    with app.app_context():
        print("=== PAYMENT DATA ANALYSIS & CREATION ===\n")
        
        # Step 1: Analyze current state
        print("1. Current Database State:")
        users = User.query.all()
        orders = Order.query.all()
        payments = Payment.query.all()
        
        print(f"   Total Users: {len(users)}")
        print(f"   Total Orders: {len(orders)}")
        print(f"   Total Payments: {len(payments)}")
        
        # Step 2: Show user breakdown with their data
        print(f"\n2. User Analysis:")
        for user in users:
            user_orders = Order.query.filter_by(user_id=user.user_id).count()
            user_payments = Payment.query.join(Order).filter(Order.user_id == user.user_id).count()
            print(f"   👤 {user.username} ({user.role}):")
            print(f"      ID: {user.user_id}")
            print(f"      Orders: {user_orders}")
            print(f"      Payments: {user_payments}")
        
        # Step 3: Find or create customers with payment data
        customers = User.query.filter_by(role='customer').all()
        
        if not customers:
            print(f"\n3. No customers found - creating test customers...")
            
            # Create test customer
            customer = User(
                username='customer1',
                name='Test Customer',
                email='customer@test.com',
                role='customer',
                phone='555-0100'
            )
            customer.set_password('password')
            db.session.add(customer)
            db.session.flush()
            customers = [customer]
            print(f"   ✓ Created customer: {customer.username} (ID: {customer.user_id})")
        
        # Step 4: Ensure we have menu items
        menu_item = MenuItem.query.first()
        if not menu_item:
            print(f"\n4. No menu items found - creating test item...")
            
            # Create category if needed
            category = Category.query.first()
            if not category:
                category = Category(name='Test Category', description='Test items')
                db.session.add(category)
                db.session.flush()
            
            menu_item = MenuItem(
                name='Test Burger',
                description='Delicious test burger for payment testing',
                price=19.99,
                category_id=category.category_id,
                status='available'
            )
            db.session.add(menu_item)
            db.session.flush()
            print(f"   ✓ Created menu item: {menu_item.name}")
        
        # Step 5: Create payments for each customer
        print(f"\n5. Creating payment data for customers...")
        
        for customer in customers:
            # Check if customer already has payments
            existing_payments = Payment.query.join(Order).filter(Order.user_id == customer.user_id).count()
            
            if existing_payments > 0:
                print(f"   Customer {customer.username} already has {existing_payments} payments - skipping")
                continue
                
            print(f"   Creating payments for {customer.username}...")
            
            # Create 3 different payment scenarios
            payment_scenarios = [
                {
                    'amount': 29.99,
                    'type': 'card',
                    'status': 'completed',
                    'notes': 'Card payment - completed',
                    'days_ago': 1
                },
                {
                    'amount': 45.50,
                    'type': 'cash',
                    'status': 'completed',
                    'notes': 'Cash payment - completed',
                    'days_ago': 3
                },
                {
                    'amount': 15.99,
                    'type': 'wallet',
                    'status': 'pending',
                    'notes': 'Digital wallet - pending',
                    'days_ago': 0
                }
            ]
            
            for i, scenario in enumerate(payment_scenarios):
                # Create order
                order_time = datetime.utcnow() - timedelta(days=scenario['days_ago'])
                
                order = Order(
                    user_id=customer.user_id,
                    status='completed' if scenario['status'] == 'completed' else 'new',
                    total_amount=scenario['amount'],
                    notes=scenario['notes'],
                    order_time=order_time
                )
                db.session.add(order)
                db.session.flush()
                
                # Create order item
                order_item = OrderItem(
                    order_id=order.order_id,
                    item_id=menu_item.item_id,
                    quantity=1,
                    unit_price=scenario['amount'],
                    note=f'Test item {i+1}'
                )
                db.session.add(order_item)
                
                # Create payment
                payment = Payment(
                    order_id=order.order_id,
                    amount=scenario['amount'],
                    payment_type=scenario['type'],
                    status=scenario['status'],
                    transaction_id=f'test_txn_{customer.user_id}_{i+1}',
                    timestamp=order_time
                )
                db.session.add(payment)
                
                print(f"     ✓ Order #{order.order_id}: ${scenario['amount']} via {scenario['type']} ({scenario['status']})")
        
        db.session.commit()
        
        # Step 6: Final verification
        print(f"\n6. Final Verification:")
        for customer in customers:
            customer_payments = Payment.query.join(Order).filter(Order.user_id == customer.user_id).count()
            print(f"   {customer.username} now has {customer_payments} payments")
        
        print(f"\n=== PAYMENT DATA READY ===")
        print(f"Login Credentials for Testing:")
        for customer in customers:
            print(f"   Username: {customer.username}")
            print(f"   Password: password")
            print(f"   Expected payments: {Payment.query.join(Order).filter(Order.user_id == customer.user_id).count()}")
        
        print(f"\nThe payment history page should now show payments when you login as any of these customers.")

if __name__ == "__main__":
    analyze_and_create_payment_data()
