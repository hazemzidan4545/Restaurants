#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import Order, User
from app.extensions import db
import random

def fix_order_assignments():
    """Fix orders that are all assigned to admin by redistributing to customers"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Fixing order assignments...")
        
        # Get admin user (probably user_id = 1)
        admin_user = User.query.filter_by(role='admin').first()
        if not admin_user:
            print("❌ No admin user found")
            return
        
        print(f"Admin user: {admin_user.name} (ID: {admin_user.user_id})")
        
        # Get all customer users
        customers = User.query.filter_by(role='customer').all()
        if not customers:
            print("❌ No customer users found")
            return
        
        print(f"Found {len(customers)} customer users")
        
        # Get orders assigned to admin
        admin_orders = Order.query.filter_by(user_id=admin_user.user_id).all()
        print(f"Found {len(admin_orders)} orders assigned to admin")
        
        if len(admin_orders) > len(customers) * 2:  # If admin has too many orders
            print("🚨 Admin has suspiciously many orders - redistributing some to customers")
            
            # Redistribute half of the admin's orders to customers
            orders_to_reassign = admin_orders[len(customers):]  # Keep some for admin, reassign the rest
            
            for i, order in enumerate(orders_to_reassign):
                # Assign to a random customer
                customer = random.choice(customers)
                old_user_id = order.user_id
                order.user_id = customer.user_id
                print(f"  Reassigning order {order.order_id} from {old_user_id} to {customer.user_id} ({customer.name})")
            
            db.session.commit()
            print(f"✅ Reassigned {len(orders_to_reassign)} orders")
        else:
            print("✅ Order assignments look reasonable")
        
        # Show final distribution
        print("\n📊 Final order distribution:")
        all_users = User.query.all()
        for user in all_users:
            order_count = Order.query.filter_by(user_id=user.user_id).count()
            if order_count > 0:
                print(f"  {user.name} ({user.role}): {order_count} orders")

if __name__ == "__main__":
    fix_order_assignments()
