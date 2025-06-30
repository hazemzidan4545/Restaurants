#!/usr/bin/env python3
"""
Test service functionality for customers
"""

from app import create_app
from app.models import Service

app = create_app()

# Test the customer menu route
with app.test_client() as client:
    with app.app_context():
        # Check if services are being fetched
        services = Service.query.filter_by(is_active=True).order_by(Service.display_order, Service.name).all()
        print(f'Active services found: {len(services)}')
        
        for service in services:
            print(f'- {service.name} (Icon: {service.icon})')
        
        # Test the menu route
        response = client.get('/customer/menu')
        print(f'\nMenu route status: {response.status_code}')
        
        if response.status_code == 200:
            print('✅ Customer menu route is working')
            # Check if 'services-grid' is in the response data (this would be passed to template)
            if b'services-grid' in response.data:
                print('✅ Services section found in template')
            else:
                print('❌ Services section not found in template')
        else:
            print(f'❌ Customer menu route failed: {response.status_code}')
    print("=" * 40)
    
    # Test 1: Get services
    print("1. Testing GET /service/api/services")
    try:
        response = requests.get('http://localhost:5000/service/api/services')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            services = data.get('services', [])
            print(f"   ✅ Found {len(services)} services")
            for service in services[:3]:
                print(f"      - {service['name']}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 2: Create service request
    print("2. Testing POST /service/api/request")
    try:
        request_data = {
            'table_id': 1,
            'request_type': 'call_waiter',
            'description': 'Customer needs assistance'
        }
        response = requests.post(
            'http://localhost:5000/service/api/request',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(request_data)
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"   ✅ Service request created!")
            print(f"      Request ID: {data.get('request_id')}")
            print(f"      Status: {data.get('status')}")
            print(f"      Message: {data.get('message')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 3: Test with invalid table
    print("3. Testing with invalid table ID")
    try:
        request_data = {
            'table_id': 999,  # Invalid table
            'request_type': 'call_waiter',
            'description': 'Test invalid table'
        }
        response = requests.post(
            'http://localhost:5000/service/api/request',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(request_data)
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 400:
            data = response.json()
            print(f"   ✅ Correctly rejected: {data.get('error')}")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == '__main__':
    test_service_requests()
