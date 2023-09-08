# Frontend

![Tests and deployment status](https://github.com/The-Silverwood-Institute/Frontend/actions/workflows/build.yml/badge.svg)

The website of [Recibase][recibase], the recipe ingestion and discovery service.

Recibase's frontend uses [web.py][webpy].

## Requirements

- Python 3.9
- pip

## Installation

`pip install -r requirements.txt`

Test with `pytest`

## Usage

### To start
`BACKEND_URL="https://api.reciba.se/" python3 app.py`
Then navigate to http://0.0.0.0:8080/

If you don't specify `BACKEND_URL` you will need to also have the [Recibase API][recibase] running locally.

### To stop
Hold `Ctrl + C` until it quits

[recibase]: https://github.com/The-Silverwood-Institute/Recibase
[webpy]: http://webpy.org/
