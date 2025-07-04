#!/usr/bin/env python3
"""
Simple QR Code API Test
Tests the QR code generation without authentication
"""

import requests
import json
import sys

def test_flask_running():
    """Test if Flask is running"""
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        print(f"✅ Flask is running (Status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Flask is not running or not accessible")
        return False
    except Exception as e:
        print(f"❌ Error checking Flask: {e}")
        return False

def check_qr_endpoints():
    """Check if QR endpoints are accessible"""
    print("\n🔧 Checking QR code endpoints accessibility...")
    
    # Check if we can at least reach the endpoints (even if they return 401/403)
    endpoints = [
        "/admin/api/qr-codes/generate/1",
        "/admin/api/qr-codes/generate-all"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.post(f"http://localhost:5000{endpoint}", timeout=5)
            
            # We expect 401/403 (unauthorized) instead of 500 (server error)
            if response.status_code in [401, 403]:
                print(f"✅ Endpoint {endpoint} is accessible (requires auth)")
            elif response.status_code == 500:
                print(f"❌ Endpoint {endpoint} has server error")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('message', 'Unknown error')}")
                except:
                    print(f"   Raw error: {response.text[:200]}")
            else:
                print(f"⚠️  Endpoint {endpoint} returned: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error checking endpoint {endpoint}: {e}")

def main():
    """Main test function"""
    print("🧪 Simple QR Code API Test")
    print("=" * 40)
    
    # Test if Flask is running
    if not test_flask_running():
        print("❌ Cannot proceed - Flask is not running")
        return
    
    # Check endpoint accessibility
    check_qr_endpoints()
    
    print("\n" + "=" * 40)
    print("📝 Test completed. Check the results above.")
    print("If endpoints show server errors (500), the fix needs adjustment.")
    print("If endpoints show auth errors (401/403), the endpoints are working correctly.")

if __name__ == '__main__':
    main()
