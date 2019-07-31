import sqlalchemy
from flask import request
from flask_restful import Resource
from app.orders.controller import OrdersController
from app.commons import (
    get_exception_msg, 
    create_error_msg, 
    permissions
)

orders_controller = OrdersController()


class Orders(Resource):
    
    method_decorators = [permissions]

    def get(self, type='A'):
        try:
            #return orders_controller.getlistCoin(request), 200
            return 'cxvxcv', 200
        except sqlalchemy.exc.InternalError, e:
            return create_error_msg(get_exception_msg(e)), 50

    def post(self):
        if request.is_json:
            #a = coins_controller.addCoin(request)
            return a, 200
        else:
            return create_error_msg("Data not is Json"), 500

    def put(self):
        if request.is_json:
            try:
                #return coins_controller.updateCoin(request), 200
                return 'asdsad', 200
            except sqlalchemy.exc.InternalError, e:
                return create_error_msg(get_exception_msg(e)), 500
        else:
            return create_error_msg("Data not is Json"), 500
            