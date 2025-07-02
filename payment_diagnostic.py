#!/usr/bin/env python3
"""
Comprehensive payment history diagnostic and fix
"""

from app import create_app
from app.models import User, Order, Payment, OrderItem, MenuItem, db
from datetime import datetime

def diagnose_and_fix_payment_history():
    app = create_app()
    
    with app.app_context():
        print("=== PAYMENT HISTORY DIAGNOSTIC ===\n")
        
        # Step 1: Check database state
        print("1. Checking database state...")
        users = User.query.all()
        orders = Order.query.all()
        payments = Payment.query.all()
        
        print(f"   Users: {len(users)}")
        print(f"   Orders: {len(orders)}")
        print(f"   Payments: {len(payments)}")
        
        # Step 2: Check user roles
        print("\n2. User breakdown:")
        for role in ['customer', 'admin', 'waiter']:
            role_users = User.query.filter_by(role=role).all()
            print(f"   {role}: {len(role_users)}")
            if role_users and role == 'customer':
                customer = role_users[0]
                customer_orders = Order.query.filter_by(user_id=customer.user_id).count()
                print(f"     First customer ({customer.username}) has {customer_orders} orders")
        
        # Step 3: Check payment-order relationships
        print("\n3. Checking payment-order relationships...")
        for payment in payments:
            try:
                order = payment.order
                customer = order.customer if hasattr(order, 'customer') else None
                print(f"   Payment #{payment.payment_id} -> Order #{payment.order_id} -> User: {customer.username if customer else 'None'}")
            except Exception as e:
                print(f"   Payment #{payment.payment_id} -> ERROR: {e}")
        
        # Step 4: Test the actual query used in the route
        print("\n4. Testing payment history queries...")
        
        # Find a customer
        customer = User.query.filter_by(role='customer').first()
        if customer:
            print(f"   Testing query for customer: {customer.username}")
            
            # Test the exact query from the route
            try:
                customer_payments = Payment.query.join(Order).filter(
                    Order.user_id == customer.user_id
                ).order_by(Payment.timestamp.desc()).all()
                print(f"   ✓ Customer payments query successful: {len(customer_payments)} payments")
                
                for payment in customer_payments:
                    print(f"     - Payment #{payment.payment_id}: ${payment.amount}, {payment.status}")
                    
            except Exception as e:
                print(f"   ✗ Customer payments query failed: {e}")
        
        # Test admin query
        admin = User.query.filter_by(role='admin').first()
        if admin:
            print(f"   Testing query for admin: {admin.username}")
            try:
                all_payments = Payment.query.order_by(Payment.timestamp.desc()).all()
                print(f"   ✓ Admin payments query successful: {len(all_payments)} payments")
            except Exception as e:
                print(f"   ✗ Admin payments query failed: {e}")
        
        # Step 5: Create test data if needed
        if len(payments) == 0:
            print("\n5. No payments found - creating test data...")
            
            # Find or create a customer
            customer = User.query.filter_by(role='customer').first()
            if not customer:
                print("   Creating test customer...")
                customer = User(
                    username='test_customer',
                    name='Test Customer',
                    email='test@customer.com',
                    role='customer'
                )
                customer.set_password('password')
                db.session.add(customer)
                db.session.flush()
            
            # Find or create a menu item
            menu_item = MenuItem.query.first()
            if not menu_item:
                print("   No menu items found - payment testing limited")
                return
            
            # Create test order
            print(f"   Creating test order for {customer.username}...")
            test_order = Order(
                user_id=customer.user_id,
                status='completed',
                total_amount=29.99,
                notes='Test order for payment history diagnostic',
                order_time=datetime.utcnow()
            )
            db.session.add(test_order)
            db.session.flush()
            
            # Create order item
            order_item = OrderItem(
                order_id=test_order.order_id,
                item_id=menu_item.item_id,
                quantity=2,
                unit_price=14.99,
                note='Test item'
            )
            db.session.add(order_item)
            
            # Create test payment
            print(f"   Creating test payment for order #{test_order.order_id}...")
            test_payment = Payment(
                order_id=test_order.order_id,
                amount=29.99,
                payment_type='card',
                status='completed',
                transaction_id=f'test_txn_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                timestamp=datetime.utcnow()
            )
            db.session.add(test_payment)
            
            # Create another payment for variety
            test_payment2 = Payment(
                order_id=test_order.order_id,
                amount=5.00,
                payment_type='cash',
                status='completed',
                transaction_id=f'test_tip_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                timestamp=datetime.utcnow()
            )
            db.session.add(test_payment2)
            
            db.session.commit()
            
            print(f"   ✓ Created test order #{test_order.order_id} with 2 payments")
            
            # Test the query again
            print("\n6. Re-testing queries with new data...")
            customer_payments = Payment.query.join(Order).filter(
                Order.user_id == customer.user_id
            ).order_by(Payment.timestamp.desc()).all()
            print(f"   Customer now has {len(customer_payments)} payments")
            
        print("\n=== DIAGNOSTIC COMPLETE ===")
        print("Payment history should now work. Try accessing the page again.")
        print("If it still shows no payments, check the user session and login status.")

if __name__ == "__main__":
    diagnose_and_fix_payment_history()
