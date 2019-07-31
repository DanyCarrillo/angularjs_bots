import hmac
import hashlib
import logging
import requests
import time
from datetime import datetime, date, timedelta

try:
    from urllib import urlencode
# for python3
except ImportError:
    from urllib.parse import urlencode


ENDPOINT = "https://www.binance.com"

BUY = "BUY"
SELL = "SELL"

LIMIT = "LIMIT"
MARKET = "MARKET"

GTC = "GTC"
IOC = "IOC"
FOK= "FOK"

options = {}

def request(method, path, params=None):
    resp = requests.request(method, ENDPOINT + path, params=params)
    data = resp.json()
    if "msg" in data:
        logging.error(data['msg'])
    return data

#------------------------Publicos------------------------

def orderBook(symbol, **kwargs):
    """obtener order book.
    Args:
        symbol (str)
        limit (int, optional): Default 100. Must be one of 50, 20, 100, 500, 5,
            200, 10.
    """
    params = {"symbol": symbol.upper()}
    params.update(kwargs)
    res = request("GET", "/api/v1/depth", params)
    #print(res)
    # res_data={
    #      "bids": {px: qty for px, qty, _ in res["bids"]},
    #    "asks": {px: qty for px, qty, _ in res["asks"]},
    # }
    if 'msg' in res:
        return {'error': True, 'msg': res['msg']}
    else:
        sales=[]
        purcharses=[]

        for data in res:
            if data == 'bids':
                for order in res[data]:
                    sales.append({'amount':order[1],'price':order[0]})  
            elif data == 'asks':
                for order in res[data]: 
                    purcharses.append({'amount':order[1],'price':order[0]})
        return {'sales':sales,'purcharses':purcharses} 


def marketPriceBinance(send_data):
    symbol = send_data['symbol']
    res = request("GET","/api/v3/ticker/bookTicker?symbol="+ symbol)        
    bid = 0
    ask = 0    
    if res.has_key("bidPrice"):        
        bid=res['bidPrice']
        ask=res['askPrice']
    return {'bid':bid,'ask':ask}   
                 

#--------------------Privados(ApiKey,Secret)--------------------------------
def balances():
    """Obtener saldos actuales para todos los simbolos."""
    #set_('yfdu3eXm7zSwNDrZyyKqTh7pLN5gDuNEmwHayKbEkmOf1TYdFqwuhPkjdjbbZSG2','vFkY4NaLiCGW1goVKofptFYn3kqQOynDmHTzTbrjfUPRnRujRhBzY19AlxSTh41o') 
    try:
        data = firma("GET", "/api/v3/account", {})
        if 'msg' in data: 
            return ValueError("Apikey o Secret invalido: {}".format(data['msg']))
        else:
            return {d["asset"]: {
                "free": d["free"],
                "locked": d["locked"],
            } for d in data.get("balances", [])}
    except Exception as e:
        return "Revise ApiKey e Secretkey"

def newOrder(firstCurrency, secondCurrency, side, quantity, price=None, orderType=MARKET, timeInForce=GTC,
          test=False, **kwargs):
    """Enviar una nueva orden.
    newOrder("BNBBTC",'BUY',151.93,0.0019767,test=True)
    Args:
        symbol (str)
        side (str): BUY o SELL.
        quantity (float, str o decimal)
        price (float, str o decimal)
        orderType (str, optional): LIMIT or MARKET.
        timeInForce (str, optional): GTC or IOC.
        test (bool, optional): crea y valida un nuevo pedido pero no lo hace
            envia al motor correspondiente. Devuelve dict vacio si es exitoso
            .
        newClientOrderId (str, optional): Una identificacion unica para la orden.
            generado automaticamente si no se envia.
        stopPrice (float, str or decimal, optional): Usado con ordenes stop.
        icebergQty (float, str or decimal, optional): Usado con ordenes de iceberg.

    """
    params = {
        "symbol": (firstCurrency+secondCurrency).upper(),
        "side": side,
        "type": orderType,
        "timeInForce": timeInForce,
        "quantity": formatNumero(quantity),
        "price": formatNumero(price) if price is not None else '',
    }
    if orderType == 'MARKET':
        del params["timeInForce"]
        del params["price"]
    params.update(kwargs)
    path = "/api/v3/order/test" if test else "/api/v3/order"
    data = firma("POST", path, params)
    if 'msg' in data or len(data) is 0:
        return {'error': True, 'msg': data['msg']}
    else:
        all_data = {}
        all_data["firstCurrency"] = firstCurrency
        all_data["secondCurrency"] = secondCurrency
        data["transactTime"] = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(data["transactTime"] / 1000.0))
        all_data["date"] = data["transactTime"]
        all_data["amount"] = data["origQty"]
        all_data["idOrder"] = data["orderId"]
        all_data["amount"] = data["price"]
        all_data["status"] = data["status"]
        all_data["total"] = formatNumero(float(data["origQty"]) * float(data["price"]))
        if data["side"] == 'SELL':
            all_data["typeOrder"] = 'SELL'
        else:
            all_data["typeOrder"] = 'BUY'
    return all_data


def allOrders(symbol, **kwargs):
    """obtener todos las ordenes de la cuenta, activada, cancelada o llenada.

        Si se establece orderId, recibira ordenes >= ese orderId. De lo contrario
    ordenes recientes son devueltos.

    Args:
        symbol (str)
        orderId (int, optional)
        limit (int, optional): Default 500; max 500.
        recvWindow (int, optional)

    """
    params = {"symbol": symbol.upper()}
    params.update(kwargs)
    data = firma("GET", "/api/v3/allOrders", params)
    if 'msg' in data: 
            return ValueError("Error en: {}".format(data['msg']))
    else:    
        return data

def openOrders(symbol, **kwargs):
    """Obtener todas las ordenes abiertas en un simbolo.

    Args:
        symbol (str)
        recvWindow (int, optional)

    """
    params = {"symbol": symbol.upper()}
    params.update(kwargs)
    data = firma("GET", "/api/v3/openOrders", params)
    if "msg" in data:
        return ValueError("Error en: "+data['msg'])
    else:
        return data

def set_(cred):
    """Llamar antes de signature()
    """
    options["apiKey"] = cred['key']
    options["secret"] = cred['secret']

def firma(method, path, params):

    if "apiKey" not in options or "secret" not in options:
        return ValueError("Es necesario que ingrese apikay y secret")
    else:
        query = urlencode(sorted(params.items()))
        query += "&timestamp={}".format(int(time.time()*1000))
        secret = bytes(options["secret"].encode("utf-8"))
        signature = hmac.new(secret, query.encode("utf-8"),
                             hashlib.sha256).hexdigest()
        query += "&signature={}".format(signature)
        resp = requests.request(method,
                                ENDPOINT + path + "?" + query,
                                headers={"X-MBX-APIKEY": options["apiKey"]})
        data = resp.json()
        if "msg" in data:
            logging.error('En params de Firma: ' + data['msg'])
            return data
        else:
            return data

def formatNumero(x):
    if isinstance(x, float):
        return "{:.8f}".format(x)

    else:
        return str(x)


    





