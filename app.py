import json
import os
import random

import requests
from flask import Flask, make_response, redirect, render_template, request

import cached_backend
import scaler

app = Flask(__name__)

backendBaseUrl = os.getenv('BACKEND_URL', "http://localhost:8081/")
frontendVersion = os.getenv('RENDER_GIT_COMMIT', 'latest')

backendMenuFetcher = cached_backend.CachedBackendCall(
    lambda: requests.get(backendBaseUrl + 'recipes/', timeout=10).json())
backendVersion = cached_backend.CachedBackendCall(
    lambda: requests.get(backendBaseUrl + 'manifest', timeout=10).json()['version'])


def fetchRecipeList():
    return backendMenuFetcher.fetch_data()


def fetchApiVersion():
    return backendVersion.fetch_data()


@app.context_processor
def inject_globals():
    return dict(
        fetchRecipeList=fetchRecipeList,
        fetchApiVersion=fetchApiVersion,
    )


app.config.update(
    frontendVersion=frontendVersion,
)


@app.route("/")
def homepage():
    return render_template('home.html')


@app.route("/manifest.json")
def manifest():
    appInfo = {
        'version': frontendVersion,
        'apiUrl': backendBaseUrl
    }
    response = make_response(json.dumps(appInfo))
    response.headers['Content-Type'] = 'text/json'
    return response


@app.route("/sitemap.xml")
def sitemap():
    if "HEROKU_SLUG_COMMIT" in os.environ:
        base_url = f"https://{request.host}"
    else:
        base_url = request.url_root.rstrip('/')
    return render_template("sitemap.xml", baseUrl=base_url)


@app.errorhandler(404)
def page_not_found(error):
    return make_response(render_template('notfound.html'), 404)


@app.errorhandler(500)
def special_exception_handler(error):
    if app.debug:
        raise error
    return make_response(render_template('internalerror.html'), 500)


@app.route("/random")
def random_recipe():
    return redirect(random.choice(fetchRecipeList())['permalink'], 302)


@app.route("/<name>")
def recipe(name):
    if name.lower() != name:
        return redirect('/' + name.lower(), 301)

    response = requests.get(backendBaseUrl + 'recipes/' + name, timeout=10)

    if response.status_code == 200:
        recipe_data = response.json()

        scale_factor = scaler.get_scale_factor(request.args)
        if scale_factor:
            recipe_data['ingredients_blocks'] = list(map(
                lambda b: dict(
                    name=b['name'],
                    ingredients=list(map(
                        lambda i: scaler.scale_ingredient(i, scale_factor),
                        b['ingredients'],
                    )),
                ),
                recipe_data['ingredients_blocks'],
            ))
        else:
            scale_factor = 1

        formatted_dated_notes = [
            '{}: {}'.format(note['date'], note['note'])
            for note in recipe_data['dated_notes']
        ]
        combined_notes = recipe_data['notes'] + formatted_dated_notes

        return render_template(
            'recipe.html',
            recipe=recipe_data,
            scale_factor=scale_factor,
            combined_notes=combined_notes,
        )
    else:
        return make_response(render_template('notfound.html'), 404)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
