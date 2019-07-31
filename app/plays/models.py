import sqlalchemy, json, ast, logging
from flask import session
from app import  genericConect
from app.commons import (
    datetimeconv,
    create_error_msg,
    create_success_msg,
    decrypt
)
from app.exchanges.models import ExchangeModel

class PlayModel:
    
    def getBotsData(self, id, type):
        try:
            list_bots = genericConect('sp_bots_configurations_obtener', [id, type], True)
            json_data = []
            for bot in list_bots:
                if len(list_bots) == 1:
                    json_data = {
                        'id_bot_configuration': bot[0],
                        'username': bot[1],
                        'exchange_name': bot[2],
                        'trading_type': bot[3],
                        'bot_type': bot[4],
                        'status': bot[5],
                        'max_amount': bot[6],
                        'min_amount': bot[7],
                        'buy_spread': bot[8],
                        'sell_spread': bot[9],
                        'execute_time': bot[10],
                        'complete_time': bot[11],
                        'created_date': bot[12]
                    }
                else:
                    json_data.append({
                        'username': bot[1],
                        'exchange_name': bot[2],
                        'trading_type': bot[3],
                        'bot_type': bot[4],
                        'status': bot[5],
                        'max_amount': bot[6],
                        'min_amount': bot[7],
                        'buy_spread': bot[8],
                        'sell_spread': bot[9],
                        'execute_time': bot[10],
                        'complete_time': bot[11],
                        'created_date': bot[12]
                    })
            return json.dumps(json_data, default=datetimeconv)
        except sqlalchemy.exc.InternalError as e:
            raise e

    def savePlay(self, data):
        try:
            save = genericConect('sp_bots_bots_play_insertar', data, False)
            return {'id_bot_play': save[0]} if save[0] is int else {'error': save[0]}
        except sqlalchemy.exc.InternalError as e:
           raise e

    def stopPlay(self, data):
        try:
            stop = genericConect('sp_bots_bots_play_update_stop', data, False)
            return True if stop[0] == 'True' else {'error': stop[0]}
        except sqlalchemy.exc.InternalError as e:
           raise e

    def listPlays(self, status):
        try:
            list = genericConect('sp_bots_bots_play_listar', [status, 0], True)
            list_plays = []
            for play in list:
                list_plays.append({
                    'id_bots_play': play[0],
                    'username_play': play[1],
                    'bots_configuration_id': play[2],
                    'order_type': play[3],
                    'alt_execute_time': play[4],
                    'play_date': play[5],
                    'alt_buy_spread': play[6],
                    'alt_sell_spread': play[7],
                    'status': play[8],
                    'botConfiguration': {
                        'max_amount': play[9],
                        'min_amount': play[10],
                        'buy_spread': play[11],
                        'sell_spread': play[12],
                        'execute_time': play[13],
                        'complete_time': play[14],
                        'trading_type_id': play[15],
                        'bot_type_id': play[16],
                        'pair_id': play[17],
                        'firstcurrency': play[18],
                        'secondcurrency': play[19],
                        'cancel_buy': play[20],
                        'cancel_sell': play[21],
                    },
                    'username_stop': play[20] if len(play) == 24 else '',
                    'stop_date': play[21] if len(play) == 24 else '',
                })
            return json.dumps(list_plays, default=datetimeconv)
        except sqlalchemy.exc.InternalError as e:
           raise e

    def getBotCombine(self, bot_id, type):
        model_exchange = ExchangeModel()
        try:
            data = genericConect('sp_bots_all_combine', [bot_id, type], True)
            data_lst = [list(d) for d in list(data)]
            data_lst[1][1] = (model_exchange.Select_PairPorNombre({'pair':data_lst[1][4]}))['data']
            if type == "V":
                data_combine = merge_data(data_lst)
                return json.dumps(data_combine)
            else:
                data_combine = getCombine(data_lst)
                return json.dumps(data_combine, default=datetimeconv)
        except sqlalchemy.exc.InternalError as e:
            raise e

    def insertPlayLogs(self, log):
        try:
            data = [log['id_bots_play'],
                    log['type'],
                    log['price'] if not "priceMarket" in log else log['priceMarket'],
                    log['amount'],
                    log['order_id'],
                    str(log['response'])
                    ]
            insert = genericConect('sp_bots_play_logs_insertar', data, False)
            return True
        except sqlalchemy.exc.InternalError as e:
            raise e

    def getFormatOrderBook(self):
        try:
            response = genericConect("sp_bots_ob_api_listar", [])
            if response:
                data = dict(
                    url=response[0][1],
                    method=response[0][2],
                    params=response[0][4],
                    data_type=response[0][3],
                )
                response = create_success_msg(data)
            else:
                raise ValueError(404)
        except ValueError:
            msj = "Exception on sp_bots_ob_api_listar"
            response = create_error_msg(msj)
        except sqlalchemy.exc.InternalError as e:
            response = create_error_msg(e)
        finally:
            return response

    # Adaptacion de Data de Entrada segun el Model
    # @autor avasquez
    # @Date 09/08/2018
    def Insert_BotPlay(self,data):
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            lst_input = [data['idUser'],data['idBot'],data['orderType'],data['altExecuteTime'],data['altBuySpread'],data['altSellSpread']]
            lst_input_formato = [ (item.encode('utf-8') if isinstance(item,unicode) else item) for item in lst_input]
            res = genericConect('sp_bots_bots_play_insertar', lst_input_formato)
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e 

    def Show_BotPlay(self,data):
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            lst_input = [data['status'],data['idBot']]
            lst_input_formato = [ (item.encode('utf-8') if isinstance(item,unicode) else item) for item in lst_input]
            resul = genericConect('sp_bots_bots_play_listar', lst_input_formato)
            res = []
            campos = ['idBotPlay','username','idBot','orderType','altExecuteTime','playDate','altBuySpread','altSellSpread','status','maxAmount','minAmount','buySpread','sellSpread','executeTime','completeTime','idTradingType','idBotType']
            for r in resul:
                dic = dict()
                i=0
                for c in campos:
                    dic[c] = r[i]
                    i=i+1
                dic['contPlays'] = (self.Show_countPlayByBot({'idBot':data['idBot']}))['data']
                res.append(dic)
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e

    def Show_countPlayByBot(self,data):
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            lst_input = ['inactive',data['idBot']]
            resul = genericConect('sp_bots_bots_play_listar', lst_input)
            res = len(resul)
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e

    def Update_BotPlay(self,data):
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            lst_input = [data['idBotPlay'],data['idUser']]
            lst_input_formato = [ (item.encode('utf-8') if isinstance(item,unicode) else item) for item in lst_input]
            res = genericConect('sp_bots_bots_play_update_stop', lst_input_formato)
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e

    def lastUpdate_BotPlay(self,data):
        custom_res = dict()
        custom_res['data'] = ''
        custom_res['code'] = 200
        try:
            resul = self.Show_BotPlay(data)
            campos = ['idBot','altExecuteTime','altBuySpread','altSellSpread','orderType']
            res = []
            if resul['data']!='[WARNING] Data empty from store procedure':
                res_temp = []
                for r in resul['data']:
                    dic = dict()
                    for c in campos:
                        dic[c] = r[c]
                    res_temp.append(dic)
                tam = len(resul['data'])
                res = res_temp[tam-1]
            custom_res['data'] = res if res else '[WARNING] Data empty from store procedure'
            custom_res['code'] = 201
            return custom_res
        except sqlalchemy.exc.InternalError, e:
            raise e

    def getPlayList(self, id_bot):
        try:
            list = genericConect('sp_bots_bots_play_listar', ['All', id_bot], True)
            list_plays = []
            for play in list:
                list_plays.append({
                    'id_bots_play': play[0],
                    'user_play': play[1],
                    'bots_configuration_id': play[2],
                    'typ_trading': play[3],
                    'alt_execute_time': play[4],
                    'dat_play': play[5],
                    'alt_buy_spread': play[6],
                    'alt_sell_spread': play[7],
                    'status': play[8],
                    'user_stop': play[22] if len(play) == 24 else '',
                    'dat_stop': play[23] if len(play) == 24 else '',
                })
            pos_trade_active = 0
            trade_active = []
            for i,lp in enumerate(list_plays):
                if lp['dat_stop'] == None:
                    pos_trade_active = i
                    trade_active.append(lp)
            del list_plays[pos_trade_active]
            list_plays_reorded = trade_active + [ list_plays[len(list_plays)-i-1] for i,lp in enumerate(list_plays) ]
            return json.dumps(list_plays_reorded, default=datetimeconv)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def getPlayLog(self, id_play):
        try:
            list = genericConect('sp_bots_play_logs_obtener', [id_play], True)
            list_plays = []
            for play in list:
                list_plays.append({
                    'id_play_log': play[0],
                    'bot_play_id': play[1],
                    'type': play[2],
                    'price': play[3],
                    'amount': play[4],
                    'response': play[5],
                    'date': play[6],
                    'order_id': play[7]
                })
            return json.dumps(list_plays, default=datetimeconv)
        except sqlalchemy.exc.InternalError, e:
            raise e


def getCombine(combine_result):
    data_pair = {}
    data_error = {}
    data_users = {}
    data_exchange = {}
    data_formats = {}
    data_combine = {
        "Exchange":[],
        "Users":[],
        "Formats":[],
        "Pairs":[]
    }
    try:
        for combine in combine_result:
            if combine[0] == 'EX':
                data_exchange['exchange_name'] = combine[2]
                data_exchange['type'] = combine[3]
                data_exchange['priority'] = combine[4]
                data_combine['Exchange'].append(data_exchange if data_exchange else '')
            elif combine[0] == 'UE':
                data_users['username'] = combine[2]
                data_users['credentials'] = decrypt(combine[3])
                data_combine['Users'].append(data_users if data_users else '')
            elif combine[0] == 'EF':
                data_formats['format_name'] = combine[2]
                data_formats['url'] = combine[3]
                data_formats['method'] = combine[4]
                data_formats['data_type'] = combine[5]
                data_formats['params'] = combine[6]
                data_combine['Formats'].append(data_formats if data_formats else '')
            elif combine[0] == 'PA':
                data_pair['id_pair'] = combine[2]
                data_pair['firstcurrency'] = combine[3]
                data_pair['secondcurrency'] = combine[4]
                data_pair['pair'] = combine[5]
                data_combine['Pairs'].append(data_pair if data_pair else '')
            else:
                data_error = combine[0]
                data_combine = data_error

        return data_combine
    except sqlalchemy.exc.InternalError, e:
        raise e

def merge_data(all_data):
    dicc = {}
    list_ex = []
    list_usu = []
    list_pair = []
    list_formats = []

    try:
        for data in all_data:
            if data[0] == 'EX':
                list_ex.append({
                    'exchange_name': data[2],
                    'type': data[3],
                    'priority': data[4]
                })
            elif data[0] == 'UE':
                list_usu.append({
                    'username': data[2],
                    'credentials': decrypt(data[3])
                })
            elif data[0] == 'EF':
                list_formats.append({
                    'format_name': data[2],
                    'url': data[3],
                    'method': data[4],
                    'data_type': data[5],
                    'params': data[6]
                })
            elif data[0] == 'PA':
                list_pair.append({
                    'id_pair': data[1],
                    'firstcurrency': data[2],
                    'secondcurrency': data[3],
                    'pair': data[4]
                })
            else:
                data_error = data[0]
                dicc = data_error
        dicc['Users'] = list_usu if list_usu else ""
        dicc['Exchange'] = list_ex if list_ex else ""
        dicc['Pairs'] = list_pair if list_pair else ""
        dicc['Formats'] = list_formats if list_formats else ""

        return dicc
    except sqlalchemy.exc.InternalError, e:
        raise e
