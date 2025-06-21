// Restaurant Management System - Main JavaScript

// Initialize Socket.IO connection
let socket;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Socket.IO if available
    if (typeof io !== 'undefined') {
        socket = io();
        
        // Handle connection events
        socket.on('connect', function() {
            console.log('Connected to server');
        });
        
        socket.on('disconnect', function() {
            console.log('Disconnected from server');
        });
        
        // Handle order updates
        socket.on('order_update', function(data) {
            showNotification('Order Update', data.message, 'info');
            updateOrderStatus(data.order_id, data.status);
        });
        
        // Handle service request updates
        socket.on('service_request_update', function(data) {
            showNotification('Service Request', data.message, 'info');
        });
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

// Utility Functions
function showNotification(title, message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    notification.innerHTML = `
        <strong>${title}:</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(function() {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

function updateOrderStatus(orderId, status) {
    const statusElement = document.querySelector(`[data-order-id="${orderId}"] .order-status`);
    if (statusElement) {
        statusElement.textContent = status;
        statusElement.className = `status-badge status-${status.toLowerCase()}`;
    }
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-EG', {
        style: 'currency',
        currency: 'EGP'
    }).format(amount);
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-EG', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Loading spinner functions
function showLoading(element) {
    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    spinner.id = 'loading-spinner';
    
    if (typeof element === 'string') {
        element = document.querySelector(element);
    }
    
    if (element) {
        element.appendChild(spinner);
    }
}

function hideLoading() {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.remove();
    }
}

// AJAX helper functions
function makeRequest(url, method = 'GET', data = null) {
    return fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: data ? JSON.stringify(data) : null
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    });
}

function getCSRFToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    return token ? token.getAttribute('content') : '';
}

// Form validation helpers
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const re = /^[\+]?[1-9][\d]{0,15}$/;
    return re.test(phone);
}

// Menu item functions - moved to cart.js for unified cart system

// Service request functions
function submitServiceRequest(type, message = '') {
    const data = {
        request_type: type,
        message: message
    };
    
    makeRequest('/api/service-requests', 'POST', data)
        .then(response => {
            if (response.success) {
                showNotification('Success', 'Service request submitted', 'success');
            } else {
                showNotification('Error', response.message, 'danger');
            }
        })
        .catch(error => {
            console.error('Error submitting service request:', error);
            showNotification('Error', 'Failed to submit service request', 'danger');
        });
}

// Export functions for global use
window.RestaurantApp = {
    showNotification,
    updateOrderStatus,
    formatCurrency,
    formatDateTime,
    showLoading,
    hideLoading,
    makeRequest,
    addToCart,
    submitServiceRequest
};
