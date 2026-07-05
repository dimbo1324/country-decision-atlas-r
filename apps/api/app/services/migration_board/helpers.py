import re
from app.core.auth import CurrentUser
from app.core.errors import api_error
from app.repositories.analytics import insert_analytics_event
from app.repositories.audit import insert_audit_event
from app.services.feature_flags import (
    ensure_feature_enabled as _ensure_feature_enabled,
)
from app.services.methodology_config import get_active_methodology_config
from psycopg import Connection
from typing import Any
from uuid import UUID


BOARD_FEATURE_KEY = "migration_board_enabled"
MATCHING_FEATURE_KEY = "companion_matching_enabled"
CONTACT_FEATURE_KEY = "contact_requests_enabled"
PUBLIC_LISTING_FEATURE_KEY = "migration_board_public_listing_enabled"
MODERATION_FEATURE_KEY = "migration_board_moderation_enabled"
ALLOWED_TAGS = {
    "pets",
    "children",
    "remote_work",
    "business",
    "study",
    "documents",
    "housing",
    "tax",
    "banking",
    "language_exchange",
    "safety",
    "low_budget",
}
ALLOWED_TIMELINE_WINDOWS = {
    "0_3_months",
    "3_6_months",
    "6_12_months",
    "12_plus_months",
    "unknown",
}
ALLOWED_BUDGET_RANGES = {"low", "medium", "high", "undisclosed"}
ALLOWED_HOUSEHOLD_TYPES = {"solo", "couple", "family", "friends", "undisclosed"}
ALLOWED_MIGRATION_STAGES = {
    "researching",
    "preparing_documents",
    "applying",
    "waiting_decision",
    "relocating_soon",
    "already_relocated",
    "on_hold",
}
ALLOWED_COMPANION_GOALS = {
    "info_exchange",
    "travel_together",
    "housing_search",
    "document_support",
    "study_group",
    "business_network",
    "family_network",
    "other",
}
ALLOWED_VISIBILITIES = {"public", "members_only", "private"}
ALLOWED_REPORT_REASONS = {
    "spam",
    "scam",
    "abuse",
    "privacy",
    "misleading",
    "unsafe_contact",
    "off_topic",
    "other",
}
PII_PATTERNS = (
    re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE),
    re.compile(r"(?:\+?\d[\s().-]*){8,}"),
    re.compile(r"(?<!\w)@[A-Za-z0-9_]{4,32}\b"),
    re.compile(r"https?://|www\.", re.IGNORECASE),
)


def ensure_feature_enabled(
    connection: Connection[Any], feature_key: str
) -> None:
    _ensure_feature_enabled(
        connection,
        feature_key,
        "This migration board feature is currently disabled.",
    )


def max_active_posts(connection: Connection[Any]) -> int:
    return get_active_methodology_config(connection).board.max_active_posts


def max_contact_requests_per_day(connection: Connection[Any]) -> int:
    return get_active_methodology_config(
        connection
    ).board.max_contact_requests_per_day


def max_reports_per_day(connection: Connection[Any]) -> int:
    return get_active_methodology_config(connection).board.max_reports_per_day


def auto_hide_report_threshold(connection: Connection[Any]) -> int:
    return get_active_methodology_config(
        connection
    ).board.auto_hide_report_threshold


def _reject_public_pii(title: str, summary: str) -> None:
    text = f"{title}\n{summary}"
    if any(pattern.search(text) for pattern in PII_PATTERNS):
        raise api_error(
            422,
            "pii_not_allowed",
            "Public migration board text cannot include direct contact details.",
            {},
        )


def _require_submit_ready(post: dict[str, Any]) -> None:
    _reject_public_pii(str(post["title"]), str(post["summary"]))
    if (
        not post["risk_acknowledged"]
        or not post["legal_disclaimer_acknowledged"]
    ):
        raise api_error(
            422,
            "acknowledgements_required",
            "Risk and legal acknowledgements are required before publication.",
            {},
        )


def _country_ref(row: dict[str, Any], prefix: str) -> dict[str, Any]:
    return {
        "id": row[f"{prefix}_country_id"],
        "slug": row[f"{prefix}_country_slug"],
        "name": row[f"{prefix}_country_name"],
    }


def _route_ref(row: dict[str, Any]) -> dict[str, Any] | None:
    if not row.get("route_id"):
        return None
    return {
        "id": row["route_id"],
        "slug": row["route_slug"],
        "title": row["route_title"],
    }


def _scenario_ref(row: dict[str, Any]) -> dict[str, Any] | None:
    if not row.get("scenario_slug"):
        return None
    return {
        "slug": row["scenario_slug"],
        "label": row.get("scenario_label") or row["scenario_slug"],
    }


def _persona_ref(row: dict[str, Any]) -> dict[str, Any] | None:
    if not row.get("persona_slug"):
        return None
    return {
        "slug": row["persona_slug"],
        "label": row.get("persona_label") or row["persona_slug"],
    }


def _public_post(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "title": row["title"],
        "summary": row["summary"],
        "author": {"display_name": row.get("author_display_name") or "Member"},
        "destination_country": _country_ref(row, "destination"),
        "origin_country": _country_ref(row, "origin")
        if row.get("origin_country_id")
        else None,
        "route": _route_ref(row),
        "scenario": _scenario_ref(row),
        "persona": _persona_ref(row),
        "target_city": row.get("target_city"),
        "target_month": row.get("target_month"),
        "timeline_window": row["timeline_window"],
        "budget_range": row["budget_range"],
        "household_type": row["household_type"],
        "migration_stage": row["migration_stage"],
        "companion_goal": row["companion_goal"],
        "preferred_language": row["preferred_language"],
        "visibility": row["visibility"],
        "contact_requests_enabled": row["contact_requests_enabled"],
        "tags": list(row.get("tags") or []),
        "published_at": row.get("published_at"),
    }


def _public_detail(row: dict[str, Any]) -> dict[str, Any]:
    return {**_public_post(row), "created_at": row["created_at"]}


def _my_post(row: dict[str, Any]) -> dict[str, Any]:
    return {
        **_public_detail(row),
        "status": row["status"],
        "moderation_status": row["moderation_status"],
        "risk_acknowledged": row["risk_acknowledged"],
        "legal_disclaimer_acknowledged": row["legal_disclaimer_acknowledged"],
        "updated_at": row["updated_at"],
        "submitted_at": row.get("submitted_at"),
        "archived_at": row.get("archived_at"),
        "rejected_at": row.get("rejected_at"),
        "moderation_reason": row.get("moderation_reason"),
    }


def _admin_post(row: dict[str, Any]) -> dict[str, Any]:
    return {
        **_my_post(row),
        "user_id": row["user_id"],
        "author_display_name": row.get("author_display_name") or "Member",
        "moderated_by": row.get("moderated_by"),
        "moderated_at": row.get("moderated_at"),
    }


def _contact_request(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "post_id": row["post_id"],
        "post_title": row["post_title"],
        "from_user_display_name": row.get("from_user_display_name") or "Member",
        "to_user_display_name": row.get("to_user_display_name") or "Member",
        "message": row["message"],
        "status": row["status"],
        "created_at": row["created_at"],
        "responded_at": row.get("responded_at"),
        "cancelled_at": row.get("cancelled_at"),
        "response_note": row.get("response_note"),
    }


def _report(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "post_id": row.get("post_id"),
        "contact_request_id": row.get("contact_request_id"),
        "reason": row["reason"],
        "details": row.get("details"),
        "status": row["status"],
        "created_at": row["created_at"],
        "reviewed_at": row.get("reviewed_at"),
        "resolution_note": row.get("resolution_note"),
    }


def _safe_filter_metadata(filters: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in filters.items() if value is not None}


def _safe_post_metadata(post: dict[str, Any]) -> dict[str, Any]:
    return {
        "destination_country_slug": post.get("destination_country_slug"),
        "origin_country_slug": post.get("origin_country_slug"),
        "route_id": post.get("route_id"),
        "scenario_slug": post.get("scenario_slug"),
        "persona_slug": post.get("persona_slug"),
        "timeline_window": post.get("timeline_window"),
        "companion_goal": post.get("companion_goal"),
    }


def _total(rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    return int(rows[0].get("total_count") or len(rows))


def _audit(
    connection: Connection[Any],
    entity: dict[str, Any],
    action: str,
    current_user: CurrentUser,
    changes: dict[str, Any],
) -> None:
    entity_id = entity.get("id")
    if not entity_id:
        return
    insert_audit_event(
        connection,
        entity_type="migration_board",
        entity_id=UUID(str(entity_id)),
        action=action,
        changed_by=current_user.id,
        changes=changes,
    )


def _track_event(
    connection: Connection[Any],
    event_type: str,
    *,
    entity_id: str | None = None,
    metadata: dict[str, Any],
) -> None:
    insert_analytics_event(
        connection,
        session_hash="migration_board_runtime_0000000001",
        event_type=event_type,
        source="api",
        path=None,
        locale=None,
        country_slug=metadata.get("destination_country_slug"),
        scenario_slug=metadata.get("scenario_slug"),
        persona_slug=metadata.get("persona_slug"),
        route_id=UUID(str(metadata["route_id"]))
        if metadata.get("route_id")
        else None,
        entity_type="migration_board_post" if entity_id else None,
        entity_id=UUID(str(entity_id)) if entity_id else None,
        metadata=metadata,
    )
