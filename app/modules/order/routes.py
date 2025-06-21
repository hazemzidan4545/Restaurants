from flask import render_template
from app.modules.order import bp

@bp.route('/')
def index():
    """Order management"""
    return render_template('order/templates/index.html')
