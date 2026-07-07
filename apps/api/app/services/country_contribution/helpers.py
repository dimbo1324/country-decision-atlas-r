import re
from app.core.auth import CurrentUser
from app.core.errors import api_error
from app.repositories import country_contribution as repository
from app.repositories.audit import insert_audit_event
from app.services.feature_flags import (
    ensure_feature_enabled as _ensure_feature_enabled,
)
from psycopg import Connection
from typing import Any
from uuid import UUID


FEATURE_KEY = "country_contribution_enabled"
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ISO2_PATTERN = re.compile(r"^[A-Z]{2}$")
ISO3_PATTERN = re.compile(r"^[A-Z]{3}$")
EDITOR_ROLES = frozenset({"editor", "admin", "owner"})
SCENARIO_CRITERIA = (
    "legalization_score",
    "long_term_status_score",
    "cost_of_living_score",
    "safety_score",
    "business_score",
    "legal_stability_score",
    "source_quality_score",
)
CONFIDENCE_RANK = {"low": 0, "medium": 1, "high": 2}


def ensure_feature_enabled(connection: Connection[Any]) -> None:
    _ensure_feature_enabled(
        connection,
        FEATURE_KEY,
        "Country contribution is currently disabled.",
    )


def get_owner_proposal_or_404(
    connection: Connection[Any], proposal_id: str, proposer_user_id: str
) -> dict[str, Any]:
    proposal = repository.get_proposal_for_owner(
        connection, proposal_id, proposer_user_id
    )
    if proposal is None:
        raise api_error(
            404,
            "country_proposal_not_found",
            "Country proposal was not found.",
            {},
        )
    return proposal


def get_proposal_or_404(
    connection: Connection[Any], proposal_id: str
) -> dict[str, Any]:
    proposal = repository.get_proposal_by_id(connection, proposal_id)
    if proposal is None:
        raise api_error(
            404,
            "country_proposal_not_found",
            "Country proposal was not found.",
            {},
        )
    return proposal


def require_draft_editable(proposal: dict[str, Any]) -> None:
    if proposal["status"] != "draft":
        raise api_error(
            409,
            "country_proposal_not_editable",
            "Country proposal content can only be edited while it is a draft.",
            {"status": proposal["status"]},
        )


def validate_slug(slug: str) -> None:
    if not SLUG_PATTERN.match(slug):
        raise api_error(
            422,
            "invalid_slug",
            "Slug must be lowercase alphanumeric segments separated by hyphens.",
            {},
        )


def validate_iso_codes(iso2: str, iso3: str) -> None:
    if not ISO2_PATTERN.match(iso2) or not ISO3_PATTERN.match(iso3):
        raise api_error(
            422,
            "invalid_iso_code",
            "iso2 must be two uppercase letters and iso3 three uppercase letters.",
            {},
        )


def _proposal_view(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "proposer_user_id": row["proposer_user_id"],
        "country_id": row["country_id"],
        "slug": row["slug"],
        "name_en": row["name_en"],
        "name_ru": row["name_ru"],
        "iso2": row["iso2"],
        "iso3": row["iso3"],
        "justification": row["justification"],
        "status": row["status"],
        "curator_user_id": row.get("curator_user_id"),
        "readiness_snapshot": row.get("readiness_snapshot"),
        "moderated_by": row.get("moderated_by"),
        "moderated_at": row.get("moderated_at"),
        "moderation_reason": row.get("moderation_reason"),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "published_at": row.get("published_at"),
        "country_is_active": row["country_is_active"],
        "country_is_demo": row["country_is_demo"],
    }


def _total(rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    return int(rows[0].get("total_count") or len(rows))


def _audit(
    connection: Connection[Any],
    proposal_id: str,
    action: str,
    changed_by: str,
    changes: dict[str, Any],
) -> None:
    insert_audit_event(
        connection,
        entity_type="country_proposal",
        entity_id=UUID(str(proposal_id)),
        action=action,
        changed_by=changed_by,
        changes=changes,
    )


def require_curator_role(current_user: CurrentUser) -> None:
    if current_user.role not in EDITOR_ROLES:
        raise api_error(
            403,
            "insufficient_role",
            "Only editors can curate country proposals.",
            {"required_roles": sorted(EDITOR_ROLES)},
        )


def weakest_confidence(confidences: list[str]) -> str:
    return min(confidences, key=lambda value: CONFIDENCE_RANK.get(value, 0))
