#!/usr/bin/env python3
"""Force database recreation by using a new database file"""

import os
import sys
from app import create_app
from app.models import db, User, MenuItem, Category
from werkzeug.security import generate_password_hash

# Temporarily change the database file
os.environ['DATABASE_URL'] = 'sqlite:///restaurant_new.db'

app = create_app()

with app.app_context():
    try:
        print("=== CREATING NEW DATABASE WITH CORRECT SCHEMA ===")
        
        # Create all tables with the correct schema
        db.create_all()
        
        print("✅ New database created with correct schema")
        
        # Create test data
        print("Creating essential test data...")
        
        # Create customer
        customer = User(
            name='Test Customer',
            email='customer@test.com',
            password_hash=generate_password_hash('test123'),
            role='customer',
            phone='555-0123'
        )
        db.session.add(customer)
        
        # Create admin
        admin = User(
            name='Admin User',
            email='admin@test.com',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            phone='555-0124'
        )
        db.session.add(admin)
        
        # Create category
        category = Category(
            name='Main Dishes',
            description='Delicious main courses',
            is_active=True,
            display_order=1
        )
        db.session.add(category)
        db.session.flush()
        
        # Create menu items
        items_data = [
            {'name': 'Chicken Pizza', 'price': 18.99, 'description': 'Delicious chicken pizza'},
            {'name': 'Beef Burger', 'price': 15.99, 'description': 'Juicy beef burger with fries'},
            {'name': 'Caesar Salad', 'price': 12.99, 'description': 'Fresh caesar salad'},
            {'name': 'Pasta Carbonara', 'price': 16.99, 'description': 'Creamy pasta carbonara'}
        ]
        
        for item_data in items_data:
            menu_item = MenuItem(
                name=item_data['name'],
                price=item_data['price'],
                description=item_data['description'],
                category_id=category.category_id,
                status='available',
                stock=50
            )
            db.session.add(menu_item)
        
        db.session.commit()
        
        print("✅ Test data created successfully")
        print("\nNow you need to:")
        print("1. Stop the Flask app")
        print("2. Replace restaurant_dev.db with restaurant_new.db")
        print("3. Restart the Flask app")
        print("\nLogin credentials:")
        print("Customer: customer@test.com / test123")
        print("Admin: admin@test.com / admin123")
        
        # Show the database file location
        db_path = os.path.join(os.getcwd(), 'restaurant_new.db')
        print(f"\nNew database created at: {db_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
