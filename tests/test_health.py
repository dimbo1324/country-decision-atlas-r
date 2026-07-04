"""Basic healthcheck endpoint payload."""

import asyncio
from app.main import health


def test_healthcheck_payload() -> None:
    assert asyncio.run(health()).model_dump() == {
        "status": "ok",
        "service": "api",
        "environment": "production",
    }
