# coding: utf8
import json
from flask import Flask
from flask import Response
from flask import request, url_for
from services import Security

import json

app = Flask(__name__)
version = "0.0.1"

@app.after_request
def apply_caching(response):
    response.headers["Version"] = version
    return response

@app.route('/')
def home():
    return ""

@app.route('/rest/asktoken')
def askToken():
    securityLvl = Security.SecurityLevel.UNAUTH
    error       = Security.check_if_token_allow_access(request, securityLvl)

    token       = Security.generateToken(error.value == Security.Error.SUCCESS.value, securityLvl)
    errorDesc   = Security.Error.asDescription(error)

    #data  = request.form
    #print data["tokenRequest"]
    return json.dumps({"token" : token.__dict__, "error" : errorDesc.__dict__})
