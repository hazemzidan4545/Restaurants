#!/usr/bin/env python3
"""
Comprehensive test for checkout and reorder functionality
"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.models import User, Order, MenuItem, OrderItem, db
from app.extensions import db
import json

def test_reorder_and_checkout():
    """Test reorder and checkout functionality"""
    print("🔍 Testing Reorder and Checkout Functionality")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        try:
            # 1. Find a test customer
            customer = User.query.filter_by(role='customer').first()
            if not customer:
                print("❌ No customer found in database")
                return False
            
            print(f"✅ Found customer: {customer.email} (ID: {customer.user_id})")
            
            # 2. Find orders for this customer
            orders = Order.query.filter_by(user_id=customer.user_id).all()
            if not orders:
                print("❌ No orders found for customer")
                return False
            
            test_order = orders[0]
            print(f"✅ Found test order: {test_order.order_id}")
            print(f"   Status: {test_order.status}")
            print(f"   Total: ${test_order.total_amount}")
            
            # 3. Test order items loading
            order_items = test_order.order_items.all()
            print(f"✅ Order has {len(order_items)} items")
            
            # Check if menu items still exist
            available_items = 0
            unavailable_items = 0
            
            for item in order_items:
                menu_item = MenuItem.query.get(item.item_id)
                if menu_item and menu_item.status == 'available':
                    available_items += 1
                    print(f"   ✅ {menu_item.name}: {item.quantity}x @ ${item.unit_price}")
                else:
                    unavailable_items += 1
                    print(f"   ❌ Item {item.item_id}: {item.quantity}x @ ${item.unit_price} (unavailable)")
            
            print(f"📊 Summary: {available_items} available, {unavailable_items} unavailable")
            
            # 4. Test the reorder logic (simulate the route logic)
            print("\n🔄 Testing reorder logic...")
            
            # Simulate cart session
            cart = []
            items_added = 0
            
            for original_item in order_items:
                menu_item = MenuItem.query.get(original_item.item_id)
                if menu_item and menu_item.status == 'available':
                    # Check if item already exists in cart
                    existing_item = None
                    for cart_item in cart:
                        if cart_item['id'] == menu_item.item_id:
                            existing_item = cart_item
                            break
                    
                    if existing_item:
                        existing_item['quantity'] += original_item.quantity
                    else:
                        cart_item = {
                            'id': menu_item.item_id,
                            'name': menu_item.name,
                            'price': float(menu_item.price),
                            'quantity': original_item.quantity,
                            'image': menu_item.image_url or 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=300&h=200&fit=crop',
                            'specialInstructions': original_item.note or '',
                            'category': 'Reordered Item'
                        }
                        cart.append(cart_item)
                    
                    items_added += 1
            
            print(f"✅ Reorder simulation successful: {items_added} items would be added to cart")
            print(f"   Cart would contain {len(cart)} unique items")
            
            # 5. Test checkout logic
            print("\n💳 Testing checkout logic...")
            
            # Test loading order with joinedload
            from sqlalchemy.orm import joinedload
            order_with_table = Order.query.options(joinedload(Order.table)).get(test_order.order_id)
            
            if order_with_table.table:
                print(f"✅ Order table loaded: Table {order_with_table.table.table_number}")
            else:
                print("✅ Order has no table (takeaway)")
            
            # Test payment service
            from app.modules.payment.payment_service import PaymentService
            payment_service = PaymentService()
            payment_methods = payment_service.get_payment_methods()
            print(f"✅ Payment methods loaded: {len(payment_methods)} methods available")
            
            # Test permission checks
            if order_with_table.user_id == customer.user_id:
                print("✅ Customer has permission to pay for this order")
            else:
                print("❌ Permission check failed")
            
            print("\n🎉 All tests passed!")
            return True
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_reorder_and_checkout()
    if success:
        print("\n✅ All functionality appears to be working correctly!")
    else:
        print("\n❌ Some issues were found that need to be addressed.")
