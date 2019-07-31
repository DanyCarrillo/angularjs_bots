import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    THREADS_PER_PAGE = 2
    IP_ALLOWED = ['ip de la vpn']
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://USUARIO:CLAVE@192.168.7.22:1987/bots'
    DATABASE_CONNECT_OPTIONS = {}
    SECRET_KEY = '6468202b-463a-4c7e-88f1-a97987a75ecd'
    CSRF_SESSION_KEY = '6468202b-463a-4c7e-88f1-a97987a75ecd'
    IP_REDIS = '0.0.0.0'
    PORT_REDIS = '6379'
    USER_PERMISSION = {'admin': ['All'], 'user': ['GET', 'POST', 'PUT']}
    SESSION_TIME = 200  # '''Time in minutes'''
    HOST = '0.0.0.0'
    PORT = 1234
    KEY_AES = "1C7F6F3340C29050C826B6B29EB507F3"
    BOTS_PER_PAGE = 11
    VARIATION = 20

    # Celery Execute timers
    CONVERT_PRICE_TIME = 300
    RETRY_PRICE_UPDATE = 50
    MARKET_PRICE_TIME = 360
    BOTS_PLAY_TIME = 30
    COMPLETE_ORDERS_TIME = 300
    CHECK_BALANCE_TIME = 600
    CANCEL_ORDERS_TIME = 30
    CANCEL_ORDERS_TIME_TIME = 300
    CANCEL_ORDESR_TIME_EXEC = 60

    # Time for custom task
    LONGTASK_LIMIT = 180
    LONGTASK_LIMIT_SOFT = 120

    # Config Celery
    CELERY_TIMEZONE = 'UTC'
    CELERY_ENABLE_UTC = True
    CELERY_ACKS_LATE = False
    CELERYD_TASK_TIME_LIMIT = 5
    CELERY_TASK_CREATE_MISSING_QUEUES = True
    CELERY_DEFAULT_QUEUE = "default"
    CELERY_QUEUES = {
        "default": {
            "binding_key": "task.#",
        },
        "feed_tasks": {
            "binding_key": "feed.#",
        },
        "broker": {
            "binding_key": "broker.#",
        },
        "others": {
            "binding_key": "others.#",
        },
        "savebd": {
            "binding_key": "savebd.#",
        },
        "cancelOrders": {
            "binding_key": "cancelOrders.#",
        },
        "cancelCalculate":{
            "binding_key":"cancelCalculate.#"
        },
        "killcancel":{
            "binding_key":"killcancel.#"
        },
        "createOrder": {
            "binding_key": "createOrder.#",
        },
        "helpUdpPrice": {
            "binding_key": "helpUdpPrice.#",
        },
        "addVolume": {
            "binding_key": "addVolume.#",
        }
    }
    CELERY_DEFAULT_EXCHANGE = "tasks"
    CELERY_DEFAULT_EXCHANGE_TYPE = "topic"
    CELERY_DEFAULT_ROUTING_KEY = "task.default"
    CELERY_ROUTES = {
        "feeds.tasks.import_feed": {
            "queue": "feed_tasks",
            "routing_key": "feed.import",
        },
        "broker.tasks.import_broker": {
            "queue": "broker",
            "routing_key": "broker.import",
        },
        "others.tasks.import_others": {
            "queue": "others",
            "routing_key": "others.import",
        },
        "savebd.tasks.import_savebd": {
            "queue": "savebd",
            "routing_key": "savebd.import",
        },
        "cancelOrders.tasks.import_cancelOrders": {
            "queue": "cancelOrders",
            "routing_key": "cancelOrders.import",
        },
        "cancelCalculate.tasks.import_cancelOrders": {
            "queue": "cancelCalculate",
            "routing_key": "cancelCalculate.import",
        },
        "killcancel.tasks.import_cancelOrders": {
            "queue": "killcancel",
            "routing_key": "killcancel.import",
        },
        "createOrder.tasks.import_createOrder": {
            "queue": "createOrder",
            "routing_key": "createOrder.import",
        },
        "helpUdpPrice.tasks.import_helpUdpPrice": {
            "queue": "helpUdpPrice",
            "routing_key": "helpUdpPrice.import",
        },
        "addVolume.tasks.import_addVolume": {
            "queue": "addVolume",
            "routing_key": "addVolume.import",
        }
    }
    COUNT_MARKET = 0

    # Acount email
    SENDER_EMAIL = 'xxckckckc@bitinka.com'
    SENDER_PASSWORD = 'lkasldknxxckc'

    # Ruta de websocket
    URI_WEBSOCKET = 'https://websocket.bitinka.com/'

class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
