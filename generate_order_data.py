#!/usr/bin/env python3
"""
Script to generate realistic random order data for testing popular items functionality
"""

import random
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models import User, MenuItem, Order, OrderItem, Table

def create_sample_users():
    """Create sample users for orders"""
    sample_users = [
        {'name': 'Ahmed Hassan', 'email': 'ahmed.hassan@email.com', 'phone': '01234567890'},
        {'name': 'Fatma Ali', 'email': 'fatma.ali@email.com', 'phone': '01234567891'},
        {'name': 'Mohamed Saeed', 'email': 'mohamed.saeed@email.com', 'phone': '01234567892'},
        {'name': 'Nour Ibrahim', 'email': 'nour.ibrahim@email.com', 'phone': '01234567893'},
        {'name': 'Omar Khaled', 'email': 'omar.khaled@email.com', 'phone': '01234567894'},
        {'name': 'Yasmin Mostafa', 'email': 'yasmin.mostafa@email.com', 'phone': '01234567895'},
        {'name': 'Karim Farouk', 'email': 'karim.farouk@email.com', 'phone': '01234567896'},
        {'name': 'Dina Mahmoud', 'email': 'dina.mahmoud@email.com', 'phone': '01234567897'},
        {'name': 'Tamer Youssef', 'email': 'tamer.youssef@email.com', 'phone': '01234567898'},
        {'name': 'Rana Adel', 'email': 'rana.adel@email.com', 'phone': '01234567899'},
    ]
    
    created_users = []
    for user_data in sample_users:
        # Check if user already exists
        existing_user = User.query.filter_by(email=user_data['email']).first()
        if not existing_user:
            user = User(
                name=user_data['name'],
                email=user_data['email'],
                phone=user_data['phone'],
                role='customer'
            )
            user.set_password('password123')  # Default password
            db.session.add(user)
            created_users.append(user)
        else:
            created_users.append(existing_user)
    
    db.session.commit()
    return created_users

def create_sample_tables():
    """Create sample tables if they don't exist"""
    tables = []
    for i in range(1, 11):  # Tables 1-10
        existing_table = Table.query.filter_by(table_number=str(i)).first()
        if not existing_table:
            table = Table(
                table_number=str(i),
                capacity=random.choice([2, 4, 6, 8]),
                status='available'
            )
            db.session.add(table)
            tables.append(table)
        else:
            tables.append(existing_table)
    
    db.session.commit()
    return tables

def generate_realistic_orders(num_orders=100):
    """Generate realistic random orders with weighted item popularity"""
    
    # Get all available menu items
    menu_items = MenuItem.query.filter_by(status='available').all()
    users = create_sample_users()
    tables = create_sample_tables()
    
    if not menu_items:
        print("No menu items found. Please run init_db.py first.")
        return
    
    # Define popularity weights for different items (higher = more popular)
    item_popularity = {
        'Turkish Coffee': 0.25,      # Very popular
        'Grilled Chicken': 0.20,     # Very popular
        'Beef Burger': 0.18,         # Popular
        'Fresh Orange Juice': 0.15,  # Popular
        'Egyptian Breakfast': 0.12,  # Moderately popular
        'Pancakes': 0.10,            # Moderately popular
        'Chocolate Cake': 0.08,      # Less popular
        'Fish & Chips': 0.07,        # Less popular
        'Apple Mint Hookah': 0.06,   # Less popular
        'Cheese Omelette': 0.05,     # Less popular
        'Mint Tea': 0.04,            # Less popular
        'Ice Cream': 0.04,           # Less popular
        'Baklava': 0.03,             # Less popular
        'Double Apple Hookah': 0.02, # Least popular
        'Grape Hookah': 0.01,        # Least popular
    }
    
    print(f"Generating {num_orders} realistic orders...")
    
    orders_created = 0
    for i in range(num_orders):
        try:
            # Random order time within last 30 days
            order_time = datetime.utcnow() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # Create order
            order = Order(
                user_id=random.choice(users).user_id,
                table_id=random.choice(tables).table_id,
                order_time=order_time,
                status=random.choice(['completed', 'completed', 'completed', 'processing', 'new']),  # Most orders completed
                total_amount=0,  # Will be calculated
                notes=random.choice(['', '', '', 'Extra spicy', 'No onions', 'Well done', 'Less salt'])
            )
            db.session.add(order)
            db.session.flush()  # Get order ID
            
            # Add 1-4 items per order
            num_items = random.choices([1, 2, 3, 4], weights=[0.3, 0.4, 0.2, 0.1])[0]
            total_amount = 0
            
            selected_items = []
            for _ in range(num_items):
                # Select items based on popularity weights
                available_items = [item for item in menu_items if item not in selected_items]
                if not available_items:
                    break
                
                # Use weighted selection based on item popularity
                weights = []
                for item in available_items:
                    weight = item_popularity.get(item.name, 0.01)  # Default low weight
                    weights.append(weight)
                
                selected_item = random.choices(available_items, weights=weights)[0]
                selected_items.append(selected_item)
                
                # Random quantity (1-3, mostly 1)
                quantity = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
                
                order_item = OrderItem(
                    order_id=order.order_id,
                    item_id=selected_item.item_id,
                    quantity=quantity,
                    unit_price=selected_item.price,
                    note=random.choice(['', '', '', 'Medium spice', 'Extra sauce', 'No ice'])
                )
                db.session.add(order_item)
                total_amount += float(selected_item.price) * quantity
            
            # Add service charge
            total_amount += 2.00
            order.total_amount = total_amount
            
            # Set completion time for completed orders
            if order.status == 'completed':
                order.completed_at = order_time + timedelta(minutes=random.randint(15, 45))
            
            orders_created += 1
            
            if orders_created % 20 == 0:
                print(f"Created {orders_created} orders...")
                
        except Exception as e:
            print(f"Error creating order {i}: {e}")
            db.session.rollback()
            continue
    
    try:
        db.session.commit()
        print(f"✅ Successfully created {orders_created} orders with realistic popularity patterns!")
        
        # Show popularity statistics
        print("\n📊 Order Statistics:")
        from sqlalchemy import func
        popular_items = db.session.query(
            MenuItem.name,
            func.sum(OrderItem.quantity).label('total_ordered')
        ).join(OrderItem).group_by(MenuItem.name).order_by(
            func.sum(OrderItem.quantity).desc()
        ).limit(10).all()
        
        for i, (name, count) in enumerate(popular_items, 1):
            print(f"{i:2d}. {name:<25} - {count} orders")
            
    except Exception as e:
        print(f"Error committing orders: {e}")
        db.session.rollback()

def main():
    """Main function to generate order data"""
    app = create_app()
    
    with app.app_context():
        print("🚀 Starting order data generation...")
        generate_realistic_orders(150)  # Generate 150 orders
        print("✨ Order data generation complete!")

if __name__ == "__main__":
    main()
