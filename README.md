# bsendpoint

## Overview


## Tech

- Python 3.7
- FastAPI
- Pydantic
- uvicorn
- docker
- docker-compose

## Build

Repo contains Dockerfile and docker-compose.yml  
There is no need for database or any other writable storage.

Dependencies are handled with `pip-tools`

### Configuration

App is using starlette config module (https://www.starlette.io/config/)  
All configuration happens via `.env` file or environment variables.

#### Supported environment variables:


### Using docker compose
```
docker-compose up
```

## Dev setup

As application has no needs for database and is only using packages from public PyPi it's very easy to setup locally for development.

### Setup virtualenv
```
cd bsendpoint
python3 -m venv .venv
source .venv/bin/activate
pip install pip-tools
pip-compile requirements/test-requirements.in
```

## API docs

FastAPI supports openapi out-of-the-box.
Location of api docs in local development: http://127.0.0.1:8089/docs
