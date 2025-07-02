#!/usr/bin/env python3
"""
Database integrity test to check for any remaining schema issues
"""

from app import create_app
from app.models import User, Order, OrderItem, MenuItem, Category, Table, ServiceRequest
from app.extensions import db
from sqlalchemy import text

def test_database_integrity():
    app = create_app()
    
    with app.app_context():
        print("=== DATABASE INTEGRITY TEST ===\n")
        
        # Test 1: Check table existence
        print("1. Checking table structure...")
        try:
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            required_tables = ['user', 'menu_item', 'category', 'order', 'order_item', 'table', 'service_request']
            
            missing_tables = [table for table in required_tables if table not in tables]
            if missing_tables:
                print(f"   ✗ Missing tables: {missing_tables}")
            else:
                print("   ✓ All required tables exist")
        except Exception as e:
            print(f"   ✗ Table check error: {e}")
        
        # Test 2: Check OrderItem.item_id column
        print("\n2. Checking OrderItem schema...")
        try:
            columns = inspector.get_columns('order_item')
            column_names = [col['name'] for col in columns]
            
            if 'item_id' in column_names:
                print("   ✓ OrderItem.item_id column exists")
            else:
                print("   ✗ OrderItem.item_id column missing")
                
            if 'menu_item_id' in column_names:
                print("   ⚠ OrderItem.menu_item_id still exists (should be removed or ignored)")
        except Exception as e:
            print(f"   ✗ OrderItem schema check error: {e}")
        
        # Test 3: Check foreign key relationships
        print("\n3. Testing relationship integrity...")
        try:
            # Test Order -> User relationship
            order_count = Order.query.count()
            valid_order_users = db.session.query(Order).join(User).count()
            print(f"   Orders: {order_count} total, {valid_order_users} with valid users")
            
            # Test OrderItem -> MenuItem relationship
            order_item_count = OrderItem.query.count()
            valid_order_items = db.session.query(OrderItem).join(MenuItem, OrderItem.item_id == MenuItem.item_id).count()
            print(f"   Order Items: {order_item_count} total, {valid_order_items} with valid menu items")
            
            # Test MenuItem -> Category relationship
            menu_item_count = MenuItem.query.count()
            valid_menu_categories = db.session.query(MenuItem).join(Category).count()
            print(f"   Menu Items: {menu_item_count} total, {valid_menu_categories} with valid categories")
            
        except Exception as e:
            print(f"   ✗ Relationship test error: {e}")
        
        # Test 4: Check data consistency
        print("\n4. Testing data consistency...")
        try:
            # Check for orders with user_id = 1 (admin user)
            admin_user = User.query.filter_by(role='admin').first()
            if admin_user:
                admin_orders = Order.query.filter_by(user_id=admin_user.user_id).count()
                print(f"   Admin user orders: {admin_orders}")
                if admin_orders > 0:
                    print("   ⚠ Warning: Admin user has orders (might be test data or legacy)")
            
            # Check for customer orders
            customer_users = User.query.filter_by(role='customer').all()
            customer_order_count = 0
            for customer in customer_users:
                orders = Order.query.filter_by(user_id=customer.user_id).count()
                customer_order_count += orders
                if orders > 0:
                    print(f"   Customer {customer.username}: {orders} orders")
            
            print(f"   Total customer orders: {customer_order_count}")
            
        except Exception as e:
            print(f"   ✗ Data consistency check error: {e}")
        
        # Test 5: Check for orphaned records
        print("\n5. Checking for orphaned records...")
        try:
            # Orders without valid users
            orphaned_orders = db.session.execute(text("""
                SELECT COUNT(*) FROM [order] o 
                WHERE o.user_id NOT IN (SELECT user_id FROM [user])
            """)).scalar()
            print(f"   Orphaned orders: {orphaned_orders}")
            
            # Order items without valid orders or menu items
            orphaned_items = db.session.execute(text("""
                SELECT COUNT(*) FROM order_item oi 
                WHERE oi.order_id NOT IN (SELECT order_id FROM [order])
                   OR oi.item_id NOT IN (SELECT item_id FROM menu_item)
            """)).scalar()
            print(f"   Orphaned order items: {orphaned_items}")
            
        except Exception as e:
            print(f"   ✗ Orphaned records check error: {e}")
        
        print("\n=== DATABASE INTEGRITY TEST COMPLETE ===")
        print("\nRECOMMENDATIONS:")
        print("- If any integrity issues are found, run the fix scripts")
        print("- Consider cleaning up any test data assigned to admin users")
        print("- Monitor for future orphaned records")

if __name__ == "__main__":
    test_database_integrity()
