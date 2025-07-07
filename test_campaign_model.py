#!/usr/bin/env python3
"""
Test the PromotionalCampaign model to see if it loads correctly
"""

from app import create_app
from app.extensions import db
from app.models import PromotionalCampaign

def test_model():
    app = create_app()
    
    with app.app_context():
        try:
            # Try to query the campaigns table
            campaigns = PromotionalCampaign.query.limit(5).all()
            print(f"✅ Successfully loaded {len(campaigns)} campaigns")
            
            for campaign in campaigns:
                print(f"  - {campaign.name} (ID: {campaign.campaign_id})")
                print(f"    Minimum order: {campaign.minimum_order_amount}")
                print(f"    Target tier: {campaign.target_customer_tier}")
                print(f"    Discount type: {campaign.discount_type}")
                
        except Exception as e:
            print(f"❌ Error loading campaigns: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_model()
