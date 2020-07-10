import web
import os
import requests

urls = (
    '/', 'homepage',
    '/(.*)', 'recipe'
)
app = web.application(urls, globals())
backendBaseUrl = os.getenv('BACKEND_URL', "http://localhost:8081/")

recipeList = requests.get(backendBaseUrl + 'recipes/').json()

templates = web.template.render('templates/', base='layout', globals={'recipeList':recipeList})

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

        response = requests.get(backendBaseUrl + 'recipes/' + name)

        if response.status_code == 200:
            return templates.recipe(response.json())
        else:
            raise web.notfound()

app.notfound = notfound
app.internalerror = internalerror

if __name__ == "__main__":
    app.run()
