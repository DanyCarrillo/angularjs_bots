import json, requests,logging
import sqlalchemy
from flask import render_template, jsonify, request, session
from app.commons import get_exception_msg,create_error_msg,create_success_msg,val_num_slash,convert_unicode
from app.orderBook.models import OrderBookModel


class OrderBookController(object):
    def __init__(self):
        pass

    @staticmethod
    def list():
        return render_template("orderBook/index.html")

    def listOrderBookByPair(self):
        try:
            data = request.json
            model = OrderBookModel()
            res = model.orderBookListByPair(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError as e:
            raise e

