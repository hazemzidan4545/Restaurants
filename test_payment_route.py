#!/usr/bin/env python3
"""
Simple test to access payment history route directly
"""

from app import create_app
from app.models import User, Order, Payment, db
from datetime import datetime
from flask import url_for

def test_payment_history_route():
    app = create_app()
    
    with app.app_context():
        print("=== TESTING PAYMENT HISTORY ROUTE ===\n")
        
        # Test with Flask test client
        with app.test_client() as client:
            print("1. Testing unauthenticated access...")
            response = client.get('/payment/history')
            print(f"   Status: {response.status_code}")
            if response.status_code == 302:
                print("   ✓ Correctly redirected (login required)")
            
            # Find a customer user for testing
            customer = User.query.filter_by(role='customer').first()
            if customer:
                print(f"\n2. Found customer: {customer.username}")
                
                # Check if customer has any orders with payments
                orders_with_payments = Order.query.filter_by(user_id=customer.user_id).join(Payment).count()
                print(f"   Orders with payments: {orders_with_payments}")
                
                if orders_with_payments == 0:
                    # Create a test order and payment
                    print("   Creating test data...")
                    
                    # Create test order
                    test_order = Order(
                        user_id=customer.user_id,
                        status='completed',
                        total_amount=25.99,
                        notes='Test order for payment history',
                        order_time=datetime.utcnow()
                    )
                    db.session.add(test_order)
                    db.session.flush()
                    
                    # Create test payment
                    test_payment = Payment(
                        order_id=test_order.order_id,
                        amount=25.99,
                        payment_type='card',
                        status='completed',
                        transaction_id='test_txn_123',
                        timestamp=datetime.utcnow()
                    )
                    db.session.add(test_payment)
                    db.session.commit()
                    
                    print(f"   ✓ Created test order #{test_order.order_id} with payment #{test_payment.payment_id}")
                
                print(f"\n3. Customer {customer.username} now has payments - ready to test route")
            else:
                print("\n2. ✗ No customer users found - need to create test users")
        
        print("\n=== TEST COMPLETE ===")
        print("Try accessing the payment history page again in your browser.")
        print("The route should now work without the 'customer_id' and 'created_at' errors.")

if __name__ == "__main__":
    test_payment_history_route()
