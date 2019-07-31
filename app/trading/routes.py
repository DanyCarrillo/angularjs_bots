from flask import Blueprint, request, jsonify, json
from app import api
from app.commons import permissions, create_error_msg
from app.trading.resource import Trading
from app.trading.controller import TradingController

# from app.trading.bitstamp_controller import PublicBit, PrivateBit


trading = Blueprint('trading', __name__)
trading_controller = TradingController()
# public_bit = PublicBit()
# private_bit = PrivateBit()

api.add_resource(Trading, '/trading', '/trading/<string:type>')


@trading.route('/updateMarketprices', methods=['GET'])
def updateMarketprices():
    return trading_controller.updMarketPrice()

@trading.route('/cronUpdatePrice', methods=['GET'])
def cronUpdatePrice():
    return trading_controller.convertPrices()

@trading.route('/priceInkaAll/<string:pair>', methods=['GET'])
@trading.route('/priceInkaAll', methods=['GET'])
def listCriptoPrice(pair=None):
    if pair is not None:
        return trading_controller.getPairMarketPrice(pair)
    else:
        return trading_controller.listCriptoPrice()

@trading.route('/getTypesTrading', methods=['GET'])
def getTypesTrading():
    return trading_controller.getTypesTrading()

@trading.route('/getMarketPrice', methods=['POST'])
def getMarketPrice():
    data = request.get_json()
    return jsonify(trading_controller.getMarketPrice(data))

@trading.route('/getPriceLink', methods=['POST'])
def getPriceLink():
    return jsonify(trading_controller.getPriceLink(request))

@trading.route('/modTrade/completeOrder', methods=['POST'])
def completeOrder():
    if request.is_json:
        data = request.get_json()
        if not 'price' and 'order_id' and 'amount_completed' and 'type' in data:
                return jsonify(create_error_msg("Invalid request data"))
        else:
            return jsonify(trading_controller.saveOrderTrade(data))
    else:
        return jsonify(create_error_msg("Json datatype is missing"))

@trading.route('/test', methods=['GET'])
def test():
    return jsonify(trading_controller.getFilterOrders())

# Adaptacion API v1.0
# Metodos API independientes:
# Controlador: exchanges_controler (controller.py)

# (1) Listar Tipos de Trading:
@trading.route('/trading/type/show', methods=['GET'])
@permissions
def showTradingType():
    return trading_controller.getTypesTrading()

# (2) Mostrar Precios de Compra y Venta de cada Exchange segun IdPair:
@trading.route('/trading/exchange/marketprices', methods=['POST'])
def selMarketPricesExchange():
    return trading_controller.selectMarketPricesExchange()

# (3) Listar Ordenes Activas segun Pair: 
@trading.route('/trading/orders/active', methods=['POST'])
def showActiveOrdersByPair():
    return trading_controller.Show_ActiveOrdersByPair()

# (4) Listar Ordenes Activas segun Bot: 
@trading.route('/trading/orders/active/bot', methods=['POST'])
def showActiveOrdersByBot():
    return trading_controller.Show_ActiveOrdersByBot()

# (5) Cancelar una Orden Activa:
@trading.route('/trading/orders/cancel', methods=['POST'])
def sendOrdersToCancel():
    return trading_controller.Send_OrdersToCancel()

@trading.route('/cancelOrders', methods=['GET'])
def cancelOrders():
    return trading_controller.cancelOrders()
