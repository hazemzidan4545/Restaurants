from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.modules.customer import bp

@bp.route('/menu')
def menu():
    """Customer menu view"""
    return render_template('menu.html')

@bp.route('/profile')
@login_required
def profile():
    """Customer profile"""
    if not current_user.is_customer():
        return redirect(url_for('main.index'))
    return render_template('profile.html')

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
