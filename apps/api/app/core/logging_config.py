import json
import logging
from app.core.request_context import get_request_id
from datetime import UTC, datetime
from typing import Any


class JsonLogFormatter(logging.Formatter):
    """Structured JSON logs (P2-1, Аудит-эпизод 7) — a plain
    logging.Formatter subclass, no new dependency. Every line carries level,
    time, component, message, and the current request's X-Request-ID (or
    "-" outside a request), so log lines from one request can be grepped
    together across every component that touched it."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=UTC
            ).isoformat(),
            "level": record.levelname,
            "component": record.name,
            "message": record.getMessage(),
            "request_id": get_request_id(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonLogFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)
