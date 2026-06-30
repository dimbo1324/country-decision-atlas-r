from app.repositories import data_quality as data_quality_repository
from psycopg import Connection
from typing import Any


def list_enabled_feature_flags_without_access_rules(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT ff.key, ff.status, ff.access_tier
        FROM feature_flags ff
        LEFT JOIN feature_access_rules far ON far.feature_key = ff.key
        WHERE ff.status IN ('enabled', 'internal')
        GROUP BY ff.key, ff.status, ff.access_tier
        HAVING COUNT(far.id) = 0
        ORDER BY ff.key
        """,
        (),
    )


def list_disabled_feature_flags_without_access_rules(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT ff.key, ff.status, ff.access_tier
        FROM feature_flags ff
        LEFT JOIN feature_access_rules far ON far.feature_key = ff.key
        WHERE ff.status = 'disabled'
        GROUP BY ff.key, ff.status, ff.access_tier
        HAVING COUNT(far.id) = 0
        ORDER BY ff.key
        """,
        (),
    )


def list_data_journal_events_with_internal_payload_fields(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT id::text AS id, event_type, country_slug
        FROM domain_events
        WHERE event_type IN (
            'legal_signal.published',
            'legal_signal_event.published',
            'route.published',
            'user_story.published'
        )
          AND payload ?| ARRAY[
              'changed_by',
              'admin',
              'admin_identity',
              'internal_metadata',
              'raw_diff',
              'changes',
              'last_error',
              'attempts',
              'status'
          ]
        ORDER BY created_at DESC
        """,
        (),
    )


def list_data_journal_events_referencing_non_public_content(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        SELECT
            de.id::text AS id,
            de.event_type,
            de.aggregate_type,
            de.aggregate_id::text,
            de.country_slug
        FROM domain_events de
        LEFT JOIN legal_signals ls
            ON de.aggregate_type = 'legal_signal'
            AND ls.id = de.aggregate_id
        LEFT JOIN routes r
            ON de.aggregate_type = 'route'
            AND r.id = de.aggregate_id
        WHERE de.event_type IN ('legal_signal.published', 'route.published')
          AND (
              (de.aggregate_type = 'legal_signal' AND COALESCE(ls.status, '') <> 'published')
              OR (de.aggregate_type = 'route' AND COALESCE(r.status, '') <> 'published')
          )
        ORDER BY de.created_at DESC
        """,
        (),
    )
