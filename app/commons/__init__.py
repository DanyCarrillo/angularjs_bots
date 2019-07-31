import json, datetime, requests, collections, decimal, pyaes, base64
from functools import wraps
from flask import Flask, request, redirect, session


app = Flask('app', template_folder='template')
app.config.from_object('config.DevelopmentConfig')


def encrypt(data):
    aes     = pyaes.AESModeOfOperationCTR(app.config['KEY_AES'])
    encrypt = base64.b64encode(aes.encrypt(data))
    return encrypt

def decrypt(data):
    aes    = pyaes.AESModeOfOperationCTR(app.config['KEY_AES'])
    decrypt = aes.decrypt(base64.b64decode(data))
    return decrypt


def get_exception_msg(e):
    res = str(e).partition('CONTEXT:')
    res = res[0].partition('Exception:')
    return res[2]


def create_error_msg(mensaje):
    data  = {
        'success': False, 
        'mensaje': mensaje
    } 
    
    return data 


def create_success_msg(data):
    response = {
        'success': True, 
        'datos': data
    }

    return response 


def permissions(func):
    @wraps(func)
    def permission_decorator(*args, **kwargs):
        permission = app.config['USER_PERMISSION']
        if 'id_user' in session:
            if session['user_data_login']['role'] == 'admin':
                return func(*args, **kwargs)
            elif session['user_data_login']['role'] == 'user':
                if request.method in permission['user']:
                    return func(*args, **kwargs)
                else:
                    data = {
                        "error": True, 
                        "mensaje": 'Sorry, URL not permision'
                    }
                    return data, 401
            else:
                data = {
                    "error": True, 
                    "mensaje": 'Sorry, URL not permision'
                }
                return data, 401
        else:
            return redirect('/modUser/login')

    return permission_decorator


def val_num_slash(request_path, num):
    cant_value = len(request_path.split('/'))
    
    return cant_value == num


def emitirAClientes(url='http://localhost:5000/emitirOrderSockect', data={}):
    respuesta = {}
    res = request_post_url(url, data=json.dumps(data))

    if res.status_code == 200:
        respuesta['status'] = True
    else:
        respuesta['status'] = False
    return respuesta


def datetimeconv(o):
    if isinstance(o, datetime.datetime):
        return o.__str__().format(o.year, o.month, o.day)
    if isinstance(o, decimal.Decimal):
        return float(o)



@app.before_request
def limit_remote_addr():
    ipAllowed = app.config['IP_ALLOWED']
    ip = request.remote_addr
    if ip in ipAllowed:
        pass
    else:
        abort(403, 'Unauthorized')


def convert_unicode(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert_unicode, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert_unicode, data))
    else:
        return data


def orders_format_response(base, quote, date_time, amount, id, price, type):
    res = {
        'firstCurrency': base,
        'secondCurrency': quote,
        'date': date_time,
        'amount': amount,
        'idOrder': id,
        'price': price,
        'typeOrder': 'sell' if type == 1 else 'buy'
    }
    return res

def request_post_url(url, data):
    headers = {'Content-Type': 'application/json'}
    return requests.post(url, data=data, headers=headers)
