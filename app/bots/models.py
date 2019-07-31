import json, sqlalchemy
from flask import session
from app import genericConect, bots_per_page
from app.commons import datetimeconv
from app.plays.models import PlayModel
from app.trading.models import TradingModel
from app.users.models import UsersModel
from decimal import *
from dateutil.parser import parse
from datetime import datetime, timedelta

class BotModel():

    def botsAllList(self, all):
        try:
            store = "sp_bots_configurations_listar"
            if not all:
                list_bots = genericConect(store, [0])
            else:
                list_bots = genericConect(store, [int(session['id_user'])])

            lista = []
            for bot in list_bots:
                dicc = {}
                dicc["id"] = bot[0]
                dicc["id_pair"] = bot[1]
                dicc["name_pair"] = bot[2]
                dicc["name_user"] = bot[3]
                dicc["name_exchange"] = bot[4]
                dicc["type_trading"] = bot[5]
                dicc["max_btc"] = bot[6]
                dicc["min_btc"] = bot[7]
                dicc["var_buy"] = bot[8]
                dicc["var_sell"] = bot[9]
                dicc["tim_trading"] = bot[10]
                dicc["tim_completed"] = bot[11]
                dicc["type_bot"] = bot[12]
                if bot[13] == 1:
                    dicc["status"] = "A"
                else:
                    dicc["status"] = "D"
                dicc["name_t_trading"] = bot[14]    
                dicc["id_exchange"] = bot[15]
                dicc["bot_play_id"] = bot[18]
                dicc["bot_play_status"] = bot[17]
                dicc["bot_play_date"] = bot[16]
                lista.append(dicc)

            return json.dumps(lista, default=datetimeconv)
        except sqlalchemy.exc.InternalError as e:
            raise e

    def BotConfigInsert(self, data):
        try:
            lista = []
            store = "sp_bots_configurations_insertar"

            lista.append(int(session['id_user']))
            lista.append(data["id_pair"])
            lista.append(data["id_exchange"])
            lista.append(data["type_trading"])
            lista.append(data["max_btc"])
            lista.append(data["min_btc"])
            lista.append(data["var_buy"])
            lista.append(data["var_sell"])
            lista.append(data["tim_trading"])
            lista.append(data["tim_completed"])
            lista.append(data["type_bot"])
            lista.append(1)

            res = genericConect(store, lista)

            if res:
                for row in res:
                    dicc = {}
                    dicc["id"] = row[0]
                    dicc["id_user"] = row[1]
                    dicc["id_pair"] = row[2]
                    dicc["id_exchange"] = row[3]
                    dicc["type_trading"] = row[4]
                    dicc["max_btc"] = row[5]
                    dicc["min_btc"] = row[6]
                    dicc["var_buy"] = row[7]
                    dicc["var_sell"] = row[8]
                    dicc["tim_trading"] = row[9]
                    dicc["tim_completed"] = row[10]
                    dicc["status"] = row[11]
                    dicc["type_bot"] = row[14]

                return dicc
        except sqlalchemy.exc.InternalError as e:
            raise e

    # Adaptacion de Data de Entrada segun el Model
    # @autor avasquez
    # @Date 09/08/2018
    def getTypesBot(self):
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            resul = genericConect('sp_bots_bots_types_listar', [])
            res = []
            for r in resul:
                dic = dict()
                dic['idBotType'] = r[0]
                dic['name'] = r[1]
                res.append(dic)
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e

    def Show_Bot(self,data):
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            lst_input = [0 if data['tipo']==0 else int(session['id_user'])]
            resul = genericConect('sp_bots_configurations_listar', lst_input)
            res = []
            campos = ['idBot','idPair','pair','username','nameExchange','idTradingType','maxAmount','minAmount','buySpread','buyPercent','sellSpread','sellPercent','executeTime','completeTime','idBotType','status','TradingName','idExchange']
            for r in resul:
                dic = dict()
                i=0
                for c in campos: 
                    dic[c] = float(r[i]) if isinstance(r[i],Decimal) else r[i]
                    i=i+1
                dic['exchangeUsername'] = r[23]
                dic['maxUSD'] = r[24]
                dic['minUSD'] = r[25]
                res.append(dic)

            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201 if res else 203
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e

    def Select_CryptoPricesPair(self,data):
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            lst_input = [data['idPair']]
            resul = genericConect('sp_bots_crypto_prices_listar', lst_input)
            res = []
            if not isinstance(resul[0][0],unicode):
                campos = ['idCryptoPrice','idPair','pair','buyMarketPrice','sellMarketPrice','typeCalcule','status','idExchange','createdDate','modifiedDate']
                for r in resul:
                    dic = dict()
                    i=0
                    for c in campos: 
                        dic[c] = "%.8f" % float(r[i]) if isinstance(r[i],Decimal) else r[i]
                        i=i+1
                    res.append(dic)
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e        

    def Insert_Bot(self,data):
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            lst_input = [int(session['id_user']),data['idPair'],data['idExchange'],data['idTradingType'],data['maxAmount'],data['minAmount'],data['buySpread'],data['buyPercent'],data['sellSpread'],data['sellPercent'],data['executeTime'],data['completeTime'],data['idBotType'],data['status'],data['idUserExchange'],data['minUSD'],data['maxUSD']]
            lst_input_formato = [ (item.encode('utf-8') if isinstance(item,unicode) else item) for item in lst_input]
            resul = genericConect('sp_bots_configurations_insertar', lst_input_formato)
            res = []
            campos = ['idBot','idUserExchange']
            for r in resul:
                dic = dict()
                i=0
                for c in campos:
                    dic[c] = r[i]
                    i=i+1
                res.append(dic)

            # Get all data:
            bots_created = self.Show_Bot({'tipo':1})['data']
            bot_create = [sam for sam in bots_created if sam['idBot']==res[0]['idBot'] ][0]

            campos_general = ['idBot','idBotType','idTradingType','buySpread','buyPercent','sellPercent','sellSpread','completeTime','executeTime','minAmount','maxAmount','username','exchangeUsername','maxUSD','minUSD']
            campos_bot = ['idExchange','idPair','TradingName','nameExchange','pair','status']
            gen = dict()
            for g in campos_general:
                gen[g] = float(bot_create[g]) if isinstance(bot_create[g],Decimal) else bot_create[g]
            gen['idUser'] = int(session['id_user'])
            bot = dict()
            for b in campos_bot:
                bot[b] = bot_create[b]
            resp = dict()

            resp['general'] = gen
            resp['bot'] = bot
            resp['play'] = dict({'altExecuteTime':0})

            custom_res['data'] = resp if resp else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e        

    def Update_Bot(self,data):
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            lst_input = [data['idBot'],data['idUser'],data['idPair'],data['idExchange'],data['idTradingType'],data['maxAmount'],data['minAmount'],data['buySpread'],data['buyPercent'],data['sellSpread'],data['sellPercent'],data['executeTime'],data['completeTime'],data['idBotType'],data['status'],data['idUser'],data['minUSD'],data['maxUSD']]
            lst_input_formato = [ (item.encode('utf-8') if isinstance(item,unicode) else item) for item in lst_input]
            resul = genericConect('sp_bots_configurations_modificar', lst_input_formato)
            res = []
            campos = ['idBot','idUser','idPair','idExchange','idTradingType','maxAmount','minAmount','minUSD','maxUSD','buySpread','buyPercent','sellSpread','sellPercent','executeTime','completeTime','idBotType','status']
            for r in resul:
                dic = dict()
                i=0
                for c in campos:
                    dic[c] = float(r[i]) if isinstance(r[i],Decimal) else r[i]
                    i=i+1
                res.append(dic)
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e 

    def Delete_Bot(self,data):
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            lst_input = [data['idBot'],data['status'],data['idUser']] 
            resul = genericConect('sp_bots_configurations_retener', lst_input, False)
            if isinstance(resul[0],unicode):
                res = [resul[0]]
            else:
                res = []
                campos = ['idBot','status']    
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

    def Show_BotYPlay(self,data):
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        idUser = data['idUser']
        try:
            resul = genericConect('sp_bots_integration_listar', [data['idUser'],data['start']*bots_per_page,bots_per_page])
            res_sp = []
            campos = ['idBotResource','idUser','username','idExchangeUsername','exchangeUsername','idBot','idBotType','idTradingType','buySpread','sellSpread','buyPercent','sellPercent','completeTime','executeTime','minAmount','maxAmount','status','idExchange','idPair','TradingName','nameExchange','pair','statusPair','idBotPlay','altExecuteTime','altBuySpread','altSellSpread','orderType','playDate','stopDate','statusPlay','contPlays','maxUSD','minUSD']

            if idUser == 0:
                for r in resul:
                    d = dict()
                    for i,c in enumerate(campos):
                        d[c] = r[i]
                    res_sp.append(d)
            else:
                for r in resul:
                    if r[1] == idUser:
                        d = dict()
                        for i,c in enumerate(campos):
                            d[c] = r[i]
                        res_sp.append(d)

            campos_general = ['idBot','idBotType','idTradingType','buySpread','sellSpread','buyPercent','sellPercent','completeTime','executeTime','minAmount','maxAmount','maxUSD','minUSD','username','exchangeUsername','idUser']
            campos_bot = ['idExchange','idPair','TradingName','nameExchange','pair','status']

            res = []
            for rb in res_sp:
                json_general = dict()
                for g in campos_general:
                    json_general[g] = float(rb[g]) if isinstance(rb[g],Decimal) else rb[g]
                json_general['buyPercent'] = abs(json_general['buyPercent'])
                json_general['sellPercent'] = abs(json_general['sellPercent'])

                json_bot = dict()
                for b in campos_bot:
                    json_bot[b] = rb[b]

                json_play = dict()
                campos_play = []

                datetime_format = '%Y-%m-%d %H:%M:%S'
                t1 = str(rb['playDate']) if rb['stopDate']!=None else 0
                t2 = str(rb['stopDate']) if rb['stopDate']!=None else t1
                
                if t1>=t2:
                    campos_play = ['idBotPlay','altExecuteTime','altBuySpread','altSellSpread','orderType','playDate','statusPlay','contPlays']
                else:
                    campos_play = ['altExecuteTime','altBuySpread','altSellSpread','orderType','contPlays']      

                for p in campos_play:
                    if p == 'statusPlay':
                        json_play['status'] = rb[p]
                    elif p == 'playDate' and rb['playDate'] and rb['playDate'] != None:
                        aux = rb['playDate'] + timedelta(hours=-5) 
                        json_play['playDate'] = aux.strftime('%Y-%m-%d %H:%M:%S.%f')
                    else:
                        json_play[p] = rb[p]
                    
                JASON = dict()
                JASON['general'] = json_general
                JASON['bot'] = json_bot
                JASON['play'] = json_play

                res.append(JASON)

            custom_res['continue'] = True if len(resul)>0 else False
            custom_res['bots_per_page'] = bots_per_page
            custom_res['code'] = 201
            custom_res['data'] = res
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e      

    def Verify_TypesBotAndTrading(self):
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        model_trading = TradingModel()
        try:
            res = dict()
            typesbot = self.getTypesBot()['data'] if self.getTypesBot()['data']!='[WARNING] Data empty from store procedure' else ''
            typestrading = model_trading.getTypesTrading()['data'] if model_trading.getTypesTrading()['data']!='[WARNING] Data empty from store procedure' else ''
            idtypebot = [sam['idBotType'] for sam in typesbot if sam['idBotType']=='D']
            idtradingtype = [sam['idTradingType'] for sam in typestrading if sam['idTradingType']==1]
            res['idBotType'] = idtypebot[0]
            res['idTradingType'] = idtradingtype[0]
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e      

