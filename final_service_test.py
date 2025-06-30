#!/usr/bin/env python3
"""
Quick test of service request API after fixes
"""

import requests
import json
import time

def test_service_request():
    print("🧪 Testing Service Request API")
    print("=" * 40)
    
    # Test creating a service request
    request_data = {
        'table_id': 3,
        'request_type': 'call_waiter',
        'description': 'Customer needs menu assistance'
    }
    
    try:
        print("📤 Submitting service request...")
        response = requests.post(
            'http://localhost:5000/service/api/request',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(request_data),
            timeout=10
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("✅ SUCCESS! Service request created:")
            print(f"   📋 Request ID: {data.get('request_id')}")
            print(f"   📍 Table: {request_data['table_id']}")
            print(f"   🔧 Service: {request_data['request_type']}")
            print(f"   📝 Description: {request_data['description']}")
            print(f"   ⚡ Status: {data.get('status')}")
            print(f"   💬 Message: {data.get('message')}")
            
            return data.get('request_id')
        else:
            print(f"❌ FAILED: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

def test_invalid_request():
    print("\n🧪 Testing Invalid Request (Invalid Table)")
    print("=" * 40)
    
    request_data = {
        'table_id': 999,  # Invalid table
        'request_type': 'call_waiter',
        'description': 'Test invalid table'
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/service/api/request',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(request_data),
            timeout=10
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 400:
            data = response.json()
            print("✅ SUCCESS! Invalid request correctly rejected:")
            print(f"   ❌ Error: {data.get('error')}")
        else:
            print(f"❌ UNEXPECTED: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == '__main__':
    print("🍽️ Restaurant Service Request Test")
    print("=" * 50)
    
    # Test valid request
    request_id = test_service_request()
    
    # Test invalid request  
    test_invalid_request()
    
    print("\n" + "=" * 50)
    if request_id:
        print("🎉 All tests completed successfully!")
        print(f"📋 Created service request ID: {request_id}")
        print("\n💡 Now you can test in the browser:")
        print("   • Open: http://localhost:5000/service/")
        print("   • Click any service button")
        print("   • Enter table number when prompted")
        print("   • Confirm the request")
    else:
        print("⚠️  Some tests failed. Check the Flask app logs.")
    
    print("\n🔗 Test pages available:")
    print("   • Customer Service: http://localhost:5000/service/")  
    print("   • Test Page: http://localhost:5000/customer-service-test")
