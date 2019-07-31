import hashlib
import requests
import json

url_okex = "https://www.okex.com/api/v1/" 

###
# crea una orden 
# @autor:@gangulo
# @date: 05/07/2018
# @param send_data dict 
#   
#  "api_key":"8a60dfsdf-34234-42423-42342",
#  "symbol":"btc_usdt",
#  "type":"sell",  limit order(buy/sell) market order(buy_market/sell_market)
#  "price":"20000", For limit orders, the price must be between 0~1,000,000. 
#                   IMPORTANT: for market buy orders, the price is to total amount you want to buy, 
#                   and it must be higher than the current price of 0.01 BTC 
#                   (minimum buying unit), 0.1 LTC or 0.01 ETH. For market sell orders, the price is not required
#  "amount":"0.00000001", Must be higher than 0.01 for BTC, 0.1 for LTC or 0.01 for ETH.For market buy roders, the amount is not required
#  "sign":"",
#  "secret_key":"KAJFUFNFUCDIDMDD8374JDKDJDJDJU"
#    
###

def createOrderOkex(send_data):
    symbol = send_data['symbol']
    symbol = symbol.split("_")
    firstCurrency = symbol[0]
    secondCurrency = symbol[1]
    send_data["sign"] = sign(send_data)
    res    = requests.post(url_okex + "trade.do",data=send_data)
    res    = res.json()
    if res.has_key("order_id"):
        sendIdOrden = {}
        order_id = res["order_id"]
        sendIdOrden['api_key']  = send_data['api_key']
        sendIdOrden['symbol']   = send_data['symbol']
        sendIdOrden['secret_key'] = send_data['secret_key']
        sendIdOrden['order_id'] = order_id
        sendIdOrden['sign']     = sign(sendIdOrden)
        res    = requests.post(url_okex + "order_info.do",data=sendIdOrden)
        res    = res.json()
        if res.has_key("orders"):
            rest = {}
            rest['firstCurrency'] = firstCurrency
            rest['secondCurrency'] = secondCurrency
            rest['date'] = res["orders"][0]['create_date'] 
            rest['amount'] = res["orders"][0]['amount']
            rest['idOrder'] = order_id
            rest['price'] = res["orders"][0]["price"]
            rest['status'] = res["orders"][0]['status']
            rest['total'] = float(res["orders"][0]["price"])*float(res["orders"][0]["amount"])
            rest['typeOrder'] = res["orders"][0]["type"]
        else:
            rest = {}
            error = getError(res['error_code'])
            rest["error_code"] = error  

    else:
        rest = {}
        error = getError(res['error_code'])
        rest["error_code"] = error
    return rest

###
# obtiene el balance del usuario
# @autor:@gangulo
# @date: 05/07/2018
# @param send_data dict 
#   
#  "api_key":"8a60dfsdf-34234-42423-42342",
#  "sign":"",
#  "secret_key":"KAJFUFNFUCDIDMDD8374JDKDJDJDJU"
#    
###

def getBalanceOkex(send_data):
    send_data["sign"] = sign(send_data)
    res    = requests.post(url_okex + "userinfo.do",data=send_data)
    res    = res.json()
    if res.has_key("error_code"):
        error = getError(res['error_code'])
        res["error_code"] = error
    return res


###
# obtiene el order book del exchange Okex
# @autor:@gangulo
# @date: 05/07/2018
#      
###

def orderBookOkex(send_data):
    symbol = send_data['symbol']
    res    = requests.get(url_okex + "depth.do?symbol=" + symbol)
    res    = res.json()
    if res.has_key("error_code"):
        error = getError(res['error_code'])
        res["error_code"] = error
    return res

def marketPriceOkex(send_data):    
    symbol = send_data['symbol']
    res    = requests.get(url_okex+"ticker.do?symbol="+ symbol)
    res    = res.json()    
    bid = 0
    ask = 0    
    if res.has_key("ticker"):        
        bid=res['ticker']['buy']
        ask=res['ticker']['sell']
    return {'bid':bid,'ask':ask}  

###
# lista las ordenes
# @autor:@gangulo
# @date: 05/07/2018
# @param send_data dict 
#   
#  "api_key":"8a60dfsdf-34234-42423-42342",
#  "symbol":"btc_usdt",
#  "status":"0",  0 for unfilled orders, 1 for filled orders
#  "current_page":"1",
#  "page_lengtht":"20", number of orders returned per page, maximum 200
#  "sign":"",
#  "secret_key":"KAJFUFNFUCDIDMDD8374JDKDJDJDJU"
#    
###

def historyOrderOkex(send_data):
    send_data["sign"] = sign(send_data)
    res    = requests.post(url_okex + "order_history.do",data=send_data)
    res    = res.json()
    if res.has_key("error_code"):
        error = getError(res['error_code'])
        res["error_code"] = error
    return res


 ###
# crea la firma que se necesita para realizar los request a okex 
# @autor:@gangulo
# @date: 05/07/2018
# @param send_data dict 
#       
###   

def sign(send_data):
    secret_key    = send_data['secret_key']
    data = ""
    for key in sorted(send_data.keys()):
        if key != "sign" and key != "secret_key":
            data += key + '=' + str(send_data[key]) +'&'
    data += 'secret_key=' + secret_key
    string =  hashlib.md5(data.encode('utf-8')).hexdigest().upper()
    return string


###
# obtiene el error mapeado segun la documentacion https://support.okcoin.com/hc/en-us/articles/360000695152-REST-API-Request-Process
# @autor:@gangulo
# @date: 05/07/2018
# @param key str 
#       
###   


def getError(key):
    error = {}
    error["10000"] = "Mandatory parameters cannot be blank"
    error["10001"] = "Request frequency exceeds the port limit"
    error["10002"] = "System error"
    error["10004"] = "This IP is not on the whitelist"
    error["10005"] = "SecretKey does not exist"
    error["10006"] = "Api_key does not exist"
    error["10007"] = "Signatures do not match"
    error["10008"] = "Invalid parameters"
    error["10009"] = "Order does not exist"
    error["10010"] = "Insufficient balance"
    error["10011"] = "BTC/LTC buying volume is smaller than the minimum limit"
    error["10012"] = "Only btc_usd ltc_usd are supported on this website"
    error["10013"] = "This port only accepts https requests"
    error["10014"] = "Order price cannot be <=0 or >=1000000"
    error["10015"] = "Order price differs too much from last traded price "
    error["10016"] = "Insufficient tokens"
    error["10017"] = "API authentication failed"
    error["10018"] = "Borrowing amount cannot be lower than the minimum limit [usd:100,btc:0.1,ltc:1]"
    error["10019"] = "Loan agreement is not included"
    error["10020"] = "Fee cannot be greater than 1%"
    error["10021"] = "Fee cannot be smaller than 0.01%"
    error["10023"] = "Last traded price retrieval error"
    error["10024"] = "Insufficient available loan amount"
    error["10025"] = "Quota reached. Loan temporarily not available"
    error["10026"] = "Loan (including the reserved loan) and security deposit cannot be withdrawn"
    error["10027"] = "Withdrawal will not be available for 24 hours after important validation info is edited"
    error["10028"] = "Withdrawal amount exceeds today's limit"
    error["10029"] = "Please cancel or repay all loans before withdrawal"
    error["10031"] = "BTC/LT deposits require 6 confirmations"
    error["10032"] = "Not linked to mobile number / Google Authenticator"
    error["10033"] = "Service fee is greater than network fee"
    error["10034"] = "Service fee is smaller than network fee"
    error["10035"] = "Insufficient BTC/LTC amount"
    error["10036"] = "Withdrawal amount smaller than the minimum limit"
    error["10037"] = "Fund password not set"
    error["10040"] = "Withdrawal cancellation failed"
    error["10041"] = "Withdrawal address does not exist/is not validated"
    error["10042"] = "Incorrect fund password"
    error["10043"] = "Futures equity error. Withdrawal failed"
    error["10044"] = "Loan cancellation failed"
    error["10047"] = "This feature is not available for subaccount"
    error["10048"] = "Withdrawal info does not exist"
    error["10049"] = "The unfilled amount of small amount order (<0.15BTC) cannot be larger than 50"
    error["10050"] = "Repeated cancellation order"
    error["10052"] = "Withdrawal limited"
    error["10064"] = "Part of the asset cannot be withdrawn within 48 hours after USD deposit"
    error["10100"] = "Account has been frozen"
    error["10101"] = "Incorrect order type"
    error["10102"] = "Order does not belong to this account"
    error["10103"] = "Incorrect private order key"
    error["10216"] = "Private API"
    error["1002"] = "Transaction amount is larger than the available balance"
    error["1003"] = "Transaction amount is smaller than the minimum limit"
    error["1004"] = "Transaction amount is smaller than 0"
    error["1007"] = "No trading market data"
    error["1008"] = "No latest market data"
    error["1009"] = "No order"
    error["1010"] = "Accounts of order creation and order cancellation do not match"
    error["1011"] = "User not found"
    error["1013"] = "Order category not found"
    error["1014"] = "Not logged in"
    error["1015"] = "Unable to retrieve market data"
    error["1017"] = "Incorrect Date parameter"
    error["1018"] = "Order placement failed"
    error["1019"] = "Order cancellation failed"
    error["1024"] = "Token does not exist"
    error["1025"] = "Chart category not found"
    error["1026"] = "Base token amount not found"
    error["1027"] = "Invalid parameter"
    error["1028"] = "Failed to keep the decimals"
    error["1029"] = "Preparing"
    error["1030"] = "Unable to trade with loan"
    error["1031"] = "Insufficient transfer balance"
    error["1032"] = "The token is non-transferable"
    error["1035"] = "Invalid password"
    error["1036"] = "Invalid Google Authentication code"
    error["1037"] = "Incorrect Google Authentication code"
    error["1038"] = "Google Authentication code already used"
    error["1039"] = "SMS code incorrect attempt limit"
    error["1040"] = "Invalid SMS code"
    error["1041"] = "Incorrect SMS code"
    error["1042"] = "Google authentication code incorrect attempt limit"
    error["1043"] = "Login password and fund password cannot be identical"
    error["1044"] = "Incorrect original password"
    error["1045"] = "2 factor authentication not set"
    error["1046"] = "Original password is blank"
    error["1048"] = "Account is frozen"
    error["1201"] = "Account will be removed at 0:00"
    error["1202"] = "Account does not exist"
    error["1203"] = "Transfer amount is larger than balance"
    error["1204"] = "Other tokens cannot be transferred"
    error["1205"] = "Master and sub accounts not set"
    error["1206"] = "Withdrawal account is frozen"
    error["1207"] = "Transfer is not supported"
    error["1208"] = "Transfer account does not exist"
    error["1209"] = "Current API cannot be used"
    error["HTTP Error Code 403"] = "Request too frequent. IP is blocked"
    error["Ping not working"] = "Request too frequent. IP is blocked"
    resError = error.get(str(key), "No found error")
    return resError