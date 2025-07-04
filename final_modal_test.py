#!/usr/bin/env python3
"""
Final test to verify all modal-to-page conversions are working
"""
import requests
import sys

def test_page(url, description):
    """Test if a page is accessible"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {description}: Working (Status 200)")
            return True
        elif response.status_code == 404:
            print(f"❌ {description}: Not Found (Status 404)")
            return False
        else:
            print(f"⚠️ {description}: Status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {description}: Connection refused (Flask not running?)")
        return False
    except Exception as e:
        print(f"❌ {description}: Error - {e}")
        return False

def main():
    print("🔍 FINAL MODAL-TO-PAGE CONVERSION TEST")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5000/admin"
    working_pages = 0
    total_pages = 0
    
    # Test main management pages
    print("\n📊 MAIN MANAGEMENT PAGES:")
    pages = [
        (f"{base_url}/loyalty-management", "Loyalty Management"),
        (f"{base_url}/campaigns-management", "Campaigns Management"),
    ]
    
    for url, desc in pages:
        total_pages += 1
        if test_page(url, desc):
            working_pages += 1
    
    # Test loyalty system pages
    print("\n💎 LOYALTY SYSTEM PAGES:")
    loyalty_pages = [
        (f"{base_url}/loyalty-settings", "Loyalty Settings"),
        (f"{base_url}/loyalty-adjust-points", "Adjust Points"),
        (f"{base_url}/loyalty-customer-details/1", "Customer Details (ID: 1)"),
        (f"{base_url}/loyalty-transactions/1", "Customer Transactions (ID: 1)"),
    ]
    
    for url, desc in loyalty_pages:
        total_pages += 1
        if test_page(url, desc):
            working_pages += 1
    
    # Test campaign pages
    print("\n📢 CAMPAIGN PAGES:")
    campaign_pages = [
        (f"{base_url}/campaigns/add", "Add Campaign"),
        (f"{base_url}/campaign-statistics/1", "Campaign Statistics (ID: 1)"),
    ]
    
    for url, desc in campaign_pages:
        total_pages += 1
        if test_page(url, desc):
            working_pages += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📈 RESULTS: {working_pages}/{total_pages} pages working")
    
    if working_pages == total_pages:
        print("🎉 ALL PAGES ARE WORKING! Modal conversion complete!")
        return True
    else:
        print(f"⚠️ {total_pages - working_pages} pages need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
