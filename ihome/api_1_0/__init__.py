from flask import Blueprint

api = Blueprint('api_1_0', __name__)

from . import index, verify_code, passport, profile,houses, orders, pay

