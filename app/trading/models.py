import json, sqlalchemy, ast, requests
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine
from flask import session
from app import app, genericConect, set_BackLogs
from app.commons import (
    decrypt,
    datetimeconv, 
    create_error_msg,
    create_success_msg
)

from app.exchanges.models import ExchangeModel
from app.coins.models import CoinModel

class TradingModel:

    def getApis_model(self, type='', relate=''):
        try:
            list_apis = genericConect('sp_bots_coin_api_link_listar', [type, relate], True)
            json_data = []
            for apis in list_apis:
                json_data.append({
                    'coin': apis[1],
                    'type_coin': apis[2],
                    'link': apis[3],
                    'method': apis[4],
                    'data_type': apis[5],
                    'params': apis[6],
                    'coordinates': apis[7],
                    'coin_relate': apis[8]
                })
            return json.dumps(json_data, default=datetimeconv)
        except sqlalchemy.exc.InternalError as e:
            raise e

    def getApisPairs_model(self, flag, id_pair):
        s1 = "sp_bots_api_link_play_intern"
        s2 = "sp_bots_api_link_play_extern"
        store = s1 if flag == "I" else s2
        try:
            list_apis = genericConect(store, [id_pair], True)
            json_data = []
            if list_apis:
                for apis in list_apis:
                    json_data.append({
                        'pair': apis[0],
                        'link': apis[1],
                        'method': apis[2],
                        'data_type': apis[3],
                        'params': apis[4],
                        'format_name_id': apis[5],
                        'exchange_id': apis[6],
                        'exchange_name': apis[7],
                        'priority': apis[8],
                        'max_trade_amount': apis[9],
                        'case': apis[10]
                    })
            else:
                json_data.append({False})
            return json.dumps(json_data, default=datetimeconv)
        except sqlalchemy.exc.InternalError, e:
            error_cod=111
            modulo='Trading-Model'
            description='Error conexion con BD:function-getApisPairs_model'
            set_BackLogs(error_cod,modulo,description)

    def getMarketPrice(self, id_pair):
        try:
            list_prices = genericConect(
                'sp_bots_crypto_prices_listar', 
                [id_pair], 
                True
            )
            json_data = []
            if list_prices is not None:
                for price in list_prices:
                    if len(price) > 3:
                        name_pair=price[2]
                        curs = name_pair.split('/')
                        json_data = dict(
                            pair=price[2],
                            firstCurrency=curs[0],
                            secondCurrency=curs[1],
                            status=price[6],
                            type_calc=price[5],
                            created_date=price[8],
                            modified_date=price[9],
                            id_crypto_prices=price[0],
                            buy_marketprice=float(price[3]),
                            sell_marketprice=float(price[4]),
                        )
                        data = json.dumps(json_data, default=datetimeconv)
                        return create_success_msg(data)
                    else:
                        msj = "No exists in pairs table or is inactive."
                        return create_error_msg(msj)
            else:
                raise ValueError(404)
        except ValueError:
            msj = "Exception on sp_bots_crypto_prices_listar"
            return create_error_msg(msj)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def addCriptoPrice(self, data):
        try:
            response = genericConect('sp_bots_crypto_price_insertar', data, False)
            return True if response else False
        except sqlalchemy.exc.InternalError, e:
            raise e

    def getPairsCoins(self, coin=''):
        try:
            list_pairs = genericConect('sp_bots_coins_play', [coin], True)
            json_data = []
            if list_pairs:
                for pair in list_pairs:
                    json_data.append({
                        'id_pair': pair[0],
                        'firstcurrency': pair[1],
                        'secondcurrency': pair[2],
                        'pair': pair[3],
                        'type_coin': pair[5]
                    })
            return json.dumps(json_data, default=datetimeconv)
        except sqlalchemy.exc.InternalError as e:
            raise e

    def updateConvertValues(self, data):
        try:
            response = genericConect('sp_bots_coins_update', data, False)
            if response:
                result = True
            else:
                result = False

            return result
        except sqlalchemy.exc.InternalError, e:
            raise e

    def getCoin(self, coin):
        try:
            old_data = genericConect('sp_bots_coins_obtener', [coin], False)
            if not not old_data and len(old_data) > 1:
                json_return = {
                    'id_coin': old_data[0],
                    'name': old_data[1],
                    'type': old_data[2],
                    'buy_convertion': old_data[3],
                    'sell_convertion': old_data[4],
                    'status': old_data[5],
                    'created_date': old_data[6],
                    'modified_date': old_data[7],
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
    def getTypesTrading(self):
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            resul = genericConect('sp_bots_trading_types_listar', [])
            res = []
            for r in resul:
                dic = dict()
                dic['idTradingType'] = r[0]
                dic['name'] = r[1]
                dic['type'] = r[2]
                dic['status'] = r[3]
                res.append(dic)
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201
            return custom_res
        except sqlalchemy.exc.InternalError as e:
            raise e

    def getOrderBookFormats(self):
        try:
            ob = genericConect('sp_bots_ob_api_listar', [], False)
            json_result = {
                'format_name_id': ob[0],
                'url': ob[1],
                'method': ob[2],
                'data_type': ob[3],
                'params': ob[4],
                'type_exchange': ob[5],
                'exchange_id': ob[6],
                'exchange_name': ob[7]
            }
            return json.dumps(json_result)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def getOrderData(self, pair_id, type):
        try:
            ob_list = genericConect('sp_bots_check_order_id', [pair_id, type], False)
            json_result = False
            if not ob_list is None:
                if ob_list[0] is not None and ob_list[0] != 'False':
                    json_result = {
                        'firstCurrency': ob_list[0],
                        'secondCurrency': ob_list[1],
                        'username': ob_list[2],
                        'credentials': decrypt(ob_list[3]),
                        'format_name': ob_list[4],
                        'url': ob_list[5],
                        'method': ob_list[6],
                        'data_type': ob_list[7],
                        'params': ob_list[8],
                        'exchange_name': ob_list[9],
                        'exchange_id': ob_list[10],
                        'price': ob_list[11]
                    }
                else:
                    json_result = False
            return json.dumps(json_result, default=datetimeconv)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def checkOrderData(self, order_id):
        try:
            ob_list = genericConect('sp_bots_play_log_listar', [order_id], False)
            json_result = False
            if not ob_list is None:
                if ob_list[0] is not None and ob_list[0] != 'False':
                    json_result = {
                        'order_id': ob_list[0],
                        'exchange_name': ob_list[1],
                        'exchange_id': ob_list[2]
                    }
                else:
                    json_result = False
            return json.dumps(json_result)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def checkPriceOrder(self, price, order_id):
        try:
            check = genericConect('sp_bots_check_price', [float(price), int(order_id)], False)
            return True if check[0] == 'TRUE' else False
        except sqlalchemy.exc.InternalError, e:
            raise e

    def saveCompleteResponse(self, data):
        try:
            save = genericConect('sp_bots_complete_order_response_crud', data, False)
            if isinstance(save, tuple,):
                order_save = {
                    'id_complete_order': save[0],
                    'exchange_id': save[1],
                    'amount': save[2],
                    'price': save[3],
                    'type': save[4],
                    'response': save[5],
                    'order_id': save[6],
                    'created_date': save[7],
                    'status': save[8],
                    'modified_date': save[9],
                }
            else:
                order_save = 'Order not saving'
            return json.dumps(order_save, default=datetimeconv)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def getCompleteOrders(self):
        try:
            save = genericConect('sp_bots_complete_order_response_listar', [], True)
            if len(save) > 0:
                data = []
                for order in save:
                    data.append({
                        'id_complete_order': order[0],
                        'exchange_id': order[1],
                        'amount': order[2],
                        'price': order[3],
                        'type': order[4],
                        'response': order[5],
                        'order_id': order[6],
                        'created_date': order[7],
                        'pair_id': order[8],
                        'pair': order[9],
                        'status': order[10]
                    })
            else:
                data = 'empty'
            return json.dumps(data, default=datetimeconv)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def getformat(self, id_format):
        try:
            response = genericConect('sp_bots_exchange_formats_obtener', [id_format])
            if response:
                data = dict(
                    url=response[0][3],
                    method=response[0][4],
                    params=response[0][6],
                    data_type=response[0][5],
                )
                response = create_success_msg(data)
            else:
                msj = "Exception on sp_bots_ob_api_listar"
                response = create_error_msg(msj)
        except Exception as e:
            response = create_error_msg(e)
        except sqlalchemy.exc.InternalError as e:
            response = create_error_msg(e)
        finally:
            return response       

    def getUserPlay(self, id_play):
        try:
            res = genericConect('sp_bots_depth_combine', [id_play])
            if res:
                data = None
                for row in res:
                    if row[0] == "UE":
                        data = dict(credentials=decrypt(row[3]))
                if data:
                    response = create_success_msg(data)
                else:
                    raise ValueError(404)
            else:
                raise ValueError(404)
        except ValueError:
            msj = "Exception on sp_bots_depth_combine"
            response = create_error_msg(msj)
        except sqlalchemy.exc.InternalError as e:
            response = create_error_msg(e)
        finally:
            return response 

    def Show_ActiveOrdersByBot(self, data):
        custom_res = dict()
        custom_res['data'] = ""
        custom_res['code'] = 200
        trading = TradingModel()
        try:
            # Obtencion de Orders Activas:
            if data['idBotType'] != 'D':
                custom_res['code'] = 202
                custom_res['data'] = 'Data doesn\'t available for Bot Type different to Depth'
            else:
                res_user_exchange = trading.getUserPlay(data['idBot'])
                res_format_exchange = trading.getformat("AO")

                if res_user_exchange['success']==True and res_format_exchange['success']==True:

                    # Obtener el Link (segun Exchange Bitinka):
                    url_orders = res_format_exchange['datos']['url'] 

                    # Pair:
                    pair = str(data['pair']).split("/")
                    firstCurrency = pair[0]
                    secondCurrency = pair[1]

                    # Obtener las credenciales:
                    credentials = json.loads(res_user_exchange['datos']['credentials']) 
                    key = credentials['key']
                    secret = credentials['secret'] 

                    # Trade:
                    trade = 1

                    # Obtener las Ordenes Activas
                    post = dict()
                    post['key'] = key 
                    post['secret'] = secret 
                    post['trade'] = trade
                    post['firstCurrency'] = firstCurrency
                    post['secondCurrency'] = secondCurrency

                    session= requests.Session()
                    session.trust_env = False
                    r = session.post(url=url_orders, data=post) 

                    if isinstance(json.loads(r.content),dict):
                        custom_res['code'] = 203
                        custom_res['data'] = json.loads(r.content)
                    else:
                        r_contenido = dict()
                        r_contenido['idBot'] = data['idBot']
                        r_contenido['key'] = key
                        r_contenido['secret'] = secret
                        r_contenido['history'] = json.loads(r.content)

                        custom_res['code'] = 201
                        custom_res['data'] = [r_contenido]
                
                else:
                    custom_res['code'] = 203
                    custom_res['data'] = str(res_format_exchange)

            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e

    def Show_ActiveOrdersByUserYPair(self, data):
        custom_res = dict()
        custom_res['data'] = ""
        custom_res['code'] = 200
        trading = TradingModel()
        exchange = ExchangeModel()
        try:
            # Obtencion de Orders Activas:
            ruexch = exchange.Select_UserExchange({'idExchange':1})
            ruexch_s = ([ r for r in ruexch['data'] if r[3]==data['usernameExchange'] ])[0]

            res_user_exchange = exchange.string2decrypt(ruexch_s[4])
            res_format_exchange = trading.getformat("AO")

            if len(res_user_exchange)==2 and res_format_exchange['success']==True:

                # Obtener el Link (segun Exchange Bitinka):
                url_orders = res_format_exchange['datos']['url'] 

                # Pair:
                pair = str(data['pair']).split("/")
                firstCurrency = pair[0]
                secondCurrency = pair[1]

                # Obtener las credenciales:
                credentials = res_user_exchange
                key = credentials['key']
                secret = credentials['secret'] 

                # Trade:
                trade = 1

                # Obtener las Ordenes Activas
                post = dict()
                post['key'] = key 
                post['secret'] = secret 
                post['trade'] = trade
                post['firstCurrency'] = firstCurrency
                post['secondCurrency'] = secondCurrency

                session= requests.Session()
                session.trust_env = False
                r = session.post(url=url_orders, data=post) 

                if isinstance(json.loads(r.content),dict):
                    custom_res['code'] = 203
                    custom_res['data'] = json.loads(r.content)
                else:
                    r_contenido = dict()
                    r_contenido['key'] = key
                    r_contenido['secret'] = secret
                    r_contenido['history'] = json.loads(r.content)

                    custom_res['code'] = 201
                    custom_res['data'] = [r_contenido]
                
            else:
                custom_res['code'] = 203
                custom_res['data'] = str(res_format_exchange)

            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e

    def orderApis_model(self, data):
        try:
            response = False
            data_ordered = dict()
            for api in data:
                if(data_ordered.has_key(api['coin']) is False):
                    data_ordered[api['coin']]  = []  
                data_ordered[api['coin']].append(api)
            response = data_ordered
        except Exception as e:
            print "ERROR: orderApis_model"
            print e
            response = False
        finally:
            return response


    def proApiReference(self, api, coin):
        try:
            modelCoin = CoinModel()
            data = []
            getcoin = modelCoin.getCoin('BTC')
            if getcoin != False:
                buyconvertusd = float(getcoin[3])
                sellconvertusd = float(getcoin[4])
            else:
                raise NameError("BTC NOT FOUND") 

            for link in api:
                res = self.proLinkReference(link)
                if len(res) == 3 and res.has_key('coin') and res.has_key('buy') and res.has_key('sell') and res['buy'] > 0 and res['sell'] > 0:
                    if link['coin_relate'] == 'BTC':
                        if link['type_coin'] == 'C':
                            res['buy'] = res['buy']*buyconvertusd
                            res['sell'] = res['sell']*sellconvertusd
                        elif link['type_coin'] == 'F':
                            res['buy'] = res['buy']/buyconvertusd
                            res['sell'] = res['sell']/sellconvertusd

                    data.append(res)
                else:
                    error_cod = 140
                    modulo = 'Trading-model'
                    description = 'link no cumple con campos solicitados:function-proApiReference'
                    set_BackLogs(error_cod, modulo, description)
        except Exception as e:
            print e
            error_cod = 140
            modulo = 'Trading-model'
            description = 'Exception on proApiReference to %s - %s' %(coin, str(e))
            set_BackLogs(error_cod, modulo, description)
        finally:
            return data

    def proLinkReference(self, api):
        try:
            result = {
                'coin': api['coin'],
                'buy': 0,
                'sell': 0
            }
            values = self.getApiData(api)
            result['buy'] = float(values['buy'])
            result['sell'] = float(values['sell'])
        except Exception, e:
            error_cod = 140
            modulo = 'Trading-model'
            description = 'Exception on proLinkReference for %s on %s - %s' %(links['coin'], links['coin_relate'], str(e))
            set_BackLogs(error_cod, modulo, description)
        finally:
            return result

    def getApiData(self, links):
        try:
            result = {
                'buy': 0,
                'sell': 0
            }
            if links['method'] == 'GET':
                if links['params'] != '':
                    links['link'] = links['link'] + links['params']
                data = requests.get(links["link"])
                links["coordinates"] = eval(links["coordinates"])
                if links["coordinates"]:
                    for key in links["coordinates"]:
                        if data.status_code == 200:
                            val = data.json()
                            for cor in links["coordinates"][key]:
                                val = val[cor]
                                if type(val) != 'dict':
                                    if key == 'buy':
                                        result['buy'] = val
                                    else:
                                        result['sell'] = val
                                else:
                                    raise NameError("Error result is not dict") 
                        else:
                            raise NameError("estatus_code: %s" % (data.status_code)) 
                else:
                    raise NameError('No coordinates')  
            else:
                if links['data_type'] == 'JSON':
                    data_send = str(links['params'])
                endPoint = links['link']
                data = requests.post(endPoint, data=data_send)
                links["coordinates"] = eval(links["coordinates"])
                if links["coordinates"]:
                    for key in links["coordinates"]:
                        if data['success'] is True:
                            val = data.json()
                            for cor in links["coordinates"][key]:
                                val = val[cor]
                                if type(val) != 'dict':
                                    if key == 'buy':
                                        result['buy'] = val
                                    else:
                                        result['sell'] = val
                                else:
                                    raise NameError("Error result is not dict")
                        else:
                            raise NameError("estatus_code: %s" % (data.status_code)) 
                else:
                    raise NameError('No coordinates') 
        except Exception, e:
            error_cod = 140
            modulo = 'Trading-model'
            description = 'Exception on getApiData for %s on %s - %s' %(links['coin'], links['coin_relate'], str(e))
            set_BackLogs(error_cod, modulo, description)
        finally:
            return result



def verify_account_balance_():
    try:
        lista = []
        store = "sp_bots_complete_order_response_listar"
        credentials = genericConect(store, [])
        dicc = dict()
        for cred in credentials:
            lista.append(cred[3])
        return lista
    except sqlalchemy.exc.InternalError, e:
        raise e
        