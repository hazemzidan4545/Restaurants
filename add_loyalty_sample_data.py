#!/usr/bin/env python3
"""
Add sample loyalty program data for testing
"""

import os
import sys
from datetime import datetime, timedelta

# Add the parent directory to the path to import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import LoyaltyProgram, RewardItem, PromotionalCampaign, MenuItem

def add_sample_loyalty_data():
    """Add sample loyalty program data"""
    app = create_app('development')
    
    with app.app_context():
        print("Adding sample loyalty program data...")
        
        # Create default loyalty program if it doesn't exist
        program = LoyaltyProgram.query.filter_by(status='active').first()
        if not program:
            program = LoyaltyProgram(
                name='Restaurant Loyalty Program',
                description='Earn points with every purchase and redeem exciting rewards',
                points_per_50EGP=100,
                status='active'
            )
            db.session.add(program)
            print("✓ Created default loyalty program")
        
        # Add sample reward items
        sample_rewards = [
            {
                'name': 'Free Appetizer',
                'description': 'Get any appetizer from our menu absolutely free',
                'points_required': 500,
                'category': 'Food',
                'status': 'active'
            },
            {
                'name': 'Free Dessert',
                'description': 'Enjoy any dessert from our delicious selection',
                'points_required': 300,
                'category': 'Food',
                'status': 'active'
            },
            {
                'name': 'Free Beverage',
                'description': 'Get any non-alcoholic beverage on the house',
                'points_required': 200,
                'category': 'Beverages',
                'status': 'active'
            },
            {
                'name': '10% Discount',
                'description': '10% off your entire order',
                'points_required': 800,
                'category': 'Discounts',
                'status': 'active'
            },
            {
                'name': 'Free Main Course',
                'description': 'Choose any main course from our menu for free',
                'points_required': 1200,
                'category': 'Food',
                'status': 'active'
            },
            {
                'name': '20% Discount',
                'description': '20% off your entire order',
                'points_required': 1500,
                'category': 'Discounts',
                'status': 'active'
            },
            {
                'name': 'Free Hookah Session',
                'description': 'Enjoy a complimentary hookah session',
                'points_required': 1000,
                'category': 'Entertainment',
                'status': 'active'
            },
            {
                'name': 'VIP Table Reservation',
                'description': 'Priority reservation for VIP tables',
                'points_required': 2000,
                'category': 'Experience',
                'status': 'active'
            }
        ]
        
        rewards_added = 0
        for reward_data in sample_rewards:
            existing = RewardItem.query.filter_by(name=reward_data['name']).first()
            if not existing:
                reward = RewardItem(**reward_data)
                db.session.add(reward)
                rewards_added += 1
        
        print(f"✓ Added {rewards_added} new reward items")
        
        # Add sample promotional campaigns
        sample_campaigns = [
            {
                'name': 'Double Points Weekend',
                'description': 'Earn double points on all orders during the weekend',
                'bonus_multiplier': 2.0,
                'start_date': datetime.utcnow(),
                'end_date': datetime.utcnow() + timedelta(days=7),
                'status': 'active'
            },
            {
                'name': 'Triple Points Happy Hour',
                'description': 'Triple points during happy hour (5-7 PM)',
                'bonus_multiplier': 3.0,
                'start_date': datetime.utcnow() + timedelta(days=1),
                'end_date': datetime.utcnow() + timedelta(days=30),
                'status': 'active',
                'conditions': 'Valid during 5-7 PM only'
            },
            {
                'name': 'New Customer Bonus',
                'description': '50% bonus points for new customers',
                'bonus_multiplier': 1.5,
                'start_date': datetime.utcnow(),
                'end_date': datetime.utcnow() + timedelta(days=90),
                'status': 'active',
                'conditions': 'Valid for first-time customers only'
            },
            {
                'name': 'Holiday Special',
                'description': 'Special holiday bonus points',
                'bonus_multiplier': 2.5,
                'start_date': datetime.utcnow() + timedelta(days=30),
                'end_date': datetime.utcnow() + timedelta(days=45),
                'status': 'inactive',
                'conditions': 'Holiday promotion'
            }
        ]
        
        campaigns_added = 0
        for campaign_data in sample_campaigns:
            existing = PromotionalCampaign.query.filter_by(name=campaign_data['name']).first()
            if not existing:
                campaign = PromotionalCampaign(**campaign_data)
                db.session.add(campaign)
                campaigns_added += 1
        
        print(f"✓ Added {campaigns_added} new promotional campaigns")
        
        # Commit all changes
        db.session.commit()
        print("✓ All sample data committed to database")
        print("\nSample loyalty program data has been successfully added!")
        print("\nYou can now:")
        print("- View rewards in the admin panel")
        print("- Manage promotional campaigns")
        print("- Test the loyalty system with customer orders")

if __name__ == '__main__':
    add_sample_loyalty_data()
