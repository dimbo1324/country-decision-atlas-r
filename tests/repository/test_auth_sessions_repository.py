"""apps/api/app/repositories/auth.py: session lookup and rotation against a
real Postgres instance (P2-7, Аудит-эпизод 8).

get_session_with_user_by_token_hash is the AE-1 JOIN query that replaced
3-4 separate session-validation queries - the grace-period OR clause
(current token vs. previous token within its expiry window) is exactly the
kind of logic that mocked repository tests can't catch a regression in.
"""

import psycopg
from app.repositories import auth as auth_repo
from datetime import UTC, datetime, timedelta
from typing import Any


def _make_user(connection: psycopg.Connection[Any], suffix: str) -> str:
    user = auth_repo.create_user(
        connection,
        email=f"repo-test-{suffix}@example.local",
        display_name=f"Repo Test {suffix}",
        role="user",
    )
    return str(user["id"])


def _make_session(
    connection: psycopg.Connection[Any],
    user_id: str,
    suffix: str,
    *,
    expires_at: datetime | None = None,
) -> tuple[str, str]:
    session = auth_repo.create_auth_session(
        connection,
        user_id=user_id,
        token_hash=f"token-hash-{suffix}",
        expires_at=expires_at or (datetime.now(UTC) + timedelta(hours=1)),
        user_agent_hash=None,
        ip_hash=None,
    )
    return str(session["id"]), f"token-hash-{suffix}"


def test_fresh_token_matches_and_returns_session_and_user(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    user_id = _make_user(connection, unique_suffix)
    _, token_hash = _make_session(connection, user_id, unique_suffix)

    result = auth_repo.get_session_with_user_by_token_hash(
        connection, token_hash
    )

    assert result is not None
    assert result["matched_current_token"] is True
    assert result["is_revoked"] is False
    assert result["is_expired"] is False
    assert result["user"]["id"] == user_id
    assert result["session"]["user_id"] == user_id


def test_unknown_token_returns_none(
    connection: psycopg.Connection[Any],
) -> None:
    assert (
        auth_repo.get_session_with_user_by_token_hash(
            connection, "no-such-token-hash"
        )
        is None
    )


def test_revoked_session_reports_is_revoked_true(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    user_id = _make_user(connection, unique_suffix)
    session_id, token_hash = _make_session(connection, user_id, unique_suffix)

    revoked = auth_repo.revoke_session(connection, session_id, user_id)
    assert revoked is not None

    result = auth_repo.get_session_with_user_by_token_hash(
        connection, token_hash
    )
    assert result is not None
    assert result["is_revoked"] is True


def test_expired_session_reports_is_expired_true(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    user_id = _make_user(connection, unique_suffix)
    _, token_hash = _make_session(
        connection,
        user_id,
        unique_suffix,
        expires_at=datetime.now(UTC) - timedelta(hours=1),
    )

    result = auth_repo.get_session_with_user_by_token_hash(
        connection, token_hash
    )
    assert result is not None
    assert result["is_expired"] is True


def test_rotate_session_token_updates_current_token(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    user_id = _make_user(connection, unique_suffix)
    session_id, old_token_hash = _make_session(
        connection, user_id, unique_suffix
    )
    new_token_hash = f"token-hash-{unique_suffix}-rotated"

    auth_repo.rotate_session_token(
        connection,
        session_id,
        new_token_hash=new_token_hash,
        previous_token_hash=old_token_hash,
        previous_token_expires_at=datetime.now(UTC) + timedelta(minutes=5),
    )

    result = auth_repo.get_session_with_user_by_token_hash(
        connection, new_token_hash
    )
    assert result is not None
    assert result["matched_current_token"] is True


def test_previous_token_matches_within_grace_period(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    user_id = _make_user(connection, unique_suffix)
    session_id, old_token_hash = _make_session(
        connection, user_id, unique_suffix
    )
    new_token_hash = f"token-hash-{unique_suffix}-rotated"

    auth_repo.rotate_session_token(
        connection,
        session_id,
        new_token_hash=new_token_hash,
        previous_token_hash=old_token_hash,
        previous_token_expires_at=datetime.now(UTC) + timedelta(minutes=5),
    )

    result = auth_repo.get_session_with_user_by_token_hash(
        connection, old_token_hash
    )
    assert result is not None
    assert result["matched_current_token"] is False
    assert result["session"]["id"] == session_id


def test_previous_token_past_grace_period_does_not_match(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    user_id = _make_user(connection, unique_suffix)
    session_id, old_token_hash = _make_session(
        connection, user_id, unique_suffix
    )
    new_token_hash = f"token-hash-{unique_suffix}-rotated"

    auth_repo.rotate_session_token(
        connection,
        session_id,
        new_token_hash=new_token_hash,
        previous_token_hash=old_token_hash,
        previous_token_expires_at=datetime.now(UTC) - timedelta(minutes=5),
    )

    assert (
        auth_repo.get_session_with_user_by_token_hash(
            connection, old_token_hash
        )
        is None
    )
