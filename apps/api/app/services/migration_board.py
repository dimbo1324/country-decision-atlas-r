from app.core.auth import CurrentUser
from app.core.errors import api_error
from app.repositories import migration_board as repository
from app.repositories.analytics import insert_analytics_event
from app.repositories.audit import insert_audit_event
from app.services.feature_flags import is_feature_enabled_by_key
from psycopg import Connection
import re
from typing import Any
from uuid import UUID


BOARD_FEATURE_KEY = "migration_board_enabled"
MATCHING_FEATURE_KEY = "companion_matching_enabled"
CONTACT_FEATURE_KEY = "contact_requests_enabled"
PUBLIC_LISTING_FEATURE_KEY = "migration_board_public_listing_enabled"
MODERATION_FEATURE_KEY = "migration_board_moderation_enabled"
MAX_ACTIVE_POSTS = 5
MAX_CONTACT_REQUESTS_PER_DAY = 20
MAX_REPORTS_PER_DAY = 20
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


def ensure_feature_enabled(connection: Connection[Any], feature_key: str) -> None:
    if not is_feature_enabled_by_key(connection, feature_key):
        raise api_error(
            403,
            "feature_disabled",
            "This migration board feature is currently disabled.",
            {"feature_key": feature_key},
        )


def list_public_posts(
    connection: Connection[Any],
    *,
    current_user: CurrentUser | None,
    filters: dict[str, Any],
    limit: int,
    offset: int,
) -> dict[str, Any]:
    ensure_feature_enabled(connection, BOARD_FEATURE_KEY)
    ensure_feature_enabled(connection, PUBLIC_LISTING_FEATURE_KEY)
    rows = repository.list_public_posts(
        connection,
        filters=filters,
        include_members_only=current_user is not None,
        include_private_for_user_id=current_user.id
        if current_user is not None
        else None,
        limit=limit,
        offset=offset,
    )
    _track_event(
        connection,
        "migration_board_list_viewed",
        metadata=_safe_filter_metadata(filters),
    )
    return {
        "items": [_public_post(row) for row in rows],
        "total": _total(rows),
        "limit": limit,
        "offset": offset,
    }


def get_public_post(
    connection: Connection[Any], *, post_id: str, current_user: CurrentUser | None
) -> dict[str, Any]:
    ensure_feature_enabled(connection, BOARD_FEATURE_KEY)
    post = repository.get_post_by_id(connection, post_id)
    if post is None or not _can_view_post(post, current_user):
        raise api_error(
            404, "post_not_found", "Migration board post was not found.", {}
        )
    _track_event(
        connection,
        "migration_board_post_viewed",
        entity_id=post_id,
        metadata={"destination_country_slug": post.get("destination_country_slug")},
    )
    return _public_detail(post)


def create_user_post(
    connection: Connection[Any], *, current_user: CurrentUser, payload: Any
) -> dict[str, Any]:
    ensure_feature_enabled(connection, BOARD_FEATURE_KEY)
    if (
        repository.count_user_active_posts(connection, current_user.id)
        >= MAX_ACTIVE_POSTS
    ):
        raise api_error(
            429,
            "active_post_limit_exceeded",
            "You have reached the active migration board post limit.",
            {"limit": MAX_ACTIVE_POSTS},
        )
    refs = _validate_post_payload(connection, payload)
    _reject_public_pii(payload.title, payload.summary)
    tags = _validate_tags(payload.tags)
    destination_country_id = refs["destination_country_id"]
    if destination_country_id is None:
        raise api_error(
            422,
            "destination_country_required",
            "Destination country is required.",
            {},
        )
    post = repository.create_post(
        connection,
        user_id=current_user.id,
        destination_country_id=destination_country_id,
        origin_country_id=refs["origin_country_id"],
        route_id=payload.route_id,
        scenario_slug=payload.scenario_slug,
        persona_slug=payload.persona_slug,
        title=payload.title,
        summary=payload.summary,
        target_city=payload.target_city,
        target_month=payload.target_month,
        timeline_window=payload.timeline_window,
        budget_range=payload.budget_range,
        household_type=payload.household_type,
        migration_stage=payload.migration_stage,
        companion_goal=payload.companion_goal,
        preferred_language=payload.preferred_language,
        visibility=payload.visibility,
        risk_acknowledged=payload.risk_acknowledged,
        legal_disclaimer_acknowledged=payload.legal_disclaimer_acknowledged,
        contact_requests_enabled=payload.contact_requests_enabled,
        tags=tags,
    )
    _audit(connection, post, "created", current_user, {"status": {"new": "draft"}})
    _track_event(
        connection,
        "migration_board_post_created",
        entity_id=post["id"],
        metadata=_safe_post_metadata(post),
    )
    return _my_post(post)


def update_user_post(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    post_id: str,
    payload: Any,
) -> dict[str, Any]:
    ensure_feature_enabled(connection, BOARD_FEATURE_KEY)
    existing = _get_owner_post_or_404(connection, post_id, current_user.id)
    if existing["status"] not in {
        "draft",
        "review",
        "published",
        "rejected",
        "archived",
    }:
        raise api_error(409, "invalid_post_status", "Post cannot be updated.", {})
    refs = _validate_post_payload(connection, payload, existing=existing)
    title = payload.title if payload.title is not None else existing["title"]
    summary = payload.summary if payload.summary is not None else existing["summary"]
    _reject_public_pii(title, summary)
    tags = _validate_tags(payload.tags) if payload.tags is not None else None
    reset_to_review = existing["status"] == "published" and _is_significant_edit(
        payload
    )
    updated = repository.update_post(
        connection,
        post_id=post_id,
        destination_country_id=refs["destination_country_id"],
        origin_country_id=refs["origin_country_id"],
        route_id=payload.route_id,
        scenario_slug=payload.scenario_slug,
        persona_slug=payload.persona_slug,
        title=payload.title,
        summary=payload.summary,
        target_city=payload.target_city,
        target_month=payload.target_month,
        timeline_window=payload.timeline_window,
        budget_range=payload.budget_range,
        household_type=payload.household_type,
        migration_stage=payload.migration_stage,
        companion_goal=payload.companion_goal,
        preferred_language=payload.preferred_language,
        visibility=payload.visibility,
        risk_acknowledged=payload.risk_acknowledged,
        legal_disclaimer_acknowledged=payload.legal_disclaimer_acknowledged,
        contact_requests_enabled=payload.contact_requests_enabled,
        reset_to_review=reset_to_review,
        tags=tags,
    )
    if updated is None:
        raise api_error(
            404, "post_not_found", "Migration board post was not found.", {}
        )
    _audit(
        connection,
        updated,
        "updated",
        current_user,
        _diff_for_update(existing, updated),
    )
    return _my_post(updated)


def submit_user_post(
    connection: Connection[Any], *, current_user: CurrentUser, post_id: str
) -> dict[str, Any]:
    ensure_feature_enabled(connection, BOARD_FEATURE_KEY)
    post = _get_owner_post_or_404(connection, post_id, current_user.id)
    _require_submit_ready(post)
    updated = repository.submit_post_for_review(connection, post_id)
    if updated is None:
        raise api_error(
            409, "invalid_status_transition", "Post cannot be submitted.", {}
        )
    _audit(
        connection,
        updated,
        "submitted_for_review",
        current_user,
        {"status": {"old": post["status"], "new": "review"}},
    )
    _track_event(
        connection,
        "migration_board_post_submitted",
        entity_id=post_id,
        metadata=_safe_post_metadata(updated),
    )
    return _my_post(updated)


def archive_user_post(
    connection: Connection[Any], *, current_user: CurrentUser, post_id: str
) -> dict[str, Any]:
    ensure_feature_enabled(connection, BOARD_FEATURE_KEY)
    post = _get_owner_post_or_404(connection, post_id, current_user.id)
    updated = repository.archive_post(connection, post_id)
    if updated is None:
        raise api_error(
            409, "invalid_status_transition", "Post cannot be archived.", {}
        )
    _audit(
        connection,
        updated,
        "archived",
        current_user,
        {"status": {"old": post["status"], "new": "archived"}},
    )
    return _my_post(updated)


def list_my_posts(
    connection: Connection[Any], current_user: CurrentUser
) -> dict[str, Any]:
    ensure_feature_enabled(connection, BOARD_FEATURE_KEY)
    rows = repository.list_user_posts(connection, current_user.id)
    return {"items": [_my_post(row) for row in rows], "total": len(rows)}


def get_my_post(
    connection: Connection[Any], *, current_user: CurrentUser, post_id: str
) -> dict[str, Any]:
    ensure_feature_enabled(connection, BOARD_FEATURE_KEY)
    return _my_post(_get_owner_post_or_404(connection, post_id, current_user.id))


def list_posts_for_moderation(
    connection: Connection[Any], *, status: str | None, limit: int, offset: int
) -> dict[str, Any]:
    ensure_feature_enabled(connection, BOARD_FEATURE_KEY)
    ensure_feature_enabled(connection, MODERATION_FEATURE_KEY)
    rows = repository.list_posts_for_moderation(
        connection, status=status, limit=limit, offset=offset
    )
    return {"items": [_admin_post(row) for row in rows], "total": _total(rows)}


def get_post_for_moderation(
    connection: Connection[Any], post_id: str
) -> dict[str, Any]:
    ensure_feature_enabled(connection, BOARD_FEATURE_KEY)
    post = repository.get_post_by_id(connection, post_id)
    if post is None:
        raise api_error(
            404, "post_not_found", "Migration board post was not found.", {}
        )
    return _admin_post(post)


def approve_post(
    connection: Connection[Any], *, current_user: CurrentUser, post_id: str
) -> dict[str, Any]:
    ensure_feature_enabled(connection, BOARD_FEATURE_KEY)
    ensure_feature_enabled(connection, MODERATION_FEATURE_KEY)
    post = repository.get_post_by_id(connection, post_id)
    if post is None:
        raise api_error(
            404, "post_not_found", "Migration board post was not found.", {}
        )
    _require_submit_ready(post)
    updated = repository.publish_post(
        connection, post_id=post_id, moderator_user_id=current_user.id
    )
    if updated is None:
        raise api_error(
            409, "invalid_status_transition", "Post cannot be approved.", {}
        )
    _audit(
        connection,
        updated,
        "published",
        current_user,
        {"status": {"old": post["status"], "new": "published"}},
    )
    return _admin_post(updated)


def reject_post(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    post_id: str,
    reason: str | None,
) -> dict[str, Any]:
    ensure_feature_enabled(connection, BOARD_FEATURE_KEY)
    ensure_feature_enabled(connection, MODERATION_FEATURE_KEY)
    post = repository.get_post_by_id(connection, post_id)
    if post is None:
        raise api_error(
            404, "post_not_found", "Migration board post was not found.", {}
        )
    updated = repository.reject_post(
        connection, post_id=post_id, moderator_user_id=current_user.id, reason=reason
    )
    if updated is None:
        raise api_error(
            409, "invalid_status_transition", "Post cannot be rejected.", {}
        )
    _audit(connection, updated, "rejected", current_user, {"reason": {"new": reason}})
    return _admin_post(updated)


def hide_post(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    post_id: str,
    reason: str | None,
) -> dict[str, Any]:
    ensure_feature_enabled(connection, BOARD_FEATURE_KEY)
    ensure_feature_enabled(connection, MODERATION_FEATURE_KEY)
    post = repository.get_post_by_id(connection, post_id)
    if post is None:
        raise api_error(
            404, "post_not_found", "Migration board post was not found.", {}
        )
    updated = repository.hide_post(
        connection, post_id=post_id, moderator_user_id=current_user.id, reason=reason
    )
    if updated is None:
        raise api_error(409, "invalid_status_transition", "Post cannot be hidden.", {})
    _audit(connection, updated, "hidden", current_user, {"reason": {"new": reason}})
    return _admin_post(updated)


def create_contact_request(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    post_id: str,
    message: str,
) -> dict[str, Any]:
    ensure_feature_enabled(connection, BOARD_FEATURE_KEY)
    ensure_feature_enabled(connection, CONTACT_FEATURE_KEY)
    post = repository.get_post_by_id(connection, post_id)
    if post is None or not _can_receive_contact_request(post):
        raise api_error(
            404, "post_not_found", "Migration board post was not found.", {}
        )
    if post["user_id"] == current_user.id:
        raise api_error(
            422, "self_contact_not_allowed", "You cannot contact yourself.", {}
        )
    if repository.is_user_blocked(
        connection, user_a_id=current_user.id, user_b_id=post["user_id"]
    ):
        raise api_error(403, "contact_blocked", "Contact request is blocked.", {})
    if repository.pending_contact_request_exists(
        connection, post_id=post_id, from_user_id=current_user.id
    ):
        raise api_error(
            409,
            "duplicate_pending_contact_request",
            "A pending request already exists.",
            {},
        )
    if (
        repository.count_contact_requests_created_since(
            connection, user_id=current_user.id, since_sql="1 day"
        )
        >= MAX_CONTACT_REQUESTS_PER_DAY
    ):
        raise api_error(
            429,
            "contact_request_limit_exceeded",
            "Daily contact request limit exceeded.",
            {"limit": MAX_CONTACT_REQUESTS_PER_DAY},
        )
    request = repository.create_contact_request(
        connection,
        post_id=post_id,
        from_user_id=current_user.id,
        to_user_id=post["user_id"],
        message=message,
    )
    _audit(
        connection,
        post,
        "contact_request_created",
        current_user,
        {"contact_request_id": {"new": request["id"]}},
    )
    _track_event(
        connection,
        "migration_board_contact_request_created",
        entity_id=post_id,
        metadata=_safe_post_metadata(post),
    )
    return _contact_request(request)


def list_incoming_requests(
    connection: Connection[Any], current_user: CurrentUser
) -> dict[str, Any]:
    ensure_feature_enabled(connection, BOARD_FEATURE_KEY)
    rows = repository.list_incoming_contact_requests(connection, current_user.id)
    return {"items": [_contact_request(row) for row in rows], "total": len(rows)}


def list_outgoing_requests(
    connection: Connection[Any], current_user: CurrentUser
) -> dict[str, Any]:
    ensure_feature_enabled(connection, BOARD_FEATURE_KEY)
    rows = repository.list_outgoing_contact_requests(connection, current_user.id)
    return {"items": [_contact_request(row) for row in rows], "total": len(rows)}


def accept_contact_request(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    request_id: str,
    response_note: str | None,
) -> dict[str, Any]:
    return _change_contact_request(
        connection,
        current_user=current_user,
        request_id=request_id,
        status="accepted",
        response_note=response_note,
        expected_user_field="to_user_id",
        action="accepted",
    )


def decline_contact_request(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    request_id: str,
    response_note: str | None,
) -> dict[str, Any]:
    return _change_contact_request(
        connection,
        current_user=current_user,
        request_id=request_id,
        status="declined",
        response_note=response_note,
        expected_user_field="to_user_id",
        action="declined",
    )


def cancel_contact_request(
    connection: Connection[Any], *, current_user: CurrentUser, request_id: str
) -> dict[str, Any]:
    return _change_contact_request(
        connection,
        current_user=current_user,
        request_id=request_id,
        status="cancelled",
        response_note=None,
        expected_user_field="from_user_id",
        action="cancelled",
    )


def report_post(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    post_id: str,
    reason: str,
    details: str | None,
) -> dict[str, Any]:
    ensure_feature_enabled(connection, BOARD_FEATURE_KEY)
    _validate_report(reason, details)
    if repository.get_post_by_id(connection, post_id) is None:
        raise api_error(
            404, "post_not_found", "Migration board post was not found.", {}
        )
    return _create_report(
        connection,
        current_user=current_user,
        post_id=post_id,
        contact_request_id=None,
        reason=reason,
        details=details,
    )


def report_contact_request(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    request_id: str,
    reason: str,
    details: str | None,
) -> dict[str, Any]:
    ensure_feature_enabled(connection, BOARD_FEATURE_KEY)
    _validate_report(reason, details)
    request = repository.get_contact_request_by_id(connection, request_id)
    if request is None or current_user.id not in {
        request["from_user_id"],
        request["to_user_id"],
    }:
        raise api_error(
            404, "contact_request_not_found", "Contact request was not found.", {}
        )
    return _create_report(
        connection,
        current_user=current_user,
        post_id=None,
        contact_request_id=request_id,
        reason=reason,
        details=details,
    )


def list_reports_for_moderation(
    connection: Connection[Any], *, status: str | None, limit: int, offset: int
) -> dict[str, Any]:
    ensure_feature_enabled(connection, BOARD_FEATURE_KEY)
    rows = repository.list_reports_for_moderation(
        connection, status=status, limit=limit, offset=offset
    )
    return {"items": [_report(row) for row in rows], "total": _total(rows)}


def resolve_report(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    report_id: str,
    resolution_note: str | None,
    hide_related_post: bool,
) -> dict[str, Any]:
    return _review_report(
        connection,
        current_user=current_user,
        report_id=report_id,
        status="resolved",
        resolution_note=resolution_note,
        hide_related_post=hide_related_post,
    )


def dismiss_report(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    report_id: str,
    resolution_note: str | None,
) -> dict[str, Any]:
    return _review_report(
        connection,
        current_user=current_user,
        report_id=report_id,
        status="dismissed",
        resolution_note=resolution_note,
        hide_related_post=False,
    )


def block_user(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    blocked_user_id: str,
    reason: str | None,
) -> dict[str, Any]:
    ensure_feature_enabled(connection, BOARD_FEATURE_KEY)
    if blocked_user_id == current_user.id:
        raise api_error(422, "self_block_not_allowed", "You cannot block yourself.", {})
    if not repository.user_exists(connection, blocked_user_id):
        raise api_error(404, "user_not_found", "User was not found.", {})
    row = repository.block_user(
        connection,
        blocker_user_id=current_user.id,
        blocked_user_id=blocked_user_id,
        reason=reason,
    )
    _audit(
        connection,
        {"id": blocked_user_id},
        "user_blocked",
        current_user,
        {"blocked_user_id": {"new": blocked_user_id}},
    )
    return row


def unblock_user(
    connection: Connection[Any], *, current_user: CurrentUser, blocked_user_id: str
) -> None:
    ensure_feature_enabled(connection, BOARD_FEATURE_KEY)
    repository.unblock_user(
        connection, blocker_user_id=current_user.id, blocked_user_id=blocked_user_id
    )
    _audit(
        connection,
        {"id": blocked_user_id},
        "user_unblocked",
        current_user,
        {"blocked_user_id": {"old": blocked_user_id}},
    )


def list_blocked_users(
    connection: Connection[Any], current_user: CurrentUser
) -> dict[str, Any]:
    ensure_feature_enabled(connection, BOARD_FEATURE_KEY)
    rows = repository.list_blocked_users(connection, current_user.id)
    return {"items": rows, "total": len(rows)}


def list_companion_matches(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    post_id: str | None,
    limit: int,
) -> dict[str, Any]:
    ensure_feature_enabled(connection, BOARD_FEATURE_KEY)
    ensure_feature_enabled(connection, MATCHING_FEATURE_KEY)
    source = _select_source_post(connection, current_user, post_id)
    rows = repository.list_potential_companion_posts(
        connection, source_post=source, user_id=current_user.id, limit=limit
    )
    _track_event(
        connection,
        "migration_board_match_viewed",
        entity_id=source["id"],
        metadata=_safe_post_metadata(source),
    )
    return {
        "items": [
            {**_public_post(row), "match_reasons": _match_reasons(source, row)}
            for row in rows
        ],
        "total": len(rows),
    }


def _validate_post_payload(
    connection: Connection[Any], payload: Any, existing: dict[str, Any] | None = None
) -> dict[str, str | None]:
    destination_country_id = existing["destination_country_id"] if existing else None
    origin_country_id = existing.get("origin_country_id") if existing else None
    if getattr(payload, "destination_country_slug", None):
        country = repository.get_country_by_slug(
            connection, payload.destination_country_slug
        )
        if country is None:
            raise api_error(
                404,
                "destination_country_not_found",
                "Destination country was not found.",
                {},
            )
        destination_country_id = country["id"]
    if getattr(payload, "origin_country_slug", None):
        country = repository.get_country_by_slug(
            connection, payload.origin_country_slug
        )
        if country is None:
            raise api_error(
                404, "origin_country_not_found", "Origin country was not found.", {}
            )
        origin_country_id = country["id"]
    route_id = getattr(payload, "route_id", None)
    if route_id:
        route = repository.get_route_for_validation(connection, route_id)
        if route is None:
            raise api_error(404, "route_not_found", "Route was not found.", {})
        if route["country_id"] != destination_country_id:
            raise api_error(
                422,
                "route_destination_mismatch",
                "Route must belong to the destination country.",
                {},
            )
    scenario_slug = getattr(payload, "scenario_slug", None)
    if scenario_slug and not repository.scenario_exists(connection, scenario_slug):
        raise api_error(404, "scenario_not_found", "Scenario was not found.", {})
    persona_slug = getattr(payload, "persona_slug", None)
    if persona_slug and not repository.persona_exists(connection, persona_slug):
        raise api_error(404, "persona_not_found", "Persona was not found.", {})
    _validate_enum(getattr(payload, "timeline_window", None), ALLOWED_TIMELINE_WINDOWS)
    _validate_enum(getattr(payload, "budget_range", None), ALLOWED_BUDGET_RANGES)
    _validate_enum(getattr(payload, "household_type", None), ALLOWED_HOUSEHOLD_TYPES)
    _validate_enum(getattr(payload, "migration_stage", None), ALLOWED_MIGRATION_STAGES)
    _validate_enum(getattr(payload, "companion_goal", None), ALLOWED_COMPANION_GOALS)
    _validate_enum(getattr(payload, "visibility", None), ALLOWED_VISIBILITIES)
    if destination_country_id is None:
        raise api_error(
            422,
            "destination_country_required",
            "Destination country is required.",
            {},
        )
    return {
        "destination_country_id": str(destination_country_id),
        "origin_country_id": str(origin_country_id) if origin_country_id else None,
    }


def _validate_enum(value: str | None, allowed: set[str]) -> None:
    if value is not None and value not in allowed:
        raise api_error(422, "invalid_enum_value", "Invalid migration board value.", {})


def _validate_tags(tags: list[str]) -> list[str]:
    unique_tags = list(dict.fromkeys(tags))
    invalid = [tag for tag in unique_tags if tag not in ALLOWED_TAGS]
    if invalid:
        raise api_error(422, "invalid_tag", "Migration board tag is not allowed.", {})
    return unique_tags


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
    if not post["risk_acknowledged"] or not post["legal_disclaimer_acknowledged"]:
        raise api_error(
            422,
            "acknowledgements_required",
            "Risk and legal acknowledgements are required before publication.",
            {},
        )


def _get_owner_post_or_404(
    connection: Connection[Any], post_id: str, user_id: str
) -> dict[str, Any]:
    post = repository.get_post_for_owner(connection, post_id, user_id)
    if post is None:
        raise api_error(
            404, "post_not_found", "Migration board post was not found.", {}
        )
    return post


def _can_view_post(post: dict[str, Any], current_user: CurrentUser | None) -> bool:
    if post["status"] != "published" or post["moderation_status"] != "approved":
        return current_user is not None and current_user.id == post["user_id"]
    if post["visibility"] == "public":
        return True
    if post["visibility"] == "members_only":
        return current_user is not None
    return current_user is not None and current_user.id == post["user_id"]


def _can_receive_contact_request(post: dict[str, Any]) -> bool:
    return (
        post["status"] == "published"
        and post["moderation_status"] == "approved"
        and post["visibility"] in {"public", "members_only"}
        and bool(post["contact_requests_enabled"])
    )


def _change_contact_request(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    request_id: str,
    status: str,
    response_note: str | None,
    expected_user_field: str,
    action: str,
) -> dict[str, Any]:
    ensure_feature_enabled(connection, BOARD_FEATURE_KEY)
    request = repository.get_contact_request_by_id(connection, request_id)
    if request is None or request[expected_user_field] != current_user.id:
        raise api_error(
            404, "contact_request_not_found", "Contact request was not found.", {}
        )
    updated = repository.update_contact_request_status(
        connection, request_id=request_id, status=status, response_note=response_note
    )
    if updated is None:
        raise api_error(
            409, "invalid_contact_request_status", "Request cannot change.", {}
        )
    _audit(
        connection,
        {"id": updated["post_id"]},
        f"contact_request_{action}",
        current_user,
        {"contact_request_id": {"new": request_id}, "status": {"new": status}},
    )
    return _contact_request(updated)


def _create_report(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    post_id: str | None,
    contact_request_id: str | None,
    reason: str,
    details: str | None,
) -> dict[str, Any]:
    if (
        repository.count_reports_created_today(connection, current_user.id)
        >= MAX_REPORTS_PER_DAY
    ):
        raise api_error(
            429,
            "report_limit_exceeded",
            "Daily report limit exceeded.",
            {"limit": MAX_REPORTS_PER_DAY},
        )
    if repository.existing_pending_report_exists(
        connection,
        reporter_user_id=current_user.id,
        post_id=post_id,
        contact_request_id=contact_request_id,
    ):
        raise api_error(
            409, "duplicate_pending_report", "A pending report already exists.", {}
        )
    report = repository.create_report(
        connection,
        reporter_user_id=current_user.id,
        post_id=post_id,
        contact_request_id=contact_request_id,
        reason=reason,
        details=details,
    )
    _audit(
        connection,
        {"id": post_id or contact_request_id},
        "report_created",
        current_user,
        {"reason": {"new": reason}},
    )
    _track_event(
        connection,
        "migration_board_report_created",
        entity_id=post_id or contact_request_id,
        metadata={"reason": reason},
    )
    return _report(report)


def _validate_report(reason: str, details: str | None) -> None:
    if reason not in ALLOWED_REPORT_REASONS:
        raise api_error(422, "invalid_report_reason", "Report reason is invalid.", {})
    if details is not None and len(details) > 1000:
        raise api_error(
            422, "report_details_too_long", "Report details are too long.", {}
        )


def _review_report(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    report_id: str,
    status: str,
    resolution_note: str | None,
    hide_related_post: bool,
) -> dict[str, Any]:
    ensure_feature_enabled(connection, BOARD_FEATURE_KEY)
    ensure_feature_enabled(connection, MODERATION_FEATURE_KEY)
    report = repository.get_report_by_id(connection, report_id)
    if report is None:
        raise api_error(404, "report_not_found", "Report was not found.", {})
    updated = repository.update_report_status(
        connection,
        report_id=report_id,
        status=status,
        reviewed_by=current_user.id,
        resolution_note=resolution_note,
    )
    if updated is None:
        raise api_error(409, "invalid_report_status", "Report cannot be reviewed.", {})
    if hide_related_post and updated.get("post_id"):
        repository.hide_post(
            connection,
            post_id=updated["post_id"],
            moderator_user_id=current_user.id,
            reason=resolution_note,
        )
    _audit(
        connection,
        {"id": report_id},
        f"report_{status}",
        current_user,
        {"status": {"old": report["status"], "new": status}},
    )
    return _report(updated)


def _select_source_post(
    connection: Connection[Any], current_user: CurrentUser, post_id: str | None
) -> dict[str, Any]:
    if post_id is not None:
        return _get_owner_post_or_404(connection, post_id, current_user.id)
    rows = repository.list_user_posts(connection, current_user.id)
    for row in rows:
        if row["status"] in {"review", "published", "draft"}:
            return row
    raise api_error(
        404,
        "source_post_not_found",
        "Create a migration board post before viewing matches.",
        {},
    )


def _is_significant_edit(payload: Any) -> bool:
    fields = {
        "destination_country_slug",
        "origin_country_slug",
        "route_id",
        "scenario_slug",
        "persona_slug",
        "title",
        "summary",
        "timeline_window",
        "migration_stage",
        "companion_goal",
        "visibility",
    }
    return any(getattr(payload, field, None) is not None for field in fields)


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


def _match_reasons(source: dict[str, Any], candidate: dict[str, Any]) -> list[str]:
    reasons = ["same_destination"]
    if source.get("route_id") and source.get("route_id") == candidate.get("route_id"):
        reasons.append("same_route")
    if source.get("timeline_window") == candidate.get("timeline_window"):
        reasons.append("similar_timeline")
    if source.get("scenario_slug") and source.get("scenario_slug") == candidate.get(
        "scenario_slug"
    ):
        reasons.append("same_scenario")
    if source.get("persona_slug") and source.get("persona_slug") == candidate.get(
        "persona_slug"
    ):
        reasons.append("same_persona")
    if source.get("companion_goal") == candidate.get("companion_goal"):
        reasons.append("same_goal")
    return reasons


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


def _diff_for_update(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    changes: dict[str, Any] = {}
    for field in (
        "title",
        "summary",
        "timeline_window",
        "migration_stage",
        "companion_goal",
        "visibility",
        "status",
        "moderation_status",
    ):
        if before.get(field) != after.get(field):
            changes[field] = {"old": before.get(field), "new": after.get(field)}
    return changes or {"updated": {"new": True}}


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
        route_id=UUID(str(metadata["route_id"])) if metadata.get("route_id") else None,
        entity_type="migration_board_post" if entity_id else None,
        entity_id=UUID(str(entity_id)) if entity_id else None,
        metadata=metadata,
    )


def _total(rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    return int(rows[0].get("total_count") or len(rows))
