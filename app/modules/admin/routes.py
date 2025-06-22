from flask import render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.modules.admin import bp
from app.models import MenuItem, Category, User, Order, Table
from app.extensions import db
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
    """Admin dashboard - Optimized with single query"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))

    # Performance: Use single query with aggregation for better performance
    from sqlalchemy import func, case

    stats_query = db.session.query(
        func.count(MenuItem.item_id).label('total_menu_items'),
        func.sum(case((MenuItem.status == 'available', 1), else_=0)).label('active_menu_items'),
        func.sum(case((MenuItem.status == 'out_of_stock', 1), else_=0)).label('out_of_stock_items')
    ).first()

    # Separate query for categories (usually small dataset)
    total_categories = Category.query.filter_by(is_active=True).count()

    # Performance: Get recent orders count for dashboard
    from datetime import datetime, timedelta, timezone
    recent_orders = Order.query.filter(
        Order.order_time >= datetime.now(timezone.utc) - timedelta(days=7)
    ).count()

    stats = {
        'total_menu_items': stats_query.total_menu_items or 0,
        'active_menu_items': stats_query.active_menu_items or 0,
        'total_categories': total_categories,
        'out_of_stock_items': stats_query.out_of_stock_items or 0,
        'recent_orders': recent_orders
    }

    return render_template('dashboard.html', stats=stats)

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
            'id': f"{order.order_id:05d}",
            'name': order.customer.name,
            'qr_number': f"#{order.table.table_number}" if order.table else "N/A",
            'date': order.order_time.strftime('%d %b %Y'),
            'type': 'Order',  # Could be enhanced based on order items
            'status': order.status.title(),
            'total': f"{order.total_amount:.2f}"
        })

    return render_template('orders.html',
                         orders=formatted_orders,
                         pagination=orders_pagination)

@bp.route('/meals')
@login_required
def meals():
    """Admin meals page"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))

    # Sample meals data - replace with actual database queries
    meals = [
        {
            'id': 1,
            'name': 'Office',
            'description': 'Office Ipsum you must be Office Ipsum you must be',
            'price': '500.00',
            'image': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=300&h=200&fit=crop'
        },
        {
            'id': 2,
            'name': 'Office',
            'description': 'Office Ipsum you must be Office Ipsum you must be',
            'price': '500.00',
            'image': 'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=300&h=200&fit=crop'
        },
        {
            'id': 3,
            'name': 'Office',
            'description': 'Office Ipsum you must be Office Ipsum you must be',
            'price': '500.00',
            'image': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=300&h=200&fit=crop'
        },
        {
            'id': 4,
            'name': 'Office',
            'description': 'Office Ipsum you must be Office Ipsum you must be',
            'price': '500.00',
            'image': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=300&h=200&fit=crop'
        },
        {
            'id': 5,
            'name': 'Office',
            'description': 'Office Ipsum you must be Office Ipsum you must be',
            'price': '500.00',
            'image': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=300&h=200&fit=crop'
        },
        {
            'id': 6,
            'name': 'Office',
            'description': 'Office Ipsum you must be Office Ipsum you must be',
            'price': '500.00',
            'image': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=300&h=200&fit=crop'
        },
        {
            'id': 7,
            'name': 'Office',
            'description': 'Office Ipsum you must be Office Ipsum you must be',
            'price': '500.00',
            'image': 'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=300&h=200&fit=crop'
        },
        {
            'id': 8,
            'name': 'Office',
            'description': 'Office Ipsum you must be Office Ipsum you must be',
            'price': '500.00',
            'image': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=300&h=200&fit=crop'
        },
        {
            'id': 9,
            'name': 'Office',
            'description': 'Office Ipsum you must be Office Ipsum you must be',
            'price': '500.00',
            'image': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=300&h=200&fit=crop'
        },
        {
            'id': 10,
            'name': 'Office',
            'description': 'Office Ipsum you must be Office Ipsum you must be',
            'price': '500.00',
            'image': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=300&h=200&fit=crop'
        },
        {
            'id': 11,
            'name': 'Office',
            'description': 'Office Ipsum you must be Office Ipsum you must be',
            'price': '500.00',
            'image': 'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=300&h=200&fit=crop'
        },
        {
            'id': 12,
            'name': 'Office',
            'description': 'Office Ipsum you must be Office Ipsum you must be',
            'price': '500.00',
            'image': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=300&h=200&fit=crop'
        },
        {
            'id': 13,
            'name': 'Office',
            'description': 'Office Ipsum you must be Office Ipsum you must be',
            'price': '500.00',
            'image': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=300&h=200&fit=crop'
        },
        {
            'id': 14,
            'name': 'Office',
            'description': 'Office Ipsum you must be Office Ipsum you must be',
            'price': '500.00',
            'image': 'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=300&h=200&fit=crop'
        },
        {
            'id': 15,
            'name': 'Office',
            'description': 'Office Ipsum you must be Office Ipsum you must be',
            'price': '500.00',
            'image': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=300&h=200&fit=crop'
        }
    ]

    return render_template('meals.html', meals=meals)

@bp.route('/services')
@login_required
def services():
    """Admin services page"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))

    # Sample services data - replace with actual database queries
    services = [
        {
            'id': 1,
            'name': 'Waiter',
            'icon': 'fas fa-user-tie',
            'description': 'Professional waiter service'
        },
        {
            'id': 2,
            'name': 'Request the Bill',
            'icon': 'fas fa-receipt',
            'description': 'Request bill service'
        },
        {
            'id': 3,
            'name': 'Extra Napkins',
            'icon': 'fas fa-tissue',
            'description': 'Additional napkins service'
        },
        {
            'id': 4,
            'name': 'Refill Coals',
            'icon': 'fas fa-fire',
            'description': 'Hookah coal refill service'
        },
        {
            'id': 5,
            'name': 'Order Ice',
            'icon': 'fas fa-cube',
            'description': 'Ice order service'
        },
        {
            'id': 6,
            'name': 'Adjust AC',
            'icon': 'fas fa-snowflake',
            'description': 'Air conditioning adjustment'
        },
        {
            'id': 7,
            'name': 'Clean My Table',
            'icon': 'fas fa-broom',
            'description': 'Table cleaning service'
        },
        {
            'id': 8,
            'name': 'Custom Request',
            'icon': 'fas fa-comment-dots',
            'description': 'Custom service request'
        },
        {
            'id': 9,
            'name': 'Custom Request',
            'icon': 'fas fa-comment-dots',
            'description': 'Custom service request'
        },
        {
            'id': 10,
            'name': 'Custom Request',
            'icon': 'fas fa-comment-dots',
            'description': 'Custom service request'
        },
        {
            'id': 11,
            'name': 'Custom Service',
            'icon': 'fas fa-plus',
            'description': 'Add custom service'
        }
    ]

    return render_template('services.html', services=services)

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
            status=status
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
