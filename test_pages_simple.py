#!/usr/bin/env python3
"""
Simple test to verify all modal-to-page conversions are working
"""

import requests
import sys

def test_page(url, page_name):
    """Test if a page loads successfully"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {page_name}: OK")
            return True
        else:
            print(f"❌ {page_name}: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {page_name}: Error - {str(e)}")
        return False

def main():
    base_url = "http://localhost:5000"
    
    print("=== Testing Modal-to-Page Conversions ===\n")
    
    # Test main pages
    main_pages = [
        ("/admin/loyalty", "Loyalty Management"),
        ("/admin/campaigns", "Campaigns Management"),
    ]
    
    print("Main Pages:")
    for url, name in main_pages:
        test_page(f"{base_url}{url}", name)
    
    print("\nLoyalty Management Pages:")
    # Test loyalty management pages
    loyalty_pages = [
        ("/admin/loyalty/settings", "Loyalty Settings"),
        ("/admin/loyalty/adjust-points", "Adjust Points"),
        ("/admin/loyalty/transactions", "Loyalty Transactions"),
    ]
    
    for url, name in loyalty_pages:
        test_page(f"{base_url}{url}", name)
    
    print("\nCampaign Pages:")
    # Test campaign pages
    campaign_pages = [
        ("/admin/campaigns/statistics", "Campaign Statistics"),
    ]
    
    for url, name in campaign_pages:
        test_page(f"{base_url}{url}", name)
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
