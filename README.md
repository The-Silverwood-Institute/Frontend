# Frontend

![Tests and deployment status](https://github.com/The-Silverwood-Institute/Frontend/actions/workflows/build.yml/badge.svg)

The website of [Recibase][recibase], the recipe ingestion and discovery service.

Recibase's frontend uses [web.py][webpy].

## Requirements

- Python 3.9
- pip

Currently [doesn't work](https://github.com/webpy/webpy/issues/799) on Python 3.13

## Setup

1. `python3 -m venv .venv`
2. `source .venv/bin/activate`
3. `pip install -r requirements.txt`

Repeat step 2 every time you open a new shell

Test setup was successful with `pytest`

## Usage

### To start
1. `BACKEND_URL="https://api.reciba.se/" python3 app.py`
2. Navigate to http://0.0.0.0:8080/

If you don't specify `BACKEND_URL` you will need to also have the [Recibase API][recibase] running locally.

### To stop
Hold `Ctrl + C` until it quits

[recibase]: https://github.com/The-Silverwood-Institute/Recibase
[webpy]: http://webpy.org/
