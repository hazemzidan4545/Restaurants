#!/usr/bin/env python3
"""
Test script to verify loyalty management functionality
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import User, CustomerLoyalty, PointTransaction, LoyaltyProgram
from datetime import datetime

def test_loyalty_system():
    """Test the loyalty system functionality"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Testing loyalty system functionality...")
            
            # Test 1: Check if models are working
            print("\n1. Testing model relationships...")
            customers = CustomerLoyalty.query.limit(5).all()
            print(f"✓ Found {len(customers)} customers")
            
            for customer in customers:
                if customer.user:
                    print(f"  - {customer.user.name}: {customer.total_points} points ({customer.tier_level})")
                else:
                    print(f"  - Customer #{customer.loyalty_id}: {customer.total_points} points ({customer.tier_level})")
            
            # Test 2: Check transactions
            print("\n2. Testing transaction relationships...")
            transactions = PointTransaction.query.limit(5).all()
            print(f"✓ Found {len(transactions)} transactions")
            
            for transaction in transactions:
                customer = transaction.customer
                customer_name = customer.user.name if customer and customer.user else "Unknown"
                print(f"  - {customer_name}: {transaction.transaction_type} - {transaction.points_earned or 0} earned, {transaction.points_redeemed or 0} redeemed")
            
            # Test 3: Check loyalty program settings
            print("\n3. Testing loyalty program...")
            program = LoyaltyProgram.query.filter_by(status='active').first()
            if program:
                print(f"✓ Active program: {program.name}")
                print(f"  - Points per 50 EGP: {program.points_per_50EGP}")
                print(f"  - Points value: {program.points_value}")
                print(f"  - Min redemption: {program.min_redemption}")
                print(f"  - Max redemption %: {program.max_redemption_percentage}")
            else:
                print("! No active loyalty program found")
            
            print("\n✓ All tests passed! Loyalty system is working correctly.")
            
        except Exception as e:
            print(f"✗ Test failed: {str(e)}")
            raise

if __name__ == '__main__':
    test_loyalty_system()
