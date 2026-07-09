from app.core.database import execute_one, fetch_all, fetch_one
from app.repositories.migration_board import posts
from psycopg import Connection
from typing import Any


def block_user(
    connection: Connection[Any],
    *,
    blocker_user_id: str,
    blocked_user_id: str,
    reason: str | None,
) -> dict[str, Any]:
    return execute_one(
        connection,
        """
        INSERT INTO migration_board_blocks (
            blocker_user_id,
            blocked_user_id,
            reason
        )
        VALUES (%s::uuid, %s::uuid, %s)
        ON CONFLICT (blocker_user_id, blocked_user_id) DO UPDATE
        SET reason = COALESCE(EXCLUDED.reason, migration_board_blocks.reason)
        RETURNING
            id::text AS id,
            blocked_user_id::text AS blocked_user_id,
            (
                SELECT display_name
                FROM users
                WHERE id = migration_board_blocks.blocked_user_id
            ) AS blocked_user_display_name,
            created_at,
            reason
        """,
        (blocker_user_id, blocked_user_id, reason),
    )


def unblock_user(
    connection: Connection[Any], *, blocker_user_id: str, blocked_user_id: str
) -> bool:
    cursor = connection.execute(
        """
        DELETE FROM migration_board_blocks
        WHERE blocker_user_id = %s::uuid AND blocked_user_id = %s::uuid
        """,
        (blocker_user_id, blocked_user_id),
    )
    return cursor.rowcount > 0


def is_user_blocked(
    connection: Connection[Any], *, user_a_id: str, user_b_id: str
) -> bool:
    row = fetch_one(
        connection,
        """
        SELECT 1
        FROM migration_board_blocks
        WHERE (
            blocker_user_id = %s::uuid AND blocked_user_id = %s::uuid
        ) OR (
            blocker_user_id = %s::uuid AND blocked_user_id = %s::uuid
        )
        """,
        (user_a_id, user_b_id, user_b_id, user_a_id),
    )
    return row is not None


def list_blocked_users(
    connection: Connection[Any], user_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            mbb.id::text AS id,
            mbb.blocked_user_id::text AS blocked_user_id,
            u.display_name AS blocked_user_display_name,
            mbb.created_at,
            mbb.reason
        FROM migration_board_blocks mbb
        JOIN users u ON u.id = mbb.blocked_user_id
        WHERE mbb.blocker_user_id = %s::uuid
        ORDER BY mbb.created_at DESC
        """,
        (user_id,),
    )


def list_potential_companion_posts(
    connection: Connection[Any],
    *,
    source_post: dict[str, Any],
    user_id: str,
    limit: int,
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        SELECT
            {posts.POST_SELECT}
        {posts.POST_JOINS}
        WHERE mbp.status = 'published'
          AND mbp.moderation_status = 'approved'
          AND mbp.visibility IN ('public', 'members_only')
          AND mbp.user_id::text <> %s
          AND mbp.destination_country_id = %s::uuid
          AND NOT EXISTS (
              SELECT 1
              FROM migration_board_blocks mbb
              WHERE (
                  mbb.blocker_user_id = %s::uuid
                  AND mbb.blocked_user_id = mbp.user_id
              ) OR (
                  mbb.blocked_user_id = %s::uuid
                  AND mbb.blocker_user_id = mbp.user_id
              )
          )
        ORDER BY
            (mbp.route_id = %s::uuid) DESC,
            (mbp.timeline_window = %s) DESC,
            (mbp.scenario_slug = %s) DESC,
            mbp.published_at DESC NULLS LAST
        LIMIT %s
        """,
        (
            user_id,
            source_post["destination_country_id"],
            user_id,
            user_id,
            source_post.get("route_id"),
            source_post.get("timeline_window"),
            source_post.get("scenario_slug"),
            limit,
        ),
    )


def get_country_by_slug(
    connection: Connection[Any], slug: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        "SELECT id::text AS id, slug, COALESCE(name, slug) AS name FROM countries WHERE slug = %s",
        (slug,),
    )


def get_route_for_validation(
    connection: Connection[Any], route_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        SELECT id::text AS id, country_id::text AS country_id, slug, title
        FROM routes
        WHERE id = %s::uuid
        """,
        (route_id,),
    )


def scenario_exists(connection: Connection[Any], slug: str) -> bool:
    row = fetch_one(
        connection,
        "SELECT 1 FROM scenarios WHERE slug = %s AND is_active = TRUE",
        (slug,),
    )
    return row is not None


def persona_exists(connection: Connection[Any], slug: str) -> bool:
    row = fetch_one(
        connection,
        "SELECT 1 FROM personas WHERE slug = %s AND is_active = TRUE",
        (slug,),
    )
    return row is not None


def user_exists(connection: Connection[Any], user_id: str) -> bool:
    row = fetch_one(
        connection, "SELECT 1 FROM users WHERE id = %s::uuid", (user_id,)
    )
    return row is not None
