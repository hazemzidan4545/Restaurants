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
    
    # Create menu items with detailed nutritional information
    menu_items_data = [
        # Hookah
        {
            'name': 'Apple Mint Hookah',
            'description': 'Fresh apple and mint flavor hookah with premium tobacco blend',
            'price': 150.00, 'category_id': 1, 'stock': 10, 'image_url': 'apple_mint_hookah.jpg',
            'ingredients': 'Premium tobacco, Apple flavoring, Fresh mint leaves, Molasses, Glycerin',
            'calories': 0, 'preparation_time': 10, 'allergens': 'None',
            'serving_size': '1 session (45-60 minutes)', 'dietary_info': 'Contains nicotine'
        },
        {
            'name': 'Double Apple Hookah',
            'description': 'Classic double apple flavor with authentic Middle Eastern taste',
            'price': 140.00, 'category_id': 1, 'stock': 15, 'image_url': 'double_apple_hookah.jpg',
            'ingredients': 'Premium tobacco, Red apple flavoring, Green apple flavoring, Molasses, Glycerin',
            'calories': 0, 'preparation_time': 10, 'allergens': 'None',
            'serving_size': '1 session (45-60 minutes)', 'dietary_info': 'Contains nicotine'
        },
        {
            'name': 'Grape Hookah',
            'description': 'Sweet grape flavor with smooth, aromatic smoke',
            'price': 145.00, 'category_id': 1, 'stock': 12, 'image_url': 'grape_hookah.jpg',
            'ingredients': 'Premium tobacco, Grape flavoring, Molasses, Glycerin, Natural grape essence',
            'calories': 0, 'preparation_time': 10, 'allergens': 'None',
            'serving_size': '1 session (45-60 minutes)', 'dietary_info': 'Contains nicotine'
        },

        # Drinks
        {
            'name': 'Turkish Coffee',
            'description': 'Traditional Turkish coffee brewed to perfection with authentic spices',
            'price': 25.00, 'category_id': 2, 'stock': 50, 'image_url': 'turkish_coffee.jpg',
            'ingredients': 'Finely ground Turkish coffee beans, Sugar (optional), Cardamom, Water',
            'calories': 5, 'preparation_time': 8, 'allergens': 'Caffeine',
            'serving_size': '1 cup (60ml)', 'dietary_info': 'Vegan, Gluten-free'
        },
        {
            'name': 'Fresh Orange Juice',
            'description': 'Freshly squeezed orange juice packed with vitamin C',
            'price': 35.00, 'category_id': 2, 'stock': 30, 'image_url': 'fresh_orange_juice.jpg',
            'ingredients': 'Fresh oranges, Natural orange pulp',
            'calories': 112, 'preparation_time': 5, 'allergens': 'None',
            'serving_size': '1 glass (250ml)', 'dietary_info': 'Vegan, Gluten-free, Natural'
        },
        {
            'name': 'Mint Tea',
            'description': 'Refreshing mint tea with fresh mint leaves and honey',
            'price': 20.00, 'category_id': 2, 'stock': 40, 'image_url': 'mint_tea.jpg',
            'ingredients': 'Fresh mint leaves, Green tea, Honey, Hot water',
            'calories': 25, 'preparation_time': 5, 'allergens': 'None',
            'serving_size': '1 cup (200ml)', 'dietary_info': 'Vegetarian, Gluten-free'
        },

        # Brunch
        {
            'name': 'Egyptian Breakfast',
            'description': 'Traditional Egyptian breakfast platter with ful medames, eggs, and fresh bread',
            'price': 85.00, 'category_id': 3, 'stock': 20, 'image_url': 'egyptian_breakfast.jpg',
            'ingredients': 'Ful medames (fava beans), Eggs, Tahini, Tomatoes, Cucumbers, Fresh bread, Olive oil, Lemon juice, Parsley',
            'calories': 520, 'preparation_time': 15, 'allergens': 'Gluten, Eggs',
            'serving_size': '1 platter', 'dietary_info': 'Vegetarian'
        },
        {
            'name': 'Cheese Omelette',
            'description': 'Fluffy omelette filled with melted cheese and fresh herbs',
            'price': 45.00, 'category_id': 3, 'stock': 25, 'image_url': 'cheese_omelette.jpg',
            'ingredients': 'Fresh eggs, Cheddar cheese, Mozzarella cheese, Butter, Fresh chives, Salt, Black pepper',
            'calories': 380, 'preparation_time': 8, 'allergens': 'Eggs, Dairy',
            'serving_size': '1 omelette (3 eggs)', 'dietary_info': 'Vegetarian, Gluten-free'
        },
        {
            'name': 'Pancakes',
            'description': 'Stack of fluffy pancakes served with maple syrup and fresh berries',
            'price': 55.00, 'category_id': 3, 'stock': 15, 'image_url': 'pancakes.jpg',
            'ingredients': 'Flour, Eggs, Milk, Sugar, Baking powder, Vanilla extract, Butter, Maple syrup, Fresh berries',
            'calories': 450, 'preparation_time': 12, 'allergens': 'Gluten, Eggs, Dairy',
            'serving_size': '3 pancakes', 'dietary_info': 'Vegetarian'
        },

        # Main Courses
        {
            'name': 'Grilled Chicken',
            'description': 'Marinated grilled chicken breast with Mediterranean herbs and spices',
            'price': 120.00, 'category_id': 4, 'stock': 18, 'image_url': 'grilled_chicken.jpg',
            'ingredients': 'Chicken breast, Olive oil, Garlic, Lemon juice, Oregano, Thyme, Rosemary, Salt, Black pepper, Side vegetables',
            'calories': 320, 'preparation_time': 25, 'allergens': 'None',
            'serving_size': '200g chicken + sides', 'dietary_info': 'Gluten-free, High protein'
        },
        {
            'name': 'Beef Burger',
            'description': 'Juicy beef burger with cheese, lettuce, tomato, and crispy fries',
            'price': 95.00, 'category_id': 4, 'stock': 22, 'image_url': 'beef_burger.jpg',
            'ingredients': 'Ground beef, Burger bun, Cheddar cheese, Lettuce, Tomato, Onion, Pickles, Special sauce, French fries',
            'calories': 680, 'preparation_time': 15, 'allergens': 'Gluten, Dairy',
            'serving_size': '1 burger + fries', 'dietary_info': 'High protein'
        },
        {
            'name': 'Fish & Chips',
            'description': 'Crispy battered fish fillet served with golden fries and tartar sauce',
            'price': 110.00, 'category_id': 4, 'stock': 16, 'image_url': 'fish_and_chips.jpg',
            'ingredients': 'White fish fillet, Flour, Beer batter, Potatoes, Vegetable oil, Tartar sauce, Lemon, Mushy peas',
            'calories': 590, 'preparation_time': 18, 'allergens': 'Gluten, Fish',
            'serving_size': '1 fish fillet + chips', 'dietary_info': 'High protein'
        },

        # Desserts
        {
            'name': 'Chocolate Cake',
            'description': 'Rich chocolate layer cake with chocolate ganache and fresh cream',
            'price': 40.00, 'category_id': 5, 'stock': 12, 'image_url': 'chocolate_cake.jpg',
            'ingredients': 'Dark chocolate, Flour, Sugar, Eggs, Butter, Cocoa powder, Heavy cream, Vanilla extract',
            'calories': 420, 'preparation_time': 5, 'allergens': 'Gluten, Eggs, Dairy',
            'serving_size': '1 slice', 'dietary_info': 'Vegetarian'
        },
        {
            'name': 'Baklava',
            'description': 'Traditional Middle Eastern pastry with layers of phyllo, nuts, and honey syrup',
            'price': 35.00, 'category_id': 5, 'stock': 20, 'image_url': 'baklava.jpg',
            'ingredients': 'Phyllo pastry, Mixed nuts (walnuts, pistachios), Honey, Sugar syrup, Butter, Cinnamon, Rose water',
            'calories': 280, 'preparation_time': 3, 'allergens': 'Gluten, Nuts, Dairy',
            'serving_size': '2 pieces', 'dietary_info': 'Vegetarian'
        },
        {
            'name': 'Ice Cream',
            'description': 'Vanilla ice cream served with chocolate sauce, nuts, and fresh fruit toppings',
            'price': 30.00, 'category_id': 5, 'stock': 25, 'image_url': 'ice_cream.jpg',
            'ingredients': 'Vanilla ice cream, Chocolate sauce, Mixed nuts, Fresh fruits, Whipped cream, Wafer cone',
            'calories': 320, 'preparation_time': 3, 'allergens': 'Dairy, Nuts, Gluten',
            'serving_size': '2 scoops + toppings', 'dietary_info': 'Vegetarian'
        },
    ]
    
    for item_data in menu_items_data:
        menu_item = MenuItem(
            name=item_data['name'],
            description=item_data['description'],
            price=item_data['price'],
            category_id=item_data['category_id'],
            stock=item_data['stock'],
            image_url=item_data['image_url'],
            ingredients=item_data['ingredients'],
            calories=item_data['calories'],
            preparation_time=item_data['preparation_time'],
            allergens=item_data['allergens'],
            serving_size=item_data['serving_size'],
            dietary_info=item_data['dietary_info']
        )
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
