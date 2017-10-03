from flask import Flask
from flask import Response

app = Flask(__name__)
version = "0.0.1"

@app.route('/')
def home():
    resp = Response("")
    resp.headers['Version'] = version
    return resp
