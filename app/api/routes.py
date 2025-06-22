from flask import jsonify, request
from app.api import bp
from app.models import MenuItem, Category, Order, OrderItem, User
from app.extensions import db
from datetime import datetime
import uuid

@bp.route('/health')
def health():
    """API health check"""
    return jsonify({'status': 'healthy', 'message': 'Restaurant API is running'})

@bp.route('/menu-items')
def get_menu_items():
    """Get all available menu items"""
    try:
        items = MenuItem.query.filter_by(status='available').all()
        menu_items = []

        for item in items:
            # Get default image URL based on category
            default_images = {
                'Hookah': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300&h=200&fit=crop',
                'Drinks': 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=300&h=200&fit=crop',
                'Brunch': 'https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=300&h=200&fit=crop',
                'Main Courses': 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=300&h=200&fit=crop',
                'Desserts': 'https://images.unsplash.com/photo-1551024506-0bccd828d307?w=300&h=200&fit=crop'
            }

            category_name = item.category.name if item.category else 'Main Courses'
            image_url = item.image_url or default_images.get(category_name, 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=300&h=200&fit=crop')

            menu_items.append({
                'id': item.item_id,
                'name': item.name,
                'description': item.description,
                'price': float(item.price),
                'category': category_name,
                'image': image_url,
                'stock': item.stock
            })

        return jsonify({
            'status': 'success',
            'data': menu_items
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/menu-items/suggested')
def get_suggested_items():
    """Get suggested menu items for cart"""
    try:
        # Get 3 random available items
        items = MenuItem.query.filter_by(status='available').limit(3).all()
        suggested_items = []

        for item in items:
            # Get default image URL based on category
            default_images = {
                'Hookah': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=80&h=80&fit=crop',
                'Drinks': 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=80&h=80&fit=crop',
                'Brunch': 'https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=80&h=80&fit=crop',
                'Main Courses': 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=80&h=80&fit=crop',
                'Desserts': 'https://images.unsplash.com/photo-1551024506-0bccd828d307?w=80&h=80&fit=crop'
            }

            category_name = item.category.name if item.category else 'Main Courses'
            image_url = item.image_url or default_images.get(category_name, 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=80&h=80&fit=crop')

            suggested_items.append({
                'id': item.item_id,
                'name': item.name,
                'description': item.description,
                'price': float(item.price),
                'category': category_name,
                'image': image_url
            })

        return jsonify({
            'status': 'success',
            'data': suggested_items
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/orders', methods=['POST'])
def create_order():
    """Process checkout and create new order"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data or 'items' not in data or 'paymentMethod' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields: items and paymentMethod'
            }), 400

        if not data['items']:
            return jsonify({
                'status': 'error',
                'message': 'Cart is empty'
            }), 400

        # Create new order
        order = Order(
            user_id=1,  # Default user for now (will be updated when auth is implemented)
            status='new',
            total_amount=0,  # Will be calculated
            notes=data.get('notes', ''),
            order_time=datetime.utcnow()
        )

        db.session.add(order)
        db.session.flush()  # Get order ID

        total_amount = 0

        # Process each cart item
        for cart_item in data['items']:
            # Find menu item
            menu_item = MenuItem.query.get(cart_item['id'])
            if not menu_item:
                return jsonify({
                    'status': 'error',
                    'message': f'Menu item {cart_item["id"]} not found'
                }), 400

            # Check availability
            if menu_item.status != 'available':
                return jsonify({
                    'status': 'error',
                    'message': f'{menu_item.name} is not available'
                }), 400

            # Create order item
            order_item = OrderItem(
                order_id=order.order_id,
                item_id=menu_item.item_id,
                quantity=cart_item['quantity'],
                note=cart_item.get('specialInstructions', ''),
                unit_price=menu_item.price
            )

            db.session.add(order_item)
            total_amount += float(menu_item.price) * cart_item['quantity']

        # Add service charge
        service_charge = 2.00
        total_amount += service_charge

        # Update order total
        order.total_amount = total_amount

        # Commit transaction
        db.session.commit()

        # Generate order number for display
        order_number = f"ORD-{order.order_id:06d}"

        return jsonify({
            'status': 'success',
            'message': 'Order placed successfully',
            'data': {
                'order_id': order.order_id,
                'order_number': order_number,
                'total_amount': float(total_amount),
                'status': order.status,
                'estimated_time': 25,  # Default 25 minutes
                'order_time': order.order_time.isoformat()
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to process order: {str(e)}'
        }), 500

@bp.route('/orders/<int:order_id>')
def get_order(order_id):
    """Get order details by ID"""
    try:
        order = Order.query.get_or_404(order_id)

        # Get order items with menu item details
        order_items = []
        for item in order.order_items:
            order_items.append({
                'id': item.item_id,
                'name': item.menu_item.name,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'total_price': float(item.unit_price * item.quantity),
                'note': item.note
            })

        return jsonify({
            'status': 'success',
            'data': {
                'order_id': order.order_id,
                'order_number': f"ORD-{order.order_id:06d}",
                'status': order.status,
                'total_amount': float(order.total_amount),
                'order_time': order.order_time.isoformat(),
                'estimated_time': order.estimated_time or 25,
                'notes': order.notes,
                'items': order_items
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Update order status"""
    try:
        data = request.get_json()

        if not data or 'status' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Status is required'
            }), 400

        valid_statuses = ['new', 'processing', 'completed', 'rejected', 'cancelled']
        if data['status'] not in valid_statuses:
            return jsonify({
                'status': 'error',
                'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }), 400

        order = Order.query.get_or_404(order_id)
        order.status = data['status']

        # Set completion time if order is completed
        if data['status'] == 'completed':
            order.completed_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Order status updated successfully',
            'data': {
                'order_id': order.order_id,
                'status': order.status,
                'completed_at': order.completed_at.isoformat() if order.completed_at else None
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
