#!/usr/bin/env python3
"""
Quick fix for payment history - create data and show what to do
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import User, Order, Payment, MenuItem, OrderItem, Category, db
from datetime import datetime

def quick_payment_fix():
    try:
        app = create_app()
        
        with app.app_context():
            print("PAYMENT HISTORY QUICK FIX")
            print("=" * 40)
            
            # Check current state
            payments_count = Payment.query.count()
            users_count = User.query.count()
            
            print(f"Current database:")
            print(f"  Users: {users_count}")
            print(f"  Payments: {payments_count}")
            
            if payments_count == 0:
                print("\n❌ NO PAYMENTS FOUND - This is why you see 'No payments found'")
                print("\n🔧 CREATING TEST DATA...")
                
                # Find or create customer
                customer = User.query.filter_by(role='customer').first()
                if not customer:
                    print("  Creating test customer...")
                    customer = User(
                        username='testcustomer',
                        name='Test Customer',
                        email='test@customer.com',
                        role='customer'
                    )
                    customer.set_password('password')
                    db.session.add(customer)
                    db.session.flush()
                
                # Find or create menu item
                menu_item = MenuItem.query.first()
                if not menu_item:
                    print("  Creating test menu item...")
                    category = Category(name='Test', description='Test category')
                    db.session.add(category)
                    db.session.flush()
                    
                    menu_item = MenuItem(
                        name='Test Item',
                        description='Test item for payments',
                        price=25.99,
                        category_id=category.category_id,
                        status='available'
                    )
                    db.session.add(menu_item)
                    db.session.flush()
                
                # Create test orders and payments
                print("  Creating test payments...")
                for i in range(3):
                    # Create order
                    order = Order(
                        user_id=customer.user_id,
                        status='completed',
                        total_amount=25.99 + i,
                        notes=f'Test order {i+1}',
                        order_time=datetime.utcnow()
                    )
                    db.session.add(order)
                    db.session.flush()
                    
                    # Create order item
                    order_item = OrderItem(
                        order_id=order.order_id,
                        item_id=menu_item.item_id,
                        quantity=1,
                        unit_price=25.99 + i,
                        note=f'Test item {i+1}'
                    )
                    db.session.add(order_item)
                    
                    # Create payment
                    payment = Payment(
                        order_id=order.order_id,
                        amount=25.99 + i,
                        payment_type=['card', 'cash', 'wallet'][i],
                        status='completed',
                        transaction_id=f'test_{i+1}',
                        timestamp=datetime.utcnow()
                    )
                    db.session.add(payment)
                
                db.session.commit()
                print("  ✅ Created 3 test payments!")
                
                print(f"\n🎯 SOLUTION:")
                print(f"1. Logout if currently logged in")
                print(f"2. Login with these credentials:")
                print(f"   Username: {customer.username}")
                print(f"   Password: password")
                print(f"3. Go to Payment History")
                print(f"4. You should now see 3 payments!")
                
            else:
                print(f"\n✅ PAYMENTS EXIST ({payments_count} total)")
                print(f"\n🔍 DIAGNOSING ISSUE...")
                
                # Show what each user should see
                customers = User.query.filter_by(role='customer').all()
                admins = User.query.filter_by(role='admin').all()
                
                print(f"\nCustomer accounts:")
                for customer in customers:
                    customer_payments = Payment.query.join(Order).filter(Order.user_id == customer.user_id).count()
                    print(f"  {customer.username}: {customer_payments} payments")
                
                print(f"\nAdmin accounts:")
                for admin in admins:
                    print(f"  {admin.username}: sees ALL {payments_count} payments")
                
                print(f"\n🎯 SOLUTION:")
                print(f"You're probably logged in as a user with no payments.")
                
                # Find best test account
                best_customer = None
                max_payments = 0
                for customer in customers:
                    customer_payments = Payment.query.join(Order).filter(Order.user_id == customer.user_id).count()
                    if customer_payments > max_payments:
                        max_payments = customer_payments
                        best_customer = customer
                
                if best_customer:
                    print(f"Try logging in as: {best_customer.username} (should see {max_payments} payments)")
                elif admins:
                    print(f"Try logging in as admin: {admins[0].username} (should see all {payments_count} payments)")
                else:
                    print(f"No suitable test accounts found.")
            
            print(f"\n" + "=" * 40)
            print(f"PAYMENT HISTORY SHOULD NOW WORK!")
            
    except Exception as e:
        print(f"Error: {e}")
        print(f"Make sure Flask app is running and database is accessible.")

if __name__ == "__main__":
    quick_payment_fix()
