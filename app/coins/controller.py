import json, requests
import sqlalchemy
from flask import (
    render_template,
    jsonify,
    request,
    session
)
from app.commons import (
    get_exception_msg,
    create_error_msg,
    create_success_msg,
    val_num_slash,
    convert_unicode
)
from app.coins.models import CoinModel
from app import set_log


class CoinsController(object):

    def __init__(self):
        pass

    @staticmethod
    def list():
        return render_template("coins/index.html")

    def getlistCoin(self, res):
        if val_num_slash(res.path, 4):
            p_type = res.path.split("/")[3]
            model = CoinModel()
            res = model.coinAll(p_type)
            return create_success_msg(res)
        else:
            data = "URL not found."
            return create_error_msg(data)

    def addCoin(self, res):
        data = json.dumps(res.get_json());
        data = json.loads(data)
        model = CoinModel()
        response = model.coinInsert(data)
        response=json.loads(response)
        if response['success'] is True:
            #Set_log
            action='Creacion de Moneda'
            set_log(action,data)
            return response
        else:
            return response
    def updateCoin(self, res):
        try:
            data = json.dumps(res.get_json())
            data = json.loads(data)
            if type(data['con_buy']) is unicode:
                data['con_buy'] = float(data['con_buy'])
            model = CoinModel()
            res = model.coinUpdate(data)
            return create_success_msg(res)
        except sqlalchemy.exc.InternalError, e:
            raise e

    @staticmethod
    def loadLinks():
        try:
            data =json.dumps(request.get_json());
            data = json.loads(data)
            model = CoinModel()
            res = model.loadLinks(data)
            if res['success']==True:
                return jsonify(create_success_msg(res)), 200
            else:
                return jsonify(create_error_msg(res)), 400
        except sqlalchemy.exc.InternalError,e:
            return jsonify(crear_mensaje_error(obt_mes_exception(e))), 500

    @staticmethod
    def updLink():
        try:
            data = json.dumps(request.get_json(force=True))
            data = json.loads(data)
            if data.has_key('id') == False:
                return jsonify(create_error_msg("Id no puede ser null")), 500
            if data.has_key('links') == False:
                return jsonify(create_error_msg("Parametro links no puede estar null")), 500
            model = CoinModel()
            res = model.updateLinks(data)
            if res['success']==True:
                return jsonify(create_success_msg(res)), 200
            else:
                return jsonify(create_error_msg(res)), 400
        except sqlalchemy.exc.InternalError, e:
            return jsonify(create_error_msg(get_exception_msg(e))), 500

    def getApiResponse(self):
        try:
            if request.is_json:
                data = request.get_json()
                if data['method'] == 'GET':
                    if 'params' in data and data['params'] != None:
                        link = data['link'] + data['params']
                    else:
                        link = data['link']
                    response = requests.get(link)
                    if response.status_code == 200:
                        return jsonify(response.json())
                    else:
                        return jsonify('Api not response'), int(response.status_code)
                else:
                    link = data['link']
                    #data_send = str(data['params'])
                    data_send = json.dumps(data['params'])
                    data_send = json.loads(data['params'])
                    response = requests.post(link, data=data_send)
                    if response.status_code == 200:
                        return jsonify(response.json())
                    else:
                        return jsonify('Api not response'), int(response.status_code)

            else:
                return jsonify('Invalid request')
        except Exception, e:
            raise e

    def CurrencyRate(self):
        model = CoinModel()
        datos = {}
        try:
            coins = json.loads(model.CurrencyRate())
            coins = convert_unicode(coins)
            for data in coins:
                price = (float(data['con_buy']) + float(data['con_sell'])) / 2
                value = {data['name']: float('{0:.8f}'.format(price))}
                datos = dict(datos.items() + value.items())
            result = dict(
                success=True,
                data=datos
            )
            return result
        except Exception, e:
            return dict(
                success=False,
                msg=str(e)
            )
