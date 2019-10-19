from app import app
from flask import render_template, request
# from app import , formopener

@app.route('/')
@app.route('/index')
def index():
    return render_template ("index.html")
