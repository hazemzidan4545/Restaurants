from flask import Blueprint

bp = Blueprint('service', __name__, template_folder='templates')

from app.modules.service import routes
