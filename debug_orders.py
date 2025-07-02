#!/usr/bin/env python3
"""Debug orders and payments"""

from app import create_app
from app.models import db, User, Order, OrderItem, Payment
from datetime import datetime

app = create_app()

with app.app_context():
    print("=== ORDERS AND PAYMENTS DEBUG ===")
    
    # Check all users
    users = User.query.all()
    print(f"\nTotal users: {len(users)}")
    for user in users:
        print(f"  {user.user_id}: {user.email} ({user.role})")
    
    # Check all orders
    orders = Order.query.all()
    print(f"\nTotal orders: {len(orders)}")
    for order in orders:
        print(f"  Order {order.order_id}: User {order.user_id}, Status: {order.status}, Amount: ${order.total_amount}")
        
        # Check order items
        items = order.order_items.all()
        print(f"    Items: {len(items)}")
        for item in items:
            print(f"      - {item.menu_item.name if item.menu_item else 'Unknown'}: {item.quantity}x ${item.unit_price}")
        
        # Check payments
        payments = order.payments.all()
        print(f"    Payments: {len(payments)}")
        for payment in payments:
            print(f"      - Payment {payment.payment_id}: ${payment.amount}, Status: {payment.status}")
    
    # Check payments separately
    all_payments = Payment.query.all()
    print(f"\nTotal payments: {len(all_payments)}")
    
    # Test customer query specifically
    customer_users = User.query.filter_by(role='customer').all()
    print(f"\nCustomer users: {len(customer_users)}")
    
    if customer_users:
        test_customer = customer_users[0]
        print(f"Testing with customer: {test_customer.email}")
        
        customer_orders = Order.query.filter_by(user_id=test_customer.user_id).all()
        print(f"Orders for this customer: {len(customer_orders)}")
