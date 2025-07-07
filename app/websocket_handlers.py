from flask_socketio import emit, join_room, leave_room, rooms, disconnect
from flask_login import current_user
from flask import current_app
from app.extensions import socketio
from app.models import Order, User, ServiceRequest
from app.extensions import db
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Utility functions for real-time notifications
def notify_waiters(event_type, data):
    """Send notification to all connected waiters"""
    socketio.emit(event_type, data, room='waiter')
    socketio.emit(event_type, data, room='admin')  # Also notify admins

def notify_customer(user_id, event_type, data):
    """Send notification to specific customer"""
    socketio.emit(event_type, data, room=f'user_{user_id}')

def notify_all_staff(event_type, data):
    """Send notification to all staff (waiters and admins)"""
    socketio.emit(event_type, data, room='waiter')
    socketio.emit(event_type, data, room='admin')

@socketio.on('connect')
def handle_connect(auth=None):
    """Handle client connection"""
    if current_user.is_authenticated:
        logger.info(f"User {current_user.user_id} ({current_user.role}) connected")
        
        # Join user to their personal room
        join_room(f"user_{current_user.user_id}")
        
        # Join role-based rooms
        if current_user.is_admin():
            join_room("admin")
        elif current_user.is_waiter():
            join_room("waiter")
        elif current_user.is_customer():
            join_room("customer")
        
        emit('connection_status', {
            'status': 'connected',
            'user_id': current_user.user_id,
            'role': current_user.role,
            'message': 'Successfully connected to real-time updates'
        })
    else:
        logger.warning("Unauthenticated user attempted to connect")
        disconnect()

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    if current_user.is_authenticated:
        logger.info(f"User {current_user.user_id} ({current_user.role}) disconnected")

@socketio.on('join_order_room')
def handle_join_order_room(data):
    """Join room for specific order updates"""
    order_id = data.get('order_id')
    if not order_id:
        return
    
    # Verify user has permission to track this order
    order = Order.query.get(order_id)
    if not order:
        emit('error', {'message': 'Order not found'})
        return
    
    # Check permissions
    if (current_user.is_customer() and order.customer_id != current_user.user_id) and \
       not (current_user.is_admin() or current_user.is_waiter()):
        emit('error', {'message': 'Permission denied'})
        return
    
    join_room(f"order_{order_id}")
    emit('joined_order_room', {
        'order_id': order_id,
        'current_status': order.status,
        'message': f'Joined order {order_id} updates'
    })

@socketio.on('leave_order_room')
def handle_leave_order_room(data):
    """Leave room for specific order updates"""
    order_id = data.get('order_id')
    if order_id:
        leave_room(f"order_{order_id}")
        emit('left_order_room', {'order_id': order_id})

@socketio.on('join_table_room')
def handle_join_table_room(data):
    """Join room for specific table updates"""
    table_id = data.get('table_id')
    if not table_id:
        return
    
    # Only waiters and admins can join table rooms
    if not (current_user.is_admin() or current_user.is_waiter()):
        emit('error', {'message': 'Permission denied'})
        return
    
    join_room(f"table_{table_id}")
    emit('joined_table_room', {
        'table_id': table_id,
        'message': f'Joined table {table_id} updates'
    })

@socketio.on('update_order_status')
def handle_update_order_status(data):
    """Handle order status updates from staff"""
    if not (current_user.is_admin() or current_user.is_waiter()):
        emit('error', {'message': 'Permission denied'})
        return
    
    order_id = data.get('order_id')
    new_status = data.get('status')
    estimated_time = data.get('estimated_time')
    
    if not order_id or not new_status:
        emit('error', {'message': 'Missing required data'})
        return
    
    try:
        order = Order.query.get(order_id)
        if not order:
            emit('error', {'message': 'Order not found'})
            return
        
        # Update order status
        old_status = order.status
        order.status = new_status

        if estimated_time:
            order.estimated_delivery_time = estimated_time

        db.session.commit()

        # Award loyalty points when order is completed
        if new_status == 'completed' and old_status != 'completed':
            try:
                from app.modules.loyalty.loyalty_service import award_points_for_order
                current_app.logger.info(f"Attempting to award points for order {order_id} to user {order.user_id}")
                result = award_points_for_order(order_id, order.user_id)
                current_app.logger.info(f"Point awarding result for order {order_id}: {result}")
            except Exception as e:
                current_app.logger.error(f"Error awarding loyalty points for order {order_id}: {str(e)}")
                import traceback
                current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Broadcast update to all relevant rooms
        update_data = {
            'order_id': order_id,
            'old_status': old_status,
            'new_status': new_status,
            'estimated_time': estimated_time,
            'updated_by': current_user.name,
            'timestamp': order.updated_at.isoformat() if order.updated_at else None
        }
        
        # Notify customer
        socketio.emit('order_status_updated', update_data, 
                     room=f"user_{order.customer_id}")
        
        # Notify order room
        socketio.emit('order_status_updated', update_data, 
                     room=f"order_{order_id}")
        
        # Notify staff
        socketio.emit('order_status_updated', update_data, 
                     room="waiter")
        socketio.emit('order_status_updated', update_data, 
                     room="admin")
        
        emit('status_update_success', {
            'order_id': order_id,
            'new_status': new_status
        })
        
    except Exception as e:
        logger.error(f"Error updating order status: {str(e)}")
        db.session.rollback()
        emit('error', {'message': 'Failed to update order status'})

@socketio.on('service_request')
def handle_service_request(data):
    """Handle service requests from customers"""
    if not current_user.is_customer():
        emit('error', {'message': 'Only customers can make service requests'})
        return
    
    request_type = data.get('type')
    table_number = data.get('table_number')
    message = data.get('message', '')
    
    if not request_type:
        emit('error', {'message': 'Service request type is required'})
        return
    
    try:
        # Create service request
        service_request = ServiceRequest(
            customer_id=current_user.user_id,
            request_type=request_type,
            table_number=table_number,
            message=message,
            status='pending'
        )
        
        db.session.add(service_request)
        db.session.commit()
        
        # Broadcast to staff
        request_data = {
            'request_id': service_request.id,
            'customer_name': current_user.name,
            'customer_id': current_user.user_id,
            'type': request_type,
            'table_number': table_number,
            'message': message,
            'timestamp': service_request.created_at.isoformat(),
            'status': 'pending'
        }
        
        # Notify waiters and admins
        socketio.emit('new_service_request', request_data, room="waiter")
        socketio.emit('new_service_request', request_data, room="admin")
        
        # Notify specific table if applicable
        if table_number:
            socketio.emit('new_service_request', request_data, 
                         room=f"table_{table_number}")
        
        emit('service_request_sent', {
            'request_id': service_request.id,
            'message': 'Service request sent successfully'
        })
        
    except Exception as e:
        logger.error(f"Error creating service request: {str(e)}")
        db.session.rollback()
        emit('error', {'message': 'Failed to send service request'})

@socketio.on('update_service_request')
def handle_update_service_request(data):
    """Handle service request status updates from staff"""
    if not (current_user.is_admin() or current_user.is_waiter()):
        emit('error', {'message': 'Permission denied'})
        return
    
    request_id = data.get('request_id')
    new_status = data.get('status')
    
    if not request_id or not new_status:
        emit('error', {'message': 'Missing required data'})
        return
    
    try:
        service_request = ServiceRequest.query.get(request_id)
        if not service_request:
            emit('error', {'message': 'Service request not found'})
            return
        
        old_status = service_request.status
        service_request.status = new_status
        service_request.handled_by = current_user.user_id
        
        db.session.commit()
        
        # Broadcast update
        update_data = {
            'request_id': request_id,
            'old_status': old_status,
            'new_status': new_status,
            'handled_by': current_user.name,
            'timestamp': service_request.updated_at.isoformat()
        }
        
        # Notify customer
        socketio.emit('service_request_updated', update_data, 
                     room=f"user_{service_request.customer_id}")
        
        # Notify staff
        socketio.emit('service_request_updated', update_data, room="waiter")
        socketio.emit('service_request_updated', update_data, room="admin")
        
        emit('service_update_success', {
            'request_id': request_id,
            'new_status': new_status
        })
        
    except Exception as e:
        logger.error(f"Error updating service request: {str(e)}")
        db.session.rollback()
        emit('error', {'message': 'Failed to update service request'})

@socketio.on('payment_status_update')
def handle_payment_status_update(data):
    """Handle payment status updates"""
    if not (current_user.is_admin() or current_user.is_waiter()):
        emit('error', {'message': 'Permission denied'})
        return
    
    payment_id = data.get('payment_id')
    new_status = data.get('status')
    
    if not payment_id or not new_status:
        emit('error', {'message': 'Missing required data'})
        return
    
    try:
        from app.models import Payment
        payment = Payment.query.get(payment_id)
        if not payment:
            emit('error', {'message': 'Payment not found'})
            return
        
        old_status = payment.status
        payment.status = new_status
        
        db.session.commit()
        
        # Broadcast update
        update_data = {
            'payment_id': payment_id,
            'order_id': payment.order_id,
            'old_status': old_status,
            'new_status': new_status,
            'updated_by': current_user.name,
            'timestamp': payment.updated_at.isoformat()
        }
        
        # Notify customer
        socketio.emit('payment_status_updated', update_data, 
                     room=f"user_{payment.customer_id}")
        
        # Notify order room
        socketio.emit('payment_status_updated', update_data, 
                     room=f"order_{payment.order_id}")
        
        emit('payment_update_success', {
            'payment_id': payment_id,
            'new_status': new_status
        })
        
    except Exception as e:
        logger.error(f"Error updating payment status: {str(e)}")
        db.session.rollback()
        emit('error', {'message': 'Failed to update payment status'})

@socketio.on('get_real_time_stats')
def handle_get_real_time_stats():
    """Get real-time statistics (admin only)"""
    if not current_user.is_admin():
        emit('error', {'message': 'Permission denied'})
        return
    
    try:
        # Get current statistics
        total_orders = Order.query.count()
        pending_orders = Order.query.filter_by(status='pending').count()
        completed_orders = Order.query.filter_by(status='completed').count()
        total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter_by(status='completed').scalar() or 0
        
        pending_service_requests = ServiceRequest.query.filter_by(status='pending').count()
        
        stats = {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'total_revenue': float(total_revenue),
            'pending_service_requests': pending_service_requests,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        emit('real_time_stats', stats)
        
    except Exception as e:
        logger.error(f"Error getting real-time stats: {str(e)}")
        emit('error', {'message': 'Failed to get statistics'})

# Utility functions for broadcasting updates
def broadcast_order_update(order_id, status, estimated_time=None, updated_by=None):
    """Broadcast order status update to all relevant clients"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return
        
        update_data = {
            'order_id': order_id,
            'new_status': status,
            'estimated_time': estimated_time,
            'updated_by': updated_by or 'System',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Notify customer
        socketio.emit('order_status_updated', update_data, 
                     room=f"user_{order.customer_id}")
        
        # Notify order room
        socketio.emit('order_status_updated', update_data, 
                     room=f"order_{order_id}")
        
        # Notify staff
        socketio.emit('order_status_updated', update_data, room="waiter")
        socketio.emit('order_status_updated', update_data, room="admin")
        
    except Exception as e:
        logger.error(f"Error broadcasting order update: {str(e)}")

def broadcast_new_order(order_id):
    """Broadcast new order notification to staff"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return
        
        order_data = {
            'order_id': order_id,
            'customer_name': order.customer.name,
            'table_number': order.table_number,
            'total_amount': float(order.total_amount),
            'status': order.status,
            'timestamp': order.order_time.isoformat(),
            'item_count': len(order.order_items)
        }
        
        # Notify staff
        socketio.emit('new_order', order_data, room="waiter")
        socketio.emit('new_order', order_data, room="admin")
        
    except Exception as e:
        logger.error(f"Error broadcasting new order: {str(e)}")

def broadcast_payment_update(payment_id, status):
    """Broadcast payment status update"""
    try:
        from app.models import Payment
        payment = Payment.query.get(payment_id)
        if not payment:
            return
        
        update_data = {
            'payment_id': payment_id,
            'order_id': payment.order_id,
            'new_status': status,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Notify customer
        socketio.emit('payment_status_updated', update_data, 
                     room=f"user_{payment.customer_id}")
        
        # Notify order room
        socketio.emit('payment_status_updated', update_data, 
                     room=f"order_{payment.order_id}")
        
    except Exception as e:
        logger.error(f"Error broadcasting payment update: {str(e)}")

from datetime import datetime
