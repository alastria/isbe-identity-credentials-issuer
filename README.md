# Backend-template

[Manual de configuración](/docs/manual.md )


## Requirements

- Python 3.12.11

### You can install all the requirements with uv (it's very faster)
https://pypi.org/project/uv/

``` bash
# Install uv on macOS and Linux.
$ curl -LsSf https://astral.sh/uv/install.sh | sh
# Creating virtualenv at: .venv
$ uv venv
# Activate with: 
$ source .venv/bin/activate
# Install libs for project
$ uv pip install -r requirements.txt
```

### You can install all the requirements with only pip (OLD)
```bash
pip install -r requirements.txt
or
pip3 install -r requirements.txt
```

## Deployment

To deploy this repo locally, you need to follow these steps

### step-0

You need firstly to pay attention to continue config vars

```bash
ALLOWED_HOSTS:
AWS_ACCESS_KEY:
AWS_BUCKET:
AWS_SECRET_KEY:
BACKEND_DOMAIN:
CERTIFICATIONS_SERVICE_PATH:
NETWORK_SERVICE_HOST:
FEATURE_TOGGLE_PATH:
TOKENIZATION_ACCOUNT_MNEMONIC
TOKENIZATION_ACCOUNT_PATH
TOKENIZATION_SERVICE
OPERATOR_AUTOMATIC_STAFF
CRYPTO_SERVICE
```

### step-1

The backend runs in Docker. We need to have docker (docker-engine) and docker compose installed

To build Docker images (remember that you have to do this everytime you add a new dependency to Pipfile too)

```bash
docker compose build
```

### step-2

The first time we start the project locally it will be necessary to migrate the data and create a superuser

```bash
docker compose run --rm backend python manage.py migrate
docker compose run --rm backend python manage.py createsuperuser
```

### step-3

Start everything (redis, postgress, server, celery and rest of things written in docker compose.yml)

```bash
docker compose up --build
```

Run the backend without docker
```bash
daphne -b 0.0.0.0 -p 8000 project.asgi:application
or
python manage.py runserver # for auto-reload
```

### 3.1. Project commands

If you have project commands, for example one called xxx (define in "project_commands/management/commands/xxx.py"), you can run the command:


```bash
docker compose run --rm backend python manage.py xxx
```


## Monitorización

La aplicación expone métricas Prometheus en `/metrics`. Se puede configurar el prefijo de las métricas con la envvar `PROMETHEUS_METRIC_NAMESPACE`. Por defecto está vacío.

## URLs

- `/metrics`
  - Destinado a ser consumido por Prometheus
  - Abierto, no implementa mecanismos de autenticación/autorización


Copyright © 2025 Comunidad de Madrid & Alastria