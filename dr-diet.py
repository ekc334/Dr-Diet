import ssl, os
import asyncio

from bs4 import BeautifulSoup

from boundio import run_tasks

import urllib.parse
import urllib.request
import aiohttp

import requests

import re

base_url = "https://allrecipes.com/search/results/?"

def parse_catalog_data(soup):
    search_data = []
    articles = soup.findAll("article", {"class": "fixed-recipe-card"})

    iterarticles = iter(articles)
    try:
        next(iterarticles)
    except:
        return
    for article in iterarticles:
        data = {}
        try:
            data["name"] = article.find("h3", {"class": "fixed-recipe-card__h3"}).get_text()
            data["description"] = article.find("div", {"class": "fixed-recipe-card__description"}).get_text().strip(' \t\n\r')

            data["url"] = article.find("a", href=re.compile('^https://www.allrecipes.com/recipe/'))['href']
        except Exception as e2:
            pass
        if data:  # Do not include if no image -> its probably an add or something you do not want in your result
            search_data.append(data)
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
    print(f"get_recipe url is: {url}")
    async with session.get(url, headers = { 'Cookie':'euConsent=true' }) as resp:
        url_escaped = url.replace("\\", '').replace("/", '').replace(':', '')
        text = await resp.text()
        with open(f'data/{url_escaped}.html', 'w') as f:
            f.write(text.replace('\\n', '\n'))

        soup = BeautifulSoup(text, 'html.parser')
        return parse_recipe_data(soup)


async def allergen_search(allergen, recipe_name):
    query_options = {
        "wt": recipe_name,
        "sort" : "re"
    }
    allergen_count = 0
    total_count = 0
    async with aiohttp.ClientSession() as session:
        searches = []
        for n in range(1, 5):
            searches.append(search(session, query_options, n))

        results = []
        for result in await asyncio.gather(*searches):
            results += result

        recipe_searches = [get_recipe(session, result['url']) for result in results]
        recipes = await asyncio.gather(*recipe_searches)

        for detailed_recipe in recipes:
            present = False
            total_count += 1
            if detailed_recipe:
                for ingredient in detailed_recipe:
                     present = present or allergen in ingredient
                if(present):
                    print(f"ITEM NO.: {total_count}")
                    allergen_count += 1
                    print(f"ALLERGEN COUNT: {allergen_count}")
    print("allergen count is", allergen_count)
    retval = allergen_count/total_count
    return retval

async def print_async(boi):
    print(await boi)

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

allergens = 'cheese'
rn = "grilled cheese sandwich"

print(run_tasks(print_async(allergen_search(allergens, rn))))
