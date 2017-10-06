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
    Security.check_if_token_allow_access(request, SecurityLevel.UNAUTH)
    #data  = request.form
    #print data["tokenRequest"]
    return ""
