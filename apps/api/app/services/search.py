from app.core.errors import api_error
from app.repositories import search as repository
from app.schemas.search import (
    SearchResponse,
    SearchResultItem,
    SearchResultType,
)
from psycopg import Connection
from typing import Any, get_args


VALID_ENTITY_TYPES: frozenset[str] = frozenset(get_args(SearchResultType))


def _parse_entity_types(types: str | None) -> list[str] | None:
    if not types:
        return None
    parsed = [item.strip() for item in types.split(",") if item.strip()]
    invalid = [item for item in parsed if item not in VALID_ENTITY_TYPES]
    if invalid:
        raise api_error(
            422,
            "invalid_search_entity_type",
            "Unknown search entity type requested.",
            {
                "invalid_types": invalid,
                "allowed_types": sorted(VALID_ENTITY_TYPES),
            },
        )
    return parsed or None


def run_search(
    connection: Connection[Any],
    q: str,
    locale: str,
    types: str | None,
    country_slug: str | None,
    limit: int,
    offset: int,
) -> SearchResponse:
    normalized_query = q.strip()
    if not normalized_query:
        raise api_error(
            422,
            "search_query_empty",
            "Search query must not be empty.",
            {"q": q},
        )
    entity_types = _parse_entity_types(types)
    rows = repository.search_documents(
        connection,
        normalized_query,
        locale,
        entity_types,
        country_slug,
        limit,
        offset,
    )
    total = repository.count_search_documents_matching(
        connection, normalized_query, locale, entity_types, country_slug
    )
    return SearchResponse(
        query=normalized_query,
        locale=locale,
        total=total,
        limit=limit,
        offset=offset,
        items=[SearchResultItem(**row) for row in rows],
    )
