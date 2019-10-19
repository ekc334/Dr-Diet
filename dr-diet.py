import ssl, os

from bs4 import BeautifulSoup

from boundio import task, run_tasks

import urllib.parse
import urllib.request

import requests

import re

base_url = "https://allrecipes.com/search/results/?"

def parse_catalog_data(soup):
    search_data = []
    articles = soup.findAll("article", {"class": "fixed-recipe-card"})

    iterarticles = iter(articles)
    next(iterarticles)
    for article in iterarticles:
        data = {}
        try:
            data["name"] = article.find("h3", {"class": "fixed-recipe-card__h3"}).get_text().strip(' \t\n\r')
            data["description"] = article.find("div", {"class": "fixed-recipe-card__description"}).get_text().strip(' \t\n\r')
            data["url"] = article.find("a", href=re.compile('^https://www.allrecipes.com/recipe/'))['href']
        except Exception as e2:
            pass
        if data:  # Do not include if no image -> its probably an add or something you do not want in your result
            search_data.append(data)
    return search_data

def parse_recipe_data(soup):
    ingredients = soup.findAll("li", {"class": "checkList__line"})

    data = {
        "ingredients": [],
    }

    for ingredient in ingredients:
        string = ingredient.find("span", {"class": "recipe-ingred_txt"}).get_text()
        if string and string != "Add all ingredients to list":
            data["ingredients"].append(string)

    return data

async def search(query_dict, k):
    url = base_url + urllib.parse.urlencode(query_dict) + "&page="+str(k)

    response = requests.get(url, headers={ 'Cookie':'euConsent=true' })

    soup = BeautifulSoup(response.content, 'html.parser')

    return parse_catalog_data(soup)

async def get_recipe(url):
    response = requests.get(url, headers={ 'Cookie':'euConsent=true' })

    soup = BeautifulSoup(response.content, 'html.parser')
    return parse_recipe_data(soup)


async def allergen_search(allergen, recipe_name):
    query_options = {
        "wt": recipe_name,
        "sort" : "re"
    }
    allergen_count = 0
    for pageNumber in range(1,3):
        query_result = await search(query_options, pageNumber)
        if (pageNumber==1):
            for item in range(16):
                print((16*(pageNumber-1))+item)
                recipe_url = query_result[item]['url']
                detailed_recipe = await get_recipe(recipe_url)
                for ingredient in detailed_recipe['ingredients']:
                    if (ingredient.find(allergen)):
                        allergen_count += 1
        else:
            for item in range(4):
                print((4*(pageNumber-1))+item)
                recipe_url = query_result[item]['url']
                detailed_recipe = await get_recipe(recipe_url)
                for ingredient in detailed_recipe['ingredients']:
                    if (ingredient.find(allergen)):
                        allergen_count += 1

    return allergen_count

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

allergens = 'peanut'
rn = "mashed potatoes"
print(run_tasks(allergen_search(allergens, rn)))
