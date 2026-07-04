from app.repositories import route_checklists as repository
from app.schemas.route_checklists import (
    RouteChecklistItem,
    RouteChecklistResponse,
)
from psycopg import Connection
from typing import Any


def get_route_checklist(
    connection: Connection[Any], route_id: str, locale: str
) -> RouteChecklistResponse:
    rows = repository.list_route_checklist_items(connection, route_id, locale)
    return RouteChecklistResponse(
        items=[RouteChecklistItem(**row) for row in rows]
    )


def get_route_checklist_by_slug(
    connection: Connection[Any], country_slug: str, route_slug: str, locale: str
) -> RouteChecklistResponse:
    rows = repository.list_route_checklist_items_by_route_slug(
        connection, country_slug, route_slug, locale
    )
    return RouteChecklistResponse(
        items=[RouteChecklistItem(**row) for row in rows]
    )
