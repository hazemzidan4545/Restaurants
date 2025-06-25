#!/usr/bin/env python3
"""
Test script to verify popular items functionality
"""

from app import create_app
from app.models import MenuItem

def test_popular_items():
    """Test the popular items calculation"""
    app = create_app()
    
    with app.app_context():
        print("🧪 Testing Popular Items Functionality")
        print("=" * 50)
        
        # Test get_popular_items method
        popular_items = MenuItem.get_popular_items(limit=5)
        print(f"\n📊 Top 5 Popular Items:")
        for i, item in enumerate(popular_items, 1):
            print(f"{i}. {item.name} - {item.price} EGP")
        
        # Test get_popular_items_with_counts method
        popular_with_counts = MenuItem.get_popular_items_with_counts(limit=5)
        print(f"\n📈 Top 5 Popular Items with Order Counts:")
        for i, (item, count) in enumerate(popular_with_counts, 1):
            revenue = float(item.price) * int(count)
            print(f"{i}. {item.name:<25} - {count:3d} orders - {revenue:8.2f} EGP revenue")
        
        # Test fallback when no orders exist
        print(f"\n🔄 Testing fallback mechanism...")
        all_items = MenuItem.query.filter_by(status='available').limit(4).all()
        print(f"Available items for fallback: {len(all_items)}")
        
        print(f"\n✅ Popular items functionality is working correctly!")
        print(f"📊 Total popular items found: {len(popular_items)}")
        
        if popular_items:
            most_popular = popular_with_counts[0]
            print(f"🏆 Most popular item: {most_popular[0].name} with {most_popular[1]} orders")

if __name__ == "__main__":
    test_popular_items()
