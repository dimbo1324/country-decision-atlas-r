from app.core.database import execute_one, fetch_all, fetch_one
from psycopg import Connection
from psycopg.types.json import Jsonb
from typing import Any


def insert_ai_interaction_log(
    conn: Connection[Any],
    *,
    request_type: str,
    locale: str,
    country_slug: str | None,
    scenario_slug: str | None,
    persona_slug: str | None,
    provider: str,
    provider_model: str,
    ai_mode: str,
    status: str,
    refused: bool,
    grounded: bool,
    query_hash: str | None,
    sanitized_preview: str | None,
    context_items_count: int,
    citations_count: int,
    error_code: str | None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return execute_one(
        conn,
        """
        INSERT INTO ai_interaction_logs (
            request_type,
            locale,
            country_slug,
            scenario_slug,
            persona_slug,
            provider,
            provider_model,
            ai_mode,
            status,
            refused,
            grounded,
            query_hash,
            sanitized_preview,
            context_items_count,
            citations_count,
            error_code,
            metadata
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s
        )
        RETURNING
            id::text,
            request_type,
            locale,
            status,
            refused,
            grounded,
            context_items_count,
            citations_count,
            created_at
        """,
        (
            request_type,
            locale,
            country_slug,
            scenario_slug,
            persona_slug,
            provider,
            provider_model,
            ai_mode,
            status,
            refused,
            grounded,
            query_hash,
            sanitized_preview,
            context_items_count,
            citations_count,
            error_code,
            Jsonb(metadata or {}),
        ),
    )


def count_ai_interactions(
    conn: Connection[Any], request_type: str | None = None
) -> int:
    if request_type is None:
        row = fetch_one(conn, "SELECT COUNT(*) AS total FROM ai_interaction_logs")
    else:
        row = fetch_one(
            conn,
            """
            SELECT COUNT(*) AS total
            FROM ai_interaction_logs
            WHERE request_type = %s
            """,
            (request_type,),
        )
    return int(row["total"]) if row else 0


def list_ai_interaction_logs_for_admin(
    conn: Connection[Any], limit: int = 50
) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        """
        SELECT
            id::text,
            request_type,
            locale,
            country_slug,
            scenario_slug,
            persona_slug,
            provider,
            provider_model,
            ai_mode,
            status,
            refused,
            grounded,
            query_hash,
            sanitized_preview,
            context_items_count,
            citations_count,
            error_code,
            metadata,
            created_at
        FROM ai_interaction_logs
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (limit,),
    )
