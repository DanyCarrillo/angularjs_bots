import json, sqlalchemy, logging, smtplib
from email.MIMEText import MIMEText
from flask import json
from flask import (
    jsonify,
    request,
    render_template,
)
from app import (
    app,
    celery,
    set_log,
    sanitizer,
    set_BackLogs,
    genericConect
)
from app.commons import (
    encrypt,
    create_error_msg,
    create_success_msg
)
from app.exchanges.models import *
from app.exchanges.models import ExchangeModel
from app.external_exchange import binance_controller
from app.external_exchange.okex import getBalanceOkex
from app.external_exchange.huobi import getBalanceHuobi
from app.external_exchange.bitstamp_controller import PrivateBit


private_bit = PrivateBit()


class ExchangeController(object):

    def __init__(self):
       pass

    @staticmethod
    def list():
        return render_template("exchanges/index.html")

    def listExchangeAll(self):
        try:
            model = ExchangeModel()
            res = model.exchangeAll()
            return create_success_msg(json.loads(res))
        except sqlalchemy.exc.InternalError, e:
            raise e

    def addExchange(self, res):
        try:
            data = json.dumps(res.get_json())
            data = json.loads(data)
            general_data = [
                data['general']['name'], 
                data['general']['type'], 
                1,  
                data['general']['priority']
            ]

            pairs_data = formatData(data['pairs'])
            users_data = formatData(data['usersExchange'])
            formats_data = formatData(data['formatsExchange'])
            model = ExchangeModel()

            res = model.exchangeInsert(
                general_data,
                users_data,
                formats_data,
                pairs_data
            )

            action = 'Creacion de Exchange'
            set_log(action, res)
            return create_success_msg("")
        except sqlalchemy.exc.InternalError, e:
            raise e

    def update2Exchange(self, res):
        try:
            model = ExchangeModel()
            res = model.exchangeUpdate(res.get_json())
            return create_success_msg(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def suspendExchange(self, res):
        try:
            data = json.dumps(res.get_json(force=True))
            data = json.loads(data, encoding='utf-8')
            model = ExchangeModel()
            if data.has_key('id') == False:
                data['id'] = None
            res = model.exchangeSuspend(data["id"])
            return create_success_msg(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def getPairslist(self):
        try:
            model = ExchangeModel()
            res = model.getListPair()
            res = json.loads(res)
            if not 'success' in res:
                response = res
            else:
                if 'msg' in res:
                    raise Exception(res['msg'])
                else:
                    raise Exception('Not data response')
        except Exception, e:
            response = create_error_msg(str(e))
        finally:
            return jsonify(response)

    def getPairsExchange(self):
        try:
            data = request.get_json()
            model = ExchangeModel()
            res = model.getPairs(data)
            res = json.loads(res)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def getFormatNamesExchange(self):
        try:
            model = ExchangeModel()
            res = model.getFormatNames()
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    # Adaptacion API v1.0
    # Metodos API independientes:
    # Modelo: modelo (models.py)
    def insertExchange(self):
        try:
            model = ExchangeModel()
            data = request.json
            res = model.Insert_Exchange(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e
        
    def updateExchange(self):
        try:
            data = request.json
            model = ExchangeModel()
            res = model.Update_Exchange(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def selectExchange(self):
        try:
            data = request.json
            model = ExchangeModel()
            res = model.Select_Exchange(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def deleteExchange(self):
        try:
            data = request.json
            model = ExchangeModel()
            res = model.Delete_Exchange(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e        

    def showExchange(self):
        try:
            model = ExchangeModel()
            res = model.Show_Exchange()
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def viewExchange(self):
        try:
            data = request.json
            model = ExchangeModel()
            res = model.View_Exchange(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e        

    def viewAllExchange(self):
        try:
            model = ExchangeModel()
            res = model.View_AllExchange()
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e        

    def insertUserExchange(self):
        try:
            data = request.json
            model = ExchangeModel()
            res = model.Insert_UserExchange(data)
            
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e        

    def updateUserExchange(self):
        try:
            data = request.json
            model = ExchangeModel()
            res = model.Update_UserExchange(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def selectUserExchange(self):
        try:
            data = request.json
            model = ExchangeModel()
            res = model.Select_UserExchange(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def insertPairUserExchange(self):
        try:
            data = request.json
            model = ExchangeModel()
            res = model.Insert_PairUserExchange(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def updatePairUserExchange(self):
        try:
            data = request.json
            model = ExchangeModel()
            res = model.Update_PairUserExchange(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def selectPairUserExchange(self):
        try:
            data = request.json
            model = ExchangeModel()
            res = model.Select_PairUserExchange(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def insertFormatExchange(self):
        try:
            data = request.json
            model = ExchangeModel()
            res = model.Insert_FormatExchange(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def updateFormatExchange(self):
        try:
            data = request.json
            model = ExchangeModel()
            res = model.Update_FormatExchange(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def selectFormatExchange(self):
        try:
            data = request.json
            model = ExchangeModel()
            res = model.Select_FormatExchange(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def selectFormatExchangeByStatus(self):
        try:
            data = request.json
            model = ExchangeModel()
            res = model.Select_FormatExchangeByStatus(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def showFormatExchange(self):
        try:
            model = ExchangeModel()
            res = model.Show_FormatExchange()
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def showPair(self):
        try:
            model = ExchangeModel()
            res = model.Show_Pair()
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def selectPair(self):
        try:
            data = request.json
            model = ExchangeModel()
            res = model.Select_Pair(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def selectPairPorNombre(self):
        try:
            data = request.json
            model = ExchangeModel()
            res = model.Select_PairPorNombre(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    def insertExchangeUsersApilinks(self):
        try:
            data = request.json
            model = ExchangeModel()
            res = model.Insert_ExchangeUsersApilinks(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e      

    def updateExchangeUsersApilinks(self):
        try:
            data = request.json
            model = ExchangeModel()
            res = model.Update_ExchangeUsersApilinks(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e        

    def verifyExchangeBitinka(self):
        try:
            model = ExchangeModel()
            res = model.Verify_ExchangeBitinka()
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e        


    def checkBalance(self):
        try:
            reg_master = []

            model = ExchangeModel()
            data = model.checkBalance()
            # res = model.Update_UserExchange(data)
            
            if data["success"] == True:
                for exchange in data["datos"]:
                    count = 0
                    list_coin = []
                    if exchange[0].lower() == "bitstamp":
                        logging.info("***Consult balance in Bitstamp***")
                        for user in data["datos"][exchange]:
                            bal_bit = private_bit.account_balance(user["credentials"])
                            for coin_usu in user["pairs"]:
                                cad = coin_usu.lower() + "_" + "balance"
                                if float(bal_bit[cad]) == 0.0:
                                    count = count + 1
                                    list_coin.append(coin_usu)

                            if count == len(user["pairs"]):
                                dat_user = dict(
                                    status=2,
                                    idExchange=exchange[1],
                                    username=user["username"],
                                    idModifyUser=user["id_user"],
                                    idUserExchange=user["id_user"],
                                    credentials=user["credentials"]
                                )
                                model.Update_UserExchange(dat_user)
                        if count > 0:
                            cad = "Bitstamp: " + ', '.join(list_coin)
                            reg_master.append(cad)
                        else:
                            reg_master.append("")

                    elif exchange[0].lower() == "binance":
                        logging.info("***Consult balance in Binance***")
                        for user in data["datos"][exchange]:
                            binance_controller.set_(user["credentials"])
                            bal_bin = binance_controller.balances()
                            for coin in bal_bin:
                                for coin_usu in user["pairs"]:
                                    coin_usu = coin_usu + "T" if coin_usu == "USD" else coin_usu
                                    if coin_usu == coin:
                                        if float(bal_bin[coin]['free']) == 0.0:
                                            count = count + 1
                                            list_coin.append(coin_usu)

                            if count == len(user["pairs"]):
                                dat_user = dict(
                                    status=2,
                                    idExchange=exchange[1],
                                    username=user["username"],
                                    idModifyUser=user["id_user"],
                                    idUserExchange=user["id_user"],
                                    credentials=user["credentials"]
                                )
                                model.Update_UserExchange(dat_user)
                        if count > 0:
                            cad = "Binance: " + ', '.join(list_coin)
                            reg_master.append(cad)
                        else:
                            reg_master.append("")

                    elif exchange[0].lower() == "huobi":
                        logging.info("***Consult balance in Huobi***")
                        for user in data["datos"][exchange]:
                            cred = dict(
                                AccessKeyId=user["credentials"]["key"],
                                SecretKey=user["credentials"]["secret"] 
                            )
                            bal_huobi = getBalanceHuobi(cred)
                            bal_huobi = bal_huobi['data']['list']
                            for coin_usu in user["pairs"]:
                                for coin in bal_huobi:
                                    coin_usu = coin_usu + "T" if coin_usu == "USD" else coin_usu
                                    if coin['type'] == 'trade' and coin['currency'] == coin_usu.lower():
                                        if float(coin['balance']) == 0.0:
                                            count = count + 1
                                            list_coin.append(coin_usu)

                            if count == len(user["pairs"]):
                                dat_user = dict(
                                    status=2,
                                    idExchange=exchange[1],
                                    username=user["username"],
                                    idModifyUser=user["id_user"],
                                    idUserExchange=user["id_user"],
                                    credentials=user["credentials"]
                                )
                                model.Update_UserExchange(dat_user)
                        if count > 0:
                            cad = "Huobi: " + ', '.join(list_coin)
                            reg_master.append(cad)
                        else:
                            reg_master.append("")

                    elif exchange[0].lower() == "okex":
                        logging.info("***Consult balance in Okex***")
                        for user in data["datos"][exchange]:
                            cred = dict(
                                api_key=user["credentials"]["key"],
                                secret_key=user["credentials"]["secret"]
                            )
                            okex = getBalanceOkex(cred)
                            for coin_usu in user["pairs"]:
                                for k, v in okex['info']['funds']['free'].items():
                                    coin_usu = coin_usu + "T" if coin_usu == "USD" else coin_usu    
                                    if coin_usu.lower() == k and float(v) == 0.0:
                                        count = count + 1
                                        list_coin.append(coin_usu)
                            if count == len(user["pairs"]):
                                dat_user = dict(
                                    status=2,
                                    idExchange=exchange[1],
                                    username=user["username"],
                                    idModifyUser=user["id_user"],
                                    idUserExchange=user["id_user"],
                                    credentials=user["credentials"]
                                )
                                model.Update_UserExchange(dat_user)
                        if count > 0:
                            cad = "Okex: " + ', '.join(list_coin)
                            reg_master.append(cad)
                        else:
                            reg_master.append("")

                    else:
                        logging.info("Exchange external not implement - %s." %(exchange)) 

                for exchange in reg_master:
                    if exchange != "":
                        send_email_to_admin(exchange)
                        
                return True
            else:
                raise ValueError()
        except ValueError:
            logging.info(data["mensaje"])
            set_BackLogs(121, "mod_exchanges", data["mensaje"])

    
def formatData(data):
    return_data = []
    for indexs in data:
        list_data = []
        for index in indexs:
            if index == 'credentials' or index == 'params':
                list_data.append(str(indexs[index]).replace("\n", ""))
            else:
                list_data.append(indexs[index])
        return_data.append(list_data)
    return return_data

def send_email_to_admin(exchange):
    try:
        gmail_user = app.config['SENDER_EMAIL']
        gmail_pass = app.config['SENDER_PASSWORD']

        msg = 'No cuenta con saldo en la Exchange %s.' %(exchange)
        mensaje = MIMEText(msg)
        mensaje["Subject"] = "Saldo Agotado en ExchangeAccount"

        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        mail.login(gmail_user, gmail_pass)
        mail.sendmail(
            gmail_user, 
            [gmail_user], 
            mensaje.as_string()
        )
        mail.close()
    except Exception as e:
        logging.info(e)
