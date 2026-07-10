from app.core.database import fetch_all
from psycopg import Connection
from typing import Any


def list_published_author_metrics_without_methodology(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT id::text AS id, methodology_en, methodology_ru
        FROM author_metric_definitions
        WHERE status = 'published'
          AND (BTRIM(methodology_en) = '' OR BTRIM(methodology_ru) = '')
        """,
    )


def list_author_metric_values_missing_source_or_experience(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            metric_id::text AS metric_id,
            country_id::text AS country_id
        FROM author_metric_values
        WHERE source_url IS NULL AND is_personal_experience IS NOT TRUE
        """,
    )


def list_author_metric_values_out_of_scale(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            amv.id::text AS id,
            amv.metric_id::text AS metric_id,
            amv.value,
            amd.scale_min,
            amd.scale_max
        FROM author_metric_values amv
        JOIN author_metric_definitions amd ON amd.id = amv.metric_id
        WHERE amv.value < amd.scale_min OR amv.value > amd.scale_max
        """,
    )


def list_published_public_author_metrics_text(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    """Candidate rows for the PII data-quality check (P2-8, Аудит-эпизод 10).

    PII detection itself runs in Python against these fetched rows
    (services.data_quality.author_metrics_checks), using the same
    app.services.pii_patterns.PII_PATTERNS as every other PII check in the
    codebase. This used to be a hand-written PostgreSQL regex duplicate of
    those patterns, translated into POSIX ERE syntax (no lookbehind/word-
    boundary support) — it had already drifted from the Python patterns by
    the time of the audit and could never be made byte-identical to them
    given the regex-dialect gap.
    """
    return fetch_all(
        connection,
        """
        SELECT id::text AS id, name_en, name_ru, methodology_en, methodology_ru
        FROM author_metric_definitions
        WHERE status = 'published' AND visibility = 'public'
        """,
    )


def list_author_metrics_with_dangling_fork_lineage(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT amd.id::text AS id, amd.forked_from_id::text AS forked_from_id
        FROM author_metric_definitions amd
        WHERE amd.forked_from_id IS NOT NULL
          AND NOT EXISTS (
              SELECT 1
              FROM author_metric_definitions parent
              WHERE parent.id = amd.forked_from_id
          )
        """,
    )
