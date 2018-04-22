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
def internalerror():
    return web.internalerror(templates.internalerror())

app.notfound = notfound
if not web.config.debug:
    app.internalerror = internalerror

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
            recipe.notes = toList(recipe.notes)
            recipe.ingredients = toList(recipe.ingredients)
            recipe.method = toList(recipe.method)
            print recipe.description
            return templates.recipe(recipe)
        else:
            raise web.notfound()

if __name__ == "__main__":
    app.run()
