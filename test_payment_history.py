#!/usr/bin/env python3
"""
Test script to verify payment history functionality
"""

from app import create_app
from app.models import User, Order, Payment, db
from datetime import datetime

def test_payment_history():
    app = create_app()
    
    with app.app_context():
        print("=== PAYMENT HISTORY TEST ===\n")
        
        # Check if we have any payments
        payments = Payment.query.all()
        print(f"Total payments in database: {len(payments)}")
        
        # Check users
        users = User.query.all()
        print(f"Total users: {len(users)}")
        
        for user in users:
            if user.role == 'customer':
                # Get payments for this user through orders
                user_payments = Payment.query.join(Order).filter(
                    Order.user_id == user.user_id
                ).all()
                print(f"Customer {user.username}: {len(user_payments)} payments")
                
                for payment in user_payments:
                    print(f"  - Payment #{payment.payment_id}: ${payment.amount}, Status: {payment.status}")
        
        # Check if any payments exist
        if not payments:
            print("\n⚠ No payments found. Creating test payment...")
            
            # Find a customer and an order
            customer = User.query.filter_by(role='customer').first()
            if customer:
                order = Order.query.filter_by(user_id=customer.user_id).first()
                if order:
                    # Create a test payment
                    test_payment = Payment(
                        order_id=order.order_id,
                        amount=order.total_amount,
                        payment_type='card',
                        status='completed',
                        transaction_id='test_txn_001',
                        timestamp=datetime.utcnow()
                    )
                    db.session.add(test_payment)
                    db.session.commit()
                    print(f"✓ Created test payment for order #{order.order_id}")
                else:
                    print("✗ No orders found for customer")
            else:
                print("✗ No customers found")
        
        print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_payment_history()
