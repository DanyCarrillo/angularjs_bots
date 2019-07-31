# -*- coding: utf-8 -*-
import json, ast, sqlalchemy, logging
from flask import session
from app import  genericConect, set_log
from app.commons import (
    datetimeconv, 
    convert_unicode, 
    create_error_msg,
    create_success_msg, 
)
from app.trading.models import TradingModel
from app.bots.models import BotModel

class OrdersModel():

    def Show_AllActivesOrdersByUser(self, data):
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        bot = BotModel()
        tradin = TradingModel()
        try:
            res = []
            # Obtener listado de bots segun el usuario loggeado (no user exchange):
            vec_bots = bot.Show_Bot({'tipo':data['tipo']})
            if vec_bots['code']==201:
                bots_userExchange = []
                for vb in vec_bots['data']:
                    if vb['exchangeUsername']==data['usernameExchange'] and vb['status']==1:
                        bots_userExchange.append(vb) 

                # Get uniques config bots:
                bots_userExchangeYpair = [b for b in bots_userExchange if b['pair']==data['pair']]
                aux = []
                for i,b in enumerate(bots_userExchangeYpair):
                    if i==0:
                        aux.append(b)
                    else :
                        if b['TradingName']!=aux[i-1]['TradingName'] and b['idTradingType']!=aux[i-1]['idTradingType']:
                            aux.append(b)
                bots_userExchangeYpair = aux

                # Obtener las ordenes realizadas por cada bot:
                vec_tradin = []
                for b in bots_userExchangeYpair:
                    post_order = dict();
                    post_order['idBot'] = b['idBot']
                    post_order['pair'] = data['pair']
                    post_order['idBotType'] = data['idBotType']
                    post_order['tipo'] = data['tipo']
                    vec_tradin.append(tradin.Show_ActiveOrdersByBot(post_order))
                
                # Acumulado de listado de ordenes activas:
                res = vec_tradin
            else:
                res = []

            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201 if res else 203
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e

    def Show_OrdersByUserYPair(self, data):
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        bot = BotModel()
        tradin = TradingModel()
        try:
            rp = tradin.Show_ActiveOrdersByUserYPair(data)
            res = [] if rp['code']==203 else rp['data'][0]
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201 if res else 203
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e
