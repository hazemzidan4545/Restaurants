#!/usr/bin/env python3
"""Fix admin template extends to use correct base template path"""

import os
import glob

def fix_admin_template_extends():
    """Fix all admin templates to extend base.html (the admin one)"""
    
    # Get all HTML files in admin templates directory
    admin_templates_dir = "app/modules/admin/templates"
    template_files = glob.glob(f"{admin_templates_dir}/*.html")
    
    updated_files = []
    
    for template_file in template_files:
        # Skip the base.html itself
        if template_file.endswith('/base.html') or template_file.endswith('\\base.html'):
            continue
            
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace extends "admin/base.html" with extends "base.html"
            if '{% extends "admin/base.html" %}' in content:
                new_content = content.replace('{% extends "admin/base.html" %}', '{% extends "base.html" %}')
                
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                updated_files.append(template_file)
                print(f"✅ Fixed: {template_file}")
            elif '{% extends "base.html" %}' in content:
                print(f"✓ Already correct: {template_file}")
            else:
                print(f"⚠️ No extends found: {template_file}")
                
        except Exception as e:
            print(f"❌ Error updating {template_file}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"Total files fixed: {len(updated_files)}")
    if updated_files:
        print(f"Fixed files:")
        for file in updated_files:
            print(f"  - {file}")

if __name__ == "__main__":
    fix_admin_template_extends()
