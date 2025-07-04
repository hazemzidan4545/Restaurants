#!/usr/bin/env python3
"""Simple loyalty system test and fix utility"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, User, Order, CustomerLoyalty, PointTransaction, LoyaltyProgram
from app.modules.loyalty.loyalty_service import award_points_for_order
from sqlalchemy import func
from datetime import datetime, timedelta

def main():
    print("Starting loyalty system test and fix...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Test 1: Check if loyalty program exists
            program = LoyaltyProgram.query.filter_by(status='active').first()
            if not program:
                print("Creating default loyalty program...")
                program = LoyaltyProgram(
                    name='Default Rewards Program',
                    description='Earn 100 points per 50 EGP spent',
                    points_per_50EGP=100,
                    status='active'
                )
                db.session.add(program)
                db.session.commit()
                print("✅ Default loyalty program created")
            else:
                print("✅ Loyalty program exists")
            
            # Test 2: Find completed orders without points
            completed_orders = Order.query.filter_by(status='completed').all()
            print(f"Found {len(completed_orders)} completed orders")
            
            fixed_orders = 0
            for order in completed_orders:
                existing = PointTransaction.query.filter_by(
                    order_id=order.order_id,
                    transaction_type='earned'
                ).first()
                
                if not existing:
                    # Ensure customer has loyalty account
                    loyalty = CustomerLoyalty.query.filter_by(user_id=order.user_id).first()
                    if not loyalty:
                        loyalty = CustomerLoyalty(user_id=order.user_id)
                        db.session.add(loyalty)
                        db.session.commit()
                    
                    # Award points
                    try:
                        result = award_points_for_order(order.order_id, order.user_id)
                        if result:
                            fixed_orders += 1
                            user = User.query.get(order.user_id)
                            print(f"✅ Fixed Order {order.order_id}: {order.total_amount} EGP for {user.name if user else 'Unknown'}")
                    except Exception as e:
                        print(f"❌ Error fixing Order {order.order_id}: {e}")
            
            print(f"Fixed {fixed_orders} orders")
            
            # Test 3: Verify current state
            print("\n=== CURRENT LOYALTY STATUS ===")
            customers = CustomerLoyalty.query.all()
            
            for loyalty in customers:
                user = User.query.get(loyalty.user_id)
                total_spent = db.session.query(func.sum(Order.total_amount)).filter(
                    Order.user_id == loyalty.user_id,
                    Order.status.in_(['completed', 'delivered'])
                ).scalar() or 0
                
                completed_count = Order.query.filter(
                    Order.user_id == loyalty.user_id,
                    Order.status.in_(['completed', 'delivered'])
                ).count()
                
                print(f"{user.name if user else 'Unknown'}:")
                print(f"  Points: {loyalty.total_points}")
                print(f"  Tier: {loyalty.tier_level}")
                print(f"  Total Spent: {float(total_spent):.2f} EGP")
                print(f"  Orders: {completed_count}")
                print()
            
            print("=== LOYALTY SYSTEM CHECK COMPLETE ===")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
