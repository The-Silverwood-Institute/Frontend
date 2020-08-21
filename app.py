import web
import os
import json
import requests

class DerpApplication(web.application):
    def handle(self):
        print(web.ctx.host)
        return web.application.handle(self)

urls = (
    '/', 'homepage',
    '/sitemap.xml', 'sitemap',
    '/manifest.json', 'manifest',
    '/(.*)', 'recipe'
)
app = DerpApplication(urls, globals())
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

class recipe:
    def GET(self, name):
        if name.lower() != name:
            return web.redirect(name.lower())

        response = requests.get(backendBaseUrl + 'recipes/' + name)

        if response.status_code == 200:
            return templates.recipe(response.json())
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

app.notfound = notfound
app.internalerror = internalerror

if __name__ == "__main__":
    app.run()
