import sqlalchemy
from flask_restful import Resource
from flask import request, json
from app.exchanges.controller import ExchangeController
from app.commons import get_exception_msg, create_error_msg, permissions


exchange_controller = ExchangeController()


class Exchange(Resource):

    method_decorators = [permissions]

    def get(self):
        try:
            return exchange_controller.listExchangeAll(), 200
        except sqlalchemy.exc.InternalError, e:
            return create_error_msg(get_exception_msg(e)), 500

    def post(self):
        if request.is_json:
            data = json.dumps(request.get_json())
            data = json.loads(data)
            if data['usersExchange']:
                if data['formatsExchange']:
                    if data['pairs']:
                        try:
                            return exchange_controller.addExchange(request), 200
                        except sqlalchemy.exc.InternalError, e:
                            return create_error_msg(get_exception_msg(e)), 500
                    else:
                        return create_error_msg("Add pairs"), 500
                else:
                    return create_error_msg("Add formats"), 500
            else:
                return create_error_msg("Add users"), 500
        else:
            return create_error_msg("Data not is Json"), 500

    def put(self):
        if request.is_json:
            try:
                return exchange_controller.updateExchange(request), 200
            except sqlalchemy.exc.InternalError, e:
                return create_error_msg(get_exception_msg(e)), 500
        else:
            return create_error_msg("Data not is Json"), 500

    def delete(self):
        try:
            return exchange_controller.suspendExchange(request), 200
        except sqlalchemy.exc.InternalError, e:
            return create_error_msg(get_exception_msg(e)), 500
