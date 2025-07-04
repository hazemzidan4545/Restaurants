#!/usr/bin/env python3
"""Update all admin templates to use correct base template"""

import os
import glob

def update_admin_templates():
    """Update all admin templates to extend admin/base.html"""
    
    # Get all HTML files in admin templates directory
    admin_templates_dir = "app/modules/admin/templates"
    template_files = glob.glob(f"{admin_templates_dir}/*.html")
    
    updated_files = []
    
    for template_file in template_files:
        # Skip the base.html itself
        if template_file.endswith('/base.html'):
            continue
            
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace extends "base.html" with extends "admin/base.html"
            if '{% extends "base.html" %}' in content:
                new_content = content.replace('{% extends "base.html" %}', '{% extends "admin/base.html" %}')
                
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                updated_files.append(template_file)
                print(f"✅ Updated: {template_file}")
            elif '{% extends "admin/base.html" %}' in content:
                print(f"✓ Already correct: {template_file}")
            else:
                print(f"⚠️ No extends found: {template_file}")
                
        except Exception as e:
            print(f"❌ Error updating {template_file}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"Total files updated: {len(updated_files)}")
    print(f"Updated files:")
    for file in updated_files:
        print(f"  - {file}")

if __name__ == "__main__":
    update_admin_templates()
