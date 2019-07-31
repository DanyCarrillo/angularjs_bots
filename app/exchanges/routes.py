from flask import Blueprint
from app import api
from app.commons import permissions
from app.exchanges.resource import Exchange
from app.exchanges.controller import ExchangeController


exchanges = Blueprint('exchanges', __name__)
exchanges_controller = ExchangeController()

api.add_resource(Exchange, '/exchanges', '/exchanges/<string:type>')


@exchanges.route('/modExchange/list', methods=['GET'])
@permissions
def lisExchange():
    return exchanges_controller.list()

@exchanges.route('/modPairs/getPairslist', methods=['GET'])
def getPairslist():
    return exchanges_controller.getPairslist()

@exchanges.route('/exchanges/getPairsExchange', methods=['POST'])
def getPairsExchange():
    return exchanges_controller.getPairsExchange()

@exchanges.route('/exchanges/getFormatNamesExchange', methods=['GET'])
def getFormatNamesExchange():
	return exchanges_controller.getFormatNamesExchange()

# Adaptacion API v1.0
# Metodos API independientes:
# Controlador: exchanges_controler (controller.py)

# (1) Agregar Nuevo Exchange:
@exchanges.route('/exchange/add', methods=['POST'])
@permissions
def addExchange():
	return exchanges_controller.insertExchange()

# (2) Modificar Exchange Existente:
@exchanges.route('/exchange/upd', methods=['PUT'])
@permissions
def updExchange():
	return exchanges_controller.updateExchange()

# (2) Mostrar Exchange Segun idExchange:
@exchanges.route('/exchange/sel', methods=['POST'])
@permissions
def selExchange():
	return exchanges_controller.selectExchange()

# (3) Listar Exchanges Existentes:
@exchanges.route('/exchange/show', methods=['GET'])
@permissions
def showExchange():
	return exchanges_controller.showExchange()

# (4) Mostrar Datos de Exchange Existente:
@exchanges.route('/exchange/view', methods=['POST'])
@permissions
def viewExchange():
	return exchanges_controller.viewExchange()

# (4) Mostrar Datos de Exchange Existente:
@exchanges.route('/exchange/all/view', methods=['GET'])
@permissions
def viewAllExchange():
	return exchanges_controller.viewAllExchange()

# (4) Eliminar Exchange Existente:
@exchanges.route('/exchange/del', methods=['PUT'])
@permissions
def delExchange():
	return exchanges_controller.deleteExchange()		

# (5) Insertar Usuario Exchange:
@exchanges.route('/exchange/user/add', methods=['POST'])
@permissions
def addUserExchange():
	return exchanges_controller.insertUserExchange()

# (6) Modificar Usuario Exchange:
@exchanges.route('/exchange/user/upd', methods=['PUT'])	
@permissions
def updUserExchange():
	return exchanges_controller.updateUserExchange()

# (7) Mostrar Usuario Exchange Segun idExchange:
@exchanges.route('/exchange/user/sel', methods=['POST'])
@permissions
def selUserExchange():
	return exchanges_controller.selectUserExchange()

# (8) Insertar Par Usuario Exchange:
@exchanges.route('/exchange/user/pair/add', methods=['POST'])
@permissions
def addPairUserExchange():
	return exchanges_controller.insertPairUserExchange()

# (9) Modificar Par Usuario Exchange:
@exchanges.route('/exchange/user/pair/upd', methods=['PUT'])	# <------------- FALTA CREAR SP
@permissions
def updPairUserExchange():
	return exchanges_controller.updatePairUserExchange()

# (10) Mostrar Par Usuario Exchange segun idExchange(Obligatorio) y idUserExchange(Opcional):
@exchanges.route('/exchange/user/pair/sel', methods=['POST'])	
@permissions
def selPairUserExchange():
	return exchanges_controller.selectPairUserExchange()

# (11) Insertar Format Exchange:
@exchanges.route('/exchange/format/add', methods=['POST'])
@permissions
def addFormatExchange():
	return exchanges_controller.insertFormatExchange()

# (12) Modificar Format Exchange:
@exchanges.route('/exchange/format/upd', methods=['PUT'])	
@permissions
def updFormatExchange():
	return exchanges_controller.updateFormatExchange()

# (13) Mostrar Format Exchange segun idExchange:
@exchanges.route('/exchange/format/sel', methods=['POST'])	
@permissions
def selFormatExchange():
	return exchanges_controller.selectFormatExchange()

# (14) Listar todos los Pairs:
@exchanges.route('/pair/show', methods=['GET'])	
@permissions
def showPair():
	return exchanges_controller.showPair()

# (14) Mostrar Pair segun idPair:
@exchanges.route('/pair/sel', methods=['POST'])	
@permissions
def selPair():
	return exchanges_controller.selectPair()

# (14) Mostrar Pair segun Nombre:
@exchanges.route('/pair/selpornombre', methods=['POST'])	
@permissions
def selPairPorNombre():
	return exchanges_controller.selectPairPorNombre()

# (15) Listar todos los Formats:
@exchanges.route('/exchange/format/show', methods=['GET'])	
@permissions
def showFormatExchange():
	return exchanges_controller.showFormatExchange()

# (16) Insertar Exchange con Users y Apilinks:
@exchanges.route('/exchange/users/apilinks/add', methods=['POST'])	
@permissions
def addExchangeUsersApilinks():
	return exchanges_controller.insertExchangeUsersApilinks()

# (16) Actualizar Exchange con Users y Apilinks:
@exchanges.route('/exchange/users/apilinks/upd', methods=['PUT'])	
@permissions
def updExchangeUsersApilinks():
	return exchanges_controller.updateExchangeUsersApilinks()

@exchanges.route('/checkBalance', methods=['GET'])	
def checkBalance():
	return exchanges_controller.checkBalance()

# (16) Verificar si el Exchange Bitinka existe:
@exchanges.route('/exchange/verify/bitinka', methods=['GET'])
@permissions
def verifyExchangeBitinka():
	return exchanges_controller.verifyExchangeBitinka()

# (17) Obtener Format Exchange segun idExchange y Status Format:
@exchanges.route('/exchange/format/sel/status',methods=['POST'])
@permissions
def selFormatExchangeByStatus():
	return exchanges_controller.selectFormatExchangeByStatus()