/**
 * Real-time WebSocket Client for Restaurant Management System
 * Handles order updates, service requests, and notifications
 */

class RestaurantWebSocketClient {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.callbacks = {
            orderStatusUpdated: [],
            newOrder: [],
            serviceRequestUpdated: [],
            newServiceRequest: [],
            paymentStatusUpdated: [],
            realTimeStats: [],
            connectionStatus: []
        };
        
        this.init();
    }

    init() {
        try {
            this.socket = io({
                transports: ['websocket', 'polling'],
                upgrade: true,
                rememberUpgrade: true
            });
            
            this.setupEventListeners();
            this.setupConnectionHandlers();
        } catch (error) {
            console.error('Failed to initialize WebSocket connection:', error);
        }
    }

    setupConnectionHandlers() {
        this.socket.on('connect', () => {
            console.log('Connected to real-time server');
            this.isConnected = true;
            const hadConnectionIssues = this.reconnectAttempts > 0;
            this.reconnectAttempts = 0;
            
            // Only show status in status element, not as notification
            this.showConnectionStatus('Connected', 'success');
            this.triggerCallbacks('connectionStatus', { status: 'connected' });
            
            // Clear any previous connection error notifications
            this.clearConnectionErrorNotifications();
            
            // Only show reconnection success if there were previous issues
            if (hadConnectionIssues) {
                this.showNotification('Real-time updates restored', 'success');
            }
            
            // Never show "connected" notification on initial connection
            // Notifications are only for problems or successful reconnections
        });

        this.socket.on('disconnect', (reason) => {
            console.log('Disconnected from server:', reason);
            this.isConnected = false;
            this.showConnectionStatus('Disconnected', 'warning');
            this.triggerCallbacks('connectionStatus', { status: 'disconnected', reason });
            
            // Only show notification for unexpected disconnections, not normal page navigation
            if (reason !== 'io client disconnect' && reason !== 'transport close') {
                this.showNotification('Connection lost - attempting to reconnect...', 'warning');
            }
            
            if (reason === 'io server disconnect') {
                // Server initiated disconnect, try to reconnect
                this.attemptReconnect();
            }
        });

        this.socket.on('connect_error', (error) => {
            console.error('Connection error:', error);
            this.showConnectionStatus('Connection Error', 'error');
            this.showNotification('Real-time updates connection failed - retrying...', 'error');
            this.attemptReconnect();
        });

        this.socket.on('connection_status', (data) => {
            console.log('Connection status:', data);
            // Remove the automatic "connected" notification
            // Only log to console for debugging
        });
    }

    setupEventListeners() {
        // Order status updates
        this.socket.on('order_status_updated', (data) => {
            console.log('Order status updated:', data);
            this.handleOrderStatusUpdate(data);
            this.triggerCallbacks('orderStatusUpdated', data);
        });

        // New order notifications (for staff)
        this.socket.on('new_order', (data) => {
            console.log('New order received:', data);
            this.handleNewOrder(data);
            this.triggerCallbacks('newOrder', data);
        });

        // Service request updates
        this.socket.on('service_request_updated', (data) => {
            console.log('Service request updated:', data);
            this.handleServiceRequestUpdate(data);
            this.triggerCallbacks('serviceRequestUpdated', data);
        });

        // New service requests (for staff)
        this.socket.on('new_service_request', (data) => {
            console.log('New service request:', data);
            this.handleNewServiceRequest(data);
            this.triggerCallbacks('newServiceRequest', data);
        });

        // Payment status updates
        this.socket.on('payment_status_updated', (data) => {
            console.log('Payment status updated:', data);
            this.handlePaymentStatusUpdate(data);
            this.triggerCallbacks('paymentStatusUpdated', data);
        });

        // Real-time statistics (admin)
        this.socket.on('real_time_stats', (data) => {
            console.log('Real-time stats:', data);
            this.updateDashboardStats(data);
            this.triggerCallbacks('realTimeStats', data);
        });

        // Error handling
        this.socket.on('error', (data) => {
            console.error('WebSocket error:', data.message);
            this.showNotification(data.message, 'error');
        });
    }

    // Connection management
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
            
            console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
            this.showConnectionStatus(`Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`, 'info');
            
            // Only show notification if this is not the first reconnect attempt
            if (this.reconnectAttempts > 1) {
                this.showNotification(`Reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`, 'info');
            }
            
            setTimeout(() => {
                this.socket.connect();
            }, delay);
        } else {
            console.error('Max reconnection attempts reached');
            this.showConnectionStatus('Connection Failed', 'error');
            this.showNotification('Real-time updates unavailable - please refresh the page', 'error');
        }
    }

    // Room management
    joinOrderRoom(orderId) {
        if (this.isConnected) {
            this.socket.emit('join_order_room', { order_id: orderId });
        }
    }

    leaveOrderRoom(orderId) {
        if (this.isConnected) {
            this.socket.emit('leave_order_room', { order_id: orderId });
        }
    }

    joinTableRoom(tableId) {
        if (this.isConnected) {
            this.socket.emit('join_table_room', { table_id: tableId });
        }
    }

    // Order management
    updateOrderStatus(orderId, status, estimatedTime = null) {
        if (this.isConnected) {
            this.socket.emit('update_order_status', {
                order_id: orderId,
                status: status,
                estimated_time: estimatedTime
            });
        }
    }

    handleOrderStatusUpdate(data) {
        // Update order status in UI
        const orderElements = document.querySelectorAll(`[data-order-id="${data.order_id}"]`);
        orderElements.forEach(element => {
            const statusElement = element.querySelector('.order-status');
            if (statusElement) {
                statusElement.textContent = data.new_status.charAt(0).toUpperCase() + data.new_status.slice(1);
                statusElement.className = `order-status status-${data.new_status}`;
            }
        });

        // Show notification
        this.showNotification(`Order #${data.order_id} is now ${data.new_status}`, 'info');

        // Update progress bars if they exist
        this.updateOrderProgress(data.order_id, data.new_status);
    }

    handleNewOrder(data) {
        // Add new order to staff dashboards
        this.addOrderToQueue(data);
        
        // Show notification for staff
        this.showNotification(`New order #${data.order_id} from ${data.customer_name}`, 'success');
        
        // Play notification sound
        this.playNotificationSound();
    }

    // Service request management
    sendServiceRequest(type, tableNumber = null, message = '') {
        if (this.isConnected) {
            this.socket.emit('service_request', {
                type: type,
                table_number: tableNumber,
                message: message
            });
        }
    }

    updateServiceRequestStatus(requestId, status) {
        if (this.isConnected) {
            this.socket.emit('update_service_request', {
                request_id: requestId,
                status: status
            });
        }
    }

    handleServiceRequestUpdate(data) {
        // Update service request status in UI
        const requestElements = document.querySelectorAll(`[data-request-id="${data.request_id}"]`);
        requestElements.forEach(element => {
            const statusElement = element.querySelector('.request-status');
            if (statusElement) {
                statusElement.textContent = data.new_status.charAt(0).toUpperCase() + data.new_status.slice(1);
                statusElement.className = `request-status status-${data.new_status}`;
            }
        });

        // Show notification
        this.showNotification(`Service request #${data.request_id} is now ${data.new_status}`, 'info');
    }

    handleNewServiceRequest(data) {
        // Add new service request to staff interface
        this.addServiceRequestToQueue(data);
        
        // Show notification for staff
        this.showNotification(`New service request: ${data.type} (Table ${data.table_number || 'N/A'})`, 'warning');
        
        // Play notification sound
        this.playNotificationSound();
    }

    // Payment management
    handlePaymentStatusUpdate(data) {
        // Update payment status in UI
        const paymentElements = document.querySelectorAll(`[data-payment-id="${data.payment_id}"]`);
        paymentElements.forEach(element => {
            const statusElement = element.querySelector('.payment-status');
            if (statusElement) {
                statusElement.textContent = data.new_status.charAt(0).toUpperCase() + data.new_status.slice(1);
                statusElement.className = `payment-status status-${data.new_status}`;
            }
        });

        // Show notification
        this.showNotification(`Payment #${data.payment_id} is now ${data.new_status}`, 'info');
    }

    // Statistics updates (admin)
    getRealTimeStats() {
        if (this.isConnected) {
            this.socket.emit('get_real_time_stats');
        }
    }

    updateDashboardStats(data) {
        // Update statistics cards
        const statsElements = {
            'total-orders': data.total_orders,
            'pending-orders': data.pending_orders,
            'completed-orders': data.completed_orders,
            'total-revenue': `$${data.total_revenue.toFixed(2)}`,
            'pending-service-requests': data.pending_service_requests
        };

        Object.entries(statsElements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    // UI Helper Methods
    showConnectionStatus(message, type) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `connection-status ${type}`;
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close">&times;</button>
            </div>
        `;

        // Add to notification container
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            document.body.appendChild(container);
        }

        container.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);

        // Add close button functionality
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        });
    }

    updateOrderProgress(orderId, status) {
        const progressElement = document.querySelector(`[data-order-id="${orderId}"] .order-progress`);
        if (!progressElement) return;

        const statusSteps = {
            'new': 1,
            'confirmed': 2,
            'preparing': 3,
            'ready': 4,
            'delivered': 5,
            'completed': 5
        };

        const progress = (statusSteps[status] || 1) * 20;
        const progressBar = progressElement.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
    }

    addOrderToQueue(orderData) {
        const queueContainer = document.getElementById('order-queue');
        if (!queueContainer) return;

        const orderElement = document.createElement('div');
        orderElement.className = 'order-card new-order';
        orderElement.setAttribute('data-order-id', orderData.order_id);
        orderElement.innerHTML = `
            <div class="order-header">
                <span class="order-number">#${orderData.order_id}</span>
                <span class="order-status status-${orderData.status}">${orderData.status.charAt(0).toUpperCase() + orderData.status.slice(1)}</span>
            </div>
            <div class="order-details">
                <p><strong>Customer:</strong> ${orderData.customer_name}</p>
                <p><strong>Table:</strong> ${orderData.table_number || 'Takeaway'}</p>
                <p><strong>Total:</strong> $${orderData.total_amount.toFixed(2)}</p>
                <p><strong>Items:</strong> ${orderData.item_count}</p>
            </div>
            <div class="order-actions">
                <button class="btn btn-sm btn-primary" onclick="viewOrderDetails(${orderData.order_id})">View Details</button>
                <button class="btn btn-sm btn-success" onclick="updateOrderStatus(${orderData.order_id}, 'confirmed')">Confirm</button>
            </div>
        `;

        queueContainer.insertBefore(orderElement, queueContainer.firstChild);

        // Highlight the new order
        setTimeout(() => {
            orderElement.classList.remove('new-order');
        }, 3000);
    }

    addServiceRequestToQueue(requestData) {
        const queueContainer = document.getElementById('service-request-queue');
        if (!queueContainer) return;

        const requestElement = document.createElement('div');
        requestElement.className = 'service-request-card new-request';
        requestElement.setAttribute('data-request-id', requestData.request_id);
        requestElement.innerHTML = `
            <div class="request-header">
                <span class="request-type">${requestData.type}</span>
                <span class="request-status status-${requestData.status}">${requestData.status.charAt(0).toUpperCase() + requestData.status.slice(1)}</span>
            </div>
            <div class="request-details">
                <p><strong>Customer:</strong> ${requestData.customer_name}</p>
                <p><strong>Table:</strong> ${requestData.table_number || 'N/A'}</p>
                ${requestData.message ? `<p><strong>Message:</strong> ${requestData.message}</p>` : ''}
            </div>
            <div class="request-actions">
                <button class="btn btn-sm btn-warning" onclick="updateServiceRequestStatus(${requestData.request_id}, 'in_progress')">Accept</button>
                <button class="btn btn-sm btn-success" onclick="updateServiceRequestStatus(${requestData.request_id}, 'completed')">Complete</button>
            </div>
        `;

        queueContainer.insertBefore(requestElement, queueContainer.firstChild);

        // Highlight the new request
        setTimeout(() => {
            requestElement.classList.remove('new-request');
        }, 3000);
    }

    playNotificationSound() {
        try {
            const audio = new Audio('/static/sounds/notification.mp3');
            audio.volume = 0.3;
            audio.play().catch(e => console.log('Could not play notification sound:', e));
        } catch (e) {
            console.log('Notification sound not available');
        }
    }

    // Callback system for external integrations
    on(event, callback) {
        if (this.callbacks[event]) {
            this.callbacks[event].push(callback);
        }
    }

    off(event, callback) {
        if (this.callbacks[event]) {
            const index = this.callbacks[event].indexOf(callback);
            if (index > -1) {
                this.callbacks[event].splice(index, 1);
            }
        }
    }

    triggerCallbacks(event, data) {
        if (this.callbacks[event]) {
            this.callbacks[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in ${event} callback:`, error);
                }
            });
        }
    }

    // Cleanup
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
    }

    clearConnectionErrorNotifications() {
        // Remove any existing connection-related notifications
        const container = document.getElementById('notification-container');
        if (container) {
            const notifications = container.querySelectorAll('.notification');
            notifications.forEach(notification => {
                const message = notification.querySelector('.notification-message').textContent.toLowerCase();
                // Remove all connection-related notifications
                if (message.includes('connection') || message.includes('real-time') || 
                    message.includes('reconnection') || message.includes('reconnecting') ||
                    message.includes('connected') || message.includes('disconnected') ||
                    message.includes('failed') || message.includes('restored') ||
                    message.includes('unavailable')) {
                    notification.remove();
                }
            });
        }
    }
}

// Global WebSocket client instance
let restaurantWS = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if user is authenticated
    if (document.body.classList.contains('authenticated')) {
        restaurantWS = new RestaurantWebSocketClient();
        
        // Make it globally available
        window.restaurantWS = restaurantWS;
        
        console.log('Restaurant WebSocket client initialized');
    }
});

// Expose global functions for inline event handlers
window.updateOrderStatus = function(orderId, status) {
    if (restaurantWS) {
        restaurantWS.updateOrderStatus(orderId, status);
    }
};

window.updateServiceRequestStatus = function(requestId, status) {
    if (restaurantWS) {
        restaurantWS.updateServiceRequestStatus(requestId, status);
    }
};

window.sendServiceRequest = function(type, tableNumber, message) {
    if (restaurantWS) {
        restaurantWS.sendServiceRequest(type, tableNumber, message);
    }
};

// CSS for notifications and real-time features
const realTimeCSS = `
.notification-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 10000;
    max-width: 400px;
}

.notification {
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    margin-bottom: 10px;
    animation: slideInRight 0.3s ease;
}

.notification-success { border-left: 4px solid #28a745; }
.notification-info { border-left: 4px solid #17a2b8; }
.notification-warning { border-left: 4px solid #ffc107; }
.notification-error { border-left: 4px solid #dc3545; }

.notification-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px;
}

.notification-message {
    flex: 1;
    font-size: 14px;
    color: #333;
}

.notification-close {
    background: none;
    border: none;
    font-size: 18px;
    color: #999;
    cursor: pointer;
    padding: 0;
    margin-left: 10px;
}

.notification-close:hover {
    color: #333;
}

@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.connection-status {
    position: fixed;
    bottom: 20px;
    left: 20px;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    z-index: 9999;
}

.connection-status.success {
    background: #28a745;
    color: white;
}

.connection-status.warning {
    background: #ffc107;
    color: #333;
}

.connection-status.error {
    background: #dc3545;
    color: white;
}

.connection-status.info {
    background: #17a2b8;
    color: white;
}

.new-order, .new-request {
    animation: highlightNew 3s ease;
}

@keyframes highlightNew {
    0% { background-color: #fff3cd; }
    100% { background-color: transparent; }
}

.order-progress {
    height: 4px;
    background: #e9ecef;
    border-radius: 2px;
    overflow: hidden;
    margin-top: 10px;
}

.order-progress .progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #f3cd21, #1c1d1f);
    transition: width 0.5s ease;
}
`;

// Inject CSS
const style = document.createElement('style');
style.textContent = realTimeCSS;
document.head.appendChild(style);
