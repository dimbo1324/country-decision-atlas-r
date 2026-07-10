"""Request-id middleware, JSON log formatter, and /metrics (P2-1, Аудит-
эпизод 7). Builds the real app via create_app() rather than a bare FastAPI()
test app - the acceptance criteria are about the actual middleware stack
(response headers, rate-limit exemption), not router-level logic."""

import json
import logging
import re
import sys
from app.bootstrap.app_factory import create_app
from app.core.config import Settings
from app.core.logging_config import JsonLogFormatter
from app.core.request_context import (
    bind_request_id,
    get_request_id,
    reset_request_id,
)
from app.schemas.system import HealthResponse, ReadinessResponse
from app.services import metrics
from fastapi.testclient import TestClient


async def _health() -> HealthResponse:
    return HealthResponse(status="ok", service="api", environment="local")


def _ready() -> ReadinessResponse:
    return ReadinessResponse(
        status="ready", service="api", environment="local", database="ok"
    )


def _client() -> TestClient:
    app = create_app(
        settings=Settings(app_env="local"),
        rate_limit_client=lambda _request: None,
        health_handler=_health,
        readiness_handler=_ready,
    )
    return TestClient(app, raise_server_exceptions=False)


def test_response_includes_a_generated_request_id() -> None:
    response = _client().get("/health")
    request_id = response.headers.get("x-request-id")
    assert request_id is not None
    assert re.fullmatch(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        request_id,
    )


def test_incoming_request_id_is_echoed_not_replaced() -> None:
    response = _client().get(
        "/health", headers={"X-Request-ID": "caller-supplied-id"}
    )
    assert response.headers.get("x-request-id") == "caller-supplied-id"


def test_request_id_is_unique_per_request() -> None:
    client = _client()
    first = client.get("/health").headers.get("x-request-id")
    second = client.get("/health").headers.get("x-request-id")
    assert first != second


def test_request_id_context_var_round_trips() -> None:
    assert get_request_id() == "-"
    token = bind_request_id("abc-123")
    try:
        assert get_request_id() == "abc-123"
    finally:
        reset_request_id(token)
    assert get_request_id() == "-"


def test_json_log_formatter_produces_parseable_lines_with_expected_keys() -> (
    None
):
    logger = logging.getLogger("test.observability")
    record = logger.makeRecord(
        name="test.observability",
        level=logging.INFO,
        fn=__file__,
        lno=1,
        msg="something happened: %s",
        args=("detail",),
        exc_info=None,
    )
    rendered = JsonLogFormatter().format(record)
    parsed = json.loads(rendered)
    assert parsed["level"] == "INFO"
    assert parsed["component"] == "test.observability"
    assert parsed["message"] == "something happened: detail"
    assert "timestamp" in parsed
    assert "request_id" in parsed


def test_json_log_formatter_includes_request_id_when_bound() -> None:
    logger = logging.getLogger("test.observability")
    record = logger.makeRecord(
        name="test.observability",
        level=logging.INFO,
        fn=__file__,
        lno=1,
        msg="inside a request",
        args=(),
        exc_info=None,
    )
    token = bind_request_id("req-42")
    try:
        parsed = json.loads(JsonLogFormatter().format(record))
    finally:
        reset_request_id(token)
    assert parsed["request_id"] == "req-42"


def test_json_log_formatter_captures_exception_info() -> None:
    logger = logging.getLogger("test.observability")
    try:
        raise ValueError("boom")
    except ValueError:
        record = logger.makeRecord(
            name="test.observability",
            level=logging.ERROR,
            fn=__file__,
            lno=1,
            msg="failed",
            args=(),
            exc_info=sys.exc_info(),
            sinfo=None,
        )
    parsed = json.loads(JsonLogFormatter().format(record))
    assert "ValueError: boom" in parsed["exception"]


def test_metrics_endpoint_returns_prometheus_text_with_expected_names() -> None:
    metrics.reset_metrics()
    client = _client()
    client.get("/health")
    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    body = response.text
    assert "# TYPE http_requests_total counter" in body
    assert "# TYPE http_request_duration_seconds histogram" in body
    assert "# TYPE db_pool_connections gauge" in body
    assert 'http_requests_total{status="200"}' in body


def test_metrics_records_request_count_and_latency() -> None:
    metrics.reset_metrics()
    metrics.record_request(200, 0.02)
    metrics.record_request(200, 0.02)
    metrics.record_request(404, 0.5)
    rendered = metrics.render_prometheus_text()
    assert 'http_requests_total{status="200"} 2' in rendered
    assert 'http_requests_total{status="404"} 1' in rendered
    assert "http_request_duration_seconds_count 3" in rendered


def test_metrics_is_exempt_from_rate_limiting() -> None:
    metrics.reset_metrics()
    client = _client()
    responses = [client.get("/metrics") for _ in range(5)]
    assert all(response.status_code == 200 for response in responses)


def test_metrics_reset_clears_previous_counts() -> None:
    metrics.record_request(500, 1.0)
    metrics.reset_metrics()
    rendered = metrics.render_prometheus_text()
    assert 'status="500"' not in rendered
