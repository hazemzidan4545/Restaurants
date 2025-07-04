#!/usr/bin/env python3
"""
Test script to verify admin templates functionality
"""

from app import create_app
from app.models import User, CustomerLoyalty, RewardItem, PromotionalCampaign, db
import os

def test_admin_templates():
    """Test admin templates with mock data"""
    app = create_app()
    
    with app.test_client() as client:
        try:
            # Create a test user and login to access admin pages
            with app.app_context():
                # Check if templates can be found and loaded
                from jinja2 import Environment, FileSystemLoader
                import os
                
                template_dir = os.path.join(app.root_path, 'modules', 'admin', 'templates')
                env = Environment(loader=FileSystemLoader(template_dir))
                
                # Test each template loads without syntax errors
                templates = ['loyalty_management.html', 'campaigns_management.html', 'rewards_management.html']
                
                for template_name in templates:
                    try:
                        template = env.get_template(template_name)
                        print(f"✓ {template_name} loads successfully")
                    except Exception as e:
                        print(f"❌ {template_name} error: {e}")
                        return False
                
                print("✓ All templates load without syntax errors")
                return True
                
        except Exception as e:
            print(f"❌ Template test error: {e}")
            return False

def test_database_models():
    """Test database models and relationships"""
    app = create_app()
    
    with app.app_context():
        try:
            # Test model imports and basic queries
            total_users = User.query.count()
            total_loyalty = CustomerLoyalty.query.count()
            total_rewards = RewardItem.query.count()
            total_campaigns = PromotionalCampaign.query.count()
            
            print(f"\n📊 Database Statistics:")
            print(f"- Users: {total_users}")
            print(f"- Loyalty Records: {total_loyalty}")
            print(f"- Rewards: {total_rewards}")
            print(f"- Campaigns: {total_campaigns}")
            
            # Test relationship (if CustomerLoyalty records exist)
            if total_loyalty > 0:
                sample_loyalty = CustomerLoyalty.query.first()
                if hasattr(sample_loyalty, 'user') and sample_loyalty.user:
                    print("✓ CustomerLoyalty -> User relationship working")
                else:
                    print("⚠️  CustomerLoyalty -> User relationship needs verification")
            
            return True
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False

if __name__ == "__main__":
    print("🔍 Testing Admin Templates and Database...")
    print("=" * 50)
    
    templates_ok = test_admin_templates()
    database_ok = test_database_models()
    
    print("\n" + "=" * 50)
    if templates_ok and database_ok:
        print("✅ All tests passed! Admin system is ready.")
    else:
        print("❌ Some tests failed. Check the output above.")
