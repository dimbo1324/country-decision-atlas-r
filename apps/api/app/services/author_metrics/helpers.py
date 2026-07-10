from app.core.auth import CurrentUser
from app.core.errors import api_error
from app.repositories import author_metrics as repository
from app.repositories.analytics import insert_analytics_event
from app.repositories.audit import insert_audit_event
from app.services.feature_flags import (
    ensure_feature_enabled as _ensure_feature_enabled,
)
from app.services.methodology_config import get_active_methodology_config
from app.services.pii_patterns import contains_pii
from psycopg import Connection
from typing import Any
from uuid import UUID


FEATURE_KEY = "author_metrics_enabled"
ALLOWED_POLARITIES = {"higher_is_better", "lower_is_better"}
ALLOWED_LICENSES = {"platform", "cc_by_sa"}
ALLOWED_VISIBILITIES = {"private", "public"}
LOCKED_LICENSE_STATUSES = {"review", "published", "archived"}


def ensure_feature_enabled(connection: Connection[Any]) -> None:
    _ensure_feature_enabled(
        connection,
        FEATURE_KEY,
        "Author metrics are currently disabled.",
    )


def min_methodology_length(connection: Connection[Any]) -> int:
    return get_active_methodology_config(
        connection
    ).author_metrics.min_methodology_length


def min_country_coverage(connection: Connection[Any]) -> int:
    return get_active_methodology_config(
        connection
    ).author_metrics.min_country_coverage


def get_owner_definition_or_404(
    connection: Connection[Any], definition_id: str, author_user_id: str
) -> dict[str, Any]:
    definition = repository.get_definition_for_author(
        connection, definition_id, author_user_id
    )
    if definition is None:
        raise api_error(
            404,
            "author_metric_not_found",
            "Author metric definition was not found.",
            {},
        )
    return definition


def get_definition_or_404(
    connection: Connection[Any], definition_id: str
) -> dict[str, Any]:
    definition = repository.get_definition_by_id(connection, definition_id)
    if definition is None:
        raise api_error(
            404,
            "author_metric_not_found",
            "Author metric definition was not found.",
            {},
        )
    return definition


def _reject_pii(*texts: str) -> None:
    if contains_pii(*texts):
        raise api_error(
            422,
            "pii_not_allowed",
            "Author metric text cannot include direct contact details.",
            {},
        )


def _require_submit_ready(
    connection: Connection[Any], definition: dict[str, Any]
) -> None:
    _reject_pii(
        str(definition["name_en"]),
        str(definition["name_ru"]),
        str(definition["methodology_en"]),
        str(definition["methodology_ru"]),
    )
    combined_length = len(str(definition["methodology_en"])) + len(
        str(definition["methodology_ru"])
    )
    threshold = min_methodology_length(connection)
    if combined_length < threshold:
        raise api_error(
            422,
            "methodology_too_short",
            "Methodology description is too short to submit for review.",
            {"min_methodology_length": threshold},
        )


def _require_publish_ready(
    connection: Connection[Any], *, country_coverage: int
) -> None:
    threshold = min_country_coverage(connection)
    if country_coverage < threshold:
        raise api_error(
            422,
            "insufficient_country_coverage",
            "Author metric needs values for more countries before it can be published.",
            {"min_country_coverage": threshold},
        )


def _validate_enum(value: str | None, allowed: set[str], code: str) -> None:
    if value is not None and value not in allowed:
        raise api_error(422, code, "Invalid author metric value.", {})


def _require_value_source_or_experience(
    *, source_url: str | None, is_personal_experience: bool
) -> None:
    if source_url is None and not is_personal_experience:
        raise api_error(
            422,
            "value_source_required",
            "Provide a source URL or mark the value as personal experience.",
            {},
        )


def _require_value_within_scale(
    *, value: float, scale_min: float, scale_max: float
) -> None:
    if value < float(scale_min) or value > float(scale_max):
        raise api_error(
            422,
            "value_out_of_scale",
            "Value is outside the metric's declared scale.",
            {"scale_min": float(scale_min), "scale_max": float(scale_max)},
        )


def _author_ref(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "user_id": row["author_user_id"],
        "display_name": row.get("author_display_name") or "Member",
    }


def _public_definition(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "slug": row["slug"],
        "name_en": row["name_en"],
        "name_ru": row["name_ru"],
        "methodology_en": row["methodology_en"],
        "methodology_ru": row["methodology_ru"],
        "polarity": row["polarity"],
        "scale_min": row["scale_min"],
        "scale_max": row["scale_max"],
        "license": row["license"],
        "author": _author_ref(row),
        "forked_from_id": row.get("forked_from_id"),
        "version": row["version"],
        "published_at": row.get("published_at"),
    }


def _my_definition(row: dict[str, Any]) -> dict[str, Any]:
    return {
        **_public_definition(row),
        "status": row["status"],
        "visibility": row["visibility"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "submitted_at": row.get("submitted_at"),
        "archived_at": row.get("archived_at"),
        "rejected_at": row.get("rejected_at"),
        "moderation_reason": row.get("moderation_reason"),
    }


def _admin_definition(row: dict[str, Any]) -> dict[str, Any]:
    return {
        **_my_definition(row),
        "author_user_id": row["author_user_id"],
        "moderated_by": row.get("moderated_by"),
        "moderated_at": row.get("moderated_at"),
    }


def _country_value(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "country_id": row["country_id"],
        "country_slug": row["country_slug"],
        "country_name": row["country_name"],
        "value": row["value"],
        "source_url": row.get("source_url"),
        "is_personal_experience": row["is_personal_experience"],
        "note": row.get("note"),
        "valid_as_of": row.get("valid_as_of"),
        "updated_at": row["updated_at"],
    }


def _overlay_entry(row: dict[str, Any]) -> dict[str, Any]:
    return {
        **_public_definition(row),
        "value": row["value"],
        "source_url": row.get("source_url"),
        "is_personal_experience": row["is_personal_experience"],
        "note": row.get("note"),
        "valid_as_of": row.get("valid_as_of"),
        "value_updated_at": row["value_updated_at"],
    }


def _feed_entry(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "metric_id": row["metric_id"],
        "metric_slug": row["metric_slug"],
        "metric_name_en": row["metric_name_en"],
        "metric_name_ru": row["metric_name_ru"],
        "author": {
            "user_id": row["author_user_id"],
            "display_name": row.get("author_display_name") or "Member",
        },
        "country_id": row["country_id"],
        "country_slug": row["country_slug"],
        "country_name": row["country_name"],
        "value": row["value"],
        "value_updated_at": row["value_updated_at"],
    }


def _subscription(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "metric_id": row.get("metric_id"),
        "metric_slug": row.get("metric_slug"),
        "metric_name_en": row.get("metric_name_en"),
        "author_user_id": row.get("author_user_id"),
        "author_display_name": row.get("author_display_name"),
        "created_at": row["created_at"],
    }


def _reputation(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "author_user_id": row["author_user_id"],
        "coverage_score": row["coverage_score"],
        "freshness_score": row["freshness_score"],
        "sourcing_score": row["sourcing_score"],
        "subscriber_count": row["subscriber_count"],
        "published_metric_count": row["published_metric_count"],
        "computed_at": row["computed_at"],
        "methodology_version": row["methodology_version"],
    }


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
        entity_type="author_metric_definition",
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
        session_hash="author_metrics_runtime_0000000001",
        event_type=event_type,
        source="api",
        path=None,
        locale=None,
        country_slug=metadata.get("country_slug"),
        scenario_slug=None,
        persona_slug=None,
        route_id=None,
        entity_type="author_metric_definition" if entity_id else None,
        entity_id=UUID(str(entity_id)) if entity_id else None,
        metadata=metadata,
    )
