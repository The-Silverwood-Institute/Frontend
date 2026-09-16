import copy

import pytest
import requests
from unittest.mock import MagicMock, patch

SAMPLE_RECIPES = [
    {'permalink': 'test-recipe', 'name': 'Test Recipe'},
]

SAMPLE_RECIPE = {
    'name': 'Test Recipe',
    'description': 'A test recipe',
    'permalink': 'test-recipe',
    'tagline': 'Tasty',
    'image': None,
    'edit': 'https://github.com/example/edit',
    'ingredients_blocks': [{
        'name': 'Sauce',
        'ingredients': [{
            'name': 'Onion',
            'quantity': '2',
            'prep': 'chopped',
            'notes': None,
        }, {
            'name': 'Butter',
            'quantity': '50g',
            'prep': None,
            'notes': None,
        }],
    }, {
        'name': 'Finish',
        'ingredients': [{
            'name': 'butter',
            'quantity': '150g',
            'prep': None,
            'notes': None,
        }],
    }],
    'method': ['Chop onion', 'Eat'],
    'notes': [],
    'dated_notes': [],
    'tags': [],
    'source': None,
}


def _http_error(response):
    error = requests.HTTPError(response=response)
    error.response = response
    return error


def _mock_requests_get(url, **kwargs):
    response = MagicMock()
    response.status_code = 200
    if url.endswith('recipes/'):
        response.json.return_value = SAMPLE_RECIPES
    elif url.endswith('manifest'):
        response.json.return_value = {'version': 'deadbeef'}
    elif url.endswith('recipes/test-recipe'):
        response.json.return_value = copy.deepcopy(SAMPLE_RECIPE)
    elif url.endswith('recipes/missing-recipe'):
        response.status_code = 404
        response.raise_for_status.side_effect = _http_error(response)
    else:
        response.status_code = 404
        response.raise_for_status.side_effect = _http_error(response)
    return response


@pytest.fixture(scope='session')
def flask_app():
    with patch('requests.get', side_effect=_mock_requests_get):
        import importlib
        import app as app_module
        importlib.reload(app_module)
        app_module.app.config['TESTING'] = True
        yield app_module.app


@pytest.fixture
def client(flask_app):
    return flask_app.test_client()
