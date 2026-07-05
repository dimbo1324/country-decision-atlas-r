from app.core.auth import CurrentUser
from app.core.errors import api_error
from app.repositories import capabilities as repository
from app.repositories.audit import insert_audit_event
from app.services import admin_users
from collections.abc import Iterable
from psycopg import Connection
from typing import Any
from uuid import UUID


MODERATOR_BOARD = "moderator.board"
MODERATOR_METRICS = "moderator.metrics"
MODERATOR_COMMUNITY = "moderator.community"
AUTHOR_METRICS = "author.metrics"
CONTRIBUTOR_COUNTRIES = "contributor.countries"

KNOWN_CAPABILITIES = frozenset(
    {
        MODERATOR_BOARD,
        MODERATOR_METRICS,
        MODERATOR_COMMUNITY,
        AUTHOR_METRICS,
        CONTRIBUTOR_COUNTRIES,
    }
)

_FULL_ACCESS_ROLES = frozenset({"admin", "owner"})
_MODERATOR_ROLE = "moderator"
_MODERATOR_CAPABILITY_PREFIX = "moderator."


def has_capability(
    connection: Connection[Any], user: CurrentUser, capability: str
) -> bool:
    if user.role in _FULL_ACCESS_ROLES:
        return True
    if user.role == _MODERATOR_ROLE and capability.startswith(
        _MODERATOR_CAPABILITY_PREFIX
    ):
        return True
    return repository.has_active_grant(connection, user.id, capability)


def assert_no_moderation_conflict(
    current_user: CurrentUser, involved_user_ids: Iterable[str | None]
) -> None:
    if current_user.id in {uid for uid in involved_user_ids if uid}:
        raise api_error(
            403,
            "moderation_conflict_of_interest",
            "Moderators cannot act on objects where they are a party.",
            {},
        )


def grant_capability(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    user_id: str,
    capability: str,
    note: str | None,
) -> dict[str, Any]:
    _ensure_known_capability(capability)
    admin_users.get_user_or_404(connection, user_id)
    row = repository.grant_capability(
        connection,
        user_id=user_id,
        capability=capability,
        granted_by=current_user.id,
        note=note,
    )
    _audit(connection, row, "granted", current_user)
    return row


def revoke_capability(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    capability_id: str,
) -> dict[str, Any]:
    row = repository.revoke_capability_by_id(connection, capability_id)
    if row is None:
        raise api_error(
            404,
            "capability_grant_not_found",
            "Capability grant was not found or already revoked.",
            {},
        )
    _audit(connection, row, "revoked", current_user)
    return row


def list_capabilities(
    connection: Connection[Any],
    *,
    user_id: str | None,
    capability: str | None,
    active_only: bool,
    limit: int,
    offset: int,
) -> dict[str, Any]:
    rows = repository.list_capabilities(
        connection,
        user_id=user_id,
        capability=capability,
        active_only=active_only,
        limit=limit,
        offset=offset,
    )
    return {"items": rows, "total": _total(rows)}


def _ensure_known_capability(capability: str) -> None:
    if capability not in KNOWN_CAPABILITIES:
        raise api_error(
            422,
            "unknown_capability",
            "Capability is not recognized.",
            {
                "capability": capability,
                "known_capabilities": sorted(KNOWN_CAPABILITIES),
            },
        )


def _audit(
    connection: Connection[Any],
    row: dict[str, Any],
    action: str,
    current_user: CurrentUser,
) -> None:
    insert_audit_event(
        connection,
        entity_type="user_capability",
        entity_id=UUID(str(row["id"])),
        action=action,
        changed_by=current_user.id,
        changes={"user_id": row["user_id"], "capability": row["capability"]},
    )


def _total(rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    return int(rows[0].get("total_count") or len(rows))
