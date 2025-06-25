from flask import Blueprint

bp = Blueprint('order', __name__)

from app.modules.order import routes

# Removed the registration of order_api as a sub-blueprint
