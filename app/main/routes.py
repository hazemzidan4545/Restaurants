from flask import render_template, redirect, url_for, send_from_directory, current_app
from flask_login import current_user
from app.main import bp
import os

@bp.route('/')
def index():
    """Main landing page"""
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_waiter():
            return redirect(url_for('waiter.dashboard'))
        else:
            return redirect(url_for('customer.menu'))
    return render_template('shared/landing.html')

@bp.route('/test-checkout')
def test_checkout():
    """Test checkout functionality"""
    return send_from_directory('.', 'test_checkout.html')

@bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    upload_folder = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
    return send_from_directory(upload_folder, filename)
