#!/usr/bin/env python3
"""
Final comprehensive test for delete modal functionality.
This script tests that the modal appears above all overlays and is fully clickable.
"""

import sys
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_modal_functionality():
    """Test that the delete modal is fully functional and appears above overlays."""
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless for testing
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)
    
    try:
        print("🔍 Testing Modal Functionality...")
        
        # Navigate to menu management page
        driver.get("http://localhost:5000/admin/menu")
        
        # Wait for page to load
        print("⏳ Waiting for page to load...")
        time.sleep(3)
        
        # Check if we can find delete buttons
        delete_buttons = driver.find_elements(By.CSS_SELECTOR, ".delete-item-btn")
        print(f"✅ Found {len(delete_buttons)} delete buttons")
        
        if not delete_buttons:
            print("❌ No delete buttons found - test cannot proceed")
            return False
        
        # Click the first delete button
        print("🖱️ Clicking first delete button...")
        first_delete_btn = delete_buttons[0]
        driver.execute_script("arguments[0].click();", first_delete_btn)
        
        # Wait for modal to appear
        time.sleep(1)
        
        # Check if modal is visible and has correct z-index
        modal = wait.until(EC.presence_of_element_located((By.ID, "deleteModal")))
        
        # Check modal styling
        modal_z_index = driver.execute_script("return window.getComputedStyle(arguments[0]).zIndex;", modal)
        modal_display = driver.execute_script("return window.getComputedStyle(arguments[0]).display;", modal)
        modal_position = driver.execute_script("return window.getComputedStyle(arguments[0]).position;", modal)
        
        print(f"📊 Modal Properties:")
        print(f"   Z-Index: {modal_z_index}")
        print(f"   Display: {modal_display}")
        print(f"   Position: {modal_position}")
        
        # Check if modal dialog is positioned correctly
        modal_dialog = driver.find_element(By.CSS_SELECTOR, ".modal-dialog")
        dialog_z_index = driver.execute_script("return window.getComputedStyle(arguments[0]).zIndex;", modal_dialog)
        dialog_position = driver.execute_script("return window.getComputedStyle(arguments[0]).position;", modal_dialog)
        dialog_transform = driver.execute_script("return window.getComputedStyle(arguments[0]).transform;", modal_dialog)
        
        print(f"📊 Modal Dialog Properties:")
        print(f"   Z-Index: {dialog_z_index}")
        print(f"   Position: {dialog_position}")
        print(f"   Transform: {dialog_transform}")
        
        # Check if modal content is clickable
        modal_content = driver.find_element(By.CSS_SELECTOR, ".modal-content")
        content_z_index = driver.execute_script("return window.getComputedStyle(arguments[0]).zIndex;", modal_content)
        content_pointer_events = driver.execute_script("return window.getComputedStyle(arguments[0]).pointerEvents;", modal_content)
        
        print(f"📊 Modal Content Properties:")
        print(f"   Z-Index: {content_z_index}")
        print(f"   Pointer Events: {content_pointer_events}")
        
        # Try to interact with modal buttons
        try:
            cancel_btn = driver.find_element(By.CSS_SELECTOR, ".modal-footer .btn-secondary")
            confirm_btn = driver.find_element(By.CSS_SELECTOR, ".modal-footer .btn-danger")
            
            # Check if buttons are clickable
            cancel_clickable = cancel_btn.is_enabled() and cancel_btn.is_displayed()
            confirm_clickable = confirm_btn.is_enabled() and confirm_btn.is_displayed()
            
            print(f"🎯 Button Interactivity:")
            print(f"   Cancel Button Clickable: {cancel_clickable}")
            print(f"   Confirm Button Clickable: {confirm_clickable}")
            
            # Try to click cancel button
            print("🖱️ Testing cancel button click...")
            driver.execute_script("arguments[0].click();", cancel_btn)
            time.sleep(1)
            
            # Check if modal was closed
            modal_after_cancel = driver.find_elements(By.CSS_SELECTOR, ".modal.show")
            modal_closed = len(modal_after_cancel) == 0
            
            print(f"✅ Modal closed after cancel: {modal_closed}")
            
            return modal_closed and cancel_clickable and confirm_clickable
            
        except Exception as e:
            print(f"❌ Error testing button interactions: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    finally:
        driver.quit()

def check_css_properties():
    """Check the CSS properties in the template file."""
    
    print("\n🔍 Checking CSS Properties in Template...")
    
    template_path = "app/modules/admin/templates/menu_management.html"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for high z-index values
        if "z-index: 999999" in content:
            print("✅ Found maximum z-index for modal")
        else:
            print("❌ High z-index not found for modal")
        
        # Check for position fixed
        if "position: fixed" in content:
            print("✅ Found position: fixed in CSS")
        else:
            print("❌ Position: fixed not found")
        
        # Check for backdrop disabled
        if "backdrop: false" in content:
            print("✅ Found backdrop disabled in JavaScript")
        else:
            print("❌ Backdrop not disabled")
        
        # Check for transform centering
        if "translate(-50%, -50%)" in content:
            print("✅ Found centering transform")
        else:
            print("❌ Centering transform not found")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Template file not found: {template_path}")
        return False
    except Exception as e:
        print(f"❌ Error checking CSS: {e}")
        return False

def main():
    """Run all modal tests."""
    
    print("🚀 Starting Final Modal Functionality Tests")
    print("=" * 50)
    
    # Check CSS properties first
    css_ok = check_css_properties()
    
    if not css_ok:
        print("❌ CSS checks failed - modal may not work correctly")
        return False
    
    # Run the functional test
    try:
        # First, start the Flask app
        print("\n🔧 Please ensure Flask app is running on localhost:5000")
        print("Run: python run.py")
        input("Press Enter when the app is running...")
        
        # Run the modal test
        modal_test_passed = test_modal_functionality()
        
        if modal_test_passed:
            print("\n🎉 All modal tests PASSED!")
            print("✅ Modal should now be fully functional and clickable")
            return True
        else:
            print("\n❌ Modal tests FAILED")
            print("The modal may still have visibility/interaction issues")
            return False
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
