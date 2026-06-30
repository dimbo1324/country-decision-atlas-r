from app.core.database import fetch_all, fetch_one
from psycopg import Connection
from typing import Any


def list_methodology_sections(
    connection: Connection[Any], locale: str = "en"
) -> list[dict[str, Any]]:
    use_ru = locale == "ru"
    return fetch_all(
        connection,
        """
        SELECT
            slug,
            CASE WHEN %s THEN title_ru ELSE title END AS title,
            CASE WHEN %s THEN summary_ru ELSE summary END AS summary,
            CASE WHEN %s THEN body_ru ELSE body END AS body,
            section_type,
            display_order,
            updated_at
        FROM methodology_sections
        WHERE status = 'published'
        ORDER BY display_order ASC
        """,
        (use_ru, use_ru, use_ru),
    )


def get_methodology_section(
    connection: Connection[Any], slug: str, locale: str = "en"
) -> dict[str, Any] | None:
    use_ru = locale == "ru"
    return fetch_one(
        connection,
        """
        SELECT
            slug,
            CASE WHEN %s THEN title_ru ELSE title END AS title,
            CASE WHEN %s THEN summary_ru ELSE summary END AS summary,
            CASE WHEN %s THEN body_ru ELSE body END AS body,
            section_type,
            display_order,
            updated_at
        FROM methodology_sections
        WHERE slug = %s
          AND status = 'published'
        """,
        (use_ru, use_ru, use_ru, slug),
    )
