from flask import Blueprint, jsonify, render_template
from app import api
from app.commons import permissions
from app.logUsers.resource import LogUsers
from app.logUsers.controller import LogUsersController

logUsers = Blueprint('logUsers', __name__)
api.add_resource(LogUsers,'/logUser')

logUsers_controller=LogUsersController()
@logUsers.route('/modLogUsers/list', methods=['GET'])
@permissions
def lisLogUsers():
	return logUsers_controller.list()
