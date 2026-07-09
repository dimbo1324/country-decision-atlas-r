from app.core.database import execute_one, fetch_all, fetch_one
from psycopg import Connection
from typing import Any


PROPOSAL_FIELDS = """
    cp.id,
    cp.proposer_user_id,
    cp.country_id,
    cp.slug,
    cp.name_en,
    cp.name_ru,
    cp.iso2,
    cp.iso3,
    cp.justification,
    cp.status,
    cp.curator_user_id,
    cp.readiness_snapshot,
    cp.moderated_by,
    cp.moderated_at,
    cp.moderation_reason,
    cp.created_at,
    cp.updated_at,
    cp.published_at,
    c.is_active AS country_is_active,
    c.is_demo AS country_is_demo
"""


def country_slug_exists(connection: Connection[Any], slug: str) -> bool:
    return (
        fetch_one(
            connection, "SELECT 1 FROM countries WHERE slug = %s", (slug,)
        )
        is not None
    )


def country_iso_exists(
    connection: Connection[Any], iso2: str, iso3: str
) -> bool:
    return (
        fetch_one(
            connection,
            "SELECT 1 FROM countries WHERE iso2 = %s OR iso3 = %s",
            (iso2, iso3),
        )
        is not None
    )


def create_country_shell(
    connection: Connection[Any],
    *,
    slug: str,
    iso2: str,
    iso3: str,
    name_en: str,
) -> dict[str, Any]:
    return execute_one(
        connection,
        """
        INSERT INTO countries (slug, iso2, iso3, name, is_active, is_demo)
        VALUES (%s, %s, %s, %s, FALSE, FALSE)
        RETURNING id, slug
        """,
        (slug, iso2, iso3, name_en),
    )


def create_country_name_translation(
    connection: Connection[Any], *, country_id: str, name_ru: str
) -> None:
    connection.execute(
        """
        INSERT INTO translations (
            entity_type, entity_id, field_name, locale_id, translated_value, status
        )
        SELECT 'country', %s::uuid, 'name', l.id, %s, 'approved'
        FROM locales l
        WHERE l.code = 'ru'
        ON CONFLICT (entity_type, entity_id, field_name, locale_id) DO UPDATE
        SET translated_value = EXCLUDED.translated_value,
            status = EXCLUDED.status
        """,
        (country_id, name_ru),
    )


def create_proposal_row(
    connection: Connection[Any],
    *,
    proposer_user_id: str,
    country_id: str,
    slug: str,
    name_en: str,
    name_ru: str,
    iso2: str,
    iso3: str,
    justification: str,
) -> dict[str, Any]:
    return execute_one(
        connection,
        """
        INSERT INTO country_proposals (
            proposer_user_id, country_id, slug, name_en, name_ru,
            iso2, iso3, justification
        )
        VALUES (%s, %s::uuid, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            proposer_user_id,
            country_id,
            slug,
            name_en,
            name_ru,
            iso2,
            iso3,
            justification,
        ),
    )


def get_proposal_by_id(
    connection: Connection[Any], proposal_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT {PROPOSAL_FIELDS}
        FROM country_proposals cp
        JOIN countries c ON c.id = cp.country_id
        WHERE cp.id = %s::uuid
        """,
        (proposal_id,),
    )


def get_proposal_for_owner(
    connection: Connection[Any], proposal_id: str, proposer_user_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT {PROPOSAL_FIELDS}
        FROM country_proposals cp
        JOIN countries c ON c.id = cp.country_id
        WHERE cp.id = %s::uuid AND cp.proposer_user_id = %s::uuid
        """,
        (proposal_id, proposer_user_id),
    )


def list_proposals_for_user(
    connection: Connection[Any],
    proposer_user_id: str,
    *,
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        SELECT {PROPOSAL_FIELDS}, COUNT(*) OVER() AS total_count
        FROM country_proposals cp
        JOIN countries c ON c.id = cp.country_id
        WHERE cp.proposer_user_id = %s::uuid
        ORDER BY cp.created_at DESC
        LIMIT %s OFFSET %s
        """,
        (proposer_user_id, limit, offset),
    )


def list_proposals_for_curation(
    connection: Connection[Any],
    *,
    status: str | None,
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    filters = ["TRUE"]
    params: list[Any] = []
    if status is not None:
        filters.append("cp.status = %s")
        params.append(status)
    where_sql = " AND ".join(filters)
    return fetch_all(
        connection,
        f"""
        SELECT {PROPOSAL_FIELDS}, COUNT(*) OVER() AS total_count
        FROM country_proposals cp
        JOIN countries c ON c.id = cp.country_id
        WHERE {where_sql}
        ORDER BY cp.created_at ASC
        LIMIT %s OFFSET %s
        """,
        (*params, limit, offset),
    )


def update_justification(
    connection: Connection[Any],
    *,
    proposal_id: str,
    proposer_user_id: str,
    justification: str,
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        UPDATE country_proposals
        SET justification = %s
        WHERE id = %s::uuid AND proposer_user_id = %s::uuid AND status = 'draft'
        RETURNING id
        """,
        (justification, proposal_id, proposer_user_id),
    )


def assign_curator(
    connection: Connection[Any], *, proposal_id: str, curator_user_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        UPDATE country_proposals
        SET curator_user_id = %s
        WHERE id = %s::uuid AND curator_user_id IS NULL
        RETURNING id
        """,
        (curator_user_id, proposal_id),
    )


def store_readiness_snapshot(
    connection: Connection[Any], *, proposal_id: str, snapshot_json: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        UPDATE country_proposals
        SET readiness_snapshot = %s::jsonb
        WHERE id = %s::uuid
        RETURNING id
        """,
        (snapshot_json, proposal_id),
    )


def apply_status_transition(
    connection: Connection[Any],
    proposal_id: str,
    *,
    old_status: str,
    new_status: str,
    moderated_by: str | None = None,
    moderation_reason: str | None = None,
    set_published_at: bool = False,
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        UPDATE country_proposals
        SET status = %s,
            moderated_by = COALESCE(%s::uuid, moderated_by),
            moderated_at = CASE WHEN %s::uuid IS NOT NULL THEN NOW() ELSE moderated_at END,
            moderation_reason = COALESCE(%s, moderation_reason),
            published_at = CASE WHEN %s THEN NOW() ELSE published_at END
        WHERE id = %s::uuid AND status = %s
        RETURNING id
        """,
        (
            new_status,
            moderated_by,
            moderated_by,
            moderation_reason,
            set_published_at,
            proposal_id,
            old_status,
        ),
    )


def set_country_active(
    connection: Connection[Any], *, country_id: str, is_active: bool
) -> None:
    connection.execute(
        "UPDATE countries SET is_active = %s WHERE id = %s::uuid",
        (is_active, country_id),
    )


def get_user_role(connection: Connection[Any], user_id: str) -> str | None:
    row = fetch_one(
        connection, "SELECT role FROM users WHERE id = %s::uuid", (user_id,)
    )
    return str(row["role"]) if row else None
