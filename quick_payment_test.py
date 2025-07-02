#!/usr/bin/env python3
"""
Quick test for payment history with fixed relationships
"""

from app import create_app
from app.models import User, Order, Payment, db
from datetime import datetime

def quick_payment_test():
    app = create_app()
    
    with app.app_context():
        print("=== QUICK PAYMENT HISTORY TEST ===\n")
        
        # Test the fixed relationship
        print("1. Testing Order -> User relationship...")
        orders = Order.query.all()
        for order in orders[:3]:  # Test first 3 orders
            try:
                customer = order.customer
                print(f"   Order #{order.order_id} -> Customer: {customer.username if customer else 'None'}")
            except Exception as e:
                print(f"   Order #{order.order_id} -> ERROR: {e}")
        
        # Test payment history query
        print("\n2. Testing payment history query...")
        customer = User.query.filter_by(role='customer').first()
        if customer:
            try:
                # Test the exact query from the fixed route
                payments = Payment.query.join(Order).filter(
                    Order.user_id == customer.user_id
                ).order_by(Payment.timestamp.desc()).all()
                
                print(f"   Customer {customer.username} has {len(payments)} payments")
                
                for payment in payments:
                    print(f"     - Payment #{payment.payment_id}: ${payment.amount}")
                    print(f"       Order: #{payment.order.order_id}")
                    print(f"       Customer: {payment.order.customer.username}")
                
                if len(payments) == 0:
                    print("   No payments found - creating test payment...")
                    
                    # Create test order and payment
                    test_order = Order(
                        user_id=customer.user_id,
                        status='completed',
                        total_amount=25.99,
                        notes='Test payment for history',
                        order_time=datetime.utcnow()
                    )
                    db.session.add(test_order)
                    db.session.flush()
                    
                    test_payment = Payment(
                        order_id=test_order.order_id,
                        amount=25.99,
                        payment_type='card',
                        status='completed',
                        transaction_id='test_payment_001',
                        timestamp=datetime.utcnow()
                    )
                    db.session.add(test_payment)
                    db.session.commit()
                    
                    print(f"   ✓ Created test payment #{test_payment.payment_id}")
                    
            except Exception as e:
                print(f"   ✗ Payment query failed: {e}")
        else:
            print("   No customer found")
        
        # Test template access pattern
        print("\n3. Testing template access patterns...")
        payment = Payment.query.first()
        if payment:
            try:
                print(f"   Payment #{payment.payment_id}:")
                print(f"     payment.payment_id: {payment.payment_id}")
                print(f"     payment.amount: {payment.amount}")
                print(f"     payment.payment_type: {payment.payment_type}")
                print(f"     payment.status: {payment.status}")
                print(f"     payment.timestamp: {payment.timestamp}")
                print(f"     payment.order.order_id: {payment.order.order_id}")
                print(f"     payment.order.customer.username: {payment.order.customer.username}")
                print("   ✓ All template fields accessible")
            except Exception as e:
                print(f"   ✗ Template access error: {e}")
        
        print("\n=== TEST COMPLETE ===")
        print("Payment history should now work correctly!")

if __name__ == "__main__":
    quick_payment_test()
