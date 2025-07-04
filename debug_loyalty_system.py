#!/usr/bin/env python3
"""Debug loyalty system issues"""

from app import create_app
from app.models import db, User, Order, CustomerLoyalty, PointTransaction, MenuItem, OrderItem
from app.modules.loyalty.loyalty_service import award_points_for_order
from sqlalchemy import func
from datetime import datetime

def debug_loyalty_issues():
    """Debug both loyalty system issues"""
    app = create_app()
    
    with app.app_context():
        print("=== DEBUGGING LOYALTY SYSTEM ISSUES ===\n")
        
        # Issue 1: Check if points are being awarded on order completion
        print("1. Checking Point Awarding System...")
        print("-" * 50)
        
        # Find a customer to test with
        customer = User.query.filter_by(role='customer').first()
        if not customer:
            print("❌ No customer found")
            return
            
        print(f"Testing with customer: {customer.name} (ID: {customer.user_id})")
        
        # Check if customer has loyalty account
        loyalty = CustomerLoyalty.query.filter_by(user_id=customer.user_id).first()
        if not loyalty:
            print("   Creating loyalty account...")
            loyalty = CustomerLoyalty(user_id=customer.user_id)
            db.session.add(loyalty)
            db.session.commit()
        
        points_before = loyalty.total_points
        print(f"   Current points: {points_before}")
        
        # Create a new test order
        test_order = Order(
            user_id=customer.user_id,
            status='new',
            total_amount=100.00,  # 100 EGP should give 200 points
            order_time=datetime.utcnow(),
            notes='Test order for loyalty debugging'
        )
        db.session.add(test_order)
        db.session.flush()
        
        # Add order item
        menu_item = MenuItem.query.first()
        if menu_item:
            order_item = OrderItem(
                order_id=test_order.order_id,
                item_id=menu_item.item_id,
                quantity=1,
                unit_price=100.00
            )
            db.session.add(order_item)
        
        db.session.commit()
        print(f"   Created test order {test_order.order_id} for 100 EGP")
        
        # Mark order as completed
        test_order.status = 'completed'
        db.session.commit()
        print("   Marked order as completed")
        
        # Try to award points
        result = award_points_for_order(test_order.order_id, customer.user_id)
        print(f"   Point awarding result: {result}")
        
        # Check if points were awarded
        db.session.refresh(loyalty)
        points_after = loyalty.total_points
        points_earned = points_after - points_before
        
        print(f"   Points after: {points_after}")
        print(f"   Points earned: {points_earned}")
        
        if points_earned > 0:
            print("   ✅ Points are being awarded correctly!")
        else:
            print("   ❌ Points are NOT being awarded!")
        
        # Issue 2: Check admin total spent calculation
        print("\n2. Checking Admin Total Spent Calculation...")
        print("-" * 50)
        
        # Get all customers with loyalty accounts
        customers = CustomerLoyalty.query.all()
        print(f"Found {len(customers)} loyalty customers:")
        
        for customer_loyalty in customers:
            # Calculate total spent (same logic as admin route)
            total_spent = db.session.query(func.sum(Order.total_amount)).filter(
                Order.user_id == customer_loyalty.user_id,
                Order.status.in_(['completed', 'delivered'])
            ).scalar() or 0
            
            user = User.query.get(customer_loyalty.user_id)
            completed_orders = Order.query.filter(
                Order.user_id == customer_loyalty.user_id,
                Order.status.in_(['completed', 'delivered'])
            ).count()
            
            print(f"   • {user.name if user else 'Unknown'}:")
            print(f"     - Points: {customer_loyalty.total_points}")
            print(f"     - Tier: {customer_loyalty.tier_level}")
            print(f"     - Completed Orders: {completed_orders}")
            print(f"     - Total Spent: {float(total_spent):.2f} EGP")
            
            # Check if this matches what should be displayed in admin
            if total_spent > 0:
                print(f"     ✅ Has spending data")
            else:
                print(f"     ⚠️  No spending data (may be new customer)")
            print()
        
        # Issue 3: Check currency display
        print("3. Checking Currency Display...")
        print("-" * 50)
        
        # Check recent orders and their amounts
        recent_orders = Order.query.filter(
            Order.status.in_(['completed', 'delivered'])
        ).order_by(Order.order_time.desc()).limit(5).all()
        
        print("Recent completed orders:")
        for order in recent_orders:
            user = User.query.get(order.user_id)
            print(f"   • Order {order.order_id}: {order.total_amount} EGP by {user.name if user else 'Unknown'}")
        
        # Check point transactions
        recent_transactions = PointTransaction.query.filter(
            PointTransaction.transaction_type == 'earned'
        ).order_by(PointTransaction.timestamp.desc()).limit(5).all()
        
        print("\nRecent point transactions:")
        for transaction in recent_transactions:
            user = User.query.get(transaction.user_id)
            print(f"   • {user.name if user else 'Unknown'}: +{transaction.points_earned} points")
            print(f"     Description: {transaction.description}")
        
        print("\n=== DEBUGGING COMPLETE ===")

if __name__ == "__main__":
    debug_loyalty_issues()
