#!env/bin/python
# -*- coding: utf-8 -*-
import logging
from flask import Flask
from flask import jsonify
from flask import abort 
from flask import make_response  
from flask import request  

from keystoneauth1 import loading
from keystoneauth1 import session
from keystoneauth1.exceptions.http import Unauthorized

from functools import wraps

logging.basicConfig(filename="/var/log/api-gateway/api.log", level=logging.INFO)
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.logger.setLevel(logging.INFO)

app.logger.handlers=logging.getLogger("api-gateway").handlers 

OK_RESPONSE = {"msg": "OK"}

@app.before_request
def clear_response():
    if "data" in OK_RESPONSE:
        OK_RESPONSE.pop("data")

def authenticate(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        request_auth = request.authorization
        if not request_auth:
            return make_response(jsonify({"msg":"No auth credentials"} ),401)
        loader = loading.get_plugin_loader('password')
        auth = loader.load_from_options(auth_url="http://localhost/identity",
                username=request_auth.username,password=request_auth.password,
                user_domain_id="default")
        sess = session.Session(auth=auth)
        try:
             return func(sess,*args, **kwargs)
        except Unauthorized as e:
            app.logger.info(f"Deny access  user {request_auth.username} exception {e}")
            return make_response(jsonify({"msg":"Acssess deny"} ),401)
    return decorated

@app.route("/networks",methods=["GET"])
@authenticate
def get_networks(session = None):
    return jsonify(OK_RESPONSE)

if __name__=="__main__":
    app.logger.setLevel(logging.DEBUG)
    consoleHandler = logging.StreamHandler()
    app.logger.addHandler(consoleHandler)
    app.run()


