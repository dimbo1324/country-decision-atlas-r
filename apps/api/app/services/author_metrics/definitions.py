import re
from app.core.auth import CurrentUser
from app.core.errors import api_error
from app.repositories import author_metrics as repository
from app.services import capabilities as capabilities_service
from app.services.author_metrics import helpers
from app.services.list_helpers import total_from_window_count
from psycopg import Connection, errors as psycopg_errors
from typing import Any


SLUG_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def list_public_definitions_for_author(
    connection: Connection[Any], author_user_id: str
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    rows = repository.list_published_definitions_for_author(
        connection, author_user_id
    )
    return {
        "items": [helpers._public_definition(row) for row in rows],
        "total": len(rows),
    }


def create_my_definition(
    connection: Connection[Any], *, current_user: CurrentUser, payload: Any
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    _validate_slug(payload.slug)
    helpers._validate_enum(
        payload.polarity, helpers.ALLOWED_POLARITIES, "invalid_polarity"
    )
    helpers._validate_enum(
        payload.license, helpers.ALLOWED_LICENSES, "invalid_license"
    )
    helpers._validate_enum(
        payload.visibility, helpers.ALLOWED_VISIBILITIES, "invalid_visibility"
    )
    if payload.scale_min >= payload.scale_max:
        raise api_error(
            422, "invalid_scale", "scale_min must be less than scale_max.", {}
        )
    if repository.get_definition_by_author_slug(
        connection, current_user.id, payload.slug
    ):
        raise api_error(
            409,
            "author_metric_slug_taken",
            "You already have an author metric with this slug.",
            {},
        )
    helpers._reject_pii(
        payload.name_en,
        payload.name_ru,
        payload.methodology_en,
        payload.methodology_ru,
    )
    try:
        definition = repository.create_definition(
            connection,
            author_user_id=current_user.id,
            slug=payload.slug,
            name_en=payload.name_en,
            name_ru=payload.name_ru,
            methodology_en=payload.methodology_en,
            methodology_ru=payload.methodology_ru,
            polarity=payload.polarity,
            scale_min=payload.scale_min,
            scale_max=payload.scale_max,
            license=payload.license,
            visibility=payload.visibility,
            forked_from_id=None,
        )
    except psycopg_errors.UniqueViolation as exc:
        raise api_error(
            409,
            "author_metric_slug_taken",
            "You already have an author metric with this slug.",
            {},
        ) from exc
    helpers._audit(
        connection,
        definition,
        "created",
        current_user,
        {"status": {"new": "draft"}},
    )
    return helpers._my_definition(definition)


def update_my_definition(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    definition_id: str,
    payload: Any,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    existing = helpers.get_owner_definition_or_404(
        connection, definition_id, current_user.id
    )
    if existing["status"] == "archived":
        raise api_error(
            409,
            "invalid_definition_status",
            "Definition cannot be updated.",
            {},
        )
    helpers._validate_enum(
        payload.polarity, helpers.ALLOWED_POLARITIES, "invalid_polarity"
    )
    helpers._validate_enum(
        payload.license, helpers.ALLOWED_LICENSES, "invalid_license"
    )
    helpers._validate_enum(
        payload.visibility, helpers.ALLOWED_VISIBILITIES, "invalid_visibility"
    )
    scale_min = (
        payload.scale_min
        if payload.scale_min is not None
        else existing["scale_min"]
    )
    scale_max = (
        payload.scale_max
        if payload.scale_max is not None
        else existing["scale_max"]
    )
    if float(scale_min) >= float(scale_max):
        raise api_error(
            422, "invalid_scale", "scale_min must be less than scale_max.", {}
        )
    license_value = payload.license
    if (
        license_value is not None
        and existing["status"] in helpers.LOCKED_LICENSE_STATUSES
    ):
        raise api_error(
            409,
            "license_locked",
            "License cannot be changed once the definition has been submitted or published.",
            {},
        )
    name_en = (
        payload.name_en if payload.name_en is not None else existing["name_en"]
    )
    name_ru = (
        payload.name_ru if payload.name_ru is not None else existing["name_ru"]
    )
    methodology_en = (
        payload.methodology_en
        if payload.methodology_en is not None
        else existing["methodology_en"]
    )
    methodology_ru = (
        payload.methodology_ru
        if payload.methodology_ru is not None
        else existing["methodology_ru"]
    )
    helpers._reject_pii(name_en, name_ru, methodology_en, methodology_ru)
    reset_to_review = existing[
        "status"
    ] == "published" and _is_significant_edit(payload)
    updated = repository.update_definition(
        connection,
        definition_id=definition_id,
        name_en=payload.name_en,
        name_ru=payload.name_ru,
        methodology_en=payload.methodology_en,
        methodology_ru=payload.methodology_ru,
        polarity=payload.polarity,
        scale_min=payload.scale_min,
        scale_max=payload.scale_max,
        license=license_value,
        visibility=payload.visibility,
        reset_to_review=reset_to_review,
    )
    if updated is None:
        raise api_error(
            404,
            "author_metric_not_found",
            "Author metric definition was not found.",
            {},
        )
    helpers._audit(
        connection,
        updated,
        "updated",
        current_user,
        _diff_for_update(existing, updated),
    )
    return helpers._my_definition(updated)


def submit_my_definition(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    definition_id: str,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    definition = helpers.get_owner_definition_or_404(
        connection, definition_id, current_user.id
    )
    helpers._require_submit_ready(connection, definition)
    updated = repository.submit_definition_for_review(connection, definition_id)
    if updated is None:
        raise api_error(
            409,
            "invalid_status_transition",
            "Author metric definition cannot be submitted.",
            {},
        )
    helpers._audit(
        connection,
        updated,
        "submitted_for_review",
        current_user,
        {"status": {"old": definition["status"], "new": "review"}},
    )
    return helpers._my_definition(updated)


def archive_my_definition(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    definition_id: str,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    definition = helpers.get_owner_definition_or_404(
        connection, definition_id, current_user.id
    )
    updated = repository.archive_definition(connection, definition_id)
    if updated is None:
        raise api_error(
            409,
            "invalid_status_transition",
            "Author metric definition cannot be archived.",
            {},
        )
    helpers._audit(
        connection,
        updated,
        "archived",
        current_user,
        {"status": {"old": definition["status"], "new": "archived"}},
    )
    return helpers._my_definition(updated)


def list_my_definitions(
    connection: Connection[Any], current_user: CurrentUser
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    rows = repository.list_definitions_for_author(connection, current_user.id)
    return {
        "items": [helpers._my_definition(row) for row in rows],
        "total": len(rows),
    }


def get_my_definition(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    definition_id: str,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    return helpers._my_definition(
        helpers.get_owner_definition_or_404(
            connection, definition_id, current_user.id
        )
    )


def get_definition_for_moderation(
    connection: Connection[Any], definition_id: str
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    return helpers._admin_definition(
        helpers.get_definition_or_404(connection, definition_id)
    )


def list_definitions_for_moderation(
    connection: Connection[Any], *, status: str | None, limit: int, offset: int
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    rows = repository.list_definitions_for_moderation(
        connection, status=status, limit=limit, offset=offset
    )
    return {
        "items": [helpers._admin_definition(row) for row in rows],
        "total": total_from_window_count(rows),
    }


def approve_definition(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    definition_id: str,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    definition = helpers.get_definition_or_404(connection, definition_id)
    capabilities_service.assert_no_moderation_conflict(
        current_user, [definition["author_user_id"]]
    )
    coverage = repository.count_countries_with_values(connection, definition_id)
    helpers._require_publish_ready(connection, country_coverage=coverage)
    updated = repository.publish_definition(
        connection,
        definition_id=definition_id,
        moderator_user_id=current_user.id,
    )
    if updated is None:
        raise api_error(
            409,
            "invalid_status_transition",
            "Author metric definition cannot be approved.",
            {},
        )
    helpers._audit(
        connection,
        updated,
        "published",
        current_user,
        {"status": {"old": definition["status"], "new": "published"}},
    )
    helpers._track_event(
        connection,
        "author_metric_published",
        entity_id=definition_id,
        metadata={"author_user_id": updated["author_user_id"]},
    )
    return helpers._admin_definition(updated)


def reject_definition(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    definition_id: str,
    reason: str | None,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    definition = helpers.get_definition_or_404(connection, definition_id)
    capabilities_service.assert_no_moderation_conflict(
        current_user, [definition["author_user_id"]]
    )
    updated = repository.reject_definition(
        connection,
        definition_id=definition_id,
        moderator_user_id=current_user.id,
        reason=reason,
    )
    if updated is None:
        raise api_error(
            409,
            "invalid_status_transition",
            "Author metric definition cannot be rejected.",
            {},
        )
    helpers._audit(
        connection,
        updated,
        "rejected",
        current_user,
        {"reason": {"new": reason}},
    )
    return helpers._admin_definition(updated)


def _validate_slug(slug: str) -> None:
    if not SLUG_PATTERN.match(slug):
        raise api_error(
            422,
            "invalid_slug",
            "Slug must be lowercase alphanumeric segments separated by hyphens.",
            {},
        )


def _is_significant_edit(payload: Any) -> bool:
    fields = (
        "name_en",
        "name_ru",
        "methodology_en",
        "methodology_ru",
        "polarity",
    )
    return any(getattr(payload, field, None) is not None for field in fields)


def _diff_for_update(
    before: dict[str, Any], after: dict[str, Any]
) -> dict[str, Any]:
    changes: dict[str, Any] = {}
    for field in (
        "name_en",
        "name_ru",
        "polarity",
        "visibility",
        "license",
        "status",
    ):
        if before.get(field) != after.get(field):
            changes[field] = {"old": before.get(field), "new": after.get(field)}
    return changes or {"updated": {"new": True}}
