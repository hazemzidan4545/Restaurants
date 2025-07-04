#!/usr/bin/env python3
"""
Test script to verify campaign statistics page functionality
"""

from app import app, db
from app.models import Campaign
from datetime import datetime, timedelta
import requests
import json

def test_campaign_statistics():
    with app.app_context():
        # Check if any campaigns exist
        campaigns = Campaign.query.all()
        print(f"Found {len(campaigns)} campaigns in database")
        
        if not campaigns:
            # Create a test campaign
            print("Creating test campaign...")
            test_campaign = Campaign(
                name="Test Campaign",
                description="Test campaign for statistics verification",
                bonus_multiplier=2.0,
                start_date=datetime.utcnow() - timedelta(days=5),
                end_date=datetime.utcnow() + timedelta(days=5),
                status='active'
            )
            db.session.add(test_campaign)
            db.session.commit()
            print(f"Created campaign: {test_campaign.name} (ID: {test_campaign.campaign_id})")
            campaigns = [test_campaign]
        
        # Test the first campaign
        campaign = campaigns[0]
        print(f"\nTesting campaign: {campaign.name} (ID: {campaign.campaign_id})")
        
        # Test if the route exists and works
        try:
            # Start a test client
            with app.test_client() as client:
                # Try to access the campaign statistics page
                response = client.get(f'/admin/campaign_statistics/{campaign.campaign_id}')
                print(f"Response status: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ Campaign statistics page loads successfully")
                    
                    # Check if the page contains expected elements
                    response_text = response.data.decode('utf-8')
                    
                    # Check for campaign name
                    if campaign.name in response_text:
                        print("✅ Campaign name appears in the page")
                    else:
                        print("❌ Campaign name not found in the page")
                    
                    # Check for statistics cards
                    if "Orders Affected" in response_text:
                        print("✅ Statistics cards are present")
                    else:
                        print("❌ Statistics cards not found")
                    
                    # Check for back button
                    if "Back to Campaigns" in response_text:
                        print("✅ Navigation back button is present")
                    else:
                        print("❌ Back button not found")
                        
                    # Check for JavaScript
                    if "progress-circle" in response_text:
                        print("✅ JavaScript functionality is included")
                    else:
                        print("❌ JavaScript functionality not found")
                        
                else:
                    print(f"❌ Failed to load page: {response.status_code}")
                    if response.status_code == 404:
                        print("   Route may not be properly configured")
                    elif response.status_code == 500:
                        print("   Server error - check template or route logic")
                        
        except Exception as e:
            print(f"❌ Error testing campaign statistics: {str(e)}")
        
        print("\n" + "="*50)
        print("Campaign Statistics Test Complete")

if __name__ == "__main__":
    test_campaign_statistics()
