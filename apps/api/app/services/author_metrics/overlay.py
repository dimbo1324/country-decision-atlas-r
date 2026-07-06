from app.core.errors import api_error
from app.repositories import (
    author_metrics as repository,
    countries as countries_repository,
)
from app.services.author_metrics import helpers
from psycopg import Connection
from typing import Any


def get_author_metrics_for_country(
    connection: Connection[Any], country_slug: str
) -> dict[str, Any]:
    helpers.ensure_feature_enabled(connection)
    country = countries_repository.get_active_country_by_slug(
        connection, country_slug
    )
    if country is None:
        raise api_error(404, "country_not_found", "Country was not found.", {})
    rows = repository.list_published_definitions_for_country(
        connection, country["id"]
    )
    return {
        "country_slug": country["slug"],
        "items": [helpers._overlay_entry(row) for row in rows],
        "total": len(rows),
    }
