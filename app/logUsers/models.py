import json, sqlalchemy, ast
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine
from flask import session
import pdb
from app import  app, genericConect, set_BackLogs
from app.commons import decrypt, datetimeconv, create_error_msg, create_success_msg

from flask import jsonify

class LogUsersModel:
    def getUserLogs(self):
        try:
            response = genericConect('sp_UsersLogs_Listar',[int(session['id_user'])]) 
            all_data=[]
            lista=[]
            lista2=[]
            if response:
                for i in response:
                    data={
                        'id_user_logs':int(i[0]),
                        'username':str(i[1]),
                        'id_table':int(i[2]),
                        'stored_proc':str(i[3]),
                        'description':i[4].replace("'",'"'),
                        'created_date':str(i[5])
                    }
                    all_data.append(data)
                response =create_success_msg(all_data)
            else:
                msj = "Exception on sp_UsersLogs_Listar"
                response = create_error_msg(msj)
        except Exception as e:
            response = create_error_msg(e)
        except sqlalchemy.exc.InternalError as e:
            response = create_error_msg(e)
        finally:
            return response
