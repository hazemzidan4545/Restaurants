#!/usr/bin/env python3
"""
Test QR Code Regeneration API
Tests the fixed QR code generation endpoints
"""

import requests
import json
import time

# Wait for Flask to start
print("Waiting for Flask to start...")
time.sleep(3)

base_url = "http://localhost:5000"

def test_admin_login():
    """Test admin login"""
    session = requests.Session()
    
    # Get login page to get CSRF token
    login_page = session.get(f"{base_url}/admin/login")
    
    if login_page.status_code != 200:
        print(f"❌ Cannot access login page: {login_page.status_code}")
        return None
        
    # Try to extract CSRF token (simplified)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(login_page.text, 'html.parser')
    csrf_token = None
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    if csrf_input:
        csrf_token = csrf_input.get('value')
    
    # Login with admin credentials
    login_data = {
        'username': 'admin',
        'password': 'admin123',
    }
    if csrf_token:
        login_data['csrf_token'] = csrf_token
    
    login_response = session.post(f"{base_url}/admin/login", data=login_data)
    
    if "dashboard" in login_response.url or login_response.status_code == 200:
        print("✅ Admin login successful")
        return session
    else:
        print(f"❌ Admin login failed: {login_response.status_code}")
        return None

def test_single_qr_generation(session):
    """Test single QR code generation"""
    print("\n🔧 Testing single QR code generation...")
    
    # Get first table ID
    try:
        # Test with table ID 1
        response = session.post(f"{base_url}/admin/api/qr-codes/generate/1")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Single QR code generation working")
                return True
            else:
                print(f"❌ Single QR generation failed: {data.get('message')}")
                return False
        else:
            print(f"❌ Single QR generation failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing single QR generation: {e}")
        return False

def test_bulk_qr_generation(session):
    """Test bulk QR code generation"""
    print("\n🔧 Testing bulk QR code generation...")
    
    try:
        response = session.post(f"{base_url}/admin/api/qr-codes/generate-all")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Bulk QR code generation working")
                print(f"Message: {data.get('message')}")
                return True
            else:
                print(f"❌ Bulk QR generation failed: {data.get('message')}")
                return False
        else:
            print(f"❌ Bulk QR generation failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing bulk QR generation: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing QR Code Regeneration Fix")
    print("=" * 50)
    
    # Test admin login
    session = test_admin_login()
    if not session:
        print("❌ Cannot proceed without admin session")
        return
    
    # Test single QR generation
    single_success = test_single_qr_generation(session)
    
    # Test bulk QR generation
    bulk_success = test_bulk_qr_generation(session)
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"Single QR Generation: {'✅ PASS' if single_success else '❌ FAIL'}")
    print(f"Bulk QR Generation: {'✅ PASS' if bulk_success else '❌ FAIL'}")
    
    if single_success and bulk_success:
        print("\n🎉 All QR code generation tests PASSED!")
        print("The regeneration issue has been fixed.")
    else:
        print("\n⚠️  Some tests failed. The fix may need adjustment.")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ Test script error: {e}")
