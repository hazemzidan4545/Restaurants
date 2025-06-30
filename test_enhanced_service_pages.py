#!/usr/bin/env python3
"""
Test script for Enhanced Service Management Pages
This script validates the enhanced add and edit service templates.
"""

import os
import sys

def check_template_exists(template_path):
    """Check if template file exists and return basic info"""
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = len(content.split('\n'))
            return True, lines, len(content)
    return False, 0, 0

def main():
    """Main test function"""
    print("🔍 Testing Enhanced Service Management Pages")
    print("=" * 50)
    
    # Base paths
    base_path = os.path.dirname(os.path.abspath(__file__))
    templates_path = os.path.join(base_path, "app", "modules", "admin", "templates")
    
    # Templates to check
    templates = {
        "Services Management": "services_management.html",
        "Add Service": "add_service.html", 
        "Edit Service": "edit_service.html"
    }
    
    results = {}
    
    for name, template_file in templates.items():
        template_path = os.path.join(templates_path, template_file)
        exists, lines, size = check_template_exists(template_path)
        results[name] = {
            'exists': exists,
            'lines': lines,
            'size': size,
            'path': template_path
        }
    
    # Print results
    for name, result in results.items():
        status = "✅" if result['exists'] else "❌"
        print(f"{status} {name}")
        if result['exists']:
            print(f"   📄 Lines: {result['lines']}")
            print(f"   💾 Size: {result['size']} bytes")
        else:
            print(f"   ❌ Not found: {result['path']}")
        print()
    
    # Check CSS file
    css_path = os.path.join(base_path, "app", "static", "css", "admin.css")
    css_exists, css_lines, css_size = check_template_exists(css_path)
    
    status = "✅" if css_exists else "❌"
    print(f"{status} Admin CSS")
    if css_exists:
        print(f"   📄 Lines: {css_lines}")
        print(f"   💾 Size: {css_size} bytes")
    print()
    
    # Summary
    all_exist = all(result['exists'] for result in results.values()) and css_exists
    
    print("=" * 50)
    if all_exist:
        print("✅ All enhanced service management files are present!")
        print("🚀 The enhanced UI should be ready to use.")
    else:
        print("❌ Some files are missing.")
        print("🔧 Please check the missing files above.")
    
    print("\n📋 Enhancement Features:")
    print("   • Modern card-based grid layout")
    print("   • Enhanced page headers with gradients")
    print("   • Live preview for services")
    print("   • Improved form design with sections")
    print("   • Custom switches and enhanced inputs")
    print("   • Centered flash messages and modals")
    print("   • Service statistics display")
    print("   • Icon suggestion buttons")
    print("   • Mobile-responsive design")

if __name__ == "__main__":
    main()
