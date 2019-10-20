from app import app
from flask import render_template, request
from app.allergen_count import allergen_search
import asyncio
# from app import , formopener

@app.route('/')
@app.route('/index')
def index():
    allergens = request.args.get('dishName')
    rn = "grilled cheese sandwich"
    loop = asyncio.new_event_loop()
    return str(loop.run_until_complete(allergen_search(allergens, rn)))
