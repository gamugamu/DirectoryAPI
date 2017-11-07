# coding: utf8
import json
import markdown

from flask import Flask
from flask import Response
from flask import request, url_for
from flask import render_template
from flask import make_response

from flask import Markup
from flask_bootstrap import Bootstrap
from flask_flatpages import FlatPages, pygments_style_defs

from settings import file
from services import Security
from services import Login
from services.Mail import sendmail
from testAPI import performtest
from cloud import CloudService
from helper import Sanityzer
from jinja2 import Environment

FLATPAGES_AUTO_RELOAD   = True
FLATPAGES_EXTENSION     = '.md'
FLATPAGES_ROOT          = 'content'

app         = Flask(__name__)
Bootstrap(app)
app.config["CACHE_TYPE"]    = "null"
flatpages                   = FlatPages(app)

API_VERSION = "0.0.2"
VERSION_URI = "/rest/" + API_VERSION + "/"

# Les données ne sont pas stocké sur le même serveur que l'API.
cloud = CloudService.CloudService()
cloud.connect_to_cloud()

app.config['DEBUG'] = True

@app.after_request
def apply_caching(response):
    response.headers["Version"]         = API_VERSION
    response.headers['Cache-Control']   = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma']          = 'no-cache'
    response.headers['Expires']         = '0'
    response.headers['Access-Control-Allow-Origin']  = '*'
    response.headers['Access-Control-Allow-Headers'] = 'token-request, Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST'

    return response

@app.route(VERSION_URI)
def home():
    #sendmail("cryptodraco@gmail.com", "test", "bodybody")
    content = file('documentation.md').decode('utf8')
    content = Environment().from_string(content).render()
    md      = markdown.Markdown(content, extensions=['markdown.extensions.toc'])
    md.convert(content)

    toc     = Markup(md.toc)
    content = markdown.markdown(content, extensions=['markdown.extensions.extra', 'markdown.extensions.toc', 'superscript', 'markdown.extensions.nl2br', 'markdown.extensions.fenced_code', 'markdown.extensions.codehilite', 'pymdownx.emoji'])
    content = Markup(content)
    return render_template('index.html', **locals())

@app.route(VERSION_URI + 'testAPI')
def test_api():
    return render_template('testAPI.html')

@app.route('/starttest', methods=['POST'])
def get_counts():
    return performtest(request.url_root, API_VERSION)

@app.route(VERSION_URI + 'testmarkdown')
def test_markdown():
    content = file('testmarkdown.md')
    content = Environment().from_string(content).render().decode('utf-8')
    content = Markup(markdown.markdown(content, extensions=['markdown.extensions.extra', 'markdown.extensions.toc', 'superscript', 'markdown.extensions.nl2br', 'markdown.extensions.fenced_code', 'markdown.extensions.codehilite', 'pymdownx.emoji']))

    return render_template('index.html', **locals())

@app.route(VERSION_URI + 'asktoken')
def askToken():
    securityLvl = Security.SecurityLevel.NONE
    error       = Security.check_if_token_allow_access(request, securityLvl)
    token       = Security.generateToken(error.value == Security.Error.SUCCESS.value, securityLvl, from_request=request)
    errorDesc   = Security.Error.asDescription(error)

    return json.dumps({"token" : token.as_dict(), "error" : errorDesc.__dict__})

@app.route(VERSION_URI + 'createaccount', methods=['POST'])
def createaccount():
    securityLvl = Security.SecurityLevel.UNAUTH
    error       = Security.check_if_token_allow_access(request, securityLvl)
    error       = Login.create_account(from_error=error, request=request)
    errorDesc   = Security.Error.asDescription(error)

    return json.dumps({"error" : errorDesc.__dict__})

@app.route(VERSION_URI + 'login', methods=['POST'])
def login():
    securityLvl         = Security.SecurityLevel.UNAUTH
    error               = Security.check_if_token_allow_access(request, securityLvl)
    error, user, token  = Login.login(from_error=error, request=request)
    errorDesc           = Security.Error.asDescription(error)

    return json.dumps({"error" : errorDesc.__dict__, "user" : Sanityzer.sanityse(user), "token" : token.as_dict()})

@app.route(VERSION_URI + 'logout', methods=['GET'])
def logout():
    securityLvl         = Security.SecurityLevel.LOGGED
    error               = Security.check_if_token_allow_access(request, securityLvl)
    error               = Login.logout(from_error=error, request=request)
    errorDesc           = Security.Error.asDescription(error)

    return json.dumps({"error" : errorDesc.__dict__})


@app.route(VERSION_URI + 'deleteaccount', methods=['GET'])
def delete_account():
    securityLvl         = Security.SecurityLevel.LOGGED
    error               = Security.check_if_token_allow_access(request, securityLvl)
    error               = Login.delete_account(from_error=error, request=request)
    errorDesc           = Security.Error.asDescription(error)

    return json.dumps({"error" : errorDesc.__dict__})

@app.route(VERSION_URI + 'createfile', methods=['POST'])
def create_file():
    securityLvl         = Security.SecurityLevel.LOGGED
    error               = Security.check_if_token_allow_access(request, securityLvl)
    user_id             = Security.user_id_from_request(request)
    error, _file        = cloud.create_file(error, request, user_id)
    errorDesc           = Security.Error.asDescription(error)

    return json.dumps({"error" : errorDesc.__dict__, "filepayload" : _file.__dict__})

@app.route(VERSION_URI + 'deletefile', methods=['POST'])
def delete_file():
    securityLvl         = Security.SecurityLevel.LOGGED
    error               = Security.check_if_token_allow_access(request, securityLvl)
    user_id             = Security.user_id_from_request(request)
    error               = cloud.delete_file(error, request, user_id)
    errorDesc           = Security.Error.asDescription(error)

    return json.dumps({"error" : errorDesc.__dict__})

@app.route(VERSION_URI + 'modifyfile', methods=['POST'])
def modify_file():
    securityLvl             = Security.SecurityLevel.LOGGED
    error                   = Security.check_if_token_allow_access(request, securityLvl)
    user_id                 = Security.user_id_from_request(request)
    error                   = cloud.modify_file(error, request, user_id)
    errorDesc               = Security.Error.asDescription(error)

    return json.dumps({"error" : errorDesc.__dict__})

@app.route(VERSION_URI + 'filesheader', methods=['POST'])
def files_header():
    securityLvl         = Security.SecurityLevel.LOGGED
    error               = Security.check_if_token_allow_access(request, securityLvl)
    user_id             = Security.user_id_from_request(request)
    error, files_header = cloud.get_files_header(error, request, user_id)
    errorDesc           = Security.Error.asDescription(error)

    return json.dumps({"error" : errorDesc.__dict__, "filesheader" : files_header})

@app.route(VERSION_URI + 'filespayload', methods=['POST'])
def files_payload():
    securityLvl             = Security.SecurityLevel.LOGGED
    error                   = Security.check_if_token_allow_access(request, securityLvl)
    user_id                 = Security.user_id_from_request(request)
    error, files_payload    = cloud.get_files_payload(error, request, user_id)
    errorDesc               = Security.Error.asDescription(error)

    return json.dumps({"error" : errorDesc.__dict__, "filesheader" : files_payload})

@app.route(VERSION_URI + 'graph', methods=['POST'])
def graph():
    securityLvl             = Security.SecurityLevel.NONE
    error                   = Security.check_if_token_allow_access(request, securityLvl)
    user_id                 = Security.user_id_from_request(request)
    error, graph            = cloud.graph(error, request, user_id)
    errorDesc               = Security.Error.asDescription(error)

    return json.dumps({"error" : errorDesc.__dict__, "graph" : graph})
