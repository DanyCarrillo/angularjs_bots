import json, requests,logging
import sqlalchemy
from flask import render_template, jsonify, request, session
from app.commons import get_exception_msg,create_error_msg,create_success_msg,val_num_slash,convert_unicode
from app.activePairs.models import pairsModel


class ActivePairsController(object):
    def __init__(self):
        pass

    @staticmethod
    def list():
        return render_template("activePairs/index.html")

    def viewPairsController(self):
        try:
            pairs_model=pairsModel()
            response=pairs_model.viewPairsModel()
            if response['success']==True:
                return response
            else:
                return create_error_msg(response)
        except sqlalchemy.exc.InternalError as e:
            raise e

    def suspendPairController(self,res):
        try:
            data = json.dumps(res.get_json(force=True))
            data = json.loads(data, encoding='utf-8')
            pairs_model=pairsModel()
            response=pairs_model.suspendPairModel(data)
            if response['success']==True:
                response= jsonify(response)
            else:
                response= jsonify(response)
        except Exception as e:
            response=create_error_msg(e)
        except sqlalchemy.exc.InternalError as e:
            response= create_error_msg(e)
        finally:
            return response

    def selPairTypeCoins(self):
        try:
            data = request.json
            model = pairsModel()
            res = model.selectPairTypeCoins(data)
            return jsonify(res)
        except sqlalchemy.exc.InternalError, e:
            raise e