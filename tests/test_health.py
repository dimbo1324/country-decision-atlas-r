from app.main import health
import asyncio


def test_healthcheck_payload() -> None:
    assert asyncio.run(health()).model_dump() == {
        "status": "ok",
        "service": "api",
        "environment": "production",
    }
