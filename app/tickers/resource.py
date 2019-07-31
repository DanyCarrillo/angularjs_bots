import sqlalchemy
from flask import request
from flask_restful import Resource
from app.tickers.controller import TickersController
from app.commons import (
    get_exception_msg, 
    create_error_msg, 
    permissions
)

tickers_controller=TickersController()

class Tickers(Resource):
    method_decorators = [permissions]
    def get(self):
        try:
            return tickers_controller.viewTickers(), 200
        except sqlalchemy.exc.InternalError, e:
            return create_success_msg(get_exception_msg(e)), 500
