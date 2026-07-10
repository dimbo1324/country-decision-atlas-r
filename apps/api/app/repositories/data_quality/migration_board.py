from app.core.database import fetch_all
from psycopg import Connection
from typing import Any


def list_published_migration_board_posts_without_approval(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT id::text AS id, status, moderation_status
        FROM migration_board_posts
        WHERE status = 'published' AND moderation_status <> 'approved'
        """,
    )


def list_published_migration_board_posts_without_acknowledgements(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            risk_acknowledged,
            legal_disclaimer_acknowledged
        FROM migration_board_posts
        WHERE status = 'published'
          AND (
              risk_acknowledged IS NOT TRUE
              OR legal_disclaimer_acknowledged IS NOT TRUE
          )
        """,
    )


def list_migration_board_posts_with_route_country_mismatch(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            mbp.id::text AS id,
            mbp.destination_country_id::text AS destination_country_id,
            r.country_id::text AS route_country_id
        FROM migration_board_posts mbp
        JOIN routes r ON r.id = mbp.route_id
        WHERE r.country_id <> mbp.destination_country_id
        """,
    )


def list_published_public_migration_board_posts_text(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    """Candidate rows for the PII data-quality check (P2-8, Аудит-эпизод 10).

    See app.repositories.data_quality.author_metrics.
    list_published_public_author_metrics_text for why this returns
    unfiltered candidates instead of matching a hand-written PostgreSQL
    regex duplicate of app.services.pii_patterns.PII_PATTERNS — the same
    POSIX-vs-PCRE dialect gap applies here.
    """
    return fetch_all(
        connection,
        """
        SELECT id::text AS id, title, summary
        FROM migration_board_posts
        WHERE status = 'published'
          AND moderation_status = 'approved'
          AND visibility IN ('public', 'members_only')
        """,
    )


def list_invalid_migration_board_contact_requests(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            mbcr.id::text AS id,
            mbcr.status,
            mbp.status AS post_status,
            mbp.moderation_status AS post_moderation_status,
            mbcr.from_user_id::text AS from_user_id,
            mbcr.to_user_id::text AS to_user_id
        FROM migration_board_contact_requests mbcr
        JOIN migration_board_posts mbp ON mbp.id = mbcr.post_id
        WHERE mbcr.from_user_id = mbcr.to_user_id
          OR mbcr.status NOT IN (
              'pending',
              'accepted',
              'declined',
              'cancelled',
              'expired',
              'reported'
          )
          OR (
              mbcr.status = 'pending'
              AND (
                  mbp.status <> 'published'
                  OR mbp.moderation_status <> 'approved'
                  OR mbp.contact_requests_enabled IS NOT TRUE
              )
          )
          OR EXISTS (
              SELECT 1
              FROM migration_board_blocks mbb
              WHERE (
                  mbb.blocker_user_id = mbcr.from_user_id
                  AND mbb.blocked_user_id = mbcr.to_user_id
              ) OR (
                  mbb.blocker_user_id = mbcr.to_user_id
                  AND mbb.blocked_user_id = mbcr.from_user_id
              )
          )
        """,
    )


def list_duplicate_pending_migration_board_contact_requests(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            post_id::text AS post_id,
            from_user_id::text AS from_user_id,
            COUNT(*) AS duplicate_count
        FROM migration_board_contact_requests
        WHERE status = 'pending'
        GROUP BY post_id, from_user_id
        HAVING COUNT(*) > 1
        """,
    )


def list_invalid_migration_board_reports(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            status,
            reason,
            reviewed_by::text AS reviewed_by,
            reviewed_at
        FROM migration_board_reports
        WHERE (
            post_id IS NULL AND contact_request_id IS NULL
        )
          OR reason NOT IN (
              'spam',
              'scam',
              'abuse',
              'privacy',
              'misleading',
              'unsafe_contact',
              'off_topic',
              'other'
          )
          OR status NOT IN ('pending', 'reviewing', 'resolved', 'dismissed')
          OR (
              status IN ('resolved', 'dismissed')
              AND (reviewed_by IS NULL OR reviewed_at IS NULL)
          )
        """,
    )


def list_invalid_migration_board_blocks(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            blocker_user_id::text AS blocker_user_id,
            blocked_user_id::text AS blocked_user_id
        FROM migration_board_blocks
        WHERE blocker_user_id = blocked_user_id
        """,
    )


def list_open_threads_without_active_contact(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            ct.id::text AS id,
            ct.status,
            ct.contact_request_id::text AS contact_request_id,
            mbcr.status AS contact_request_status
        FROM contact_threads ct
        JOIN migration_board_contact_requests mbcr
            ON mbcr.id = ct.contact_request_id
        WHERE ct.status = 'open' AND mbcr.status <> 'accepted'
        """,
    )


def list_thread_messages_after_thread_closed(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            tm.id::text AS id,
            tm.thread_id::text AS thread_id,
            tm.created_at,
            ct.closed_at
        FROM thread_messages tm
        JOIN contact_threads ct ON ct.id = tm.thread_id
        WHERE ct.status = 'closed' AND tm.created_at > ct.closed_at
        """,
    )


def list_thread_messages_after_block(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            tm.id::text AS id,
            tm.thread_id::text AS thread_id,
            tm.created_at,
            mbb.created_at AS block_created_at
        FROM thread_messages tm
        JOIN contact_threads ct ON ct.id = tm.thread_id
        JOIN migration_board_contact_requests mbcr
            ON mbcr.id = ct.contact_request_id
        JOIN migration_board_blocks mbb ON (
            (
                mbb.blocker_user_id = mbcr.from_user_id
                AND mbb.blocked_user_id = mbcr.to_user_id
            ) OR (
                mbb.blocker_user_id = mbcr.to_user_id
                AND mbb.blocked_user_id = mbcr.from_user_id
            )
        )
        WHERE tm.created_at > mbb.created_at
        """,
    )
