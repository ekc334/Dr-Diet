class AllRecipes(object):

	@staticmethod
	def search(query_dict):
		"""
		Search recipes parsing the returned html data.
		"""
		base_url = "https://allrecipes.com/search/results/?"
		query_url = urllib.parse.urlencode(query_dict)

		url = base_url + query_url

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
    
def allergen_search(allergen, recipe_name):
    query_options = {
        "wt": recipe_name,
        "sort" : "re"
    }
    allergen_count = 0
    query_result = ar.search(query_options)
    for i in range(100):
        recipe_url = query_result[i]['url']
        detailed_recipe = ar.get(recipe_url)
        for ingredient in detailed_recipe['ingredients']:
            print(ingredient)
            if (ingredient.find(allergen)):
                allergen_count += 1

    return allergen_count/100

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

allergens = 'peanut'
rn = "grilled cheese"
print(allergen_search(allergens, rn))
