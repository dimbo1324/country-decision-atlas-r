from app.core.database import execute_one, fetch_all, fetch_one
from psycopg import Connection
from typing import Any


DEFINITION_SELECT = """
    amd.id::text AS id,
    amd.author_user_id::text AS author_user_id,
    u.display_name AS author_display_name,
    amd.slug,
    amd.name_en,
    amd.name_ru,
    amd.methodology_en,
    amd.methodology_ru,
    amd.polarity,
    amd.scale_min,
    amd.scale_max,
    amd.license,
    amd.status,
    amd.visibility,
    amd.forked_from_id::text AS forked_from_id,
    amd.version,
    amd.created_at,
    amd.updated_at,
    amd.submitted_at,
    amd.published_at,
    amd.archived_at,
    amd.rejected_at,
    amd.moderated_by::text AS moderated_by,
    amd.moderated_at,
    amd.moderation_reason
"""

DEFINITION_JOINS = """
FROM author_metric_definitions amd
JOIN users u ON u.id = amd.author_user_id
"""


def create_definition(
    connection: Connection[Any],
    *,
    author_user_id: str,
    slug: str,
    name_en: str,
    name_ru: str,
    methodology_en: str,
    methodology_ru: str,
    polarity: str,
    scale_min: float,
    scale_max: float,
    license: str,
    visibility: str,
    forked_from_id: str | None,
) -> dict[str, Any]:
    row = execute_one(
        connection,
        """
        INSERT INTO author_metric_definitions (
            author_user_id,
            slug,
            name_en,
            name_ru,
            methodology_en,
            methodology_ru,
            polarity,
            scale_min,
            scale_max,
            license,
            visibility,
            forked_from_id
        )
        VALUES (
            %s::uuid, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::uuid
        )
        RETURNING id::text AS id
        """,
        (
            author_user_id,
            slug,
            name_en,
            name_ru,
            methodology_en,
            methodology_ru,
            polarity,
            scale_min,
            scale_max,
            license,
            visibility,
            forked_from_id,
        ),
    )
    definition = get_definition_by_id(connection, str(row["id"]))
    if definition is None:
        raise RuntimeError(
            "Expected author metric definition to exist after insert."
        )
    return definition


def update_definition(
    connection: Connection[Any],
    *,
    definition_id: str,
    name_en: str | None,
    name_ru: str | None,
    methodology_en: str | None,
    methodology_ru: str | None,
    polarity: str | None,
    scale_min: float | None,
    scale_max: float | None,
    license: str | None,
    visibility: str | None,
    reset_to_review: bool,
) -> dict[str, Any] | None:
    row = fetch_one(
        connection,
        """
        UPDATE author_metric_definitions
        SET
            name_en = COALESCE(%s, name_en),
            name_ru = COALESCE(%s, name_ru),
            methodology_en = COALESCE(%s, methodology_en),
            methodology_ru = COALESCE(%s, methodology_ru),
            polarity = COALESCE(%s, polarity),
            scale_min = COALESCE(%s, scale_min),
            scale_max = COALESCE(%s, scale_max),
            license = COALESCE(%s, license),
            visibility = COALESCE(%s, visibility),
            status = CASE WHEN %s THEN 'review' ELSE status END,
            published_at = CASE WHEN %s THEN NULL ELSE published_at END,
            version = CASE WHEN %s THEN version + 1 ELSE version END,
            updated_at = NOW()
        WHERE id::text = %s
        RETURNING id::text AS id
        """,
        (
            name_en,
            name_ru,
            methodology_en,
            methodology_ru,
            polarity,
            scale_min,
            scale_max,
            license,
            visibility,
            reset_to_review,
            reset_to_review,
            reset_to_review,
            definition_id,
        ),
    )
    return get_definition_by_id(connection, definition_id) if row else None


def get_definition_by_id(
    connection: Connection[Any], definition_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {DEFINITION_SELECT}
        {DEFINITION_JOINS}
        WHERE amd.id::text = %s
        """,
        (definition_id,),
    )


def get_definition_for_author(
    connection: Connection[Any], definition_id: str, author_user_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {DEFINITION_SELECT}
        {DEFINITION_JOINS}
        WHERE amd.id::text = %s AND amd.author_user_id::text = %s
        """,
        (definition_id, author_user_id),
    )


def get_definition_by_author_slug(
    connection: Connection[Any], author_user_id: str, slug: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {DEFINITION_SELECT}
        {DEFINITION_JOINS}
        WHERE amd.author_user_id::text = %s AND amd.slug = %s
        """,
        (author_user_id, slug),
    )


def list_definitions_for_author(
    connection: Connection[Any], author_user_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        SELECT
            {DEFINITION_SELECT}
        {DEFINITION_JOINS}
        WHERE amd.author_user_id::text = %s
        ORDER BY amd.updated_at DESC, amd.created_at DESC
        """,
        (author_user_id,),
    )


def list_published_definitions_for_author(
    connection: Connection[Any], author_user_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        SELECT
            {DEFINITION_SELECT}
        {DEFINITION_JOINS}
        WHERE amd.author_user_id::text = %s
          AND amd.status = 'published'
          AND amd.visibility = 'public'
        ORDER BY amd.published_at DESC NULLS LAST
        """,
        (author_user_id,),
    )


def list_published_definitions_for_country(
    connection: Connection[Any], country_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        SELECT
            {DEFINITION_SELECT},
            amv.value,
            amv.source_url,
            amv.is_personal_experience,
            amv.note,
            amv.valid_as_of,
            amv.updated_at AS value_updated_at
        {DEFINITION_JOINS}
        JOIN author_metric_values amv ON amv.metric_id = amd.id
        WHERE amv.country_id::text = %s
          AND amd.status = 'published'
          AND amd.visibility = 'public'
        ORDER BY amd.published_at DESC NULLS LAST
        """,
        (country_id,),
    )


def list_definitions_for_moderation(
    connection: Connection[Any], *, status: str | None, limit: int, offset: int
) -> list[dict[str, Any]]:
    filters = []
    params: list[Any] = []
    if status is not None:
        filters.append("amd.status = %s")
        params.append(status)
    where_sql = " AND ".join(filters) if filters else "TRUE"
    return fetch_all(
        connection,
        f"""
        SELECT
            {DEFINITION_SELECT},
            COUNT(*) OVER() AS total_count
        {DEFINITION_JOINS}
        WHERE {where_sql}
        ORDER BY
            CASE amd.status WHEN 'review' THEN 1 ELSE 2 END,
            amd.submitted_at DESC NULLS LAST,
            amd.updated_at DESC
        LIMIT %s OFFSET %s
        """,
        (*params, limit, offset),
    )


def submit_definition_for_review(
    connection: Connection[Any], definition_id: str
) -> dict[str, Any] | None:
    row = fetch_one(
        connection,
        """
        UPDATE author_metric_definitions
        SET
            status = 'review',
            submitted_at = NOW(),
            updated_at = NOW()
        WHERE id::text = %s AND status IN ('draft', 'rejected', 'archived')
        RETURNING id::text AS id
        """,
        (definition_id,),
    )
    return get_definition_by_id(connection, definition_id) if row else None


def publish_definition(
    connection: Connection[Any], *, definition_id: str, moderator_user_id: str
) -> dict[str, Any] | None:
    row = fetch_one(
        connection,
        """
        UPDATE author_metric_definitions
        SET
            status = 'published',
            moderated_by = %s::uuid,
            moderated_at = NOW(),
            moderation_reason = NULL,
            published_at = NOW(),
            rejected_at = NULL,
            updated_at = NOW()
        WHERE id::text = %s AND status = 'review'
        RETURNING id::text AS id
        """,
        (moderator_user_id, definition_id),
    )
    return get_definition_by_id(connection, definition_id) if row else None


def reject_definition(
    connection: Connection[Any],
    *,
    definition_id: str,
    moderator_user_id: str,
    reason: str | None,
) -> dict[str, Any] | None:
    row = fetch_one(
        connection,
        """
        UPDATE author_metric_definitions
        SET
            status = 'rejected',
            moderated_by = %s::uuid,
            moderated_at = NOW(),
            moderation_reason = %s,
            rejected_at = NOW(),
            published_at = NULL,
            updated_at = NOW()
        WHERE id::text = %s AND status IN ('review', 'published')
        RETURNING id::text AS id
        """,
        (moderator_user_id, reason, definition_id),
    )
    return get_definition_by_id(connection, definition_id) if row else None


def archive_definition(
    connection: Connection[Any], definition_id: str
) -> dict[str, Any] | None:
    row = fetch_one(
        connection,
        """
        UPDATE author_metric_definitions
        SET
            status = 'archived',
            archived_at = NOW(),
            published_at = NULL,
            updated_at = NOW()
        WHERE id::text = %s AND status IN ('draft', 'review', 'published', 'rejected')
        RETURNING id::text AS id
        """,
        (definition_id,),
    )
    return get_definition_by_id(connection, definition_id) if row else None
