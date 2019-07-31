from flask import Blueprint, jsonify
from app import api
from app.commons import permissions
from app.coins.resource import Coins
from app.coins.controller import CoinsController


coins = Blueprint('coins', __name__)
api.add_resource(
	Coins, 
	'/modCoins/coins', 
	'/modCoins/coins/<string:type>'
)

controllerCoins = CoinsController()


@coins.route('/modCoins/list', methods=['GET'])
@permissions
def listCoins():
    return CoinsController.list()


@coins.route('/loadLinks', methods=['POST'])
@permissions
def loadLinks():
    return CoinsController.loadLinks()


@coins.route('/modCoins/updLinks', methods=['PUT'])
@permissions
def updLink():
    return CoinsController.updLink()


@coins.route('/modCoins/getApiResponse', methods=['POST'])
def getApiResponse():
    return controllerCoins.getApiResponse()

@coins.route('/CurrencyRate')
def CurrencyRate():
    return jsonify(controllerCoins.CurrencyRate())
