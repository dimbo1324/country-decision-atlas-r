from app.main import health
import asyncio


def test_healthcheck_payload() -> None:
    assert asyncio.run(health()) == {
        "status": "ok",
        "service": "api",
    }
