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


SAMPLE_TAGS = {
    'tags': [
        {'name': 'Soup', 'entry_name': 'Soup', 'description': None, 'category': 'meal', 'superset': None, 'implied_tags': []},
        {
            'name': 'Ensures recipe is excluded from meal planner. Only use if necessary.',
            'entry_name': 'Ensures recipe is excluded from meal planner. Only use if necessary.',
            'description': None,
            'category': 'meal',
            'superset': None,
            'implied_tags': [],
        },
        {'name': 'Vegan', 'entry_name': 'Vegan', 'description': 'No animal products', 'category': 'diet', 'superset': 'Vegan-ish', 'implied_tags': ['Vegan-ish']},
        {'name': 'Vegetarian-ish', 'entry_name': 'Vegetarian-ish', 'description': 'Can make vegetarian with minimal changes', 'category': 'diet', 'superset': 'Pescatarian', 'implied_tags': ['Pescatarian']},
        {'name': 'Pescatarian', 'entry_name': 'Pescatarian', 'description': 'Contains fish but not meat', 'category': 'diet', 'superset': None, 'implied_tags': []},
        {'name': 'Gluten-Free', 'entry_name': 'Gluten-Free', 'description': None, 'category': 'diet', 'superset': None, 'implied_tags': []},
        {'name': 'Spicy', 'entry_name': 'Spicy', 'description': 'Hot, rather than just aromatic', 'category': 'vibe', 'superset': None, 'implied_tags': []},
        {'name': 'Scales', 'entry_name': 'Scales', 'description': 'Easy to scale up to many servings', 'category': 'making', 'superset': None, 'implied_tags': []},
        {'name': 'Freezes', 'entry_name': 'Freezes', 'description': 'Keeps well in the freezer', 'category': 'practical', 'superset': None, 'implied_tags': []},
        {'name': 'AI', 'entry_name': 'AI', 'description': 'The recipe text was drafted with AI', 'category': 'practical', 'superset': None, 'implied_tags': []},
        {'name': 'Never Eaten', 'entry_name': 'Never Eaten', 'description': 'Never eaten for dinner', 'category': 'usage', 'superset': None, 'implied_tags': []},
        {'name': 'Popular', 'entry_name': 'Popular', 'description': 'Eaten for dinner at least five times', 'category': 'usage', 'superset': None, 'implied_tags': []},
        {'name': 'New', 'entry_name': 'New', 'description': 'Added in the last 12 months', 'category': 'usage', 'superset': None, 'implied_tags': []},
    ],
}


def _mock_requests_get(url, **kwargs):
    response = MagicMock()
    response.status_code = 200
    if url.endswith('recipes/'):
        response.json.return_value = SAMPLE_RECIPES
    elif url.endswith('/tags'):
        response.json.return_value = SAMPLE_TAGS
    elif url.endswith('manifest'):
        response.json.return_value = {
            'version': 'deadbeef',
            'name': 'Recibase',
            'source_url': 'https://github.com/The-Silverwood-Institute/Recibase',
            'base_commit_url': 'https://github.com/The-Silverwood-Institute/Recibase/commit/',
        }
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
