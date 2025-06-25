// Listen for real-time order status updates and update the UI accordingly
if (typeof socket !== 'undefined') {
    socket.on('order_status_updated', function(data) {
        // Show a notification
        RestaurantApp.showNotification('Order Status Updated', `Order #${data.order_id} status is now ${data.status}`, 'info');
        // Update order status in the UI (admin/waiter dashboards)
        RestaurantApp.updateOrderStatus(data.order_id, data.status);
    });
}
