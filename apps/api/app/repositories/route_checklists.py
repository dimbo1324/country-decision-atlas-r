from app.core.database import fetch_all, fetch_one
from app.core.locales import validate_locale
from psycopg import Connection
from typing import Any


CHECKLIST_ITEM_FIELDS = """
    rci.id::text AS id,
    rci.route_id::text AS route_id,
    rci.step_order,
    {title_col} AS title,
    {description_col} AS description,
    rci.document_note,
    rci.cost_note,
    rci.timing_note,
    rci.official_requirement_note,
    rci.is_required,
    rci.source_id::text AS source_id,
    rci.evidence_item_id::text AS evidence_item_id
"""


def _localized_columns(locale: str) -> tuple[str, str]:
    requested_locale = validate_locale(locale)
    if requested_locale == "ru":
        return (
            "COALESCE(rci.title_ru, rci.title)",
            "COALESCE(rci.description_ru, rci.description)",
        )
    return "rci.title", "rci.description"


def list_route_checklist_items(
    connection: Connection[Any], route_id: str, locale: str = "en"
) -> list[dict[str, Any]]:
    title_col, description_col = _localized_columns(locale)
    return fetch_all(
        connection,
        f"""
        SELECT
            {CHECKLIST_ITEM_FIELDS.format(title_col=title_col, description_col=description_col)}
        FROM route_checklist_items rci
        WHERE rci.route_id::text = %s
          AND rci.status = 'published'
        ORDER BY rci.step_order
        """,
        (route_id,),
    )


def list_route_checklist_items_by_route_slug(
    connection: Connection[Any],
    country_slug: str,
    route_slug: str,
    locale: str = "en",
) -> list[dict[str, Any]]:
    title_col, description_col = _localized_columns(locale)
    return fetch_all(
        connection,
        f"""
        SELECT
            {CHECKLIST_ITEM_FIELDS.format(title_col=title_col, description_col=description_col)}
        FROM route_checklist_items rci
        JOIN routes r ON r.id = rci.route_id
        JOIN countries c ON c.id = r.country_id
        WHERE c.slug = %s
          AND r.slug = %s
          AND rci.status = 'published'
        ORDER BY rci.step_order
        """,
        (country_slug, route_slug),
    )


def count_published_checklist_items(connection: Connection[Any]) -> int:
    row = fetch_one(
        connection,
        "SELECT COUNT(*) AS total FROM route_checklist_items WHERE status = 'published'",
    )
    return int(row["total"]) if row else 0


def list_orphan_checklist_items(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            rci.id::text AS id,
            rci.route_id::text AS route_id,
            r.slug AS route_slug,
            r.status AS route_status
        FROM route_checklist_items rci
        JOIN routes r ON r.id = rci.route_id
        WHERE rci.status = 'published'
          AND r.status <> 'published'
        ORDER BY r.slug, rci.step_order
        """,
    )


def list_published_checklist_items_without_traceability(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            rci.id::text AS id,
            rci.route_id::text AS route_id,
            r.slug AS route_slug,
            c.slug AS country_slug
        FROM route_checklist_items rci
        JOIN routes r ON r.id = rci.route_id
        JOIN countries c ON c.id = r.country_id
        WHERE rci.status = 'published'
          AND rci.source_id IS NULL
          AND rci.evidence_item_id IS NULL
        ORDER BY c.slug, r.slug, rci.step_order
        """,
    )
