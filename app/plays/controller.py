import sqlalchemy
import ast, json, random, logging, requests
from kombu import Queue
from datetime import datetime, date
from random import randint, uniform
from flask import (
    session,
    jsonify,
    request,
    current_app as app
)
from app.commons import (
    convert_unicode,
    create_error_msg,
    request_post_url,
    create_success_msg,
)
from app import celery, set_BackLogs, r, genericConect
from app.plays.models import PlayModel
from app.trading.controller import TradingController, updateMarketPrice
from app.trading.controller import selectMarketPricesExchange_attempt
from app.trading.controller import selectMarketPricesExchange_hz
from app.exchanges.models import ExchangeModel
import math
import numpy as np
from decimal import Decimal

class PlayController(object):

    data = {
        'price': 0.0,
        'type': '',
        'amount': 0.0,
        'pair': '',
        'firstcurrency': '',
        'secondcurrency': '',
        'trade': 0
    }

    def __init__(self, res_create=""):
        self.res_create = res_create

    def play(self):
        if request.is_json:
            data = request.get_json()
            data = convert_unicode(data)
            try:
                if data['ATE'] < data['ET']:
                    if data['ATC'] < (data['ET'] - data['CT']):
                        play_save = [
                            int(session['id_user']),
                            data['id_bot_configuration'],
                            data['order_type'],
                            data['ATE'],
                            data['ATC']
                        ]
                        model = PlayModel()
                        result = model.savePlay(play_save)
                        if result:
                            response = create_success_msg(result)
                        else:
                            response = create_error_msg("Can't play bot")
                    else:
                        msj = 'ATC must be less than the result of the subtraction of ET and CT'
                        response = create_error_msg(msj)
                else:
                    response = create_error_msg('ATE must be less than ET')
            except Exception, response:
                raise create_error_msg(jsonify(response))
            finally:
                return jsonify(str(response))
        else:
            return jsonify("Invalid Format")

    def stop(self):
        if request.is_json:
            data = request.get_json()
            try:
                play_save = [session['id_user'], data['id_bot_play']]
                model = PlayModel()
                result = model.stopPlay(play_save)
                if result:
                    response = create_success_msg(result)
                else:
                    response = create_error_msg("Can't stop bot")

            except Exception, response:
                raise create_error_msg(str(response))
            finally:
                return jsonify(str(response))
        else:
            return jsonify("Invalid Format")

    def botsPlaying(self):
        try:
            model = PlayModel()
            active_plays = model.listPlays('Active')
            if active_plays:
                active_plays = convert_unicode(json.loads(active_plays))
                count_plays = len(active_plays)
                for play in active_plays:
                    if play['status'] == 'active':
                        model = PlayModel()
                        bot_used = json.loads(model.getBotCombine(
                            play['bots_configuration_id'],
                            play['botConfiguration']['bot_type_id']
                        ))
                        if play['botConfiguration']['bot_type_id'] == 'B':
                            logging.info("****Function Bots Broker****")
                            bot_used['botConfiguration'] = play['botConfiguration']
                            del play['botConfiguration']
                            execute_Broker(play, bot_used)
                        elif play['botConfiguration']['bot_type_id'] == 'V':
                            logging.info("****Function Bots Volume****")
                            bot_used = convert_unicode(bot_used)
                            bot_used["botConfig"] = convert_unicode(play['botConfiguration'])
                            execute_Volume_hz(play, bot_used) # execute_Volume(play, bot_used)
                        elif play['botConfiguration']['bot_type_id'] == 'D':
                            logging.info("****Executing execute_Deph to id_play: %s ****" %(play['id_bots_play']))
                            bot_used['botConfiguration'] = convert_unicode(play['botConfiguration'])
                            del play['botConfiguration']
                            execute_Deph(play, bot_used)
                        else:
                            logging.info("****log no existe este tipo de bot****")
                logging.info("Processed bots %s" %(count_plays))
            else:
                logging.info("Not found bots.")
            response = True
        except Exception as e:
            error_cod = 500
            modulo = 'Plays-controller'
            id_play = play['id_bots_play']
            description = 'Error in botsPlaying: ' + str(e) + ' id_play ' + str(id_play)
            set_BackLogs(error_cod, modulo, description)
            logging.warning("Exception botsPlaying: %s" % (e.message))
            response = False
        finally:
            return response

    def insertBotPlay(self):
        try:
            data = request.json

            # In Redis/Celery/Kombu:
            purgeQueue()

            model = PlayModel()
            res = model.Insert_BotPlay(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def showBotPlay(self):
        try:
            data = request.json
            model = PlayModel()
            res = model.Show_BotPlay(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def updateBotPlay(self):
        try:
            data = request.json
            
            # In Redis/Celery/Kombu:
            purgeQueue()

            # In DataBase:
            model = PlayModel()
            res = model.Update_BotPlay(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def lastUpdateBotPlay(self):
        try:
            data = request.json
            model = PlayModel()
            res = model.lastUpdate_BotPlay(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def listPlays(self):
        model = PlayModel()
        try:
            if request.is_json:
                data = request.get_json()
                response = json.loads(model.getPlayList(data['idBot']))
                for data in response:
                    data['diferencia'] = eval_time(data['dat_play'], data['dat_stop']) if not data['dat_stop'] is None else ''
                    data['logs'] = json.loads(model.getPlayLog(data['id_bots_play']))
                    for values in data['logs']:
                        values['response'] = ast.literal_eval(str(values['response']))
                        values['response'] = values['response']['datos'] if 'datos' in values['response'] else values['response']
                response = create_success_msg(response)
            else:
                response = "Invalid request"
        except Exception, e:
            error_cod = 500
            modulo = 'Plays-controller'
            description = 'Error in listing plays: ' + str(e)
            set_BackLogs(error_cod, modulo, description)
            response = str(description)
        finally:
            return jsonify(response)


def execute_Broker(data_play, data_bot):
    PlayController.data['firstcurrency'] = data_bot['Pairs'][0]['firstcurrency']
    PlayController.data['secondcurrency'] = data_bot['Pairs'][0]['secondcurrency']
    PlayController.data['pair'] = data_bot['Pairs'][0]['pair']
    PlayController.data['amount'] = str(
        round(uniform(float(data_bot['botConfiguration']['min_amount']),
                      float(data_bot['botConfiguration']['max_amount'])), 8))
    data_play['alt_execute_time'] += data_bot['botConfiguration']['execute_time']
    execute_time = randint(data_bot['botConfiguration']['execute_time'], data_play['alt_execute_time'])
    if data_play['order_type'] == 'both':
        for i in range(2):
            if i == 0:
                PlayController.data['type'] = 'buy'
            else:
                PlayController.data['type'] = 'sell'

            formats_temp = data_bot['Formats']
            data_bot['Formats'] = paramsMerge(data_bot['Formats'][0])
            log = {'id_bots_play': data_play['id_bots_play'], 'type': PlayController.data['type'],
                   'amount': PlayController.data['amount']}
            createOrder.apply_async(
                queue="broker",
                countdown=execute_time,
                routing_key="broker.import",
                args=[data_bot['Users'][0],data_bot['Formats'], log],
            )
            data_bot['Formats'] = formats_temp
    else:
        PlayController.data['type'] = data_play['order_type']
        data_bot['Formats'] = paramsMerge(data_bot['Formats'][0])
        log = {'id_bots_play': data_play['id_bots_play'], 'type': PlayController.data['type'],
               'amount': PlayController.data['amount']}

        createOrder.apply_async(
            queue="broker",
            countdown=execute_time,
            routing_key="broker.import",
            args=[data_bot['Users'][0],data_bot['Formats'], log],
        )
    return True


def execute_Volume(data_play, data_bot):
    """
    :param data_play: obj global request from flask
    :param data_bot: tuple with all params
    :return: dict **kwargs
    """

    # Set temp data
    dat_tmp = dict(
        pair=data_bot['Pairs'][0]['pair'],
        id_pair=data_bot['Pairs'][0]['id_pair'],
        firstCurrency=data_bot['Pairs'][0]['firstcurrency'],
        secondCurrency=data_bot['Pairs'][0]['secondcurrency']
    )
    amount_rand = round(
        random.uniform(
            data_bot['botConfig']['min_amount'],
            data_bot['botConfig']['max_amount']
        ), 6
    )
    
    # Save temp data
    if data_bot['Formats']:
        info = {}
        list_formats = []
        for formatEx in data_bot['Formats']:
            formatEx["params"] = ast.literal_eval(formatEx["params"])
            if formatEx["format_name"] == "B":
                formatEx["params"]["new"]["typeOrder"] = "Buy"
            else:
                formatEx["params"]["new"]["typeOrder"] = "Sell"
            list_formats.append(replace_data(formatEx, dat_tmp))

        # Generate new structure
        for formatEx in list_formats:
            if formatEx["format_name"] == "B":
                info["buy"] = formatEx
            else:
                info["sell"] = formatEx
        data_bot['Formats'] = info
    else:
        logging.info("Not found formatsExchange.")
        return False

    # Random for typeOrder
    num = random.randint(0, 1)
    typeOrder = "buy" if num == 1 else "sell"

    # Prices Management
    # Set Variations
    p_buy = data_bot["botConfig"]["buy_spread"]
    p_sell = data_bot["botConfig"]["sell_spread"]

    # Get priceMarket
    user = data_bot["Users"][0]
    user = ast.literal_eval(user["credentials"])
    prices = findPrice(
        user,
        dat_tmp['firstCurrency'],
        dat_tmp['secondCurrency']
    )

    if prices:
        prices["buy"] = prices["buy"] if prices.has_key("buy") else 0
        prices["sell"] = prices["sell"] if prices.has_key("sell") else 0
        if prices["buy"] == 0 or prices["sell"] == 0:
            t_controller = TradingController()
            dat_prices = t_controller.getMarketPrice(dat_tmp["id_pair"])  
            if dat_prices:
                if prices["buy"] == 0:
                    prices["buy"] = dat_prices["sell_marketprice"]
                elif prices["sell"] == 0:
                    prices["sell"] = dat_prices["buy_marketprice"]
            else:
                prices = None
                logging.warning("Prices not found.")
    else:
        t_controller = TradingController()
        dat_prices = t_controller.getMarketPrice(dat_tmp["id_pair"])  
        if dat_prices:
            prices["buy"] = dat_prices["sell_marketprice"]
            prices["sell"] = dat_prices["buy_marketprice"]
        else:
            prices = None
            logging.warning("Prices not found.")                                

    if prices:
        # Add Variations
        dicc_price = dict(
            buy=round((prices["buy"]-prices["buy"]*p_buy), 2),
            sell=round((prices["sell"]+prices["sell"]*p_sell), 2)
        )

        # Define Investement
        dicc_inv = dict(
            sell=amount_rand,
            buy=dicc_price[typeOrder] * amount_rand
        )

        # Set User
        p_order = data_bot["Users"][0]

        # Create Mother Order
        format_seleted = data_bot['Formats'][typeOrder]
        format_seleted["id_bots_play"] = data_play['id_bots_play'],
        format_seleted["params"]["new"]["trade"] = 1
        format_seleted["params"]["new"]["price"] = dicc_price[typeOrder]
        format_seleted["params"]["new"]["investement"] = dicc_inv[typeOrder]

        # Send task
        celery.send_task(
            name='addVolume',
            args=[
                p_order["credentials"],
                format_seleted,
            ],
        )
    else:
        return True
         
    return True

def execute_Volume_attempt(data_play, data_bot):
    """
    :param data_play: obj global request from flask
    :param data_bot: tuple with all params
    :return: dict **kwargs
    """

    # Set temp data
    dat_tmp = dict(
        pair=data_bot['Pairs'][0]['pair'],
        id_pair=data_bot['Pairs'][0]['id_pair'],
        firstCurrency=data_bot['Pairs'][0]['firstcurrency'],
        secondCurrency=data_bot['Pairs'][0]['secondcurrency']
    )
    amount_rand = round(
        random.uniform(
            data_bot['botConfig']['min_amount'],
            data_bot['botConfig']['max_amount']
        ), 6
    )
    
    # Save temp data
    if data_bot['Formats']:
        info = {}
        list_formats = []
        for formatEx in data_bot['Formats']:
            formatEx["params"] = ast.literal_eval(formatEx["params"])
            if formatEx["format_name"] == "B":
                formatEx["params"]["new"]["typeOrder"] = "Buy"
            else:
                formatEx["params"]["new"]["typeOrder"] = "Sell"
            list_formats.append(replace_data(formatEx, dat_tmp))

        # Generate new structure
        for formatEx in list_formats:
            if formatEx["format_name"] == "B":
                info["buy"] = formatEx
            else:
                info["sell"] = formatEx
        data_bot['Formats'] = info
    else:
        logging.info("Not found formatsExchange.")
        return False

    # Random for typeOrder
    num = random.randint(0, 1)
    typeOrder = "buy" if num == 1 else "sell"

    # Prices Management
    # Set Variations
    p_buy = data_bot["botConfig"]["buy_spread"]
    p_sell = data_bot["botConfig"]["sell_spread"]

    # Get priceMarket
    user = data_bot["Users"][0]
    user = ast.literal_eval(user["credentials"])
    """
    prices_tr = findPrice_attempt(
        user,
        dat_tmp['firstCurrency'],
        dat_tmp['secondCurrency']
    )
    """
    prices = selectMarketPricesExchange_attempt({'idPair':dat_tmp['id_pair']})

    if prices:
        prices["buy"] = prices["buy"] if prices.has_key("buy") else 0
        prices["sell"] = prices["sell"] if prices.has_key("sell") else 0
        if prices["buy"] == 0 or prices["sell"] == 0:
            t_controller = TradingController()
            dat_prices = t_controller.getMarketPrice_attempt(dat_tmp["id_pair"])  
            if dat_prices:
                if prices["buy"] == 0:
                    prices["buy"] = dat_prices["sell_marketprice"]
                elif prices["sell"] == 0:
                    prices["sell"] = dat_prices["buy_marketprice"]
            else:
                prices = None
                logging.warning("Prices not found.")
    else:
        t_controller = TradingController()
        dat_prices = t_controller.getMarketPrice_attempt(dat_tmp["id_pair"])  
        if dat_prices:
            prices["buy"] = dat_prices["sell_marketprice"]
            prices["sell"] = dat_prices["buy_marketprice"]
        else:
            prices = None
            logging.warning("Prices not found.")                                

    if prices:
        # Add Variations
        dicc_price = dict(
            buy=round((prices["buy"] + (prices["buy"]*p_buy)/100), 2),
            sell=round((prices["sell"] + (prices["sell"]*p_sell)/100), 2)
        )

        # Define Investement
        dicc_inv = dict(
            sell=amount_rand,
            buy=dicc_price[typeOrder] * amount_rand
        )

        # Set User
        p_order = data_bot["Users"][0]

        # Create Mother Order
        format_seleted = data_bot['Formats'][typeOrder]
        format_seleted["id_bots_play"] = data_play['id_bots_play'],
        format_seleted["params"]["new"]["trade"] = 1
        format_seleted["params"]["new"]["price"] = dicc_price[typeOrder]
        format_seleted["params"]["new"]["investement"] = dicc_inv[typeOrder]

        # Generate Times
        if data_bot['botConfig']['execute_time'] > data_play['alt_execute_time']:
            execute_time = randint(
                data_play['alt_execute_time'], 
                    data_bot['botConfig']['execute_time']
            )
        else:
            execute_time = randint(
                data_bot['botConfig']['execute_time'], 
                data_play['alt_execute_time']
            )

        # Send task
        addVolume.apply_async(
            queue="addVolume",
            countdown=execute_time,
            routing_key="addVolume.import",
            args=[
                p_order["credentials"],
                format_seleted,
            ],
        )

    else:
        return True
         
    return True

def execute_Volume_hz(data_play, data_bot):
    """
    :param data_play: obj global request from flask
    :param data_bot: tuple with all params
    :return: dict **kwargs
    """

    # Get real user exchange assigned in bot config:
    user_bot = getCurrentUserBot(data_play['bots_configuration_id'])
    data_bot['Users'][0] = user_bot

    # Currencies:
    hz = (data_bot['Pairs'][0]['pair']).split('/')
    firstCur = hz[0]
    secondCur = hz[1]

    # Set temp data
    bot_tmp = dict(
        pair=data_bot['Pairs'][0]['pair'],
        id_pair=data_bot['Pairs'][0]['id_pair'],
        firstCurrency=firstCur,
        secondCurrency=secondCur
    )
    
    # Monto aleatorio:
    amount_rand = round(
        random.uniform(
            data_bot['botConfig']['min_amount'],
            data_bot['botConfig']['max_amount']
        ), 6
    )
    
    # Precio por par: (obtencion de precios externos)
    prices = selectMarketPricesExchange_attempt({'idPair':bot_tmp['id_pair']})

    # Pares de ordenes aleatorios:
    orden_dominante = data_play['order_type']
    pares_aleat = 2 #*random.randint(1,2) #(1,3)

    # Obtencion de datos financieros segun typeOrder:
    investement_main = 0
    if orden_dominante != 'sell' and orden_dominante != 'buy':
        logging.info('Order dont recognized.')
        return False
    if orden_dominante == 'sell':
        investement_main = amount_rand
        total = prices[orden_dominante]*investement_main
        TOTAL_AMOUNT_FOR_ORDERSEC = total 
    if orden_dominante == 'buy':
        investement_main = prices[orden_dominante]*amount_rand
        total = investement_main
        TOTAL_AMOUNT_FOR_ORDERSEC = amount_rand
        
    # Get structure for Buy and Sell - Volume:
    struct_format = getFormatExchange('VB') if orden_dominante=='buy' else getFormatExchange('VS')

    # Get buy/sell variation:
    maxPrice = 0
    minPrice = 0
    if orden_dominante=='buy':
        variation = data_play['botConfiguration']['buy_spread'] #-1.5
        maxPrice = prices['sell'] 
        minPrice = maxPrice + maxPrice*(variation/100)
    else:
        variation = data_play['botConfiguration']['sell_spread'] #1.5
        maxPrice = prices['buy'] 
        minPrice = maxPrice + maxPrice*(variation/100)
        
    """
    CREACION DE ORDEN PRIMARIA 
    """
    credentials_main = json.loads(user_bot['credentials'])
    params_order = [credentials_main['key'].encode('utf-8'), credentials_main['secret'].encode('utf-8')]
    params_format = [struct_format['data_type'], struct_format['format_name'], data_play['id_bots_play'], struct_format['method'], struct_format['url']]
    params_new_format = [orden_dominante, prices[orden_dominante], round(float(investement_main),8), bot_tmp['firstCurrency'], bot_tmp['secondCurrency']]
    order_primary = estructure_order_volume(params_order=params_order, params_format=params_format, params_new_format=params_new_format,tipo='primary')
    """
    CREACION DE ORDENES SECUNDARIAS
    """
    type_ordsec = 'buy' if orden_dominante=='sell' else 'sell'
    HELP_DECIMALES = 1000   # Ayuda a dividir y multiplicar las cantidades para obtener los datos aleatorios 
    EACH_AMOUNT_FOR_ORDERSEC = TOTAL_AMOUNT_FOR_ORDERSEC/(pares_aleat-1) #math.floor(TOTAL_AMOUNT_FOR_ORDERSEC*HELP_DECIMALES/(pares_aleat-1))/HELP_DECIMALES # Monto que no exceda la n-ava parte del TOTAL

    investement = []
    price_aleat = []

    # Inversiones segun par de ordenes aleatorio:
    if pares_aleat == 2:

        # Invesrion:
        investement = [investement_main/prices[orden_dominante]] if orden_dominante=='buy' else [investement_main*prices[orden_dominante]] #[TOTAL_AMOUNT_FOR_ORDERSEC]

        # Precio:
        price_aleat = [round(random.uniform(minPrice,maxPrice),8)] #[prices[orden_dominante]] 
        
    if pares_aleat == 4:
        
        # Inversion:
        investement = []
        for i in range((pares_aleat-1) - 1):
            aleat = random.uniform(0,EACH_AMOUNT_FOR_ORDERSEC)
            investement.append(aleat)
        last_inv = TOTAL_AMOUNT_FOR_ORDERSEC - sum(investement)
        investement.append(last_inv)

        # Precio:
        price_aleat = getVecPricesAleat(minPrice, maxPrice, pares_aleat-1)

        # Ordenar inversiones y precios:
        if type_ordsec=='buy':
            price_aleat.sort(reverse=True)
        else:
            price_aleat.sort()

    if pares_aleat == 6:
        
        # Inversion:
        investement = []
        for i in range((pares_aleat-1) - 1):
            aleat = random.uniform(0,EACH_AMOUNT_FOR_ORDERSEC)
            investement.append(aleat)
        last_inv = TOTAL_AMOUNT_FOR_ORDERSEC - sum(investement)
        investement.append(last_inv)
        
        # Precio:
        price_aleat = getVecPricesAleat(minPrice, maxPrice, pares_aleat-1)

        # Ordenar inversiones y precios:
        if type_ordsec=='buy':
            price_aleat.sort(reverse=True)
        else: 
            price_aleat.sort()

    """
    VALIDACION DE INVERSION
    """ 
    # Referencial para verificar que no supera la inversion
    lst_gains = validateInvestement(price_aleat,investement,investement_main,tipo_primary=orden_dominante)
    aux_lst = lst_gains[0:-1]
    residual = investement_main - sum(aux_lst)
    aux_lst.append(residual)
    view_investement = aux_lst
    if sum(view_investement) > investement_main:
        return False, "Gain exceed to investment"

    # Orden secundaria:
    orders_secundaries = []
    for i in range(0,pares_aleat-1):

        # Parametros:
        user_aleat_bot = getAleatUserBot(user_bot['username'])
        credentials_ = json.loads(user_aleat_bot['credentials'])
        params_order = [credentials_['key'].encode('utf-8'), credentials_['secret'].encode('utf-8')]
        fname = 'VB' if type_ordsec=='buy' else 'VS'
        params_format = [struct_format['data_type'], fname, data_play['id_bots_play'], struct_format['method'], struct_format['url']]
        params_new_format = [type_ordsec, price_aleat[i], investement[i], bot_tmp['firstCurrency'], bot_tmp['secondCurrency']]

        # Orden:
        order_vol = estructure_order_volume(params_order=params_order, params_format=params_format ,params_new_format=params_new_format)
        orders_secundaries.append(order_vol)

    """
    ORDEN PRIMARIA + ORDENES SECUNDARIAS
    """ 
    volume_orders = []
    volume_orders.append(order_primary)
    volume_orders.extend(orders_secundaries)

    # Generate Times
    if data_bot['botConfig']['execute_time'] > data_play['alt_execute_time']:
        execute_time = randint(
            data_play['alt_execute_time'], 
            data_bot['botConfig']['execute_time']
        )
    else:
        execute_time = randint(
            data_bot['botConfig']['execute_time'], 
            data_play['alt_execute_time']
        )

    # Send task
    addVolume.apply_async(
        queue="addVolume",
        countdown=execute_time,
        routing_key="addVolume.import",
        args=[
            {
                'volume_orders':volume_orders
            }
        ],
    )

    return True

def estructure_order_volume(params_order=[], params_format=[], params_new_format=[], tipo='secondary'):
    params_order = [po.encode('utf-8') if isinstance(po,unicode) else po for po in params_order]
    params_format = [pf.encode('utf-8') if isinstance(pf,unicode) else pf for pf in params_format]
    params_new_formato = [pwf.encode('utf-8') if isinstance(pwf,unicode) else pwf for pwf in params_new_format]
    order = dict(
        key=params_order[0],
        secret=params_order[1]
    )
    new_format = dict(
        typeOrder=params_new_format[0],
        price=params_new_format[1],
        investement=params_new_format[2], 
        firstCurrency=params_new_format[3], 
        secondCurrency=params_new_format[4],
        trade=1
    )
    formato=dict(
        data_type=params_format[0],
        format_name=params_format[1],
        id_bots_play=params_format[2],
        method=params_format[3],
        params={'new':new_format},
        url=params_format[4]
    )
    estruct_order = dict(
        order=order,
        format=formato,
        type=tipo
    )
    return estruct_order

def getCurrentUserBot(id_bot_config):

    # Find user bot assign to bot config:
    lst_bots = genericConect('sp_bots_configurations_listar', [0]) # List all bots
    bot_conf = [r for r in lst_bots if r[0]==id_bot_config]
    bot_conf = list(bot_conf[0])
    username_bot = bot_conf[23]

    # Find data of user bot:
    id_exchange = 1
    lst_bot_users = genericConect('sp_bots_listar_combine', [id_exchange], True)
    users = [r for r in lst_bot_users if r[0]=="UE"]
    data_username_bot = [u for u in users if u[3]==unicode(username_bot)]
    data_username_bot = list(data_username_bot[0])

    # Decrypt credentials:
    exchange_model = ExchangeModel()
    user_bot_credentiales = exchange_model.string2decrypt(data_username_bot[4])
    current_user_bot = dict(
        username = username_bot.encode('utf-8'),
        credentials = json.dumps(user_bot_credentiales)
    )

    return current_user_bot

def getAleatUserBot(username_bot):

    # Find users exchange bitinka:
    id_exchange = 1
    lst_bot_users = genericConect('sp_bots_listar_combine', [id_exchange], True)
    users = [r for r in lst_bot_users if r[0]=="UE"]

    # Erase current username exchange bot:
    indice = 0
    for i,u in enumerate(users):
        indice = i if u[3]==username_bot else indice
    users.pop(indice)

    # Get random user:
    num_aleat = random.randint(0,len(users)-1)
    data_username_bot = list(users[num_aleat])

    # Decrypt credentials:
    exchange_model = ExchangeModel()
    user_bot_credentiales = exchange_model.string2decrypt(data_username_bot[4])
    aleat_user_bot = dict(
        username = data_username_bot[3],
        credentials = json.dumps(user_bot_credentiales)
    )

    return aleat_user_bot

def getFormatExchange(type_order):

    id_exchange = 1
    lst_bot_formats = genericConect('sp_bots_listar_combine', [id_exchange], True)
    formats = [f for f in lst_bot_formats if f[0]=="EF"]

    indice = 0
    for i,f in enumerate(formats):
        indice = i if f[3]==type_order else indice

    exchange_format = list(formats[indice])

    format_exchange = dict(
        data_type=exchange_format[6],
        url=exchange_format[4],
        format_name=exchange_format[3],
        params=exchange_format[7],
        method=exchange_format[5]
    )

    return format_exchange

def validateInvestement(list_prices, list_investements, investement, tipo_primary="buy"):
    lst = [prc*inv for prc,inv in zip(list_prices,list_investements)] if tipo_primary=="buy" else [inv/prc for prc,inv in zip(list_prices,list_investements)]
    return lst

def getVecPricesAleat(min_amount, max_amount, cant):
    vec_prices_aleat = []
    for i in range(cant):
        aleat = random.uniform(min_amount, max_amount)
        vec_prices_aleat.append(aleat)
    return vec_prices_aleat

def paramsMerge(formats_touse):
    for key in PlayController.data:
        formats_touse['params'] = formats_touse['params'].replace(key.upper(), str(PlayController.data[key]))
    return formats_touse


def replace_data(data1, data2):
    """
    :param data1: dict - estructura a remplazar
    :param data2: dict - estructura con info
    :return: dict - estructura con info set.
    """
    dicc_tmp = data1['params']["new"]
    for value in dicc_tmp.values():
        for key in data2:
            if value == key.upper():
                key_index = dicc_tmp.keys()[dicc_tmp.values().index(value)]
                dicc_tmp[key_index] = data2[key] 
    data1['params']["new"] = dicc_tmp

    return data1


def res_request(url, data):
    """
    :param url: str - URL para request
    :param data: dict - info a enviar
    :return: dict - respuesta de request.
    """
    headers = {'content-type': 'application/json'}
    response = requests.post(
        url,
        data=data,
        headers=headers
    )
    return response


def findPrice(user, firstC, secondC):
    """
    :param user: dict - credenciales de usuario
    :param firstC: str - pair en first
    :param secondC: str - pair en second
    :return: dict - precios para buy/sell.
    """
    result = getFormat()
    if result:
        pair = firstC + "_" + secondC
        response = dataRequest(result, user, pair)
        try:
            if response["success"] == True:
                if not "result" in response["datos"]:
                    dicc = {}
                    levels = ['purchases', 'sales']
                    for level in levels:
                        if level in response["datos"]['orders']:
                            data = response["datos"]['orders'][level][secondC][0]
                            if data:
                                if level == "purchases":
                                    dicc["buy"] = data["Price"] if data["Price"] else 0
                                else:
                                    dicc["sell"] = data["Price"] if data["Price"] else 0
                    return dicc
                else:
                    logging.info(response["datos"]["result"])
                    return None
            else:
                raise ValueError(404)
        except ValueError:
            logging.info(response["mensaje"])
    else:
        return None

def findPrice_attempt(user, firstC, secondC):
    result = getFormat()
    if result:
        pair = firstC + "_" + secondC
        response = dataRequest_attempt(result, user, pair)
        try:
            if response["success"] == True:
                if 'status' in response['datos'] and isinstance(response['datos']['status'],str):
                    return None
                else:
                    if not "result" in response["datos"]:
                        dicc = {}
                        prices_order_buy = [order['Price'] for order in response['datos'] if order['Type']=='BUY']
                        prices_order_sell = [order['Price'] for order in response['datos'] if order['Type']=='SELL']
                        dicc['buy'] = min(prices_order_buy) if len(prices_order_buy) > 0 else 0
                        dicc['sell'] = max(prices_order_sell) if len(prices_order_sell) > 0 else 0
                        return dicc
                    else:
                        logging.info(response["datos"]["result"])
                        return None
            else:
                raise ValueError(404)
        except ValueError:
            logging.info(response["mensaje"])
    else:
        return None

def dataRequest(all_params, user, pair):
    """
    :param all_params: dict - parametros para consulta
    :param user: dict - credenciales de usuario
    :param pair: str - pairs concatenados
    :return: dict - precios para buy/sell.
    """
    cadena = all_params['params'].split("?")[0]
    new_params = all_params['params'].replace(cadena, pair)
    if all_params['method'] == 'GET':
        if all_params['params'] != '':
            endPoint = all_params['url'] + new_params
        response = requests.get(endPoint)

    if response.status_code == 200:
        response = convert_unicode(response.json())
        result = create_success_msg(response)
    else:
        response = response.status_code
        msj  = "Error on request %s" %(response)
        result = create_error_msg(msj)
    return result

def dataRequest_attempt(all_params, user, pair):
    response = None
    if all_params['method'] == 'GET':
        cadena = all_params['params'].split("?")[0]
        new_params = all_params['params'].replace(cadena, pair)
        if all_params['params'] != '':
            endPoint = all_params['url'] + new_params
        response = requests.get(endPoint)

    if all_params['method'] == 'POST':
        firstcurrency = pair.split("_")[0]
        secondcurrency = pair.split("_")[1]
        endPoint = all_params['url']
        body = dict(
            trade=1,
            firstCurrency=firstcurrency,
            secondCurrency=secondcurrency,
            secret=user['secret'],
            key=user['key']
        )
        response = requests.post(url=endPoint,data=body)

    if response.status_code == 200:
        response = convert_unicode(response.json())
        result = create_success_msg(response)
    else:
        response = response.status_code
        msj  = "Error on request %s" %(response)
        result = create_error_msg(msj)
    return result    

def getFormat():
    model = PlayModel()
    result = model.getFormatOrderBook()

    if result["success"] == True:
        response = result["datos"]
        return response
    else:
        logging.info(result["mensaje"])
        return None


def execute_Deph(play, bot_used):
    trade_controller = TradingController()
    if bot_used["Formats"] and bot_used["Pairs"] and bot_used["Users"]:
        bot_used['Formats'] = bot_used['Formats'][0]
        cripto_prices = trade_controller.getMarketPrice(bot_used['Pairs'][0]['id_pair'])
        if cripto_prices:
            var_buy = play['alt_buy_spread']
            var_sell = play['alt_sell_spread']
            buy_spread = bot_used['botConfiguration']['buy_spread']
            sell_spread = bot_used['botConfiguration']['sell_spread']

            # Generate prices and amount
            prices = calcPrices(
                buy_spread, 
                sell_spread, 
                cripto_prices, 
                float(var_buy), 
                float(var_sell)
            )
            amount = round(
                uniform(
                    float(bot_used['botConfiguration']['min_amount']), 
                    float(bot_used['botConfiguration']['max_amount'])
                ), 
                8
            )

            # Asign data pair
            PlayController.data['pair'] = bot_used['Pairs'][0]['pair']
            PlayController.data['firstcurrency'] = bot_used['Pairs'][0]['firstcurrency']
            PlayController.data['secondcurrency'] = bot_used['Pairs'][0]['secondcurrency']
            PlayController.data['trade'] = bot_used['botConfiguration']['trading_type_id']

            # Generate Times
            if bot_used['botConfiguration']['execute_time'] > play['alt_execute_time']:
                execute_time = randint(
                    play['alt_execute_time'], 
                    bot_used['botConfiguration']['execute_time']
                )
            else:
                execute_time = randint(
                    bot_used['botConfiguration']['execute_time'], 
                    play['alt_execute_time']
                )

            # Define Order
            try:
                if play['order_type'] == 'both':
                    for i in range(2):
                        dataTemp = PlayController.data
                        if i == 0:
                            PlayController.data['type'] = 'buy'
                            PlayController.data['price'] = prices['buy']
                            priceMarket = cripto_prices['buy_marketprice']
                            PlayController.data['amount'] = str(
                                round((amount * prices['buy']), 8)
                            )
                        else:
                            PlayController.data['type'] = 'sell'
                            PlayController.data['price'] = prices['sell']
                            priceMarket = cripto_prices['sell_marketprice']
                            PlayController.data['amount'] = str(amount)

                        formats_temp = bot_used['Formats']['params']
                        bot_used['Formats'] = paramsMerge(bot_used['Formats'])

                        # Define Log 
                        log = dict(
                            amount=str(amount),
                            priceMarket=priceMarket,  
                            id_bots_play=play['id_bots_play'],
                            type=PlayController.data['type'],
                        )

                        # Send Task
                        createOrder.apply_async(
                            queue="createOrder",
                            countdown=execute_time,
                            routing_key="createOrder.import",
                            args=[bot_used['Users'][0], bot_used['Formats'], log],
                        )

                        bot_used['Formats']['params'] = formats_temp
                        PlayController.data = dataTemp
                else:
                    PlayController.data['type'] = play['order_type']
                    PlayController.data['price'] = prices[play['order_type']]
                    if play['order_type'] == 'buy':
                        priceMarket = cripto_prices['buy_marketprice']
                        PlayController.data['amount'] = str(
                            round((amount * prices[play['order_type']]), 8)
                        )
                    else:
                        priceMarket = cripto_prices['sell_marketprice']
                        PlayController.data['amount'] = str(amount)
                    bot_used['Formats'] = paramsMerge(bot_used['Formats'])

                    # Define Log
                    log = dict(
                        amount=str(amount),
                        priceMarket=priceMarket,
                        id_bots_play=play['id_bots_play'],
                        type=PlayController.data['type'],
                    )

                    # Send Task
                    createOrder.apply_async(
                        queue="createOrder",
                        countdown=execute_time,
                        routing_key="createOrder.import",
                        args=[bot_used['Users'][0], bot_used['Formats'], log],
                    )

            except Exception as e:
                msj = "Error in execute_Deph: %s" %(str(e))
                logging.warning(msj)   
        else:
            logging.info("Not found priceMarket in execute_DephTask")
            updateMarketPrice.apply_async(
                queue="helpUdpPrice", 
                routing_key='helpUdpPrice.import',
                args=[ bot_used['Pairs'][0]],
            )


def calcPrices(buy_spread, sell_spread, cripto_prices, var_buy, var_sell):
    buy_spread = buy_spread / 100
    sell_spread = sell_spread / 100
    var_buy = var_buy / 100
    var_sell = var_sell / 100
    spreadBuyPrice = (buy_spread * cripto_prices['buy_marketprice']) + cripto_prices['buy_marketprice']
    spreadSellPrice = (sell_spread * cripto_prices['sell_marketprice']) + cripto_prices['sell_marketprice']
    variationBuyPrice = (var_buy * spreadBuyPrice) + spreadBuyPrice
    variationSellPrice = (var_sell * spreadSellPrice) + spreadSellPrice

    buyPrice = uniform(spreadBuyPrice, variationBuyPrice)
    sellPrice = uniform(spreadSellPrice, variationSellPrice)
    return {'buy': float('{0:.8f}'.format(buyPrice)), 'sell': float('{0:.8f}'.format(sellPrice))}


def eval_time(start, stop):
    formato_fecha = "%Y-%m-%d %H:%M:%S"
    fecha_inicial = datetime.strptime(start, formato_fecha)
    fecha_final = datetime.strptime(stop, formato_fecha)
    diferencia = fecha_final - fecha_inicial
    horas = diferencia.seconds / 3600
    residuo = int(diferencia.seconds) - int(horas * 3600)
    minutos = residuo / 60
    segundos = residuo - int(minutos * 60)
    return str(diferencia.days) + " Days " + str(horas) + " hours " + str(minutos) + " minutes " + str(
        segundos) + " seconds"


def purgeQueue():
    count = 0
    while count != 3:
        celery.control.purge()
        count += 1


@celery.task(name='createOrder')
def createOrder(user, formats_result, log):
    try:
        logging.info("Task Executed")
        logging.info(formats_result['params'])
        if formats_result['method'] == 'GET':
            if formats_result['params'] != '':
                endPoint = formats_result['link'] + formats_result['params']
            response = requests.get(endPoint)
        else:
            user_credentials = ast.literal_eval(user['credentials'])
            params = ast.literal_eval(formats_result['params'])
            data = dict(params.items() + user_credentials.items())
            if formats_result['data_type'] == 'JSON':
                data = json.dumps(data)
            endPoint = formats_result['url']
            response = request_post_url(endPoint, data)

        if response.status_code == 200:
            response = response.json()
            result = create_success_msg(str(convert_unicode(response)))
        else:
            result = create_error_msg('Conection Error, Code: ' + str(response.status_code))

        log['price'] = response['price'] if 'price' in response else '0'
        if 'order_id' in response:
            log['order_id'] = response['order_id']
        elif 'idOrder' in response:
            log['order_id'] = response['idOrder']
        else:
            log['order_id'] = 0
        log['response'] = result

        model = PlayModel()
        model.insertPlayLogs(log)
    except Exception, e:
        error_cod = 500
        modulo = 'Plays-controller'
        description = 'Error sending order: ' + str(e)
        set_BackLogs(error_cod, modulo, description)
        raise e
    finally:
        return True


@celery.task(name='addVolume')
def addVolume(dict_orders):
    """ TaskCelery: Genera un userBot Principal
    :param user: dict - credenciales del user select random
    :param formats_result: dict - formatos para obtencion de info
    """

    # Ordenes entregadas:
    list_orders = dict_orders['volume_orders']
    data = list_orders
    url = data[0]['format']['url']

    # HTTP Request para creacion de ordenes de volumen:
    response = requests.post(url=url, json=data, headers={'Content-type':'application/json'})
        
    # Validacion de http request status:
    result = None
    if response.status_code == 200:
        response = response.json()
        if response["status"] == True:
            result = response
        else:
            result = str(response["msg"])
    else:
        result = 'Conection Error, Code: ' + str(response)

    # Orden principal para obtener data generica:
    order_main = data[0]

    # Almacenamiento en Log:
    log = dict(
        response=result,
        id_bots_play=order_main['format']["id_bots_play"],
        type=order_main['format']["params"]["new"]["typeOrder"],
        price=response["price"] if 'price' in response else 0,
        amount=response["amount"] if 'amount' in response else 0,
        order_id=response["order_id"] if 'order_id' in response else 0,
    )
    model = PlayModel()
    model.insertPlayLogs(log)
   
    return True
    
