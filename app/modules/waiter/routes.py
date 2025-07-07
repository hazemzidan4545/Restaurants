from flask import render_template, redirect, url_for, request, jsonify, flash
from flask_login import login_required, current_user
from app.modules.waiter import bp
from app.models import Order, OrderItem, Table, ServiceRequest, User, db
from app.extensions import socketio
from datetime import datetime
from sqlalchemy.orm import joinedload

@bp.route('/dashboard')
@login_required
def dashboard():
    """Waiter dashboard with real order data"""
    if not current_user.is_waiter():
        return redirect(url_for('main.index'))

    # Get orders with status filtering
    status_filter = request.args.get('status', 'active')

    # Base query with eager loading to avoid N+1 queries
    orders_query = Order.query.options(
        joinedload(Order.customer),
        joinedload(Order.table),
        joinedload(Order.order_items).joinedload(OrderItem.menu_item)
    )

    # Apply status filtering
    if status_filter == 'active':
        orders = orders_query.filter(Order.status.in_(['new', 'processing'])).order_by(Order.order_time.desc()).all()
    elif status_filter == 'all':
        orders = orders_query.order_by(Order.order_time.desc()).limit(50).all()
    else:
        orders = orders_query.filter_by(status=status_filter).order_by(Order.order_time.desc()).limit(20).all()

    # Get order counts by status for filter buttons
    order_counts = {
        'new': Order.query.filter_by(status='new').count(),
        'processing': Order.query.filter_by(status='processing').count(),
        'completed': Order.query.filter_by(status='completed').count(),
        'rejected': Order.query.filter_by(status='rejected').count()
    }

    # Get table information
    tables = Table.query.all()

    # Get pending service requests
    service_requests = ServiceRequest.query.filter_by(status='pending').order_by(ServiceRequest.created_at.desc()).limit(10).all()

    return render_template('waiter_dashboard.html',
                         orders=orders,
                         order_counts=order_counts,
                         tables=tables,
                         service_requests=service_requests,
                         current_filter=status_filter,
                         now=datetime.utcnow())

@bp.route('/update_order_status', methods=['POST'])
@login_required
def update_order_status():
    """Update order status"""
    if not current_user.is_waiter():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    try:
        data = request.get_json()
        order_id = data.get('order_id')
        new_status = data.get('status')

        if not order_id or not new_status:
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400

        # Validate status
        valid_statuses = ['new', 'processing', 'completed', 'rejected']
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'message': 'Invalid status'}), 400

        # Get and update order
        order = Order.query.get_or_404(order_id)
        old_status = order.status
        order.status = new_status
        order.updated_at = datetime.utcnow()

        # If order is completed, update table status
        if new_status == 'completed' and order.table:
            order.table.status = 'available'

        db.session.commit()

        # Emit real-time update to all connected clients
        socketio.emit('order_status_updated', {
            'order_id': order_id,
            'old_status': old_status,
            'new_status': new_status,
            'table_number': order.table.table_number if order.table else None,
            'customer_name': order.customer.name if order.customer else 'Unknown',
            'updated_by': current_user.name
        }, room='admin')

        # Notify customer
        if order.customer:
            socketio.emit('order_update', {
                'order_id': order_id,
                'status': new_status,
                'message': f'Your order status has been updated to {new_status}'
            }, room=f'user_{order.customer.user_id}')

        return jsonify({
            'success': True,
            'message': f'Order #{order_id} status updated to {new_status}',
            'new_status': new_status
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/service_requests')
@login_required
def service_requests():
    """View and manage service requests"""
    if not current_user.is_waiter():
        return redirect(url_for('main.index'))

    # Get service requests with filtering
    status_filter = request.args.get('status', 'pending')

    query = ServiceRequest.query.options(
        joinedload(ServiceRequest.customer),
        joinedload(ServiceRequest.table)
    )

    if status_filter == 'all':
        requests = query.order_by(ServiceRequest.created_at.desc()).limit(50).all()
    else:
        requests = query.filter_by(status=status_filter).order_by(ServiceRequest.created_at.desc()).all()

    # Get request counts by status
    request_counts = {
        'pending': ServiceRequest.query.filter_by(status='pending').count(),
        'acknowledged': ServiceRequest.query.filter_by(status='acknowledged').count(),
        'completed': ServiceRequest.query.filter_by(status='completed').count()
    }

    return render_template('service_requests.html',
                         requests=requests,
                         request_counts=request_counts,
                         current_filter=status_filter)

@bp.route('/update_service_request', methods=['POST'])
@login_required
def update_service_request():
    """Update service request status"""
    if not current_user.is_waiter():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    try:
        data = request.get_json()
        request_id = data.get('request_id')
        new_status = data.get('status')

        if not request_id or not new_status:
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400

        # Validate status
        valid_statuses = ['pending', 'acknowledged', 'completed']
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'message': 'Invalid status'}), 400

        # Get and update service request
        service_request = ServiceRequest.query.get_or_404(request_id)
        old_status = service_request.status
        service_request.status = new_status
        service_request.updated_at = datetime.utcnow()

        # Set waiter who handled the request
        if new_status in ['acknowledged', 'completed']:
            service_request.handled_by = current_user.user_id

        db.session.commit()

        # Emit real-time update
        socketio.emit('service_request_updated', {
            'request_id': request_id,
            'old_status': old_status,
            'new_status': new_status,
            'table_number': service_request.table.table_number if service_request.table else None,
            'handled_by': current_user.name
        }, room='waiter')

        # Notify customer
        if service_request.customer:
            socketio.emit('service_update', {
                'request_id': request_id,
                'status': new_status,
                'message': f'Your service request has been {new_status}'
            }, room=f'user_{service_request.customer.user_id}')

        return jsonify({
            'success': True,
            'message': f'Service request #{request_id} marked as {new_status}',
            'new_status': new_status
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/tables')
@login_required
def table_management():
    """Table management interface"""
    if not current_user.is_waiter():
        return redirect(url_for('main.index'))

    # Get all tables with their current status and active orders
    tables = Table.query.options(
        joinedload(Table.orders.and_(Order.status.in_(['new', 'processing'])))
    ).all()

    # Get table statistics
    table_stats = {
        'total': Table.query.count(),
        'available': Table.query.filter_by(status='available').count(),
        'occupied': Table.query.filter_by(status='occupied').count(),
        'reserved': Table.query.filter_by(status='reserved').count()
    }

    return render_template('table_management.html',
                         tables=tables,
                         table_stats=table_stats)

@bp.route('/update_table_status', methods=['POST'])
@login_required
def update_table_status():
    """Update table status"""
    if not current_user.is_waiter():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    try:
        data = request.get_json()
        table_id = data.get('table_id')
        new_status = data.get('status')

        if not table_id or not new_status:
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400

        # Validate status
        valid_statuses = ['available', 'occupied', 'reserved']
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'message': 'Invalid status'}), 400

        # Get and update table
        table = Table.query.get_or_404(table_id)
        old_status = table.status
        table.status = new_status

        db.session.commit()

        # Emit real-time update
        socketio.emit('table_status_updated', {
            'table_id': table_id,
            'table_number': table.table_number,
            'old_status': old_status,
            'new_status': new_status,
            'updated_by': current_user.name
        }, room='admin')

        return jsonify({
            'success': True,
            'message': f'Table {table.table_number} status updated to {new_status}',
            'new_status': new_status
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
