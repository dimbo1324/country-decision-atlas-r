from app.repositories import data_quality as data_quality_repository
from app.repositories.data_quality._shared import (
    MVP_COUNTRY_SLUGS,
)
from psycopg import Connection
from typing import Any


def list_mvp_countries_without_legal_events(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT c.slug AS country_slug
        FROM countries c
        WHERE c.slug = ANY(%s)
          AND c.is_active = TRUE
          AND NOT EXISTS (
              SELECT 1
              FROM legal_signals ls
              JOIN legal_signal_events lse ON lse.legal_signal_id = ls.id
              WHERE ls.country_id = c.id
          )
        ORDER BY c.slug
        """,
        (list(MVP_COUNTRY_SLUGS),),
    )


def list_published_legal_signals_with_missing_legal_status(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT id::text AS id, title, legal_status
        FROM legal_signals
        WHERE status = 'published'
          AND COALESCE(BTRIM(legal_status), '') = ''
        ORDER BY title
        """,
        (),
    )


def list_published_legal_signals_with_unknown_legal_status(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT id::text AS id, title, legal_status
        FROM legal_signals
        WHERE status = 'published'
          AND legal_status = 'unknown'
        ORDER BY title
        """,
        (),
    )


def list_review_sources_with_missing_required_fields(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            title,
            CASE
                WHEN COALESCE(BTRIM(title), '') = '' THEN 'title'
                WHEN COALESCE(BTRIM(url), '') = '' THEN 'url'
                WHEN COALESCE(BTRIM(source_type), '') = '' THEN 'source_type'
                WHEN COALESCE(BTRIM(publisher), '') = '' THEN 'publisher'
                WHEN COALESCE(confidence, reliability_level) IS NULL THEN 'confidence'
                ELSE 'unknown'
            END AS missing_field
        FROM sources
        WHERE status = 'review'
          AND (
              COALESCE(BTRIM(title), '') = ''
              OR COALESCE(BTRIM(url), '') = ''
              OR COALESCE(BTRIM(source_type), '') = ''
              OR COALESCE(BTRIM(publisher), '') = ''
              OR COALESCE(confidence, reliability_level) IS NULL
          )
        ORDER BY title
        """,
        (),
    )


def list_review_evidence_items_with_missing_required_fields(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            title,
            claim,
            CASE
                WHEN source_id IS NULL THEN 'source_id'
                WHEN country_id IS NULL THEN 'country_id'
                WHEN COALESCE(BTRIM(claim), BTRIM(title), '') = '' THEN 'claim'
                WHEN COALESCE(confidence, confidence_level) IS NULL THEN 'confidence'
                WHEN COALESCE(BTRIM(url), BTRIM(excerpt), BTRIM(quote), '') = '' THEN 'excerpt'
                ELSE 'unknown'
            END AS missing_field
        FROM evidence_items
        WHERE status = 'review'
          AND (
              source_id IS NULL
              OR country_id IS NULL
              OR COALESCE(BTRIM(claim), BTRIM(title), '') = ''
              OR COALESCE(confidence, confidence_level) IS NULL
              OR COALESCE(BTRIM(url), BTRIM(excerpt), BTRIM(quote), '') = ''
          )
        ORDER BY title
        """,
        (),
    )


def list_review_legal_signals_with_missing_required_fields(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            title,
            CASE
                WHEN country_id IS NULL THEN 'country_id'
                WHEN source_id IS NULL THEN 'source_id'
                WHEN COALESCE(BTRIM(signal_type), '') = '' THEN 'signal_type'
                WHEN COALESCE(BTRIM(impact_direction), '') = '' THEN 'impact_direction'
                WHEN COALESCE(BTRIM(impact_level), '') = '' THEN 'impact_level'
                WHEN COALESCE(BTRIM(title_en), BTRIM(title), '') = '' THEN 'title_en'
                WHEN COALESCE(BTRIM(summary_en), BTRIM(summary), '') = '' THEN 'summary_en'
                WHEN COALESCE(confidence, confidence_level) IS NULL THEN 'confidence'
                WHEN COALESCE(BTRIM(legal_status), '') = '' THEN 'legal_status'
                ELSE 'unknown'
            END AS missing_field
        FROM legal_signals
        WHERE status = 'review'
          AND (
              country_id IS NULL
              OR source_id IS NULL
              OR COALESCE(BTRIM(signal_type), '') = ''
              OR COALESCE(BTRIM(impact_direction), '') = ''
              OR COALESCE(BTRIM(impact_level), '') = ''
              OR COALESCE(BTRIM(title_en), BTRIM(title), '') = ''
              OR COALESCE(BTRIM(summary_en), BTRIM(summary), '') = ''
              OR COALESCE(confidence, confidence_level) IS NULL
              OR COALESCE(BTRIM(legal_status), '') = ''
          )
        ORDER BY title
        """,
        (),
    )


def list_published_evidence_items_with_missing_required_fields(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            title,
            claim,
            CASE
                WHEN source_id IS NULL THEN 'source_id'
                WHEN country_id IS NULL THEN 'country_id'
                WHEN COALESCE(BTRIM(claim), BTRIM(title), '') = '' THEN 'claim'
                WHEN COALESCE(confidence, confidence_level) IS NULL THEN 'confidence'
                WHEN COALESCE(BTRIM(url), BTRIM(excerpt), BTRIM(quote), '') = '' THEN 'excerpt'
                ELSE 'unknown'
            END AS missing_field
        FROM evidence_items
        WHERE status = 'published'
          AND (
              source_id IS NULL
              OR country_id IS NULL
              OR COALESCE(BTRIM(claim), BTRIM(title), '') = ''
              OR COALESCE(confidence, confidence_level) IS NULL
              OR COALESCE(BTRIM(url), BTRIM(excerpt), BTRIM(quote), '') = ''
          )
        ORDER BY title
        """,
        (),
    )


def list_published_legal_signals_with_missing_required_fields(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            title,
            CASE
                WHEN country_id IS NULL THEN 'country_id'
                WHEN source_id IS NULL THEN 'source_id'
                WHEN COALESCE(BTRIM(signal_type), '') = '' THEN 'signal_type'
                WHEN COALESCE(BTRIM(impact_direction), '') = '' THEN 'impact_direction'
                WHEN COALESCE(BTRIM(impact_level), '') = '' THEN 'impact_level'
                WHEN COALESCE(BTRIM(title_en), BTRIM(title), '') = '' THEN 'title_en'
                WHEN COALESCE(BTRIM(summary_en), BTRIM(summary), '') = '' THEN 'summary_en'
                WHEN COALESCE(confidence, confidence_level) IS NULL THEN 'confidence'
                ELSE 'unknown'
            END AS missing_field
        FROM legal_signals
        WHERE status = 'published'
          AND (
              country_id IS NULL
              OR source_id IS NULL
              OR COALESCE(BTRIM(signal_type), '') = ''
              OR COALESCE(BTRIM(impact_direction), '') = ''
              OR COALESCE(BTRIM(impact_level), '') = ''
              OR COALESCE(BTRIM(title_en), BTRIM(title), '') = ''
              OR COALESCE(BTRIM(summary_en), BTRIM(summary), '') = ''
              OR COALESCE(confidence, confidence_level) IS NULL
          )
        ORDER BY title
        """,
        (),
    )


def list_invalid_domain_events_for_dq(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            event_key,
            event_type,
            aggregate_type,
            aggregate_id::text AS aggregate_id,
            status,
            attempts,
            payload
        FROM domain_events
        WHERE COALESCE(BTRIM(event_key), '') = ''
           OR COALESCE(BTRIM(event_type), '') = ''
           OR COALESCE(BTRIM(aggregate_type), '') = ''
           OR aggregate_id IS NULL
           OR payload IS NULL
           OR attempts < 0
           OR status NOT IN ('pending', 'relayed', 'skipped', 'failed')
           OR event_type NOT IN (
               'legal_signal.published',
               'legal_signal_event.published',
               'route.published',
               'user_story.published',
               'drift.changed'
           )
        ORDER BY id
        """,
        (),
    )


def count_domain_events_for_dq(connection: Connection[Any]) -> int:
    rows = data_quality_repository.fetch_all(
        connection,
        "SELECT COUNT(*)::int AS count FROM domain_events",
        (),
    )
    return int(rows[0]["count"]) if rows else 0
