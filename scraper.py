import requests
import json

'''
Dumps the entire recipe list as a JSON list.
Useful for parity checking between releases or for data science work
'''

base_url = "https://api.reciba.se/recipes/"

recipe_list = requests.get(base_url).json()

recipes = []

for recipe_entry in recipe_list:
    recipe_url = base_url + recipe_entry['permalink']

    recipes.append(requests.get(recipe_url).json())

with open('recipes.json', 'w') as file:
    json.dump(recipes, file)
