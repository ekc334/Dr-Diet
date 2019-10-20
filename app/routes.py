from app import app
from flask import render_template, request
from app.allergen_count import allergen_search
# from app import , formopener

@app.route('/')
@app.route('/index')
def index():
    return str(allergen_search(
        request.args.get('allergenName'), request.args.get('dishName')
    ))
