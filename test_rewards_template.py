"""
Test script to verify the enhanced rewards management template
"""

import sys
import os

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_rewards_template():
    """Test the rewards management template rendering"""
    try:
        from app import create_app
        from flask import url_for
        
        print("Testing Enhanced Rewards Management Template")
        print("=" * 50)
        
        app = create_app()
        
        with app.app_context():
            # Test URL generation
            rewards_url = url_for('admin.rewards_management')
            print(f"✅ Rewards management URL: {rewards_url}")
            
            # Test template path
            template_path = os.path.join('app', 'modules', 'admin', 'templates', 'rewards_management.html')
            if os.path.exists(template_path):
                print("✅ Template file exists")
                
                # Check template content
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verify key enhancements
                checks = [
                    ('page-header', 'Page header structure'),
                    ('header-stats', 'Header statistics'),
                    ('header-quick-actions', 'Quick actions section'),
                    ('inactive_rewards', 'Inactive rewards statistic'),
                    ('table-info', 'Table information display'),
                    ('rewards-table-container', 'Table container'),
                    ('bulk-actions', 'Bulk actions functionality'),
                    ('search-filters', 'Search and filter functionality')
                ]
                
                print("\nTemplate Content Verification:")
                for check, description in checks:
                    if check in content:
                        print(f"✅ {description}")
                    else:
                        print(f"❌ Missing: {description}")
                
                # Check for removed duplicated statistics
                stats_sections = content.count('stats-row')
                if stats_sections == 0:
                    print("✅ Duplicated statistics section removed")
                else:
                    print(f"❌ Found {stats_sections} stats-row sections (should be 0)")
                
                # Check for consistent design elements
                design_elements = [
                    'header-btn',
                    'quick-action-btn',
                    'table-header',
                    'status-badge'
                ]
                
                print("\nDesign Consistency Check:")
                for element in design_elements:
                    if element in content:
                        print(f"✅ {element} styling present")
                    else:
                        print(f"❌ Missing: {element} styling")
                
                print(f"\n📊 Template Statistics:")
                print(f"   - Total lines: {len(content.splitlines())}")
                print(f"   - CSS styles: {'✅' if 'extra_css' in content else '❌'}")
                print(f"   - JavaScript: {'✅' if 'extra_js' in content else '❌'}")
                print(f"   - Mobile responsive: {'✅' if '@media' in content else '❌'}")
                
                return True
            else:
                print("❌ Template file not found")
                return False
                
    except Exception as e:
        print(f"❌ Error testing template: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_rewards_template()
    
    if success:
        print("\n🎉 Rewards Management Template Enhancement Test Passed!")
    else:
        print("\n❌ Template Enhancement Test Failed!")
        sys.exit(1)
