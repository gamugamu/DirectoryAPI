from flask import Flask
from flask import Response

app = Flask(__name__)
version = "0.0.1"

@app.after_request
def apply_caching(response):
    response.headers["Version"] = version
    return response

@app.route('/')
def home():
    return "home"
