import sqlalchemy, json, ast, re
import json
from flask import jsonify, session
from app import genericConect
from app.commons import (
    encrypt,
    decrypt, 
    datetimeconv, 
    create_error_msg,
    convert_unicode,
    create_success_msg
)

from collections import OrderedDict
import pandas as pd
import numpy as np

class ExchangeModel():

    def exchangeAll(self):
        try:
            list_exchanges = genericConect('sp_bots_exchanges_listar', [])
            json_data = []
            for data in list_exchanges:
                dicc = {
                    'name': data[1],
                    'type': data[2],
                    'status': data[3],
                    'priority': data[4],   
                    'id_exchange': data[0],
                }
                data_combine = getCombine(data[0])

                # Show only if exchange_id was created with user, apilink and pair associatte.
                if data_combine:
                    json_data.append({
                        'general': dicc,
                        'formatsExchange': data_combine['formatsExchange'],
                        'usersExchange': data_combine['usersExchange'],
                        'pairs': data_combine['pairs']
                    })
            return json.dumps(json_data, default=datetimeconv)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def exchangeInsert(self, general, users, formats, pairs):
        json_data = []
        try:
            exchange_add = genericConect(
                'sp_bots_exchanges_insertar',
                general,
                False
            )
            users_exchange = summitDataExchange(
                users,
                exchange_add[0],
                1,
                'sp_bots_user_exchanges_insertar',
                True
            )
            formats_exchange = summitDataExchange(
                formats,
                exchange_add[0],
                0,
                'sp_bots_exchange_formats_insertar',
                False
            )
            pairs_exchange = summitDataExchange(
                pairs,
                exchange_add[0],
                1,
                'sp_bots_pair_exchanges_insertar',
                False
            )

            return json.dumps(json_data, default=datetimeconv)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def exchangeUpdate(self, data, type):
        try:
            store1 = ""
            store2 = ""
            store3 = ""
            # if type = "G":

            # elif type = "U":

            # elif type = "F":

            # else:
                            

            # exchange_add = genericConect('sp_bots_exchange_modificar', [data], False)
            # json_data = []
            
            return "hola"
            # return json.dumps(json_data, default=datetimeconv)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def exchangeSuspend(self, id):
        try:
            exchange_add = genericConect(
                'sp_bots_exchange_retener', 
                [id],
                False
            )
            json_data = []

            return json.dumps(json_data, default=datetimeconv)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def getListPair(self):
        try:
            list_pair = genericConect('sp_bots_pair_listar', [], True)
            json_data = []
            if not not list_pair and not type(list_pair[0]) is int:
                for data in list_pair:
                    json_data.append({
                        'id_pair': data[0],
                        'pair': data[3],
                        'status': data[4]
                    })
            elif not not list_pair and type(list_pair[0]) is int:
                json_data.append({
                    'id_pair': list_pair[0],
                    'pair': list_pair[3],
                    'status': list_pair[4]
                })
            else:
                json_data.append({
                    'success': False,
                    'msg': list_pair[0] if not not list_pair else list_pair
                })

        except sqlalchemy.exc.InternalError, e:
            raise e

        finally:
            return json.dumps(json_data)

    def getPairs(self, id_exchange):
        try:
            lista = []
            store = "sp_bots_pairs_exchanges_listar"
            list_pair = genericConect(store, [id_exchange])
            for pair in list_pair:
                dicc = {}
                dicc["id"] = pair[1]
                dicc["name"] = pair[2]
                lista.append(dicc)

            return lista
        except sqlalchemy.exc.InternalError, e:
            raise e

    def checkBalance(self):
        try:
            store = "sp_bots_verify_account_balance"
            users_ex = genericConect(store, [])
            
            if users_ex:
                data = {}
                exchanges = set()
                users_ex = convert_unicode(users_ex)

                for user in users_ex:
                    exchanges.add((user[0], user[3]))

                for exchange in exchanges:
                    data[exchange] = []
                    for user in users_ex:
                        if user[0] == exchange[0]:
                            data_user = dict(
                                id_user=user[3],
                                username=user[1],
                                pairs=map(lambda x: x.split(","), user[4:]),
                                credentials=ast.literal_eval(decrypt(user[2])),
                            )
                            data[exchange].append(data_user)
                    if not data[exchange]:
                        del data[exchange]

                for data_ex in data.values():
                    for user in data_ex:
                        list_pair = []
                        for pair in user["pairs"][0]:
                            pair = pair.split("/")
                            list_pair += pair
                    data_ex[0]["pairs"] = list(set(list_pair))

                return create_success_msg(data)
            else:
                raise ValueError()
        except ValueError:
            msj = "Error in sp_bots_verify_account_balance"
            return create_error_msg(msj)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def getFormatNames(self):
        try:
            list_formatnames = genericConect('sp_bots_format_names_listar',[],True)
            json_data = []
            for data in list_formatnames:
                dicc = {}
                data_encode = [i.encode('utf-8') for i in data]
                dicc = {
                    'id_format_name' : data_encode[0],
                    'format_name' : data_encode[1]
                }
                json_data.append(dicc)
            return json.dumps(json_data)
        except sqlalchemy.exc.InternalError, e:
            raise e

    # Adaptacion de Data de Entrada segun el Model
    # @autor avasquez
    # @Date 09/08/2018
    def Insert_Exchange(self,data):
        params = []
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            merge, msg = sanitizer(base=params, data=data, types=InsertExchange)
            res = genericConect('sp_bots_exchanges_insertar',merge, False) if merge else '[ERROR] Invalid Parameters'
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201 if msg==True else 400
            if custom_res['code'] == 201 and len(custom_res['data'])>1:
                return custom_res
            else:
                custom_result=dict()
                custom_result['data']=custom_res['data']
                custom_result['success']=False
                return custom_result
        except sqlalchemy.exc.InternalError, e:
            raise e  

    def Update_Exchange(self,data):
        params = []
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            merge, msg = sanitizer(base=params, data=data, types=UpdateExchange)
            res = genericConect('sp_bots_exchanges_modificar',merge, False) if merge else '[ERROR] Invalid Parameters'
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201 if msg==True else 400
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e  

    def Select_Exchange(self,data):
        params = []
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            merge, msg = sanitizer(base=params, data=data, types=SelectExchange)
            res = genericConect('sp_bots_exchanges_obtener',merge, False) if merge else '[ERROR] Invalid Parameters'
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201 if msg==True else 400
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e  

    def Delete_Exchange(self,data):
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            lst_input = [data['idExchange'],data['status']] 
            resul = genericConect('sp_bots_exchanges_retener', lst_input, False)
            if isinstance(resul[0],unicode):
                res = [resul[0]]
            else:
                res = []
                campos = ['idExchange','name','type','priority','status']    
                dic = dict()
                i=0
                for c in campos:
                    dic[c] = resul[i]
                    i=i+1
                res.append(dic)
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e 

    def Show_Exchange(self):
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            res = genericConect('sp_bots_exchanges_listar', [])
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e

    def View_Exchange(self,data):
        params = []
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            merge, msg = sanitizer(base=params, data=data, types=ViewExchange)
            res = genericConect('sp_bots_listar_combine', merge, True) if merge else '[ERROR] Invalid Parameters'
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201 if msg==True else 400
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e            

    def View_AllExchange(self):
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            campos = ['idExchange','name','type','priority','status','idFormatExchange','format','url','datatype','params','method','status','idUserExchange','username','credentials','status','idPairUserExchange','pair','idPair','maxTradeAmount','status']
            resul = genericConect('sp_bots_integration_exchange_listar', [])

            # -- Pandas - DataScience: --

            # Convertir tupla en array numpy:
            np_resul = np.asarray(resul)

            # DataFrame a partir del Diccionario integrador:
            df = pd.DataFrame(np_resul,columns=campos)

            # Especificando tipos de variables:
            df['idExchange'] = df.idExchange.astype(int)
            df['idFormatExchange'] = df.idFormatExchange.astype(int)
            df['idUserExchange'] = df.idUserExchange.astype(int)
            df['idPairUserExchange'] = df.idPairUserExchange.astype(int)
            df['idPair'] = df.idPair.astype(int)
            df['maxTradeAmount'] = df.maxTradeAmount.astype(float)
            df['priority'] = df.priority.astype(int)
            df['status'] = df.status.astype(int)

            # Auxiliares de concatenacion:
            id_exchanges = df.iloc[:,0]
            id_users = df.iloc[:,12]

            # Exchange - General:
            cols_general = (df.iloc[:,0:5]).drop_duplicates()

            # Exchange - Formatos:
            formats = df.iloc[:,5:12]
            cols_formats = (pd.concat([id_exchanges,formats],axis=1,join='inner')).drop_duplicates()

            # Exchange - Usuarios:
            users = df.iloc[:,12:16]
            cols_users = (pd.concat([id_exchanges, users],axis=1,join='inner')).drop_duplicates()

            # Exchange - Pares:
            pairs = df.iloc[:,16:21]
            cols_pairs = (pd.concat([id_users, pairs],axis=1,join='inner')).drop_duplicates()

            # Constructor de diccionario:
            res = []
            dic_general = cols_general.to_dict('records')
            for i,g in enumerate(cols_general['idExchange'].tolist()):
                dic = dict()
                dic['general'] = dic_general[i]
                dic['formats'] = (cols_formats.loc[cols_formats['idExchange']==g]).to_dict('records')
                for x,f in enumerate(dic['formats']):
                    f['reference'] = x
                dic['users'] = (cols_users.loc[cols_users['idExchange']==g]).to_dict('records')
                for j,u in enumerate(dic['users']):
                    dic['users'][j]['pairs'] = (cols_pairs.loc[cols_pairs['idUserExchange']==u['idUserExchange']]).to_dict('records')
                    dic['users'][j]['credentials'] = self.string2decrypt(dic['users'][j]['credentials']) 
                res.append(dic)

            custom_res['data'] = res
            custom_res['code'] = 201
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e        

    def string2decrypt(self,cadena):
        dic = dict()
        dic['secret'] = ''
        dic['key'] = ''
        if cadena:
            aux = re.split(r"[:,]+",decrypt(cadena))
            dic['secret'] = ((aux[1].replace("'","")).replace('"','')).strip() if len(aux)>=2 else "Not Found"
            dic['key'] = ((aux[3].replace("'","")).replace('"','')).replace("}","").strip() if len(aux)>=4 else "Not Found"
        return dic

    def Insert_UserExchange(self,data):
        params = []
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            data['status'] = 1
            merge, msg = sanitizer(base=params, data=data, types=InsertUserExchange)
            res = genericConect('sp_bots_user_exchanges_insertar', merge, False) if merge else '[ERROR] Invalid Parameters'
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201 if msg==True else 400
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e            

    def Update_UserExchange(self,data):
        params = []
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            merge, msg = sanitizer(base=params, data=data, types=UpdateUserExchange)
            res = genericConect('sp_bots_user_exchanges_modificar', merge, False) if merge else '[ERROR] Invalid Parameters'
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201 if msg==True else 400
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e               

    def Select_UserExchange(self,data):
        params = []
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            merge, msg = sanitizer(base=params, data=data, types=SelectUserExchange)
            resul = genericConect('sp_bots_listar_combine', merge, True) if merge else '[ERROR] Invalid Parameters'
            res = []
            for r in resul:
                if r[0] == "UE":
                    res.append(r)
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201 if msg==True else 400
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e          

    def Insert_PairUserExchange(self,data):
        params = []
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            merge, msg = sanitizer(base=params, data=data, types=InsertPairUserExchange)
            res = genericConect('sp_bots_pairs_user_exchanges_insertar', merge, True) if merge else '[ERROR] Invalid Parameters'
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201 if msg==True else 400
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e          

    def Update_PairUserExchange(self,data):
        params = []
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            merge, msg = sanitizer(base=params, data=data, types=UpdatePairUserExchange)
            res = genericConect('sp_bots_pairs_user_exchanges_modificar', merge, True) if merge else '[ERROR] Invalid Parameters'
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201 if msg==True else 400
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e                      

    def Select_PairUserExchange(self,data):
        params = []
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            merge, msg = sanitizer(base=params, data=data, types=SelectPairUserExchange)
            res = []
            resul = genericConect('sp_bots_listar_combine', [merge[0]], True) if merge else '[ERROR] Invalid Parameters'
            for r in resul:
                if r[0] == "PUE":   # Filtrar solo por idExchange
                    if merge[1] == 0:
                        res.append(r)
                    else:           # Filtrar por idExchange y idUserExchange
                        if r[2] == merge[1]:
                            res.append(r)
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201 if msg==True else 400
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e 

    def Insert_FormatExchange(self,data):
        params = []
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            data['status'] = 1
            merge, msg = sanitizer(base=params, data=data, types=InsertFormatExchange)
            res = genericConect('sp_bots_exchange_formats_insertar', merge, True) if merge else '[ERROR] Invalid Parameters'
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201 if msg==True else 400
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e          

    def Update_FormatExchange(self,data):
        params = []
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            merge, msg = sanitizer(base=params, data=data, types=UpdateFormatExchange)
            res = genericConect('sp_bots_exchange_formats_modificar', merge, True) if merge else '[ERROR] Invalid Parameters'
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201 if msg==True else 400
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e          

    def Select_FormatExchange(self,data):
        params = []
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            merge, msg = sanitizer(base=params, data=data, types=SelectFormatExchange)
            res = []
            resul = genericConect('sp_bots_listar_combine', merge, True) if merge else '[ERROR] Invalid Parameters'
            for r in resul:
                if r[0] == "EF": 
                    res.append(r)
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201 if msg==True else 400
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e 

    def Select_FormatExchangeByStatus(self,data):
        params = []
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            merge, msg = sanitizer(base=params, data=data, types=SelectFormatExchangeByStatus)
            res = []
            resul = genericConect('sp_bots_exchange_formats_obtener', [merge[1]], True) if merge else '[ERROR] Invalid Parameters'
            res = [ m for m in resul if m[0]==merge[0] and m[7]==merge[2] ]
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201 if msg==True else 400
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e 

    def Show_FormatExchange(self):
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            res = genericConect('sp_bots_format_names_listar', [])
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e 

    def Show_Pair(self):
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            res = genericConect('sp_bots_pair_listar', [])
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e 

    def Select_Pair(self,data):
        params = []
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            merge, msg = sanitizer(base=params, data=data, types=SelectPair)
            res = genericConect('sp_bots_pair_obtener', merge, False) if merge else '[ERROR] Invalid Parameters'
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201 if msg==True else 400
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e

    def Select_PairPorNombre(self,data):
        params = []
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            merge, msg = sanitizer(base=params, data=data, types=SelectPairPorNombre)
            idPair = 0
            res_pairs = self.Show_Pair()
            for pair in res_pairs['data']:
                idPair = pair[0] if (pair[3]==merge[0]) else idPair
            custom_res['data'] = idPair
            custom_res['code'] = 201
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e

    def Insert_ExchangeUsersApilinks(self,data):
        params = []
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        custom_res_all=[]
        general = data['general']
        users = data['users']
        formats = data['apilinks']
        exchange_name=[{'name':'Bitstamp','idExchange':2},{'name':'Binance','idExchange':4},{'name':'Okex','idExchange':5},{'name':'Huobi','idExchange':6}]

        try:
            # Add Exchange:
            if len(formats)<1:
                for i in exchange_name:
                    if int(data['general']['idExchange'])==int(i['idExchange']):
                        # Update Exchange:
                        general_=[]
                        general_.append(int(data['general']['idExchange']))
                        general_.append(str(data['general']['name']))
                        general_.append(str(data['general']['type']))
                        general_.append(int(data['general']['status']))
                        general_.append(int(data['general']['priority']))
                        general_.append(int(data['general']['idModifyUser']))

                        res_general = genericConect('sp_bots_exchanges_modificar',general_, False)

                        idExchange = res_general[0]
                        flag_internal = True if idExchange=='Intern type exchange alredy exists' else False
                        flag_duplic = True if idExchange=='Exchange alredy exists' else False
            else: 
                #Add Other Exchange

                res_general = self.Insert_Exchange(general)
                idExchange = res_general['data'][0]
                flag_internal = True if idExchange=='Intern type exchange alredy exists' else False
                flag_duplic = True if idExchange=='Exchange alredy exists' else False

            if flag_internal==True or flag_duplic==True:
                custom_res_all = [flag_duplic,flag_internal]
            else:
                # Add Users:
                for user in users:
                    userexchange = {}
                    userexchange['idExchange'] = idExchange
                    userexchange['username'] = user['username']
                    userexchange['credentials'] = encrypt(json.dumps(user['credentials'],ensure_ascii=False).encode('utf-8'))
                    userexchange['status'] = user['status']
                    res_user = self.Insert_UserExchange(userexchange)
                    idUserExchange = res_user['data'][0]

                    # Add Pairs:
                    for pair in user['pairs']:
                        pairuser = {}
                        pairuser['idPair'] = pair['idPair']
                        pairuser['idUserExchange'] = idUserExchange
                        pairuser['maxTradeAmount'] = float(pair['maxTradeAmount'])
                        res_pair = self.Insert_PairUserExchange(pairuser)
                        idPairUser = res_pair['data'][0]

                # Add Apilinks:
                if len(formats)!=0:
                    for formatexchange in formats:
                        formatexchange['idExchange'] = idExchange
                        res_format = self.Insert_FormatExchange(formatexchange)
                        idFormatExchange = res_format['data'][0]

                if len(formats)>0:
                    custom_res_all.append(res_general)
                    custom_res_all.append(res_user)
                    custom_res_all.append(res_pair)
                    custom_res_all.append(res_format)
                else:
                    custom_res_all.append(res_general)
                    custom_res_all.append(res_user)
                    custom_res_all.append(res_pair)

            custom_res['data'] = custom_res_all
            custom_res['code'] = 201
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e 

    def Update_ExchangeUsersApilinks(self,data):
        params = []
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200

        general = data['general']
        users = data['users']
        formats = data['apilinks']

        try:
            # Update Exchange:
            res_general = self.Update_Exchange(general)
            idExchange = res_general['data'][0]
            flag_internal = True if idExchange=='Intern Exchange type alredy exists' else False
            flag_duplic = True if idExchange=='Exchange alredy exists' else False

            if flag_internal==True or flag_duplic==True:
                custom_res_all = [flag_duplic,flag_internal]
            else:
                # Update Users & Pairs:
                idModifyUser = 0
                for userexchange in users:
                    userexchange['idExchange'] = idExchange
                    userexchange['credentials'] = encrypt(json.dumps(userexchange['credentials'],ensure_ascii=False).encode('utf-8'))
                    idModifyUser = userexchange['idModifyUser'] if 'idUserExchange' in userexchange else 0
                    res_user = self.Update_UserExchange(userexchange) if 'idUserExchange' in userexchange else self.Insert_UserExchange(userexchange)

                    # Update pairs:
                    pairs = userexchange['pairs']
                    for pair in pairs:
                        pair['idUserExchange'] = res_user['data'][0]
                        pair['maxTradeAmount'] = float(pair['maxTradeAmount'])
                        res_pair = self.Update_PairUserExchange(pair)

                ids_usr_bd = [ ux[1] for ux in self.Select_UserExchange({"idExchange":idExchange})['data'] if self.Select_UserExchange({"idExchange":idExchange})['data']!='[WARNING] Data empty from store procedure' ]
                ids_usr_send = [ ux['idUserExchange'] for ux in users if 'idUserExchange' in ux ]

                for id_u_del in set(ids_usr_bd)^set(ids_usr_send):
                    users_to_deleted = [sam for sam  in self.Select_UserExchange({'idExchange':idExchange})['data'] if sam[1]==id_u_del]            
                    for aux in users_to_deleted:
                        usrexch = dict()
                        campos = ['status','idExchange','idModifyUser','username','credentials','idUserExchange']
                        values = [2,idExchange,idModifyUser,aux[3],aux[4],aux[1]]
                        for index,c in enumerate(campos):
                            usrexch[c] = values[index]
                        res_user_deleted = self.Update_UserExchange(usrexch)

                # Update Apilinks:
                idModifyUser = 0
                for formatexchange in formats:                      # For Insert New Apilinks added / Update Apilinks created
                    formatexchange['idExchange'] = idExchange
                    idModifyUser = formatexchange['idModifyUser'] if 'idFormatExchange' in formatexchange else 0
                    res_format = self.Update_FormatExchange(formatexchange) if 'idFormatExchange' in formatexchange else self.Insert_FormatExchange(formatexchange)

                ids_frm_bd = [ fx[1] for fx in self.Select_FormatExchange({"idExchange":idExchange})['data'] if self.Select_FormatExchange({"idExchange":idExchange})['data']!='[WARNING] Data empty from store procedure' ]
                ids_frm_send = [ fx['idFormatExchange'] for fx in formats if 'idFormatExchange' in fx]
                for id_f_del in set(ids_frm_bd)^set(ids_frm_send):  # For Delete Apilinks created
                    formats_to_deleted = [sam for sam in self.Select_FormatExchange({"idExchange":idExchange})['data'] if sam[1]==id_f_del] 
                    for aux in formats_to_deleted:
                        frmexch = dict()
                        campos = ['status','idExchange','idModifyUser','format','datatype','idFormatExchange','url','params','method']
                        values = [2,idExchange,idModifyUser,aux[3],aux[6],aux[1],aux[4],aux[7],aux[5]]
                        for index,c in enumerate(campos):
                            frmexch[c] = values[index]
                        res_format_deleted = self.Update_FormatExchange(frmexch)

                custom_res_all=[]
                custom_res_all.append(res_general)
                custom_res_all.append(res_user)
                custom_res_all.append(res_format)
            return custom_res_all
        except sqlalchemy.exc.InternalError, e:
            raise e 

    def Verify_ExchangeBitinka(self):
        params = []
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            exchanges = self.Show_Exchange()['data']
            if exchanges != '[WARNING] Data empty from store procedure':
                verify_bitinka = -1
                for exch in exchanges:
                    verify_bitinka = exch[0] if exch[1]=='Bitinka' else verify_bitinka
                custom_res['code'] = 201
                custom_res['data'] = verify_bitinka
            else:
                custom_res['code'] = 201
                custom_res['data'] = '[WARNING] Data empty from store procedure'
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e        


# Adaptacion de Data de Entrada segun el Model
# @autor avasquez
# @Date 09/08/2018
def sanitizer(base=None, data=None, types=object):
    for k,v in types.OD.items():
        for i in data:
            if k==i:
                data[i] = data[i].encode('utf-8') if isinstance(data[i],unicode) else data[i]
                if type(v) is not type(data[i]):
                    return k, "Parameter '{}' Invalid data type".format(k)
                else:
                    base.append(data[i])
    return base, True


def getCombine(id_exchange):
    data_pair = {}
    data_error = {}
    data_users = {}
    data_formats = {}
    data_combine = {}
    try:
        combine_result = genericConect('sp_bots_listar_combine', [id_exchange], True)
        for combine in combine_result:
            if combine[0] == 'UE':
                data_users['id_user'] = combine[1]
                data_users['username'] = combine[3]
                data_users['credentials'] = decrypt(combine[4])
            elif combine[0] == 'EF':
                data_formats['url'] = combine[4]
                data_formats['method'] = combine[5]
                data_formats['params'] = combine[7]
                data_formats['id_format'] = combine[1]
                data_formats['data_type'] = combine[6]
                data_formats['format_name'] = combine[3]
            elif combine[0] == 'PE':
                data_pair['pair'] = combine[4]
                data_pair['id_pair'] = combine[1]
                data_pair['id_pair_exchange'] = combine[2]
            else:
                data_error = combine[0]

        if data_users or data_formats or data_pair:
            data_combine['usersExchange'] = data_users if data_users else ''
            data_combine['formatsExchange'] = data_formats if data_formats else ''
            data_combine['pairs'] = data_pair if data_pair else ''
        else:
            data_combine = data_error

        return data_combine
    except sqlalchemy.exc.InternalError, e:
        raise e


def summitDataExchange(datas, exchange_id, position, store, status=True):
    result_data = []
    for data in datas:
        data_encode = [i.encode('utf-8') for i in data]
        data_encode.insert(position, exchange_id)
        if status is True:
            data_encode.append(1)
        dataReturn = genericConect(store, data_encode, False)
        result_data.append(dataReturn)
    return result_data


# Adaptacion API v1.0
# Metodos API independientes:
# Modelo: exchanges_controler (controller.py)
class InsertExchange(object):
    OD = OrderedDict()
    OD['name'] = str()
    OD['type'] = str()
    OD['status'] = int()
    OD['priority'] = int()  # [0-127]

class UpdateExchange(object):
    OD = OrderedDict()
    OD['idExchange'] = int()
    OD['name'] = str()
    OD['type'] = str()      
    OD['status'] = int()
    OD['priority'] = int()  # [0-127]
    OD['idModifyUser'] = int() 

class SelectExchange(object):
    OD = OrderedDict()
    OD['idExchange'] = int()

class DeleteExchange(object):
    OD = OrderedDict()
    OD['idExchange'] = int()

class ViewExchange(object):
    OD = OrderedDict()
    OD['idExchange'] = int()

class InsertUserExchange(object):
    OD = OrderedDict()
    OD['username'] = str()
    OD['idExchange'] = int()
    OD['credentials'] = str()   
    OD['status'] = int()

class UpdateUserExchange(object):      
    OD = OrderedDict()
    OD['idUserExchange'] = int()
    OD['username'] = str()
    OD['idExchange'] = int()
    OD['credentials'] = str()  
    OD['status'] = int()
    OD['idModifyUser'] = int()

class DeleteUserExchange(object):
    OD = OrderedDict()
    OD['idUserExchange'] = int()
    OD['username'] = str()
    OD['idExchange'] = int()
    OD['credentials'] = str()
    OD['status'] = int()
    OD['idModifyUser'] = int()

class SelectUserExchange(object):
    OD = OrderedDict()
    OD['idExchange'] = int()

class InsertPairUserExchange(object):
    OD = OrderedDict()
    OD['idPair'] = int()
    OD['idUserExchange'] = int()
    OD['maxTradeAmount'] = float()  

class UpdatePairUserExchange(object):    
    OD = OrderedDict()
    OD['idPair'] = int()
    OD['idUserExchange'] = int()
    OD['maxTradeAmount'] = float()  
    OD['status'] = int()

class SelectPairUserExchange(object):
    OD = OrderedDict()
    OD['idExchange'] = int()
    OD['idUserExchange'] = int()

class InsertFormatExchange(object):
    OD = OrderedDict()
    OD['idExchange'] = int()
    OD['format'] = str()
    OD['url'] = str()
    OD['method'] = str()
    OD['datatype'] = str()
    OD['params'] = str()
    OD['status'] = int()

class UpdateFormatExchange(object):    
    OD = OrderedDict()
    OD['idFormatExchange'] = int()
    OD['idExchange'] = int()
    OD['format'] = str()
    OD['url'] = str()
    OD['method'] = str()
    OD['datatype'] = str()
    OD['params'] = str()
    OD['status'] = int()
    OD['idModifyUser'] = int()

class SelectFormatExchange(object):
    OD = OrderedDict()
    OD['idExchange'] = int()

class SelectFormatExchangeByStatus(object):
    OD = OrderedDict()
    OD['idFormatExchange'] = int()
    OD['format'] = str()
    OD['status'] = str()

class SelectPair(object):
    OD = OrderedDict()
    OD['idPair'] = int()

class SelectPairPorNombre(object):
    OD = OrderedDict()
    OD['pair'] = str()