import web
import os.path
from helpers import *

if not os.path.isfile('recipes.db'):
    raise ValueError('Recipes database (recipes.db) not found')

urls = (
    '/', 'homepage',
    '/(.*)', 'recipe'
)
app = web.application(urls, globals())

db = web.database(dbn='sqlite', db='recipes.db')
templates = web.template.render('templates/', base='layout', globals={'recipeList':listRecipes(db)})

def notfound():
    return web.notfound(templates.notfound())
app.notfound = notfound

class homepage:
    def GET(self):
        return templates.home()

class recipe:
    def GET(self, name):
        if name.lower() != name:
            return web.redirect(name.lower())

        vars = {'url':name}

        recipe = db.select('recipes', where="url = $url", vars=vars).first()

        if recipe:
            recipe.ingredients = filter(notEmpty, recipe.ingredients.split("\n"))
            recipe.method = filter(notEmpty, recipe.method.split("\n"))

            return templates.recipe(recipe)
        else:
            raise web.notfound()

if __name__ == "__main__":
    app.run()
