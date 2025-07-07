#!/usr/bin/env python3
"""
Update existing campaigns with default values for new fields
"""

from app import create_app
from app.extensions import db
from app.models import PromotionalCampaign

def update_existing_campaigns():
    """Update existing campaigns with default values"""
    app = create_app()
    
    with app.app_context():
        try:
            # Get all existing campaigns
            campaigns = PromotionalCampaign.query.all()
            
            if not campaigns:
                print("✅ No existing campaigns to update")
                return
            
            print(f"🔧 Updating {len(campaigns)} existing campaigns with default values...")
            
            for campaign in campaigns:
                # Set default values for new fields if they're None
                if campaign.minimum_order_amount is None:
                    campaign.minimum_order_amount = 0.0
                
                if campaign.target_customer_tier is None:
                    campaign.target_customer_tier = 'all'
                
                if campaign.applicable_days is None:
                    campaign.applicable_days = 'all'
                
                if campaign.discount_type is None:
                    campaign.discount_type = 'points_multiplier'
                
                print(f"  ✓ Updated campaign: {campaign.name}")
            
            db.session.commit()
            print("✅ All existing campaigns updated successfully!")
            
        except Exception as e:
            print(f"❌ Update failed: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    update_existing_campaigns()
