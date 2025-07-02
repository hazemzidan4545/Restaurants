#!/usr/bin/env python3
"""
Debug script for checkout and reorder issues
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_checkout_route():
    """Test the checkout route setup"""
    try:
        from app import create_app
        from app.models import Order, Payment
        from app.modules.payment.payment_service import PaymentService
        
        app = create_app()
        with app.app_context():
            print("✅ App created successfully")
            
            # Test PaymentService
            service = PaymentService()
            methods = service.get_payment_methods()
            print(f"✅ PaymentService working, found {len(methods)} payment methods")
            
            # Test Order query
            order = Order.query.first()
            if order:
                print(f"✅ Found sample order: {order.order_id}")
                print(f"   Status: {order.status}")
                print(f"   User ID: {order.user_id}")
                
                # Test table relationship
                if hasattr(order, 'table') and order.table:
                    print(f"   Table: {order.table.table_number}")
                else:
                    print("   ⚠️ No table assigned or table relationship issue")
                    
            else:
                print("❌ No orders found in database")
                
    except Exception as e:
        print(f"❌ Error in checkout test: {e}")
        import traceback
        traceback.print_exc()

def test_reorder_data():
    """Test reorder functionality data access"""
    try:
        from app import create_app
        from app.models import Order, OrderItem, MenuItem
        
        app = create_app()
        with app.app_context():
            print("\n🔍 Testing reorder data access...")
            
            # Find a completed order
            order = Order.query.filter(Order.status.in_(['delivered', 'completed'])).first()
            if not order:
                print("❌ No completed orders found for testing")
                return
                
            print(f"✅ Found completed order: {order.order_id}")
            
            # Test order items access
            order_items = order.order_items.all()
            print(f"✅ Order has {len(order_items)} items")
            
            for item in order_items:
                print(f"   Item ID: {item.item_id}")
                print(f"   Quantity: {item.quantity}")
                print(f"   Note: {getattr(item, 'note', 'NO NOTE FIELD')}")
                print(f"   Has special_requests attr: {hasattr(item, 'special_requests')}")
                
                # Test menu item access
                menu_item = MenuItem.query.get(item.item_id)
                if menu_item:
                    print(f"   Menu item: {menu_item.name}")
                    print(f"   Status: {menu_item.status}")
                    print(f"   Price: {menu_item.price}")
                else:
                    print(f"   ❌ Menu item not found for ID {item.item_id}")
                print("   ---")
                
    except Exception as e:
        print(f"❌ Error in reorder test: {e}")
        import traceback
        traceback.print_exc()

def test_session_functionality():
    """Test session-based cart functionality"""
    try:
        from app import create_app
        
        app = create_app()
        with app.test_request_context():
            from flask import session
            
            print("\n🛒 Testing session cart...")
            
            # Test session access
            session['test'] = 'working'
            print(f"✅ Session test: {session.get('test')}")
            
            # Test cart initialization
            session['cart'] = []
            test_item = {
                'id': 1,
                'name': 'Test Item',
                'price': 25.0,
                'quantity': 2
            }
            session['cart'].append(test_item)
            session.modified = True
            
            print(f"✅ Cart test: {len(session['cart'])} items in cart")
            
    except Exception as e:
        print(f"❌ Error in session test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 DEBUGGING CHECKOUT AND REORDER ISSUES")
    print("=" * 50)
    
    test_checkout_route()
    test_reorder_data() 
    test_session_functionality()
    
    print("\n" + "=" * 50)
    print("🔧 If issues are found, check:")
    print("1. Database has orders with completed status")
    print("2. OrderItem model has 'note' field (not 'special_requests')")
    print("3. Table relationships are properly defined")
    print("4. Flask session is configured with secret key")
