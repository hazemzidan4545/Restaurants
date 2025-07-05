#!/usr/bin/env python3
"""
Simple test for API server and SystemSettings
"""

import requests
import sys
sys.path.append('.')

print("Testing API Server and SystemSettings...")
print("=" * 50)

# Test 1: API Server Health
try:
    response = requests.get('http://localhost:5000/api/health', timeout=10)
    if response.status_code == 200:
        print("✅ PASS API server is running")
    else:
        print(f"❌ FAIL API server returned status {response.status_code}")
except Exception as e:
    print(f"❌ FAIL API server connection failed: {e}")

# Test 2: SystemSettings Model
try:
    from app.models import SystemSettings
    print("✅ PASS SystemSettings model exists")
    
    # Test methods
    if hasattr(SystemSettings, 'get_setting'):
        print("✅ PASS SystemSettings.get_setting method exists")
    else:
        print("❌ FAIL SystemSettings.get_setting method missing")
        
    if hasattr(SystemSettings, 'set_setting'):
        print("✅ PASS SystemSettings.set_setting method exists")
    else:
        print("❌ FAIL SystemSettings.set_setting method missing")
        
    if hasattr(SystemSettings, 'get_currency'):
        print("✅ PASS SystemSettings.get_currency method exists")
    else:
        print("❌ FAIL SystemSettings.get_currency method missing")
        
except ImportError as e:
    print(f"❌ FAIL SystemSettings model import failed: {e}")
except Exception as e:
    print(f"❌ FAIL SystemSettings model error: {e}")

print("\nTest completed!")
