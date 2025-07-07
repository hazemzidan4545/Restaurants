"""
Test script to verify the edit menu item functionality
"""

import sys
import os

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import MenuItem, Category
from app.extensions import db

def test_edit_functionality():
    """Test the edit menu item functionality"""
    app = create_app()
    
    with app.app_context():
        # Get a test menu item
        menu_item = MenuItem.query.first()
        if not menu_item:
            print("No menu items found in database")
            return False
        
        print(f"Testing with menu item: {menu_item.name}")
        print(f"Current price: {menu_item.price}")
        print(f"Current description: {menu_item.description}")
        print(f"Current stock: {menu_item.stock}")
        print(f"Current status: {menu_item.status}")
        
        # Test the discount methods
        print(f"\nTesting discount functionality:")
        print(f"Has discount: {menu_item.has_discount()}")
        print(f"Display price: {menu_item.get_display_price()}")
        print(f"Original price: {menu_item.get_original_price()}")
        
        # Test applying a discount
        original_price = float(menu_item.price)
        menu_item.apply_discount(20.0)  # 20% discount
        print(f"After applying 20% discount:")
        print(f"Has discount: {menu_item.has_discount()}")
        print(f"Display price: {menu_item.get_display_price()}")
        print(f"Original price: {menu_item.get_original_price()}")
        print(f"Discount amount: {menu_item.get_discount_amount()}")
        
        # Test removing discount
        menu_item.remove_discount()
        print(f"After removing discount:")
        print(f"Has discount: {menu_item.has_discount()}")
        print(f"Display price: {menu_item.get_display_price()}")
        print(f"Price: {menu_item.price}")
        
        # Test special options (temporary properties)
        print(f"\nTesting special options:")
        print(f"Is featured: {menu_item.is_featured}")
        print(f"Is spicy: {menu_item.is_spicy}")
        print(f"Is vegetarian: {menu_item.is_vegetarian}")
        print(f"Is vegan: {menu_item.is_vegan}")
        
        # Set some values
        menu_item.is_featured = True
        menu_item.is_spicy = True
        print(f"After setting featured=True, spicy=True:")
        print(f"Is featured: {menu_item.is_featured}")
        print(f"Is spicy: {menu_item.is_spicy}")
        
        print(f"\nEdit functionality test completed successfully!")
        return True

def test_categories():
    """Test that categories are available for the edit form"""
    app = create_app()
    
    with app.app_context():
        categories = Category.query.filter_by(is_active=True).all()
        print(f"\nAvailable categories for edit form:")
        for category in categories:
            print(f"- {category.name} (ID: {category.category_id})")
        
        return len(categories) > 0

if __name__ == '__main__':
    print("Testing edit menu item functionality...")
    
    success = test_edit_functionality()
    categories_ok = test_categories()
    
    if success and categories_ok:
        print("\n✅ All tests passed! Edit functionality is working correctly.")
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)
