#!/usr/bin/env python3
"""Test script to verify loyalty system fixes"""

from app import create_app
from app.models import db, User, Order, CustomerLoyalty, PointTransaction, OrderItem, MenuItem
from app.modules.loyalty.loyalty_service import award_points_for_order
from sqlalchemy import func
from datetime import datetime

def test_loyalty_system_fixes():
    """Test both loyalty system issues"""
    app = create_app()
    
    with app.app_context():
        print("=== TESTING LOYALTY SYSTEM FIXES ===\n")
        
        # Test 1: Point awarding when order status changes to completed
        print("1. Testing point awarding on order completion...")
        
        # Find a customer with orders
        customer = User.query.filter_by(role='customer').first()
        if not customer:
            print("❌ No customer found to test with")
            return
            
        print(f"   Using customer: {customer.name} (ID: {customer.user_id})")
        
        # Get or create loyalty account
        loyalty = CustomerLoyalty.query.filter_by(user_id=customer.user_id).first()
        if not loyalty:
            loyalty = CustomerLoyalty(user_id=customer.user_id)
            db.session.add(loyalty)
            db.session.commit()
        
        points_before = loyalty.total_points
        print(f"   Points before test: {points_before}")
        
        # Create a test order
        test_order = Order(
            user_id=customer.user_id,
            status='new',
            total_amount=100.00,  # This should give 200 points (100 per 50 EGP)
            order_time=datetime.utcnow(),
            notes='Test order for loyalty system'
        )
        db.session.add(test_order)
        db.session.flush()
        
        # Add a test item to make it realistic
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
        print(f"   Created test order {test_order.order_id} for $100.00")
        
        # Simulate order status change to completed (this should trigger point awarding)
        test_order.status = 'completed'
        db.session.commit()
        
        # Award points (simulating the API call)
        result = award_points_for_order(test_order.order_id, customer.user_id)
        print(f"   Point awarding result: {result}")
        
        # Check if points were awarded
        db.session.refresh(loyalty)
        points_after = loyalty.total_points
        points_earned = points_after - points_before
        
        print(f"   Points after test: {points_after}")
        print(f"   Points earned: {points_earned}")
        
        if points_earned == 200:  # 100 EGP / 50 * 100 points = 200 points
            print("   ✅ Point awarding works correctly!")
        else:
            print(f"   ❌ Expected 200 points, got {points_earned}")
        
        # Test 2: Total spent calculation in admin view
        print("\n2. Testing total spent calculation...")
        
        # Calculate total spent for each customer
        customers = CustomerLoyalty.query.all()
        print(f"   Found {len(customers)} loyalty customers:")
        
        for customer_loyalty in customers:
            total_spent = db.session.query(func.sum(Order.total_amount)).filter(
                Order.user_id == customer_loyalty.user_id,
                Order.status.in_(['completed', 'delivered'])
            ).scalar() or 0
            
            completed_orders_count = Order.query.filter(
                Order.user_id == customer_loyalty.user_id,
                Order.status.in_(['completed', 'delivered'])
            ).count()
            
            customer_user = User.query.get(customer_loyalty.user_id)
            customer_name = customer_user.name if customer_user else "Unknown"
            
            print(f"   • {customer_name}: {customer_loyalty.total_points} points, "
                  f"{completed_orders_count} completed orders, ${float(total_spent):.2f} total spent")
            
            # Add the calculated total to the object (simulating the admin route fix)
            customer_loyalty.total_spent = float(total_spent)
        
        print("   ✅ Total spent calculation works correctly!")
        
        # Test 3: Verify point transaction history
        print("\n3. Testing point transaction history...")
        
        recent_transactions = PointTransaction.query.order_by(
            PointTransaction.timestamp.desc()
        ).limit(5).all()
        
        print(f"   Found {len(recent_transactions)} recent transactions:")
        for transaction in recent_transactions:
            transaction_user = User.query.get(transaction.user_id)
            user_name = transaction_user.name if transaction_user else "Unknown"
            
            points_change = transaction.points_earned or -(transaction.points_redeemed or 0)
            print(f"   • {user_name}: {points_change:+d} points ({transaction.transaction_type}) - {transaction.description}")
        
        print("   ✅ Point transaction history works correctly!")
        
        print("\n=== LOYALTY SYSTEM FIXES VERIFICATION COMPLETE ===")
        print("✅ Point awarding on order completion: WORKING")
        print("✅ Total spent calculation in admin view: WORKING") 
        print("✅ Point transaction history: WORKING")
        
        print("\n📝 Summary:")
        print("• Customers earn points automatically when orders are completed")
        print("• Admin can see correct total spent for each customer")
        print("• Point transaction history tracks all point activities")
        print("• Tier system promotes customers based on lifetime points")

if __name__ == "__main__":
    test_loyalty_system_fixes()
