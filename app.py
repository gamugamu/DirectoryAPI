# coding: utf8
import json

from flask import Flask
from flask import Response
from flask import request, url_for
from services import Security
from services import Login
from helper import Sanityzer

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
    token       = Security.generateToken(error.value == Security.Error.SUCCESS.value, securityLvl, from_request=request)
    errorDesc   = Security.Error.asDescription(error)

    return json.dumps({"token" : token.as_dict(), "error" : errorDesc.__dict__})

@app.route(version_uri + 'createaccount', methods=['POST'])
def createaccount():
    securityLvl = Security.SecurityLevel.UNAUTH
    error       = Security.check_if_token_allow_access(request, securityLvl)
    error       = Login.create_account(from_error=error, request=request)
    errorDesc   = Security.Error.asDescription(error)

    return json.dumps({"error" : errorDesc.__dict__})

@app.route(version_uri + 'login', methods=['POST'])
def login():
    securityLvl         = Security.SecurityLevel.UNAUTH
    error               = Security.check_if_token_allow_access(request, securityLvl)
    error, user, token  = Login.login(from_error=error, request=request)
    errorDesc           = Security.Error.asDescription(error)

    return json.dumps({"error" : errorDesc.__dict__, "user" : Sanityzer.sanityse(user), "token" : token.as_dict()})
