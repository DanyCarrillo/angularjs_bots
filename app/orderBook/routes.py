from flask import Blueprint, jsonify
from app import api, URI_WEBSOCKET
from app.commons import permissions
from app.orderBook.resource import OrderBook
from app.orderBook.controller import OrderBookController


orderBook = Blueprint('orderBook', __name__)
api.add_resource(
	OrderBook, 
	'/modOrderBook/orderBook'
)

controllerOrderBook = OrderBookController()

# Redireccionar a la pagina de listado de ordenes activas:
@orderBook.route('/modOrderBook/list', methods=['GET'])
@permissions
def listOrderBook():
    return controllerOrderBook.list()

# (2) Mostrar Exchange Segun idExchange:
@orderBook.route('/orderBook/pair/sel', methods=['POST'])
@permissions
def listOrderBookByPair():
	return controllerOrderBook.listOrderBookByPair()

@orderBook.route('/uriWebsocket',methods=['GET'])
@permissions
def uri_websocket():
	return jsonify({'datos':URI_WEBSOCKET,'code':200,'success':True}) if URI_WEBSOCKET else jsonify({'error':'need uri websocket','code':400,'success':False})
