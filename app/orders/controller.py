import json, requests,logging
import sqlalchemy
from flask import render_template, jsonify, request, session
from app.commons import get_exception_msg,create_error_msg,create_success_msg,val_num_slash,convert_unicode
from app.orders.models import OrdersModel


class OrdersController(object):
    def __init__(self):
        pass

    @staticmethod
    def list():
        return render_template("orders/index.html")

    def Show_AllActivesOrdersByUser(self):
        try:
            data = request.json
            model = OrdersModel()  
            res = model.Show_OrdersByUserYPair(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e
        