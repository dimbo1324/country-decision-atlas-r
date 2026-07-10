"""apps/api/app/repositories/capabilities.py against a real Postgres
instance (P2-7, Аудит-эпизод 8).

grant_capability's ON CONFLICT (user_id, capability) DO UPDATE reactivation
path and revoke_capability_by_id's WHERE revoked_at IS NULL guard are both
real-constraint behavior a mocked connection can't exercise.
"""

import psycopg
from app.repositories import (
    auth as auth_repo,
    capabilities as capabilities_repo,
)
from typing import Any


def _make_user(connection: psycopg.Connection[Any], suffix: str) -> str:
    user = auth_repo.create_user(
        connection,
        email=f"repo-cap-{suffix}@example.local",
        display_name=f"Repo Cap {suffix}",
        role="user",
    )
    return str(user["id"])


def test_grant_capability_creates_active_grant(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    grantee_id = _make_user(connection, f"{unique_suffix}-grantee")
    grantor_id = _make_user(connection, f"{unique_suffix}-grantor")

    grant = capabilities_repo.grant_capability(
        connection,
        user_id=grantee_id,
        capability="moderate_content",
        granted_by=grantor_id,
        note="integration test grant",
    )

    assert grant["revoked_at"] is None
    assert capabilities_repo.has_active_grant(
        connection, grantee_id, "moderate_content"
    )


def test_has_active_grant_false_when_never_granted(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    user_id = _make_user(connection, unique_suffix)
    assert not capabilities_repo.has_active_grant(
        connection, user_id, "moderate_content"
    )


def test_revoke_capability_by_id_clears_active_grant(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    grantee_id = _make_user(connection, f"{unique_suffix}-grantee")
    grantor_id = _make_user(connection, f"{unique_suffix}-grantor")
    grant = capabilities_repo.grant_capability(
        connection,
        user_id=grantee_id,
        capability="moderate_content",
        granted_by=grantor_id,
        note=None,
    )

    revoked = capabilities_repo.revoke_capability_by_id(
        connection, str(grant["id"])
    )

    assert revoked is not None
    assert revoked["revoked_at"] is not None
    assert not capabilities_repo.has_active_grant(
        connection, grantee_id, "moderate_content"
    )


def test_revoke_capability_by_id_returns_none_when_already_revoked(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    grantee_id = _make_user(connection, f"{unique_suffix}-grantee")
    grantor_id = _make_user(connection, f"{unique_suffix}-grantor")
    grant = capabilities_repo.grant_capability(
        connection,
        user_id=grantee_id,
        capability="moderate_content",
        granted_by=grantor_id,
        note=None,
    )
    capabilities_repo.revoke_capability_by_id(connection, str(grant["id"]))

    second_attempt = capabilities_repo.revoke_capability_by_id(
        connection, str(grant["id"])
    )

    assert second_attempt is None


def test_grant_capability_reactivates_previously_revoked_grant(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    grantee_id = _make_user(connection, f"{unique_suffix}-grantee")
    grantor_id = _make_user(connection, f"{unique_suffix}-grantor")
    first_grant = capabilities_repo.grant_capability(
        connection,
        user_id=grantee_id,
        capability="moderate_content",
        granted_by=grantor_id,
        note="first",
    )
    capabilities_repo.revoke_capability_by_id(
        connection, str(first_grant["id"])
    )
    assert not capabilities_repo.has_active_grant(
        connection, grantee_id, "moderate_content"
    )

    reactivated = capabilities_repo.grant_capability(
        connection,
        user_id=grantee_id,
        capability="moderate_content",
        granted_by=grantor_id,
        note="reactivated",
    )

    assert reactivated["id"] == first_grant["id"]
    assert reactivated["revoked_at"] is None
    assert reactivated["note"] == "reactivated"
    assert capabilities_repo.has_active_grant(
        connection, grantee_id, "moderate_content"
    )


def test_list_capabilities_filters_by_user_id(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    grantor_id = _make_user(connection, f"{unique_suffix}-grantor")
    user_a = _make_user(connection, f"{unique_suffix}-a")
    user_b = _make_user(connection, f"{unique_suffix}-b")
    capabilities_repo.grant_capability(
        connection,
        user_id=user_a,
        capability="moderate_content",
        granted_by=grantor_id,
        note=None,
    )
    capabilities_repo.grant_capability(
        connection,
        user_id=user_b,
        capability="moderate_content",
        granted_by=grantor_id,
        note=None,
    )

    rows = capabilities_repo.list_capabilities(
        connection,
        user_id=user_a,
        capability=None,
        active_only=False,
        limit=10,
        offset=0,
    )

    assert {row["user_id"] for row in rows} == {user_a}


def test_list_capabilities_active_only_excludes_revoked(
    connection: psycopg.Connection[Any], unique_suffix: str
) -> None:
    grantee_id = _make_user(connection, f"{unique_suffix}-grantee")
    grantor_id = _make_user(connection, f"{unique_suffix}-grantor")
    grant = capabilities_repo.grant_capability(
        connection,
        user_id=grantee_id,
        capability="moderate_content",
        granted_by=grantor_id,
        note=None,
    )
    capabilities_repo.revoke_capability_by_id(connection, str(grant["id"]))

    active_rows = capabilities_repo.list_capabilities(
        connection,
        user_id=grantee_id,
        capability=None,
        active_only=True,
        limit=10,
        offset=0,
    )
    all_rows = capabilities_repo.list_capabilities(
        connection,
        user_id=grantee_id,
        capability=None,
        active_only=False,
        limit=10,
        offset=0,
    )

    assert active_rows == []
    assert len(all_rows) == 1


def test_get_capability_by_id_returns_none_for_unknown_id(
    connection: psycopg.Connection[Any],
) -> None:
    assert (
        capabilities_repo.get_capability_by_id(
            connection, "00000000-0000-0000-0000-000000000000"
        )
        is None
    )
