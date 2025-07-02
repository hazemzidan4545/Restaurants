#!/usr/bin/env python3
"""
Test script to verify the current state of checkout and reorder functionality
"""
import requests
import sys

BASE_URL = "http://localhost:5000"

def test_checkout_and_reorder():
    """Test both checkout and reorder functionality"""
    print("🔍 Testing Checkout and Reorder Functionality...")
    
    # First get a session by logging in
    session = requests.Session()
    
    # Try to login
    login_data = {
        'email': 'customer@test.com',
        'password': 'password123'
    }
    
    print("1. Attempting login...")
    login_response = session.post(f"{BASE_URL}/auth/login", data=login_data)
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    print("✅ Login successful")
    
    # Get customer orders to find a test order
    print("\n2. Getting customer orders...")
    orders_response = session.get(f"{BASE_URL}/customer/my-orders")
    if orders_response.status_code != 200:
        print(f"❌ Failed to get orders: {orders_response.status_code}")
        return
    
    # Look for order IDs in the response
    import re
    order_ids = re.findall(r'/payment/checkout/(\d+)', orders_response.text)
    if not order_ids:
        print("❌ No orders found to test with")
        return
    
    test_order_id = order_ids[0]
    print(f"✅ Found test order ID: {test_order_id}")
    
    # Test checkout page
    print(f"\n3. Testing checkout page for order {test_order_id}...")
    checkout_response = session.get(f"{BASE_URL}/payment/checkout/{test_order_id}")
    if checkout_response.status_code != 200:
        print(f"❌ Checkout page failed: {checkout_response.status_code}")
        print(f"Response text: {checkout_response.text[:500]}...")
        return
    print("✅ Checkout page loads successfully")
    
    # Test reorder-to-cart
    print(f"\n4. Testing reorder-to-cart for order {test_order_id}...")
    reorder_response = session.post(
        f"{BASE_URL}/customer/order/{test_order_id}/reorder-to-cart",
        headers={'Content-Type': 'application/json'}
    )
    
    if reorder_response.status_code == 200:
        try:
            result = reorder_response.json()
            if result.get('success'):
                print(f"✅ Reorder-to-cart successful: {result.get('message')}")
            else:
                print(f"❌ Reorder failed: {result.get('message')}")
        except:
            print(f"❌ Reorder response not JSON: {reorder_response.text}")
    else:
        print(f"❌ Reorder-to-cart failed: {reorder_response.status_code}")
        print(f"Response: {reorder_response.text}")

if __name__ == "__main__":
    test_checkout_and_reorder()
