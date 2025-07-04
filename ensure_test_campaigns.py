#!/usr/bin/env python3
"""
Ensure test data exists for campaign statistics testing
"""

from app import app, db
from app.models import PromotionalCampaign
from datetime import datetime, timedelta

def create_test_campaign_if_needed():
    with app.app_context():
        # Check if any campaigns exist
        campaigns = PromotionalCampaign.query.all()
        print(f"Found {len(campaigns)} campaigns in database")
        
        if len(campaigns) == 0:
            print("Creating test campaign...")
            # Create a test campaign
            test_campaign = PromotionalCampaign(
                name="Holiday Special Campaign",
                description="Special holiday promotion with double points for all orders",
                bonus_multiplier=2.0,
                start_date=datetime.utcnow() - timedelta(days=7),
                end_date=datetime.utcnow() + timedelta(days=7),
                status='active'
            )
            
            db.session.add(test_campaign)
            db.session.commit()
            
            print(f"✅ Created test campaign: {test_campaign.name}")
            print(f"   Campaign ID: {test_campaign.campaign_id}")
            print(f"   Status: {test_campaign.status}")
            print(f"   Dates: {test_campaign.start_date} to {test_campaign.end_date}")
        else:
            print("✅ Campaigns already exist:")
            for campaign in campaigns:
                print(f"   - {campaign.name} (ID: {campaign.campaign_id}, Status: {campaign.status})")
        
        print(f"\n🔗 Test the campaign statistics page at:")
        campaigns = PromotionalCampaign.query.all()
        for campaign in campaigns:
            print(f"   http://localhost:5000/admin/campaign-statistics/{campaign.campaign_id}")

if __name__ == "__main__":
    create_test_campaign_if_needed()
