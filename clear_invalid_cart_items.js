/**
 * Cart Cleanup Script
 * This script clears any invalid cart items with timestamp-based IDs
 * Run this in the browser console to clean up the cart
 */

console.log('🧹 Starting cart cleanup...');

// Check if cart exists in localStorage
const cartKey = 'restaurant_cart';
const savedCart = localStorage.getItem(cartKey);

if (!savedCart) {
    console.log('✅ No cart found in localStorage');
} else {
    try {
        const cartData = JSON.parse(savedCart);
        console.log(`📋 Found ${cartData.length} items in cart`);
        
        // Filter out invalid items (those with timestamp IDs)
        const validItems = cartData.filter(item => {
            const itemId = parseInt(item.id);
            const isValid = !isNaN(itemId) && itemId < 1000000;
            
            if (!isValid) {
                console.log(`❌ Removing invalid item: ${item.name} (ID: ${item.id})`);
            } else {
                console.log(`✅ Keeping valid item: ${item.name} (ID: ${item.id})`);
            }
            
            return isValid;
        });
        
        if (validItems.length !== cartData.length) {
            console.log(`🔧 Cleaned cart: removed ${cartData.length - validItems.length} invalid items`);
            
            // Save cleaned cart back to localStorage
            localStorage.setItem(cartKey, JSON.stringify(validItems));
            console.log('💾 Updated cart saved to localStorage');
            
            // If cart system is loaded, update it
            if (typeof updateCartDisplay === 'function') {
                if (typeof unifiedCart !== 'undefined') {
                    unifiedCart = validItems;
                }
                updateCartDisplay();
                updateCartCount();
                console.log('🔄 Updated cart display');
            }
            
            console.log('✨ Cart cleanup completed successfully!');
            console.log('🔄 Please refresh the page to ensure all changes take effect.');
        } else {
            console.log('✅ Cart is already clean - no invalid items found');
        }
        
    } catch (error) {
        console.error('❌ Error parsing cart data:', error);
        console.log('🗑️ Clearing corrupted cart data...');
        localStorage.removeItem(cartKey);
        console.log('✅ Corrupted cart data cleared');
    }
}

console.log('🏁 Cart cleanup script finished');
