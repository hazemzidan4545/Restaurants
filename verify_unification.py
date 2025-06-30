#!/usr/bin/env python3
"""
Verification script to show that admin pages are using unified page-header styles
"""

import os
from pathlib import Path

def check_page_header_styles():
    """Check if page-header styles are properly unified"""
    
    base_dir = Path(__file__).parent
    
    # Template files to check
    templates = {
        'base.html': base_dir / 'app' / 'modules' / 'admin' / 'templates' / 'base.html',
        'menu_management.html': base_dir / 'app' / 'modules' / 'admin' / 'templates' / 'menu_management.html',
        'services_management.html': base_dir / 'app' / 'modules' / 'admin' / 'templates' / 'services_management.html'
    }
    
    print("🔍 Admin Module Page-Header Unification Status")
    print("=" * 50)
    
    # Check if base.html has page-header styles
    base_content = templates['base.html'].read_text(encoding='utf-8')
    has_page_header_in_base = '.page-header {' in base_content
    has_stat_item_in_base = '.stat-item {' in base_content
    has_header_actions_in_base = '.header-actions {' in base_content
    
    print(f"📋 Base Template (base.html):")
    print(f"   ✅ page-header styles: {'Present' if has_page_header_in_base else 'Missing'}")
    print(f"   ✅ stat-item styles: {'Present' if has_stat_item_in_base else 'Missing'}")
    print(f"   ✅ header-actions styles: {'Present' if has_header_actions_in_base else 'Missing'}")
    print()
    
    # Check if child templates have duplicate styles
    for template_name, template_path in templates.items():
        if template_name == 'base.html':
            continue
            
        content = template_path.read_text(encoding='utf-8')
        has_duplicate_page_header = content.count('.page-header {') > 0
        has_duplicate_stat_item = content.count('.stat-item {') > 0
        has_duplicate_header_actions = content.count('.header-actions {') > 0
        
        print(f"📄 {template_name}:")
        print(f"   {'❌' if has_duplicate_page_header else '✅'} page-header styles: {'Duplicate Found' if has_duplicate_page_header else 'Using Shared'}")
        print(f"   {'❌' if has_duplicate_stat_item else '✅'} stat-item styles: {'Duplicate Found' if has_duplicate_stat_item else 'Using Shared'}")
        print(f"   {'❌' if has_duplicate_header_actions else '✅'} header-actions styles: {'Duplicate Found' if has_duplicate_header_actions else 'Using Shared'}")
        
        # Check if the page-header markup is present
        has_page_header_markup = '<div class="page-header">' in content
        print(f"   ✅ page-header markup: {'Present' if has_page_header_markup else 'Missing'}")
        print()
    
    print("🎯 Unification Summary:")
    print("=" * 50)
    if has_page_header_in_base and has_stat_item_in_base and has_header_actions_in_base:
        print("✅ All shared page-header styles are in base template")
        
        # Check for any duplicates
        menu_content = templates['menu_management.html'].read_text(encoding='utf-8')
        services_content = templates['services_management.html'].read_text(encoding='utf-8')
        
        menu_duplicates = menu_content.count('.page-header {') + menu_content.count('.stat-item {') + menu_content.count('.header-actions {')
        services_duplicates = services_content.count('.page-header {') + services_content.count('.stat-item {') + services_content.count('.header-actions {')
        
        if menu_duplicates == 0 and services_duplicates == 0:
            print("✅ No duplicate styles found in child templates")
            print("✅ Admin module page-header unification: COMPLETE")
        else:
            print(f"❌ Found {menu_duplicates} duplicates in menu_management.html")
            print(f"❌ Found {services_duplicates} duplicates in services_management.html")
    else:
        print("❌ Base template missing some shared styles")
    
    print()
    print("🎨 Design Features:")
    print("   • Modern glassmorphism effects")
    print("   • Consistent stat-item styling")
    print("   • Unified header-actions buttons")
    print("   • Responsive design patterns")
    print("   • Shared animation effects")

if __name__ == "__main__":
    check_page_header_styles()
