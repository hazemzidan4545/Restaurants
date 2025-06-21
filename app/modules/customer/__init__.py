from flask import Blueprint

bp = Blueprint('customer', __name__, template_folder='templates')

from app.modules.customer import routes
