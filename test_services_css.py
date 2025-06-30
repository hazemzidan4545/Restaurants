#!/usr/bin/env python3
"""
Test to verify that the Services Management page CSS is properly contained
"""

import os
from pathlib import Path

def check_services_css():
    """Check if CSS is properly wrapped in style tags"""
    
    services_file = Path(__file__).parent / 'app' / 'modules' / 'admin' / 'templates' / 'services_management.html'
    
    if not services_file.exists():
        print("❌ Services management template not found")
        return False
    
    content = services_file.read_text(encoding='utf-8')
    
    print("🔍 Checking Services Management CSS Structure")
    print("=" * 50)
    
    # Check for proper style tag opening
    has_style_open = '<style>' in content
    print(f"✅ Opening <style> tag: {'Found' if has_style_open else 'Missing'}")
    
    # Check for proper style tag closing
    has_style_close = '</style>' in content
    print(f"✅ Closing </style> tag: {'Found' if has_style_close else 'Missing'}")
    
    # Check that CSS is not displayed as text (should be inside style tags)
    css_comment_line = '/* Enhanced Flash Messages - Centered and Prominent */'
    css_lines = content.split('\n')
    css_comment_index = -1
    
    for i, line in enumerate(css_lines):
        if css_comment_line in line:
            css_comment_index = i
            break
    
    if css_comment_index >= 0:
        # Check that the CSS comment is preceded by <style> tag
        preceding_lines = css_lines[max(0, css_comment_index-5):css_comment_index]
        has_style_before = any('<style>' in line for line in preceding_lines)
        
        print(f"✅ CSS properly wrapped: {'Yes' if has_style_before else 'No'}")
        
        if not has_style_before:
            print("❌ Found CSS outside of style tags - this will display as text!")
            return False
    
    # Count style blocks
    style_open_count = content.count('<style>')
    style_close_count = content.count('</style>')
    
    print(f"📊 Style blocks: {style_open_count} opening, {style_close_count} closing")
    
    if style_open_count != style_close_count:
        print("❌ Unmatched style tags!")
        return False
    
    print("✅ Services Management CSS structure is correct!")
    return True

if __name__ == "__main__":
    check_services_css()
