from flask import Blueprint

bp = Blueprint('order', __name__)

from app.modules.order import routes
