import json


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


def test_copy_js_merges_duplicate_ingredients():
    import subprocess

    result = subprocess.run(
        ['node', 'test_copy.js'],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
