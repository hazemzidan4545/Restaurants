#!/usr/bin/env python3
"""
Show all users and their payment data for debugging
"""

from app import create_app
from app.models import User, Order, Payment, db

def show_all_payment_data():
    app = create_app()
    
    with app.app_context():
        print("=== ALL PAYMENT DATA ===\n")
        
        users = User.query.all()
        total_payments = Payment.query.count()
        
        print(f"Total users: {len(users)}")
        print(f"Total payments: {total_payments}")
        print()
        
        for user in users:
            # Get payments for this user through orders
            user_payments = Payment.query.join(Order).filter(Order.user_id == user.user_id).all()
            user_orders = Order.query.filter_by(user_id=user.user_id).count()
            
            print(f"👤 User: {user.username} ({user.role})")
            print(f"   ID: {user.user_id}")
            print(f"   Email: {user.email}")
            print(f"   Orders: {user_orders}")
            print(f"   Payments: {len(user_payments)}")
            
            if user_payments:
                for payment in user_payments:
                    print(f"     💳 Payment #{payment.payment_id}: ${payment.amount} ({payment.payment_type}, {payment.status})")
                    print(f"        Order #{payment.order_id}, Date: {payment.timestamp}")
            print()
        
        # Show orphaned payments (payments without valid orders)
        print("🔍 Checking for orphaned payments...")
        all_payments = Payment.query.all()
        orphaned = []
        
        for payment in all_payments:
            try:
                order = payment.order
                customer = order.customer
                if not customer:
                    orphaned.append(payment)
            except:
                orphaned.append(payment)
        
        if orphaned:
            print(f"⚠️  Found {len(orphaned)} orphaned payments:")
            for payment in orphaned:
                print(f"   Payment #{payment.payment_id}: ${payment.amount} (orphaned)")
        else:
            print("✅ No orphaned payments found")
        
        print("\n=== LOGIN INSTRUCTIONS ===")
        customer = User.query.filter_by(role='customer').first()
        if customer:
            print(f"To test payment history, login as:")
            print(f"Username: {customer.username}")
            print(f"Password: password (if it's a test account)")
            print(f"This user should see {len(Payment.query.join(Order).filter(Order.user_id == customer.user_id).all())} payments")
        
        admin = User.query.filter_by(role='admin').first()
        if admin:
            print(f"\nAdmin view (sees all payments):")
            print(f"Username: {admin.username}")
            print(f"Should see all {total_payments} payments")

if __name__ == "__main__":
    show_all_payment_data()
