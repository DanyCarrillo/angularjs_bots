import sqlalchemy, json, requests
from flask import render_template, jsonify
from app import r
from app.bots.models import BotModel
from app.exchanges.models import ExchangeModel
from app.commons import create_success_msg, val_num_slash
from datetime import datetime
from flask import json, request
from app import genericConect
from app.trading.controller import eval_time

class BotsController(object):

    def __init__(self):
        pass

    @staticmethod
    def list():
        return render_template('botConfig/index.html')

    def listBotsAll(self, res):
        try:
            model = BotModel()
            all = False
            if val_num_slash(res.path, 3):
                all = True

            res = model.botsAllList(all) if (all)else model.botsAllList(False)
            res = json.loads(res)
            return create_success_msg(res)
        except sqlalchemy.exc.InternalError as e:
            raise e

    def addBotConfig(self, res):
        try:
            data = res.get_json()
            model = BotModel()
            res = model.BotConfigInsert(data)
            #Set_log
            action='Creacion de Bot'
            set_log(action,res)
            return create_success_msg(res)
        except sqlalchemy.exc.InternalError as e:
            raise e

    def updBotConfig(self, res):
        try:
            data = json.dumps(res.get_json())
            data = json.loads(data)
            if data.get('id') is None:
                data['id'] = None
            if data.get('status') is None:
                data['status'] = None
            if data.get('id_api_user') is None:
                data['id_api_user'] = None
            if data.get('id_criptocoin') is None:
                data['id_criptocoin'] = None
            if data.get('id_coin_fiat') is None:
                data['id_coin_fiat'] = None
            if data.get('var_buy') is None:
                data['var_buy'] = 0
            if data.get('var_sell') is None:
                data['var_sell'] = 0
            if data.get('mar_buy') is None:
                data['mar_buy'] = 0
            if data.get('mar_sell') is None:
                data['mar_sell'] = 0
            if data.get('max_btc') is None:
                data['max_btc'] = None
            if data.get('min_btc') is None:
                data['min_btc'] = None
            if data.get('tim_trading') is None:
                data['tim_trading'] = None
            model = BotModel()
            res = model.BotConfigUpdate(data)
             #Set_log
            all_data={'old_value':data,'new_value':res}
            action='Modificacion de Bot'
            set_log(action,all_data)

            return create_success_msg(res)
        except sqlalchemy.exc.InternalError as e:
            raise e
            getTypesBot

    # Adaptacion API v1.0
    # Metodos API independientes:
    # Modelo: modelo (models.py)
    def getTypesBot(self):
        try:
            model = BotModel()
            res = model.getTypesBot()
            return jsonify(res)
        except sqlalchemy.exc.InternalError as e:
            raise e

    def showBot(self):
        try:
            data = request.json
            model = BotModel()
            res = model.Show_Bot(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def selectCryptoPricesPair(self):
        try:
            data = request.json
            model = BotModel()
            res = model.Select_CryptoPricesPair(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def insertBot(self):
        try:
            data = request.json
            model = BotModel()
            res = model.Insert_Bot(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def updateBot(self):
        try:
            data = request.json
            bot = BotModel()
            exchange = ExchangeModel()

            # Monedas:
            currencies = (data['pair']).split('/')
            first_currency = currencies[0]
            second_currency = currencies[1]

            # Actualizacion de precio par BTC/USD:
            buy_btc_in_usd = None
            par = exchange.Select_PairPorNombre({'pair':'BTC/USD'})
            idBTCyUSD = par['data']
            now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            last_load = r.hget('last_save', idBTCyUSD)
            if eval_time(now_time, last_load):
                resul = r.hget('cripto_prices', idBTCyUSD)
                if resul:
                    json_res = json.loads(resul)
                    buy_btc_in_usd = "%.8f" % float(json_res['buy_marketprice'])
            else:
                res = bot.Select_CryptoPricesPair({'idPair':idBTCyUSD})
                buy_btc_in_usd = res['data'][0]['buyMarketPrice']
            buy_btc_in_usd = float(buy_btc_in_usd)

            """
            BEGIN - ACTUALIZACION DE PRECIOS
            """

            # Actualizacion caso Fiat/Fiat:
            if data['TypeCoinsPair']=='F/F':

                # Precio - firstCurrency/USD:
                priceFIRSTinUSD = None
                par = exchange.Select_PairPorNombre({'pair':first_currency+'/USD'})
                idFIRSTyUSD = par['data']
                now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                last_load = r.hget('last_save', idFIRSTyUSD)
                if eval_time(now_time, last_load):
                    resul = r.hget('cripto_prices', idFIRSTyUSD)
                    if resul:
                        json_res = json.loads(resul)
                        priceFIRSTinUSD = "%.8f" % float(json_res['buy_marketprice'])
                else:
                    res = bot.Select_CryptoPricesPair({'idPair':idFIRSTyUSD})
                    priceFIRSTinUSD = res['data'][0]['buyMarketPrice']
                priceFIRSTinUSD = float(priceFIRSTinUSD)

                # Update Price:
                convert_to_crypt_min = float(data['minUSD'])/float(priceFIRSTinUSD)
                convert_to_crypt_max = float(data['maxUSD'])/float(priceFIRSTinUSD)
                data['minAmount'] = round(convert_to_crypt_min,8)
                data['maxAmount'] = round(convert_to_crypt_max,8)

            else:

                if first_currency=='BTC':

                    # Update Price:
                    convert_to_crypt_min = data['minUSD']/buy_btc_in_usd
                    convert_to_crypt_max = data['maxUSD']/buy_btc_in_usd
                    data['minAmount'] = round(convert_to_crypt_min,8)
                    data['maxAmount'] = round(convert_to_crypt_max,8)

                else:

                    # Precio - firstCurrency/secondCurrency:
                    price_in_second_currency = None
                    now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    last_load = r.hget('last_save', data['idPair'])
                    if eval_time(now_time, last_load):
                        resul = r.hget('cripto_prices', data['idPair'])
                        if resul:
                            json_res = json.loads(resul)
                            price_in_second_currency = "%.8f" % float(json_res['buy_marketprice'])
                    else:
                        res = bot.Select_CryptoPricesPair(data)
                        price_in_second_currency = res['data'][0]['buyMarketPrice']
                    price_in_second_currency = float(price_in_second_currency)

                    # Precio - firstCurrency/BTC:
                    price_first_currency_in_btc = None
                    par = exchange.Select_PairPorNombre({'pair':first_currency+'/BTC'})
                    idFIRSTyBTC = par['data']
                    now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    last_load = r.hget('last_save', idFIRSTyBTC)
                    if eval_time(now_time, last_load):
                        resul = r.hget('cripto_prices', idFIRSTyBTC)
                        if resul:
                            json_res = json.loads(resul)
                            price_first_currency_in_btc = "%.8f" % float(json_res['buy_marketprice'])
                    else:
                        res = bot.Select_CryptoPricesPair({'idPair':idFIRSTyBTC})
                        price_first_currency_in_btc = res['data'][0]['buyMarketPrice']
                    price_first_currency_in_btc = float(price_first_currency_in_btc)

                    # Update Price:
                    if second_currency=='BTC':
                        convert_to_btc_min = float(data['minUSD'])/price_in_second_currency
                        convert_to_btc_max = float(data['maxUSD'])/price_in_second_currency
                        convert_to_crypt_min = convert_to_btc_min/buy_btc_in_usd
                        convert_to_crypt_max = convert_to_btc_max/buy_btc_in_usd
                        data['minAmount'] = round(convert_to_crypt_min,8)
                        data['maxAmount'] = round(convert_to_crypt_max,8)
                    elif second_currency=='USD':
                        convert_to_crypt_min = float(data['minUSD'])/price_in_second_currency
                        convert_to_crypt_max = float(data['maxUSD'])/price_in_second_currency
                        data['minAmount'] = round(convert_to_crypt_min,8)
                        data['maxAmount'] = round(convert_to_crypt_max,8)
                    else:
                        convert_to_crypt_min = float(data['minUSD'])/(price_first_currency_in_btc*buy_btc_in_usd)
                        convert_to_crypt_max = float(data['maxUSD'])/(price_first_currency_in_btc*buy_btc_in_usd)
                        data['minAmount'] = round(convert_to_crypt_min,8)
                        data['maxAmount'] = round(convert_to_crypt_max,8)
    
            """
            END - ACTUALIZACION DE PRECIOS
            """

            res = bot.Update_Bot(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e        

    def deleteBot(self):
        try:
            data = request.json
            model = BotModel()
            res = model.Delete_Bot(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e                

    def showBotYPlay(self):
        try:
            data = request.json
            model = BotModel()
            res = model.Show_BotYPlay(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e                        

    def verifyTypesBotAndTrading(self):
        try:
            model = BotModel()
            res = model.Verify_TypesBotAndTrading()
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e         