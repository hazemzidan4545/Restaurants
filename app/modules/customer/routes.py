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
