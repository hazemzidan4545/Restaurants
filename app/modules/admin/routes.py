from flask import render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import func
from app.modules.admin import bp
from app.models import MenuItem, Category, User, Order, Table, OrderItem, QRCode, RewardItem, CustomerLoyalty, PointTransaction, RewardRedemption, PromotionalCampaign, Service
from app.extensions import db
from datetime import datetime, timedelta
import os
from PIL import Image

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_menu_image(file):
    """Save uploaded menu image and return filename"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to avoid conflicts
        import time
        timestamp = str(int(time.time()))
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"

        # Ensure upload directory exists
        upload_path = os.path.join(current_app.root_path, current_app.config['MENU_IMAGE_FOLDER'])
        os.makedirs(upload_path, exist_ok=True)

        file_path = os.path.join(upload_path, filename)
        file.save(file_path)

        # Resize image for web optimization
        try:
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')

                # Resize to max 800x600 while maintaining aspect ratio
                img.thumbnail((800, 600), Image.Resampling.LANCZOS)
                img.save(file_path, 'JPEG', quality=85, optimize=True)
        except Exception as e:
            current_app.logger.error(f"Error processing image: {e}")

        return filename
    return None

@bp.route('/')
@login_required
def index():
    """Admin index - redirect to dashboard"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))
    return redirect(url_for('admin.dashboard'))

@bp.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard - Enhanced with comprehensive statistics and charts"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))

    # Performance: Use single query with aggregation for better performance
    from sqlalchemy import func, case, desc, extract, and_
    from datetime import datetime, timedelta, timezone

    # Current time and date (UTC for database operations)
    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

    # Dashboard stats query
    stats_query = db.session.query(
        func.count(MenuItem.item_id).label('total_menu_items'),
        func.sum(case((MenuItem.status == 'available', 1), else_=0)).label('active_menu_items'),
        func.sum(case((MenuItem.status == 'out_of_stock', 1), else_=0)).label('out_of_stock_items')
    ).first()

    # Separate query for categories (usually small dataset)
    total_categories = Category.query.filter_by(is_active=True).count()
    
    # Staff count - Use the dedicated method for accurate counting
    staff_count = User.get_active_staff_count()

    # Tables status based on active QR codes and their table status
    # Get all tables that have active QR codes
    tables_with_qr = db.session.query(Table.table_id).join(
        QRCode, QRCode.table_id == Table.table_id
    ).filter(
        QRCode.is_active == True,
        QRCode.qr_type == 'menu'
    ).distinct().all()
    
    # Extract table IDs from result
    table_ids = [table.table_id for table in tables_with_qr]
    
    if table_ids:
        # If we have tables with QR codes, get their stats
        tables_data = db.session.query(
            func.count(Table.table_id).label('total_tables'),
            func.sum(case((Table.status == 'available', 1), else_=0)).label('available_tables'),
            func.sum(case((Table.status == 'occupied', 1), else_=0)).label('occupied_tables')
        ).filter(Table.table_id.in_(table_ids)).first()
    else:
        # If no tables with QR codes, use None to trigger fallback
        tables_data = None

    # Today's orders and revenue
    today_orders_query = db.session.query(
        func.count(Order.order_id).label('order_count'),
        func.sum(Order.total_amount).label('total_revenue')
    ).filter(
        Order.order_time >= today_start
    ).first()
    
    # Recent orders for last 7 days
    week_orders_count = Order.query.filter(
        Order.order_time >= now - timedelta(days=7)
    ).count()
    
    # Monthly revenue (current month)
    month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    monthly_revenue = db.session.query(
        func.sum(Order.total_amount)
    ).filter(
        Order.order_time >= month_start
    ).scalar() or 0
    
    # Prepare today's order data
    todays_orders = today_orders_query.order_count or 0
    todays_revenue = round(float(today_orders_query.total_revenue or 0), 2)
    
    # Revenue data for chart (last 7 days)
    revenue_data = {'labels': [], 'orders': [], 'revenue': []}
    
    for i in range(6, -1, -1):
        day_date = now - timedelta(days=i)
        day_start = datetime(day_date.year, day_date.month, day_date.day, tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)
        
        # Get orders and revenue for this day
        day_data = db.session.query(
            func.count(Order.order_id).label('order_count'),
            func.sum(Order.total_amount).label('revenue')
        ).filter(
            Order.order_time >= day_start,
            Order.order_time < day_end
        ).first()
        
        # Format date as day name
        day_label = day_date.strftime('%a')
        revenue_data['labels'].append(day_label)
        revenue_data['orders'].append(day_data.order_count or 0)
        revenue_data['revenue'].append(float(day_data.revenue or 0))
    
    # Popular categories data for chart
    category_data = {'labels': [], 'data': []}
    
    # Get top 5 categories by order count in the past month
    top_categories = db.session.query(
        Category.name,
        func.count(OrderItem.order_item_id).label('item_count')
    ).join(
        MenuItem, MenuItem.item_id == OrderItem.item_id
    ).join(
        Category, Category.category_id == MenuItem.category_id
    ).join(
        Order, Order.order_id == OrderItem.order_id
    ).filter(
        Order.order_time >= now - timedelta(days=30)
    ).group_by(
        Category.category_id
    ).order_by(
        desc('item_count')
    ).limit(5).all()
    
    for cat in top_categories:
        category_data['labels'].append(cat.name)
        category_data['data'].append(cat.item_count)
    
    # Order status distribution
    status_data = {'labels': ['New', 'Processing', 'Completed', 'Rejected'], 'data': [], 'colors': []}
    status_colors = {
        'new': 'rgba(59, 130, 246, 0.8)',        # Blue
        'processing': 'rgba(245, 158, 11, 0.8)',  # Yellow/Orange
        'completed': 'rgba(16, 185, 129, 0.8)',   # Green
        'rejected': 'rgba(239, 68, 68, 0.8)'      # Red
    }
    
    for status in status_data['labels']:
        count = Order.query.filter(
            Order.status == status.lower(),
            Order.order_time >= now - timedelta(days=7)
        ).count()
        status_data['data'].append(count)
        status_data['colors'].append(status_colors[status.lower()])
    
    # Prepare stats dictionary
    # Count total QR codes for tables
    qr_code_count = QRCode.query.filter_by(is_active=True, qr_type='menu').count()
    
    # Force sync all table statuses before generating stats
    # This will set tables with active orders to 'occupied' and others to 'available'
    print("Dashboard view: Updating all table statuses before rendering")
    Table.update_all_table_statuses()
    
    # If no tables with QR codes found or no tables in result, get total count of all tables
    if not tables_data or not tables_data.total_tables:
        # Explicit query for all tables
        all_tables_data = db.session.query(
            func.count(Table.table_id).label('total_tables'),
        ).first()
        
        total_tables = all_tables_data.total_tables or 0
        print(f"Using all_tables_data count: {total_tables}")
    else:
        total_tables = tables_data.total_tables or 0
        print(f"Using tables_with_qr count: {total_tables}")
    
    # Double check - get full table count for validation
    actual_total = Table.query.count()
    print(f"Actual total tables in database: {actual_total}")
    
    # Direct query for occupied tables - should match get_occupied_tables_count
    direct_occupied_count = Table.query.filter_by(status='occupied').count()
    print(f"Direct query occupied tables: {direct_occupied_count}")
    
    # Get accurate count of occupied tables using our newly fixed method
    # This checks both table status and active orders in a single query
    occupied_tables = Table.get_occupied_tables_count()
    print(f"Final occupied tables count: {occupied_tables}")
    
    # Ensure total_tables is at least the number of occupied tables
    if total_tables < occupied_tables:
        print(f"Warning: total_tables ({total_tables}) < occupied_tables ({occupied_tables}), adjusting")
        total_tables = actual_total
    
    # Calculate available tables as the difference between total and occupied
    # This ensures consistency between the numbers
    available_tables = max(0, total_tables - occupied_tables)
    print(f"Available tables: {available_tables}")
    
    stats = {
        'total_menu_items': stats_query.total_menu_items or 0,
        'active_menu_items': stats_query.active_menu_items or 0,
        'total_categories': total_categories,
        'out_of_stock_items': stats_query.out_of_stock_items or 0,
        'recent_orders': week_orders_count,
        'todays_orders': todays_orders,
        'todays_revenue': todays_revenue,
        'monthly_revenue': round(float(monthly_revenue), 2),
        'staff_count': staff_count,
        'total_tables': total_tables,
        'available_tables': available_tables,
        'occupied_tables': occupied_tables,
        'qr_code_count': qr_code_count
    }
    
    # Get recent orders for display
    recent_orders = []
    orders_query = Order.query.order_by(Order.order_time.desc()).limit(10)
    
    for order in orders_query:
        # Get customer name
        customer_name = order.customer.name if order.customer else 'Guest'
        
        # Get order type based on whether it has a table
        order_type = 'Dine-in' if order.table else 'Takeaway'
        
        recent_orders.append({
            'id': order.order_id,
            'name': customer_name,
            'qr_number': order.table.table_number if order.table else 'N/A',
            'date': order.order_time.strftime('%d %b %Y, %H:%M'),
            'type': order_type,
            'status': order.status.capitalize(),
            'total': f"{float(order.total_amount):.2f} EGP"
        })

    # Ensure admin_name is properly set and extract first name for a friendlier greeting
    if current_user and current_user.name:
        admin_name = current_user.name
        # Extract first name for a more personal greeting
        admin_first_name = admin_name.split()[0] if admin_name and ' ' in admin_name else admin_name
    else:
        admin_name = "Admin"
        admin_first_name = "Admin"
    
    # Time-based greeting (based on local time)
    hour = now.hour
    if 5 <= hour < 12:
        greeting = "Good morning"
    elif 12 <= hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    
    return render_template('dashboard.html', 
                           stats=stats, 
                           now=now, 
                           recent_orders=recent_orders, 
                           revenue_data=revenue_data,
                           category_data=category_data,
                           status_data=status_data,
                           current_user=current_user,
                           admin_name=admin_name,
                           admin_first_name=admin_first_name,
                           greeting=greeting)

@bp.route('/orders')
@login_required
def orders():
    """Admin orders page - Optimized with pagination"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))

    # Performance: Add pagination and optimize query
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Configurable items per page

    # Performance: Use join to get customer names and table info in single query
    orders_query = Order.query.join(User).outerjoin(Table).order_by(Order.order_time.desc())

    # Performance: Paginate results to avoid loading all orders
    orders_pagination = orders_query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Format orders for template
    formatted_orders = []
    for order in orders_pagination.items:
        formatted_orders.append({
            'id': order.order_id,  # Keep as integer for JS to handle correctly
            'name': order.customer.name if hasattr(order, 'customer') and order.customer else "Unknown",
            'qr_number': f"#{order.table.table_number}" if order.table else "N/A",
            'date': order.order_time.strftime('%d %b %Y'),
            'type': 'Order',  # Could be enhanced based on order items
            'status': order.status.title(),
            'total': f"{order.total_amount:.2f} EGP"
        })

    return render_template('orders.html',
                         orders=formatted_orders,
                         pagination=orders_pagination)

@bp.route('/analytics/popular-items')
@login_required
def popular_items_analytics():
    """Popular items analytics page with time period filtering"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))

    # Get time period from request args
    period = request.args.get('period', 'all')
    
    # Calculate date range based on period
    end_date = datetime.now()
    start_date = None
    
    if period == 'today':
        start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'week':
        start_date = end_date - timedelta(days=7)
    elif period == 'month':
        start_date = end_date.replace(day=1)
    elif period == 'custom':
        # Parse custom date range
        try:
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
            # Set end_date to end of day
            end_date = end_date.replace(hour=23, minute=59, second=59)
        except (ValueError, TypeError):
            # If parsing fails, fall back to all-time
            pass

    # Get popular items with counts, filtered by date range if applicable
    if start_date and period != 'all':
        popular_items_data = MenuItem.get_popular_items_with_counts(limit=15, start_date=start_date, end_date=end_date)
    else:
        popular_items_data = MenuItem.get_popular_items_with_counts(limit=15)

    # Format data for template
    analytics_data = []
    for item, count in popular_items_data:
        analytics_data.append({
            'name': item.name,
            'category': item.category.name,
            'price': float(item.price),
            'total_ordered': int(count),
            'revenue': float(item.price) * int(count),
            'image_url': item.image_url
        })

    # Handle empty analytics data
    if not analytics_data:
        flash('No data available for the selected time period.', 'info')
        
    # Calculate totals
    total_orders = sum(item['total_ordered'] for item in analytics_data) if analytics_data else 0
    total_revenue = sum(item['revenue'] for item in analytics_data) if analytics_data else 0

    return render_template('popular_items_analytics.html',
                         analytics_data=analytics_data,
                         total_orders=total_orders,
                         total_revenue=total_revenue)

@bp.route('/services')
@login_required
def services():
    """Admin services management page"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))

    # Get all services from database
    services = Service.query.order_by(Service.display_order, Service.name).all()
    
    return render_template('services_management.html', services=services)

@bp.route('/services/add', methods=['GET', 'POST'])
@login_required
def add_service():
    """Add new service"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            icon = request.form.get('icon', 'fas fa-concierge-bell').strip()
            description = request.form.get('description', '').strip()
            is_active = 'is_active' in request.form
            display_order = int(request.form.get('display_order', 0))

            # Validate required fields
            if not name:
                flash('Service name is required', 'error')
                return render_template('add_service.html')

            # Create new service
            service = Service(
                name=name,
                icon=icon,
                description=description if description else None,
                is_active=is_active,
                display_order=display_order
            )

            db.session.add(service)
            db.session.commit()

            flash(f'Service "{name}" added successfully!', 'success')
            return redirect(url_for('admin.services'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error adding service: {str(e)}', 'error')
            return render_template('add_service.html')

    return render_template('add_service.html')

@bp.route('/services/edit/<int:service_id>', methods=['GET', 'POST'])
@login_required
def edit_service(service_id):
    """Edit existing service"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))

    service = Service.query.get_or_404(service_id)

    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            icon = request.form.get('icon', 'fas fa-concierge-bell').strip()
            description = request.form.get('description', '').strip()
            is_active = 'is_active' in request.form
            display_order = int(request.form.get('display_order', 0))

            # Validate required fields
            if not name:
                flash('Service name is required', 'error')
                return render_template('edit_service.html', service=service)

            # Update service
            service.name = name
            service.icon = icon
            service.description = description if description else None
            service.is_active = is_active
            service.display_order = display_order
            service.updated_at = datetime.utcnow()

            db.session.commit()

            flash(f'Service "{name}" updated successfully!', 'success')
            return redirect(url_for('admin.services'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating service: {str(e)}', 'error')
            return render_template('edit_service.html', service=service)

    return render_template('edit_service.html', service=service)

@bp.route('/services/delete/<int:service_id>', methods=['POST'])
@login_required
def delete_service(service_id):
    """Delete service"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))

    try:
        service = Service.query.get_or_404(service_id)
        service_name = service.name

        # Check if service has any requests (handle relationship error gracefully)
        try:
            request_count = service.service_requests.count()
            if request_count > 0:
                flash(f'Cannot delete service "{service_name}" - it has {request_count} associated requests', 'error')
                return redirect(url_for('admin.services'))
        except Exception:
            # If relationship check fails, proceed with deletion (likely no foreign key constraint)
            pass

        db.session.delete(service)
        db.session.commit()

        flash(f'Service "{service_name}" deleted successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting service: {str(e)}', 'error')

    return redirect(url_for('admin.services'))

@bp.route('/services/toggle/<int:service_id>', methods=['POST'])
@login_required
def toggle_service(service_id):
    """Toggle service active status"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))

    try:
        service = Service.query.get_or_404(service_id)
        service.is_active = not service.is_active
        service.updated_at = datetime.utcnow()
        
        db.session.commit()

        status = "activated" if service.is_active else "deactivated"
        flash(f'Service "{service.name}" {status} successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating service: {str(e)}', 'error')

    return redirect(url_for('admin.services'))

@bp.route('/qr-codes')
@login_required
def qr_codes():
    """Admin QR codes page"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))

    # Sample QR codes data - replace with actual database queries
    qr_codes = [
        {
            'id': 1,
            'name': '#1',
            'description': 'Table 1 QR Code',
            'url': 'https://restaurant.com/table/1'
        },
        {
            'id': 2,
            'name': '#2',
            'description': 'Table 2 QR Code',
            'url': 'https://restaurant.com/table/2'
        },
        {
            'id': 3,
            'name': '#3',
            'description': 'Table 3 QR Code',
            'url': 'https://restaurant.com/table/3'
        },
        {
            'id': 4,
            'name': '#4',
            'description': 'Table 4 QR Code',
            'url': 'https://restaurant.com/table/4'
        },
        {
            'id': 5,
            'name': '#5',
            'description': 'Table 5 QR Code',
            'url': 'https://restaurant.com/table/5'
        },
        {
            'id': 6,
            'name': '#6',
            'description': 'Table 6 QR Code',
            'url': 'https://restaurant.com/table/6'
        },
        {
            'id': 7,
            'name': '#7',
            'description': 'Table 7 QR Code',
            'url': 'https://restaurant.com/table/7'
        },
        {
            'id': 8,
            'name': '#8',
            'description': 'Table 8 QR Code',
            'url': 'https://restaurant.com/table/8'
        },
        {
            'id': 9,
            'name': '#9',
            'description': 'Table 9 QR Code',
            'url': 'https://restaurant.com/table/9'
        },
        {
            'id': 10,
            'name': '#10',
            'description': 'Table 10 QR Code',
            'url': 'https://restaurant.com/table/10'
        }
    ]

    return render_template('qr_codes.html', qr_codes=qr_codes)

@bp.route('/profile')
@login_required
def profile():
    """Admin profile page"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))

    # Sample profile data - replace with actual user data
    profile_data = {
        'name': 'Mohammed Shouman',
        'email': 'm.shouman@gmail.com',
        'phone': '+972 9944556633',
        'avatar': None,  # Will use default avatar
        'role': 'Administrator',
        'joined_date': '2024-01-15',
        'last_login': '2024-06-22'
    }

    return render_template('profile.html', profile=profile_data)

# Menu Management Routes

@bp.route('/menu')
@login_required
def menu_management():
    """Menu management page - Optimized with eager loading"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))

    # Performance: Use eager loading to avoid N+1 queries
    from sqlalchemy.orm import joinedload

    categories = Category.query.filter_by(is_active=True).order_by(Category.display_order).all()

    # Performance: Eager load category relationship to avoid N+1 queries
    menu_items = MenuItem.query.options(joinedload(MenuItem.category)).join(Category).order_by(
        Category.display_order, MenuItem.name
    ).all()

    return render_template('menu_management.html', categories=categories, menu_items=menu_items)

@bp.route('/menu/categories')
@login_required
def category_management():
    """Category management page"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))

    categories = Category.query.order_by(Category.display_order).all()
    return render_template('category_management.html', categories=categories)

@bp.route('/menu/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    """Add new category"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        display_order = request.form.get('display_order', type=int)

        if not name:
            flash('Category name is required', 'error')
            return render_template('add_category.html')

        # Check if category already exists
        if Category.query.filter_by(name=name).first():
            flash('Category with this name already exists', 'error')
            return render_template('add_category.html')

        # Set default display order if not provided
        if display_order is None:
            max_order = db.session.query(db.func.max(Category.display_order)).scalar() or 0
            display_order = max_order + 1

        category = Category(
            name=name,
            description=description,
            display_order=display_order
        )

        try:
            db.session.add(category)
            db.session.commit()
            flash('Category added successfully', 'success')
            return redirect(url_for('admin.category_management'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding category', 'error')
            current_app.logger.error(f"Error adding category: {e}")

    return render_template('add_category.html')

@bp.route('/menu/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    """Edit category"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))

    category = Category.query.get_or_404(category_id)

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        display_order = request.form.get('display_order', type=int)
        is_active = request.form.get('is_active') == 'on'

        if not name:
            flash('Category name is required', 'error')
            return render_template('edit_category.html', category=category)

        # Check if another category with this name exists
        existing = Category.query.filter(Category.name == name, Category.category_id != category_id).first()
        if existing:
            flash('Category with this name already exists', 'error')
            return render_template('edit_category.html', category=category)

        category.name = name
        category.description = description
        category.display_order = display_order or category.display_order
        category.is_active = is_active

        try:
            db.session.commit()
            flash('Category updated successfully', 'success')
            return redirect(url_for('admin.category_management'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating category', 'error')
            current_app.logger.error(f"Error updating category: {e}")

    return render_template('edit_category.html', category=category)

@bp.route('/menu/categories/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    """Delete category"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))

    category = Category.query.get_or_404(category_id)

    # Check if category has menu items
    if category.menu_items.count() > 0:
        flash('Cannot delete category with menu items. Please move or delete items first.', 'error')
        return redirect(url_for('admin.category_management'))

    try:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting category', 'error')
        current_app.logger.error(f"Error deleting category: {e}")

    return redirect(url_for('admin.category_management'))

# Menu Item Management Routes

@bp.route('/menu/items/add', methods=['GET', 'POST'])
@login_required
def add_menu_item():
    """Add new menu item"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))

    categories = Category.query.filter_by(is_active=True).order_by(Category.display_order).all()

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price', type=float)
        category_id = request.form.get('category_id', type=int)
        stock = request.form.get('stock', type=int, default=0)
        status = request.form.get('status', 'available')

        # Get nutritional information
        ingredients = request.form.get('ingredients')
        calories = request.form.get('calories', type=int)
        preparation_time = request.form.get('preparation_time', type=int)
        allergens = request.form.get('allergens')
        serving_size = request.form.get('serving_size')
        dietary_info = request.form.get('dietary_info')

        if not name or not price or not category_id:
            flash('Name, price, and category are required', 'error')
            return render_template('add_menu_item.html', categories=categories)

        # Check if item already exists
        if MenuItem.query.filter_by(name=name).first():
            flash('Menu item with this name already exists', 'error')
            return render_template('add_menu_item.html', categories=categories)

        # Handle image upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                image_filename = save_menu_image(file)
                if not image_filename:
                    flash('Invalid image file. Please use PNG, JPG, JPEG, or GIF.', 'error')
                    return render_template('add_menu_item.html', categories=categories)

        menu_item = MenuItem(
            name=name,
            description=description,
            price=price,
            category_id=category_id,
            image_url=image_filename,
            stock=stock,
            status=status,
            ingredients=ingredients,
            calories=calories,
            preparation_time=preparation_time,
            allergens=allergens,
            serving_size=serving_size,
            dietary_info=dietary_info
        )

        try:
            db.session.add(menu_item)
            db.session.commit()
            flash('Menu item added successfully', 'success')
            return redirect(url_for('admin.menu_management'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding menu item', 'error')
            current_app.logger.error(f"Error adding menu item: {e}")

    return render_template('add_menu_item.html', categories=categories)

@bp.route('/menu/items/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_menu_item(item_id):
    """Edit menu item"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))

    menu_item = MenuItem.query.get_or_404(item_id)
    categories = Category.query.filter_by(is_active=True).order_by(Category.display_order).all()

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price', type=float)
        category_id = request.form.get('category_id', type=int)
        stock = request.form.get('stock', type=int)
        status = request.form.get('status')

        # Get nutritional information
        ingredients = request.form.get('ingredients')
        calories = request.form.get('calories', type=int)
        preparation_time = request.form.get('preparation_time', type=int)
        allergens = request.form.get('allergens')
        serving_size = request.form.get('serving_size')
        dietary_info = request.form.get('dietary_info')

        if not name or not price or not category_id:
            flash('Name, price, and category are required', 'error')
            return render_template('edit_menu_item.html', menu_item=menu_item, categories=categories)

        # Check if another item with this name exists
        existing = MenuItem.query.filter(MenuItem.name == name, MenuItem.item_id != item_id).first()
        if existing:
            flash('Menu item with this name already exists', 'error')
            return render_template('edit_menu_item.html', menu_item=menu_item, categories=categories)

        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                # Delete old image if exists
                if menu_item.image_url:
                    old_image_path = os.path.join(current_app.root_path, current_app.config['MENU_IMAGE_FOLDER'], menu_item.image_url)
                    if os.path.exists(old_image_path):
                        try:
                            os.remove(old_image_path)
                        except Exception as e:
                            current_app.logger.error(f"Error deleting old image: {e}")

                # Save new image
                image_filename = save_menu_image(file)
                if image_filename:
                    menu_item.image_url = image_filename
                else:
                    flash('Invalid image file. Please use PNG, JPG, JPEG, or GIF.', 'error')
                    return render_template('edit_menu_item.html', menu_item=menu_item, categories=categories)

        menu_item.name = name
        menu_item.description = description
        menu_item.price = price
        menu_item.category_id = category_id
        menu_item.stock = stock or 0
        menu_item.status = status
        menu_item.ingredients = ingredients
        menu_item.calories = calories
        menu_item.preparation_time = preparation_time
        menu_item.allergens = allergens
        menu_item.serving_size = serving_size
        menu_item.dietary_info = dietary_info

        try:
            db.session.commit()
            flash('Menu item updated successfully', 'success')
            return redirect(url_for('admin.menu_management'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating menu item', 'error')
            current_app.logger.error(f"Error updating menu item: {e}")

    return render_template('edit_menu_item.html', menu_item=menu_item, categories=categories)

@bp.route('/menu/items/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_menu_item(item_id):
    """Delete menu item"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))

    menu_item = MenuItem.query.get_or_404(item_id)

    # Delete associated image
    if menu_item.image_url:
        image_path = os.path.join(current_app.root_path, current_app.config['MENU_IMAGE_FOLDER'], menu_item.image_url)
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                current_app.logger.error(f"Error deleting image: {e}")

    try:
        db.session.delete(menu_item)
        db.session.commit()
        flash('Menu item deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting menu item', 'error')
        current_app.logger.error(f"Error deleting menu item: {e}")

    return redirect(url_for('admin.menu_management'))

# ======================== REWARD MANAGEMENT ROUTES ========================

@bp.route('/rewards')
@login_required
def rewards_management():
    """Admin rewards management dashboard"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))
    
    # Get all rewards with their statistics
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    rewards = RewardItem.query.order_by(RewardItem.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get reward statistics
    total_rewards = RewardItem.query.count()
    active_rewards = RewardItem.query.filter_by(status='active').count()
    inactive_rewards = RewardItem.query.filter_by(status='inactive').count()
    
    # Get redemption statistics
    total_redemptions = RewardRedemption.query.count()
    recent_redemptions = RewardRedemption.query.order_by(
        RewardRedemption.redemption_date.desc()
    ).limit(10).all()
    
    return render_template('rewards_management.html',
                         rewards=rewards,
                         total_rewards=total_rewards,
                         active_rewards=active_rewards,
                         inactive_rewards=inactive_rewards,
                         total_redemptions=total_redemptions,
                         recent_redemptions=recent_redemptions)

@bp.route('/rewards/add', methods=['GET', 'POST'])
@login_required
def add_reward():
    """Add new reward item"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            reward = RewardItem(
                name=request.form.get('name'),
                description=request.form.get('description'),
                points_required=int(request.form.get('points_required')),
                category=request.form.get('category'),
                status=request.form.get('status', 'active'),
                item_id=int(request.form.get('item_id')) if request.form.get('item_id') else None,
                expiry_date=datetime.strptime(request.form.get('expiry_date'), '%Y-%m-%d') if request.form.get('expiry_date') else None
            )
            
            db.session.add(reward)
            db.session.commit()
            
            flash('Reward added successfully!', 'success')
            return redirect(url_for('admin.rewards_management'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding reward: {str(e)}', 'error')
    
    # Get menu items for linking
    menu_items = MenuItem.query.filter_by(status='available').all()
    categories = ['Cakes & Sweets', 'Beverages', 'Main Course', 'Appetizers', 'Desserts', 'Special Offers']
    
    return render_template('add_reward.html',
                         menu_items=menu_items,
                         categories=categories)

@bp.route('/rewards/edit/<int:reward_id>', methods=['GET', 'POST'])
@login_required
def edit_reward(reward_id):
    """Edit existing reward"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))
    
    reward = RewardItem.query.get_or_404(reward_id)
    
    if request.method == 'POST':
        try:
            reward.name = request.form.get('name')
            reward.description = request.form.get('description')
            reward.points_required = int(request.form.get('points_required'))
            reward.category = request.form.get('category')
            reward.status = request.form.get('status')
            reward.item_id = int(request.form.get('item_id')) if request.form.get('item_id') else None
            reward.expiry_date = datetime.strptime(request.form.get('expiry_date'), '%Y-%m-%d') if request.form.get('expiry_date') else None
            
            db.session.commit()
            
            flash('Reward updated successfully!', 'success')
            return redirect(url_for('admin.rewards_management'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating reward: {str(e)}', 'error')
    
    # Get menu items for linking
    menu_items = MenuItem.query.filter_by(status='available').all()
    categories = ['Cakes & Sweets', 'Beverages', 'Main Course', 'Appetizers', 'Desserts', 'Special Offers']
    
    return render_template('edit_reward.html',
                         reward=reward,
                         menu_items=menu_items,
                         categories=categories)

@bp.route('/rewards/delete/<int:reward_id>', methods=['POST'])
@login_required
def delete_reward(reward_id):
    """Delete reward item"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))
    
    try:
        reward = RewardItem.query.get_or_404(reward_id)
        
        # Check if reward has been redeemed
        redemptions = RewardRedemption.query.filter_by(reward_id=reward_id).count()
        
        if redemptions > 0:
            # Instead of deleting, mark as inactive
            reward.status = 'inactive'
            db.session.commit()
            flash('Reward marked as inactive (has redemption history)', 'warning')
        else:
            db.session.delete(reward)
            db.session.commit()
            flash('Reward deleted successfully!', 'success')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting reward: {str(e)}', 'error')
    
    return redirect(url_for('admin.rewards_management'))

@bp.route('/rewards/toggle/<int:reward_id>', methods=['POST'])
@login_required
def toggle_reward_status(reward_id):
    """Toggle reward active/inactive status"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        reward = RewardItem.query.get_or_404(reward_id)
        reward.status = 'inactive' if reward.status == 'active' else 'active'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'status': reward.status,
            'message': f'Reward {reward.status}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error toggling reward status: {str(e)}'
        }), 500

@bp.route('/rewards/bulk-update', methods=['POST'])
@login_required
def bulk_update_rewards():
    """Bulk update rewards (status, category, etc.)"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        reward_ids = data.get('reward_ids', [])
        action = data.get('action')
        value = data.get('value')
        
        if not reward_ids or not action:
            return jsonify({'success': False, 'message': 'Missing required parameters'}), 400
        
        rewards = RewardItem.query.filter(RewardItem.reward_id.in_(reward_ids)).all()
        
        for reward in rewards:
            if action == 'status':
                reward.status = value
            elif action == 'category':
                reward.category = value
            elif action == 'points':
                reward.points_required = int(value)
        
        db.session.commit();
        
        return jsonify({
            'success': True,
            'message': f'Updated {len(rewards)} rewards'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating rewards: {str(e)}'
        }), 500

# ======================== END REWARD MANAGEMENT ROUTES ========================

# ======================== LOYALTY MANAGEMENT ROUTES ========================

@bp.route('/loyalty-management')
@login_required
def loyalty_management():
    """Admin loyalty program management dashboard"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Number of customers per page
    
    # Get paginated customers
    customers = CustomerLoyalty.query.order_by(
        CustomerLoyalty.total_points.desc()
    ).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    # Get loyalty program statistics
    total_customers = CustomerLoyalty.query.count()
    active_customers = CustomerLoyalty.query.filter(CustomerLoyalty.total_points > 0).count()
    
    # Get tier distribution
    bronze_customers = CustomerLoyalty.query.filter_by(tier_level='bronze').count()
    silver_customers = CustomerLoyalty.query.filter_by(tier_level='silver').count()
    gold_customers = CustomerLoyalty.query.filter_by(tier_level='gold').count()
    platinum_customers = CustomerLoyalty.query.filter_by(tier_level='platinum').count()
    
    # Get total points distributed
    total_points_distributed = db.session.query(func.sum(PointTransaction.points_earned)).scalar() or 0
    total_points_redeemed = db.session.query(func.sum(PointTransaction.points_redeemed)).scalar() or 0
    
    # Get recent transactions
    recent_transactions = PointTransaction.query.order_by(
        PointTransaction.timestamp.desc()
    ).limit(10).all()
    
    # Top customers by points
    top_customers = CustomerLoyalty.query.order_by(
        CustomerLoyalty.total_points.desc()
    ).limit(10).all()
    
    return render_template('loyalty_management.html',
                         customers=customers,
                         total_customers=total_customers,
                         active_customers=active_customers,
                         bronze_customers=bronze_customers,
                         silver_customers=silver_customers,
                         gold_customers=gold_customers,
                         platinum_customers=platinum_customers,
                         total_points_distributed=total_points_distributed,
                         total_points_redeemed=total_points_redeemed,
                         recent_transactions=recent_transactions,
                         top_customers=top_customers)

# ======================== END LOYALTY MANAGEMENT ROUTES ========================

# ======================== CAMPAIGNS MANAGEMENT ROUTES ========================

@bp.route('/campaigns-management')
@login_required
def campaigns_management():
    """Admin campaigns management dashboard"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))
    
    # Get all campaigns with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    campaigns = PromotionalCampaign.query.order_by(
        PromotionalCampaign.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    # Get campaign statistics
    total_campaigns = PromotionalCampaign.query.count()
    active_campaigns = PromotionalCampaign.query.filter_by(status='active').count()
    inactive_campaigns = PromotionalCampaign.query.filter_by(status='inactive').count()
    expired_campaigns = PromotionalCampaign.query.filter_by(status='expired').count()
    
    return render_template('campaigns_management.html',
                         campaigns=campaigns,
                         total_campaigns=total_campaigns,
                         active_campaigns=active_campaigns,
                         inactive_campaigns=inactive_campaigns,
                         expired_campaigns=expired_campaigns)

@bp.route('/campaigns/add', methods=['GET', 'POST'])
@login_required
def add_campaign():
    """Add new promotional campaign"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            campaign = PromotionalCampaign(
                name=request.form.get('name'),
                description=request.form.get('description'),
                bonus_multiplier=float(request.form.get('bonus_multiplier', 1.0)),
                start_date=datetime.strptime(request.form.get('start_date'), '%Y-%m-%d'),
                end_date=datetime.strptime(request.form.get('end_date'), '%Y-%m-%d'),
                conditions=request.form.get('conditions'),
                status=request.form.get('status', 'active')
            )
            
            db.session.add(campaign)
            db.session.commit()
            
            flash('Campaign added successfully!', 'success')
            return redirect(url_for('admin.campaigns_management'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding campaign: {str(e)}', 'error')
    
    return render_template('add_campaign.html')

@bp.route('/campaigns/edit/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
def edit_campaign(campaign_id):
    """Edit existing campaign"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))
    
    campaign = PromotionalCampaign.query.get_or_404(campaign_id)
    
    if request.method == 'POST':
        try:
            campaign.name = request.form.get('name')
            campaign.description = request.form.get('description')
            campaign.bonus_multiplier = float(request.form.get('bonus_multiplier', 1.0))
            campaign.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
            campaign.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
            campaign.conditions = request.form.get('conditions')
            campaign.status = request.form.get('status')
            
            db.session.commit()
            
            flash('Campaign updated successfully!', 'success')
            return redirect(url_for('admin.campaigns_management'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating campaign: {str(e)}', 'error')
    
    return render_template('edit_campaign.html', campaign=campaign)

# ======================== END CAMPAIGNS MANAGEMENT ROUTES ========================

# API Routes for AJAX operations

@bp.route('/api/recent-activity')
@login_required
def api_recent_activity():
    """API endpoint for recent activity data"""
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    # Performance: Get recent activities with limit
    from datetime import datetime, timedelta, timezone

    recent_orders = Order.query.join(User).filter(
        Order.order_time >= datetime.now(timezone.utc) - timedelta(hours=24)
    ).order_by(Order.order_time.desc()).limit(5).all()

    activities = []
    for order in recent_orders:
        activities.append({
            'title': f'New order from {order.customer.name}',
            'icon': 'fas fa-shopping-cart',
            'time': order.order_time.strftime('%H:%M'),
            'type': 'order'
        })

    return jsonify({'activities': activities})



@bp.route('/api/search')
@login_required
def api_search():
    """API endpoint for search functionality"""
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'results': []})

    # Performance: Search across multiple models with limit
    results = []

    # Search menu items
    menu_items = MenuItem.query.filter(
        MenuItem.name.ilike(f'%{query}%')
    ).limit(5).all()

    for item in menu_items:
        results.append({
            'title': item.name,
            'type': 'menu_item',
            'url': url_for('admin.edit_menu_item', item_id=item.item_id),
            'description': item.description[:100] if item.description else ''
        })

    # Search categories
    categories = Category.query.filter(
        Category.name.ilike(f'%{query}%')
    ).limit(3).all()

    for category in categories:
        results.append({
            'title': category.name,
            'type': 'category',
            'url': url_for('admin.edit_category', category_id=category.category_id),
            'description': category.description[:100] if category.description else ''
        })

    return jsonify({'results': results})

@bp.route('/api/menu/items/<int:item_id>/stock', methods=['POST'])
@login_required
def update_item_stock(item_id):
    """Update menu item stock via AJAX"""
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    menu_item = MenuItem.query.get_or_404(item_id)
    data = request.get_json()

    if 'stock' not in data:
        return jsonify({'error': 'Stock value required'}), 400

    try:
        menu_item.stock = int(data['stock'])
        # Auto-update status based on stock
        if menu_item.stock <= 0:
            menu_item.status = 'out_of_stock'
        elif menu_item.status == 'out_of_stock' and menu_item.stock > 0:
            menu_item.status = 'available'

        db.session.commit()
        return jsonify({
            'success': True,
            'stock': menu_item.stock,
            'status': menu_item.status
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update stock'}), 500

@bp.route('/api/menu/items/<int:item_id>/status', methods=['POST'])
@login_required
def update_item_status(item_id):
    """Update menu item status via AJAX"""
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    menu_item = MenuItem.query.get_or_404(item_id)
    data = request.get_json()

    if 'status' not in data:
        return jsonify({'error': 'Status value required'}), 400

    valid_statuses = ['available', 'out_of_stock', 'discontinued']
    if data['status'] not in valid_statuses:
        return jsonify({'error': 'Invalid status'}), 400

    try:
        menu_item.status = data['status']
        db.session.commit()
        return jsonify({
            'success': True,
            'status': menu_item.status
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update status'}), 500

# API Endpoints for Real-time Notifications

@bp.route('/api/order-notifications')
@login_required
def api_order_notifications():
    """API endpoint to get order notification data"""
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        # Get count of new and processing orders
        new_orders_count = Order.get_new_orders_count()

        # Get recent orders from last 2 hours for more immediate notifications
        recent_cutoff = datetime.utcnow() - timedelta(hours=2)
        recent_orders_count = Order.query.filter(
            Order.order_time >= recent_cutoff,
            Order.status.in_(['new', 'processing'])
        ).count()

        # Determine if there are new orders to notify about
        has_new_orders = new_orders_count > 0

        return jsonify({
            'success': True,
            'has_new_orders': has_new_orders,
            'new_orders_count': new_orders_count,
            'recent_orders_count': recent_orders_count,
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f"Error fetching order notifications: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch notifications',
            'has_new_orders': False,
            'new_orders_count': 0
        }), 500

@bp.route('/api/mark-orders-seen', methods=['POST'])
@login_required
def api_mark_orders_seen():
    """API endpoint to mark orders as seen (for notification management)"""
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        # This could be enhanced to track which admin has seen which orders
        # For now, we'll just return success
        return jsonify({
            'success': True,
            'message': 'Orders marked as seen'
        })

    except Exception as e:
        current_app.logger.error(f"Error marking orders as seen: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to mark orders as seen'
        }), 500
