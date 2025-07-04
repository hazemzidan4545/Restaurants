from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.extensions import db, socketio, csrf
from app.models import Order, OrderItem, MenuItem, Table, User
from sqlalchemy.orm import joinedload
from datetime import datetime

bp = Blueprint('order_api', __name__, url_prefix='/api/order')

# Exempt these routes from CSRF protection as we'll handle it on the frontend
@bp.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-CSRFToken'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    return response

@bp.route('/test', methods=['GET'])
def test_api():
    """Test endpoint to verify API is functioning"""
    return jsonify({
        'status': 'success',
        'message': 'Order API is working correctly',
        'timestamp': datetime.utcnow().isoformat()
    })

@bp.route('/', methods=['POST'])
@login_required
def create_order():
    data = request.get_json()
    table_id = data.get('table_id')
    items = data.get('items', [])  # [{item_id, quantity, note}]
    notes = data.get('notes', '')

    if not items:
        return jsonify({'error': 'No items provided'}), 400

    order = Order(user_id=current_user.user_id, table_id=table_id, notes=notes)
    db.session.add(order)
    db.session.flush()  # Get order_id

    total = 0
    for item in items:
        try:
            item_id = item.get('item_id')
            if not item_id:
                db.session.rollback()
                return jsonify({'error': 'Item ID is required'}), 400
            
            # Validate that item_id is a reasonable database ID (not a timestamp)
            if not isinstance(item_id, int) or item_id > 1000000:
                db.session.rollback()
                return jsonify({'error': f'Menu item {item_id} not found'}), 400
            
            menu_item = MenuItem.query.get(item_id)
            if not menu_item:
                db.session.rollback()
                return jsonify({'error': f'Menu item {item_id} not found'}), 400
            
            if menu_item.status != 'available':
                db.session.rollback()
                return jsonify({'error': f'Menu item {menu_item.name} is not available'}), 400
                
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error processing item {item.get('item_id', 'unknown')}: {str(e)}")
            return jsonify({'error': f'Menu item {item.get("item_id", "unknown")} not found'}), 400
        
        order_item = OrderItem(
            order_id=order.order_id,
            item_id=menu_item.item_id,
            quantity=item.get('quantity', 1),
            note=item.get('note', ''),
            unit_price=menu_item.price
        )
        db.session.add(order_item)
        total += menu_item.price * order_item.quantity
    order.total_amount = total
    db.session.commit()
    return jsonify({'order_id': order.order_id, 'status': order.status, 'total': float(order.total_amount)}), 201

@bp.route('/<int:order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    try:
        # Log debug information
        print(f"GET /api/order/{order_id} - User: {current_user.user_id}, Role: {current_user.role}")
          # Query order first
        order = Order.query.filter_by(order_id=order_id).first()
        
        # Then manually query the order items with their menu items
        if order:
            # Convert order_items from dynamic query to list
            order_items = list(order.order_items)
            
            # Pre-load menu items to avoid N+1 query problem
            item_ids = [item.item_id for item in order_items]
            menu_items = {item.item_id: item for item in MenuItem.query.filter(MenuItem.item_id.in_(item_ids)).all()}
        
        # Check if order exists
        if not order:
            print(f"Order {order_id} not found")
            return jsonify({'error': f'Order {order_id} not found'}), 404
        
        # Check authorization
        if current_user.role != 'admin' and order.user_id != current_user.user_id:
            print(f"User {current_user.user_id} not authorized to view order {order_id}")
            return jsonify({'error': 'Unauthorized'}), 403        # Format response data
        items = []
        for oi in order_items:
            try:
                # Use our preloaded menu items dictionary
                menu_item = menu_items.get(oi.item_id)
                item_name = menu_item.name if menu_item else f"Unknown Item ({oi.item_id})"
                
                items.append({
                    'item_id': oi.item_id,
                    'name': item_name,
                    'quantity': oi.quantity,
                    'note': oi.note,
                    'unit_price': float(oi.unit_price)
                })
            except Exception as e:
                print(f"Error processing order item {oi.order_item_id}: {str(e)}")
                items.append({
                    'item_id': oi.item_id,
                    'name': f"Error loading item ({oi.item_id})",
                    'quantity': oi.quantity,
                    'note': oi.note,
                    'unit_price': float(oi.unit_price)
                })
        
        response_data = {
            'order_id': order.order_id,
            'status': order.status,
            'total': float(order.total_amount),
            'items': items,
            'notes': order.notes,
            'table_id': order.table_id,
            'order_time': order.order_time.isoformat()
        }
        
        print(f"Returning order data for {order_id}")
        return jsonify(response_data)
    except Exception as e:
        print(f"Error retrieving order {order_id}: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@bp.route('/history', methods=['GET'])
@login_required
def order_history():
    orders = Order.query.filter_by(user_id=current_user.user_id).order_by(Order.order_time.desc()).all()
    return jsonify([
        {
            'order_id': o.order_id,
            'status': o.status,
            'total': float(o.total_amount),
            'order_time': o.order_time.isoformat()
        } for o in orders
    ])

@bp.route('/<int:order_id>/status', methods=['PATCH'])
@login_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    if current_user.role not in ['admin', 'waiter']:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    new_status = data.get('status')
    if new_status not in ['new', 'processing', 'completed', 'rejected', 'cancelled']:
        return jsonify({'error': 'Invalid status'}), 400
    
    old_status = order.status
    order.status = new_status
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
    
    # Emit real-time update event
    socketio.emit('order_status_updated', {
        'order_id': order.order_id,
        'status': order.status,
        'user_id': order.user_id,
        'table_id': order.table_id
    })
    return jsonify({'order_id': order.order_id, 'status': order.status})

@bp.route('/all', methods=['GET'])
@login_required
def get_all_orders():
    if current_user.role not in ['admin', 'waiter']:
        return jsonify({'error': 'Unauthorized'}), 403
    orders = Order.query.order_by(Order.order_time.desc()).all()
    return jsonify([
        {
            'order_id': o.order_id,
            'user_id': o.user_id,
            'table_id': o.table_id,
            'status': o.status,
            'total': float(o.total_amount),
            'order_time': o.order_time.isoformat()
        } for o in orders
    ])

@bp.route('/<int:order_id>', methods=['PUT'])
@login_required
def edit_order(order_id):
    try:
        # Log debug information
        print(f"PUT /api/order/{order_id} - User: {current_user.user_id}, Role: {current_user.role}")
        
        # Get request data
        data = request.get_json()
        if not data:
            print(f"No JSON data in request body for order {order_id}")
            return jsonify({'error': 'No JSON data provided'}), 400
            
        # Get order
        order = Order.query.get_or_404(order_id)
        print(f"Found order {order_id} with status: {order.status}")
        
        # Check authorization
        if current_user.role not in ['admin', 'waiter']:
            print(f"User {current_user.user_id} not authorized to edit order {order_id}")
            return jsonify({'error': 'Unauthorized'}), 403
          # Allow editing items, notes, and status
        items = data.get('items')
        notes = data.get('notes')
        status = data.get('status')          # Update status if provided
        if status is not None and status in ['new', 'processing', 'completed', 'rejected', 'cancelled']:
            order.status = status
            print(f"Updated status for order {order_id} to: {status}")
        
        if items is not None:
            print(f"Updating {len(items)} items for order {order_id}")
            # Remove existing items (preserve in transaction)
            OrderItem.query.filter_by(order_id=order.order_id).delete()
            
            # Add new items
            total = 0
            for item in items:
                item_id = item.get('item_id')
                if not item_id:
                    print(f"Item missing item_id in request for order {order_id}")
                    return jsonify({'error': 'Item missing item_id'}), 400
                    
                menu_item = MenuItem.query.get(item_id)
                if not menu_item:
                    print(f"Item {item_id} not found for order {order_id}")
                    return jsonify({'error': f"Item {item_id} not found"}), 400
                    
                if menu_item.status != 'available':
                    print(f"Item {item_id} unavailable for order {order_id}")
                    return jsonify({'error': f"Item {item_id} unavailable"}), 400
                
                quantity = max(1, int(item.get('quantity', 1)))
                note = item.get('note', '')
                unit_price = menu_item.price
                
                order_item = OrderItem(
                    order_id=order.order_id,
                    item_id=menu_item.item_id,
                    quantity=quantity,
                    note=note,
                    unit_price=unit_price
                )
                db.session.add(order_item)
                total += menu_item.price * quantity
            
            order.total_amount = total
            print(f"Updated total for order {order_id}: {total}")
            
        if notes is not None:
            order.notes = notes
            print(f"Updated notes for order {order_id}")
        
        # Commit changes
        db.session.commit()
        print(f"Committed changes for order {order_id}")          # Emit real-time update
        socketio.emit('order_edited', {
            'order_id': order.order_id,
            'user_id': order.user_id,
            'table_id': order.table_id,
            'status': order.status
        })
        print(f"Emitted order_edited event for order {order_id} with status {order.status}")
        
        return jsonify({
            'order_id': order.order_id, 
            'status': order.status, 
            'total': float(order.total_amount),
            'message': 'Order updated successfully'
        })
        
    except Exception as e:
        # Rollback transaction on error
        db.session.rollback()
        print(f"Error editing order {order_id}: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500
