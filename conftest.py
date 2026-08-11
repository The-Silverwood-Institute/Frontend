import pytest
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
        'name': None,
        'ingredients': [{
            'name': 'Onion',
            'quantity': '2',
            'prep': 'chopped',
            'notes': None,
        }, {
            'name': 'Salt',
            'quantity': None,
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


def _mock_requests_get(url, **kwargs):
    response = MagicMock()
    if url.endswith('recipes/'):
        response.json.return_value = SAMPLE_RECIPES
    elif url.endswith('manifest'):
        response.json.return_value = {'version': 'deadbeef'}
    elif url.endswith('recipes/test-recipe'):
        response.status_code = 200
        response.json.return_value = SAMPLE_RECIPE
    elif url.endswith('recipes/missing-recipe'):
        response.status_code = 404
    else:
        response.status_code = 404
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
