from app.core.auth import CurrentUser
from app.core.errors import api_error
from app.repositories import migration_board as repository
from app.services.migration_board import helpers
from psycopg import Connection
from typing import Any


def list_public_posts(
    connection: Connection[Any],
    *,
    current_user: CurrentUser | None,
    filters: dict[str, Any],
    limit: int,
    offset: int,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    helpers.ensure_feature_enabled(
        connection, helpers.PUBLIC_LISTING_FEATURE_KEY
    )
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
    helpers._track_event(
        connection,
        "migration_board_list_viewed",
        metadata=helpers._safe_filter_metadata(filters),
    )
    return {
        "items": [helpers._public_post(row) for row in rows],
        "total": helpers._total(rows),
        "limit": limit,
        "offset": offset,
    }


def get_public_post(
    connection: Connection[Any],
    *,
    post_id: str,
    current_user: CurrentUser | None,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    post = repository.get_post_by_id(connection, post_id)
    if post is None or not _can_view_post(post, current_user):
        raise api_error(
            404, "post_not_found", "Migration board post was not found.", {}
        )
    helpers._track_event(
        connection,
        "migration_board_post_viewed",
        entity_id=post_id,
        metadata={
            "destination_country_slug": post.get("destination_country_slug")
        },
    )
    return helpers._public_detail(post)


def create_user_post(
    connection: Connection[Any], *, current_user: CurrentUser, payload: Any
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    limit = helpers.max_active_posts(connection)
    with connection.transaction():
        helpers.with_daily_limit_lock(
            connection, current_user.id, "active_post"
        )
        if (
            repository.count_user_active_posts(connection, current_user.id)
            >= limit
        ):
            raise api_error(
                429,
                "active_post_limit_exceeded",
                "You have reached the active migration board post limit.",
                {"limit": limit},
            )
        refs = _validate_post_payload(connection, payload)
        helpers._reject_public_pii(payload.title, payload.summary)
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
    helpers._audit(
        connection, post, "created", current_user, {"status": {"new": "draft"}}
    )
    helpers._track_event(
        connection,
        "migration_board_post_created",
        entity_id=post["id"],
        metadata=helpers._safe_post_metadata(post),
    )
    return helpers._my_post(post)


def update_user_post(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    post_id: str,
    payload: Any,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    existing = _get_owner_post_or_404(connection, post_id, current_user.id)
    if existing["status"] not in {
        "draft",
        "review",
        "published",
        "rejected",
        "archived",
    }:
        raise api_error(
            409, "invalid_post_status", "Post cannot be updated.", {}
        )
    refs = _validate_post_payload(connection, payload, existing=existing)
    title = payload.title if payload.title is not None else existing["title"]
    summary = (
        payload.summary if payload.summary is not None else existing["summary"]
    )
    helpers._reject_public_pii(title, summary)
    tags = _validate_tags(payload.tags) if payload.tags is not None else None
    reset_to_review = existing[
        "status"
    ] == "published" and _is_significant_edit(payload)
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
    helpers._audit(
        connection,
        updated,
        "updated",
        current_user,
        _diff_for_update(existing, updated),
    )
    return helpers._my_post(updated)


def submit_user_post(
    connection: Connection[Any], *, current_user: CurrentUser, post_id: str
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    post = _get_owner_post_or_404(connection, post_id, current_user.id)
    helpers._require_submit_ready(post)
    updated = repository.submit_post_for_review(connection, post_id)
    if updated is None:
        raise api_error(
            409, "invalid_status_transition", "Post cannot be submitted.", {}
        )
    helpers._audit(
        connection,
        updated,
        "submitted_for_review",
        current_user,
        {"status": {"old": post["status"], "new": "review"}},
    )
    helpers._track_event(
        connection,
        "migration_board_post_submitted",
        entity_id=post_id,
        metadata=helpers._safe_post_metadata(updated),
    )
    return helpers._my_post(updated)


def archive_user_post(
    connection: Connection[Any], *, current_user: CurrentUser, post_id: str
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    post = _get_owner_post_or_404(connection, post_id, current_user.id)
    updated = repository.archive_post(connection, post_id)
    if updated is None:
        raise api_error(
            409, "invalid_status_transition", "Post cannot be archived.", {}
        )
    helpers._audit(
        connection,
        updated,
        "archived",
        current_user,
        {"status": {"old": post["status"], "new": "archived"}},
    )
    return helpers._my_post(updated)


def list_my_posts(
    connection: Connection[Any], current_user: CurrentUser
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    rows = repository.list_user_posts(connection, current_user.id)
    return {
        "items": [helpers._my_post(row) for row in rows],
        "total": len(rows),
    }


def get_my_post(
    connection: Connection[Any], *, current_user: CurrentUser, post_id: str
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    return helpers._my_post(
        _get_owner_post_or_404(connection, post_id, current_user.id)
    )


def list_companion_matches(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    post_id: str | None,
    limit: int,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection, helpers.BOARD_FEATURE_KEY)
    helpers.ensure_feature_enabled(connection, helpers.MATCHING_FEATURE_KEY)
    source = _select_source_post(connection, current_user, post_id)
    rows = repository.list_potential_companion_posts(
        connection, source_post=source, user_id=current_user.id, limit=limit
    )
    helpers._track_event(
        connection,
        "migration_board_match_viewed",
        entity_id=source["id"],
        metadata=helpers._safe_post_metadata(source),
    )
    return {
        "items": [
            {
                **helpers._public_post(row),
                "match_reasons": _match_reasons(source, row),
            }
            for row in rows
        ],
        "total": len(rows),
    }


def _validate_post_payload(
    connection: Connection[Any],
    payload: Any,
    existing: dict[str, Any] | None = None,
) -> dict[str, str | None]:
    destination_country_id = (
        existing["destination_country_id"] if existing else None
    )
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
                404,
                "origin_country_not_found",
                "Origin country was not found.",
                {},
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
    if scenario_slug and not repository.scenario_exists(
        connection, scenario_slug
    ):
        raise api_error(
            404, "scenario_not_found", "Scenario was not found.", {}
        )
    persona_slug = getattr(payload, "persona_slug", None)
    if persona_slug and not repository.persona_exists(connection, persona_slug):
        raise api_error(404, "persona_not_found", "Persona was not found.", {})
    _validate_enum(
        getattr(payload, "timeline_window", None),
        helpers.ALLOWED_TIMELINE_WINDOWS,
    )
    _validate_enum(
        getattr(payload, "budget_range", None), helpers.ALLOWED_BUDGET_RANGES
    )
    _validate_enum(
        getattr(payload, "household_type", None),
        helpers.ALLOWED_HOUSEHOLD_TYPES,
    )
    _validate_enum(
        getattr(payload, "migration_stage", None),
        helpers.ALLOWED_MIGRATION_STAGES,
    )
    _validate_enum(
        getattr(payload, "companion_goal", None),
        helpers.ALLOWED_COMPANION_GOALS,
    )
    _validate_enum(
        getattr(payload, "visibility", None), helpers.ALLOWED_VISIBILITIES
    )
    if destination_country_id is None:
        raise api_error(
            422,
            "destination_country_required",
            "Destination country is required.",
            {},
        )
    return {
        "destination_country_id": str(destination_country_id),
        "origin_country_id": str(origin_country_id)
        if origin_country_id
        else None,
    }


def _validate_enum(value: str | None, allowed: set[str]) -> None:
    if value is not None and value not in allowed:
        raise api_error(
            422, "invalid_enum_value", "Invalid migration board value.", {}
        )


def _validate_tags(tags: list[str]) -> list[str]:
    unique_tags = list(dict.fromkeys(tags))
    invalid = [tag for tag in unique_tags if tag not in helpers.ALLOWED_TAGS]
    if invalid:
        raise api_error(
            422, "invalid_tag", "Migration board tag is not allowed.", {}
        )
    return unique_tags


def _get_owner_post_or_404(
    connection: Connection[Any], post_id: str, user_id: str
) -> dict[str, Any]:
    post = repository.get_post_for_owner(connection, post_id, user_id)
    if post is None:
        raise api_error(
            404, "post_not_found", "Migration board post was not found.", {}
        )
    return post


def _can_view_post(
    post: dict[str, Any], current_user: CurrentUser | None
) -> bool:
    if post["status"] != "published" or post["moderation_status"] != "approved":
        return current_user is not None and current_user.id == post["user_id"]
    if post["visibility"] == "public":
        return True
    if post["visibility"] == "members_only":
        return current_user is not None
    return current_user is not None and current_user.id == post["user_id"]


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


def _match_reasons(
    source: dict[str, Any], candidate: dict[str, Any]
) -> list[str]:
    reasons = ["same_destination"]
    if source.get("route_id") and source.get("route_id") == candidate.get(
        "route_id"
    ):
        reasons.append("same_route")
    if source.get("timeline_window") == candidate.get("timeline_window"):
        reasons.append("similar_timeline")
    if source.get("scenario_slug") and source.get(
        "scenario_slug"
    ) == candidate.get("scenario_slug"):
        reasons.append("same_scenario")
    if source.get("persona_slug") and source.get(
        "persona_slug"
    ) == candidate.get("persona_slug"):
        reasons.append("same_persona")
    if source.get("companion_goal") == candidate.get("companion_goal"):
        reasons.append("same_goal")
    return reasons


def _diff_for_update(
    before: dict[str, Any], after: dict[str, Any]
) -> dict[str, Any]:
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
