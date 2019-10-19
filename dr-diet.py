import ssl, os

from bs4 import BeautifulSoup

import urllib.parse
import urllib.request

import re


def search(query_dict, k):
	base_url = "https://allrecipes.com/search/results/?"
	query_url = urllib.parse.urlencode(query_dict)

	url = base_url + query_url + "&page="+str(k)

	req = urllib.request.Request(url)
	req.add_header('Cookie', 'euConsent=true')

	html_content = urllib.request.urlopen(req).read()

	soup = BeautifulSoup(html_content, 'html.parser')

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
			try:
				data["image"] = article.find("a", href=re.compile('^https://www.allrecipes.com/recipe/')).find("img")["data-original-src"]
			except Exception as e1:
				pass
			try:
				data["rating"] = float(article.find("div", {"class": "fixed-recipe-card__ratings"}).find("span")["data-ratingstars"])
			except ValueError:
				data["rating"] = None
		except Exception as e2:
			pass
		if data and "image" in data:  # Do not include if no image -> its probably an add or something you do not want in your result
			search_data.append(data)
	return search_data
def get(url):
		req = urllib.request.Request(url)
		req.add_header('Cookie', 'euConsent=true')

		html_content = urllib.request.urlopen(req).read()
		soup = BeautifulSoup(html_content, 'html.parser')

		ingredients = soup.findAll("li", {"class": "checkList__line"})

		data = {
				"ingredients": [],
		}

		for ingredient in ingredients:
			str_ing = ingredient.find("span", {"class": "recipe-ingred_txt"}).get_text()
			if str_ing and str_ing != "Add all ingredients to list":
				data["ingredients"].append(str_ing)

		return data
def allergen_search(allergen, recipe_name):
        query_options = {
                "wt": recipe_name,
                "sort" : "re"
            }
        allergen_count = 0
        for j in range(1,6):
                query_result = search(query_options, j)
                for i in range(16):
                        print((16*j)+i-15)
                        recipe_url = query_result[i]['url']
                        detailed_recipe = get(recipe_url)
                        for ingredient in detailed_recipe['ingredients']:
                                if (ingredient.find(allergen)):
                                        allergen_count += 1

        return allergen_count

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

allergens = 'peanut'
rn = "mashed potatoes"
print(allergen_search(allergens, rn))
