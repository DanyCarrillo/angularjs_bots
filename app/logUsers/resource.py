import sqlalchemy
from flask import request
from flask_restful import Resource
from app.logUsers.controller import LogUsersController
from app.commons import (
    get_exception_msg, 
    create_error_msg, 
    permissions
)

logUsers_controller=LogUsersController()

class LogUsers(Resource):
    method_decorators = [permissions]
    def get(self):
        try:
            return logUsers_controller.viewLogUsers(), 200
        except sqlalchemy.exc.InternalError, e:
            return create_success_msg(get_exception_msg(e)), 500
