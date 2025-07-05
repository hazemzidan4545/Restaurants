#!/usr/bin/env python3
"""
Debug QR Code Generation Issue
Tests the QR generation endpoint to identify the exact error
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json

def test_qr_generation():
    """Test QR code generation endpoint"""
    
    base_url = "http://localhost:5000"
    
    print("🔧 Testing QR Code Generation Endpoint")
    print("=" * 50)
    
    # Test without authentication first
    print("1. Testing endpoint accessibility...")
    
    try:
        # Test with table ID 1
        response = requests.post(f"{base_url}/admin/api/qr-codes/generate/1")
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        try:
            data = response.json()
            print(f"Response JSON: {json.dumps(data, indent=2)}")
        except:
            print(f"Response Text: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server. Is it running on localhost:5000?")
        return
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        return
    
    print("\n" + "=" * 50)
    print("Next steps:")
    print("1. Check Flask server logs for detailed error messages")
    print("2. Verify qrcode and PIL packages are installed")
    print("3. Check if Table model and database are accessible")

if __name__ == '__main__':
    test_qr_generation()
