from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app.modules.customer import bp
from app.models import MenuItem, Category, Order, CustomerPreferences, db
from sqlalchemy.orm import joinedload
from datetime import datetime
import os
from werkzeug.utils import secure_filename

@bp.route('/menu')
def menu():
    """Customer menu view"""
    # Load categories and menu items from database
    categories = Category.query.filter_by(is_active=True).order_by(Category.display_order).all()
    menu_items = MenuItem.query.options(joinedload(MenuItem.category)).filter_by(status='available').join(Category).order_by(
        Category.display_order, MenuItem.name
    ).all()

    return render_template('menu.html', categories=categories, menu_items=menu_items)

@bp.route('/profile')
@login_required
def profile():
    """Customer profile"""
    if not current_user.is_customer():
        return redirect(url_for('main.index'))
    
    # Get or create preferences for display
    preferences = current_user.preferences
    if not preferences:
        preferences = CustomerPreferences(user_id=current_user.user_id)
        db.session.add(preferences)
        db.session.commit()
    
    return render_template('customer_profile.html', profile=current_user, preferences=preferences, now=datetime.utcnow())

@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Customer edit profile"""
    if not current_user.is_customer():
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            # Update basic profile information
            current_user.name = request.form.get('name', '').strip()
            current_user.email = request.form.get('email', '').strip()
            current_user.phone = request.form.get('phone', '').strip() or None
            
            # Handle profile image upload
            if 'profile_img' in request.files:
                file = request.files['profile_img']
                if file and file.filename != '':
                    # Create uploads directory if it doesn't exist
                    upload_folder = 'app/static/uploads/profile_images'
                    os.makedirs(upload_folder, exist_ok=True)
                    
                    # Secure filename and save
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(upload_folder, f"user_{current_user.user_id}_{filename}")
                    file.save(file_path)
                    
                    # Store relative path for web access
                    current_user.profile_img = f"/static/uploads/profile_images/user_{current_user.user_id}_{filename}"
            
            # Save to database
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('customer.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile. Please try again.', 'error')
            
    return render_template('customer_edit_profile.html', profile=current_user)

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Customer settings"""
    if not current_user.is_customer():
        return redirect(url_for('main.index'))
    
    # Get or create preferences
    preferences = current_user.preferences
    if not preferences:
        preferences = CustomerPreferences(user_id=current_user.user_id)
        db.session.add(preferences)
        db.session.commit()
    
    if request.method == 'POST':
        try:
            # Handle password change
            if 'current_password' in request.form and 'new_password' in request.form:
                current_password = request.form.get('current_password')
                new_password = request.form.get('new_password')
                confirm_password = request.form.get('confirm_password')
                
                if not current_user.check_password(current_password):
                    flash('Current password is incorrect.', 'error')
                elif new_password != confirm_password:
                    flash('New passwords do not match.', 'error')
                elif len(new_password) < 6:
                    flash('Password must be at least 6 characters long.', 'error')
                else:
                    current_user.set_password(new_password)
                    db.session.commit()
                    flash('Password updated successfully!', 'success')
                    return redirect(url_for('customer.settings'))
            
            # Handle account deactivation
            elif 'deactivate_account' in request.form:
                confirm_password = request.form.get('deactivate_password')
                if current_user.check_password(confirm_password):
                    current_user.is_active = False
                    db.session.commit()
                    flash('Account deactivated successfully.', 'success')
                    return redirect(url_for('main.index'))
                else:
                    flash('Password is incorrect. Account not deactivated.', 'error')
                    
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')
            
    return render_template('customer_settings.html', profile=current_user, preferences=preferences)

@bp.route('/settings/preferences', methods=['POST'])
@login_required
def update_preferences():
    """Update notification and privacy preferences via AJAX"""
    if not current_user.is_customer():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        # Get or create preferences
        preferences = current_user.preferences
        if not preferences:
            preferences = CustomerPreferences(user_id=current_user.user_id)
            db.session.add(preferences)
        
        data = request.get_json()
        
        # Update notification preferences
        if 'notify_order_updates' in data:
            preferences.notify_order_updates = data['notify_order_updates']
        if 'notify_loyalty_points' in data:
            preferences.notify_loyalty_points = data['notify_loyalty_points']
        if 'notify_promotions' in data:
            preferences.notify_promotions = data['notify_promotions']
        if 'notify_service_requests' in data:
            preferences.notify_service_requests = data['notify_service_requests']
            
        # Update privacy preferences
        if 'profile_visible' in data:
            preferences.profile_visible = data['profile_visible']
        if 'order_history_private' in data:
            preferences.order_history_private = data['order_history_private']
        if 'analytics_enabled' in data:
            preferences.analytics_enabled = data['analytics_enabled']
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Preferences updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to update preferences'}), 500

@bp.route('/checkout')
def checkout():
    """Customer checkout page"""
    return render_template('checkout.html')

@bp.route('/order-confirmation/<int:order_id>')
def order_confirmation(order_id):
    """Order confirmation page"""
    return render_template('order_confirmation.html', order_id=order_id)

@bp.route('/track-order/<int:order_id>')
def track_order(order_id):
    """Order tracking page"""
    return render_template('track_order.html', order_id=order_id)

@bp.route('/home')
@bp.route('/')
def home():
    """Customer home page using default landing template"""
    # Load popular menu items for the landing page
    popular_items = MenuItem.get_popular_items(limit=4)

    # If no popular items (no orders yet), fall back to first 4 available items
    if not popular_items:
        popular_items = MenuItem.query.filter_by(status='available').limit(4).all()

    return render_template('shared/landing.html', popular_items=popular_items)

@bp.route('/orders')
@login_required
def my_orders():
    """Customer orders page"""
    if not current_user.is_customer():
        return redirect(url_for('main.index'))
    
    # Get orders for the current user
    orders = Order.query.filter_by(user_id=current_user.user_id).order_by(Order.order_time.desc()).all()
    
    return render_template('customer_orders.html', orders=orders)

@bp.route('/loyalty')
@login_required
def loyalty():
    """Customer loyalty page - redirect to main loyalty module"""
    if not current_user.is_customer():
        return redirect(url_for('main.index'))
    
    return redirect(url_for('loyalty.index'))
