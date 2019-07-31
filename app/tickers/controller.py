
import json, requests
import sqlalchemy
from flask import render_template, jsonify, request, session
from app.commons import get_exception_msg,create_error_msg,create_success_msg,val_num_slash,convert_unicode
from app.tickers.models import TickersModel
from app.trading.models import TradingModel

class TickersController(object):
    def __init__(self):
        pass
    @staticmethod
    def list():
        return render_template("tickers/index.html")

    def viewTickers(self):
        try:
            ticker_model=TickersModel()
            response=ticker_model.getformat_tickers("T")
            if response['success']==True:
                url=response['datos']['url']
                data= requests.get(url)
                if data.status_code==200:
                    return create_success_msg(data.json())
                else:
                    return jsonify('Api not response'), int(data.status_code)
            else:
                return create_error_msg(response)
        except sqlalchemy.exc.InternalError as e:
            raise e

    def viewVolumenMarketcap(self):
        try:
            trading = TradingModel()
            res_format_exchange = trading.getformat("V")
            ip_vol = res_format_exchange['datos']['url'] #"http://192.168.8.3:3333/getVol24"

            ticker_model=TickersModel()
            volumen=requests.get(ip_vol).json()
            if volumen:
                return volumen
            else:
                return volumen
        except sqlalchemy.exc.InternalError as e:
            raise e
