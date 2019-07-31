import redis
import logging
from kombu import Queue
from celery import Celery
from flask_restful import Api
from sqlalchemy.engine import create_engine
from flask import Flask, session
from commons import emitirAClientes
from crochet import setup, wait_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from datetime import datetime, date, timedelta


app = Flask('app', template_folder='template')
CORS(app)
app.config.from_object('config.DevelopmentConfig')
setup()

bots_per_page = app.config['BOTS_PER_PAGE']
URI_WEBSOCKET = app.config['URI_WEBSOCKET']

from autobahn.twisted.wamp import Application

wapp = Application()

@app.before_request
def setSessionTimeOut():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(
        minutes=app.config['SESSION_TIME']
    )

@wait_for(timeout=1)
def publish(topic, *args, **kwargs):
    return wapp.session.publish(topic, *args, **kwargs)

r = redis.StrictRedis(
    host=app.config['IP_REDIS'],
    port=app.config['PORT_REDIS'],
    db=3
)

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend='redis://' + app.config['IP_REDIS'] + ':'+app.config['PORT_REDIS']+'/1',
        broker='redis://' + app.config['IP_REDIS'] + ':'+app.config['PORT_REDIS']+'/0'
    )

    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery

celery = make_celery(app)

# Config tasks periodic
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    celery.control.purge()

    sender.add_periodic_task(
        int(app.config['RETRY_PRICE_UPDATE']),
        updMarketPrice.s(),
        ignore_result=True
    )
    sender.add_periodic_task(
        int(app.config['CONVERT_PRICE_TIME']),
        convertPrices.s(),
        ignore_result=True
    )
    sender.add_periodic_task(
        int(app.config['BOTS_PLAY_TIME']), 
        BotsPlay.s()
    )
    sender.add_periodic_task(
        int(app.config['CANCEL_ORDERS_TIME']), 
        cancelOrders.s()
    )
    sender.add_periodic_task(
        int(app.config['CANCEL_ORDESR_TIME_EXEC']),
        cancelOrdersTime.s()
    )
    # sender.send_task('checkBalance')
    # sender.send_task('CompleteOrders')

# Config BBDD
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], pool_recycle=2);
db = SQLAlchemy(app, session_options={'autocommit': True})
api = Api(app)

# Generic functions
def genericConect(store_name, list_data, mult=True):
    response = []   
    try:
        conect_raw = engine.raw_connection()
        cursor = conect_raw.cursor()
        cursor.callproc(store_name, list_data)
        if mult == True:
            response = cursor.fetchall()
        else:
            response = cursor.fetchone()
        cursor.nextset()
        conect_raw.commit()
    except Exception as e:
        logging.exception("Exception: genericConect Errno1 %s" %(str(e)))
    finally:
        try:
            cursor.close()
        except Exception as e:
            try:
                logging.exception("Exception: genericConect Errno2 %s" %(str(e)))
                conect_raw.close()
            except Exception as er:
                logging.exception("Exception: genericConect Errno3 %s" %(str(er)))      
        return response

def set_BackLogs(error_cod, module, desciption):
    store = "sp_bots_back_logs_insertar"
    lista = []
    lista.append(int(error_cod))
    lista.append(str(module))
    lista.append(str(desciption))

    list_logs = genericConect(store, lista)

def set_log(action, data):
    store = "sp_bots_log_user_insertar"
    lista = []
    all_info = {}
    all_info["action"] = action
    all_info["data"] = data

    id_creator = int(session["id_user"])
    lista.append(id_creator)
    lista.append(str(all_info))

    list_user = genericConect(store,lista)

def sanitizer(base=None, data=None, types=object):
    for k,v in types.OD.items():
        for i in data:
            if k==i:
                data[i] = data[i].encode('utf-8') if isinstance(data[i],unicode) else data[i]
                if type(v) is not type(data[i]):
                    return k, "Parameter '{}' Invalid data type".format(k)
                else:
                    base.append(data[i])
    return base, True

# Call controllers
from app.trading.controller import TradingController
from app.plays.controller import PlayController
from app.exchanges.controller import ExchangeController   

playscontroller = PlayController()
tradecontroller = TradingController()
exchangecontroller = ExchangeController()

# Call task
@celery.task(bind=True, name='updMarketPrice', queue="feed_tasks", acks_late=False)
def updMarketPrice(self):
    try:
        tradecontroller.updMarketPrice()
    except Exception, e:
        logging.exception("Exception: updMarketPrice s%" %(e))
        return self.retry(countdown=5)
    finally:
        return True

@celery.task(bind=True, name='convertPrices', queue="others", acks_late=False)
def convertPrices(self):
    try:
        result = 'Unexpected Error'
        result = tradecontroller.convertPrices()
    except Exception, e:
        logging.exception("Exception: convertPrices s%" %(e))
        return self.retry(countdown=5)
    finally:
        return result

@celery.task(bind=True, name='BotsPlay', queue="default", acks_late=False)
def BotsPlay(self):
    try:
        playscontroller.botsPlaying()
    except Exception, e:
        logging.exception("Exception: BotsPlay s%" %(e))
        return self.retry(countdown=5)
    finally:
        return True

@celery.task(bind=True, name='cancelOrders', queue="others", acks_late=False)
def cancelOrders(self):
    try:
        result = 'Unexpected Error'
        result = tradecontroller.cancelOrders(1)
    except Exception, e:
        logging.exception("Exception: cancelOrders s%" %(e))
        return self.retry(countdown=5)
    finally:
        return result

@celery.task(bind=True, name='cancelOrdersTime', queue="broker", acks_late=False)
def cancelOrdersTime(self):
    try:
        result = 'Unexcpected Error'
        result = tradecontroller.cancelOrders(2)
    except Exception as e:
        logging.exception("Exception: cancelOrders s%" %(e))
        return self.retry(countdown=5)
    finally:
        return result

@celery.task(bind=True, name='checkBalance', acks_late=False)
def checkBalance(self):
    try:
        exchangecontroller.checkBalance()
    except Exception, e:
        logging.exception(str(e))
    finally:
        return self.retry(countdown=int(app.config['CHECK_BALANCE_TIME']))

@celery.task(bind=True, name='CompleteOrders', acks_late=False)
def CompleteOrders(self):
    try:
        tradecontroller.completeOrder()
    except Exception, e:
        logging.exception(str(e))
    finally:
        return self.retry(countdown=int(app.config['COMPLETE_ORDERS_TIME']))


# Blueprint apps
from app.users.routes import users

app.register_blueprint(users)

from app.coins.routes import coins

app.register_blueprint(coins)

from app.exchanges.routes import exchanges

app.register_blueprint(exchanges)

from app.bots.routes import bots

app.register_blueprint(bots)

from app.plays.routes import plays

app.register_blueprint(plays)

from app.trading.routes import trading

app.register_blueprint(trading)

from app.tickers.routes import tickers

app.register_blueprint(tickers)

from app.logUsers.routes import logUsers

app.register_blueprint(logUsers)

from app.activePairs.routes import activePairs

app.register_blueprint(activePairs)

from app.orders.routes import orders

app.register_blueprint(orders)

from app.orderBook.routes import orderBook

app.register_blueprint(orderBook)
