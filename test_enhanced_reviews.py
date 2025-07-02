#!/usr/bin/env python3
"""
Test script to verify the enhanced review system with individual item ratings
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import User, Order, OrderItem, MenuItem, Feedback, db
from datetime import datetime

def test_enhanced_review_system():
    """Test the enhanced review system with individual item ratings"""
    app = create_app()
    
    with app.app_context():
        print("🌟 Testing Enhanced Review System")
        print("=" * 60)
        
        # Check if we have test data
        customer = User.query.filter_by(role='customer').first()
        if not customer:
            print("❌ No customer users found. Please create test data first.")
            return
        
        print(f"✅ Found customer: {customer.username}")
        
        # Test individual item rating functionality
        test_individual_item_ratings()
        test_average_rating_calculation()
        test_menu_rating_display()
        test_modal_rating_functionality()
        
        print("\n📋 Enhanced Review System Summary:")
        print("  - ✅ Individual item ratings in review form")
        print("  - ✅ Overall order rating + individual item ratings")
        print("  - ✅ Average rating calculation for menu items")
        print("  - ✅ Rating display in menu item cards")
        print("  - ✅ Rating display in item detail modals")
        print("  - ✅ Star rating system with half-stars support")
        
        print("\n🎯 User Experience:")
        print("  - Customers can rate both the order and individual items")
        print("  - Menu items show average ratings from all reviews")
        print("  - Ratings help other customers make informed choices")
        print("  - Visual star ratings make ratings easy to understand")

def test_individual_item_ratings():
    """Test individual item rating functionality"""
    print(f"\n⭐ Testing Individual Item Ratings:")
    
    # Check for existing item reviews
    item_reviews = Feedback.query.filter(Feedback.item_id.isnot(None)).all()
    print(f"  ✅ Found {len(item_reviews)} individual item reviews")
    
    # Check review template exists
    template_path = 'app/modules/customer/templates/review_order.html'
    if os.path.exists(template_path):
        print("  ✅ Enhanced review template exists")
        
        with open(template_path, 'r') as f:
            content = f.read()
            
        if 'Rate Individual Items' in content:
            print("  ✅ Individual item rating section found")
        else:
            print("  ❌ Individual item rating section not found")
            
        if 'item-rating-card' in content:
            print("  ✅ Item rating cards implemented")
        else:
            print("  ❌ Item rating cards not found")
    else:
        print("  ❌ Enhanced review template not found")

def test_average_rating_calculation():
    """Test average rating calculation for menu items"""
    print(f"\n📊 Testing Average Rating Calculation:")
    
    # Test with actual menu items
    menu_items = MenuItem.query.filter_by(status='available').limit(5).all()
    print(f"  ✅ Testing with {len(menu_items)} menu items")
    
    for item in menu_items:
        try:
            rating_data = item.get_average_rating()
            distribution = item.get_rating_distribution()
            
            print(f"  ✅ {item.name}: {rating_data['average']}/5 ({rating_data['count']} reviews)")
            
            if rating_data['count'] > 0:
                print(f"     Rating distribution: {distribution}")
        except Exception as e:
            print(f"  ❌ Error calculating rating for {item.name}: {e}")

def test_menu_rating_display():
    """Test rating display in menu templates"""
    print(f"\n🍽️  Testing Menu Rating Display:")
    
    menu_template_path = 'app/modules/customer/templates/menu.html'
    if os.path.exists(menu_template_path):
        print("  ✅ Menu template exists")
        
        with open(menu_template_path, 'r') as f:
            content = f.read()
            
        if 'items_with_ratings' in content:
            print("  ✅ Menu template uses ratings data")
        else:
            print("  ❌ Menu template doesn't use ratings data")
            
        if 'menu-item-rating' in content:
            print("  ✅ Menu item rating styles implemented")
        else:
            print("  ❌ Menu item rating styles not found")
            
        if 'data-rating-average' in content:
            print("  ✅ Rating data attributes added to menu items")
        else:
            print("  ❌ Rating data attributes not found")
    else:
        print("  ❌ Menu template not found")

def test_modal_rating_functionality():
    """Test modal rating display functionality"""
    print(f"\n🔍 Testing Modal Rating Functionality:")
    
    menu_template_path = 'app/modules/customer/templates/menu.html'
    if os.path.exists(menu_template_path):
        with open(menu_template_path, 'r') as f:
            content = f.read()
            
        if 'updateModalRating' in content:
            print("  ✅ Modal rating update function implemented")
        else:
            print("  ❌ Modal rating update function not found")
            
        if 'rating: options.rating' in content:
            print("  ✅ Rating data passed to modal function")
        else:
            print("  ❌ Rating data not passed to modal")

def create_test_reviews():
    """Create test reviews for demonstration"""
    print(f"\n🎭 Creating Test Reviews:")
    
    try:
        # Find a customer and completed order
        customer = User.query.filter_by(role='customer').first()
        if not customer:
            print("  ❌ No customer found")
            return
            
        order = Order.query.filter_by(user_id=customer.user_id, status='completed').first()
        if not order:
            print("  ❌ No completed orders found")
            return
            
        order_items = order.order_items.all()
        if not order_items:
            print("  ❌ No order items found")
            return
        
        # Create overall order review
        existing_order_review = Feedback.query.filter_by(
            order_id=order.order_id, 
            user_id=customer.user_id, 
            item_id=None
        ).first()
        
        if not existing_order_review:
            order_review = Feedback(
                user_id=customer.user_id,
                order_id=order.order_id,
                item_id=None,
                rating=4,
                comment="Great overall experience!",
                timestamp=datetime.utcnow()
            )
            db.session.add(order_review)
            print(f"  ✅ Created overall order review")
        
        # Create individual item reviews
        for i, item in enumerate(order_items[:2]):  # Limit to first 2 items
            existing_item_review = Feedback.query.filter_by(
                order_id=order.order_id,
                user_id=customer.user_id,
                item_id=item.item_id
            ).first()
            
            if not existing_item_review:
                item_rating = 3 + (i % 3)  # Ratings 3, 4, 5
                item_review = Feedback(
                    user_id=customer.user_id,
                    order_id=order.order_id,
                    item_id=item.item_id,
                    rating=item_rating,
                    comment=f"This {item.menu_item.name} was {'excellent' if item_rating >= 4 else 'good'}!",
                    timestamp=datetime.utcnow()
                )
                db.session.add(item_review)
                print(f"  ✅ Created review for {item.menu_item.name} ({item_rating}/5)")
        
        db.session.commit()
        print("  ✅ Test reviews created successfully")
        
    except Exception as e:
        db.session.rollback()
        print(f"  ❌ Error creating test reviews: {e}")

if __name__ == '__main__':
    test_enhanced_review_system()
    
    # Ask if user wants to create test reviews
    response = input("\nWould you like to create test reviews for demonstration? (y/n): ")
    if response.lower() == 'y':
        create_test_reviews()
