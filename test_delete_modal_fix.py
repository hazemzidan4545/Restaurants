#!/usr/bin/env python3
"""
Test script to verify the delete modal is working properly
"""

import requests
import sys
import os
from urllib.parse import urljoin

def test_delete_modal():
    """Test that the services management page loads and has the modal"""
    
    base_url = "http://localhost:5000"
    
    try:
        # Test if the server is running
        response = requests.get(base_url, timeout=5)
        print(f"✓ Server is running (status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"✗ Server is not accessible: {e}")
        print("Make sure the Flask app is running with: python run.py")
        return False
    
    try:
        # Test the services management page
        services_url = urljoin(base_url, "/admin/services")
        response = requests.get(services_url, timeout=10)
        
        if response.status_code == 200:
            print("✓ Services management page accessible")
            
            # Check for modal elements in the HTML
            html_content = response.text
            
            modal_checks = [
                ('deleteModal', 'id="deleteModal"' in html_content),
                ('confirmDelete function', 'function confirmDelete(' in html_content),
                ('delete-btn class', 'delete-btn' in html_content),
                ('serviceName element', 'id="serviceName"' in html_content),
                ('deleteForm', 'id="deleteForm"' in html_content),
                ('closeModal function', 'function closeModal(' in html_content)
            ]
            
            all_checks_passed = True
            for check_name, passed in modal_checks:
                if passed:
                    print(f"✓ {check_name} found in HTML")
                else:
                    print(f"✗ {check_name} NOT found in HTML")
                    all_checks_passed = False
            
            if all_checks_passed:
                print("\n✓ All modal components are present in the HTML")
                return True
            else:
                print("\n✗ Some modal components are missing")
                return False
                
        elif response.status_code == 302 or response.status_code == 403:
            print(f"✗ Access denied to services page (status: {response.status_code})")
            print("This might be due to authentication requirements")
            return False
        else:
            print(f"✗ Services page returned status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error accessing services page: {e}")
        return False

if __name__ == "__main__":
    print("Testing Delete Modal Fix...")
    print("=" * 50)
    
    if test_delete_modal():
        print("\n🎉 Delete modal test PASSED!")
        sys.exit(0)
    else:
        print("\n❌ Delete modal test FAILED!")
        sys.exit(1)
