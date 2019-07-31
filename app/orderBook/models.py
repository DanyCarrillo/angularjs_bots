import json, sqlalchemy
from flask import session
from app import genericConect, bots_per_page
from app.commons import datetimeconv
from app.plays.models import PlayModel
from app.trading.models import TradingModel
from app.trading.models import ExchangeModel
from app.users.models import UsersModel
from decimal import *
from dateutil.parser import parse
from datetime import datetime, timedelta
import requests
import pandas as pd

class OrderBookModel():

    def orderBookListByPair(self, data):
        params = []
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        data_all = []
        dict_data = {}
        list_buy = []
        list_sell = []
        try:
            exchange = ExchangeModel()
            formatos = (exchange.Select_FormatExchange({'idExchange':1}))['data']
            url = [f[4] for f in formatos if f[3]=='BB']
            url_orderbook = url[0]
            response = requests.post(url=url_orderbook,data=json.dumps(data),headers={'Content-Type': 'application/json'})

            if response.status_code!=200:
                custom_res['data'] = '[WARNING]  No data, check endpoint.'
                custom_res['code'] = response.status_code
                return custom_res
                
            res = json.loads(response.content)
            """
            Begin Processing
            """

            # Seteo de diccionario BUY(response sell se convierte en buy)
            if type(res['SELL']) is list:
                for i in res['SELL']:
                    buy_dict = {}
                    buy_dict['username'] = i['username']
                    buy_dict['hora'] = i['Hora']
                    buy_dict['idOrder'] = i['idOrder']
                    buy_dict['price'] = i['Price']
                    buy_dict['flag'] = i['flag']
                    buy_dict['amount'] = i['Amount']
                    buy_dict['pair'] = i['Pair']
                    list_buy.append(buy_dict)
            dict_data['buy'] = list_buy

            # Seteo de diccionario SELL(response buy se convierte en sell)
            if type(res['BUY']) is list:
                for i in res['BUY']:
                    sell_dict = {}
                    sell_dict['username'] = i['username']
                    sell_dict['hora'] = i['Hora']
                    sell_dict['idOrder'] = i['idOrder']
                    sell_dict['price'] = i['Price']
                    sell_dict['flag'] = i['flag']
                    sell_dict['amount'] = i['Amount']
                    sell_dict['pair'] = i['Pair']
                    list_sell.append(sell_dict)
            dict_data['sell'] = list_sell
            data_all.append(dict_data)
            """
            End Processing
            """

            custom_res['data'] = data_all if data_all else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 200 if data_all else 400
            return custom_res
        except sqlalchemy.exc.InternalError as e:
            raise e