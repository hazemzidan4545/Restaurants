#!/usr/bin/env python3
"""
Test script for waiter functionality
"""

from app import create_app
from app.extensions import db
from app.models import User, Order, OrderItem, MenuItem, Table, ServiceRequest, Category
from datetime import datetime, timedelta
import random

def test_waiter_functionality():
    """Test waiter dashboard functionality"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🧪 Testing Waiter Functionality")
            print("=" * 50)
            
            # 1. Check if waiter user exists
            waiter = User.query.filter_by(role='waiter').first()
            if not waiter:
                print("Creating test waiter...")
                waiter = User(
                    name='Test Waiter',
                    email='waiter@test.com',
                    role='waiter'
                )
                waiter.set_password('password123')
                db.session.add(waiter)
                db.session.commit()
                print(f"✅ Created waiter: {waiter.name}")
            else:
                print(f"✅ Found waiter: {waiter.name}")
            
            # 2. Check orders
            orders = Order.query.all()
            print(f"📋 Total orders in system: {len(orders)}")
            
            # Get order counts by status
            order_counts = {
                'new': Order.query.filter_by(status='new').count(),
                'processing': Order.query.filter_by(status='processing').count(),
                'completed': Order.query.filter_by(status='completed').count(),
                'rejected': Order.query.filter_by(status='rejected').count()
            }
            
            print("📊 Order Status Breakdown:")
            for status, count in order_counts.items():
                print(f"   {status.title()}: {count}")
            
            # 3. Check service requests
            service_requests = ServiceRequest.query.all()
            print(f"🔔 Total service requests: {len(service_requests)}")
            
            # Get service request counts by status
            request_counts = {
                'pending': ServiceRequest.query.filter_by(status='pending').count(),
                'acknowledged': ServiceRequest.query.filter_by(status='acknowledged').count(),
                'completed': ServiceRequest.query.filter_by(status='completed').count()
            }
            
            print("📊 Service Request Status Breakdown:")
            for status, count in request_counts.items():
                print(f"   {status.title()}: {count}")
            
            # 4. Check tables
            tables = Table.query.all()
            print(f"🪑 Total tables: {len(tables)}")
            
            table_stats = {
                'available': Table.query.filter_by(status='available').count(),
                'occupied': Table.query.filter_by(status='occupied').count(),
                'reserved': Table.query.filter_by(status='reserved').count()
            }
            
            print("📊 Table Status Breakdown:")
            for status, count in table_stats.items():
                print(f"   {status.title()}: {count}")
            
            # 5. Create test data if needed
            if len(orders) < 5:
                print("\n🔧 Creating test orders...")
                create_test_orders()
            
            if len(service_requests) < 3:
                print("\n🔧 Creating test service requests...")
                create_test_service_requests()
            
            print("\n✅ Waiter functionality test completed!")
            print("\n🌐 You can now test the waiter dashboard at:")
            print("   http://localhost:5000/waiter/dashboard")
            print("   Login with waiter credentials")
            
            return True
            
        except Exception as e:
            print(f"❌ Test error: {e}")
            import traceback
            traceback.print_exc()
            return False

def create_test_orders():
    """Create test orders for waiter dashboard"""
    try:
        # Get test data
        customer = User.query.filter_by(role='customer').first()
        if not customer:
            customer = User(
                name='Test Customer',
                email='customer@test.com',
                role='customer'
            )
            customer.set_password('password123')
            db.session.add(customer)
            db.session.commit()
        
        tables = Table.query.limit(3).all()
        if not tables:
            # Create test tables
            for i in range(1, 4):
                table = Table(table_number=f'T{i:03d}', capacity=4)
                db.session.add(table)
            db.session.commit()
            tables = Table.query.limit(3).all()
        
        menu_items = MenuItem.query.filter_by(status='available').limit(5).all()
        
        if not menu_items:
            print("⚠️ No menu items found. Please add menu items first.")
            return
        
        # Create test orders with different statuses
        statuses = ['new', 'processing', 'completed']
        
        for i, status in enumerate(statuses):
            order = Order(
                user_id=customer.user_id,
                table_id=tables[i % len(tables)].table_id,
                status=status,
                total_amount=random.uniform(50, 200),
                order_time=datetime.utcnow() - timedelta(minutes=random.randint(10, 120))
            )
            db.session.add(order)
            db.session.flush()  # Get order ID
            
            # Add order items
            for j in range(random.randint(1, 3)):
                item = random.choice(menu_items)
                order_item = OrderItem(
                    order_id=order.order_id,
                    item_id=item.item_id,
                    quantity=random.randint(1, 3),
                    unit_price=item.price
                )
                db.session.add(order_item)
        
        db.session.commit()
        print("✅ Created test orders")
        
    except Exception as e:
        print(f"❌ Error creating test orders: {e}")
        db.session.rollback()

def create_test_service_requests():
    """Create test service requests"""
    try:
        customer = User.query.filter_by(role='customer').first()
        tables = Table.query.limit(3).all()
        
        if not customer or not tables:
            print("⚠️ Need customer and tables for service requests")
            return
        
        request_types = ['clean_table', 'refill_coals', 'adjust_ac', 'call_waiter']
        descriptions = [
            'Please clean our table',
            'Need fresh coals for hookah',
            'AC is too cold, please adjust',
            'Need assistance with menu'
        ]
        
        for i in range(3):
            request = ServiceRequest(
                user_id=customer.user_id,
                table_id=tables[i % len(tables)].table_id,
                request_type=random.choice(request_types),
                description=random.choice(descriptions),
                status='pending',
                created_at=datetime.utcnow() - timedelta(minutes=random.randint(5, 60))
            )
            db.session.add(request)
        
        db.session.commit()
        print("✅ Created test service requests")
        
    except Exception as e:
        print(f"❌ Error creating test service requests: {e}")
        db.session.rollback()

if __name__ == '__main__':
    test_waiter_functionality()
