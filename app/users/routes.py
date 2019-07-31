'''
Created by rgomez
@date: 12/04/2018

Referenced file of Source/bots_2_0 project
'''

from flask import Blueprint, redirect, jsonify, request, session, render_template
from app import api
from app.users.resource import Users
from app.users.controller import UsersController
from app.commons import permissions

users = Blueprint('users', __name__)
controllerUsers = UsersController()

api.add_resource(Users, '/user')


@users.route('/', methods=['GET'])
def index():
    if 'id_user' in session:
        return redirect("/modBots/list")
    else:
        return redirect('/modUser/login')


@users.route('/modUser/list', methods=['GET'])
@permissions
def listUsers():
    return controllerUsers.list()


@users.route('/modUser/suspend', methods=['PUT'])
@permissions
def bloUser():
    return controllerUsers.suspend_user(request)


@users.route('/modUser/login', methods=['GET', 'POST'])
def login_user():
    if request.method == 'GET':
        return controllerUsers.login()
    else:
        return controllerUsers.postLogin(request)


@users.route('/modUser/logout', methods=['GET'])
def logout():
    return controllerUsers.logOut()

# Adaptacion API v1.0
# Metodos API independientes:
# Controlador: exchanges_controler (controller.py)

# (1) Listar Usuarios:
@users.route('/user/show', methods=['GET'])
@permissions
def showUser():
    return controllerUsers.showUser()

# (2) Obtener Id de Usuario segun Username:
@users.route('/user/sel/id', methods=['POST'])
@permissions
def selUserByUsername():
    return controllerUsers.selectUserByUsername()
