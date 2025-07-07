#!/usr/bin/env python3
"""
Test script for revenue analytics functionality
"""

from app import create_app
from app.extensions import db
from app.models import User, Order, OrderItem, MenuItem, Category
from app.modules.admin.routes import calculate_revenue_metrics, calculate_customer_analytics, calculate_product_performance, calculate_time_analytics
from datetime import datetime, timedelta
import random

def test_revenue_analytics():
    """Test revenue analytics functionality"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🧪 TESTING REVENUE ANALYTICS")
            print("=" * 50)
            
            # 1. Test data availability
            print("\n1️⃣ Checking Data Availability...")
            test_data_availability()
            
            # 2. Test revenue metrics calculation
            print("\n2️⃣ Testing Revenue Metrics...")
            test_revenue_metrics()
            
            # 3. Test customer analytics
            print("\n3️⃣ Testing Customer Analytics...")
            test_customer_analytics()
            
            # 4. Test product performance
            print("\n4️⃣ Testing Product Performance...")
            test_product_performance()
            
            # 5. Test time analytics
            print("\n5️⃣ Testing Time Analytics...")
            test_time_analytics()
            
            print("\n✅ REVENUE ANALYTICS TESTING COMPLETED!")
            print("\n🌐 Access Revenue Analytics at:")
            print("   http://localhost:5000/admin/analytics/revenue")
            
            return True
            
        except Exception as e:
            print(f"❌ Revenue analytics test error: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_data_availability():
    """Test if we have sufficient data for analytics"""
    orders = Order.query.count()
    order_items = OrderItem.query.count()
    customers = User.query.filter_by(role='customer').count()
    menu_items = MenuItem.query.count()
    categories = Category.query.count()
    
    print(f"   📊 Orders: {orders}")
    print(f"   🛒 Order Items: {order_items}")
    print(f"   👥 Customers: {customers}")
    print(f"   🍽️ Menu Items: {menu_items}")
    print(f"   📂 Categories: {categories}")
    
    if orders < 5:
        print("   ⚠️ Creating additional test data...")
        create_additional_test_data()
        print("   ✅ Additional test data created")

def test_revenue_metrics():
    """Test revenue metrics calculation"""
    # Test for current month
    now = datetime.now()
    start_date = datetime(now.year, now.month, 1)
    end_date = now
    
    base_query = Order.query.filter(
        Order.order_time >= start_date,
        Order.order_time <= end_date
    )
    
    revenue_data = calculate_revenue_metrics(base_query, start_date, end_date, 'month')
    
    print(f"   💰 Total Revenue: {revenue_data['total_revenue']:.2f} EGP")
    print(f"   📋 Total Orders: {revenue_data['total_orders']}")
    print(f"   💳 Avg Order Value: {revenue_data['avg_order_value']:.2f} EGP")
    print(f"   📈 Revenue Growth: {revenue_data['growth']['revenue_growth']}%")
    print(f"   📊 Status Breakdown: {len(revenue_data['status_breakdown'])} statuses")

def test_customer_analytics():
    """Test customer analytics calculation"""
    now = datetime.now()
    start_date = datetime(now.year, now.month, 1)
    end_date = now
    
    base_query = Order.query.filter(
        Order.order_time >= start_date,
        Order.order_time <= end_date
    )
    
    customer_data = calculate_customer_analytics(base_query, start_date, end_date)
    
    print(f"   👥 Unique Customers: {customer_data['unique_customers']}")
    print(f"   📋 Total Orders: {customer_data['total_orders']}")
    print(f"   📊 Orders per Customer: {customer_data['orders_per_customer']}")
    print(f"   🏆 Top Customers: {len(customer_data['top_customers'])}")

def test_product_performance():
    """Test product performance calculation"""
    now = datetime.now()
    start_date = datetime(now.year, now.month, 1)
    end_date = now
    
    base_query = Order.query.filter(
        Order.order_time >= start_date,
        Order.order_time <= end_date
    )
    
    product_data = calculate_product_performance(base_query, start_date, end_date)
    
    print(f"   🌟 Top Products: {len(product_data['top_products'])}")
    print(f"   📂 Category Performance: {len(product_data['category_performance'])}")
    
    if product_data['top_products']:
        top_product = product_data['top_products'][0]
        print(f"   🥇 Best Product: {top_product['name']} ({top_product['revenue']:.2f} EGP)")

def test_time_analytics():
    """Test time analytics calculation"""
    now = datetime.now()
    start_date = datetime(now.year, now.month, 1)
    end_date = now
    
    base_query = Order.query.filter(
        Order.order_time >= start_date,
        Order.order_time <= end_date
    )
    
    time_data = calculate_time_analytics(base_query, start_date, end_date, 'month')
    
    print(f"   🕐 Hourly Distribution: {len(time_data['hourly_distribution'])} hours")
    
    # Find peak hour
    if time_data['hourly_distribution']:
        peak_hour = max(time_data['hourly_distribution'], key=lambda x: x['revenue'])
        print(f"   🔥 Peak Hour: {peak_hour['hour']}:00 ({peak_hour['revenue']:.2f} EGP)")

def create_additional_test_data():
    """Create additional test data for analytics"""
    try:
        # Get existing data
        customer = User.query.filter_by(role='customer').first()
        menu_items = MenuItem.query.filter_by(status='available').limit(5).all()
        
        if not customer or not menu_items:
            print("   ⚠️ Missing required data for test creation")
            return
        
        # Create orders for the past 30 days
        for i in range(20):
            # Random date in the past 30 days
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            order_time = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
            
            # Random order status
            status = random.choice(['completed', 'completed', 'completed', 'new', 'processing'])
            
            # Create order
            order = Order(
                user_id=customer.user_id,
                status=status,
                total_amount=random.uniform(50, 300),
                order_time=order_time
            )
            db.session.add(order)
            db.session.flush()
            
            # Add order items
            num_items = random.randint(1, 4)
            for j in range(num_items):
                item = random.choice(menu_items)
                order_item = OrderItem(
                    order_id=order.order_id,
                    item_id=item.item_id,
                    quantity=random.randint(1, 3),
                    unit_price=item.price
                )
                db.session.add(order_item)
        
        db.session.commit()
        print("   ✅ Created 20 additional test orders")
        
    except Exception as e:
        print(f"   ❌ Error creating test data: {e}")
        db.session.rollback()

if __name__ == '__main__':
    success = test_revenue_analytics()
    if success:
        print("\n🎉 REVENUE ANALYTICS READY FOR USE!")
    else:
        print("\n💥 Revenue analytics testing failed!")
