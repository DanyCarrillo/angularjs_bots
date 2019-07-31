import json, sqlalchemy, ast,logging
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine
from flask import session
from decimal import *
from app import app, genericConect, set_BackLogs
from app.commons import decrypt, datetimeconv, create_error_msg, create_success_msg

class pairsModel:
    pass
    def viewPairsModel(self):
        try:
            response = genericConect('sp_bots_pair_listar_all',[])
            all_data=[]
            if response:
                for i in response:
                    data={}
                    data['id_pair']=int(i[0])
                    data['FirstCurrency']=str(i[1])
                    data['SecondCurrency']=str(i[2])
                    data['pair']=str(i[3])
                    data['status_id']=str(i[4])
                    if i[5]>0:
                        data['buy_marketprice']=float(str(i[5]))
                    else:
                        data['buy_marketprice']=0
                    if i[6]>0:
                        data['sell_marketprice']=float(str(i[6]))
                    else:
                        data['sell_marketprice']=0
                    data['created_date']=str(i[7])
                    data['modified_date']=str(i[8])
                    if int(i[9])>0:
                        data['cant_bots']=int(i[9])
                    else:
                        data['cant_bots']=0
                    all_data.append(data)
                response =create_success_msg(all_data)
            else:
                msj = "Exception on sp_bots_pair_listar_all"
                response = create_error_msg(msj)
        except Exception as e:
            response = create_error_msg(e)
        except sqlalchemy.exc.InternalError as e:
            response = create_error_msg(e)
        finally:
            return response

    def suspendPairModel(self, data):
        try:
            data_all=[]
            response_all=[]
            for i in data:
                data_all=[]
                data_all.append(int(i['id_pair']))
                data_all.append(int(i['status_id']))
                data_all.append(int(session['id_user']))
                response = genericConect('sp_bots_pair_modificar',data_all)
                response_all.append(response)
            all_data=[]
            if len(response_all)>0:
                for i in response_all:
                    data_dict={}
                    data_dict['id_pair']=int(i[0][0])
                    data_dict['FirstCurrency']=str(i[0][1])
                    data_dict['SecondCurrency']=str(i[0][2])
                    data_dict['pair']=str(i[0][3])
                    if i[0][4]=='inactive':
                        data_dict['status_id']=2
                    else:
                        data_dict['status_id']=1
                    if i[0][5]>0:
                        data_dict['buy_marketprice']=float(str(i[0][5]))
                    else:
                        data_dict['buy_marketprice']=0
                    if i[0][6]>0:
                        data_dict['sell_marketprice']=float(str(i[0][6]))
                    else:
                        data_dict['sell_marketprice']=0
                    data_dict['created_date']=str(i[0][7])
                    data_dict['modified_date']=str(i[0][8])
                    if int(i[0][9])>0:
                        data_dict['cant_bots']=int(i[0][9])
                    else:
                        data_dict['cant_bots']=0
                    all_data.append(data_dict)
                response =create_success_msg(all_data)

            else:
                msj = "Exception on sp_bots_pair_modificar"
                response = create_error_msg(msj)
                logging.INFO("Exception on sp_bots_pair_modificar.")
        except Exception as e:
            response_err={}
            response_err['mensaje']="No ingreso a stored, revisar parametros."
            response_err['success']=False
            response = response_err
            logging.INFO("Data no ingreso a stored, revisar parametros.")
        except sqlalchemy.exc.InternalError as e:
            response = create_error_msg(e)
        finally:
            return response

    def selectPairTypeCoins(self, data):
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            res_first = genericConect('sp_bots_coins_obtener', [data['firstCurrency']])
            res_second = genericConect('sp_bots_coins_obtener', [data['secondCurrency']])
            type_first = (res_first[0])[2]
            type_second = (res_second[0])[2]

            custom_res['data'] = type_first+'/'+type_second
            custom_res['code'] = 201
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e     