from flask import Blueprint
from app import api
from app.plays.resource import Play
from app.plays.controller import PlayController


plays = Blueprint('plays', __name__)
plays_controller = PlayController()

api.add_resource(Play, '/modPlays', '/plays/<string:type>')


@plays.route('/modPlays/play', methods=['POST'])
def play():
    return plays_controller.play()

@plays.route('/modPlays/stop', methods=['POST'])
def stop():
    return plays_controller.stop()

@plays.route('/test_botsPlaying', methods=['GET'])
def botsPlaying():
    return plays_controller.botsPlaying()

# Adaptacion API v1.0
# Metodos API independientes:
# Controlador: exchanges_controler (controller.py)

# (1) Agregar nuevo Bot Play:
@plays.route('/bot/play/add',methods=['POST'])
def addBotPlay():
	return plays_controller.insertBotPlay()

# (2) Listar Bots Play:
@plays.route('/bot/play/show',methods=['POST'])
def showBotPlay():
	return plays_controller.showBotPlay()

# (3) Modificar Bots Play a STOP:
@plays.route('/bot/play/upd',methods=['PUT'])
def updBotPlay():
	return plays_controller.updateBotPlay()

# (3) Modificar Bots Play a STOP:
@plays.route('/bot/play/lastUpdate',methods=['POST'])
def lastUpdateBotPlay():
	return plays_controller.lastUpdateBotPlay()

@plays.route('/modPlay/obtListPlayBot', methods=['POST'])
def obtListPlayBot():
    return plays_controller.listPlays()
