from . import api
from ihome import db, models
import logging
from flask import current_app

@api.route('/index')
def index():
    a = 80
    # current_app.logger.error('1')
    # current_app.logger.info(a)
    # current_app.logger.debug(a)
    # current_app.logger.warn('4')
    return 'index page'