from flask import render_template
from app.modules.menu import bp

@bp.route('/')
def index():
    """Menu listing"""
    return render_template('menu.html')
