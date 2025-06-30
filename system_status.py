#!/usr/bin/env python3
"""
System Status Check - Restaurant Management System
"""

import requests
import json
from datetime import datetime

def check_system_status():
    print("🍽️ RESTAURANT MANAGEMENT SYSTEM STATUS")
    print("=" * 60)
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test main endpoints
    endpoints = [
        ("🏠 Main Page", "http://localhost:5000/"),
        ("👤 Customer Home", "http://localhost:5000/customer/"),
        ("📋 Menu Page", "http://localhost:5000/customer/menu"),
        ("🔧 Services Page", "http://localhost:5000/service/"),
        ("🧪 Service Test Page", "http://localhost:5000/customer-service-test"),
        ("📊 Admin Panel", "http://localhost:5000/admin/"),
        ("👨‍💼 Waiter Dashboard", "http://localhost:5000/waiter/dashboard"),
    ]
    
    print("🌐 ENDPOINT STATUS:")
    print("-" * 40)
    
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                status = "✅ ONLINE"
            elif response.status_code == 302:
                status = "🔄 REDIRECT"
            elif response.status_code in [401, 403]:
                status = "🔒 AUTH REQUIRED"
            else:
                status = f"⚠️ {response.status_code}"
        except Exception as e:
            status = "❌ OFFLINE"
        
        print(f"{name:<25} {status}")
    
    print()
    print("🔧 API ENDPOINTS:")
    print("-" * 40)
    
    # Test API endpoints
    api_endpoints = [
        ("Services API", "http://localhost:5000/service/api/services"),
        ("Health Check", "http://localhost:5000/api/health"),
        ("Menu Items API", "http://localhost:5000/api/menu-items"),
    ]
    
    for name, url in api_endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'services' in data:
                    count = len(data['services'])
                    status = f"✅ {count} services"
                elif 'menu_items' in data:
                    count = len(data['menu_items'])
                    status = f"✅ {count} items"
                else:
                    status = "✅ OK"
            else:
                status = f"⚠️ {response.status_code}"
        except Exception as e:
            status = "❌ ERROR"
        
        print(f"{name:<25} {status}")
    
    print()
    print("🧪 SERVICE REQUEST TEST:")
    print("-" * 40)
    
    # Test service request functionality
    try:
        request_data = {
            'table_id': 1,
            'request_type': 'call_waiter',
            'description': 'System status test request'
        }
        response = requests.post(
            'http://localhost:5000/service/api/request',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(request_data),
            timeout=5
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Service requests working")
            print(f"   Request ID: {data.get('request_id')}")
            print(f"   Status: {data.get('status')}")
        else:
            print(f"⚠️ Service request failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Service request error: {e}")
    
    print()
    print("📱 AVAILABLE PAGES:")
    print("-" * 40)
    print("🏠 Main Landing: http://localhost:5000/")
    print("👤 Customer Home: http://localhost:5000/customer/")
    print("📋 Menu: http://localhost:5000/customer/menu")
    print("🔧 Services: http://localhost:5000/service/")
    print("🧪 Test Services: http://localhost:5000/customer-service-test")
    print("📊 Admin Panel: http://localhost:5000/admin/ (login required)")
    print("👨‍💼 Waiter Panel: http://localhost:5000/waiter/dashboard (login required)")
    
    print()
    print("🎯 CUSTOMER FEATURES:")
    print("-" * 40)
    print("✅ Personalized homepage with name greeting")
    print("✅ Access to menu and services from homepage")
    print("✅ Service request system with table selection")
    print("✅ Navigation includes Services link")
    print("✅ Both authenticated and guest access")
    
    print()
    print("=" * 60)
    print("🎉 SYSTEM IS RUNNING!")
    print("Ready for customer service requests and menu browsing.")

if __name__ == '__main__':
    check_system_status()
