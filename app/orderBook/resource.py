import sqlalchemy
from flask import request
from flask_restful import Resource
from app.orderBook.controller import OrderBookController
from app.commons import (
    get_exception_msg, 
    create_error_msg, 
    permissions
)

orderBook_controller = OrderBookController()


class OrderBook(Resource):
    
    method_decorators = [permissions]

    def get(self, type='A'):
        try:
            return 'respuesta exitosa', 200
        except sqlalchemy.exc.InternalError, e:
            return create_error_msg(get_exception_msg(e)), 500

    def post(self):
        if request.is_json:
            return 'respuesta exitosa', 200
        else:
            return create_error_msg("Data not is Json"), 500

    def put(self):
        if request.is_json:
            try:
                return 'respuesta exitosa', 200
            except sqlalchemy.exc.InternalError, e:
                return create_error_msg(get_exception_msg(e)), 500
        else:
            return create_error_msg("Data not is Json"), 500
            