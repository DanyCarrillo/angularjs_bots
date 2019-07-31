from flask import Blueprint, jsonify, render_template
from app import api
from app.commons import permissions
from app.tickers.resource import Tickers
from app.tickers.controller import TickersController

tickers = Blueprint('tickers', __name__)
api.add_resource(Tickers,'/ticker')

tickers_controller=TickersController()
@tickers.route('/modTickers/list', methods=['GET'])
@permissions
def lisTicker():
	return tickers_controller.list()

#Activar/Inactivar pares
@tickers.route('/ticker/volum/merketcap', methods=['GET'])
@permissions
def volumen_marketcap():
    return tickers_controller.viewVolumenMarketcap()
