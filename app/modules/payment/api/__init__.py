from flask import Blueprint

bp = Blueprint('payment_api', __name__)

from app.modules.payment.api import payment_api
