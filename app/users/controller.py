'''
Created by rgomez
@date: 12/04/2018

Referenced file of Source/bots_2_0 project
'''

from flask import render_template, jsonify, redirect, session
from passlib.hash import bcrypt
from app.users.models import UsersModel
from app.commons import get_exception_msg, create_error_msg, create_success_msg
import sqlalchemy
import json
from app import set_log

from flask import json, request

class UsersController(object):
    def __init__(self):
        pass

    def list(self):
        return render_template('user/index.html')

    def listUserAll(self, res):
        try:
            model = UsersModel()
            res = model.userAll()
            return create_success_msg(json.loads(res))
        except sqlalchemy.exc.InternalError, e:
            raise e

    def addUser(self, res):
        try:
            data = json.dumps(res.get_json())
            data = json.loads(data)
            model = UsersModel()
            if data['password'] == data['pass_confirm']:
                data['password'] = bcrypt.hash(data['password'])
                data = [data['username'], data['password'], data['firstname'], data['lastname'], data['email'], 1, 2]
                res = model.userInsert(data)
                res = json.loads(res)
                if res['success'] is True:
                    action="Creacion Nuevo usuario"
                    set_log(action,res)
                    return create_success_msg(res['datos'])
                else:
                    return create_error_msg(res['msg'])
            else:
                raise sqlalchemy.exc.InternalError('Passwords do not match')
        except sqlalchemy.exc.InternalError, e:
            return create_error_msg(str(e)), 403

    def updUser(self, res):
        try:
            data = json.dumps(res.get_json(force=True))
            data = json.loads(data, encoding='utf-8')
            if int(session['id_user']) == data['id_user'] or session['user_data_login']['role'] == 'admin':
                model = UsersModel()
                old_data = model.getUser(data['id_user'])
                old_data = json.loads(old_data, encoding='utf-8')
                if not not old_data:
                    role = 1 if old_data['role'] == 'admin' else 2
                    status = 1 if old_data['status'] == 'active' else 2
                    if role == 2 and status == 2:
                        raise Exception('You do not have permission to modify status')
                    else:
                        if 'password' in data:
                            if data['password'] == data['pass_confirm']:
                                data['password'] = bcrypt.hash(data['password'])
                            else:
                                raise Exception('The password does not match')
                        else:
                            data['password'] = old_data['password']
                        id_mod = int(session['id_user'])
                        data = [data['id_user'], data['username'], data['password'], data['firstname'], data['lastname'],
                                data['email'], role, status,id_mod]
                        new_data = model.userUpdate(data)
                        new_data = json.loads(new_data, encoding='utf-8')
                        if new_data['success'] is True:
                            return create_success_msg(new_data['datos']), 200
                        else:
                            if not not new_data['msg']:
                                raise Exception(new_data['msg'])
                            else:
                                raise Exception('The data update could not be performed')
                else:
                    raise Exception('The selected user was not found')
            else:
                raise Exception('You do not have permission to modify this user')
        except Exception, e:
            return create_error_msg(str(e)), 500

    def suspend_user(self, res):
        try:
            data = json.dumps(res.get_json(force=True))
            data = json.loads(data, encoding='utf-8')
            if session['user_data_login']['role'] == 'admin':
                model = UsersModel()
                old_data = model.getUser(data['id_user'])
                old_data = json.loads(old_data, encoding='utf-8')
                if not not old_data:
                    status = 2 if old_data['status'] == 'active' else 1
                    params = [data['id_user'], status]
                    new_data = model.userSuspend(params)
                    new_data = json.loads(new_data)
                    if new_data['success'] is True:
                        new_data = jsonify(new_data)
                        return new_data, 200
                    else:
                        if not not new_data['msg']:
                            raise Exception(new_data['msg'])
                        else:
                            raise Exception('The data update could not be performed')
                else:
                    raise Exception('The selected user was not found')
            else:
                raise Exception('You do not have permission to modify status')
        except Exception, e:
            return jsonify(create_error_msg(str(e))), 500

    def login(self):
        return render_template("login/index.html")

    def postLogin(self, res):
        try:
            data = json.dumps(res.get_json())
            data = json.loads(data)
            if data['username'] != '' and data['username'] is not None:
                if data['password'] != '' and data['password'] is not None:
                    model = UsersModel()
                    res = model.login(data['username'])
                    res = json.loads(res)
                    if len(res)>2:
                        pass_verify = bcrypt.verify(data['password'], str(res['password']))
                        if pass_verify == True:
                            if not not res or len(res) != 0:
                                if res['status'] == 'active':
                                    session['id_user'] = str(res["id_user"])
                                    session['user_data_login'] = res
                                     #Log Logueo
                                    if res:
                                        #Seteo dict para que data se registre correctamente
                                        res_dict_log={}
                                        res_dict_log["username"]=str(res["username"])
                                        res_dict_log["status"]=str(res["status"])
                                        res_dict_log["first_name"]=str(res["first_name"])
                                        res_dict_log["last_name"]=str(res["last_name"])
                                        res_dict_log["id_user"]=int(res["id_user"])
                                        res_dict_log["role"]=str(res["role"])
                                        res_dict_log["password"]=str(res["password"])
                                        res_dict_log["email"]=str(res["email"])
                                        action="Usuario Inicio Sesion"
                                        set_log(action,res_dict_log)

                                    return jsonify(create_success_msg(res)), 200
                                else:
                                    raise Exception('Suspended user, contact the administrator.')
                            else:
                                raise Exception('User does not exist in the database.')
                        else:
                            raise Exception('Incorrect password.')
                    else:
                        return jsonify(create_error_msg(res['msg'])), 403
                else:

                    raise Exception('Password can\'t be empty.')
            else:
                raise Exception('Username can\'t be empty.')
        except Exception, e:
            return jsonify(create_error_msg(str(e))), 403

    def logOut(self):
        dicc=session["user_data_login"]
        #seteo dict para que data se registre correctamente
        logout_log={}
        logout_log["username"]=str(dicc["username"])
        logout_log["status"]=str(dicc["status"])
        logout_log["first_name"]=str(dicc["first_name"])
        logout_log["last_name"]=str(dicc["last_name"])
        logout_log["id_user"]=int(dicc["id_user"])
        logout_log["role"]=str(dicc["role"])
        logout_log["password"]=str(dicc["password"])
        logout_log["email"]=str(dicc["email"])
        action="Usuario Cerro Sesion"
        set_log(action,logout_log)
        session.pop('id_user', None)
        session.pop('user_data_login', None)
        return redirect("modUser/login")

    # Adaptacion API v1.0
    # Metodos API independientes:
    # Modelo: modelo (models.py)
    def showUser(self):
        try:
            model = UsersModel()
            res = model.Show_User()
            return jsonify(res)
        except sqlalchemy.exc.InternalError as e:
            raise e

    def selectUserByUsername(self):
        try:
            data = request.json
            model = UsersModel()
            res = model.Select_UserByUsername(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError as e:
            raise e

