import sqlalchemy
from flask import request
from flask_restful import Resource
from app.activePairs.controller import ActivePairsController
from app.commons import (
    get_exception_msg, 
    create_error_msg, 
    permissions
)

activePairs_controller=ActivePairsController()

class ActivePairs(Resource):
    method_decorators = [permissions]

    def get(self):
        try:
            return activePairs_controller.viewPairsController(), 200
        except sqlalchemy.exc.InternalError, e:
            return create_success_msg(get_exception_msg(e)), 500
