# -*- coding: utf-8 -*-
import json, ast, sqlalchemy, logging
from flask import session
from app import genericConect, set_log
from app.commons import (
    datetimeconv, 
    convert_unicode, 
    create_error_msg,
    create_success_msg, 
)


class CoinModel():

    def coinAll(self, type_coin='A'):
        try:
            store1 = 'sp_bots_coins_listar'
            store2 = 'sp_bots_api_link_obtener'

            info = []

            if type_coin == 'A': 
                list_coins = genericConect(store1, ' ')

            elif type_coin == 'C':
                list_coins = genericConect(store1, 'C')
            else:
                list_coins = genericConect(store1, 'F')
            
            for coin in list_coins:
                data = dict(
                    id=coin[0],
                    name=coin[1],
                    type=coin[2],
                    con_buy=float(coin[3]),
                    con_sell=float(coin[4]),
                    status="A" if coin[5] == "active" else "D"
                )

                api_links = genericConect(store2, [coin[0]])

                if not str(api_links[0][0]) == "FALSE":
                    list_afi = []
                    for api_link in api_links:
                        list_afi.append({
                            "id" : api_link[0],
                            "meth" : api_link[3],
                            "name_fiat" : coin[1],
                            "link" : [api_link[2]],
                            "param" : api_link[5],
                            "coin_ref" : api_link[7],
                            "data_type" : api_link[4],
                            "id_criptocoin" : coin[0],
                            "coordinates" : api_link[6]
                        })
                    data["api_links"] = list_afi

                info.append(data)
            return info
        except sqlalchemy.exc.InternalError, e:
            raise e

    def coinInsert(self, data):
        try:
            store1 = 'sp_bots_coins_insertar'
            store2 = "sp_bots_api_link_insertar"
            lista = [
                data["name"].upper(),
                data["type"],
                float(data['con_buy']),
                float(data['con_sell']),
                1
            ]
            if data["type"]=='C' and data["links"][0].values()==[False]:
                sms=(('Not register: api link can\'t be empty.',),)
                jsonData={
                    'success':False,
                    'msg':sms
                    }
                return json.dumps(jsonData, default=datetimeconv)
            else:
                res = genericConect(store1, lista)
                json_data={
                        'success':True,
                        'datos':res
                        }
                if res:
                    if data["type"]=='F' and len(data["links"])==0 and type(res[0][0]) is int:
                        return json.dumps(json_data, default=datetimeconv)
                    else:
                        if len(data["links"])!=0 and type(res[0][0]) is int:
                            lista2 = []
                            tmp_data = convert_unicode(data["links"][0])
                            lista2.append(res[0][0])
                            lista2.append(str(tmp_data["link"]))
                            lista2.append(str(tmp_data["meth"]))
                            lista2.append(str(tmp_data["data_type"]))
                            lista2.append(str(tmp_data["coordinates"]))
                            lista2.append(str(tmp_data["param"]))
                            lista2.append("USD")
                            res2 = genericConect(store2, lista2)
                            if res2:
                                return json.dumps(json_data, default=datetimeconv)
                            else:
                                
                                logging.info("Link not inserted.")
                                return json.dumps(json_data, default=datetimeconv) 
                        else:
                            json_data_={
                                    'success':False,
                                    'msg':res
                                    }
                            return json.dumps(json_data_, default=datetimeconv)
                            logging.info("Link no found for coin.")
                else:
                    logging.info("Coin not inserted.")
        except sqlalchemy.exc.InternalError, e:
            raise e

    def coinUpdate(self, data):
        try:
            lista = []
            lista.append(data["id"])
            lista.append(data["name"])
            lista.append(data["type"])
            lista.append(float(data['con_buy']))
            lista.append(float(data['con_sell']))
            lista.append(1 if data["status"] == "A" else 2)
            lista.append(int(session['id_user']))

            store = "sp_bots_coins_modificar"
            res = genericConect(store, lista)
            if res:
                return json.dumps(res, default=datetimeconv)
            else:
                logging.info("Coin not updated.")

            return json.dumps(res, default=datetimeconv)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def loadLinks(self,data):
        try:
            result = create_success_msg('Error')
            if data["links"][0]:
                tmp_data = convert_unicode(data["links"][0])
                valid = self.validateCoinref(tmp_data["coin_ref"], data["id_criptocoin"])
                if(valid != True):
                    raise Exception(valid)

                lista = [
                    data["id_criptocoin"],
                    str(tmp_data["link"]),
                    str(tmp_data["meth"]),
                    str(tmp_data["data_type"]),
                    str(tmp_data["coordinates"]),
                    str(tmp_data["param"]),
                    str(tmp_data["coin_ref"])
                ]

                store = "sp_bots_api_link_insertar"
                res = genericConect(store, lista)
                if len(res)>0:
                    if res:
                        result = create_success_msg(res)
                    else:
                        result = create_success_msg("Link not inserted.")
                        logging.info("Link not inserted.")
                else:
                    sms=(('Connection failed, please try again.',),)
                    result = create_success_msg(sms)
                    result = json_data_
        except Exception as e:
            result = create_success_msg(str(e))
        finally:
            return result

    def updateLinks(self, data):
        try:
            store = "sp_bots_api_link_modificar"
            tmp_data = convert_unicode(data["links"][0])
            valid = self.validateCoinref(tmp_data["coin_ref"], data["coin_id"])
            if(valid != True):
                raise Exception(valid)
            lista = [
                int(data["coin_id"]),
                int(data["id"]),
                str(tmp_data["link"]),
                str(tmp_data["meth"]),
                str(tmp_data["data_type"]),
                str(tmp_data["param"]),
                str(tmp_data["coordinates"]),
                str(tmp_data["coin_ref"])
            ]
            lista.append(int(session['id_user']))
            res = genericConect(store, lista)
            if len(res)>0:
                if res:
                    res = create_success_msg(res)
                    return res
                else:
                    logging.info("Link not updated.")
            else:
                res = create_error_msg('Connection failed, please try again.')
        except Exception as e:
            res = create_error_msg(str(e))
        finally:
            return res

    def CurrencyRate(self):
        try:
            list_coins = genericConect('sp_bots_coins_listar', ' ')
            data = []
            for coin in list_coins:
                data.append(dict(
                    id=coin[0],
                    name=coin[1],
                    type=coin[2],
                    con_buy=float(coin[3]),
                    con_sell=float(coin[4]),
                    status="A" if coin[5] == "active" else "D"
                ))
            return json.dumps(data)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def validateCoinref(self, coin_ref, coin_id):
        try:
            result = 'Error on validateCoinref'
            if(coin_ref):
                getcoin = genericConect('sp_bots_coins_obtener',[coin_ref], False)
                if len(getcoin) == 1 and isinstance(getcoin, tuple):
                    result = getcoin[0]
                elif isinstance(getcoin, tuple):
                    if getcoin[0] == coin_id:
                        result = 'Coin ref must be different from coin'
                    else:
                        result = True
                else:
                    result = 'Error gettin coin'
            else:
                result = 'coin_ref must not be null'
        except Exception as e:
            result = str(e)
        finally:
            return result

    def getCoin(self, coin):
        try:
            result = False
            getcoin = genericConect('sp_bots_coins_obtener',[coin], False)
            if isinstance(getcoin, tuple):
                result = getcoin
            else:
                raise NameError("%s NOT FOUND" %(coin)) 
        except Exception as e:
            logging.info("getCoin on Coins.models: %s" %(coin))
        finally:
            return result

