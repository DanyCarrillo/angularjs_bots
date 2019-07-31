from flask import Blueprint,request, jsonify, render_template
from app import api
from app.commons import permissions
from app.activePairs.resource import ActivePairs
from app.activePairs.controller import ActivePairsController

activePairs = Blueprint('activePairs', __name__)
api.add_resource(ActivePairs,'/pairs','/pairs/<string:type>')

#Lista de pares
activePairs_controller=ActivePairsController()
@activePairs.route('/modActivePairs/list', methods=['GET'])
@permissions
def lisActivePairs():
	return activePairs_controller.list()

#Activar/Inactivar pares
@activePairs.route('/pairs/modPair', methods=['PUT'])
@permissions
def blockPair():
    return activePairs_controller.suspendPairController(request)

#Ver parametros de par params:
@activePairs.route('/pairs/seltype', methods=['POST'])
@permissions
def selectPairTypeCoins():
    return activePairs_controller.selPairTypeCoins()