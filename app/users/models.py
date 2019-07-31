# -*- coding: utf-8 -*-
import json, sqlalchemy,datetime
from flask import session
from app.commons import datetimeconv
from app import app, genericConect, set_log

class UsersModel():

    def userAll(self):
        try:
            list_user = genericConect('sp_bots_user_listar', [])
            json_data = []
            for data in list_user:
                json_data.append({
                    'id_user': data[0],
                    'username': data[3],
                    'name': data[1] + ' ' + data[2],
                    'email': data[4],
                    'status': data[6],
                    'date': data[7]
                })
            return json.dumps(json_data, default=datetimeconv)

        except sqlalchemy.exc.InternalError, e:
            raise e

    def userInsert(self, data):
        try:
            user_add = genericConect('sp_bots_user_insertar', data, False)
            if type(user_add[0]) is int:
                json_result = {
                    'success': True,
                    'datos': {
                        'id_user': user_add[0],
                        'username': user_add[1],
                        'name': user_add[2],
                        'email': user_add[3],
                        'status': user_add[4]
                    }
                }
            else:
                json_result = {
                    'success': False,
                    'msg': user_add[0]
                }
                #Log userInsert
            # if len(user_add) == 5:
            #     action = "Creacion de Nuevo Usuario"
            #     res_store = set_log(action, user_add)

            return json.dumps(json_result)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def userUpdate(self, data):
        try:
            user_update = genericConect('sp_bots_user_modificar', data, False)
            if not not user_update and type(user_update[0]) is int:
                json_result = {
                    'success': True,
                    'datos': {
                        'id_user': user_update[0],
                        'username': user_update[1],
                        'name': user_update[2],
                        'email': user_update[3],
                        'status': user_update[4]
                    }
                }
            else:
                json_result = {
                    'success': False,
                    'msg': user_update[0] if not not user_update else user_update
                }
            return json.dumps(json_result)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def userSuspend(self, data):
        try:
            user_update = genericConect('sp_bots_user_retener', data, False)
            if not not user_update and type(user_update[0]) is int:
                json_result = {
                    'success': True,
                    'datos': {
                        'id_user': user_update[0],
                        'username': user_update[1],
                        'name': user_update[2],
                        'email': user_update[3],
                        'status': user_update[4]
                    }
                }
            else:
                json_result = {
                    'success': False,
                    'msg': user_update[0] if not not user_update else user_update
                }   
            return json.dumps(json_result)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def login(self, name):
        try:
            user_login = genericConect('sp_bots_user_validar', [name], False)
            if len(user_login)>0:
                if type(user_login[0]) is int:
                    json_return = {
                        'id_user': user_login[0],
                        'username': user_login[1],
                        'first_name': user_login[2],
                        'last_name': user_login[3],
                        'email': user_login[4],
                        'role': user_login[5],
                        'status': user_login[6],
                        'password': user_login[7],
                    }
                    return json.dumps(json_return, default=datetimeconv)
                else:
                    data={
                        'success':False,
                        'msg':user_login[0]
                        }
                    return json.dumps(data, default=datetimeconv)
            else:
                data_={
                    'success':False,
                    'msg':'Connection failed, please try again.'
                    }
                return json.dumps(data_, default=datetimeconv)

        except sqlalchemy.exc.InternalError, e:
            raise e

    def getUser(self, id_user):
        try:
            old_data = genericConect('sp_bots_user_obtener', [id_user], False)
            if not not old_data and len(old_data) > 1:
                json_return = {
                    'username': old_data[0],
                    'password': old_data[1],
                    'firstname': old_data[2],
                    'lastname': old_data[3],
                    'email': old_data[4],
                    'role': old_data[5],
                    'status': old_data[6],
                    'created_date': old_data[7],
                    'modified_date': old_data[8],
                }
            else:
                json_return = {
                    'msg': old_data[0] if not not old_data else old_data
                }
            return json.dumps(json_return, default=datetimeconv)
        except sqlalchemy.exc.InternalError, e:
            raise e

    # Adaptacion de Data de Entrada segun el Model
    # @autor avasquez
    # @Date 09/08/2018
    def Show_User(self):
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            resul = genericConect('sp_bots_user_listar', [])
            res = []
            for r in resul:
                dic = dict()
                campos = ['idUser','firstName','lastName','username','email','role','status']
                for idx, val in enumerate(campos):
                    dic[val] = r[idx]
                res.append(dic)
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e

    def Select_UserByUsername(self,data):
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            resul = self.Show_User()['data']
            res = []
            for r in resul:
                res = r if r['username'] == data['username'] else res            
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e