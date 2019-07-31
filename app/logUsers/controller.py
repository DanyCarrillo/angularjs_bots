import json, requests
import sqlalchemy
from flask import render_template, jsonify, request, session
from app.commons import get_exception_msg,create_error_msg,create_success_msg,val_num_slash,convert_unicode
from app.logUsers.models import LogUsersModel


class LogUsersController(object):
    def __init__(self):
        pass

    @staticmethod
    def list():
        return render_template("logsUsers/index.html")
    def viewLogUsers(self):
        try:
            userLogs_model=LogUsersModel()
            response=userLogs_model.getUserLogs()
            if response['success']==True:
                return create_success_msg(response)
            else:
                return create_error_msg(response)
        except sqlalchemy.exc.InternalError as e:
            raise e
