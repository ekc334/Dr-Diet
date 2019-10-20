from flask import Flask

app = Flask(__name__)

def add_cors_header(resp):
    resp.headers.add('Access-Control-Allow-Origin', '*')
    return resp

app.after_request(add_cors_header)

from app import routes

