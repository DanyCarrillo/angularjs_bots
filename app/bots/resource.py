import sqlalchemy
from flask import request
from flask_restful import Resource
from app.bots.controller import BotsController
from app.commons import (
    permissions, 
    create_error_msg,
    get_exception_msg
)


bots_controller = BotsController()


class Bots(Resource):

    method_decorators = [permissions]

    def get(self, idApiUser=None):
        try:
            response = bots_controller.listBotsAll(request) 
            return (response, 200)
        except sqlalchemy.exc.InternalError as e:
            response = create_error_msg(get_exception_msg(e))
            return (response, 500)

    def post(self):
        if request.is_json:
            try:
                response = bots_controller.addBotConfig(request)
                return (response, 200)
            except sqlalchemy.exc.InternalError as e:
                response = create_error_msg(get_exception_msg(e))
                return (response, 500)
        else:
            response = create_error_msg('Data is not JSON')
            return (response, 500)

    def put(self):
        if request.is_json:
            try:
                response = bots_controller.updBotConfig(request)
                return (response, 200)
            except sqlalchemy.exc.InternalError as e:
                response = create_error_msg(get_exception_msg(e))
                return (response, 500)
        else:
            response = create_error_msg('Data is not JSON')
            return (response, 500)

    def delete(self):
        try:
            response = {"mensaje":"page not found"} 
            return (response, 404)
        except sqlalchemy.exc.InternalError as e:
            response = create_error_msg(obt_mes_exception(e))
            return (response, 500)
