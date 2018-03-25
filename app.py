import web
import os.path
from helpers import *

if not os.path.isfile('recipes.db'):
    raise ValueError('Recipes database (recipes.db) not found')

urls = (
    '/(.*)', 'recipe'
)
app = web.application(urls, globals())

db = web.database(dbn='sqlite', db='recipes.db')
recipeList = listRecipes(db)
templates = web.template.render('templates')

class recipe:
    def GET(self, name):
        if name.lower() != name:
            return web.redirect(name.lower())

        vars = {'url':name}

        recipe = db.select('recipes', where="url = $url", vars=vars).first()

        if recipe:
            recipe.ingredients = filter(notEmpty, recipe.ingredients.split("\n"))
            recipe.method = filter(notEmpty, recipe.method.split("\n"))

            return templates.recipe(recipe, recipeList)
        else:
            return web.notfound()

if __name__ == "__main__":
    app.run()
