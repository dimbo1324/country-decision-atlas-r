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


def list_migration_board_public_posts_with_pii(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT id::text AS id, title, summary
        FROM migration_board_posts
        WHERE status = 'published'
          AND moderation_status = 'approved'
          AND visibility IN ('public', 'members_only')
          AND (
              title ~* '[A-Z0-9._%%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}'
              OR summary ~* '[A-Z0-9._%%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}'
              OR title ~* '(^|[^A-Za-z0-9_])@[A-Za-z0-9_]{4,32}'
              OR summary ~* '(^|[^A-Za-z0-9_])@[A-Za-z0-9_]{4,32}'
              OR title ~* 'https?://|www\\.'
              OR summary ~* 'https?://|www\\.'
              OR title ~ '(\\+?\\d[\\s().-]*){8,}'
              OR summary ~ '(\\+?\\d[\\s().-]*){8,}'
          )
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
