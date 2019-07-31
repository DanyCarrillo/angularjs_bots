import hashlib
import requests
import json
import datetime
import urlparse
import urllib
import hmac
import base64

url_huobi = "https://api.huobi.pro"

headers = {
            "Accept": "application/json",
            'Content-Type': 'application/json',
        }

def cancelOrderHuobi(send_data):
    sendC = {}
    sendC.update(send_data)
    id_account = getAccount(send_data)
    idOrden = send_data['order-id']
    sendC["account-id"] = id_account
    method = "POST"
    url_request = "/v1/order/orders/"+idOrden+"/submitcancel"
    request = sign(sendC,method,url_huobi,url_request)
    dataRq = {}
    for key in send_data:
        if key != "AccessKeyId" and key != "SecretKey" and key != "account-id":
            dataRq[key] = send_data[key]
    dataRq = json.dumps(dataRq)
    res    = requests.post(request,dataRq,headers = headers)
    res    = res.json()
    return res

###
# crea una orden 
# @autor:@gangulo
# @date: 05/07/2018
# @param send_data dict 
#   
# "AccessKeyId":"2de8644b-aef5aa5a-ceb3242-f5434",
# "SecretKey": "e522423e5-a77324235f-2bf234235-2fe22",
# "symbol":"eth_btc",
# "amount": "0.0894",
# "price" : "0.050058",
# "source": "api",
# "type"  : "buy-limit"
#    
###

def createOrderHuobi(send_data):
    sendC = {}
    sendC.update(send_data)
    id_account = getAccount(send_data)
    symbol = send_data['symbol']
    symbol = symbol.split("_")
    firstCurrency = symbol[0]
    secondCurrency = symbol[1]
    symbol = symbol[0]+symbol[1]
    sendC["symbol"] = symbol
    sendC["account-id"] = id_account
    method = "POST"
    url_request = "/v1/order/orders/place"
    request = sign(sendC,method,url_huobi,url_request)
    dataRq = {}
    for key in sendC:
        if key != "AccessKeyId" and key != "SecretKey":
            dataRq[key] = sendC[key]
    dataRq = json.dumps(dataRq)
    res    = requests.post(request,dataRq,headers = headers)
    res    = res.json()
    if res.has_key("status") and res['status'] == "ok":
        idOrden = res['data']
        method = "GET"
        url_request = "/v1/order/orders/"+str(idOrden)
        sendOrden = {}
        for x in sendC:
            if x == "AccessKeyId" or x == "SecretKey":
                sendOrden[x] = sendC[x]
        request = sign(sendOrden,method,url_huobi,url_request)
        restInfoOrder  = requests.get(request)
        restInfoOrder    = restInfoOrder.json()
        if restInfoOrder.has_key("status") and res['status'] == "ok":
            res = {}
            res['firstCurrency'] = firstCurrency
            res['secondCurrency'] = secondCurrency
            res['date'] = restInfoOrder['data']['created-at'] 
            res['amount'] = restInfoOrder['data']['amount']
            res['idOrder'] = idOrden
            res['price'] = restInfoOrder['data']['price']
            res['status'] = restInfoOrder['data']['state']
            res['total'] = float(restInfoOrder['data']['price']) * float(restInfoOrder['data']['amount'])
            res['typeOrder'] = restInfoOrder['data']['type']

    return res if 'idOrder' in res else res

###
# obtiene el balance del usuario
# @autor:@gangulo
# @date: 05/07/2018
# @param send_data dict 
#   
# "AccessKeyId":"2de8644b-aef5aa5a-ceb04e37-ffbb9",
# "SecretKey": "e52286e5-a773ca5f-2bf32305-2fe22" 
#    
###


def getBalanceHuobi(send_data):
    id_account = getAccount(send_data)    
    method = "GET"
    url_request = "/v1/account/accounts/"+str(id_account)+"/balance"
    request = sign(send_data,method,url_huobi,url_request)
    res    = requests.get(request)
    res    = res.json()
    return res

###
# obtiene el order book del exchange Huobi
# @autor:@gangulo
# @date: 05/07/2018
#      
###

def orderBookHuobi(send_data):
    symbol = send_data['symbol']
    symbol = symbol.split("_")
    symbol = symbol[0]+symbol[1]
    type   = send_data['type']
    res    = requests.get(url_huobi + "/market/depth?symbol=" + symbol+ "&type="+type)  
    res    = res.json()
    sales = []
    purcharses = []
    if res.has_key("tick"):
        for x in res['tick']['bids']:
            purcharses.append({'amount':x[1],'price':x[0]})
        for x in res['tick']['asks']:
            sales.append({'amount':x[1],'price':x[0]})
    return {'sales':sales,'purcharses':purcharses}

def marketPriceHuobi(send_data):
    symbol = send_data['symbol']
    symbol = symbol.split("_")
    symbol = symbol[0]+symbol[1]
    type   = send_data['type']
    res    = requests.get(url_huobi + "/market/detail/merged?symbol=" + symbol+ "&type="+type)  
    res    = res.json()    
    bid = 0
    ask = 0    
    if res.has_key("tick"):
        open=res['tick']['open']
        bid=res['tick']['bid'][0]
        ask=res['tick']['ask'][0]

    return {'bid':bid,'ask':ask}    


###
# lista las ordenes activas
# @autor:@gangulo
# @date: 05/07/2018
# @param send_data dict 
#   
# "AccessKeyId":"2de8644b-aef5aa5a-ceb04e37-ffbb9",
# "SecretKey": "e52286e5-a773ca5f-2bf32305-2fe22", 
# "symbol":"eth_btc",
# "size": "10"
#    
###

def historyOrderHuobi(send_data):
    sendH = {}
    sendH.update(send_data)
    id_account = getAccount(sendH)
    symbol = sendH['symbol']
    symbol = symbol.split("_")
    symbol = symbol[0]+symbol[1]
    sendH["symbol"] = symbol
    sendH["account-id"] = id_account    
    method = "GET"
    url_request = "/v1/order/openOrders"
    request = sign(sendH,method,url_huobi,url_request)
    res    = requests.get(request)
    res    = res.json()
    return res
    
###
# crea la firma que se necesita para realizar los request a huobi 
# @autor:@gangulo
# @date: 05/07/2018
# @param send_data dict 
#       
###  

def sign(sendA,method,url,request_url):
    send = {}
    send.update(sendA)
    secret_key = send['SecretKey']
    data = ""
    send['SignatureMethod'] = "HmacSHA256"
    send['SignatureVersion'] = "2"
    send['Timestamp'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    sort = {}
    url = urlparse.urlparse(url).hostname
    for key in sorted(send.keys()):
        if method == "GET":
            if key != "SecretKey":
                sort[key] = send[key]
        if method == "POST":
            if key == "AccessKeyId" or key == "SignatureMethod" or key == "SignatureVersion" or key == "Timestamp":
                sort[key] = send[key]
    request_sort =sort
    sort = sorted(sort.items(), key=lambda d: d[0], reverse=False)
    data = urllib.urlencode(sort)
    payload = [method, url.lower(),request_url,data]
    payload = '\n'.join(payload)
    payload = payload.encode(encoding='UTF8')
    secret_key = secret_key.encode(encoding='UTF8')
    digest = hmac.new(secret_key, payload, digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(digest)
    request_sort["Signature"] = signature
    data = urllib.urlencode(request_sort)
    request_url =  "https://"+url+request_url+"?"+data
    return request_url


    
###
# obtiene el account dependiendo del secret y el accessId
# @autor:@gangulo
# @date: 05/07/2018
# @param send_data dict 
#       
###  

def getAccount(sendD):
    sendAccount = {}
    sendAccount["AccessKeyId"] = sendD['AccessKeyId']
    sendAccount["SecretKey"] = sendD['SecretKey']
    method = "GET"
    url_request = "/v1/account/accounts"
    request = sign(sendAccount,method,url_huobi,url_request)
    res    = requests.get(request)
    res    = res.json()
    if res.has_key("data"):
        id_account = res["data"][0]['id']
        return id_account
    else:
        raise NameError(res["err-msg"])    

