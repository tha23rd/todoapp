FROM python:3.9-slim as build

RUN pip install poetry
WORKDIR /app
COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.in-project true && poetry install --no-root --no-interaction
COPY app /app/app/

RUN poetry install --no-dev --no-interaction

FROM python:3.9-slim

COPY --from=build /app/.venv /app/.venv/
COPY --from=build /app/app /app/app/

COPY gunicorn_conf.py /app/gunicorn_conf.py

EXPOSE 8080
# To make mouting of HTML from static/ in fastapi_demo work
WORKDIR /app

CMD [".venv/bin/gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--config", "gunicorn_conf.py", "app.main:app", "--preload"]