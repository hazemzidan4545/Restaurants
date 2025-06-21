from flask import render_template
from app.modules.loyalty import bp

@bp.route('/')
def index():
    """Loyalty program"""
    return render_template('loyalty/templates/index.html')
