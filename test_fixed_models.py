#!/usr/bin/env python3
"""
Test the fixed model relationships
"""

from app import create_app
from app.models import User, Order, Payment, db

def test_fixed_relationships():
    app = create_app()
    
    with app.app_context():
        print("=== TESTING FIXED RELATIONSHIPS ===\n")
        
        try:
            # Test basic model queries
            users = User.query.count()
            orders = Order.query.count()
            payments = Payment.query.count()
            
            print(f"✓ Models loaded successfully:")
            print(f"  Users: {users}")
            print(f"  Orders: {orders}")
            print(f"  Payments: {payments}")
            
            # Test relationships
            print(f"\n✓ Testing relationships...")
            
            # Test User -> Orders relationship
            user = User.query.first()
            if user:
                user_orders = user.orders.count()
                print(f"  User {user.username} has {user_orders} orders")
            
            # Test Order -> Customer relationship
            order = Order.query.first()
            if order:
                customer = order.customer
                print(f"  Order #{order.order_id} belongs to customer: {customer.username if customer else 'None'}")
            
            # Test Payment -> Order -> Customer chain
            payment = Payment.query.first()
            if payment:
                customer = payment.order.customer
                print(f"  Payment #{payment.payment_id} -> Order #{payment.order.order_id} -> Customer: {customer.username if customer else 'None'}")
            
            print(f"\n✓ All relationships working correctly!")
            print(f"The payment history page should now work without SQLAlchemy errors.")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
        
        return True

if __name__ == "__main__":
    test_fixed_relationships()
