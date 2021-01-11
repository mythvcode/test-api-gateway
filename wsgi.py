#!env/bin/python
# -*- coding: utf-8 -*-

"""
api wsgi gateway to openstack

"""
import logging
import os
from functools import wraps
from pathlib import Path
from flask import Flask
from flask import jsonify
from flask import make_response
from flask import request
from werkzeug.exceptions import BadRequest as WZBadRequest

from keystoneauth1 import loading
from keystoneauth1 import session
from keystoneauth1.exceptions.http import Unauthorized
from keystoneauth1.exceptions.discovery import DiscoveryFailure
from keystoneauth1.exceptions.connection import  ConnectFailure
from novaclient.exceptions import BadRequest, NotFound, Conflict

from appmods.opensnet import OpenSNet
from appmods.opensimage import OpenSImage
from appmods.opensserver import OpenStackServer

WSGI_LOG = os.environ.get("WSGI_LOG", "/var/log/api-gateway/api.log")
USER_DOMAIN_ID = os.environ.get("USER_DOMAIN_ID", "default")

Path(WSGI_LOG).parents[0].mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename=WSGI_LOG, level=logging.INFO)
app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
# Печатать json с отступами
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

log = logging.getLogger("api-gateway")
if os.environ.get("INDOCKER"):
    consoleHandler = logging.StreamHandler()
    log.addHandler(consoleHandler)

KEYSTONE_URL = os.environ.get("KEYSTONE_URL", "http://localhost/identity")
app.logger.handlers = log.handlers
OK_RESPONSE = {"msg": "OK"}


@app.before_request
def clear_response():
    """
    The function removes the "data" key from OK_RESPONSE dict,
    what was created on previous requests.
    """
    if "data" in OK_RESPONSE:
        del OK_RESPONSE["data"]


def authenticate(func):
    """
    Decorator to authenticate api method call.
    catches the Unauthorized, DiscoveryFailure, ConnectFailure
    exceptions from the called function.
    :param func: decorating function
    :return decorated: decorated function
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        request_auth = request.authorization
        if not request_auth:
            return _make_msg_response("No auth credentials", 401)
        loader = loading.get_plugin_loader('password')
        auth = loader.load_from_options(auth_url=KEYSTONE_URL,
                                        username=request_auth.username,
                                        password=request_auth.password,
                                        user_domain_id=USER_DOMAIN_ID)
        sess = session.Session(auth=auth)
        try:
            return func(sess, *args, **kwargs)
        except Unauthorized as excp:
            log.info("Deny access  user %s exception %s", request_auth.username, excp)
            return _make_msg_response("Acssess deny", 401)
        except DiscoveryFailure as excp:
            log.error("Cannot connect to keystone err %s", excp)
            return _make_msg_response("No connection to keystone", 500)
        except ConnectFailure as excp:
            log.error("Cannot connect to endpoint %s", excp)
            return _make_msg_response(f"Cannot connect to endpoint {excp}", 500)
    return decorated


@app.route("/<get_req>", methods=["GET"])
@authenticate
def get_data(sess, get_req):
    """
    Function for finding the requested data,
    if the variable id is passed, then the data is searched
    by the id parameter
    :return: flask response json with requested data
    """
    # Переделано  с целью сохранить функционал
    # и создвать экзепляр только нужного класса
    lookup_cls = {
            "networks": {"cls": OpenSNet,"method": "get_networks"},
            "images": {"cls": OpenSImage,"method": "get_images"},
            "flavors": {"cls": OpenStackServer,"method": "get_flavors"},
            "servers": {"cls": OpenStackServer, "method": "get_servers"}
            }
    try:
        cls_inst = lookup_cls[get_req]["cls"](sess)
        method = getattr(cls_inst, lookup_cls[get_req]["method"])

    except KeyError:
        log.info("Route /%s not faund", get_req)
        return _make_msg_response("URL Not found", 404)

    if request.args and "id" in request.args:
        OK_RESPONSE["data"] = method(request.args["id"])
    else:
        OK_RESPONSE["data"] = method()

    if not OK_RESPONSE["data"]:
        return _make_msg_response("Data not found", 404)
    return jsonify(OK_RESPONSE)


@app.route("/create_server", methods=["POST"])
@authenticate
def create_srv(sess):
    """
    Function for create server
    For creation used request.json data
    :param sess: keystone session
    :return: flask response json with id created server
    """
    if not request.data:
        return _make_msg_response("Empty request data", 400)

    # Проверка на корректность данных в request.json
    required_data = ("server_name", "image_id", "flavor_id", "network_ids")
    err = _check_request_json(required_data)
    if err:
        return err

    if not request.json["network_ids"] or not \
            isinstance(request.json["network_ids"], list):
        raise _make_msg_response("Network_ids must be not empty list", 400)

    try:
        sever = OpenStackServer(sess)
        OK_RESPONSE["data"] = sever.create_server(**request.json)

    except BadRequest as excp:
        log.error("Bad request %s", excp)
        return _make_msg_response(f"Error create server {excp}", 400)

    return jsonify(OK_RESPONSE), 201


@app.route("/manage_server", methods=["POST"])
@authenticate
def manage_serv(sess):
    """
    Function for manage servers
    If sucsess action return OK_RESPONSE
    :param sess: keystone session
    :return: flask response json  with status of request
    """
    if not request.data:
        return  _make_msg_response("Empty request data", 400)

    reuired_data = ("srvid", "action")
    alowed_action = ("stop", "start", "delete")
    err = _check_request_json(reuired_data)
    if err:
        return err
    if request.json["action"] not in alowed_action:
        return _make_msg_response(f'Not allowed action {request.json["action"]}', 400)

    try:
        server = OpenStackServer(sess)
        server.manage_server(**request.json)
    except Conflict as excp:
        log.warning("Conflict manage server %s", excp)
        return _make_msg_response(f"Conflict '{excp}'", 409)
    except NotFound:
        return _make_msg_response(f"server with id '{request.json['srvid']}'"
                                  " not found", 404)

    return jsonify(OK_RESPONSE), 202

def _check_request_json(reuired_data):
    """
    The function checks for the correctness
    of the query json data
    :param reuired_data: Required keys
    :return: None if all OK else,  flask Response class with error
    """
    try:
        no_in_reques = [req_d for req_d in reuired_data if req_d not in request.json]
        if no_in_reques:
            return _make_msg_response(f"Not all required data is given '{no_in_reques}'", 400)

        no_in_reuired_data = [req_d for req_d in request.json if req_d not in reuired_data]
        if no_in_reuired_data:
            return _make_msg_response(f"Error not allowed keys '{no_in_reuired_data}'", 400)

    except WZBadRequest:
        log.error("Error no valide request json")
        return _make_msg_response("No valid json", 400)

    return None


def _make_msg_response(msg, code):
    """
    The function for forming a  response  mesage
    :param msg: str message what must be send
    :param code: status code
    :return: flask Response class
    """
    return make_response(jsonify({"msg": msg}), code)

if __name__ == "__main__":
    consoleHandler = logging.StreamHandler()
    log.addHandler(consoleHandler)
    app.logger.handlers = log.handlers
    app.run(host="0.0.0.0",port=8035)
