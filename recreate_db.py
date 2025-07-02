#!/usr/bin/env python3
"""Simple database recreation to fix schema"""

from app import create_app
from app.models import db, User, MenuItem, Category
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    try:
        print("=== RECREATING DATABASE WITH CORRECT SCHEMA ===")
        
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()
        
        print("✅ Database recreated with correct schema")
        
        # Create essential test data
        print("Creating test data...")
        
        # Create customer
        customer = User(
            name='Test Customer',
            email='customer@test.com',
            password_hash=generate_password_hash('test123'),
            role='customer',
            phone='555-0123'
        )
        db.session.add(customer)
        
        # Create category and menu item
        category = Category(name='Main Dishes', is_active=True, display_order=1)
        db.session.add(category)
        db.session.flush()
        
        menu_item = MenuItem(
            name='Chicken Pizza',
            price=18.99,
            description='Delicious chicken pizza',
            category_id=category.category_id,
            status='available',
            stock=50
        )
        db.session.add(menu_item)
        
        menu_item2 = MenuItem(
            name='Beef Burger',
            price=15.99,
            description='Juicy beef burger',
            category_id=category.category_id,
            status='available',
            stock=30
        )
        db.session.add(menu_item2)
        
        db.session.commit()
        
        print("✅ Test data created")
        print("\nLogin credentials:")
        print("Email: customer@test.com")
        print("Password: test123")
        print("\nYou can now place orders successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
