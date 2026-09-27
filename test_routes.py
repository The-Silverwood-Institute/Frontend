import json

import requests
from unittest.mock import MagicMock, patch

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


def test_resolve_deployed_version_prefers_source_commit():
    assert app.resolve_deployed_version({
        'SOURCE_COMMIT': 'abcdef1234567890',
        'GIT_COMMIT': 'deadbeef',
    }) == 'abcdef1234567890'


def test_resolve_deployed_version_ignores_head_and_latest():
    assert app.resolve_deployed_version({
        'SOURCE_COMMIT': 'HEAD',
        'GIT_COMMIT': 'latest',
        'GITHUB_SHA': 'cafeba6',
    }) == 'cafeba6'


def test_resolve_deployed_version_falls_back_to_latest():
    assert app.resolve_deployed_version({}) == 'latest'


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


def test_contribute_page(client):
    response = client.get('/contribute')
    assert response.status_code == 200
    body = response.data.decode()
    assert 'Add a recipe' in body
    assert 'name="passcode"' in body
    assert 'value="VegetarianIsh"' in body
    assert 'value="NeverEaten"' not in body
    assert 'value="Popular"' not in body
    assert 'value="New"' not in body
    assert 'mdl-navigation__link add-recipe is-current' in body


def test_contribute_link_in_drawer(client):
    response = client.get('/')
    body = response.data.decode()
    assert 'href="/contribute"' in body
    assert 'add-recipe is-current' not in body


def test_contribute_submits_recipe(client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'url': 'https://github.com/The-Silverwood-Institute/Recibase/pull/12',
    }
    with patch('app.requests.post', return_value=mock_response) as post:
        response = client.post('/contribute', data={
            'passcode': ' secret ',
            'name': ' Chilli con Carne ',
            'source': "Kit's Dad",
            'description': ' Weeknight ',
            'notes': 'Rest overnight\n\n',
            'tags': ['Spicy', 'Scales'],
            'ingredient_name': ['Mince', '  ', 'Garlic'],
            'ingredient_quantity': ['500g', '', ''],
            'ingredient_prep': ['', '', 'crushed'],
            'ingredient_notes': ['', '', ''],
            'method': 'Brown the mince.\n\nServe.',
        })
    assert response.status_code == 200
    body = response.data.decode()
    assert 'https://github.com/The-Silverwood-Institute/Recibase/pull/12' in body
    assert 'name="passcode"' not in body
    assert post.call_args.args[0].endswith('recipe-submissions')
    assert post.call_args.kwargs['timeout'] == 30
    assert post.call_args.kwargs['json'] == {
        'passcode': 'secret',
        'name': 'Chilli con Carne',
        'source': "Kit's Dad",
        'description': 'Weeknight',
        'notes': ['Rest overnight'],
        'tags': ['Spicy', 'Scales'],
        'ingredients': [
            {
                'name': 'Mince',
                'quantity': '500g',
                'prep': None,
                'notes': None,
            },
            {
                'name': 'Garlic',
                'quantity': None,
                'prep': 'crushed',
                'notes': None,
            },
        ],
        'method': ['Brown the mince.', 'Serve.'],
    }


def test_contribute_keeps_form_on_api_error(client):
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.headers = {'Content-Type': 'text/plain'}
    mock_response.text = 'invalid passcode'
    mock_response.json.side_effect = ValueError('not json')
    with patch('app.requests.post', return_value=mock_response):
        response = client.post('/contribute', data={
            'passcode': 'nope',
            'name': 'Soup',
            'source': '',
            'description': '',
            'notes': '',
            'tags': ['Spicy'],
            'ingredient_name': ['Onion'],
            'ingredient_quantity': ['1'],
            'ingredient_prep': [''],
            'ingredient_notes': ['Optional'],
            'method': 'Simmer.',
        })
    assert response.status_code == 200
    body = response.data.decode()
    assert 'invalid passcode' in body
    assert 'value="Soup"' in body
    assert 'value="Onion"' in body
    assert 'value="Optional"' in body
    assert 'value="Spicy" checked' in body
    assert 'Pull request opened' not in body


def test_contribute_shows_json_error(client):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.headers = {'Content-Type': 'application/json'}
    mock_response.text = '{"error": "Add at least one ingredient."}'
    mock_response.json.return_value = {'error': 'Add at least one ingredient.'}
    with patch('app.requests.post', return_value=mock_response):
        response = client.post('/contribute', data={
            'passcode': 'secret',
            'name': 'Empty',
            'method': 'Stir.',
        })
    assert response.status_code == 200
    assert 'Add at least one ingredient.' in response.data.decode()


def test_contribute_rejects_unexpected_pull_request_url(client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'url': 'javascript:alert(1)'}
    with patch('app.requests.post', return_value=mock_response):
        response = client.post('/contribute', data={
            'passcode': 'secret',
            'name': 'Soup',
            'ingredient_name': ['Onion'],
            'ingredient_quantity': ['1'],
            'ingredient_prep': [''],
            'ingredient_notes': [''],
            'method': 'Simmer.',
        })
    body = response.data.decode()
    assert 'javascript:alert(1)' not in body
    assert 'did not return a pull request link' in body
    assert 'value="Soup"' in body


def test_contribute_escapes_redisplayed_values(client):
    mock_response = MagicMock()
    mock_response.status_code = 502
    mock_response.headers = {'Content-Type': 'text/plain'}
    mock_response.text = 'upstream failed'
    mock_response.json.side_effect = ValueError('not json')
    with patch('app.requests.post', return_value=mock_response):
        response = client.post('/contribute', data={
            'passcode': 'secret',
            'name': '<script>alert(1)</script>',
            'ingredient_name': ['Onion'],
            'ingredient_quantity': ['1'],
            'ingredient_prep': [''],
            'ingredient_notes': [''],
            'method': 'Simmer.',
        })
    body = response.data.decode()
    assert '<script>alert(1)</script>' not in body
    assert '&lt;script&gt;alert(1)&lt;/script&gt;' in body
    assert 'upstream failed' in body


def test_contribute_reports_unreachable_api(client):
    with patch('app.requests.post', side_effect=requests.ConnectionError('down')):
        response = client.post('/contribute', data={
            'passcode': 'secret',
            'name': 'Soup',
            'method': 'Simmer.',
        })
    assert response.status_code == 200
    body = response.data.decode()
    assert 'Could not reach the recipe API' in body
    assert 'value="Soup"' in body
    assert 'Backend Unavailable' not in body


def test_recipe_copy_ingredients_are_premerged(client):
    response = client.get('/test-recipe')
    assert response.status_code == 200
    body = response.data.decode()
    assert 'x-quantity' not in body
    assert 'x-ingredient' not in body
    assert 'data-ingredients=' in body
    assert '200g Butter' in body
    assert '2 Onion' in body
