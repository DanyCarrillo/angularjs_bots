from functools import wraps
import sys
import hmac
import hashlib
import time
import warnings
from flask import request, jsonify, abort
from libs import BaseClient, TransRange, BitstampError, build_msg
from app.commons import orders_format_response
from app import app

# PUBLICS


class PublicBit:

    def __init__(self):
        pass

    def order_book(self, data):
        return Public(BaseClient).order_book_(data['par'], group=True)

    def market_price(self, data):
        return Public(BaseClient).market_price_(data['par'])    

# PRIVATES


class PrivateBit:

    def __init__(self):
        pass

    def open_orders(self, credentials, data):

        trading_cli = TradingBit(username=credentials['username'], key=credentials['key'], secret=credentials['secret'])
        return trading_cli.open_orders_(data['par'])

    def account_balance(self, credentials):

        trading_cli = TradingBit(username=credentials['username'], key=credentials['key'], secret=credentials['secret'])
        resp = trading_cli.account_balance_()
        return resp

    def buy_market_order(self, credentials, data):

        trading_cli = TradingBit(username=credentials['username'], key=credentials['key'], secret=credentials['secret'])
        return trading_cli.buy_market_order_(data['first_cur'], data['second_cur'], data['amount'])

    def sell_market_order(self, credentials, data):

        trading_cli = TradingBit(username=credentials['username'], key=credentials['key'], secret=credentials['secret'])
        return trading_cli.sell_market_order_(data['first_cur'], data['second_cur'], data['amount'])

    def buy_limit_order(self, credentials, data):

        trading_cli = TradingBit(username=credentials['username'], key=credentials['key'], secret=credentials['secret'])
        return trading_cli.buy_limit_order_(data['first_cur'], data['second_cur'], data['amount'], data['price'])

    def sell_limit_order(self, credentials, data):

        trading_cli = TradingBit(username=credentials['username'], key=credentials['key'], secret=credentials['secret'])
        return trading_cli.sell_limit_order_(data['first_cur'], data['second_cur'], data['amount'], data['price'])


class Public(BaseClient):

    def order_book_(self, par, group=True):
        """
        Returns dictionary with "bids" and "asks".

        Each is a list of open orders and each order is represented as a list
        of price and amount.
        """
        params = {'group': group}
        url = self._construct_url("order_book/", par)
        res = self._get(url, params=params, return_json=True, version=2)

        sales = []
        purchases = []
        for data in res:
            for index, order in enumerate(res[data]):
                if data == 'asks':
                    sales.append({'amount': order[1], 'price': order[0]})
                elif data == 'bids':
                    purchases.append({'amount': order[1], 'price': order[0]})
                if index == 99:
                    break
                else:
                    pass
        resp = {'sales': sales, 'purcharses': purchases}
        return resp

    def market_price_(self, par):
        url = self._construct_url("ticker/", par)
        res = self._get(url ,return_json=True, version=2)          
        bid = 0
        ask = 0    
        if res.has_key("ask"):        
            bid=res['bid']
            ask=res['ask']
        return {'bid':bid,'ask':ask}        


class TradingBit(Public):

    def __init__(self, username, key, secret, *args, **kwargs):
        """
        Stores the username, key, and secret which is used when making POST
        requests to Bitstamp.
        """
        super(TradingBit, self).__init__(
            username=username, key=key, secret=secret, *args, **kwargs)
        self.username = username
        self.key = key
        self.secret = secret

    def get_nonce(self):
        """
        Get a unique nonce for the bitstamp API.

        This integer must always be increasing, so use the current unix time.
        Every time this variable is requested, it automatically increments to
        allow for more than one API request per second.

        This isn't a thread-safe function however, so you should only rely on a
        single thread if you have a high level of concurrent API requests in
        your application.
        """
        nonce = getattr(self, '_nonce', 0)
        if nonce:
            nonce += 1
        # If the unix time is greater though, use that instead (helps low
        # concurrency multi-threaded apps always call with the largest nonce).
        self._nonce = max(int(time.time()), nonce)
        return self._nonce

    def _default_data(self, *args, **kwargs):
        """
        Generate a one-time signature and other data required to send a secure
        POST request to the Bitstamp API.
        """
        data = super(TradingBit, self)._default_data(*args, **kwargs)
        data['key'] = self.key
        nonce = self.get_nonce()
        msg = str(nonce) + self.username + self.key

        signature = hmac.new(
            self.secret.encode('utf-8'), msg=msg.encode('utf-8'),
            digestmod=hashlib.sha256).hexdigest().upper()
        data['signature'] = signature
        data['nonce'] = nonce
        return data

    def _expect_true(self, response):
        """
        A shortcut that raises a :class:`BitstampError` if the response didn't
        just contain the text 'true'.
        """
        if response.text == u'true':
            return True
        raise BitstampError("Unexpected response")

    def open_orders_(self, par):
        """
        Returns JSON list of open orders. Each order is represented as a
        dictionary.
        """
        url = self._construct_url("open_orders/", par)
        res = self._post(url, return_json=True, version=2)
        return jsonify(res)

    def account_balance_(self):
        """
        Returns dictionary::

            {u'btc_reserved': u'0',
             u'fee': u'0.5000',
             u'btc_available': u'2.30856098',
             u'usd_reserved': u'0',
             u'btc_balance': u'2.30856098',
             u'usd_balance': u'114.64',
             u'usd_available': u'114.64',
             ---If base and quote were specified:
             u'fee': u'',
             ---If base and quote were not specified:
             u'btcusd_fee': u'0.25',
             u'btceur_fee': u'0.25',
             u'eurusd_fee': u'0.20',
             }
            There could be reasons to set base and quote to None (or False),
            because the result then will contain the fees for all currency pairs
            For backwards compatibility this can not be the default however.
        """
        url = self._construct_url("balance/")
        res = self._post(url, return_json=True, version=2)
        return res

    def buy_market_order_(self, first_cur, second_cur, amount):
        """
        Order to buy amount of bitcoins for market price.
        """
        data = {'amount': amount}
        url = self._construct_url_ord("buy/market/", first_cur, second_cur)
        res = self._post(url, data=data, return_json=True, version=2)
        if res is not None and not 'reason' in res:
            data_res = orders_format_response(first_cur, second_cur, res['datetime'],
                                              res['amount'], res['id'], res['price'],
                                              res['type'])
        else:
            data_res = {'error': True, 'msg': res['reason'] if 'reason' in res else ''}

        return data_res

    def sell_market_order_(self, first_cur, second_cur, amount):
        """
        Order to sell amount of bitcoins for market price.
        """
        data = {'amount': amount}
        url = self._construct_url_ord("sell/market/", first_cur, second_cur)
        res = self._post(url, data=data, return_json=True, version=2)

        if res is not None and not 'reason' in res:
            data_res = orders_format_response(first_cur, second_cur, res['datetime'],
                                              res['amount'], res['id'], res['price'],
                                              res['type'])
        else:
            data_res = {'error': True, 'msg': res['reason'] if 'reason' in res else ''}
        return data_res

    def buy_limit_order_(self, first_cur, second_cur, amount, price, limit_price=None):
        """
        Order to buy amount of bitcoins for specified price.
        """
        data = {'amount': amount, 'price': price}
        if limit_price is not None:
            data['limit_price'] = limit_price
        url = self._construct_url_ord("buy/", first_cur, second_cur)
        res = self._post(url, data=data, return_json=True, version=2)

        data_res = dict()
        if res or res is not None:
            data_res = orders_format_response(first_cur, second_cur, res['datetime'],
                                              res['amount'], res['id'], res['price'],
                                              res['type'])
        return jsonify(data_res)

    def sell_limit_order_(self, first_cur, second_cur, amount, price, limit_price=None):
        """
        Order to sell amount of bitcoins for specified price.
        """
        data = {'amount': amount, 'price': price}
        if limit_price is not None:
            data['limit_price'] = limit_price
        url = self._construct_url_ord("sell/", first_cur, second_cur)
        res = self._post(url, data=data, return_json=True, version=2)

        data_res = dict()
        if res or res is not None:
            data_res = orders_format_response(first_cur, second_cur, res['datetime'],
                                              res['amount'], res['id'], res['price'],
                                              res['type'])
        return jsonify(data_res)


# Backwards compatibility
class BackwardsCompat(object):
    """
    Version 1 used lower case class names that didn't raise an exception when
    Bitstamp returned a response indicating an error had occured.

    Instead, it returned a tuple containing ``(False, 'The error message')``.
    """
    wrapped_class = None

    def __init__(self, *args, **kwargs):
        """
        Instantiate the wrapped class.
        """
        self.wrapped = self.wrapped_class(*args, **kwargs)
        class_name = self.__class__.__name__
        warnings.warn(
            "Use the {} class rather than the deprecated {} one".format(
                class_name.title(), class_name),
            DeprecationWarning, stacklevel=2)

    def __getattr__(self, name):
        """
        Return the wrapped attribute. If it's a callable then return the error
        tuple when appropriate.
        """
        attr = getattr(self.wrapped, name)
        if not callable(attr):
            return attr

        @wraps(attr)
        def wrapped_callable(*args, **kwargs):
            """
            Catch ``BitstampError`` and replace with the tuple error pair.
            """
            try:
                return attr(*args, **kwargs)
            except BitstampError as e:
                return False, e.args[0]

        return wrapped_callable


class public(BackwardsCompat):
    """
    Deprecated version 1 client. Use :class:`Public` instead.
    """
    wrapped_class = Public


class trading_bit(BackwardsCompat):
    """
    Deprecated version 1 client. Use :class:`Trading` instead.
    """
    wrapped_class = TradingBit


# private_bit = PrivateBit()


# @app.route('/account_balance', methods=['POST'])
# def account_balance_2():
#     return private_bit.account_balance_2()


@app.errorhandler(400)
def custom400(e):
    """
    Bad Request
    :param e: error
    :return: json - custom message
    """
    return build_msg(error_code=400, msg=str(e)), 400


@app.errorhandler(401)
def custom401(e):
    """
    Unauthorized
    :param e: error
    :return: json - custom message
    """
    return build_msg(error_code=401, msg=str(e)), 401


@app.errorhandler(403)
def custom403(e):
    """
    Forbidden
    :param e: error
    :return: json - custom message
    """
    return build_msg(error_code=403, msg=str(e)), 403


@app.errorhandler(404)
def custom404(e):
    """
    Not Found
    :param e: error
    :return: json - custom message
    """
    return build_msg(error_code=404, msg=str(e)), 404
    # return "ERROR 404"


@app.errorhandler(405)
def custom405(e):
    """
    Method Not Allowed
    :param e: error
    :return: json - custom message
    """
    return build_msg(error_code=405, msg=str(e)), 405


@app.errorhandler(406)
def custom406(e):
    """
    Not Acceptable
    :param e: error
    :return: json - custom message
    """
    return build_msg(error_code=406, msg=str(e)), 406


@app.errorhandler(409)
def custom409(e):
    """
    Conflict
    :param e: error
    :return: json - custom message
    """
    return build_msg(error_code=409, msg=str(e)), 409


@app.errorhandler(410)
def custom410(e):
    """
    Gone
    :param e: error
    :return: json - custom message
    """
    return build_msg(error_code=410, msg=str(e)), 410


@app.errorhandler(500)
def custom500(e):
    """
    Internal Server Error
    :param e: error
    :return: json - custom message
    """
    return build_msg(error_code=500, msg=_(str(e))), 500


@app.errorhandler(501)
def custom501(e):
    """
    Not Implemented
    :param e: error
    :return: json - custom message
    """
    return build_msg(error_code=501, msg=str(e)), 501


@app.errorhandler(502)
def custom502(e):
    """
    Bad Gateway
    :param e: error
    :return: json - custom message
    """
    return build_msg(error_code=502, msg=str(e)), 502


@app.errorhandler(503)
def custom503(e):
    """
    Service Unavailable
    :param e: error
    :return: json - custom message
    """
    return build_msg(error_code=503, msg=str(e)), 503


@app.errorhandler(504)
def custom504(e):
    """
    Gateway Timeout
    :param e: error
    :return: json - custom message
    """
    return build_msg(error_code=504, msg=str(e)), 504