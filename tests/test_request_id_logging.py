import io
import json
import logging

from django.test import Client
from django.test.utils import override_settings
from pythonjsonlogger.json import JsonFormatter

from project.logging.conf import ContextVarsFilter  # your filter

MINIMAL_MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "project.logging.middleware.request_id_middleware",
]


@override_settings(
    # in-memory DB so Django doesn’t try to reach Postgres
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    # avoid sessions/auth so no DB lookups happen for user/session
    MIDDLEWARE=MINIMAL_MIDDLEWARE,
    AUTHENTICATION_BACKENDS=[],
    CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}},
)
def test_health_logs_request_id():
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.addFilter(ContextVarsFilter())
    handler.setFormatter(
        JsonFormatter(
            "%(levelname)s %(name)s %(message)s %(request_id)s %(method)s %(path)s"
        )
    )

    logger = logging.getLogger("project.urls")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    try:
        client = Client()  # build after override_settings is active
        r = client.get("/api/v1/health", HTTP_X_REQUEST_ID="abc123")
        assert r.status_code == 200
    finally:
        logger.removeHandler(handler)

    stream.seek(0)
    records = [
        json.loads(line) for line in stream.getvalue().splitlines() if line.strip()
    ]

    assert any(
        rec.get("request_id") == "abc123"
        and rec.get("message") == "api health"
        and rec.get("path") == "/api/v1/health"
        and rec.get("method") == "GET"
        for rec in records
    ), records


@override_settings(
    DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    MIDDLEWARE=MINIMAL_MIDDLEWARE,
    AUTHENTICATION_BACKENDS=[],
)
def test_api_health():
    client = Client()
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
