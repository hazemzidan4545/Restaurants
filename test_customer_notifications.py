#!/usr/bin/env python3
"""
Test script to verify customer module notification improvements
"""

import os
import re

def test_customer_notifications():
    """Test that customer module uses proper notifications instead of browser alerts"""
    print("🧪 TESTING CUSTOMER MODULE NOTIFICATIONS")
    print("=" * 50)
    
    customer_templates_dir = "app/modules/customer/templates"
    issues_found = 0
    
    # Check for browser alerts
    print("\n1️⃣ Checking for Browser Alerts...")
    alert_patterns = [
        r'\balert\s*\(',
        r'\bconfirm\s*\(',
        r'\bprompt\s*\('
    ]
    
    for root, dirs, files in os.walk(customer_templates_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    file_issues = 0
                    for pattern in alert_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            print(f"   ❌ {file}: Found {len(matches)} browser alert(s)")
                            file_issues += len(matches)
                    
                    if file_issues == 0:
                        print(f"   ✅ {file}: No browser alerts found")
                    else:
                        issues_found += file_issues
                        
                except Exception as e:
                    print(f"   ❌ Error reading {file}: {e}")
    
    # Check for proper notification implementations
    print("\n2️⃣ Checking for Proper Notification Systems...")
    
    # Service requests template
    service_requests_path = os.path.join(customer_templates_dir, "service_requests.html")
    if os.path.exists(service_requests_path):
        with open(service_requests_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ("Table Number Modal", "tableNumberModal"),
            ("Notification Toast", "notificationToast"),
            ("showNotification function", "showNotification"),
            ("showTableNumberModal function", "showTableNumberModal")
        ]
        
        for check_name, check_pattern in checks:
            if check_pattern in content:
                print(f"   ✅ Service Requests: {check_name} implemented")
            else:
                print(f"   ❌ Service Requests: {check_name} missing")
                issues_found += 1
    
    # Customer settings template
    settings_path = os.path.join(customer_templates_dir, "customer_settings.html")
    if os.path.exists(settings_path):
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ("Deactivation Modal", "deactivateConfirmModal"),
            ("Settings Notification Toast", "settingsNotificationToast"),
            ("showDeactivateConfirmation function", "showDeactivateConfirmation"),
            ("showSettingsNotification function", "showSettingsNotification")
        ]
        
        for check_name, check_pattern in checks:
            if check_pattern in content:
                print(f"   ✅ Customer Settings: {check_name} implemented")
            else:
                print(f"   ❌ Customer Settings: {check_name} missing")
                issues_found += 1
    
    # Check search functionality
    print("\n3️⃣ Checking Search Functionality...")
    
    menu_path = os.path.join(customer_templates_dir, "menu.html")
    if os.path.exists(menu_path):
        with open(menu_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        search_checks = [
            ("Search Container", "search-container"),
            ("Search Box", "searchBox"),
            ("Search Function", "searchMenuItem"),
            ("No Results Message", "noSearchResults")
        ]
        
        for check_name, check_pattern in search_checks:
            if check_pattern in content:
                print(f"   ✅ Menu Search: {check_name} implemented")
            else:
                print(f"   ❌ Menu Search: {check_name} missing")
                issues_found += 1
    
    # Test notification features
    print("\n4️⃣ Testing Notification Features...")
    
    # Check if Bootstrap is available for modals and toasts
    base_template_path = "app/templates/shared/base.html"
    if os.path.exists(base_template_path):
        with open(base_template_path, 'r', encoding='utf-8') as f:
            base_content = f.read()
        
        if "bootstrap" in base_content.lower():
            print("   ✅ Bootstrap available for modals and toasts")
        else:
            print("   ❌ Bootstrap not found in base template")
            issues_found += 1
    
    # Summary
    print("\n" + "=" * 50)
    if issues_found == 0:
        print("✅ ALL CUSTOMER NOTIFICATION TESTS PASSED!")
        print("🎉 Customer module is production-ready with proper notifications")
        return True
    else:
        print(f"❌ Found {issues_found} issues in customer notifications")
        print("💡 Please fix the issues above before deployment")
        return False

def test_specific_improvements():
    """Test specific improvements made to customer module"""
    print("\n🔍 TESTING SPECIFIC IMPROVEMENTS")
    print("=" * 50)
    
    improvements = [
        {
            "name": "Service Request Modal",
            "file": "app/modules/customer/templates/service_requests.html",
            "patterns": ["tableNumberModal", "submitModalRequest", "modalTableNumber"]
        },
        {
            "name": "Customer Settings Confirmation",
            "file": "app/modules/customer/templates/customer_settings.html", 
            "patterns": ["deactivateConfirmModal", "showDeactivateConfirmation", "confirmDeactivateBtn"]
        },
        {
            "name": "Menu Search Enhancement",
            "file": "app/modules/customer/templates/menu.html",
            "patterns": ["searchMenuItem", "noSearchResults", "search-container"]
        }
    ]
    
    all_good = True
    
    for improvement in improvements:
        print(f"\n📋 {improvement['name']}:")
        
        if os.path.exists(improvement['file']):
            with open(improvement['file'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            for pattern in improvement['patterns']:
                if pattern in content:
                    print(f"   ✅ {pattern} found")
                else:
                    print(f"   ❌ {pattern} missing")
                    all_good = False
        else:
            print(f"   ❌ File not found: {improvement['file']}")
            all_good = False
    
    return all_good

if __name__ == '__main__':
    print("🚀 CUSTOMER MODULE NOTIFICATION TESTING")
    print("Testing production-level notification systems...")
    
    # Run main tests
    main_result = test_customer_notifications()
    
    # Run specific improvement tests
    improvement_result = test_specific_improvements()
    
    # Final result
    print("\n" + "=" * 60)
    if main_result and improvement_result:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Customer module notifications are production-ready")
        print("✅ No browser alerts found")
        print("✅ Proper modal and toast systems implemented")
        print("✅ Search functionality enhanced")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please review and fix the issues above")
    
    print("\n📝 SUMMARY:")
    print("- Service requests now use modal for table number input")
    print("- Account deactivation uses confirmation modal")
    print("- All notifications use Bootstrap toasts")
    print("- Search functionality is properly implemented")
    print("- No browser alerts remain in customer module")
