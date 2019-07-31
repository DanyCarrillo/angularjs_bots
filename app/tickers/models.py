import json, sqlalchemy, ast, requests
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine
from flask import session
from app import app, genericConect, set_BackLogs
from app.commons import decrypt, datetimeconv, create_error_msg, create_success_msg

class TickersModel:
    def getformat_tickers(self,id_format):
        try:
            response = genericConect('sp_bots_exchange_formats_obtener',[id_format])
            if response:
                data = dict(
                    url=response[0][3],
                    method=response[0][4],
                    params=response[0][6],
                    data_type=response[0][5]
                )
                response = create_success_msg(data)
            else:
                msj = "Exception on sp_bots_exchange_formats_obtener"
                response = create_error_msg(msj)
        except Exception as e:
            response = create_error_msg(e)
        except sqlalchemy.exc.InternalError as e:
            response = create_error_msg(e)
        finally:
            return response