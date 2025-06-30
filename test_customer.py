#!/usr/bin/env python3
"""
Test customer homepage and services access
"""

import requests

def test_customer_homepage():
    print("🏠 Testing Customer Homepage")
    print("=" * 40)
    
    try:
        # Test customer home page
        response = requests.get('http://localhost:5000/customer/', timeout=5)
        print(f"Customer home page status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Check if personalized welcome is present (when authenticated)
            if 'Welcome back,' in content:
                print("✅ Personalized welcome message found")
            elif 'Welcome to Hive Restaurant' in content:
                print("✅ Default welcome message found (guest)")
            else:
                print("⚠️  Welcome message not found")
            
            # Check if Services button is present
            if 'Services' in content:
                print("✅ Services button/link found")
            else:
                print("❌ Services button/link missing")
                
            # Check if Menu button is present
            if 'Menu' in content:
                print("✅ Menu button/link found")
            else:
                print("❌ Menu button/link missing")
                
        else:
            print(f"❌ Customer home page failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

def test_services_access():
    print("\n🔧 Testing Services Page Access")
    print("=" * 40)
    
    try:
        # Test services page
        response = requests.get('http://localhost:5000/service/', timeout=5)
        print(f"Services page status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Check if service buttons are present
            if 'Call Waiter' in content:
                print("✅ Service buttons found")
            else:
                print("❌ Service buttons missing")
                
            # Check if JavaScript functionality is present
            if 'submitServiceRequest' in content:
                print("✅ Service request JavaScript found")
            else:
                print("❌ Service request JavaScript missing")
                
        else:
            print(f"❌ Services page failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    print("🧪 Customer Access Test Suite")
    print("=" * 50)
    
    test_customer_homepage()
    test_services_access()
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")
    print("\n📝 Manual Testing:")
    print("1. Open: http://localhost:5000/customer/")
    print("   - Should see personalized welcome (if logged in)")
    print("   - Should have Menu and Services buttons")
    print("2. Click Services button or navigate to /service/")
    print("   - Should be able to request services")
    print("   - Should prompt for table number")
    print("3. Test navigation menu:")
    print("   - Services should be available in mobile menu")
