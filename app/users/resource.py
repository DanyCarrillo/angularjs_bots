from flask_restful import Resource
from flask import request
import sqlalchemy
from app.users.controller import UsersController
from app.commons import get_exception_msg, create_error_msg, create_success_msg, permissions

user_controller = UsersController()


class Users(Resource):
    method_decorators = [permissions]

    def get(self):
        try:
            return user_controller.listUserAll(request), 200
        except sqlalchemy.exc.InternalError, e:
            return create_success_msg(get_exception_msg(e)), 500

    def post(self):
        if request.is_json:
            try:
                return user_controller.addUser(request), 200
            except sqlalchemy.exc.InternalError, e:
                return create_error_msg(get_exception_msg(e)), 500
        else:
            return create_error_msg("Data not is Json"), 500

    def put(self):
        if request.is_json:
            try:
                return user_controller.updUser(request), 200
            except sqlalchemy.exc.InternalError, e:
                return create_error_msg(get_exception_msg(e)), 500
        else:
            return create_error_msg("Data not is Json"), 500

    def delete(self):
        try:
            return user_controller.delUser(request), 200
        except sqlalchemy.exc.InternalError, e:
            return create_error_msg(get_exception_msg(e)), 500
