#!/usr/bin/env python3
"""
Test the specific SQLAlchemy error that was reported
"""

import sys
import os

print("🧪 TESTING DATABASE MIGRATION FIX")
print("=" * 50)

# Test the exact query that was failing
print("\n1. Testing MenuItem query with discount columns...")

try:
    sys.path.append('.')
    from app import create_app
    from app.models import MenuItem, Category
    
    # Create app context
    app = create_app('development')
    
    with app.app_context():
        # This is the exact query that was failing before
        menu_items = MenuItem.query.join(Category, Category.category_id == MenuItem.category_id).order_by(
            Category.display_order, MenuItem.name
        ).all()
        
        print(f"✅ SUCCESS: Query returned {len(menu_items)} menu items")
        
        # Test discount fields specifically
        if menu_items:
            item = menu_items[0]
            print(f"✅ discount_percentage accessible: {item.discount_percentage}")
            print(f"✅ original_price accessible: {item.original_price}")
            
            # Test discount methods
            if hasattr(item, 'get_discounted_price'):
                price = item.get_discounted_price()
                print(f"✅ get_discounted_price() works: {price}")
            
        print("✅ All database operations successful!")
        
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("🎉 DATABASE MIGRATION VERIFICATION COMPLETE")
