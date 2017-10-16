# coding: utf8
import json

from flask import Flask
from flask import Response
from flask import request, url_for
from services import Security
from services import Login
from cloud import CloudService
from helper import Sanityzer

app         = Flask(__name__)
version     = "0.0.1"
version_uri = "/rest/"

# Les données ne sont pas stocké sur le même serveur que l'API.
cloud = CloudService.CloudService()
cloud.connect_to_cloud()

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

@app.route(version_uri + 'logout', methods=['GET'])
def logout():
    securityLvl         = Security.SecurityLevel.LOGGED
    error               = Security.check_if_token_allow_access(request, securityLvl)
    error               = Login.logout(from_error=error, request=request)
    errorDesc           = Security.Error.asDescription(error)

    return json.dumps({"error" : errorDesc.__dict__})


@app.route(version_uri + 'deleteaccount', methods=['GET'])
def delete_account():
    securityLvl         = Security.SecurityLevel.LOGGED
    error               = Security.check_if_token_allow_access(request, securityLvl)
    error               = Login.delete_account(from_error=error, request=request)
    errorDesc           = Security.Error.asDescription(error)

    return json.dumps({"error" : errorDesc.__dict__})

@app.route(version_uri + 'createfile', methods=['POST'])
def create_file():
    securityLvl         = Security.SecurityLevel.LOGGED
    error               = Security.check_if_token_allow_access(request, securityLvl)
    user_id             = Security.user_id_from_request(request)
    error, _file        = cloud.create_file(error, request, user_id)
    errorDesc           = Security.Error.asDescription(error)

    return json.dumps({"error" : errorDesc.__dict__, "filepayload" : _file.__dict__})

@app.route(version_uri + 'deletefile', methods=['POST'])
def delete_file():
    securityLvl         = Security.SecurityLevel.LOGGED
    error               = Security.check_if_token_allow_access(request, securityLvl)
    user_id             = Security.user_id_from_request(request)
    error               = cloud.delete_file(error, request, user_id)
    errorDesc           = Security.Error.asDescription(error)

    return json.dumps({"error" : errorDesc.__dict__})

@app.route(version_uri + 'filesheader', methods=['POST'])
def files_header():
    securityLvl         = Security.SecurityLevel.LOGGED
    error               = Security.check_if_token_allow_access(request, securityLvl)
    user_id             = Security.user_id_from_request(request)
    error, files_header = cloud.get_files_header(error, request, user_id)
    errorDesc           = Security.Error.asDescription(error)
    print "files_header ", files_header
    
    return json.dumps({"error" : errorDesc.__dict__, "filesheader" : files_header})
