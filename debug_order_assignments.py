#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import Order, User
from app.extensions import db

def check_order_assignments():
    """Check which users orders are assigned to"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Checking order assignments...")
        
        # Get all orders with user info
        orders = Order.query.all()
        print(f"Total orders: {len(orders)}")
        
        # Group by user
        user_order_counts = {}
        user_names = {}
        
        for order in orders:
            user_id = order.user_id
            if user_id not in user_order_counts:
                user_order_counts[user_id] = 0
                # Get user name
                user = User.query.get(user_id)
                user_names[user_id] = user.name if user else "Unknown User"
            
            user_order_counts[user_id] += 1
            
        print("\n📊 Orders by user:")
        for user_id, count in user_order_counts.items():
            user = User.query.get(user_id)
            role = user.role if user else "unknown"
            print(f"  User ID {user_id} ({user_names[user_id]}) [{role}]: {count} orders")
        
        # Check if we have admin user with lots of orders
        admin_users = User.query.filter_by(role='admin').all()
        print(f"\n👑 Admin users:")
        for admin in admin_users:
            admin_orders = user_order_counts.get(admin.user_id, 0)
            print(f"  {admin.name} (ID: {admin.user_id}): {admin_orders} orders")
            
        # Check customer users
        customer_users = User.query.filter_by(role='customer').all()
        print(f"\n👤 Customer users:")
        for customer in customer_users:
            customer_orders = user_order_counts.get(customer.user_id, 0)
            print(f"  {customer.name} (ID: {customer.user_id}): {customer_orders} orders")
            
        # Show recent orders with details
        print(f"\n📋 Recent orders:")
        recent_orders = Order.query.order_by(Order.order_time.desc()).limit(5).all()
        for order in recent_orders:
            user = User.query.get(order.user_id)
            user_name = user.name if user else "Unknown"
            user_role = user.role if user else "unknown"
            print(f"  Order {order.order_id}: {user_name} ({user_role}) - ${order.total_amount} - {order.status}")

if __name__ == "__main__":
    check_order_assignments()
