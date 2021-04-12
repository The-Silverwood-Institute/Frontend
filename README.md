# Frontend

The website of [Recibase][recibase], the recipe ingestion and discovery service.

Recibase's frontend uses [web.py][webpy].

## Requirements

- Python 3.9
- pip

## Installation

`pip install -r requirements.txt`

## Usage

### To start
`python app.py`
Then navigate to http://0.0.0.0:8080/

Recibase's frontend needs a `recipes.db` database to start. You can generate this using [Recibase][recibase].

### To stop
Hold `Ctrl + C` until it quits

[recibase]: https://github.com/The-Silverwood-Institute/Recibase
[webpy]: http://webpy.org/
