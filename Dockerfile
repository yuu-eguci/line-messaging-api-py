FROM python:3.14-slim AS requirements
RUN pip install --no-cache-dir --disable-pip-version-check pipenv==2026.10.4
WORKDIR /src
COPY Pipfile Pipfile.lock ./
RUN pipenv requirements --hash > requirements.txt \
    && pipenv requirements --dev-only --hash > requirements-dev.txt

FROM python:3.14-slim AS app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY --from=requirements /src/requirements.txt /tmp/requirements.txt
RUN pip install --require-hashes -r /tmp/requirements.txt \
    && useradd --system --uid 10001 app \
    && chown app /app
COPY *.py ./
USER 10001
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "my_flask_script:app"]

FROM app AS dev
USER 0
COPY --from=requirements /src/requirements-dev.txt /tmp/requirements-dev.txt
RUN pip install --require-hashes -r /tmp/requirements-dev.txt
COPY pyproject.toml ./
COPY tests ./tests
USER 10001
CMD ["pytest"]
