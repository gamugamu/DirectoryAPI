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
    return def home():
        return """<!DOCTYPE html>
                    <html>
                        <head>
                            <title>ApiDirectory</title>
                        </head>
                        <body>
                        HomePage
                        <img src="https://f001.backblazeb2.com/file/project0/Dolan.jpg" alt="Une image de licorne :)" height="80" width="200" />
                        </body>
                        </html>"""
