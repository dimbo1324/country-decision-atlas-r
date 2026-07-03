from app.core.database import fetch_all, fetch_one
from collections.abc import Mapping
from psycopg import Connection
from psycopg.types.json import Jsonb
from typing import Any


AI_DRAFT_FIELDS = """
    id,
    draft_type,
    status,
    country_slug,
    route_id,
    legal_signal_id,
    source_id,
    evidence_item_id,
    title,
    body,
    summary,
    detected_issue,
    provider,
    model_name,
    model_version,
    input_context,
    citations,
    confidence,
    reviewed_by,
    reviewed_at,
    created_at,
    updated_at
"""


def insert_ai_draft(
    conn: Connection[Any],
    *,
    draft_type: str,
    country_slug: str | None,
    route_id: str | None,
    legal_signal_id: str | None,
    source_id: str | None,
    evidence_item_id: str | None,
    title: str,
    body: str,
    summary: str | None,
    detected_issue: str | None,
    provider: str,
    model_name: str,
    model_version: str,
    input_context: Mapping[str, Any],
    citations: list[dict[str, Any]],
    confidence: str,
) -> dict[str, Any]:
    row = fetch_one(
        conn,
        f"""
        INSERT INTO ai_drafts (
            draft_type,
            country_slug,
            route_id,
            legal_signal_id,
            source_id,
            evidence_item_id,
            title,
            body,
            summary,
            detected_issue,
            provider,
            model_name,
            model_version,
            input_context,
            citations,
            confidence
        )
        VALUES (
            %s, %s, %s::uuid, %s::uuid, %s::uuid, %s::uuid,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        RETURNING {AI_DRAFT_FIELDS}
        """,
        (
            draft_type,
            country_slug,
            route_id,
            legal_signal_id,
            source_id,
            evidence_item_id,
            title,
            body,
            summary,
            detected_issue,
            provider,
            model_name,
            model_version,
            Jsonb(dict(input_context)),
            Jsonb(list(citations)),
            confidence,
        ),
    )
    if row is None:
        raise RuntimeError("Expected ai_drafts insert to return a row.")
    return row


def get_ai_draft(conn: Connection[Any], draft_id: str) -> dict[str, Any] | None:
    return fetch_one(
        conn,
        f"""
        SELECT {AI_DRAFT_FIELDS}
        FROM ai_drafts
        WHERE id = %s::uuid
        """,
        (draft_id,),
    )


def list_ai_drafts(
    conn: Connection[Any],
    *,
    status: str | None = None,
    draft_type: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        f"""
        SELECT {AI_DRAFT_FIELDS}
        FROM ai_drafts
        WHERE (%s::text IS NULL OR status = %s)
          AND (%s::text IS NULL OR draft_type = %s)
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (status, status, draft_type, draft_type, limit),
    )


def update_ai_draft_status(
    conn: Connection[Any],
    draft_id: str,
    status: str,
    reviewed_by: str | None = None,
) -> dict[str, Any] | None:
    return fetch_one(
        conn,
        f"""
        UPDATE ai_drafts
        SET
            status = %s,
            reviewed_by = COALESCE(%s, reviewed_by),
            reviewed_at = NOW(),
            updated_at = NOW()
        WHERE id = %s::uuid
        RETURNING {AI_DRAFT_FIELDS}
        """,
        (status, reviewed_by, draft_id),
    )


def count_ai_drafts(conn: Connection[Any], status: str | None = None) -> int:
    row = fetch_one(
        conn,
        """
        SELECT COUNT(*) AS total
        FROM ai_drafts
        WHERE (%s::text IS NULL OR status = %s)
        """,
        (status, status),
    )
    return int(row["total"]) if row else 0
