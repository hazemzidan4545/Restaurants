#!/usr/bin/env python3
"""
Simple check of all users and what they should see in payment history
"""

from app import create_app
from app.models import User, Order, Payment, db

def check_user_payments():
    app = create_app()
    
    with app.app_context():
        print("=== USER PAYMENT SUMMARY ===\n")
        
        users = User.query.all()
        total_payments = Payment.query.count()
        
        print(f"📊 Database Overview:")
        print(f"   Total Users: {len(users)}")
        print(f"   Total Payments: {total_payments}")
        print()
        
        if total_payments == 0:
            print("❌ NO PAYMENTS IN DATABASE")
            print("This is why the payment history shows 'No payments found'")
            print("\nTo fix this, create some test data:")
            print("   python create_full_payment_data.py")
            return
        
        print(f"👥 What each user should see:")
        print()
        
        for user in users:
            # Get payments for this specific user
            if user.role == 'customer':
                user_payments = Payment.query.join(Order).filter(Order.user_id == user.user_id).all()
                print(f"🔑 Login as: {user.username} (Customer)")
                print(f"   Password: password (probably)")
                print(f"   Will see: {len(user_payments)} payments")
                
                if user_payments:
                    for payment in user_payments:
                        print(f"     • ${payment.amount} via {payment.payment_type} ({payment.status})")
                else:
                    print(f"     • No payments (will see 'No payments found')")
                print()
                
            elif user.role == 'admin':
                print(f"👑 Login as: {user.username} (Admin)")
                print(f"   Password: password (probably)")
                print(f"   Will see: ALL {total_payments} payments from all users")
                print()
        
        # Show all payments with their owners
        if total_payments > 0:
            print(f"💳 All Payments in Database:")
            all_payments = Payment.query.all()
            for payment in all_payments:
                try:
                    customer = payment.order.customer
                    owner = customer.username if customer else "Unknown"
                except:
                    owner = "Error"
                print(f"   Payment #{payment.payment_id}: ${payment.amount} ({payment.payment_type}) - Owner: {owner}")
        
        print(f"\n📋 INSTRUCTIONS:")
        print(f"1. Choose a user from the list above")
        print(f"2. Login with their credentials")  
        print(f"3. Go to Payment History")
        print(f"4. You should see the number of payments listed for that user")
        
        # Recommend the best test user
        customer_with_payments = None
        for user in users:
            if user.role == 'customer':
                user_payments = Payment.query.join(Order).filter(Order.user_id == user.user_id).count()
                if user_payments > 0:
                    customer_with_payments = user
                    break
        
        if customer_with_payments:
            payments_count = Payment.query.join(Order).filter(Order.user_id == customer_with_payments.user_id).count()
            print(f"\n✅ RECOMMENDED TEST:")
            print(f"   Login as: {customer_with_payments.username}")
            print(f"   Expected result: {payments_count} payments should appear")

if __name__ == "__main__":
    check_user_payments()
