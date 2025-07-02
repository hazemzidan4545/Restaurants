#!/usr/bin/env python3
"""
Debug script for reorder-to-cart functionality
"""

import requests
import json

# Test the reorder-to-cart route directly
BASE_URL = "http://localhost:5000"

def debug_reorder_route():
    """Debug the reorder-to-cart route"""
    print("🔍 Debugging reorder-to-cart route...")
    
    # Create a session
    session = requests.Session()
    
    # Login first
    print("\n1. Attempting login...")
    login_data = {
        "username": "customer1",
        "password": "password123"
    }
    
    try:
        login_response = session.post(f"{BASE_URL}/auth/login", data=login_data, allow_redirects=False)
        print(f"   Login status: {login_response.status_code}")
        
        if login_response.status_code == 302:  # Redirect after successful login
            print("   ✅ Login appears successful (got redirect)")
        else:
            print(f"   Response text: {login_response.text[:200]}...")
    
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return
    
    # Try to access customer orders page
    print("\n2. Accessing customer orders page...")
    try:
        orders_response = session.get(f"{BASE_URL}/customer/orders")
        print(f"   Orders page status: {orders_response.status_code}")
        
        if orders_response.status_code == 200:
            print("   ✅ Successfully accessed orders page")
            
            # Look for order IDs
            import re
            order_ids = re.findall(r'data-order-id="(\d+)"', orders_response.text)
            print(f"   Found order IDs: {order_ids}")
            
            if order_ids:
                test_order_id = order_ids[0]
                print(f"   Will test with order ID: {test_order_id}")
                
                # Test the reorder-to-cart route
                print(f"\n3. Testing reorder-to-cart route for order {test_order_id}...")
                try:
                    reorder_response = session.post(
                        f"{BASE_URL}/customer/order/{test_order_id}/reorder-to-cart",
                        headers={'Content-Type': 'application/json'}
                    )
                    print(f"   Status: {reorder_response.status_code}")
                    print(f"   Response: {reorder_response.text}")
                    
                    if reorder_response.status_code == 200:
                        result = reorder_response.json()
                        if result.get('success'):
                            print("   ✅ Reorder-to-cart successful!")
                        else:
                            print(f"   ❌ Reorder failed: {result.get('message')}")
                    
                except Exception as e:
                    print(f"   ❌ Reorder request error: {e}")
            else:
                print("   ⚠️ No orders found to test with")
        else:
            print(f"   ❌ Could not access orders page: {orders_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Orders page error: {e}")

if __name__ == "__main__":
    debug_reorder_route()
