#!/usr/bin/env python3
"""Quick check of existing orders and loyalty status"""

from app import create_app
from app.models import db, User, Order, CustomerLoyalty, PointTransaction
from sqlalchemy import func

app = create_app()

with app.app_context():
    print("=== QUICK LOYALTY SYSTEM CHECK ===\n")
    
    # Check completed orders without point transactions
    completed_orders = Order.query.filter_by(status='completed').all()
    print(f"Found {len(completed_orders)} completed orders")
    
    orders_without_points = []
    for order in completed_orders:
        transaction = PointTransaction.query.filter_by(
            order_id=order.order_id,
            transaction_type='earned'
        ).first()
        
        if not transaction:
            orders_without_points.append(order)
    
    print(f"Found {len(orders_without_points)} completed orders without points")
    
    if orders_without_points:
        print("\nOrders that should have points but don't:")
        for order in orders_without_points[:5]:  # Show first 5
            user = User.query.get(order.user_id)
            print(f"  Order {order.order_id}: {order.total_amount} EGP by {user.name if user else 'Unknown'}")
    
    # Check loyalty accounts
    loyalty_accounts = CustomerLoyalty.query.all()
    print(f"\nFound {len(loyalty_accounts)} loyalty accounts:")
    
    for loyalty in loyalty_accounts:
        user = User.query.get(loyalty.user_id)
        completed_orders_count = Order.query.filter(
            Order.user_id == loyalty.user_id,
            Order.status.in_(['completed', 'delivered'])
        ).count()
        
        total_spent = db.session.query(func.sum(Order.total_amount)).filter(
            Order.user_id == loyalty.user_id,
            Order.status.in_(['completed', 'delivered'])
        ).scalar() or 0
        
        print(f"  {user.name if user else 'Unknown'}: {loyalty.total_points} points, "
              f"{completed_orders_count} orders, {float(total_spent):.2f} EGP spent")
    
    print("\n=== CHECK COMPLETE ===")
