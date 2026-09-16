import json

import requests
from unittest.mock import patch

import app


def test_homepage(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Recibase' in response.data


def test_manifest(client):
    response = client.get('/manifest.json')
    assert response.status_code == 200
    assert response.content_type == 'text/json'
    assert json.loads(response.data) == {
        'version': 'latest',
        'apiUrl': 'http://localhost:8081/',
    }


def test_sitemap(client):
    response = client.get('/sitemap.xml')
    assert response.status_code == 200
    body = response.data.decode()
    assert '<urlset' in body
    assert 'test-recipe' in body


def test_random_recipe_redirects(client):
    response = client.get('/random')
    assert response.status_code == 302
    assert response.location.endswith('test-recipe')


def test_recipe_page(client):
    response = client.get('/test-recipe')
    assert response.status_code == 200
    assert b'Test Recipe' in response.data
    assert b'Chop onion' in response.data


def test_recipe_lowercase_redirect(client):
    response = client.get('/Test-Recipe')
    assert response.status_code == 301
    assert response.location.endswith('/test-recipe')


def test_recipe_not_found(client):
    response = client.get('/missing-recipe')
    assert response.status_code == 404
    assert b'404' in response.data


def test_recipe_scaling(client):
    response = client.get('/test-recipe?scale=2')
    assert response.status_code == 200
    assert b'4' in response.data


def test_homepage_backend_unavailable(flask_app, client):
    flask_app.config['PROPAGATE_EXCEPTIONS'] = False
    try:
        with patch('app.fetchRecipeList', side_effect=app.BackendUnavailable):
            response = client.get('/')
    finally:
        flask_app.config['PROPAGATE_EXCEPTIONS'] = True
    assert response.status_code == 503
    assert b'Backend Unavailable' in response.data


def test_recipe_backend_unavailable(flask_app, client):
    flask_app.config['PROPAGATE_EXCEPTIONS'] = False
    try:
        with patch('app.requests.get', side_effect=requests.ConnectionError('down')):
            response = client.get('/test-recipe')
    finally:
        flask_app.config['PROPAGATE_EXCEPTIONS'] = True
    assert response.status_code == 503
    assert b'Backend Unavailable' in response.data


def test_recipe_copy_ingredients_are_premerged(client):
    response = client.get('/test-recipe')
    assert response.status_code == 200
    body = response.data.decode()
    assert 'x-quantity' not in body
    assert 'x-ingredient' not in body
    assert 'data-ingredients=' in body
    assert '200g Butter' in body
    assert '2 Onion' in body
