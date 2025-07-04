#!/usr/bin/env python3
"""
Test script to create sample campaign data for testing
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import PromotionalCampaign
from datetime import datetime, timedelta

def create_sample_campaigns():
    """Create sample campaigns for testing"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Creating sample campaigns for testing...")
            
            # Check if campaigns already exist
            existing_campaigns = PromotionalCampaign.query.count()
            print(f"Found {existing_campaigns} existing campaigns")
            
            if existing_campaigns == 0:
                # Create sample campaigns
                campaigns = [
                    {
                        'name': 'Summer Loyalty Boost',
                        'description': 'Double points on all orders during summer season',
                        'bonus_multiplier': 2.0,
                        'start_date': datetime.utcnow() - timedelta(days=10),
                        'end_date': datetime.utcnow() + timedelta(days=20),
                        'status': 'active'
                    },
                    {
                        'name': 'Weekend Special',
                        'description': 'Extra points for weekend orders',
                        'bonus_multiplier': 1.5,
                        'start_date': datetime.utcnow() + timedelta(days=5),
                        'end_date': datetime.utcnow() + timedelta(days=35),
                        'status': 'active'
                    },
                    {
                        'name': 'New Customer Welcome',
                        'description': 'Triple points for first-time customers',
                        'bonus_multiplier': 3.0,
                        'start_date': datetime.utcnow() - timedelta(days=30),
                        'end_date': datetime.utcnow() - timedelta(days=5),
                        'status': 'inactive'
                    }
                ]
                
                for campaign_data in campaigns:
                    campaign = PromotionalCampaign(**campaign_data)
                    db.session.add(campaign)
                
                db.session.commit()
                print(f"✓ Created {len(campaigns)} sample campaigns")
            else:
                print("✓ Sample campaigns already exist")
            
            # List all campaigns
            all_campaigns = PromotionalCampaign.query.all()
            print(f"\nCurrent campaigns:")
            for campaign in all_campaigns:
                status_info = f"({campaign.status})"
                if campaign.start_date and campaign.end_date:
                    now = datetime.utcnow()
                    if campaign.start_date <= now <= campaign.end_date:
                        status_info = f"(active - running)"
                    elif campaign.start_date > now:
                        status_info = f"(scheduled)"
                    else:
                        status_info = f"(expired)"
                
                print(f"  - {campaign.name}: {campaign.bonus_multiplier}x multiplier {status_info}")
                print(f"    URL: /admin/campaign-statistics/{campaign.campaign_id}")
            
            print("\n✓ Sample campaign data ready for testing!")
            
        except Exception as e:
            print(f"✗ Error creating sample campaigns: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    create_sample_campaigns()
