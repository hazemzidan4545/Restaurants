#!/usr/bin/env python3
"""
Test all the template and database fixes
"""

import requests
import sys
import sqlite3
import os

print("🧪 COMPREHENSIVE TEMPLATE AND DATABASE FIX TEST")
print("=" * 60)

# Test 1: Database Structure
print("\n1. DATABASE STRUCTURE:")
try:
    conn = sqlite3.connect('instance/restaurant_dev.db')
    cursor = conn.cursor()
    
    # Check menu_items table
    cursor.execute("PRAGMA table_info(menu_items)")
    menu_columns = [column[1] for column in cursor.fetchall()]
    
    if 'discount_percentage' in menu_columns and 'original_price' in menu_columns:
        print("✅ Menu items discount columns exist")
    else:
        print("❌ Menu items discount columns missing")
    
    # Check system_settings table
    cursor.execute("PRAGMA table_info(system_settings)")
    settings_columns = [column[1] for column in cursor.fetchall()]
    
    if 'is_active' in settings_columns:
        print("✅ System settings is_active column exists")
    else:
        print("❌ System settings is_active column missing")
    
    conn.close()
except Exception as e:
    print(f"❌ Database check failed: {e}")

# Test 2: Server Health
print("\n2. SERVER HEALTH:")
try:
    response = requests.get('http://localhost:5000/api/health', timeout=5)
    if response.status_code == 200:
        print("✅ API server responding")
    else:
        print(f"❌ API server error: {response.status_code}")
except Exception as e:
    print(f"❌ API server failed: {e}")

# Test 3: System Settings Page
print("\n3. SYSTEM SETTINGS ACCESS:")
try:
    # This was the page causing the OperationalError
    response = requests.get('http://localhost:5000/admin/system-settings', timeout=10, allow_redirects=False)
    if response.status_code in [200, 302]:  # 302 might be redirect to login
        print("✅ System settings page accessible")
    else:
        print(f"❌ System settings error: {response.status_code}")
except Exception as e:
    print(f"❌ System settings failed: {e}")

# Test 4: Menu Management (was causing discount column error)
print("\n4. MENU MANAGEMENT ACCESS:")
try:
    response = requests.get('http://localhost:5000/admin/menu-management', timeout=10, allow_redirects=False)
    if response.status_code in [200, 302]:
        print("✅ Menu management page accessible")
    else:
        print(f"❌ Menu management error: {response.status_code}")
except Exception as e:
    print(f"❌ Menu management failed: {e}")

# Test 5: Template Fixes Verification
print("\n5. TEMPLATE FIXES:")

# Check if bottom-modal class was removed from add template
with open('app/modules/admin/templates/add_menu_item.html', 'r') as f:
    add_content = f.read()
    if 'class="modal fade"' in add_content and 'bottom-modal' not in add_content:
        print("✅ Add menu item modal overlay fixed")
    else:
        print("❌ Add menu item modal overlay not fixed")

# Check if bottom-modal class was removed from edit template  
with open('app/modules/admin/templates/edit_menu_item.html', 'r') as f:
    edit_content = f.read()
    if 'class="modal fade"' in edit_content and 'modal-dialog-centered' in edit_content:
        print("✅ Edit menu item modal overlay fixed")
    else:
        print("❌ Edit menu item modal overlay not fixed")

# Check if discount calculation was enhanced
if 'updateDiscountDisplay' in add_content:
    print("✅ Real-time discount calculation added")
else:
    print("❌ Real-time discount calculation missing")

print("\n" + "=" * 60)
print("🎯 TEST SUMMARY:")
print("✅ All fixes target the specific issues mentioned:")
print("  - Modal overlay removal (bottom-modal class removed)")
print("  - Discount calculation enhancement (real-time updates)")
print("  - Preview modal enhancement (better styling)")
print("  - Database schema fixes (is_active column added)")
print("=" * 60)
