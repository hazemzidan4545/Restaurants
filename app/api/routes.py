from flask import jsonify, request, current_app
from flask_login import current_user, login_required
from app.api import bp
from app.models import MenuItem, Category, Order, OrderItem, User, Table, Service, ServiceRequest, TableSession
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
        # Get different types of items for variety
        suggested_items = []
        
        # Try to get popular items from different categories
        categories = ['Beverages', 'Main Courses', 'Desserts', 'Appetizers', 'Drinks']
        
        for category_name in categories:
            # Find items from this category
            category_items = MenuItem.query.join(Category).filter(
                Category.name == category_name,
                MenuItem.status == 'available'
            ).limit(1).all()
            
            if category_items:
                suggested_items.extend(category_items)
            
            # Stop if we have enough items
            if len(suggested_items) >= 3:
                break
        
        # If we don't have enough items from specific categories, get random ones
        if len(suggested_items) < 3:
            remaining_needed = 3 - len(suggested_items)
            existing_ids = [item.item_id for item in suggested_items]
            
            additional_items = MenuItem.query.filter(
                MenuItem.status == 'available',
                ~MenuItem.item_id.in_(existing_ids) if existing_ids else True
            ).order_by(db.func.random()).limit(remaining_needed).all()
            
            suggested_items.extend(additional_items)

        # Format response
        response_items = []
        for item in suggested_items[:3]:  # Ensure max 3 items
            # Get default image URL based on category
            default_images = {
                'Hookah': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=200&h=200&fit=crop',
                'Beverages': 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=200&h=200&fit=crop',
                'Drinks': 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=200&h=200&fit=crop',
                'Brunch': 'https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=200&h=200&fit=crop',
                'Main Courses': 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=200&h=200&fit=crop',
                'Desserts': 'https://images.unsplash.com/photo-1551024506-0bccd828d307?w=200&h=200&fit=crop',
                'Appetizers': 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=200&h=200&fit=crop'
            }

            category_name = item.category.name if item.category else 'Main Courses'
            image_url = item.image_url or default_images.get(category_name, 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=200&h=200&fit=crop')

            response_items.append({
                'id': item.item_id,
                'name': item.name,
                'description': item.description or f'Delicious {category_name.lower()}',
                'price': float(item.price),
                'category': category_name,
                'image': image_url
            })

        return jsonify({
            'status': 'success',
            'data': response_items
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/orders', methods=['POST'])
@login_required
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

        # Create new order using the logged-in user
        order = Order(
            user_id=current_user.user_id,  # Use the authenticated user's ID
            status='new',
            total_amount=0,  # Will be calculated
            notes=data.get('notes', ''),
            order_time=datetime.utcnow(),
            table_id=data.get('table_id')  # Add table_id if provided
        )

        db.session.add(order)
        db.session.flush()  # Get order ID

        total_amount = 0

        # Process each cart item
        for cart_item in data['items']:
            # Validate item ID format
            item_id = cart_item['id']
            try:
                item_id_int = int(item_id)
                if item_id_int > 1000000:
                    return jsonify({
                        'status': 'error',
                        'message': f'Invalid item ID {item_id}. Please clear your cart and try again.'
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    'status': 'error',
                    'message': f'Invalid item ID format: {item_id}'
                }), 400

            # Find menu item
            menu_item = MenuItem.query.get(item_id)
            if not menu_item:
                return jsonify({
                    'status': 'error',
                    'message': f'Menu item {item_id} not found. Please refresh the page and try again.'
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
        
        # Update table status if a table is associated with this order
        if order.table_id:
            table = Table.query.get(order.table_id)
            if table:
                table.status = 'occupied'  # Mark table as occupied for new orders

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
        previous_status = order.status
        order.status = data['status']

        # Set completion time if order is completed
        if data['status'] == 'completed':
            order.completed_at = datetime.utcnow()

        # Update table status if the order has a table assigned
        # Check table status on ANY order status change, not just completion
        if order.table_id is not None:
            table = order.table
            table.update_status_based_on_orders()  # This now handles the commit
        else:
            # Only commit here if we didn't update a table (since update_status_based_on_orders commits)
            db.session.commit()

        # Award loyalty points when order is completed
        if data['status'] == 'completed' and previous_status != 'completed':
            try:
                from app.modules.loyalty.loyalty_service import award_points_for_order
                current_app.logger.info(f"Attempting to award points for order {order_id} to user {order.user_id}")
                result = award_points_for_order(order_id, order.user_id)
                current_app.logger.info(f"Point awarding result for order {order_id}: {result}")
            except Exception as e:
                current_app.logger.error(f"Error awarding loyalty points for order {order_id}: {str(e)}")
                import traceback
                current_app.logger.error(f"Traceback: {traceback.format_exc()}")

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

@bp.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    """Update order details (status, notes, items)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Request data is required'
            }), 400

        order = Order.query.get_or_404(order_id)
        
        # Update status if provided
        if 'status' in data:
            valid_statuses = ['new', 'processing', 'completed', 'rejected', 'cancelled', 'on-hold', 'in-transit']
            if data['status'] in valid_statuses:
                previous_status = order.status
                order.status = data['status']

                # Set completion time if order is completed
                if data['status'] == 'completed':
                    order.completed_at = datetime.utcnow()

                # Award loyalty points when order is completed
                if data['status'] == 'completed' and previous_status != 'completed':
                    try:
                        from app.modules.loyalty.loyalty_service import award_points_for_order
                        current_app.logger.info(f"Attempting to award points for order {order_id} to user {order.user_id}")
                        result = award_points_for_order(order_id, order.user_id)
                        current_app.logger.info(f"Point awarding result for order {order_id}: {result}")
                    except Exception as e:
                        current_app.logger.error(f"Error awarding loyalty points for order {order_id}: {str(e)}")
                        import traceback
                        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Update notes if provided
        if 'notes' in data:
            order.notes = data['notes']
        
        # Update items if provided
        if 'items' in data and isinstance(data['items'], list):
            # For now, we'll only update existing items (quantity and notes)
            # Not adding/removing items as that's more complex
            for item_data in data['items']:
                if 'item_id' not in item_data:
                    return jsonify({
                        'status': 'error',
                        'message': 'Item missing item_id'
                    }), 400
                
                # Find the order item
                order_item = None
                for existing_item in order.order_items:
                    if existing_item.item_id == item_data['item_id']:
                        order_item = existing_item
                        break
                
                if order_item:
                    # Update quantity and note
                    if 'quantity' in item_data:
                        order_item.quantity = max(1, int(item_data['quantity']))
                    if 'note' in item_data:
                        order_item.note = item_data['note']
                else:
                    return jsonify({
                        'status': 'error',
                        'message': f'Order item with id {item_data["item_id"]} not found'
                    }), 400
            
            # Recalculate total amount after updating items
            total = sum(item.unit_price * item.quantity for item in order.order_items)
            order.total_amount = total
        
        db.session.commit()

        # Return updated order data
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
            'message': 'Order updated successfully',
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
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/admin/sync-table-statuses', methods=['POST'])
def sync_table_statuses():
    """Synchronize all table statuses based on their orders
    
    This is useful for admin purposes if table statuses get out of sync.
    It checks all tables and updates their statuses based on active orders.
    """
    try:
        # Get counts before sync for comparison
        before_occupied = Table.query.filter_by(status='occupied').count()
        active_orders = Order.query.filter(
            Order.status.in_(['new', 'processing']),
            Order.table_id.isnot(None)
        ).count()
        
        print(f"Before sync - Occupied tables: {before_occupied}, Active orders: {active_orders}")
        
        # Call our table update method
        total_count = Table.update_all_table_statuses()
        
        # Get counts after sync
        after_occupied = Table.query.filter_by(status='occupied').count()
        
        print(f"After sync - Total tables: {total_count}, Occupied tables: {after_occupied}")
        
        return jsonify({
            'status': 'success',
            'message': f'Updated status for {total_count} tables. Now {after_occupied} tables are occupied.',
            'data': {
                'total_tables': total_count,
                'occupied_tables': after_occupied,
                'available_tables': total_count - after_occupied
            }
        })

    except Exception as e:
        print(f"Error in sync_table_statuses: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': f'Error synchronizing table statuses: {str(e)}'
        }), 500

@bp.route('/admin/table-status', methods=['GET'])
def get_table_statuses():
    """Get detailed information about table statuses
    
    This is a debugging endpoint to help diagnose issues with table status tracking.
    It shows each table along with its status and any active orders.
    
    Query parameters:
    - fix=true: Automatically fix any status mismatches
    """
    try:
        auto_fix = request.args.get('fix', 'false').lower() == 'true'
        results = []
        tables = Table.query.all()
        
        # Track tables with mismatches
        mismatched_tables = []
        
        for table in tables:
            # Get active orders for this table
            active_orders = Order.query.filter(
                Order.table_id == table.table_id,
                Order.status.in_(['new', 'processing'])
            ).all()
            
            # Check for status mismatch
            has_active_orders = len(active_orders) > 0
            status_mismatch = (table.status == 'occupied' and not has_active_orders) or \
                             (table.status == 'available' and has_active_orders)
            
            if status_mismatch:
                mismatched_tables.append(table.table_id)
                
                # Auto-fix if requested
                if auto_fix:
                    expected_status = 'occupied' if has_active_orders else 'available'
                    print(f"Fixing table {table.table_number} status: {table.status} -> {expected_status}")
                    table.status = expected_status
            
            # Format active orders
            order_info = []
            for order in active_orders:
                order_info.append({
                    'id': order.order_id,
                    'status': order.status,
                    'time': order.order_time.isoformat() if order.order_time else None,
                    'items_count': Order.query.filter_by(order_id=order.order_id).first().items.count() 
                    if hasattr(Order, 'items') else 0
                })
            
            results.append({
                'table_id': table.table_id,
                'table_number': table.table_number,
                'status': table.status,
                'active_orders_count': len(active_orders),
                'active_orders': order_info,
                'status_mismatch': status_mismatch,
                'expected_status': 'occupied' if has_active_orders else 'available'
            })
        
        # Commit changes if we did auto-fixes
        if auto_fix and mismatched_tables:
            db.session.commit()
            print(f"Fixed status for {len(mismatched_tables)} tables")
        
        # Also get overall stats
        total_tables = Table.query.count()
        occupied_tables = Table.query.filter_by(status='occupied').count()
        tables_with_active_orders = len([t for t in results if t['active_orders_count'] > 0])
        
        mismatch_tables = [
            t for t in results 
            if (t['status'] == 'occupied' and t['active_orders_count'] == 0) or
               (t['status'] == 'available' and t['active_orders_count'] > 0)
        ]
        
        return jsonify({
            'status': 'success',
            'auto_fix_applied': auto_fix,
            'data': {
                'tables': results,
                'stats': {
                    'total_tables': total_tables,
                    'occupied_tables': occupied_tables,
                    'tables_with_active_orders': tables_with_active_orders,
                    'tables_with_status_mismatch': len(mismatch_tables),
                    'mismatch_details': [
                        {
                            'table_id': t['table_id'], 
                            'table_number': t['table_number'],
                            'current': t['status'], 
                            'expected': t['expected_status']
                        }
                        for t in mismatch_tables
                    ]
                }
            }
        })
    except Exception as e:
        print(f"Error in get_table_statuses: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': f'Error getting table statuses: {str(e)}'
        }), 500

@bp.route('/service_request', methods=['POST'])
@login_required
def create_service_request():
    """Create a new service request from customer"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
            
        service_id = data.get('service_id')
        if not service_id:
            return jsonify({
                'success': False,
                'message': 'Service ID is required'
            }), 400
            
        # Verify service exists and is active
        service = Service.query.filter_by(service_id=service_id, is_active=True).first()
        if not service:
            return jsonify({
                'success': False,
                'message': 'Service not found or unavailable'
            }), 404
            
        # Get user's current table from session or request data
        table_id = data.get('table_id')
        
        # If no table_id provided, try to get from active table session
        if not table_id and current_user.is_authenticated:
            active_session = TableSession.query.filter(
                TableSession.user_id == current_user.user_id,
                TableSession.is_active == True
            ).order_by(TableSession.started_at.desc()).first()
            
            if active_session:
                table_id = active_session.table_id
        
        if not table_id:
            return jsonify({
                'success': False,
                'message': 'Table assignment required for service request'
            }), 400
        
        # Create service request
        service_request = ServiceRequest(
            service_id=service_id,
            user_id=current_user.user_id,
            table_id=table_id,
            request_type=data.get('request_type', 'general'),
            status='pending',
            description=data.get('description', data.get('notes', ''))
        )
        
        db.session.add(service_request)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{service.name} request submitted successfully',
            'request_id': service_request.request_id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating service request: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Unable to submit service request. Please try again.'
        }), 500

@bp.route('/table-session', methods=['GET', 'POST'])
def table_session_api():
    """Handle table session operations"""
    
    if request.method == 'GET':
        # Get current table session info
        table_id = request.args.get('table_id', type=int)
        session_token = request.args.get('session_token')
        
        if not table_id:
            return jsonify({
                'success': False,
                'message': 'Table ID is required'
            }), 400
        
        try:
            # Get active session
            table_session = TableSession.get_active_session(
                table_id=table_id,
                user_id=current_user.user_id if current_user.is_authenticated else None,
                session_token=session_token
            )
            
            if not table_session:
                return jsonify({
                    'success': False,
                    'message': 'No active session found'
                }), 404
            
            return jsonify({
                'success': True,
                'session': {
                    'session_id': table_session.session_id,
                    'table_id': table_session.table_id,
                    'session_token': table_session.session_token,
                    'started_at': table_session.started_at.isoformat(),
                    'is_active': table_session.is_active,
                    'table_number': table_session.table.table_number,
                    'table_status': table_session.table.status
                }
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error retrieving session: {str(e)}'
            }), 500
    
    elif request.method == 'POST':
        # Create or manage table session
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        action = data.get('action', 'create')
        table_id = data.get('table_id')
        
        if not table_id:
            return jsonify({
                'success': False,
                'message': 'Table ID is required'
            }), 400
        
        try:
            if action == 'create':
                # Create new session
                device_info = request.headers.get('User-Agent', 'Unknown')
                ip_address = request.remote_addr
                
                table_session = TableSession.create_session(
                    table_id=table_id,
                    user_id=current_user.user_id if current_user.is_authenticated else None,
                    device_info=device_info,
                    ip_address=ip_address
                )
                
                return jsonify({
                    'success': True,
                    'message': 'Session created successfully',
                    'session': {
                        'session_id': table_session.session_id,
                        'session_token': table_session.session_token,
                        'table_id': table_session.table_id
                    }
                })
                
            elif action == 'end':
                # End existing session
                session_token = data.get('session_token')
                table_session = TableSession.get_active_session(
                    table_id=table_id,
                    user_id=current_user.user_id if current_user.is_authenticated else None,
                    session_token=session_token
                )
                
                if table_session:
                    table_session.end_session()
                    
                    # Update table status to available if no other active sessions
                    other_sessions = TableSession.query.filter(
                        TableSession.table_id == table_id,
                        TableSession.is_active == True,
                        TableSession.session_id != table_session.session_id
                    ).count()
                    
                    if other_sessions == 0:
                        table = Table.query.get(table_id)
                        if table:
                            table.status = 'available'
                            db.session.commit()
                    
                    return jsonify({
                        'success': True,
                        'message': 'Session ended successfully'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Session not found'
                    }), 404
            
            else:
                return jsonify({
                    'success': False,
                    'message': 'Invalid action'
                }), 400
                
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'Error managing session: {str(e)}'
            }), 500
