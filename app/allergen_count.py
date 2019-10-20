import ssl, os
import asyncio
from bs4 import BeautifulSoup
from boundio import run_tasks
import urllib.parse
import urllib.request
import aiohttp
import requests
import re
from flask import Flask


base_url = "https://allrecipes.com/search/results/?"
find_recipe_url = re.compile('^https://www.allrecipes.com/recipe/')
MINIMUM_RESULT_SIZE = 30

def parse_catalog_data(soup):
    search_data = []
    articles = soup.findAll("article", {"class": "fixed-recipe-card"})

    iterarticles = iter(articles)
    next(iterarticles)
    for article in iterarticles:
        search_data.append({
            "name": article.find("h3", {"class": "fixed-recipe-card__h3"}).get_text(),
            "description": article.find("div", {"class": "fixed-recipe-card__description"}).get_text().strip(),
            "url": article.find("a", href=find_recipe_url)['href']
        })
    return search_data

def parse_recipe_data(soup):
    ingredients = soup.findAll("span", {"class": "recipe-ingred_txt"})
    ingredients += soup.findAll("span", {"class": "ingredients-item-name"})
    ingredients = [i.get_text() for i in ingredients]
    return [i for i in ingredients if i and i != "Add all ingredients to list"]

async def search(session, query_dict, k):
    url = base_url + urllib.parse.urlencode(query_dict) + "&page="+str(k)
    async with session.get(url, headers = { 'Cookie':'euConsent=true' }) as resp:
        text = await resp.text()
    soup = BeautifulSoup(text, 'html.parser')
    return parse_catalog_data(soup)

async def get_recipe(session, url):
    url_shortened = url.replace('https://www.allrecipes.com/recipe/','')
    # print(f"get_recipe url is: {url_shortened}")
    async with session.get(url, headers = { 'Cookie':'euConsent=true' }) as resp:
        soup = BeautifulSoup(await resp.text(), 'html.parser')
        return parse_recipe_data(soup)

async def _allergen_search(allergen, recipe_name):
    print("Allergen search called")
    query_options = { "wt": recipe_name, "sort" : "re" }

    async with aiohttp.ClientSession() as session:
        searches = [search(session, query_options, n) for n in range(1, 2)]
        results = [i for sublist in await asyncio.gather(*searches) for i in sublist]
        recipe_searches = [get_recipe(session, result['url']) for result in results]

        recipes, pending = await asyncio.wait(recipe_searches, return_when=asyncio.FIRST_COMPLETED)

        while pending and len(recipes) < MINIMUM_RESULT_SIZE:
            cur_done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
            recipes |= cur_done

        total_count = len(recipes)
        allergen_count = 0

        for recipe in recipes:
            for ingredient in recipe:
                if allergen.lower() in ingredient.lower():
                     break
            else:
                allergen_count += 1

    print("allergen count is", allergen_count)
    retval = int(allergen_count/total_count*100)
    return retval

def allergen_search(allergen, recipe_name):
    if allergen is None or recipe_name is None:
        return ""
    try:
        loop = asyncio.get_event_loop()
    except:
        loop = asyncio.new_event_loop()

    return loop.run_until_complete(_allergen_search(allergen, recipe_name))

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context
