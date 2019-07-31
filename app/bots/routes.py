from flask import Blueprint
from app import api
from app.bots.resource import Bots
from app.commons import permissions
from app.bots.controller import BotsController


bots = Blueprint('Bots', __name__)
bot_controller = BotsController()

api.add_resource(Bots,'/botConfig','/botConfig/A')


@bots.route('/modBots/list', methods=['GET'])
@permissions
def listBots():
    return BotsController.list()

@bots.route('/modBots/getTypesBot', methods=['GET'])
@permissions
def getTypesBot():
    return bot_controller.getTypesBot()

# Adaptacion API v1.0
# Metodos API independientes:
# Controlador: exchanges_controler (controller.py)

# (1) Listar Tipos de Bot:
@bots.route('/bot/type/show', methods=['GET'])
@permissions
def showBotType():
	return bot_controller.getTypesBot()

# (2) Listar Todos los Bot Config segun Usuario:
@bots.route('/bot/show', methods=['POST'])
@permissions
def showBot():
	return bot_controller.showBot()

# (3) Obtener Precio de Compra y Venta (crypto_price) segun idPair:
@bots.route('/bots/pair/crypto_price/sel',methods=['POST'])
@permissions
def selCryptoPricesPair():
	return bot_controller.selectCryptoPricesPair()

# (4) Agregar nuevo Bot:
@bots.route('/bot/add',methods=['POST'])
@permissions
def addBot():
	return bot_controller.insertBot()

# (5) Modificar Bot existente:
@bots.route('/bot/upd',methods=['PUT'])
@permissions
def updBot():
	return bot_controller.updateBot()

# (6) Eliminar Bot Existente:
@bots.route('/bot/del',methods=['PUT'])
@permissions
def delBot():
	return bot_controller.deleteBot()

# (7) Listar BOT CONFIG & PLAY segun status:
@bots.route('/botYplay/show', methods=['POST'])
@permissions
def showBotYPlay():
	return bot_controller.showBotYPlay()

# (8) Verificar si existe 'idBotType=Depth' y idTradingType=1 (limit order):
@bots.route('/bot/verify/bottypeYtradingtype', methods=['GET'])
@permissions
def verifyTypesBotAndTrading():
	return bot_controller.verifyTypesBotAndTrading()