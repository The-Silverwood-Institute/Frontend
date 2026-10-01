import json
import os
import random
import re
from pathlib import Path

import requests
from flask import Flask, make_response, redirect, render_template, request

import cached_backend
import contribute
import scaler

app = Flask(__name__)

COMMIT_ENV_KEYS = (
    'SOURCE_COMMIT',
    'GIT_COMMIT',
    'GITHUB_SHA',
)
COMMIT_RE = re.compile(r'^[0-9a-fA-F]{7,40}$')
GIT_COMMIT_FILE = Path(__file__).with_name('GIT_COMMIT')


def resolve_deployed_version(environ=None):
    environ = os.environ if environ is None else environ
    for key in COMMIT_ENV_KEYS:
        value = (environ.get(key) or '').strip()
        if COMMIT_RE.fullmatch(value):
            return value
    try:
        value = GIT_COMMIT_FILE.read_text(encoding='utf-8').strip()
    except OSError:
        return 'latest'
    return value if COMMIT_RE.fullmatch(value) else 'latest'


backendBaseUrl = os.getenv('BACKEND_URL', "http://localhost:8081/")
frontendVersion = resolve_deployed_version()


class BackendUnavailable(Exception):
    pass


def fetch_backend_json(path):
    try:
        response = requests.get(backendBaseUrl + path, timeout=10)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as error:
        raise BackendUnavailable from error


backendMenuFetcher = cached_backend.CachedBackendCall(
    lambda: fetch_backend_json('recipes/'))
backendVersion = cached_backend.CachedBackendCall(
    lambda: fetch_backend_json('manifest')['version'])


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
    return render_template(
        "sitemap.xml",
        baseUrl=request.url_root.rstrip('/'),
    )


@app.errorhandler(404)
def page_not_found(error):
    return make_response(render_template('notfound.html'), 404)


@app.errorhandler(500)
def special_exception_handler(error):
    if app.debug:
        raise error
    return make_response(render_template('internalerror.html'), 500)


@app.errorhandler(BackendUnavailable)
def backend_unavailable(error):
    return make_response(render_template('backendunavailable.html'), 503)


@app.route("/debug")
def debug_page():
    return render_template('debug.html')


@app.route("/random")
def random_recipe():
    return redirect(random.choice(fetchRecipeList())['permalink'], 302)


def render_contribute(form=None, error=None, pr_url=None):
    return render_template(
        'contribute.html',
        recipeUrl='contribute',
        tag_groups=contribute.TAG_GROUPS,
        diet_checkboxes=contribute.DIET_CHECKBOXES,
        form=contribute.page_state(form),
        error=error,
        pr_url=pr_url,
    )


@app.route("/contribute", methods=["GET", "POST"])
def contribute_page():
    if request.method == "GET":
        return render_contribute()

    payload = contribute.submission_payload(request.form)
    try:
        response = requests.post(
            backendBaseUrl + 'recipe-submissions',
            json=payload,
            headers={
                'Authorization': contribute.authorization_header(request.form),
            },
            timeout=30,
        )
    except requests.RequestException:
        return render_contribute(
            request.form,
            error='Could not reach the recipe API. Nothing was submitted.',
        )

    if response.status_code == 200:
        try:
            body = response.json()
        except ValueError:
            body = None
        url = contribute.pull_request_url(body)
        if url is None:
            return render_contribute(
                request.form,
                error='The recipe API did not return a pull request link.',
            )
        return render_contribute(pr_url=url)

    return render_contribute(
        request.form,
        error=contribute.failure_message(response),
    )


@app.route("/<name>")
def recipe(name):
    if name.lower() != name:
        return redirect('/' + name.lower(), 301)

    try:
        response = requests.get(backendBaseUrl + 'recipes/' + name, timeout=10)
        response.raise_for_status()
        recipe_data = response.json()
    except requests.HTTPError as error:
        if error.response is not None and error.response.status_code == 404:
            return make_response(render_template('notfound.html'), 404)
        raise BackendUnavailable from error
    except (requests.RequestException, ValueError) as error:
        raise BackendUnavailable from error

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
        copy_ingredients=scaler.ingredients_copy_text(
            recipe_data['ingredients_blocks']),
    )


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
