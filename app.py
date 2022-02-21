import web
import os
import json
import random
import requests
import scaler

class AppWithHerokuRedirect(web.application):
    # Based on:
    # https://github.com/tylerwilliams/visualizer2/blob/9615392efce05f9cafab32629acd9561e4dbc45c/server/visualizer_server.py#L200
    def handle(self):
        if web.ctx.host == "recibase.herokuapp.com":
            print('Redirecting naked Heroku domain')
            web.ctx.status = "301 Moved Permanently"
            web.ctx.headers.append(('Location', 'https://reciba.se' + web.ctx.fullpath))
            return None
        else:
            return web.application.handle(self)

urls = (
    '/', 'homepage',
    '/sitemap.xml', 'sitemap',
    '/manifest.json', 'manifest',
    '/random', 'randomRecipe',
    '/(.*)', 'recipe'
)
app = AppWithHerokuRedirect(urls, globals())
backendBaseUrl = os.getenv('BACKEND_URL', "http://localhost:8081/")
frontendVersion = os.getenv('HEROKU_SLUG_COMMIT', 'latest')

globals = {
    'recipeList': requests.get(backendBaseUrl + 'recipes/').json(),
    'frontendVersion': frontendVersion,
    'apiVersion': requests.get(backendBaseUrl + 'manifest').json()['version']
}
templates = web.template.render('templates/', base='layout', globals=globals)
plainTemplates = web.template.render('templates/', globals=globals)

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

class randomRecipe:
    def GET(self):
        return web.found(random.choice(globals['recipeList'])['permalink'])

class recipe:
    def GET(self, name):
        if name.lower() != name:
            return web.redirect(name.lower())

        response = requests.get(backendBaseUrl + 'recipes/' + name)

        if response.status_code == 200:
            recipe = response.json()

            scale_factor = scaler.get_scale_factor(web.input())
            if scale_factor:
                recipe['ingredients'] = list(map(lambda i: scaler.scale_ingredient(i, scale_factor), recipe['ingredients']))

            return templates.recipe(recipe)
        else:
            raise web.notfound()

class sitemap:
    def GET(self):
        # Force HTTPS if running in Heroku
        # https://github.com/The-Silverwood-Institute/Frontend/issues/9#issuecomment-660707019
        protocol = "https" if "HEROKU_SLUG_COMMIT" in os.environ else web.ctx.protocol
        appUrl = protocol + "://" + web.ctx.host
        return plainTemplates.sitemap(appUrl)

class manifest:
    def GET(self):
        appInfo = {
            'version': frontendVersion,
            'apiUrl': backendBaseUrl
        }

        web.header('Content-Type', 'text/json')
        return json.dumps(appInfo)

if __name__ == "__main__":
    app.run()
