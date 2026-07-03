from app.core.database import fetch_all, fetch_one
from psycopg import Connection
from psycopg.types.json import Jsonb
from typing import Any


CONTRADICTION_CANDIDATE_FIELDS = """
    id,
    country_slug,
    topic,
    entity_type,
    entity_id,
    severity,
    status,
    summary,
    claim_a,
    claim_b,
    source_ids,
    evidence_item_ids,
    detected_by,
    provider,
    model_name,
    model_version,
    confidence,
    reviewed_at,
    reviewed_by,
    created_at,
    updated_at
"""


def insert_contradiction_candidate(
    conn: Connection[Any],
    *,
    country_slug: str | None,
    topic: str,
    entity_type: str | None,
    entity_id: str | None,
    severity: str,
    summary: str,
    claim_a: str,
    claim_b: str,
    source_ids: list[Any],
    evidence_item_ids: list[Any],
    detected_by: str,
    provider: str,
    model_name: str,
    model_version: str,
    confidence: str,
) -> dict[str, Any]:
    row = fetch_one(
        conn,
        f"""
        INSERT INTO contradiction_candidates (
            country_slug,
            topic,
            entity_type,
            entity_id,
            severity,
            summary,
            claim_a,
            claim_b,
            source_ids,
            evidence_item_ids,
            detected_by,
            provider,
            model_name,
            model_version,
            confidence
        )
        VALUES (
            %s, %s, %s, %s::uuid, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s
        )
        RETURNING {CONTRADICTION_CANDIDATE_FIELDS}
        """,
        (
            country_slug,
            topic,
            entity_type,
            entity_id,
            severity,
            summary,
            claim_a,
            claim_b,
            Jsonb(list(source_ids)),
            Jsonb(list(evidence_item_ids)),
            detected_by,
            provider,
            model_name,
            model_version,
            confidence,
        ),
    )
    if row is None:
        raise RuntimeError("Expected contradiction_candidates insert to return a row.")
    return row


def get_contradiction_candidate(
    conn: Connection[Any], candidate_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        conn,
        f"""
        SELECT {CONTRADICTION_CANDIDATE_FIELDS}
        FROM contradiction_candidates
        WHERE id = %s::uuid
        """,
        (candidate_id,),
    )


def list_contradiction_candidates(
    conn: Connection[Any],
    *,
    status: str | None = None,
    severity: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        f"""
        SELECT {CONTRADICTION_CANDIDATE_FIELDS}
        FROM contradiction_candidates
        WHERE (%s::text IS NULL OR status = %s)
          AND (%s::text IS NULL OR severity = %s)
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (status, status, severity, severity, limit),
    )


def update_contradiction_candidate_status(
    conn: Connection[Any],
    candidate_id: str,
    status: str,
    reviewed_by: str | None = None,
) -> dict[str, Any] | None:
    return fetch_one(
        conn,
        f"""
        UPDATE contradiction_candidates
        SET
            status = %s,
            reviewed_by = COALESCE(%s, reviewed_by),
            reviewed_at = NOW(),
            updated_at = NOW()
        WHERE id = %s::uuid
        RETURNING {CONTRADICTION_CANDIDATE_FIELDS}
        """,
        (status, reviewed_by, candidate_id),
    )


def count_contradiction_candidates(
    conn: Connection[Any], status: str | None = None
) -> int:
    row = fetch_one(
        conn,
        """
        SELECT COUNT(*) AS total
        FROM contradiction_candidates
        WHERE (%s::text IS NULL OR status = %s)
        """,
        (status, status),
    )
    return int(row["total"]) if row else 0
