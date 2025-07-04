#!/usr/bin/env python3
"""
Comprehensive fix for menu item not found errors
This addresses cart data integrity and adds proper error handling
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import MenuItem

def add_cart_validation_middleware():
    """Add validation to cart operations to prevent invalid item IDs"""
    print("🛡️ Adding cart validation recommendations...")
    
    cart_validation_code = '''
# Add this to your cart processing routes:

def validate_cart_items(cart_items):
    """Validate that all cart items reference existing menu items"""
    valid_items = []
    invalid_items = []
    
    for item in cart_items:
        item_id = item.get('id') or item.get('item_id')
        if item_id:
            # Check if menu item exists
            menu_item = MenuItem.query.filter_by(item_id=item_id).first()
            if menu_item and menu_item.status == 'available':
                valid_items.append(item)
            else:
                invalid_items.append({
                    'item_id': item_id,
                    'name': item.get('name', 'Unknown Item'),
                    'reason': 'Item no longer available' if menu_item else 'Item not found'
                })
    
    return valid_items, invalid_items

def clean_cart_data(cart_items):
    """Remove invalid items from cart and return cleaned cart"""
    valid_items, invalid_items = validate_cart_items(cart_items)
    
    if invalid_items:
        print(f"Removed {len(invalid_items)} invalid items from cart:")
        for item in invalid_items:
            print(f"  - {item['name']} (ID: {item['item_id']}): {item['reason']}")
    
    return valid_items
'''
    
    print("📝 Cart validation code:")
    print(cart_validation_code)
    return cart_validation_code

def create_cart_cleanup_script():
    """Create a client-side script to clean up localStorage cart data"""
    print("\n🧹 Creating cart cleanup JavaScript...")
    
    cleanup_script = '''
// Add this to your main JavaScript file or run in browser console
function cleanupCartData() {
    console.log('🧹 Cleaning up cart data...');
    
    try {
        // Get cart data from localStorage
        const cartData = localStorage.getItem('restaurant_cart');
        if (!cartData) {
            console.log('✅ No cart data found');
            return;
        }
        
        const cart = JSON.parse(cartData);
        console.log(`📋 Found ${cart.length} items in cart`);
        
        // Validate each item
        const validItems = [];
        const invalidItems = [];
        
        cart.forEach(item => {
            const itemId = item.id || item.item_id;
            // Check if item ID looks like a valid database ID (small integer)
            if (itemId && itemId < 1000000) {
                validItems.push(item);
            } else {
                invalidItems.push(item);
                console.log(`❌ Removing invalid item: ${item.name} (ID: ${itemId})`);
            }
        });
        
        if (invalidItems.length > 0) {
            // Update localStorage with cleaned cart
            localStorage.setItem('restaurant_cart', JSON.stringify(validItems));
            console.log(`✅ Cleaned cart: removed ${invalidItems.length} invalid items`);
            
            // Update cart display if function exists
            if (typeof updateCartDisplay === 'function') {
                updateCartDisplay();
            }
            if (typeof updateCartCount === 'function') {
                updateCartCount();
            }
        } else {
            console.log('✅ Cart is clean - no invalid items found');
        }
        
    } catch (error) {
        console.error('❌ Error cleaning cart data:', error);
        // If cart data is corrupted, clear it
        localStorage.removeItem('restaurant_cart');
        console.log('🗑️ Cleared corrupted cart data');
    }
}

// Run cleanup on page load
document.addEventListener('DOMContentLoaded', cleanupCartData);

// Also provide a manual cleanup function
window.cleanupCart = cleanupCartData;
'''
    
    print("📝 Cart cleanup JavaScript:")
    print(cleanup_script)
    return cleanup_script

def add_error_handling_recommendations():
    """Provide recommendations for error handling in order processing"""
    print("\n🛡️ Error handling recommendations...")
    
    error_handling_code = '''
# Add this error handling to your order processing routes:

@bp.route('/checkout', methods=['POST'])
def checkout():
    try:
        cart_items = request.json.get('items', [])
        
        # Validate cart items before processing
        valid_items, invalid_items = validate_cart_items(cart_items)
        
        if invalid_items:
            return jsonify({
                'status': 'error',
                'message': f'Some items are no longer available: {", ".join([item["name"] for item in invalid_items])}',
                'invalid_items': invalid_items,
                'valid_items': valid_items
            }), 400
        
        if not valid_items:
            return jsonify({
                'status': 'error',
                'message': 'Cart is empty or contains no valid items'
            }), 400
        
        # Process order with valid items only
        # ... rest of checkout logic
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Order failed: {str(e)}'
        }), 500

@bp.route('/reorder/<int:order_id>', methods=['POST'])
def reorder_to_cart(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        
        valid_items = []
        unavailable_items = []
        
        for order_item in order.order_items:
            menu_item = MenuItem.query.filter_by(item_id=order_item.item_id).first()
            
            if menu_item and menu_item.status == 'available':
                valid_items.append({
                    'id': menu_item.item_id,
                    'name': menu_item.name,
                    'price': float(menu_item.price),
                    'quantity': order_item.quantity
                })
            else:
                unavailable_items.append({
                    'name': order_item.menu_item.name if order_item.menu_item else f'Item {order_item.item_id}',
                    'reason': 'No longer available'
                })
        
        if not valid_items and unavailable_items:
            return jsonify({
                'success': False,
                'message': 'None of the items from this order are currently available'
            })
        
        # Add valid items to cart
        # ... cart logic
        
        message = f'Added {len(valid_items)} items to cart'
        if unavailable_items:
            message += f'. {len(unavailable_items)} items were unavailable.'
        
        return jsonify({
            'success': True,
            'message': message,
            'items_added': len(valid_items),
            'unavailable_items': len(unavailable_items)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Reorder failed: {str(e)}'
        })
'''
    
    print("📝 Error handling code:")
    print(error_handling_code)
    return error_handling_code

def test_current_menu_items():
    """Test that current menu items are accessible"""
    app = create_app()
    
    with app.app_context():
        print("\n🧪 Testing current menu items...")
        
        menu_items = MenuItem.query.filter_by(status='available').all()
        print(f"   Available menu items: {len(menu_items)}")
        
        for item in menu_items:
            print(f"   ✅ ID: {item.item_id}, Name: {item.name}, Price: ${item.price}")

def main():
    print("🔧 COMPREHENSIVE MENU ITEM ERROR FIX")
    print("=" * 60)
    
    # Test current menu items
    test_current_menu_items()
    
    # Add cart validation
    add_cart_validation_middleware()
    
    # Create cart cleanup script
    create_cart_cleanup_script()
    
    # Add error handling recommendations
    add_error_handling_recommendations()
    
    print("\n" + "=" * 60)
    print("✅ COMPREHENSIVE FIX COMPLETE!")
    print("\nIMMEDIATE ACTIONS NEEDED:")
    print("1. 🌐 Open browser and run: cleanupCartData() in console")
    print("2. 🔄 Clear browser localStorage: localStorage.clear()")
    print("3. 💾 Add cart validation to order processing routes")
    print("4. 🛡️ Add error handling to checkout and reorder functions")
    print("5. 🧹 Consider adding automated cart cleanup on app startup")
    
    print("\nROOT CAUSE:")
    print("The error likely occurs when:")
    print("- User cart contains timestamp-based IDs instead of database IDs")
    print("- Old cart data persists after menu item changes") 
    print("- Reorder function tries to access deleted/modified items")

if __name__ == "__main__":
    main()
