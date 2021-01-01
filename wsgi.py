#!env/bin/python
# -*- coding: utf-8 -*-

"""
api wsgi gateway к openstack

"""
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
from appmods.opensimage import get_images

logging.basicConfig(filename="/var/log/api-gateway/api.log", level=logging.INFO)
app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
# Печатать json с отступами
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

log = logging.getLogger("api-gateway")
app.logger.handlers = log.handlers
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
            log.info("Deny access  user %s exception %s", request_auth.username, excp)
            return make_response(jsonify({"msg": "Acssess deny"}),401)
        except DiscoveryFailure as excp:
            log.error("Cannot connect to keystone err %s", excp)
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
    return jsonify(OK_RESPONSE)


@app.route("/images", methods=["GET"])
@authenticate
def images(sess):
    """
    Функция описка доступных образов
    Если в get запросе пережается переменная id,
    то поиск образа осуществляетсяпо id
    :param sess: keystone session
    :return: flask response json json со1 списком доступных образов
    """
    if request.args and "id" in request.args:
        OK_RESPONSE["data"] = get_images(sess, request.args["id"])
    else:
        OK_RESPONSE["data"]=get_images(sess)
    return jsonify(OK_RESPONSE)


if __name__=="__main__":
    consoleHandler = logging.StreamHandler()
    log.addHandler(consoleHandler)
    app.logger.handlers = log.handlers
    app.run()
