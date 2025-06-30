from flask import Blueprint

bp = Blueprint('loyalty_api', __name__, url_prefix='/api/loyalty')

from app.modules.loyalty.api import loyalty_api
