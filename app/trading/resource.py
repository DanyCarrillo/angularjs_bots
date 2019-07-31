from flask_restful import Resource
from flask import request
import sqlalchemy
from app.trading.controller import TradingController
from app.commons import get_exception_msg,create_error_msg,permissions

tradeController = TradingController()

class Trading(Resource):
    method_decorators =  [permissions]

    def post(self):
        if request.is_json:
            try:
                return (
                    tradeController.traPlay(request), 200)
            except sqlalchemy.exc.InternalError as e:
                return (
                 create_error_msg(get_exception_msg(e)), 500)

        else:
            return (
             create_error_msg('Data not is Json'), 500)


    def put(self):
        if request.is_json:
            try:
                return (
                 tradeController.traStop(request), 200)
            except sqlalchemy.exc.InternalError as e:
                return (
                 create_error_msg(get_exception_msg(e)), 500)

        else:
            return (
             create_error_msg('Data not is Json'), 500)