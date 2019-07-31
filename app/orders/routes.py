from flask import Blueprint, jsonify
from app import api
from app.commons import permissions
from app.orders.resource import Orders
from app.orders.controller import OrdersController


orders = Blueprint('orders', __name__)
api.add_resource(
	Orders, 
	'/modOrders/orders', 
	'/modOrders/orders/<string:type>'
)

controllerOrders = OrdersController()

# Redireccionar a la pagina de listado de ordenes activas:
@orders.route('/modOrders/list', methods=['GET'])
@permissions
def listOrders():
    return controllerOrders.list()

# (1) Listar Ordenes Activas segun Bot: 
@orders.route('/orders/active/bot', methods=['POST'])
def showActiveOrdersByUser():
    return controllerOrders.Show_AllActivesOrdersByUser()
