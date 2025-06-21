from flask import Blueprint

bp = Blueprint('loyalty', __name__)

from app.modules.loyalty import routes
