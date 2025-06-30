from flask import Blueprint

bp = Blueprint('loyalty', __name__, template_folder='templates')

from app.modules.loyalty import routes

# Import API blueprint
from app.modules.loyalty.api import bp as loyalty_api_bp
