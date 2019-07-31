import sqlalchemy
from flask import request, json
from flask_restful import Resource
from app.plays.controller import PlayController
from app.commons import get_exception_msg, create_error_msg, permissions


class Play(Resource):

    method_decorators = [permissions]

    def get(self):
        pass


    def post(self):
        pass

    def put(self):
        pass