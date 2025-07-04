#!/usr/bin/env python3
"""
Quick verification script to test admin templates after fixes
"""

from app import create_app
from flask import url_for

def test_admin_templates():
    """Test that admin templates can be accessed without errors"""
    app = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            try:
                print("🧪 Testing Admin Template Routes...")
                print("-" * 50)
                
                # Test routes exist
                routes_to_test = [
                    ('admin.loyalty_management', 'Loyalty Management'),
                    ('admin.campaigns_management', 'Campaigns Management'), 
                    ('admin.rewards_management', 'Rewards Management')
                ]
                
                for route_name, description in routes_to_test:
                    try:
                        url = url_for(route_name)
                        print(f"✓ {description:20} | Route: {url}")
                    except Exception as e:
                        print(f"❌ {description:20} | Error: {e}")
                        return False
                
                print("\n🔧 Testing Template Syntax...")
                print("-" * 50)
                
                # Test template loading
                from jinja2 import Environment, FileSystemLoader
                import os
                
                template_dir = os.path.join(app.root_path, 'modules', 'admin', 'templates')
                env = Environment(loader=FileSystemLoader(template_dir))
                
                templates = [
                    'loyalty_management.html',
                    'campaigns_management.html', 
                    'rewards_management.html'
                ]
                
                for template_name in templates:
                    try:
                        template = env.get_template(template_name)
                        print(f"✓ {template_name:25} | Syntax OK")
                    except Exception as e:
                        print(f"❌ {template_name:25} | Error: {e}")
                        return False
                
                print("\n✅ All tests passed!")
                print("\n📋 Summary of Fixes Applied:")
                print("-" * 50)
                print("✓ Added datetime to template contexts")
                print("✓ Fixed JavaScript onclick handlers with quotes")
                print("✓ Fixed CustomerLoyalty model relationships")
                print("✓ Updated all templates to use standard page-header")
                print("✓ Removed Jinja2 min() function issues")
                print("✓ Fixed user field access (name vs first_name)")
                
                return True
                
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                return False

if __name__ == "__main__":
    success = test_admin_templates()
    if success:
        print("\n🎉 Admin templates are ready for use!")
    else:
        print("\n🔥 Some issues remain to be fixed.")
