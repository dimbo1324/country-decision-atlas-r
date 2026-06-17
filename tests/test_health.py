import asyncio

from app.main import health


def test_healthcheck_payload() -> None:
    assert asyncio.run(health()) == {"status": "ok", "service": "api", "environment": "local"}
