"""Registration feature gating and input validation (email/password strength)."""

import pytest
from app.core.config import Settings
from app.repositories import auth as repository, security_notifications
from app.services import (
    auth as service,
    feature_flags as feature_flags_service,
    rate_limiter,
)
from datetime import UTC, datetime
from fastapi import HTTPException
from typing import Any, cast
from unittest.mock import MagicMock


CONNECTION = MagicMock()

_SETTINGS = Settings(
    app_env="local",
    auth_session_ttl_hours=168,
    auth_session_touch_interval_minutes=5,
    auth_password_min_length=12,
    auth_registration_enabled=True,
)


def _enable_auth(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        feature_flags_service,
        "is_feature_enabled_by_key",
        lambda *_a, **_kw: True,
    )
    monkeypatch.setattr(service, "get_settings", lambda: _SETTINGS)


def _disable_auth(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        feature_flags_service,
        "is_feature_enabled_by_key",
        lambda *_a, **_kw: False,
    )
    monkeypatch.setattr(service, "get_settings", lambda: _SETTINGS)


def _user_row(**overrides: Any) -> dict[str, Any]:
    row = {
        "id": "11111111-1111-1111-1111-111111111111",
        "email": "user@example.local",
        "display_name": "User",
        "role": "user",
        "status": "active",
        "created_at": datetime(2026, 1, 1, tzinfo=UTC),
        "updated_at": datetime(2026, 1, 1, tzinfo=UTC),
    }
    row.update(overrides)
    return row


def _session_row(**overrides: Any) -> dict[str, Any]:
    row = {
        "id": "session-1",
        "user_id": "11111111-1111-1111-1111-111111111111",
        "created_at": datetime(2026, 1, 1, tzinfo=UTC),
        "expires_at": datetime(2026, 1, 8, tzinfo=UTC),
        "revoked_at": None,
        "last_seen_at": None,
        "rotated_at": None,
    }
    row.update(overrides)
    return row


def _session_with_user_result(
    *,
    session: dict[str, Any] | None = None,
    user: dict[str, Any] | None = None,
    is_revoked: bool = False,
    is_expired: bool = False,
    matched_current_token: bool = True,
) -> dict[str, Any]:
    return {
        "is_revoked": is_revoked,
        "is_expired": is_expired,
        "matched_current_token": matched_current_token,
        "session": session if session is not None else _session_row(),
        "user": user if user is not None else _user_row(),
    }


def _mock_known_device(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        repository,
        "has_prior_session_with_fingerprint",
        lambda *_a, **_kw: True,
    )


def test_register_user_disabled_feature_returns_403(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _disable_auth(monkeypatch)
    with pytest.raises(HTTPException) as exc_info:
        service.register_user(
            CONNECTION,
            email="new@example.local",
            password="a-long-password",
            display_name="New",
        )
    assert exc_info.value.status_code == 403
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "feature_disabled"


def test_register_user_registration_disabled_returns_403(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        feature_flags_service,
        "is_feature_enabled_by_key",
        lambda *_a, **_kw: True,
    )
    monkeypatch.setattr(
        service,
        "get_settings",
        lambda: Settings(app_env="local", auth_registration_enabled=False),
    )
    with pytest.raises(HTTPException) as exc_info:
        service.register_user(
            CONNECTION,
            email="new@example.local",
            password="a-long-password",
            display_name="New",
        )
    assert exc_info.value.status_code == 403
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "feature_disabled"


def test_register_user_rejects_invalid_email(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_auth(monkeypatch)
    with pytest.raises(HTTPException) as exc_info:
        service.register_user(
            CONNECTION,
            email="not-an-email",
            password="a-long-password",
            display_name="New",
        )
    assert exc_info.value.status_code == 422
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "invalid_email"


def test_register_user_rejects_weak_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_auth(monkeypatch)
    with pytest.raises(HTTPException) as exc_info:
        service.register_user(
            CONNECTION,
            email="new@example.local",
            password="short",
            display_name="New",
        )
    assert exc_info.value.status_code == 422
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "weak_password"


def test_register_user_rejects_duplicate_email(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_auth(monkeypatch)
    monkeypatch.setattr(
        repository, "get_user_by_email", lambda *_a: _user_row()
    )
    with pytest.raises(HTTPException) as exc_info:
        service.register_user(
            CONNECTION,
            email="user@example.local",
            password="a-long-password",
            display_name="New",
        )
    assert exc_info.value.status_code == 409
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "email_already_registered"


def test_register_user_creates_user_and_password_credential(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_auth(monkeypatch)
    monkeypatch.setattr(repository, "get_user_by_email", lambda *_a: None)
    monkeypatch.setattr(
        repository, "create_user", lambda *_a, **_kw: _user_row()
    )
    stored: dict[str, Any] = {}

    def fake_set_password_credential(
        _conn: Any, user_id: str, password_hash: str
    ) -> None:
        stored["user_id"] = user_id
        stored["password_hash"] = password_hash

    monkeypatch.setattr(
        repository, "set_password_credential", fake_set_password_credential
    )
    user = service.register_user(
        CONNECTION,
        email="  User@Example.Local  ",
        password="a-long-password",
        display_name="  New User  ",
    )
    assert user["email"] == "user@example.local"
    assert stored["user_id"] == user["id"]
    assert service.verify_password("a-long-password", stored["password_hash"])


def test_login_user_rejects_missing_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_auth(monkeypatch)
    monkeypatch.setattr(
        repository, "get_user_by_email_with_credentials", lambda *_a: None
    )
    with pytest.raises(HTTPException) as exc_info:
        service.login_user(
            CONNECTION, email="missing@example.local", password="whatever12345"
        )
    assert exc_info.value.status_code == 401
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "invalid_credentials"


def test_login_user_rejects_wrong_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_auth(monkeypatch)
    correct_hash = service.hash_password("correct-password-123")
    monkeypatch.setattr(
        repository,
        "get_user_by_email_with_credentials",
        lambda *_a: {**_user_row(), "password_hash": correct_hash},
    )
    with pytest.raises(HTTPException) as exc_info:
        service.login_user(
            CONNECTION,
            email="user@example.local",
            password="wrong-password-123",
        )
    assert exc_info.value.status_code == 401
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "invalid_credentials"


def test_login_user_rejects_when_locked_out(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_auth(monkeypatch)
    monkeypatch.setattr(rate_limiter, "is_login_locked_out", lambda *_a: True)
    get_credentials_called: dict[str, Any] = {}
    monkeypatch.setattr(
        repository,
        "get_user_by_email_with_credentials",
        lambda *_a: get_credentials_called.setdefault("called", True),
    )
    with pytest.raises(HTTPException) as exc_info:
        service.login_user(
            CONNECTION, email="user@example.local", password="whatever12345"
        )
    assert exc_info.value.status_code == 429
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "too_many_login_attempts"
    assert "called" not in get_credentials_called


def test_login_user_records_failure_on_wrong_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_auth(monkeypatch)
    monkeypatch.setattr(rate_limiter, "is_login_locked_out", lambda *_a: False)
    correct_hash = service.hash_password("correct-password-123")
    monkeypatch.setattr(
        repository,
        "get_user_by_email_with_credentials",
        lambda *_a: {**_user_row(), "password_hash": correct_hash},
    )
    recorded: dict[str, Any] = {}
    monkeypatch.setattr(
        rate_limiter,
        "record_login_failure",
        lambda email: recorded.setdefault("email", email),
    )
    with pytest.raises(HTTPException):
        service.login_user(
            CONNECTION,
            email="user@example.local",
            password="wrong-password-123",
        )
    assert recorded["email"] == "user@example.local"


def test_login_user_clears_failures_on_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_auth(monkeypatch)
    monkeypatch.setattr(rate_limiter, "is_login_locked_out", lambda *_a: False)
    correct_hash = service.hash_password("correct-password-123")
    monkeypatch.setattr(
        repository,
        "get_user_by_email_with_credentials",
        lambda *_a: {**_user_row(), "password_hash": correct_hash},
    )
    monkeypatch.setattr(repository, "update_last_login", lambda *_a: None)
    monkeypatch.setattr(
        repository,
        "create_auth_session",
        lambda *_a, **kwargs: _session_row(user_id=kwargs["user_id"]),
    )
    monkeypatch.setattr(repository, "get_user_by_id", lambda *_a: _user_row())
    _mock_known_device(monkeypatch)
    cleared: dict[str, Any] = {}
    monkeypatch.setattr(
        rate_limiter,
        "clear_login_failures",
        lambda email: cleared.setdefault("email", email),
    )
    service.login_user(
        CONNECTION,
        email="user@example.local",
        password="correct-password-123",
    )
    assert cleared["email"] == "user@example.local"


def test_login_user_rejects_suspended_account(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_auth(monkeypatch)
    correct_hash = service.hash_password("correct-password-123")
    monkeypatch.setattr(
        repository,
        "get_user_by_email_with_credentials",
        lambda *_a: {
            **_user_row(status="suspended"),
            "password_hash": correct_hash,
        },
    )
    with pytest.raises(HTTPException) as exc_info:
        service.login_user(
            CONNECTION,
            email="user@example.local",
            password="correct-password-123",
        )
    assert exc_info.value.status_code == 403
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "user_suspended"


def test_login_user_rejects_deleted_account(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_auth(monkeypatch)
    correct_hash = service.hash_password("correct-password-123")
    monkeypatch.setattr(
        repository,
        "get_user_by_email_with_credentials",
        lambda *_a: {
            **_user_row(status="deleted"),
            "password_hash": correct_hash,
        },
    )
    with pytest.raises(HTTPException) as exc_info:
        service.login_user(
            CONNECTION,
            email="user@example.local",
            password="correct-password-123",
        )
    assert exc_info.value.status_code == 403
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "user_deleted"


def test_login_user_success_creates_session_and_updates_last_login(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_auth(monkeypatch)
    correct_hash = service.hash_password("correct-password-123")
    monkeypatch.setattr(
        repository,
        "get_user_by_email_with_credentials",
        lambda *_a: {**_user_row(), "password_hash": correct_hash},
    )
    touched: dict[str, Any] = {}
    monkeypatch.setattr(
        repository,
        "update_last_login",
        lambda _conn, user_id: touched.setdefault("user_id", user_id),
    )
    monkeypatch.setattr(
        repository,
        "create_auth_session",
        lambda *_a, **kwargs: _session_row(user_id=kwargs["user_id"]),
    )
    monkeypatch.setattr(repository, "get_user_by_id", lambda *_a: _user_row())
    _mock_known_device(monkeypatch)
    raw_token, user, session, is_new_device = service.login_user(
        CONNECTION, email="user@example.local", password="correct-password-123"
    )
    assert isinstance(raw_token, str) and len(raw_token) > 0
    assert user["id"] == _user_row()["id"]
    assert session["id"] == "session-1"
    assert touched["user_id"] == _user_row()["id"]
    assert is_new_device is False


def test_create_login_session_stores_hashed_token_not_raw(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(service, "get_settings", lambda: _SETTINGS)
    _mock_known_device(monkeypatch)
    captured: dict[str, Any] = {}

    def fake_create_auth_session(_conn: Any, **kwargs: Any) -> dict[str, Any]:
        captured.update(kwargs)
        return _session_row(user_id=kwargs["user_id"])

    monkeypatch.setattr(
        repository, "create_auth_session", fake_create_auth_session
    )
    raw_token, session, is_new_device = service.create_login_session(
        CONNECTION, user_id="user-1"
    )
    assert captured["token_hash"] == service.hash_session_token(raw_token)
    assert captured["token_hash"] != raw_token
    assert session["id"] == "session-1"
    assert is_new_device is False


def test_logout_session_revokes_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_revoke_session(_conn: Any, session_id: str, user_id: str) -> None:
        captured["session_id"] = session_id
        captured["user_id"] = user_id

    monkeypatch.setattr(repository, "revoke_session", fake_revoke_session)
    service.logout_session(CONNECTION, user_id="user-1", session_id="session-1")
    assert captured == {"session_id": "session-1", "user_id": "user-1"}


def test_validate_session_token_rejects_unknown_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        repository, "get_session_with_user_by_token_hash", lambda *_a: None
    )
    with pytest.raises(HTTPException) as exc_info:
        service.validate_session_token(CONNECTION, "unknown-token")
    assert exc_info.value.status_code == 401
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "invalid_auth_token"


def test_validate_session_token_rejects_revoked_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        repository,
        "get_session_with_user_by_token_hash",
        lambda *_a: _session_with_user_result(is_revoked=True),
    )
    with pytest.raises(HTTPException) as exc_info:
        service.validate_session_token(CONNECTION, "revoked-token")
    assert exc_info.value.status_code == 401
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "invalid_auth_token"


def test_validate_session_token_reports_expired_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        repository,
        "get_session_with_user_by_token_hash",
        lambda *_a: _session_with_user_result(is_expired=True),
    )
    with pytest.raises(HTTPException) as exc_info:
        service.validate_session_token(CONNECTION, "expired-token")
    assert exc_info.value.status_code == 401
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "auth_session_expired"


def test_validate_session_token_rejects_suspended_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        repository,
        "get_session_with_user_by_token_hash",
        lambda *_a: _session_with_user_result(
            user=_user_row(status="suspended")
        ),
    )
    with pytest.raises(HTTPException) as exc_info:
        service.validate_session_token(CONNECTION, "valid-token")
    assert exc_info.value.status_code == 403
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "user_suspended"


def test_validate_session_token_success_touches_stale_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(service, "get_settings", lambda: _SETTINGS)
    monkeypatch.setattr(
        repository,
        "get_session_with_user_by_token_hash",
        lambda *_a: _session_with_user_result(
            session=_session_row(
                last_seen_at=None, rotated_at=datetime.now(UTC)
            )
        ),
    )
    touched: dict[str, Any] = {}
    monkeypatch.setattr(
        repository,
        "touch_session",
        lambda _conn, session_id: touched.setdefault("session_id", session_id),
    )
    result = service.validate_session_token(CONNECTION, "valid-token")
    assert result["user"]["id"] == _user_row()["id"]
    assert result["session"]["id"] == "session-1"
    assert touched["session_id"] == "session-1"


def test_validate_session_token_does_not_touch_recently_seen_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(service, "get_settings", lambda: _SETTINGS)
    monkeypatch.setattr(
        repository,
        "get_session_with_user_by_token_hash",
        lambda *_a: _session_with_user_result(
            session=_session_row(
                last_seen_at=datetime.now(UTC), rotated_at=datetime.now(UTC)
            )
        ),
    )
    touched: dict[str, Any] = {}
    monkeypatch.setattr(
        repository,
        "touch_session",
        lambda _conn, session_id: touched.setdefault("session_id", session_id),
    )
    service.validate_session_token(CONNECTION, "valid-token")
    assert touched == {}


def test_get_current_user_from_token_returns_user_dict(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        repository,
        "get_session_with_user_by_token_hash",
        lambda *_a: _session_with_user_result(),
    )
    monkeypatch.setattr(repository, "touch_session", lambda *_a: None)
    monkeypatch.setattr(
        repository, "rotate_session_token", lambda *_a, **_kw: None
    )
    user = service.get_current_user_from_token(CONNECTION, "valid-token")
    assert user["id"] == _user_row()["id"]


def test_validate_session_token_rotates_stale_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(service, "get_settings", lambda: _SETTINGS)
    monkeypatch.setattr(
        repository,
        "get_session_with_user_by_token_hash",
        lambda *_a: _session_with_user_result(
            session=_session_row(rotated_at=None)
        ),
    )
    rotated: dict[str, Any] = {}
    monkeypatch.setattr(
        repository,
        "rotate_session_token",
        lambda _conn, session_id, **kwargs: rotated.update(
            session_id=session_id, **kwargs
        ),
    )
    touched: dict[str, Any] = {}
    monkeypatch.setattr(
        repository,
        "touch_session",
        lambda _conn, session_id: touched.setdefault("session_id", session_id),
    )
    result = service.validate_session_token(CONNECTION, "valid-token")
    assert rotated["session_id"] == "session-1"
    assert rotated["new_token_hash"] == service.hash_session_token(
        result["rotated_token"]
    )
    assert rotated["previous_token_hash"] == service.hash_session_token(
        "valid-token"
    )
    assert result["rotated_token"] is not None
    assert result["rotated_token"] != "valid-token"
    assert touched == {}


def test_validate_session_token_does_not_rotate_fresh_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(service, "get_settings", lambda: _SETTINGS)
    monkeypatch.setattr(
        repository,
        "get_session_with_user_by_token_hash",
        lambda *_a: _session_with_user_result(
            session=_session_row(
                last_seen_at=datetime.now(UTC), rotated_at=datetime.now(UTC)
            )
        ),
    )
    rotated: dict[str, Any] = {}
    monkeypatch.setattr(
        repository,
        "rotate_session_token",
        lambda *_a, **_kw: rotated.setdefault("called", True),
    )
    result = service.validate_session_token(CONNECTION, "valid-token")
    assert rotated == {}
    assert result["rotated_token"] is None


def test_validate_session_token_accepts_previous_token_in_grace_window(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(service, "get_settings", lambda: _SETTINGS)
    monkeypatch.setattr(
        repository,
        "get_session_with_user_by_token_hash",
        lambda *_a: _session_with_user_result(
            session=_session_row(rotated_at=datetime.now(UTC)),
            matched_current_token=False,
        ),
    )
    rotated: dict[str, Any] = {}
    touched: dict[str, Any] = {}
    monkeypatch.setattr(
        repository,
        "rotate_session_token",
        lambda *_a, **_kw: rotated.setdefault("called", True),
    )
    monkeypatch.setattr(
        repository,
        "touch_session",
        lambda *_a: touched.setdefault("called", True),
    )
    result = service.validate_session_token(CONNECTION, "previous-token")
    assert result["user"]["id"] == _user_row()["id"]
    assert rotated == {}
    assert touched == {}


def test_require_step_up_reauthentication_accepts_correct_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    correct_hash = service.hash_password("correct-password-123")
    monkeypatch.setattr(
        repository,
        "get_password_credential",
        lambda *_a: {"password_hash": correct_hash},
    )
    service.require_step_up_reauthentication(
        CONNECTION, user_id="user-1", password="correct-password-123"
    )


def test_require_step_up_reauthentication_rejects_wrong_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    correct_hash = service.hash_password("correct-password-123")
    monkeypatch.setattr(
        repository,
        "get_password_credential",
        lambda *_a: {"password_hash": correct_hash},
    )
    with pytest.raises(HTTPException) as exc_info:
        service.require_step_up_reauthentication(
            CONNECTION, user_id="user-1", password="wrong-password"
        )
    assert exc_info.value.status_code == 401
    detail = cast(dict[str, Any], exc_info.value.detail)
    assert detail["error"]["code"] == "step_up_reauthentication_failed"


def test_require_step_up_reauthentication_rejects_missing_credential(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(repository, "get_password_credential", lambda *_a: None)
    with pytest.raises(HTTPException) as exc_info:
        service.require_step_up_reauthentication(
            CONNECTION, user_id="user-1", password="anything"
        )
    assert exc_info.value.status_code == 401


def test_create_login_session_flags_first_session_as_new_device(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(service, "get_settings", lambda: _SETTINGS)
    monkeypatch.setattr(
        repository,
        "has_prior_session_with_fingerprint",
        lambda *_a, **_kw: False,
    )
    monkeypatch.setattr(
        repository,
        "create_auth_session",
        lambda _conn, **kwargs: _session_row(
            id="22222222-2222-2222-2222-222222222222",
            user_id=kwargs["user_id"],
        ),
    )
    notified: dict[str, Any] = {}
    monkeypatch.setattr(
        security_notifications,
        "create_new_device_login_notification",
        lambda _conn, **kwargs: notified.update(kwargs),
    )
    audited: dict[str, Any] = {}
    monkeypatch.setattr(
        service,
        "insert_audit_event",
        lambda _conn, **kwargs: audited.update(kwargs),
    )
    _raw_token, _session, is_new_device = service.create_login_session(
        CONNECTION,
        user_id="user-1",
        user_agent="Mozilla/5.0 (Windows NT 10.0) Chrome/120.0.0.0",
        client_ip="203.0.113.5",
    )
    assert is_new_device is True
    assert notified["user_id"] == "user-1"
    assert notified["device_label"] == "Chrome on Windows"
    assert audited["action"] == "new_device_login"


def test_create_login_session_does_not_notify_known_device(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(service, "get_settings", lambda: _SETTINGS)
    _mock_known_device(monkeypatch)
    monkeypatch.setattr(
        repository,
        "create_auth_session",
        lambda _conn, **kwargs: _session_row(user_id=kwargs["user_id"]),
    )
    notified: dict[str, Any] = {}
    monkeypatch.setattr(
        security_notifications,
        "create_new_device_login_notification",
        lambda _conn, **kwargs: notified.update(kwargs),
    )
    _raw_token, _session, is_new_device = service.create_login_session(
        CONNECTION, user_id="user-1"
    )
    assert is_new_device is False
    assert notified == {}


def test_create_login_session_skips_notification_when_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(service, "get_settings", lambda: _SETTINGS)
    monkeypatch.setattr(
        repository,
        "has_prior_session_with_fingerprint",
        lambda *_a, **_kw: False,
    )
    monkeypatch.setattr(
        repository,
        "create_auth_session",
        lambda _conn, **kwargs: _session_row(user_id=kwargs["user_id"]),
    )
    notified: dict[str, Any] = {}
    monkeypatch.setattr(
        security_notifications,
        "create_new_device_login_notification",
        lambda _conn, **kwargs: notified.update(kwargs),
    )
    _raw_token, _session, is_new_device = service.create_login_session(
        CONNECTION, user_id="user-1", notify_new_device=False
    )
    assert is_new_device is False
    assert notified == {}
