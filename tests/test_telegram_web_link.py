from app.repositories import auth as repository
from app.services import telegram_web_link as service
from datetime import UTC, datetime
from fastapi import HTTPException
import pytest
from typing import Any, cast
from unittest.mock import MagicMock


CONNECTION = MagicMock()


class FakeTelegramLinkClient:
    def __init__(
        self, *, consume_result: service.ConsumeLinkCodeResult, unlink_ok: bool = True
    ) -> None:
        self._consume_result = consume_result
        self._unlink_ok = unlink_ok
        self.unlink_calls: list[str] = []

    def consume_link_code(
        self, _code: str, _web_user_id: str
    ) -> service.ConsumeLinkCodeResult:
        return self._consume_result

    def unlink(self, telegram_user_id: str) -> bool:
        self.unlink_calls.append(telegram_user_id)
        return self._unlink_ok


def _link_row(**overrides: Any) -> dict[str, Any]:
    row = {
        "id": "link-1",
        "user_id": "user-1",
        "telegram_user_id": "tg-1",
        "status": "linked",
        "linked_at": datetime(2026, 1, 1, tzinfo=UTC),
        "unlinked_at": None,
    }
    row.update(overrides)
    return row


def _use_fake_client(
    monkeypatch: pytest.MonkeyPatch, client: FakeTelegramLinkClient
) -> None:
    monkeypatch.setattr(service, "get_telegram_link_client", lambda: client)


def test_link_telegram_account_rejects_when_already_linked(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        repository, "get_telegram_link_by_user", lambda *_a: _link_row()
    )
    with pytest.raises(HTTPException) as exc_info:
        service.link_telegram_account(CONNECTION, user_id="user-1", code="123456")
    assert exc_info.value.status_code == 409
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "telegram_already_linked"


@pytest.mark.parametrize(
    ("grpc_error", "expected_code"),
    [
        ("invalid_code", "telegram_link_invalid_code"),
        ("expired_code", "telegram_link_expired_code"),
        ("already_used", "telegram_link_already_used"),
        ("unexpected_error", "telegram_link_invalid_code"),
    ],
)
def test_link_telegram_account_maps_grpc_errors(
    monkeypatch: pytest.MonkeyPatch, grpc_error: str, expected_code: str
) -> None:
    monkeypatch.setattr(repository, "get_telegram_link_by_user", lambda *_a: None)
    fake_client = FakeTelegramLinkClient(
        consume_result=service.ConsumeLinkCodeResult(
            ok=False, telegram_user_id="", error=grpc_error
        )
    )
    _use_fake_client(monkeypatch, fake_client)
    with pytest.raises(HTTPException) as exc_info:
        service.link_telegram_account(CONNECTION, user_id="user-1", code="000000")
    assert exc_info.value.status_code == 422
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == expected_code


def test_link_telegram_account_success_creates_link(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(repository, "get_telegram_link_by_user", lambda *_a: None)
    fake_client = FakeTelegramLinkClient(
        consume_result=service.ConsumeLinkCodeResult(
            ok=True, telegram_user_id="tg-42", error=""
        )
    )
    _use_fake_client(monkeypatch, fake_client)
    captured: dict[str, Any] = {}

    def fake_create_telegram_link(_conn: Any, **kwargs: Any) -> dict[str, Any]:
        captured.update(kwargs)
        return _link_row(telegram_user_id=kwargs["telegram_user_id"])

    monkeypatch.setattr(repository, "create_telegram_link", fake_create_telegram_link)
    link = service.link_telegram_account(CONNECTION, user_id="user-1", code="123456")
    assert link["telegram_user_id"] == "tg-42"
    assert captured == {"user_id": "user-1", "telegram_user_id": "tg-42"}


def test_unlink_telegram_account_noop_when_not_linked(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(repository, "get_telegram_link_by_user", lambda *_a: None)
    fake_client = FakeTelegramLinkClient(
        consume_result=service.ConsumeLinkCodeResult(
            ok=True, telegram_user_id="", error=""
        )
    )
    _use_fake_client(monkeypatch, fake_client)
    service.unlink_telegram_account(CONNECTION, user_id="user-1")
    assert fake_client.unlink_calls == []


def test_unlink_telegram_account_calls_grpc_then_repository(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        repository, "get_telegram_link_by_user", lambda *_a: _link_row()
    )
    fake_client = FakeTelegramLinkClient(
        consume_result=service.ConsumeLinkCodeResult(
            ok=True, telegram_user_id="", error=""
        )
    )
    _use_fake_client(monkeypatch, fake_client)
    captured: dict[str, Any] = {}
    monkeypatch.setattr(
        repository,
        "unlink_telegram_user",
        lambda _conn, user_id: captured.setdefault("user_id", user_id),
    )
    service.unlink_telegram_account(CONNECTION, user_id="user-1")
    assert fake_client.unlink_calls == ["tg-1"]
    assert captured["user_id"] == "user-1"


def test_get_telegram_link_status_returns_repository_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        repository, "get_telegram_link_by_user", lambda *_a: _link_row()
    )
    status = service.get_telegram_link_status(CONNECTION, user_id="user-1")
    assert status is not None
    assert status["telegram_user_id"] == "tg-1"


def test_get_telegram_link_status_returns_none_when_not_linked(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(repository, "get_telegram_link_by_user", lambda *_a: None)
    status = service.get_telegram_link_status(CONNECTION, user_id="user-1")
    assert status is None
