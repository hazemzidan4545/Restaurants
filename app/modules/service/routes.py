from flask import render_template
from app.modules.service import bp

@bp.route('/')
def index():
    """Services page"""
    return render_template('index.html')
