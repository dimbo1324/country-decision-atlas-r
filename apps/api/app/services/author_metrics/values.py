from app.core.auth import CurrentUser
from app.core.errors import api_error
from app.repositories import (
    author_metrics as repository,
    countries as countries_repository,
)
from app.services.author_metrics import helpers
from psycopg import Connection
from typing import Any


def list_values_for_my_definition(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    definition_id: str,
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    helpers.get_owner_definition_or_404(
        connection, definition_id, current_user.id
    )
    rows = repository.list_values_for_definition(connection, definition_id)
    return {
        "items": [helpers._country_value(row) for row in rows],
        "total": len(rows),
    }


def bulk_upsert_values(
    connection: Connection[Any],
    *,
    current_user: CurrentUser,
    definition_id: str,
    items: list[Any],
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    definition = helpers.get_owner_definition_or_404(
        connection, definition_id, current_user.id
    )
    if definition["status"] == "archived":
        raise api_error(
            409,
            "invalid_definition_status",
            "Values cannot be set on an archived definition.",
            {},
        )
    slugs = [item.country_slug for item in items]
    duplicate_slugs = {slug for slug in slugs if slugs.count(slug) > 1}
    if duplicate_slugs:
        raise api_error(
            422,
            "duplicate_country_slug",
            "Each country_slug may appear at most once per bulk-upsert request.",
            {"duplicate_country_slugs": sorted(duplicate_slugs)},
        )
    resolved_countries = []
    for item in items:
        helpers._require_value_source_or_experience(
            source_url=item.source_url,
            is_personal_experience=item.is_personal_experience,
        )
        helpers._require_value_within_scale(
            value=item.value,
            scale_min=definition["scale_min"],
            scale_max=definition["scale_max"],
        )
        country = countries_repository.get_active_country_by_slug(
            connection, item.country_slug
        )
        if country is None:
            raise api_error(
                404,
                "country_not_found",
                "Country was not found.",
                {"country_slug": item.country_slug},
            )
        resolved_countries.append((item, country))
    for item, country in resolved_countries:
        repository.upsert_value(
            connection,
            metric_id=definition_id,
            country_id=country["id"],
            value=item.value,
            source_url=item.source_url,
            is_personal_experience=item.is_personal_experience,
            note=item.note,
            valid_as_of=item.valid_as_of,
        )
    helpers._audit(
        connection,
        definition,
        "updated",
        current_user,
        {"values_upserted": {"new": len(items)}},
    )
    rows = repository.list_values_for_definition(connection, definition_id)
    return {
        "items": [helpers._country_value(row) for row in rows],
        "total": len(rows),
    }
