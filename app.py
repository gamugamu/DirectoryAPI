# coding: utf8
import json
from flask import Flask
from flask import Response
from flask import request, url_for
from services import Security

import json

app         = Flask(__name__)
version     = "0.0.1"
version_uri = "/rest/"

@app.after_request
def apply_caching(response):
    response.headers["Version"] = version
    return response

@app.route('/')
def home():
    return "ApiDrectory v0.0.1"

@app.route(version_uri + 'asktoken')
def askToken():
    securityLvl = Security.SecurityLevel.NONE
    error       = Security.check_if_token_allow_access(request, securityLvl)
    token       = Security.generateToken(error.value == Security.Error.SUCCESS.value, securityLvl)
    errorDesc   = Security.Error.asDescription(error)
    print token.as_dict()

    return json.dumps({"token" : token.as_dict(), "error" : errorDesc.__dict__})

@app.route(version_uri + 'createaccount')
def createaccount():
    securityLvl = Security.SecurityLevel.UNAUTH
    error       = Security.check_if_token_allow_access(request, securityLvl)
    errorDesc   = Security.Error.asDescription(error)

    print errorDesc.__dict__

    return json.dumps({"error" : errorDesc.__dict__})
