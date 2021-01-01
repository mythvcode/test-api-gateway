#!env/bin/python
# -*- coding: utf-8 -*-
import logging
from functools import wraps
from flask import Flask
from flask import jsonify
from flask import make_response
from flask import request

from keystoneauth1 import loading
from keystoneauth1 import session
from keystoneauth1.exceptions.http import Unauthorized
from keystoneauth1.exceptions.discovery import DiscoveryFailure

from appmods.opensnet import get_networks

logging.basicConfig(filename="/var/log/api-gateway/api.log", level=logging.INFO)
app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
# Печатать json с отступами
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

app.logger.handlers = logging.getLogger("api-gateway").handlers
OK_RESPONSE = {"msg": "OK"}


@app.before_request
def clear_response():
    """
    Функция удаляет даныые по ключу data из OK_RESPONSE,
    созданные при предыдущих запросах.
    """
    if "data" in OK_RESPONSE:
        OK_RESPONSE.pop("data")


def authenticate(func):
    """
    Декоратор для аутентификации вызова метода api
    перехватывает  исключение Unauthorized из вызываемой функции
    :param func: декорируемая функция
    :return decorated: декорированная функция
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        request_auth = request.authorization
        if not request_auth:
            return make_response(jsonify({"msg": "No auth credentials"}), 401)
        loader = loading.get_plugin_loader('password')
        auth = loader.load_from_options(auth_url="http://localhost/identity",
                                        username=request_auth.username,
                                        password=request_auth.password,
                                        user_domain_id="default")
        sess = session.Session(auth=auth)
        try:
            return func(sess, *args, **kwargs)
        except Unauthorized as excp:
            app.logger.info(f"Deny access  user {request_auth.username} exception {excp}")
            return make_response(jsonify({"msg": "Acssess deny"}),401)
        except DiscoveryFailure as excp:
            app.logger.error(f"Cannot connect to keystone err {excp}")
            return make_response(jsonify({"msg": "No connection to keystone"}), 500)
    return decorated


@app.route("/networks", methods=["GET"])
@authenticate
def networks(sess):
    """
    Функция описка доступных сетей neutron
    Если в get запросе пережается переменная id то поиск сети осуществляется
    по id сети
    :param sess: keystone session
    :return: flask response json json со списком доступных сетей
    """
    if request.args and "id" in request.args:
        OK_RESPONSE["data"] = get_networks(sess, request.args["id"])
    else:
        OK_RESPONSE["data"]=get_networks(sess)
    print(type(jsonify(OK_RESPONSE)))
    return jsonify(OK_RESPONSE)


if __name__=="__main__":
    consoleHandler = logging.StreamHandler()
    app.logger.addHandler(consoleHandler)
    app.run()
