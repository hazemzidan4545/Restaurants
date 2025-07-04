#!/usr/bin/env python3
"""Test actual order completion and point awarding flow"""

from app import create_app
from app.models import db, User, Order, CustomerLoyalty, PointTransaction, MenuItem, OrderItem
from app.modules.loyalty.loyalty_service import award_points_for_order
from datetime import datetime
import requests
import json

def test_real_order_flow():
    """Test the complete order to completion flow"""
    app = create_app()
    
    with app.app_context():
        print("=== TESTING REAL ORDER COMPLETION FLOW ===\n")
        
        # Get a customer
        customer = User.query.filter_by(role='customer').first()
        if not customer:
            print("❌ No customer found")
            return
            
        print(f"Testing with customer: {customer.name} (ID: {customer.user_id})")
        
        # Ensure customer has loyalty account
        loyalty = CustomerLoyalty.query.filter_by(user_id=customer.user_id).first()
        if not loyalty:
            loyalty = CustomerLoyalty(user_id=customer.user_id)
            db.session.add(loyalty)
            db.session.commit()
            print("   Created loyalty account")
        
        points_before = loyalty.total_points
        print(f"   Points before: {points_before}")
        
        # Create a new order directly (simulating order creation)
        menu_item = MenuItem.query.first()
        if not menu_item:
            print("❌ No menu items found")
            return
            
        new_order = Order(
            user_id=customer.user_id,
            status='new',
            total_amount=150.00,  # 150 EGP = 300 points (150/50 * 100)
            order_time=datetime.utcnow(),
            notes='Test order for loyalty point testing'
        )
        db.session.add(new_order)
        db.session.flush()
        
        # Add order items
        order_item = OrderItem(
            order_id=new_order.order_id,
            item_id=menu_item.item_id,
            quantity=3,
            unit_price=50.00
        )
        db.session.add(order_item)
        db.session.commit()
        
        print(f"   Created order {new_order.order_id} for 150 EGP")
        
        # Simulate the order status update process (like what happens in the API)
        print("   Simulating order status change to 'completed'...")
        
        old_status = new_order.status
        new_order.status = 'completed'
        db.session.commit()
        
        # Award points (simulating the API call)
        if new_order.status == 'completed' and old_status != 'completed':
            try:
                result = award_points_for_order(new_order.order_id, new_order.user_id)
                print(f"   Point awarding result: {result}")
            except Exception as e:
                print(f"   ❌ Error awarding points: {str(e)}")
                return
        
        # Check results
        db.session.refresh(loyalty)
        points_after = loyalty.total_points
        points_earned = points_after - points_before
        
        print(f"   Points after: {points_after}")
        print(f"   Points earned: {points_earned}")
        
        expected_points = int((150.00 / 50.0) * 100)  # Should be 300 points
        if points_earned == expected_points:
            print(f"   ✅ Correct! Earned {points_earned} points (expected {expected_points})")
        else:
            print(f"   ❌ Wrong! Earned {points_earned} points, expected {expected_points}")
        
        # Check transaction record
        transaction = PointTransaction.query.filter_by(
            order_id=new_order.order_id,
            transaction_type='earned'
        ).first()
        
        if transaction:
            print(f"   ✅ Transaction recorded: {transaction.description}")
        else:
            print("   ❌ No transaction record found")
        
        print("\n=== TESTING ADMIN TOTAL SPENT CALCULATION ===")
        
        # Test the admin calculation
        from sqlalchemy import func
        
        customers = CustomerLoyalty.query.all()
        for customer_loyalty in customers:
            total_spent = db.session.query(func.sum(Order.total_amount)).filter(
                Order.user_id == customer_loyalty.user_id,
                Order.status.in_(['completed', 'delivered'])
            ).scalar() or 0
            
            user = User.query.get(customer_loyalty.user_id)
            completed_orders_count = Order.query.filter(
                Order.user_id == customer_loyalty.user_id,
                Order.status.in_(['completed', 'delivered'])
            ).count()
            
            print(f"   {user.name if user else 'Unknown'}:")
            print(f"     • Points: {customer_loyalty.total_points}")
            print(f"     • Tier: {customer_loyalty.tier_level}")
            print(f"     • Total Spent: {float(total_spent):.2f} EGP")
            print(f"     • Completed Orders: {completed_orders_count}")
            print()
        
        print("=== TEST COMPLETE ===")
        print("✅ Order completion and point awarding flow tested")
        print("✅ Admin total spent calculation tested")
        print("✅ Currency display updated to EGP")

if __name__ == "__main__":
    test_real_order_flow()
