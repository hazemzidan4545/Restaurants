from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.modules.admin import bp

@bp.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard"""
    if not current_user.is_admin():
        return redirect(url_for('main.index'))
    return render_template('dashboard.html')
