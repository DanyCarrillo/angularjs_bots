from __future__ import division
from celery import shared_task
from flask import jsonify, request, json
import sqlalchemy, json, requests, ast, logging
from app import r, set_BackLogs, app, celery
from app.trading.models import TradingModel
from app.plays.models import PlayModel
from app.bots.models import BotModel
from datetime import datetime, date, timedelta
from app.external_exchange.conections import (
    getOrderbook,
    createOrder,
    getExchangeMarketPrice
)
from app.commons import (
    create_success_msg,
    create_error_msg,
    request_post_url,
    convert_unicode
)

from app.exchanges.models import ExchangeModel
from app.coins.models import CoinModel

class TradingController(object):

    def __init__(self):
        pass

    def listCriptoPrice(self):
        data = {
            'data': {},
            'error': False,
            'success': True
        }
        try:
            last_redis_update = r.hget('last_save', 0)
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if eval_time(current_date, last_redis_update):
                cripto_prices = r.hgetall('cripto_prices')
                if not not cripto_prices:
                    for key in cripto_prices:
                        price = json.loads(cripto_prices[key])
                        last_price_date = datetime.strptime(price['created_date'], "%Y-%m-%d %H:%M:%S")
                        diff_redis_pair = datetime.combine(date.today(), current_date.time()) - datetime.combine(
                            date.today(),
                            last_price_date.time())
                        if diff_redis_pair.seconds <= int(app.config['MARKET_PRICE_TIME']):
                            price['pair'] = price['pair'].replace('/', '_')
                            redis_data = {price['pair']: {'price_market_buy': price['buy_marketprice'],
                                                          'price_market_sell': price['sell_marketprice']}}
                            data['data'] = dict(data['data'].items() + redis_data.items())
                        else:
                            r.hdel('cripto_prices', key)
                else:
                    data['data'] = getPriceDB()
            else:
                error_cod = 111
                modulo = 'Trading-controller'
                description = 'Conexion fallida con redis:function-listCriptoPrice'
                set_BackLogs(error_cod, modulo, description)
                data['data'] = getPriceDB()
            if not data['data']:
                data = {
                    'success': False,
                    'error': True,
                    'data': 'Error updating prices'
                }
        except Exception, e:
            data = create_error_msg(str(e))
        finally:
            return jsonify(data)

    def getPairMarketPrice(self, pair):
        data = {
            'data': {},
            'error': True,
            'success': False
        }
        model = TradingModel()
        try:
            pairs_list = json.loads(model.getPairsCoins())
            for pairs in pairs_list:
                if pairs['pair'] == pair.replace('_', '/'):
                    pair_id = pairs['id_pair']
            marketPrice = self.getMarketPrice(pair_id)
            if marketPrice is not False:
                del marketPrice['id_crypto_prices']
                del marketPrice['type_calc']
                del marketPrice['status']
                marketPrice['pair'] = marketPrice['pair'].replace('/', '_')
                data['data'] = marketPrice
                data['error'] = False
                data['success'] = True
            else:
                data['msg'] = 'Price is not updated'
        except Exception, e:
            raise e
        finally:
            return jsonify(data)

    def getTypesTrading(self):
        try:
            model = TradingModel()
            res = model.getTypesTrading()
            return jsonify(res)
        except sqlalchemy.exc.InternalError as e:
            raise e

    def selectMarketPricesExchange(self):
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            data = request.json
            now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            last_load = r.hget('last_save', data['idPair'])
            if eval_time(now_time, last_load):
                resul = r.hget('cripto_prices', data['idPair'])
                if resul:
                    json_res = json.loads(resul)

                    res = []
                    dic = dict()
                    dic['idCryptoPrice'] = 0
                    dic['idPair'] = data['idPair']
                    dic['pair'] = json_res['pair']
                    dic['buyMarketPrice'] = "%.8f" % float(json_res['buy_marketprice'])
                    dic['sellMarketPrice'] = "%.8f" % float(json_res['sell_marketprice'])
                    dic['typeCalcule'] = "--------"
                    dic['status'] = "------"
                    dic['idExchange'] = json_res['exchange_id']
                    dic['createdDate'] = json_res['created_date']
                    dic['modifiedDate'] = "--/--/--"
                    res.append(dic)

                    custom_res['data'] = res
                    custom_res['code'] = 201
                    logging.info("Price found with Redis.")
                else:
                    custom_res['data'] = 'Price don\'t found with Redis '
                    custom_res['code'] = 201
            else:
                model = BotModel()
                res = model.Select_CryptoPricesPair(data)
                custom_res = res

            return jsonify(custom_res)
        except sqlalchemy.exc.InternalError as e:
            raise e

    def Show_ActiveOrdersByPair(self):
        custom_res = dict()
        custom_res['data'] = ""
        custom_res['code'] = 200

        try:
            # Obtener el Link (segun Exchange Bitinka) para obtener las Ordenes Activas:
            trading = TradingModel()
            res_format_exchange = trading.getformat("AO")

            # Listar Bots Play y Bots Configuration
            play = PlayModel()
            res_bots_play = json.loads(play.listPlays("active"))

            # Pair:
            data = str(request.json['pair']).split("/")
            
            # Obtencion de Orders Activas:
            if res_format_exchange['success'] == True:
                historial = []
                for rplay in res_bots_play:

                    if rplay['botConfiguration']['bot_type_id'] == 'D':
                        credentials = json.loads(trading.getUserPlay(rplay['bots_configuration_id'])['datos']['credentials'])
                        post = dict()
                        post['key'] = credentials['key'] #"59ZJA87O-DQXNXF9M-OH8ZVC50-I266Z854-I4OTDVIQ"
                        post['secret'] = credentials['secret'] #"mfdjvn6j4ejzrp09s6grflvyqkr3f9u1p7llvr5z6ozxdz756nxl9sjzcb2slxua" #credentials['secret']
                        post['trade'] = 1
                        post['firstCurrency'] = data[0]
                        post['secondCurrency'] = data[1]
                        url_orders = res_format_exchange['datos']['url']

                        r = requests.post(url=url_orders, data=post)  

                        if isinstance(json.loads(r.content),dict):
                            historial.append(json.loads(r.content))
                        else:
                            r_contenido = dict(json.loads(r.content)[0]) 
                            r_contenido['idBot'] = rplay['bots_configuration_id']
                            r_contenido['key'] = credentials['key']
                            r_contenido['secret'] = credentials['secret']
                            historial.append({'Order':r_contenido})
                
                custom_res['data'] = historial
            
            return jsonify(custom_res)
        except sqlalchemy.exc.InternalError as e:
            raise e        

    def Show_ActiveOrdersByBot(self):
        try:
            data = request.json
            model = TradingModel()
            res = model.Show_ActiveOrdersByBot(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError as e:
            raise e    

    def Send_OrdersToCancel(self):
        custom_res = dict()
        custom_res['data'] = ""
        custom_res['code'] = 200
        trading = TradingModel()
        exchange = ExchangeModel()
        data = request.json
        try: 

            # Obtencion de Orders Canceladas:
            res_format_exchange = trading.getformat("CO")

            # Validacion de Format Exchange:
            if res_format_exchange['success'] == True:
                if res_format_exchange['datos']['method'] == "POST":

                    # Link para Cancelar Ordenes:
                    url_orders = res_format_exchange['datos']['url']

                    # Obtener las credenciales:
                    if 'idBot' in data:
                        credentials = json.loads((trading.getUserPlay(data['idBot']))['datos']['credentials'])
                    else:
                        ruexch = exchange.Select_UserExchange({'idExchange':1})
                        ruexch_s = ([ r for r in ruexch['data'] if r[3]==data['usernameExchange'] ])[0]
                        res_user_exchange = exchange.string2decrypt(ruexch_s[4])
                        credentials = res_user_exchange

                    key = credentials['key'] 
                    secret = credentials['secret'] 

                    # Trade:
                    trade = 1   

                    # Send Request - Cancel Order:
                    r_status = ""
                    r_content = ""
                    str_orders = ""
                    for id_order in data['idOrders']:
                        str_orders = str_orders + str(id_order) + ','

                    curs = data['pair'].split('/')

                    post = dict()
                    post['idOrders'] =  str_orders[:-1]
                    post['firstCurrency'] = curs[0]
                    post['secondCurrency'] = curs[1]

                    session = requests.Session()
                    r = session.post(url=url_orders, data=json.dumps(post),headers={'content-type':'application/json'}) 
                    
                    custom_res['code'] = str(r.status_code)
                    custom_res['data'] = str(r.content)
            else:
                custom_res['code'] = 203
                custom_res['data'] = create_error_msg(res_format_exchange)

            return jsonify(custom_res)
        except sqlalchemy.exc.InternalError as e:
            raise e  

    def getMarketPrice(self, id_pair):
        try:
            now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = r.hget('cripto_prices', id_pair)

            if data:
                data = json.loads(data)
                if eval_time(now_time, data["created_date"]):
                    logging.info("Price found with Redis.")
                    return data
                 
            model = TradingModel()
            response = model.getMarketPrice(id_pair)
            if response["success"] == True:
                response = model.getMarketPrice(id_pair)
                response = json.loads(response["datos"])
                if eval_time(now_time, response['modified_date']):
                    logging.info("Price found with Model.")
                    return response
                else:
                    return False
            else:
                logging.info(response["mensaje"])
                return None
        except sqlalchemy.exc.InternalError, e:
            raise e

    def getMarketPrice_attempt(self, id_pair):
        try:
            now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Redis:
            data = r.hget('cripto_prices', id_pair)
            if data:
                data = json.loads(data)
                #if eval_time(now_time, data["created_date"]):
                logging.info("Price found with Redis.")
                return data
                 
            # Local:
            model = TradingModel()
            response = model.getMarketPrice(id_pair)
            if response["success"] == True:
                response = model.getMarketPrice(id_pair)
                response = json.loads(response["datos"])
                #if eval_time(now_time, response['created_date']):
                logging.info("Price found with Model.")
                return response
                #else:
                #    return False
            else:
                logging.info(response["mensaje"])
                return None
        except sqlalchemy.exc.InternalError, e:
            raise e

    def getPriceLink(self, res):
        try:
            id_pair = res.get_json()

            model = TradingModel()
            links = model.getApisPairs_model('I', id_pair)
            links = json.loads(links)

            if checkList(links):
                lista = []
                for link in links[:3]:
                    if link:
                        url_basic = link["link"].split('//')[1].split('/')[0]
                        res = model.getApiData(link)
                        prom = sum(res.values()) / 2
                        lista.append({
                            "link": url_basic,
                            "price": prom
                        })
                    else:
                        lista.append({
                            "link": "",
                            "price": ""
                        })

                return lista
            else:
                logging.info('Function getPriceLink not found links.')
        except sqlalchemy.exc.InternalError, e:
            raise e

    def doOldProcess(self, pair):
        try:
            result = False
            model = TradingModel()
            links = model.getApisPairs_model('I', pair['id_pair'])
            links = json.loads(links)
            sum_buy = 0
            sum_sell = 0
            if links[0] != None:
                count = 0
                for link in links:
                    link['coordinates'] = link['priority']
                    res_apiLink = model.getApiData(link)
                    valid_buy = res_apiLink['buy'] if validPrices(res_apiLink['buy']) else False
                    valid_sell = res_apiLink['sell'] if validPrices(res_apiLink['sell']) else False
                    if link['case'] == 'DIRECT':
                        if valid_buy and valid_sell:
                            sum_buy += float(valid_buy)
                            sum_sell += float(valid_sell)
                            count += 1
                    elif link['case'] == 'CONVERT':
                        if valid_buy and valid_sell:
                            convertPrice = convertProcess(
                                valid_buy, 
                                valid_sell,
                                pair
                            )
                            sum_buy += float(convertPrice['buy'])
                            sum_sell += float(convertPrice['sell'])
                            count += 1

                buy = sum_buy / count
                sell = sum_sell / count
                result = {'buy': buy, 'sell': sell, 'type_calc': str(link['case']) + '-OLD', 'exchange_id': link['exchange_id']}
            elif links[0] is None:
                convertPrice = convertProcess(0, 0, pair, True)
                result = {'buy': float(convertPrice['buy']), 'sell': float(convertPrice['sell']), 'type_calc': 'RE-CONVERT', 'exchange_id': 0}
                error_cod = 300
                modulo = 'Trading-controller'
                description = 'Not links returned:Re-convert process used '
                set_BackLogs(error_cod, modulo, description)
        except Exception, e:
            raise e
            result = False
        finally:
            return result

    def updMarketPrice(self):
        try:
            model = TradingModel()
            res = json.loads(model.getPairsCoins())
            app.config['COUNT_MARKET'] = 1 if app.config['COUNT_MARKET'] == 0 else 0
            if app.config['COUNT_MARKET'] == 1:
                res = reversed(res)
                
            for pair in res:
                updateMarketPrice.apply_async(
                    args=[pair],
                    queue="feed_tasks", 
                    routing_key='feed.import'
                )
        except Exception as e:
            error_cod = 121
            modulo = 'Trading-controller'
            description = 'Exception: updMarketPrice %s' + str(e)
            set_BackLogs(error_cod, modulo, description)
            logging.info("Exception: updMarketPrice %s" % (str(e)))
        finally:
            return True

    def convertPrices(self):
        try:
            response = 'Error convertPrices'
            model = TradingModel()
            res = model.getApis_model('', '')
            res = json.loads(res)
            if res:
                orderapilink = model.orderApis_model(res)
                count = 0
                try:
                    for coin in orderapilink:
                        updatePriceConvertByCoin.apply_async(
                            args=[orderapilink[coin], coin],
                            queue="others", 
                            routing_key='others.import'
                        )
                        count = count + 1
                except Exception as e:
                    logging.info("Exception: convertPrices %s" % (str(e)))
                finally:
                    response = 'convertPrices sent to updatePriceConvertByCoin: %d' %(count)
            else:
                response = 'Error convertPrices getting apilink'
        except Exception as e:
            error_cod = 131
            modulo = 'Trading-controller'
            description = 'No actualizo promedio fiatPrice: function-cronPrice ' + str(e)
            response = description
            set_BackLogs(error_cod, modulo, description)
        finally:
            return response


    def getExchangesOrders(self, links, pair):
        result = {
            'buy': 0,
            'sell': 0
        }
        buy_count = 0
        sell_count = 0
        buy_total = 0
        sell_total = 0
        sum_priceB = 0
        sum_priceS = 0
        try:
            if links['params'] is not None:
                for key in pair:
                    if pair[key] == 'USD':
                        if links['exchange_name'] == 'Binance' or links['exchange_name'] == 'Okex' or links[
                            'exchange_name'] == 'Huobi':
                            pair[key] += 't'
                    links['params'] = links['params'].replace(key.upper(), str(pair[key]))                
                exchange_market_price = getExchangeMarketPrice(links['exchange_name'], links['params'])
                if isinstance(exchange_market_price, dict, ):                    
                    result['buy']=exchange_market_price['bid']
                    result['sell'] = exchange_market_price['ask']  
                    if result['sell'] == 0 or result['buy'] == 0:
                        result['buy'] = 0
                        result['sell'] = 0
                else:
                    result['buy'] = 0
                    result['sell'] = 0
        except Exception, e:
            result['buy'] = 0
            result['sell'] = 0
        finally:
            return result

    def saveOrderTrade(self, request):
        model = TradingModel()
        try:
            idData = json.loads(model.checkOrderData(request['order_id']))
            request['amount_completed'] = float(request['amount_completed'])
            if isinstance(idData, dict, ):
                data = {
                    'price': request['price'],
                    'amount': request['amount_completed'],
                    'type': 'sell' if request['type'] == 'buy' else 'buy',
                    'order_id': request['order_id']
                }
                dataSave = [0, idData['exchange_id'], float(data['amount']), float(data['price']), data['type'],
                            'Save the order, waiting for the batch to be completed',
                            data['order_id'], 4]
                data = json.loads(model.saveCompleteResponse(dataSave))
                if isinstance(data, dict, ):
                    response = create_success_msg(data)
                else:
                    error_cod = 1234
                    modulo = 'Trading-controller'
                    description = 'Error saving order: {}'.format(data)
                    set_BackLogs(error_cod, modulo, description)
                    response = create_error_msg(data)
            else:
                error_cod = 1235
                modulo = 'Trading-controller'
                description = 'Error complete order: Invalid order id'
                set_BackLogs(error_cod, modulo, description)
                response = create_error_msg('Invalid order id')
        except Exception, e:
            error_cod = 1236
            modulo = 'Trading-controller'
            description = 'Error saving order: {}'.format(str(e))
            set_BackLogs(error_cod, modulo, description)
            response = str(e)
            raise e
        finally:
            return response

    def completeOrder(self):
        model = TradingModel()
        request = {}
        try:
            completeOrder = getCompleteOrder()
            for type in completeOrder:
                if type is 'buyOrders':
                    request['type'] = 'buy'
                else:
                    request['type'] = 'sell'
                for pair in completeOrder[type]:
                    request['amount_completed'] = completeOrder[type][pair]['totalAmount']
                    request['pair_id'] = completeOrder[type][pair]['pair_id']
                    if request['amount_completed'] >= 0.01:
                        response = doCompleteOrder(request)
                        for order in completeOrder[type][pair]['orders']:
                            if 'success' in response:
                                dataSave = [order['id_complete_order'], order['exchange_id'], float(order['amount']), float(order['price']),
                                            order['type'],
                                            str(response['data']),
                                            order['order_id'], 5]
                            else:
                                dataSave = [order['id_complete_order'], order['exchange_id'], float(order['amount']), float(order['price']),
                                            order['type'],
                                            str(response['data']),
                                            order['order_id'], 4]
                            data = json.loads(model.saveCompleteResponse(dataSave))
                            if isinstance(data, dict, ):
                                print "Updated"
                            else:
                                error_cod = 500
                                modulo = 'Trading-controller'
                                description = 'Error updating order: {}'.format(data)
                                set_BackLogs(error_cod, modulo, description)
                    else:
                        error_cod = 1341
                        modulo = 'Trading-controller'
                        description = 'Error complete order: Amount to complete is to low in Type {}'.format(type)
                        set_BackLogs(error_cod, modulo, description)
        except Exception, e:
            error_cod = 123
            modulo = 'Trading-controller'
            description = 'Error complete order: ' + str(e)
            set_BackLogs(error_cod, modulo, description)
        finally:
            return True

    def cancelOrders(self, type_cancel):
        try:
            result = False
            mod_trad = TradingModel()
            mod_play = PlayModel()
            con_trad = TradingController()
            res = mod_trad.getformat("AO")
            dat_plays = json.loads(mod_play.listPlays("active"))
            if res['success']:
                res["datos"].update({"params":{"trade":1}})
                if isinstance(dat_plays,list):
                    list_del = []
                    for play in dat_plays:
                        info = {}
                        info[0]=[]
                        try:
                            if play.has_key("id_bots_play"):
                                info[play["id_bots_play"]] = False
                                if play['botConfiguration']['bot_type_id'] == 'D':
                                    data = dict(
                                        id_pair = play["botConfiguration"]["pair_id"],
                                        firstCurrency=play["botConfiguration"]["firstcurrency"],
                                        secondCurrency=play["botConfiguration"]["secondcurrency"],
                                        id_bots_play = play["id_bots_play"],
                                        bots_configuration_id=play["bots_configuration_id"],
                                        res=res,
                                        cancelBuy= play['botConfiguration']["cancel_buy"],
                                        cancelSell = play['botConfiguration']["cancel_sell"],
                                        type=type_cancel
                                        )
                                    killOrders.apply_async(
                                        args=[data],
                                        queue="killcancel", 
                                        routing_key='killcancel.import'
                                    )
                                    info[play["id_bots_play"]] = True
                            else:
                               info[0].append(play["id_bots_play"])
                        except Exception as e:
                            info[play["id_bots_play"]] = str(e)
                        finally:
                            list_del.append(info)
                    result = list_del
                else:
                    result = "Task Error: cancelOrders not found listPlays active"
            else:
                result = "Task Error: cancelOrders not found Format AO"
        except Exception as e:
            result =  str(e)
        finally:
            return result

def selectMarketPricesExchange_attempt(data):
    market_prices = None
    model = BotModel()
    try:
        now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_load = r.hget('last_save', data['idPair'])
        if eval_time(now_time, last_load):
            externo = r.hget('cripto_prices', data['idPair'])
            if externo:
                externo = json.loads(externo)
                market_prices = dict(
                    buy = externo['buy_marketprice'],
                    sell = externo['sell_marketprice']
                )
                logging.info("Price found with Redis.")
            else:
                market_prices = None
                logging.info('Price don\'t found with Redis ')
        else:
            bitinka = model.Select_CryptoPricesPair(data)
            if bitinka:
                market_prices = dict(
                    buy = float(bitinka['data'][0]['buyMarketPrice']),
                    sell = float(bitinka['data'][0]['sellMarketPrice'])
                )
                logging.info('Price found with Internal Exchange')   
            else:
                market_prices = None
                logging.info('Price don\'t found with Internal Exchange')   

        return market_prices
    except sqlalchemy.exc.InternalError as e:
        raise e

def selectMarketPricesExchange_hz(data):
    params = []
    custom_res = dict()
    try:
        exchange = ExchangeModel()
        formatos = (exchange.Select_FormatExchange({'idExchange':1}))['data']
        url = [f[4] for f in formatos if f[3]=='BB']
        url_orderbook = url[0]
        response = requests.post(url=url_orderbook,data=json.dumps(data),headers={'Content-Type': 'application/json'})
        res = json.loads(response.text)

        # Compra:
        if 'status' in res['BUY']:
            custom_res['buy'] = 0
        else:
            custom_res['buy'] = res['SELL'][0]['Price']

        # Venta:
        if 'status' in res['SELL']:
            custom_res['sell'] = 0
        else:
            custom_res['sell'] = res['BUY'][0]['Price']

        return custom_res
    except sqlalchemy.exc.InternalError as e:
        raise e

def dataRequest(user=None, formats_result=None, pair=None):
    if formats_result['method'] == 'GET':
        if formats_result['params'] != '':
            endPoint = formats_result['url'] + formats_result['params']
        response = requests.get(endPoint)
    else:
        user_credentials = ast.literal_eval(user['credentials'])
        if type(formats_result['params']) == str:
            params = ast.literal_eval(formats_result['params'])
        else:
            params = formats_result['params']
        data = dict(params.items() + user_credentials.items())
        if pair:
            data.update(pair.items())
        if formats_result['data_type'] == 'JSON':
            data = json.dumps(data)
        endPoint = formats_result['url']
        response = request_post_url(endPoint, data)
    if response.status_code == 200:
        response = response.json()
        result = convert_unicode(response)
        result = create_success_msg(result)
    else:
        response = response.status_code
        msj = "Error on request %s" %(response)
        result = create_error_msg(msj)
    return result


def convertProcess(buy_api, sell_api, pair, reconvert=False):
    model = TradingModel()
    if reconvert is False:
        convert_coin = model.getCoin(pair['secondcurrency'])
        convert_coin = json.loads(convert_coin)
        if convert_coin['type'] == 'C':
            buy = float(buy_api) / float(convert_coin['buy_convertion'])
            sell = float(sell_api) / float(convert_coin['sell_convertion'])
        else:
            buy = float(buy_api) * float(convert_coin['buy_convertion'])
            sell = float(sell_api) * float(convert_coin['sell_convertion'])
    else:
        firstcurrency_data = model.getCoin(pair['firstcurrency'])
        secondcurrency_data = model.getCoin(pair['secondcurrency'])
        firstcurrency_data = json.loads(firstcurrency_data)
        secondcurrency_data = json.loads(secondcurrency_data)
        if secondcurrency_data['type'] == 'C':
            buy = float(firstcurrency_data['buy_convertion']) / float(secondcurrency_data['buy_convertion'])
            sell = float(firstcurrency_data['sell_convertion']) / float(secondcurrency_data['sell_convertion'])
        else:
            buy = float(firstcurrency_data['buy_convertion']) * float(secondcurrency_data['buy_convertion'])
            sell = float(firstcurrency_data['sell_convertion']) * float(secondcurrency_data['sell_convertion'])
    return {'buy': float('{0:.8f}'.format(buy)), 'sell': float('{0:.8f}'.format(sell))}


def getPriceDB():
    model = TradingModel()
    data = {}
    list_prices = model.getMarketPrice(0)
    list_prices = json.loads(list_prices)
    current_date = datetime.now()
    for prices in list_prices:
        prices['pair'] = prices['pair'].replace('/', '_')
        last_update = datetime.strptime(prices['created_date'], "%Y-%m-%d %H:%M:%S")
        diff = datetime.combine(date.today(), current_date.time()) - datetime.combine(date.today(),
                                                                                      last_update.time())
        price_db = {prices['pair']: {'price_market_buy': prices['buy_marketprice'],
                                     'price_market_sell': prices['sell_marketprice']}}
        if (current_date.date() == last_update.date()) and diff.seconds <= int(app.config['MARKET_PRICE_TIME']):
            data = dict(data.items() + price_db.items())
    return data


def eval_time(new_time, old_time):
    if new_time and old_time:
        lista = [new_time, old_time]
        all_data = []

        for row in lista:
            pos = row.find(" ")
            all_data.append(row[:pos])
            all_data.append(row[pos + 1:])

        if (all_data[0] == all_data[2]):
            val1 = datetime.strptime(all_data[1], '%H:%M:%S')
            val2 = datetime.strptime(all_data[3], '%H:%M:%S')
            res = val1 - val2
            point = timedelta(seconds=int(app.config['MARKET_PRICE_TIME']))
            if res < point:
                return True
    return False


def checkList(lista):
    if lista:
        if lista[0] != None:
            return True
    return False


def validateOrderId(order_id, price):
    try:
        if r.hexists('filterOrders', order_id):
            price_order = r.hget('filterOrders', order_id)
            if price == price_order:
                result = True
            else:
                result = False
        else:
            result = False
    except Exception, e:
        raise e
    finally:
        return result


def findOrderBit(formats, idData, request):
    result = False
    for key in idData:
        formats['params'] = formats['params'].replace(key.upper(), str(idData[key]))
    response = dataRequest(formats_result=formats)
    level = 'purchases' if request['type'] == 'buy' else 'sales'
    if level in response["datos"]['orders']:
        for values in response['orders'][level][idData['secondCurrency']]:
            checkPrice = checkPriceOrder(values['Price'], request['order_id'])
            if checkPrice is False:
                amountToSend = request['amount_completed'] if float(request['amount_completed']) <= float(values['Amount']) else values['Amount']
                if level == 'purchases':
                    if float(values['Price']) <= float(request['price']) and float(
                            request['amount_completed']) <= float(values['Amount']):
                        if result is False or float(result['price']) >= float(values['Price']):
                            result = {
                                'type': 'sell',
                                'amount': float(amountToSend),
                                'price': values['Price'],
                                'firstCurrency': idData['firstCurrency'],
                                'secondCurrency': idData['secondCurrency'],
                                'trade': 2
                            }
                    else:
                        result = False if result is False else result
                else:
                    if float(values['Price']) >= float(request['price']) and float(
                            request['amount_completed']) <= float(values['Amount']):
                        if result is False or float(result['price']) >= float(values['Price']):
                            result = {
                                'type': 'buy',
                                'amount': round((float(amountToSend) * float(values['Price'])), 8),
                                'price': values['Price'],
                                'firstCurrency': idData['firstCurrency'],
                                'secondCurrency': idData['secondCurrency'],
                                'trade': 2
                            }
                    else:
                        result = False if result is False else result
            else:
                result = False if result is False else result
    else:
        result = False
    return result


def checkPriceOrder(Price, order_id):
    model = TradingModel()
    return model.checkPriceOrder(Price, order_id)


def doCompleteTransaction(order, data):
    if order is not False:
        for key in order:
            data['params'] = data['params'].replace(key.upper(), str(order[key]))
        send_user = {'username': data['username'], 'credentials': data['credentials']}
        send_formats = {'url': data['url'], 'method': data['method'], 'data_type': data['data_type'],
                        'params': data['params']}
        response = dataRequest(send_user, send_formats)
        response = response["datos"]
    else:
        response = False
    return response


def getCompleteOrder():
    model = TradingModel()
    completeOrders = json.loads(model.getCompleteOrders())
    data = {
        'buyOrders': {},
        'sellOrders': {}
    }
    for order in completeOrders:
        if order['type'] == 'buy':
            if not order['pair'] in data['buyOrders']:
                data['buyOrders'][order['pair']] = {
                    'totalAmount': order['amount'],
                    'pair_id': order['pair_id'],
                    'orders': [order]
                }
            else:
                data['buyOrders'][order['pair']]['totalAmount'] += order['amount']
                data['buyOrders'][order['pair']]['orders'].append(order)
        else:
            if not order['pair'] in data['sellOrders']:
                data['sellOrders'][order['pair']] = {
                    'totalAmount': order['amount'],
                    'pair_id': order['pair_id'],
                    'orders': [order]
                }
            else:
                data['sellOrders'][order['pair']]['totalAmount'] += order['amount']
                data['sellOrders'][order['pair']]['orders'].append(order)
    return data


def dispatchOrderEx(idData, data):
    for key in data:
        idData['params'] = idData['params'].replace(key.upper(), str(data[key]))
    send_data = dict(json.loads(idData['credentials']).items() + json.loads(idData['params']).items())
    send_data['username'] = idData['username']
    response = createOrder(idData['exchange_name'], convert_unicode(send_data), send_data['type'])
    return response


def doCompleteOrder(request):
    model = TradingModel()
    order_type = 'S' if request['type'] == 'sell' else 'B'
    idData = json.loads(model.getOrderData(request['pair_id'], order_type))
    request['amount_completed'] = float(request['amount_completed'])
    complete = False
    if isinstance(idData, dict, ):
        data = {
            'amount': request['amount_completed'],
            'type': 'sell' if order_type == 'S' else 'buy',
            'firstcurrency': idData['firstCurrency'],
            'secondcurrency': idData['secondCurrency'],
            'price': idData['price']
        }
        dispatch = dispatchOrderEx(idData, data)
        if isinstance(dispatch, dict,):
            complete = {
                'success': True,
                'data': dispatch
            }
        else:
            error_cod = 500
            modulo = 'Trading-controller'
            description = 'Error complete order: Cant create the order' + str(dispatch)
            set_BackLogs(error_cod, modulo, description)
            complete = {
                'error': True,
                'data': str(dispatch)
            }
    else:
        error_cod = 124
        modulo = 'Trading-controller'
        description = 'Error complete order: Invalid order id'
        set_BackLogs(error_cod, modulo, description)

    return complete


def validPrices(data):
    values = ["", 0, 0.0]
    for val in values:
        result = False if val == data else True
        if not result:
            break
    return result

@celery.task(name="addCriptoPrice", queue="savebd", acks_late=False)
def addCriptoPrice(data):
    model = TradingModel()
    success = False
    try:
        model.addCriptoPrice(data)
        success = True
    except Exception, e:
        error_cod = 500
        modulo = 'Trading-controller'
        description = 'Saving prices: data: ' + str(data)
        set_BackLogs(error_cod, modulo, description)
        logging.info("Exception: addCriptoPrice %s" %(e.message))
        success = False
    finally:
        return success


@celery.task(name="updateMarketPrice", queue="feed_tasks")
def updateMarketPrice(pair):
    try:
        model = TradingModel()
        links = model.getApisPairs_model('E', pair['id_pair'])
        links = json.loads(links)
        trading_c = TradingController()
        criptoPrice = None 
        if links[0] != None:
            buy = 0
            sell = 0
            for link in links:
                link = convert_unicode(link)
                if link['format_name_id'] == 'OB':
                    pair_get = link['pair'].split('/')
                    pair_get = {'firstcurrency': pair_get[0], 'secondcurrency': pair_get[1]}
                    res_apiLink = trading_c.getExchangesOrders(link, pair_get)
                    if res_apiLink['sell'] and res_apiLink['buy'] != 0:
                        if res_apiLink is not False:
                            if link['case'] == 'DIRECT':
                                buy = float(res_apiLink['buy'])
                                sell = float(res_apiLink['sell'])
                                exchange_id = link['exchange_id']
                                break
                            elif link['case'] == 'CONVERT':
                                convertPrice = convertProcess(res_apiLink['buy'], res_apiLink['sell'],pair)
                                buy = float(convertPrice['buy'])
                                sell = float(convertPrice['sell'])
                                exchange_id = link['exchange_id']
                                break
            if sell == 0 and buy == 0:
                oldPriceProcess = trading_c.doOldProcess(pair)
                if oldPriceProcess is not False:
                    criptoPrice = {
                        'id_pair': pair['id_pair'], 
                        'buy_marketprice': oldPriceProcess['buy'],
                        'sell_marketprice': oldPriceProcess['sell'], 
                        'type_calc': 'COINS_CONVERT',
                        'exchange_id': oldPriceProcess['exchange_id']
                    }
            else:
                criptoPrice = {
                    'id_pair': pair['id_pair'], 
                    'buy_marketprice': buy,
                    'sell_marketprice': sell, 
                    'type_calc': link['case'], 
                    'exchange_id': exchange_id
                }
        elif links[0] == None:
            oldPriceProcess = trading_c.doOldProcess(pair)
            if oldPriceProcess is not False:
                criptoPrice = {
                    'id_pair': pair['id_pair'], 
                    'buy_marketprice': oldPriceProcess['buy'],
                    'sell_marketprice': oldPriceProcess['sell'], 
                    'type_calc': oldPriceProcess['type_calc'],
                    'exchange_id': oldPriceProcess['exchange_id']
                }
        else:
            error_cod = 120
            modulo = 'Trading-controller'
            description = 'Link no existe:function-priceMarketUpdate '
            set_BackLogs(error_cod, modulo, description)

        if criptoPrice:
            criptoPrice['created_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            data = [
                criptoPrice['id_pair'], 
                criptoPrice['buy_marketprice'], 
                criptoPrice['sell_marketprice'],
                criptoPrice['type_calc'], 
                criptoPrice['exchange_id'], 
                criptoPrice['created_date']
            ]

            r.hset('cripto_prices', int(criptoPrice['id_pair']), json.dumps(
                {
                    'pair': pair['pair'],
                    'buy_marketprice': criptoPrice['buy_marketprice'],
                    'sell_marketprice': criptoPrice['sell_marketprice'],
                    'exchange_id': criptoPrice['exchange_id'],
                    'created_date': criptoPrice['created_date']
                }
            ))
            r.hset('last_save', 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            r.hset('last_save', int(criptoPrice['id_pair']), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            addCriptoPrice.apply_async(
                args=[data],
                queue="savebd", 
                routing_key='savebd.import'
            )
    except Exception, e:
        error_cod = 121
        modulo = 'Trading-controller'
        description = 'Exception in updateMarketPrice: ' + str(e)
        set_BackLogs(error_cod, modulo, description)
    finally:
        return True


@celery.task(name="killOrders", queue="others", soft_time_limit=app.config['LONGTASK_LIMIT_SOFT'], time_limit=app.config['LONGTASK_LIMIT'])
def killOrders(data):
    try:
        result = False
        type_cancel = data['type']
        mod_trad = TradingModel()
        dat_pair = dict(firstCurrency=data["firstCurrency"], secondCurrency=data["secondCurrency"])
        pair = dat_pair['firstCurrency']+"/"+dat_pair["secondCurrency"]
        cred = mod_trad.getUserPlay(data["bots_configuration_id"])
        if cred['success'] == True:
            response = dataRequest(cred["datos"], data["res"]["datos"], dat_pair)
            if response["success"] == True:
                orders = response["datos"]
                
                if isinstance(orders,list):
                    if(type_cancel != 2):
                        CancelOrderCalculate.apply_async(
                            queue="cancelCalculate",
                            routing_key="cancelCalculate.import",
                            args=[orders,dat_pair,data["id_pair"],data["cancelBuy"],data["cancelSell"], cred["datos"],data["id_bots_play"]]
                        )
                    else:  
                        cancelOrdersTimeCalculate.apply_async(
                            queue="cancelCalculate",
                            routing_key="cancelCalculate.import",
                            args=[orders,dat_pair,cred["datos"],data["id_bots_play"]]
                        )
                    result = dict(orders=orders,pair=pair,bot=data["id_bots_play"])
                else:
                    result = "Not Found orders to cancel in %s for botsplay %d." %(pair, data["id_bots_play"])
            else:
                result = "Error getting orders to cancel in %s for botsplay %d." %(pair, data["id_bots_play"])
        else:
            result = cred['mensaje']
    except Exception as e:
        result = str(e)
    finally:
        return result

@celery.task(name="CancelOrderCalculate_old", queue="cancelCalculate_old")
def CancelOrderCalculate_old(orders,pair,id_pair,cancelBuy,cancelSell, cred, id_play):
    try:
        result = False
        pair_name = pair["firstCurrency"]+"/"+pair["secondCurrency"]
        con_trad = TradingController()
        lista_buy = []
        lista_sell = []
        for order in orders:
            if order["Type"] == "BUY":
                lista_buy.append(order["Price"])
            else:
                lista_sell.append(order["Price"])
        sell = max(lista_sell) if lista_sell else 0
        buy = min(lista_buy) if lista_buy else 0
        prices = con_trad.getMarketPrice(id_pair)
        if prices:
            if buy != 0 and prices.has_key("buy_marketprice"):
                marketbuy = prices["buy_marketprice"]
                diffbuy = abs(marketbuy-buy)
                varbuy = (diffbuy/buy)*100
            else:
                marketbuy = 0
                varbuy = 0

            if sell != 0 and prices.has_key("sell_marketprice"):
                marketsell = prices["sell_marketprice"]
                diffsell = abs(marketsell-sell)
                varsell = (diffsell/sell)*100
            else:
                marketsell = 0
                varsell = 0
            list_del = "" 
            for order in orders: 
                if order["Type"] == "SELL" and abs(varsell) >= abs(cancelSell):
                    if marketsell > 0 and order["Price"] >= marketsell:
                        list_del = list_del + str(order["order_id"]) + ',' #.append(order["order_id"])
                elif order["Type"] == "BUY" and abs(varbuy) >= abs(cancelBuy):
                    if marketbuy > 0 and order["Price"] <= marketbuy:
                        list_del = list_del + str(order["order_id"]) + ',' #.append(order["order_id"])

            if list_del:
                list_del = list_del[:-1]
                sendCancelOrder.apply_async(
                    queue="cancelOrders", 
                    args=[{"idOrders":list_del, 'firstCurrency':pair["firstCurrency"], 'secondCurrency':pair["secondCurrency"]}],
                    routing_key='cancelOrders.import',
                )
                result = dict(orders=list_del,pair=pair_name,bot=id_play,sell=marketsell,buy=marketbuy)
            else:
                result = "Not orders higher than %d or lower than %d to Cancel in  %s for play %d" %(marketbuy, marketsell, pair_name, id_play)

        else:
            result = "Not found updated pricesMarket to taskCancelation in pair %s for play %d." %(pair_name, id_play)
    except Exception as e:
        result = str(e)
    finally:
        return result

@celery.task(name="CancelOrderCalculate", queue="cancelCalculate")
def CancelOrderCalculate(orders,pair,id_pair,cancelBuy,cancelSell, cred, id_play):
    try:
        result = False
        pair_name = pair["firstCurrency"]+"/"+pair["secondCurrency"]
        con_trad = TradingController()
        lista_buy = []
        lista_sell = []
        for order in orders:
            if order["Type"] == "BUY":
                lista_buy.append(order["Price"])
            else:
                lista_sell.append(order["Price"])
        sell = min(lista_sell) if lista_sell else 0
        buy = max(lista_buy) if lista_buy else 0
        prices = con_trad.getMarketPrice(id_pair)
        if prices:
            if buy != 0 and prices.has_key("buy_marketprice"):
                marketbuy = prices["buy_marketprice"]
                diffbuy = abs(marketbuy-buy)
                varbuy = (diffbuy/buy)*100
            else:
                marketbuy = 0
                varbuy = 0

            if sell != 0 and prices.has_key("sell_marketprice"):
                marketsell = prices["sell_marketprice"]
                diffsell = abs(marketsell-sell)
                varsell = (diffsell/sell)*100
            else:
                marketsell = 0
                varsell = 0
            list_del = ""
            for order in orders: 
                if order["Type"] == "SELL" and abs(varsell) >= abs(cancelSell):
                    if marketsell > 0 and order["Price"] >= marketsell:
                        list_del = list_del + str(order["order_id"]) + ','
                elif order["Type"] == "BUY" and abs(varbuy) >= abs(cancelBuy):
                    if marketbuy > 0 and order["Price"] <= marketbuy:
                        list_del = list_del + str(order["order_id"]) + ','

            if list_del:
                list_del = list_del[:-1]
                sendCancelOrder.apply_async(
                    queue="cancelOrders", 
                    args=[{"idOrders":list_del, 'firstCurrency':pair["firstCurrency"], 'secondCurrency':pair["secondCurrency"]}],
                    routing_key='cancelOrders.import',
                )
                result = dict(orders=list_del,pair=pair_name,bot=id_play,sell=marketsell,buy=marketbuy)
            else:
                result = "Not orders higher than %d or lower than %d to Cancel in  %s for play %d" %(marketbuy, marketsell, pair_name, id_play)

        else:
            result = "Not found updated pricesMarket to taskCancelation in pair %s for play %d." %(pair_name, id_play)
    except Exception as e:
        result = str(e)
    finally:
        return result

@celery.task(name="cancelOrdersTimeCalculate", queue="cancelCalculate")
def cancelOrdersTimeCalculate(orders,pair,cred,id_play):
    try:
        result = False
        time_to_cancel = app.config['CANCEL_ORDERS_TIME_TIME']
        pair_name = pair["firstCurrency"]+"/"+pair["secondCurrency"]
        current_date = datetime.now()
        list_del = ""
        for order in orders:
            order_time = datetime.strptime(order['datetime'],"%Y-%m-%d %H:%M:%S")
            difftime = current_date - order_time
            difftimesecond = difftime.total_seconds()
            if difftimesecond >= time_to_cancel:
                list_del = list_del + str(order["order_id"]) + ','

        if list_del:
            list_del = list_del[:-1]
            sendCancelOrder.apply_async(
                queue="cancelOrders", 
                args=[{"idOrders":list_del, 'firstCurrency':pair["firstCurrency"], 'secondCurrency':pair["secondCurrency"]}],
                routing_key='cancelOrders.import',
            )
            result = dict(orders=list_del,pair=pair_name,bot=id_play)
        else:
            hour_to_cancel = current_date - timedelta(seconds=time_to_cancel)
            result = "Not found orders older than %s in %s for play %d" %(hour_to_cancel.strftime("%Y-%m-%d %H:%M:%S"), pair_name, id_play)

    except Exception as e:
        result = str(e)
    finally:
        return result


@celery.task(name="sendCancelOrder", queue="cancelOrders", soft_time_limit=app.config['LONGTASK_LIMIT_SOFT'], time_limit=app.config['LONGTASK_LIMIT'])
def sendCancelOrder(dict_del):
    try:
        result = False
        model = TradingModel()
        format_co = model.getformat("CO")
        if format_co['success'] == True:
            response = convert_unicode(format_co["datos"])
            endPoint = response['url']
            if response["method"]  == "POST":
                data = dict_del
                if response["data_type"] == "JSON":
                    data = json.dumps(data)

                res = request_post_url(endPoint, data)
                if res.status_code == 200:
                    num_orders = len(json.loads(res.text))
                    result = "Canceled executed to %s orders."%(num_orders)
                else:
                    res = res.status_code
                    result = "Error on request cancel order - %s." %(res)

        else:
            result = "Task Error: sendCancelOrder not found Format CO."
        response = convert_unicode(format_co["datos"])
    except Exception as e:
        result = str(e)
    finally:
        return result


@celery.task(name="updatePriceConvertByCoin", queue="others", soft_time_limit=app.config['LONGTASK_LIMIT_SOFT'], time_limit=app.config['LONGTASK_LIMIT'])
def updatePriceConvertByCoin(apilinks, coin):
    try:
        result = False
        model = TradingModel()
        prices =  model.proApiReference(apilinks, coin)
        modelCoin = CoinModel()
        getcoin = modelCoin.getCoin(coin)
        
        if getcoin != False:
            buyprice = float(getcoin[3])
            sellprice = float(getcoin[4])
            date_conin = getcoin[7]
            date_now = datetime.now()
        else:
            raise NameError("%s NOT FOUND" %(coin))  
        count = 0
        sum_buy = 0
        sum_sell = 0
        variation = app.config['VARIATION']
        difftimeconf = app.config['MARKET_PRICE_TIME']
        diff_time = (date_now - date_conin).seconds  if date_now > date_conin else 0
        for price in prices:
            variationbuy = (abs(buyprice-price['buy'])*100)/buyprice
            variationsell = (abs(sellprice-price['sell'])*100)/buyprice
            if (variationbuy <= variation and variationsell <= variation) or (diff_time > difftimeconf):
                sum_buy = sum_buy + price['buy']
                sum_sell = sum_sell + price['sell']
                count = count + 1

        if count > 0:
            prom_buy = float(sum_buy/count)
            prom_sell = float(sum_sell/count)
            saveData = [coin, prom_buy, prom_sell]
            save = model.updateConvertValues(saveData)
            if save is True:
                result = "Price Saved on %s. Buy: %f - Sell: %f. PricesCount: %d" %(coin, prom_buy, prom_sell, count)
            else:
                raise NameError("No actualizo promedio fiatPrice:function-cronPrice")
        else:
            logging.info("Price founded: ")
            logging.info(prices)
            raise NameError("Not exists price in range on %s.  Buy: %f - Sell: %f" %(coin, buyprice, sellprice))

    except Exception as e:
        result = "Task Error: updatePriceConvertByCoin - %s" %(str(e))
    finally:
        return result
    