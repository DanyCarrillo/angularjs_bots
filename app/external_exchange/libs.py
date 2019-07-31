
import requests
import smtplib
from flask import jsonify

# ERROR_MSG_TEMPLATE = {
#     'success': False,
#     'msg': '',
#     'error_code': 000,
#     'data': []
# }


def error_msg_template_(msg, error_code):
    return {
        'success': False,
        'msg': msg,
        'error_code': error_code,
        'data': []
    }


def build_msg(error_code, msg):

    build_msg = error_msg_template_(error_code, msg)
    return jsonify(build_msg)


SENDER_EMAIL = 'pruebabitinka@gmail.com'
SENDER_PASSWORD = 'P@ssw0rd2018'


def send_email_to_userExchange(msg):
    try:
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo() #identify computer
        mail.starttls() #transport layer security
        mail.login(SENDER_EMAIL, SENDER_PASSWORD)
        mail.sendmail(SENDER_EMAIL, 'pruebabitinka@gmail.com', msg)
        mail.close()

    except Exception as e:
        print(e)


class BitstampError(Exception):
    pass


class TransRange(object):
    """
    Enum like object used in transaction method to specify time range
    from which to get list of transactions
    """
    HOUR = 'hour'
    MINUTE = 'minute'


class BaseClient(object):
    """
    A base class for the API Client methods that handles interaction with
    the requests library.
    """
    api_url = {1: 'https://www.bitstamp.net/api/',
               2: 'https://www.bitstamp.net/api/v2/'}
    exception_on_error = True

    def __init__(self, proxydict=None, *args, **kwargs):
        self.proxydict = proxydict

    def _get(self, *args, **kwargs):
        """
        Make a GET request.
        """
        return self._request(requests.get, *args, **kwargs)

    def _post(self, *args, **kwargs):
        """
        Make a POST request.
        """
        data = self._default_data()
        data.update(kwargs.get('data') or {})
        kwargs['data'] = data
        return self._request(requests.post, *args, **kwargs)

    def _default_data(self):
        """
        Default data for a POST request.
        """
        return {}

    def _construct_url(self, url, par=None):
        """
        Adds the orderbook to the url if base and quote are specified.
        """
        if not par:
            return url
        else:
            url = url + par.lower() + "/"
            return url

    def _construct_url_ord(self, url, base, quote):
        """
        Adds the orderbook to the url if base and quote are specified.
        """
        if not base and not quote:
            return url
        else:
            url = url + base.lower() + quote.lower() + "/"
            return url

    def _request(self, func, url, version=1, *args, **kwargs):
        """
        Make a generic request, adding in any proxy defined by the instance.

        Raises a ``requests.HTTPError`` if the response status isn't 200, and
        raises a :class:`BitstampError` if the response contains a json encoded
        error message.
        """
        return_json = kwargs.pop('return_json', False)
        url = self.api_url[version] + url
        response = func(url, *args, **kwargs)

        if 'proxies' not in kwargs:
            kwargs['proxies'] = self.proxydict

        return response.json()
