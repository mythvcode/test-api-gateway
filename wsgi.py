#!env/bin/python
# -*- coding: utf-8 -*-

"""
api wsgi gateway to openstack

"""
import logging
import os
from functools import wraps
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

from appmods.opensnet import get_networks
from appmods.opensimage import get_images
from appmods.opensserver import get_flavors
from appmods.opensserver import get_servers
from appmods.opensserver import create_server
from appmods.opensserver import manage_server

logging.basicConfig(filename="/var/log/api-gateway/api.log", level=logging.INFO)
app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
# Печатать json с отступами
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

log = logging.getLogger("api-gateway")
if os.environ.get("INDOCKER"):
    consoleHandler = logging.StreamHandler()
    log.addHandler(consoleHandler)

KEYSTONE_HOST = os.environ.get("KEYSTONEHOST")
if not KEYSTONE_HOST:
    KEYSTONE_HOST = "localhost"

app.logger.handlers = log.handlers
OK_RESPONSE = {"msg": "OK"}


@app.before_request
def clear_response():
    """
    The function removes the "data" key from OK_RESPONSE dict,
    what was created on previous requests.
    """
    if "data" in OK_RESPONSE:
        OK_RESPONSE.pop("data")


def authenticate(func):
    """
    Decorator to authenticate api method call.
    catches the Unauthorized, DiscoveryFailure, ConnectFailure  exceptions from the called function.
    :param func: decorating function
    :return decorated: decorated function
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        request_auth = request.authorization
        if not request_auth:
            return make_response(jsonify({"msg": "No auth credentials"}), 401)
        loader = loading.get_plugin_loader('password')
        auth = loader.load_from_options(auth_url=f"http://{KEYSTONE_HOST}/identity",
                                        username=request_auth.username,
                                        password=request_auth.password,
                                        user_domain_id="default")
        sess = session.Session(auth=auth)
        try:
            return func(sess, *args, **kwargs)
        except Unauthorized as excp:
            log.info("Deny access  user %s exception %s", request_auth.username, excp)
            return make_response(jsonify({"msg": "Acssess deny"}), 401)
        except DiscoveryFailure as excp:
            log.error("Cannot connect to keystone err %s", excp)
            return make_response(jsonify({"msg": "No connection to keystone"}), 500)
        except ConnectFailure as excp:
            log.error("Cannot connect to endpoint %s", excp)
            return make_response(jsonify({"msg": f"Cannot connect to endpoint {excp}"}), 500)
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
    # Поиск функции сделан так из-за R0912
    lookup_func = {
            "networks": get_networks,
            "images": get_images,
            "flavors": get_flavors,
            "servers": get_servers
            }
    try:
        func = lookup_func[get_req]
    except KeyError:
        log.info("Route /%s not faund", get_req)
        return make_response(jsonify({"msg": "URL Not found"}), 404)

    if request.args and "id" in request.args:
        OK_RESPONSE["data"] = func(sess, request.args["id"])
    else:
        OK_RESPONSE["data"] = func(sess)

    if not OK_RESPONSE["data"]:
        return make_response(jsonify({"msg": "Data not found"}), 404)
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
        return make_response(jsonify({"msg": "Empty request data"}), 400)
    if not request.is_json:
        return make_response(jsonify({"msg": "Allowed only json"}), 400)
    try:

        OK_RESPONSE["data"] = create_server(sess, request.json)

    except BadRequest as excp:
        log.error("Bad request %s", excp)
        return make_response(jsonify({"msg": f"Error create server {excp}"}), 400)

    except WZBadRequest:
        log.error("Error no valide request json")
        return make_response(jsonify({"msg": "No valid json"}), 400)

    return jsonify(OK_RESPONSE), 201


@app.route("/manage_server", methods=["POST"])
@authenticate
def manage_serv(sess):
    """
    Function for manage servers
    If sucsess action return OK_RESPONSE
    :param sess: keystone session
    :return: flask response json with  with status of request
    """
    if not request.data:
        return  make_response(jsonify({"msg": "Empty request data"}), 400)

    try:
        manage_server(sess, request.json)
    except WZBadRequest:
        log.error("Error no valide request json")
        return make_response(jsonify({"msg": "No valid json"}), 400)
    except BadRequest as excp:
        log.error("Bad request %s", excp)
        return make_response(jsonify({"msg": f"Error '{excp}'"}), 400)
    except Conflict as excp:
        log.warning("Conflict manage server %s", excp)
        return make_response(jsonify({"msg": f"Conflict '{excp}'"}), 409)
    except NotFound:
        return make_response(jsonify({"msg": f"server with id '{request.json['id']}'"
                                             " not found"}), 404)

    return jsonify(OK_RESPONSE), 202


if __name__ == "__main__":
    consoleHandler = logging.StreamHandler()
    log.addHandler(consoleHandler)
    app.logger.handlers = log.handlers
    app.run()
