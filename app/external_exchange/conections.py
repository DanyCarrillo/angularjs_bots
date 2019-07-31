import json
from flask import (
    jsonify
)
from app.commons import (
    create_error_msg,
    create_success_msg,
    convert_unicode
)
from .bitstamp_controller import PublicBit, PrivateBit

public_bit = PublicBit()
private_bit = PrivateBit()

from app.external_exchange.okex import *
import binance_controller
from app.external_exchange.huobi import *


def getOrderbook(exchange_name, send_data):
    if exchange_name == 'Bitstamp':
        data = {'par': send_data}
        response = public_bit.order_book(data)
    elif exchange_name == 'Binance':
        response = binance_controller.orderBook(send_data)
        if 'error' in response:
            response = False
    elif exchange_name == 'Okex':
        send_data = {'symbol': send_data.lower()}
        response = orderBookOkex(send_data)
        if not "error_code" in response:
            response = estructureOkexData(response)
        else:
            response = False
    elif exchange_name == 'Huobi':
        send_data = {'symbol': send_data.lower(), 'type': 'step0'}
        response = orderBookHuobi(send_data)
    else:
        response = 'Invalid Exchange name'

    return response

def getExchangeMarketPrice(exchange_name, send_data):    
    if exchange_name == 'Bitstamp':
        data = {'par': send_data}
        response = public_bit.market_price(data)
    elif exchange_name == 'Binance':
        send_data = {'symbol': send_data.upper()}
        response = binance_controller.marketPriceBinance(send_data)
    elif exchange_name == 'Okex':
        send_data = {'symbol': send_data.lower()}        
        response = marketPriceOkex(send_data)
    elif exchange_name == 'Huobi':
        send_data = {'symbol': send_data.lower(), 'type': 'step0'}        
        response = marketPriceHuobi(send_data)
    else:
        response = 'Invalid Exchange name'

    return response    


def createOrder(exchange_name, send_data, type):
    if exchange_name == 'Bitstamp':
        armed = armedBitstamp(send_data)
        if type == 'buy':
            response = private_bit.buy_market_order(armed['credentials'], armed['data'])
        else:
            response = private_bit.sell_market_order(armed['credentials'], armed['data'])
        if 'error' in response and response['error'] is True:
            response = response['msg']
        else:
            response = response
    elif exchange_name == 'Binance':
        armedBinance(send_data)
        response = binance_controller.newOrder(send_data['firstcurrency'], send_data['secondcurrency'],
                                               send_data['type'].upper(), send_data['amount'], send_data['price'])
        if 'error' in response:
            response = response['msg']
    elif exchange_name == 'Okex':
        send_data = armedOkex(send_data)
        response = createOrderOkex(send_data)
        if 'error_code' in response:
            response = response['error_code']
    elif exchange_name == 'Huobi':
        send_data = armedHuobi(send_data, type)
        response = createOrderHuobi(send_data)
        if response['status'] == 'error':
            response = response['err-msg']
    else:
        response = 'Invalid Exchange name'

    return response


def getBalance(exchange_name, send_data):
    if exchange_name is 'Bitstamp':
        # response = 'Bitstamp function'
        response = private_bit.account_balance(send_data)
    elif exchange_name is 'Binance':
        response = 'Binance function'
    elif exchange_name is 'Okex':
        response = getBalanceOkex(send_data)
    elif exchange_name is 'Huobi':
        response = 'Huobi function'
    else:
        response = 'Invalid Exchange name'

    return response




def getUsersOrders(exchange_name, send_data):
    if exchange_name is 'Bitstamp':
        # response = 'Bitstamp function'
        response = private_bit.open_orders(send_data)
    elif exchange_name is 'Binance':
        response = 'Binance function'
    elif exchange_name is 'Okex':
        response = historyOrderOkex(send_data)
    elif exchange_name is 'Huobi':
        response = 'Huobi function'
    else:
        response = 'Invalid Exchange name'

    return response


def estructureOkexData(res):
    sales = []
    purcharses = []
    res['asks'].reverse()
    for data in res:
        for order in res[data]:
            if data == 'bids':
                sales.append({'amount': order[1], 'price': order[0]})
            elif data == 'asks':
                purcharses.append({'amount': order[1], 'price': order[0]})
    return {'sales': sales, 'purcharses': purcharses}


def armedBitstamp(send_data):
    credentials = {'username': send_data['username'], 'key': send_data['key'], 'secret': send_data['secret']}
    data = {'first_cur': send_data['firstcurrency'], 'second_cur': send_data['secondcurrency'],
            'amount': send_data['amount']}
    return {'credentials': credentials, 'data': data}


def armedBinance(send_data):
    binance_controller.options['secret'] = send_data['secret']
    binance_controller.options['apiKey'] = send_data['key']

def armedOkex(send_data):
    send_data['symbol'] = send_data['symbol'].lower()
    send_data['sign'] = ""
    send_data['api_key'] = send_data['key']
    send_data['secret_key'] = send_data['secret']
    del send_data['key']
    del send_data['secret']
    return send_data

def armedHuobi(send_data, type):
    send_data['amount'] = round(float(send_data['amount']) * float(send_data['price']), 2) if type == 'buy-market' else \
        float(send_data['amount'])
    send_data['AccessKeyId'] = send_data['key']
    send_data['SecretKey'] = send_data['secret']
    del send_data['key']
    del send_data['secret']
    del send_data['price']
    send_data['symbol'] = send_data['symbol'].lower()
    return send_data