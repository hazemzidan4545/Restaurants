#!/usr/bin/env python3
"""
Quick verification script for modal-to-page conversion
Tests key pages with shorter timeouts
"""

import requests
import sys

def test_page_quick(url, name):
    """Test page with short timeout"""
    try:
        response = requests.get(url, timeout=3)
        print(f"✓ {name}: Status {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ {name}: {str(e)}")
        return False

def main():
    print("=== Quick Modal Conversion Verification ===\n")
    
    base_url = "http://localhost:5000"
    
    pages = [
        (f"{base_url}/admin/loyalty", "Loyalty Management"),
        (f"{base_url}/admin/loyalty/settings", "Loyalty Settings"),
        (f"{base_url}/admin/loyalty/adjust-points", "Adjust Points"),
        (f"{base_url}/admin/campaigns", "Campaigns Management"),
    ]
    
    success_count = 0
    for url, name in pages:
        if test_page_quick(url, name):
            success_count += 1
    
    print(f"\n{success_count}/{len(pages)} pages working correctly")
    
    if success_count == len(pages):
        print("🎉 All main pages are working!")
    else:
        print("⚠️ Some pages need attention")

if __name__ == "__main__":
    main()
