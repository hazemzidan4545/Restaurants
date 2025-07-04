#!/usr/bin/env python3
"""
Quick fix for the menu item error - create JavaScript cart cleanup
"""

def create_cart_cleanup_file():
    """Create a JavaScript file to clean up cart data"""
    
    cleanup_script = '''// Cart Data Cleanup Script
// Run this in browser console or add to your main JS file

function cleanupCartData() {
    console.log('🧹 Cleaning up cart data...');
    
    try {
        // Get cart data from localStorage
        const cartData = localStorage.getItem('restaurant_cart');
        if (!cartData) {
            console.log('✅ No cart data found');
            return { cleaned: 0, total: 0 };
        }
        
        const cart = JSON.parse(cartData);
        console.log(`📋 Found ${cart.length} items in cart`);
        
        // Validate each item
        const validItems = [];
        const invalidItems = [];
        
        cart.forEach(item => {
            const itemId = item.id || item.item_id;
            console.log(`Checking item: ${item.name} (ID: ${itemId})`);
            
            // Check if item ID looks like a valid database ID (small integer)
            // Large numbers like 1751552825116 are likely timestamps and invalid
            if (itemId && itemId < 1000000 && Number.isInteger(itemId)) {
                validItems.push(item);
                console.log(`✅ Valid item: ${item.name}`);
            } else {
                invalidItems.push(item);
                console.log(`❌ Invalid item: ${item.name} (ID: ${itemId})`);
            }
        });
        
        if (invalidItems.length > 0) {
            // Update localStorage with cleaned cart
            localStorage.setItem('restaurant_cart', JSON.stringify(validItems));
            console.log(`✅ Cleaned cart: removed ${invalidItems.length} invalid items`);
            
            // Try to update cart display if functions exist
            try {
                if (typeof updateCartDisplay === 'function') {
                    updateCartDisplay();
                }
                if (typeof updateCartCount === 'function') {
                    updateCartCount();
                }
            } catch (e) {
                console.log('Cart display functions not available');
            }
            
            return { cleaned: invalidItems.length, total: cart.length };
        } else {
            console.log('✅ Cart is clean - no invalid items found');
            return { cleaned: 0, total: cart.length };
        }
        
    } catch (error) {
        console.error('❌ Error cleaning cart data:', error);
        // If cart data is corrupted, clear it
        localStorage.removeItem('restaurant_cart');
        console.log('🗑️ Cleared corrupted cart data');
        return { cleaned: 'all', total: 0 };
    }
}

// Clear all cart data (nuclear option)
function clearAllCartData() {
    console.log('🗑️ Clearing all cart data...');
    localStorage.removeItem('restaurant_cart');
    sessionStorage.removeItem('restaurant_cart');
    
    // Try to clear any other cart-related storage
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
        if (key.includes('cart') || key.includes('order')) {
            localStorage.removeItem(key);
            console.log(`Removed: ${key}`);
        }
    });
    
    console.log('✅ All cart data cleared');
}

// Check cart integrity
function checkCartIntegrity() {
    console.log('🔍 Checking cart integrity...');
    const result = cleanupCartData();
    
    if (result.total === 0) {
        console.log('ℹ️ Cart is empty');
    } else if (result.cleaned === 0) {
        console.log(`✅ Cart is healthy (${result.total} items)`);
    } else {
        console.log(`⚠️ Cart had issues: cleaned ${result.cleaned} of ${result.total} items`);
    }
    
    return result;
}

// Auto-run on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkCartIntegrity);
} else {
    checkCartIntegrity();
}

// Make functions available globally
window.cleanupCart = cleanupCartData;
window.clearCart = clearAllCartData;
window.checkCart = checkCartIntegrity;

console.log('🛡️ Cart cleanup script loaded. Available commands:');
console.log('  - cleanupCart() - Remove invalid items');
console.log('  - clearCart() - Clear all cart data');
console.log('  - checkCart() - Check cart integrity');
'''
    
    return cleanup_script

def main():
    print("🚀 QUICK MENU ITEM ERROR FIX")
    print("=" * 40)
    
    # Create the cleanup script
    script_content = create_cart_cleanup_file()
    
    # Write to file
    with open('cart_cleanup.js', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ Created cart_cleanup.js")
    print("\nIMMEDIATE SOLUTION:")
    print("1. 🌐 Open your browser")
    print("2. 🔧 Open Developer Tools (F12)")
    print("3. 📋 Go to Console tab")
    print("4. 🧹 Run: clearCart()")
    print("5. 🔄 Refresh the page")
    
    print("\nOR use this one-liner in browser console:")
    print("localStorage.removeItem('restaurant_cart'); location.reload();")
    
    print("\nROOT CAUSE:")
    print("- Cart contains timestamp-based item ID: 1751552825116")
    print("- This is not a valid database menu item ID")
    print("- Clearing cart data should resolve the issue")
    
    print("\nLONG-TERM FIX:")
    print("- Add cart validation before order processing")
    print("- Handle missing menu items gracefully")
    print("- Auto-cleanup invalid cart items on app load")

if __name__ == "__main__":
    main()
