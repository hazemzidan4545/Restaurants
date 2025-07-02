#!/usr/bin/env python3
"""
Simple test to check checkout and reorder functionality
"""
from app import create_app
from app.models import Order, User, MenuItem
from flask_login import login_user
import logging

def test_functionality():
    """Test the functionality manually"""
    app = create_app()
    
    with app.app_context():
        with app.test_client() as client:
            # Try to get a customer user
            customer = User.query.filter_by(email='customer@test.com').first()
            if not customer:
                print("❌ No test customer found. Please create one first.")
                return
            
            # Login as customer
            print(f"🔍 Testing with customer: {customer.email} (ID: {customer.user_id})")
            
            # Get customer orders
            orders = Order.query.filter_by(user_id=customer.user_id).first()
            if not orders:
                print("❌ No orders found for customer")
                return
            
            print(f"✅ Found test order: {orders.order_id}")
            
            # Test checkout route
            try:
                from app.modules.payment.routes import checkout
                from app.modules.payment.payment_service import PaymentService
                from flask import g
                
                with app.test_request_context():
                    # Simulate being logged in
                    from flask_login import login_user
                    login_user(customer)
                    
                    print("🔍 Testing checkout route...")
                    
                    # Get payment methods
                    service = PaymentService()
                    methods = service.get_payment_methods()
                    print(f"✅ Payment methods available: {len(methods)}")
                    
                    # Test order loading with joinedload
                    from sqlalchemy.orm import joinedload
                    order = Order.query.options(joinedload(Order.table)).get(orders.order_id)
                    print(f"✅ Order loaded with table: {order.table.table_number if order.table else 'No table'}")
                    
            except Exception as e:
                print(f"❌ Checkout test failed: {e}")
                import traceback
                traceback.print_exc()
            
            # Test reorder functionality
            try:
                print("\n🔍 Testing reorder functionality...")
                
                # Check order items
                items = orders.order_items.all()
                print(f"✅ Order has {len(items)} items")
                
                for item in items:
                    menu_item = MenuItem.query.get(item.item_id)
                    if menu_item:
                        print(f"  - {menu_item.name}: {item.quantity}x @ ${item.unit_price}")
                    else:
                        print(f"  - Item {item.item_id}: {item.quantity}x @ ${item.unit_price} (menu item not found)")
                
            except Exception as e:
                print(f"❌ Reorder test failed: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    test_functionality()
