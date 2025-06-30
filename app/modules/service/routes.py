from flask import render_template
from app.modules.service import bp
from app.models import Service

@bp.route('/')
def index():
    """Services page"""
    # Get all active services from database
    services = Service.query.filter_by(is_active=True).order_by(Service.display_order, Service.name).all()
    return render_template('index.html', services=services)
