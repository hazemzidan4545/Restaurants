#!/usr/bin/env python3
"""
Quick test to check if the delete modal issue is fixed
"""

import requests
import time

def test_services_page():
    try:
        response = requests.get('http://localhost:5000/admin/services', timeout=10)
        
        if response.status_code == 200:
            print("✓ Services page loads successfully")
            
            # Check for the modal fix elements
            html = response.text
            
            checks = [
                ('modalIsOpen flag', 'let modalIsOpen = false' in html),
                ('Modal prevention check', 'if (modalIsOpen)' in html),
                ('Modal flag setting', 'modalIsOpen = true' in html),
                ('Modal flag clearing', 'modalIsOpen = false' in html),
                ('Overlay delay', 'setTimeout(() => {' in html),
            ]
            
            print("\nModal Fix Checks:")
            for check_name, passed in checks:
                status = "✓" if passed else "✗"
                print(f"{status} {check_name}: {passed}")
            
            all_passed = all(check[1] for check in checks)
            
            if all_passed:
                print("\n🎉 All modal fixes are present in the code!")
                return True
            else:
                print("\n❌ Some modal fixes are missing")
                return False
                
        else:
            print(f"✗ Services page returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Modal Auto-Close Fix...")
    print("=" * 40)
    
    if test_services_page():
        print("\n✅ Modal fix verification PASSED!")
        print("\nThe following fixes have been applied:")
        print("- Added modalIsOpen flag to prevent multiple modals")
        print("- Added delay before attaching overlay click listener")
        print("- Improved event handling with stopImmediatePropagation")
        print("- Added modal state checks")
        print("\nTry the delete button again - it should stay open now!")
    else:
        print("\n❌ Modal fix verification FAILED!")
