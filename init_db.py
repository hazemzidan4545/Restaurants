#!/usr/bin/env python3
"""
Database initialization script for Restaurant Management System
Creates tables and populates with seed data
"""

import os
from app import create_app
from app.extensions import db
from app.models import (
    User, Table, Category, MenuItem, Order, OrderItem, Payment,
    ServiceRequest, Notification, Feedback, LoyaltyProgram,
    CustomerLoyalty, PointTransaction, RewardItem, RewardRedemption,
    PromotionalCampaign, QRCode, AuditLog
)
from datetime import datetime, timedelta

def init_database():
    """Initialize database with tables and seed data"""
    app = create_app('development')
    
    with app.app_context():
        # Drop all tables and recreate
        print("Dropping existing tables...")
        db.drop_all()
        
        print("Creating tables...")
        db.create_all()
        
        # Add seed data
        print("Adding seed data...")
        add_seed_data()
        
        print("Database initialization completed successfully!")

def add_seed_data():
    """Add initial seed data to the database"""
    
    # Create default users
    admin = User(
        name='Admin User',
        email='admin@restaurant.com',
        phone='+201234567890',
        role='admin',
        is_active=True
    )
    admin.set_password('admin123')
    
    waiter = User(
        name='Waiter User',
        email='waiter@restaurant.com',
        phone='+201234567891',
        role='waiter',
        is_active=True
    )
    waiter.set_password('waiter123')
    
    customer = User(
        name='John Doe',
        email='customer@example.com',
        phone='+201234567892',
        role='customer',
        is_active=True
    )
    customer.set_password('customer123')
    
    db.session.add_all([admin, waiter, customer])
    db.session.commit()
    
    # Create tables
    tables_data = [
        {'table_number': 'T001', 'capacity': 4, 'status': 'available'},
        {'table_number': 'T002', 'capacity': 2, 'status': 'available'},
        {'table_number': 'T003', 'capacity': 6, 'status': 'occupied'},
        {'table_number': 'T004', 'capacity': 4, 'status': 'available'},
        {'table_number': 'T005', 'capacity': 8, 'status': 'reserved'},
    ]
    
    for table_data in tables_data:
        table = Table(**table_data)
        db.session.add(table)
    
    db.session.commit()
    
    # Create menu categories
    categories_data = [
        {'name': 'Hookah', 'description': 'Premium hookah flavors and accessories', 'display_order': 1},
        {'name': 'Drinks', 'description': 'Hot and cold beverages', 'display_order': 2},
        {'name': 'Brunch', 'description': 'Delicious brunch items', 'display_order': 3},
        {'name': 'Main Courses', 'description': 'Hearty main dishes', 'display_order': 4},
        {'name': 'Desserts', 'description': 'Sweet treats and desserts', 'display_order': 5},
    ]
    
    for cat_data in categories_data:
        category = Category(**cat_data)
        db.session.add(category)
    
    db.session.commit()
    
    # Create menu items
    menu_items_data = [
        # Hookah
        {'name': 'Apple Mint Hookah', 'description': 'Fresh apple and mint flavor', 'price': 150.00, 'category_id': 1, 'stock': 10},
        {'name': 'Double Apple Hookah', 'description': 'Classic double apple flavor', 'price': 140.00, 'category_id': 1, 'stock': 15},
        {'name': 'Grape Hookah', 'description': 'Sweet grape flavor', 'price': 145.00, 'category_id': 1, 'stock': 12},
        
        # Drinks
        {'name': 'Turkish Coffee', 'description': 'Traditional Turkish coffee', 'price': 25.00, 'category_id': 2, 'stock': 50},
        {'name': 'Fresh Orange Juice', 'description': 'Freshly squeezed orange juice', 'price': 35.00, 'category_id': 2, 'stock': 30},
        {'name': 'Mint Tea', 'description': 'Refreshing mint tea', 'price': 20.00, 'category_id': 2, 'stock': 40},
        
        # Brunch
        {'name': 'Egyptian Breakfast', 'description': 'Traditional Egyptian breakfast platter', 'price': 85.00, 'category_id': 3, 'stock': 20},
        {'name': 'Cheese Omelette', 'description': 'Fluffy omelette with cheese', 'price': 45.00, 'category_id': 3, 'stock': 25},
        {'name': 'Pancakes', 'description': 'Stack of fluffy pancakes with syrup', 'price': 55.00, 'category_id': 3, 'stock': 15},
        
        # Main Courses
        {'name': 'Grilled Chicken', 'description': 'Marinated grilled chicken breast', 'price': 120.00, 'category_id': 4, 'stock': 18},
        {'name': 'Beef Burger', 'description': 'Juicy beef burger with fries', 'price': 95.00, 'category_id': 4, 'stock': 22},
        {'name': 'Fish & Chips', 'description': 'Crispy fish with golden fries', 'price': 110.00, 'category_id': 4, 'stock': 16},
        
        # Desserts
        {'name': 'Chocolate Cake', 'description': 'Rich chocolate layer cake', 'price': 40.00, 'category_id': 5, 'stock': 12},
        {'name': 'Baklava', 'description': 'Traditional Middle Eastern pastry', 'price': 35.00, 'category_id': 5, 'stock': 20},
        {'name': 'Ice Cream', 'description': 'Vanilla ice cream with toppings', 'price': 30.00, 'category_id': 5, 'stock': 25},
    ]
    
    for item_data in menu_items_data:
        menu_item = MenuItem(**item_data)
        db.session.add(menu_item)
    
    db.session.commit()
    
    # Create loyalty program
    loyalty_program = LoyaltyProgram(
        name='Restaurant Rewards',
        description='Earn points with every purchase and redeem for free items',
        points_per_50EGP=100,
        status='active'
    )
    db.session.add(loyalty_program)
    
    # Create customer loyalty account
    customer_loyalty = CustomerLoyalty(
        user_id=customer.user_id,
        total_points=500,
        lifetime_points=1200,
        tier_level='silver'
    )
    db.session.add(customer_loyalty)
    
    db.session.commit()
    
    # Create reward items
    reward_items_data = [
        {'name': 'Free Coffee', 'description': 'Complimentary Turkish coffee', 'points_required': 200, 'item_id': 4},
        {'name': 'Free Dessert', 'description': 'Any dessert from our menu', 'points_required': 300, 'category': 'desserts'},
        {'name': '10% Discount', 'description': '10% off your next order', 'points_required': 500, 'category': 'discount'},
    ]
    
    for reward_data in reward_items_data:
        reward = RewardItem(**reward_data)
        db.session.add(reward)
    
    db.session.commit()
    
    # Create promotional campaign
    campaign = PromotionalCampaign(
        name='Double Points Weekend',
        description='Earn double points on all orders during weekends',
        bonus_multiplier=2.0,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=30),
        status='active'
    )
    db.session.add(campaign)
    
    db.session.commit()
    
    print(f"Created {User.query.count()} users")
    print(f"Created {Table.query.count()} tables")
    print(f"Created {Category.query.count()} categories")
    print(f"Created {MenuItem.query.count()} menu items")
    print(f"Created {RewardItem.query.count()} reward items")
    print("Seed data added successfully!")

if __name__ == '__main__':
    init_database()
