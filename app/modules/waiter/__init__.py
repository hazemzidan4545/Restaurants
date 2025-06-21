from flask import Blueprint

bp = Blueprint('waiter', __name__, template_folder='templates')

from app.modules.waiter import routes
