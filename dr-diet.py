from allrecipes import AllRecipes as ar
import os, ssl

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
