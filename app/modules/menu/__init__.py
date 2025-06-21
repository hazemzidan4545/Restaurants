from flask import Blueprint

bp = Blueprint('menu', __name__, template_folder='../customer/templates')

from app.modules.menu import routes
