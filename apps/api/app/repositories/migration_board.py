from app.core.database import execute_one, fetch_all, fetch_one
from psycopg import Connection
from typing import Any


POST_SELECT = """
    mbp.id::text AS id,
    mbp.user_id::text AS user_id,
    u.display_name AS author_display_name,
    mbp.origin_country_id::text AS origin_country_id,
    oc.slug AS origin_country_slug,
    COALESCE(oc.name, oc.slug) AS origin_country_name,
    mbp.destination_country_id::text AS destination_country_id,
    dc.slug AS destination_country_slug,
    COALESCE(dc.name, dc.slug) AS destination_country_name,
    mbp.route_id::text AS route_id,
    r.slug AS route_slug,
    r.title AS route_title,
    mbp.scenario_slug,
    s.name AS scenario_label,
    mbp.persona_slug,
    p.name AS persona_label,
    mbp.title,
    mbp.summary,
    mbp.target_city,
    mbp.target_month,
    mbp.timeline_window,
    mbp.budget_range,
    mbp.household_type,
    mbp.migration_stage,
    mbp.companion_goal,
    mbp.preferred_language,
    mbp.visibility,
    mbp.status,
    mbp.moderation_status,
    mbp.risk_acknowledged,
    mbp.legal_disclaimer_acknowledged,
    mbp.contact_requests_enabled,
    mbp.created_at,
    mbp.updated_at,
    mbp.submitted_at,
    mbp.published_at,
    mbp.archived_at,
    mbp.rejected_at,
    mbp.moderated_by::text AS moderated_by,
    mbp.moderated_at,
    mbp.moderation_reason,
    COALESCE(tags.tags, ARRAY[]::text[]) AS tags
"""

POST_JOINS = """
FROM migration_board_posts mbp
JOIN users u ON u.id = mbp.user_id
JOIN countries dc ON dc.id = mbp.destination_country_id
LEFT JOIN countries oc ON oc.id = mbp.origin_country_id
LEFT JOIN routes r ON r.id = mbp.route_id
LEFT JOIN scenarios s ON s.slug = mbp.scenario_slug
LEFT JOIN personas p ON p.slug = mbp.persona_slug
LEFT JOIN LATERAL (
    SELECT ARRAY_AGG(mbpt.tag ORDER BY mbpt.tag) AS tags
    FROM migration_board_post_tags mbpt
    WHERE mbpt.post_id = mbp.id
) tags ON TRUE
"""


def create_post(
    connection: Connection[Any],
    *,
    user_id: str,
    destination_country_id: str,
    origin_country_id: str | None,
    route_id: str | None,
    scenario_slug: str | None,
    persona_slug: str | None,
    title: str,
    summary: str,
    target_city: str | None,
    target_month: Any,
    timeline_window: str,
    budget_range: str,
    household_type: str,
    migration_stage: str,
    companion_goal: str,
    preferred_language: str,
    visibility: str,
    risk_acknowledged: bool,
    legal_disclaimer_acknowledged: bool,
    contact_requests_enabled: bool,
    tags: list[str],
) -> dict[str, Any]:
    row = execute_one(
        connection,
        """
        INSERT INTO migration_board_posts (
            user_id,
            origin_country_id,
            destination_country_id,
            route_id,
            scenario_slug,
            persona_slug,
            title,
            summary,
            target_city,
            target_month,
            timeline_window,
            budget_range,
            household_type,
            migration_stage,
            companion_goal,
            preferred_language,
            visibility,
            risk_acknowledged,
            legal_disclaimer_acknowledged,
            contact_requests_enabled
        )
        VALUES (
            %s::uuid,
            %s::uuid,
            %s::uuid,
            %s::uuid,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        RETURNING id::text AS id
        """,
        (
            user_id,
            origin_country_id,
            destination_country_id,
            route_id,
            scenario_slug,
            persona_slug,
            title,
            summary,
            target_city,
            target_month,
            timeline_window,
            budget_range,
            household_type,
            migration_stage,
            companion_goal,
            preferred_language,
            visibility,
            risk_acknowledged,
            legal_disclaimer_acknowledged,
            contact_requests_enabled,
        ),
    )
    replace_post_tags(connection, post_id=str(row["id"]), tags=tags)
    post = get_post_by_id(connection, str(row["id"]))
    if post is None:
        raise RuntimeError("Expected migration board post to exist after insert.")
    return post


def update_post(
    connection: Connection[Any],
    *,
    post_id: str,
    destination_country_id: str | None,
    origin_country_id: str | None,
    route_id: str | None,
    scenario_slug: str | None,
    persona_slug: str | None,
    title: str | None,
    summary: str | None,
    target_city: str | None,
    target_month: Any,
    timeline_window: str | None,
    budget_range: str | None,
    household_type: str | None,
    migration_stage: str | None,
    companion_goal: str | None,
    preferred_language: str | None,
    visibility: str | None,
    risk_acknowledged: bool | None,
    legal_disclaimer_acknowledged: bool | None,
    contact_requests_enabled: bool | None,
    reset_to_review: bool,
    tags: list[str] | None,
) -> dict[str, Any] | None:
    row = fetch_one(
        connection,
        """
        UPDATE migration_board_posts
        SET
            origin_country_id = COALESCE(%s::uuid, origin_country_id),
            destination_country_id = COALESCE(%s::uuid, destination_country_id),
            route_id = COALESCE(%s::uuid, route_id),
            scenario_slug = COALESCE(%s, scenario_slug),
            persona_slug = COALESCE(%s, persona_slug),
            title = COALESCE(%s, title),
            summary = COALESCE(%s, summary),
            target_city = COALESCE(%s, target_city),
            target_month = COALESCE(%s, target_month),
            timeline_window = COALESCE(%s, timeline_window),
            budget_range = COALESCE(%s, budget_range),
            household_type = COALESCE(%s, household_type),
            migration_stage = COALESCE(%s, migration_stage),
            companion_goal = COALESCE(%s, companion_goal),
            preferred_language = COALESCE(%s, preferred_language),
            visibility = COALESCE(%s, visibility),
            risk_acknowledged = COALESCE(%s, risk_acknowledged),
            legal_disclaimer_acknowledged = COALESCE(%s, legal_disclaimer_acknowledged),
            contact_requests_enabled = COALESCE(%s, contact_requests_enabled),
            status = CASE WHEN %s THEN 'review' ELSE status END,
            moderation_status = CASE WHEN %s THEN 'pending' ELSE moderation_status END,
            published_at = CASE WHEN %s THEN NULL ELSE published_at END,
            updated_at = NOW()
        WHERE id::text = %s
        RETURNING id::text AS id
        """,
        (
            origin_country_id,
            destination_country_id,
            route_id,
            scenario_slug,
            persona_slug,
            title,
            summary,
            target_city,
            target_month,
            timeline_window,
            budget_range,
            household_type,
            migration_stage,
            companion_goal,
            preferred_language,
            visibility,
            risk_acknowledged,
            legal_disclaimer_acknowledged,
            contact_requests_enabled,
            reset_to_review,
            reset_to_review,
            reset_to_review,
            post_id,
        ),
    )
    if row is None:
        return None
    if tags is not None:
        replace_post_tags(connection, post_id=post_id, tags=tags)
    return get_post_by_id(connection, post_id)


def replace_post_tags(
    connection: Connection[Any], *, post_id: str, tags: list[str]
) -> None:
    connection.execute(
        "DELETE FROM migration_board_post_tags WHERE post_id::text = %s",
        (post_id,),
    )
    for tag in tags:
        connection.execute(
            """
            INSERT INTO migration_board_post_tags (post_id, tag)
            VALUES (%s::uuid, %s)
            ON CONFLICT DO NOTHING
            """,
            (post_id, tag),
        )


def get_post_by_id(connection: Connection[Any], post_id: str) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {POST_SELECT}
        {POST_JOINS}
        WHERE mbp.id::text = %s
        """,
        (post_id,),
    )


def get_post_for_owner(
    connection: Connection[Any], post_id: str, user_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        f"""
        SELECT
            {POST_SELECT}
        {POST_JOINS}
        WHERE mbp.id::text = %s AND mbp.user_id::text = %s
        """,
        (post_id, user_id),
    )


def list_public_posts(
    connection: Connection[Any],
    *,
    filters: dict[str, Any],
    include_members_only: bool,
    include_private_for_user_id: str | None,
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    where_sql, params = _public_filters(
        filters=filters,
        include_members_only=include_members_only,
        include_private_for_user_id=include_private_for_user_id,
    )
    return fetch_all(
        connection,
        f"""
        SELECT
            {POST_SELECT},
            COUNT(*) OVER() AS total_count
        {POST_JOINS}
        WHERE {where_sql}
        ORDER BY mbp.published_at DESC NULLS LAST, mbp.created_at DESC, mbp.id
        LIMIT %s OFFSET %s
        """,
        (*params, limit, offset),
    )


def list_user_posts(connection: Connection[Any], user_id: str) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        f"""
        SELECT
            {POST_SELECT}
        {POST_JOINS}
        WHERE mbp.user_id::text = %s
        ORDER BY mbp.updated_at DESC, mbp.created_at DESC
        """,
        (user_id,),
    )


def list_posts_for_moderation(
    connection: Connection[Any], *, status: str | None, limit: int, offset: int
) -> list[dict[str, Any]]:
    filters = []
    params: list[Any] = []
    if status is not None:
        filters.append("mbp.status = %s")
        params.append(status)
    where_sql = " AND ".join(filters) if filters else "TRUE"
    return fetch_all(
        connection,
        f"""
        SELECT
            {POST_SELECT},
            COUNT(*) OVER() AS total_count
        {POST_JOINS}
        WHERE {where_sql}
        ORDER BY
            CASE mbp.status WHEN 'review' THEN 1 ELSE 2 END,
            mbp.submitted_at DESC NULLS LAST,
            mbp.updated_at DESC
        LIMIT %s OFFSET %s
        """,
        (*params, limit, offset),
    )


def submit_post_for_review(
    connection: Connection[Any], post_id: str
) -> dict[str, Any] | None:
    row = fetch_one(
        connection,
        """
        UPDATE migration_board_posts
        SET
            status = 'review',
            moderation_status = 'pending',
            submitted_at = NOW(),
            updated_at = NOW()
        WHERE id::text = %s AND status IN ('draft', 'rejected', 'archived')
        RETURNING id::text AS id
        """,
        (post_id,),
    )
    return get_post_by_id(connection, post_id) if row is not None else None


def publish_post(
    connection: Connection[Any], *, post_id: str, moderator_user_id: str
) -> dict[str, Any] | None:
    row = fetch_one(
        connection,
        """
        UPDATE migration_board_posts
        SET
            status = 'published',
            moderation_status = 'approved',
            moderated_by = %s::uuid,
            moderated_at = NOW(),
            published_at = NOW(),
            rejected_at = NULL,
            updated_at = NOW()
        WHERE id::text = %s
          AND status = 'review'
          AND risk_acknowledged IS TRUE
          AND legal_disclaimer_acknowledged IS TRUE
        RETURNING id::text AS id
        """,
        (moderator_user_id, post_id),
    )
    return get_post_by_id(connection, post_id) if row is not None else None


def reject_post(
    connection: Connection[Any],
    *,
    post_id: str,
    moderator_user_id: str,
    reason: str | None,
) -> dict[str, Any] | None:
    row = fetch_one(
        connection,
        """
        UPDATE migration_board_posts
        SET
            status = 'rejected',
            moderation_status = 'rejected',
            moderated_by = %s::uuid,
            moderated_at = NOW(),
            moderation_reason = %s,
            rejected_at = NOW(),
            published_at = NULL,
            updated_at = NOW()
        WHERE id::text = %s AND status IN ('review', 'published')
        RETURNING id::text AS id
        """,
        (moderator_user_id, reason, post_id),
    )
    return get_post_by_id(connection, post_id) if row is not None else None


def archive_post(connection: Connection[Any], post_id: str) -> dict[str, Any] | None:
    row = fetch_one(
        connection,
        """
        UPDATE migration_board_posts
        SET
            status = 'archived',
            archived_at = NOW(),
            published_at = NULL,
            updated_at = NOW()
        WHERE id::text = %s AND status IN ('draft', 'review', 'published', 'rejected')
        RETURNING id::text AS id
        """,
        (post_id,),
    )
    return get_post_by_id(connection, post_id) if row is not None else None


def hide_post(
    connection: Connection[Any],
    *,
    post_id: str,
    moderator_user_id: str,
    reason: str | None,
) -> dict[str, Any] | None:
    row = fetch_one(
        connection,
        """
        UPDATE migration_board_posts
        SET
            moderation_status = 'hidden',
            moderated_by = %s::uuid,
            moderated_at = NOW(),
            moderation_reason = %s,
            published_at = NULL,
            updated_at = NOW()
        WHERE id::text = %s
        RETURNING id::text AS id
        """,
        (moderator_user_id, reason, post_id),
    )
    return get_post_by_id(connection, post_id) if row is not None else None


def count_user_active_posts(connection: Connection[Any], user_id: str) -> int:
    row = fetch_one(
        connection,
        """
        SELECT COUNT(*) AS total
        FROM migration_board_posts
        WHERE user_id::text = %s AND status IN ('draft', 'review', 'published')
        """,
        (user_id,),
    )
    return int(row["total"]) if row else 0


def create_contact_request(
    connection: Connection[Any],
    *,
    post_id: str,
    from_user_id: str,
    to_user_id: str,
    message: str,
) -> dict[str, Any]:
    row = execute_one(
        connection,
        """
        INSERT INTO migration_board_contact_requests (
            post_id,
            from_user_id,
            to_user_id,
            message,
            expires_at
        )
        VALUES (%s::uuid, %s::uuid, %s::uuid, %s, NOW() + INTERVAL '30 days')
        RETURNING id::text AS id
        """,
        (post_id, from_user_id, to_user_id, message),
    )
    request = get_contact_request_by_id(connection, str(row["id"]))
    if request is None:
        raise RuntimeError("Expected contact request to exist after insert.")
    return request


def get_contact_request_by_id(
    connection: Connection[Any], request_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        SELECT
            mbcr.id::text AS id,
            mbcr.post_id::text AS post_id,
            mbp.title AS post_title,
            mbcr.from_user_id::text AS from_user_id,
            fu.display_name AS from_user_display_name,
            mbcr.to_user_id::text AS to_user_id,
            tu.display_name AS to_user_display_name,
            mbcr.message,
            mbcr.status,
            mbcr.created_at,
            mbcr.responded_at,
            mbcr.cancelled_at,
            mbcr.expires_at,
            mbcr.response_note
        FROM migration_board_contact_requests mbcr
        JOIN migration_board_posts mbp ON mbp.id = mbcr.post_id
        JOIN users fu ON fu.id = mbcr.from_user_id
        JOIN users tu ON tu.id = mbcr.to_user_id
        WHERE mbcr.id::text = %s
        """,
        (request_id,),
    )


def list_incoming_contact_requests(
    connection: Connection[Any], user_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            mbcr.id::text AS id,
            mbcr.post_id::text AS post_id,
            mbp.title AS post_title,
            mbcr.from_user_id::text AS from_user_id,
            fu.display_name AS from_user_display_name,
            mbcr.to_user_id::text AS to_user_id,
            tu.display_name AS to_user_display_name,
            mbcr.message,
            mbcr.status,
            mbcr.created_at,
            mbcr.responded_at,
            mbcr.cancelled_at,
            mbcr.expires_at,
            mbcr.response_note
        FROM migration_board_contact_requests mbcr
        JOIN migration_board_posts mbp ON mbp.id = mbcr.post_id
        JOIN users fu ON fu.id = mbcr.from_user_id
        JOIN users tu ON tu.id = mbcr.to_user_id
        WHERE mbcr.to_user_id::text = %s
          AND NOT EXISTS (
              SELECT 1
              FROM migration_board_blocks mbb
              WHERE mbb.blocker_user_id = mbcr.to_user_id
                AND mbb.blocked_user_id = mbcr.from_user_id
          )
        ORDER BY mbcr.created_at DESC
        """,
        (user_id,),
    )


def list_outgoing_contact_requests(
    connection: Connection[Any], user_id: str
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            mbcr.id::text AS id,
            mbcr.post_id::text AS post_id,
            mbp.title AS post_title,
            mbcr.from_user_id::text AS from_user_id,
            fu.display_name AS from_user_display_name,
            mbcr.to_user_id::text AS to_user_id,
            tu.display_name AS to_user_display_name,
            mbcr.message,
            mbcr.status,
            mbcr.created_at,
            mbcr.responded_at,
            mbcr.cancelled_at,
            mbcr.expires_at,
            mbcr.response_note
        FROM migration_board_contact_requests mbcr
        JOIN migration_board_posts mbp ON mbp.id = mbcr.post_id
        JOIN users fu ON fu.id = mbcr.from_user_id
        JOIN users tu ON tu.id = mbcr.to_user_id
        WHERE mbcr.from_user_id::text = %s
        ORDER BY mbcr.created_at DESC
        """,
        (user_id,),
    )


def update_contact_request_status(
    connection: Connection[Any],
    *,
    request_id: str,
    status: str,
    response_note: str | None,
) -> dict[str, Any] | None:
    row = fetch_one(
        connection,
        """
        UPDATE migration_board_contact_requests
        SET
            status = %s,
            responded_at = CASE WHEN %s IN ('accepted', 'declined') THEN NOW() ELSE responded_at END,
            cancelled_at = CASE WHEN %s = 'cancelled' THEN NOW() ELSE cancelled_at END,
            response_note = %s
        WHERE id::text = %s AND status = 'pending'
        RETURNING id::text AS id
        """,
        (status, status, status, response_note, request_id),
    )
    return (
        get_contact_request_by_id(connection, request_id) if row is not None else None
    )


def pending_contact_request_exists(
    connection: Connection[Any], *, post_id: str, from_user_id: str
) -> bool:
    row = fetch_one(
        connection,
        """
        SELECT 1
        FROM migration_board_contact_requests
        WHERE post_id::text = %s AND from_user_id::text = %s AND status = 'pending'
        """,
        (post_id, from_user_id),
    )
    return row is not None


def count_contact_requests_created_since(
    connection: Connection[Any], *, user_id: str, since_sql: str
) -> int:
    row = fetch_one(
        connection,
        """
        SELECT COUNT(*) AS total
        FROM migration_board_contact_requests
        WHERE from_user_id::text = %s AND created_at >= NOW() - INTERVAL '1 day'
        """,
        (user_id,),
    )
    _ = since_sql
    return int(row["total"]) if row else 0


def create_report(
    connection: Connection[Any],
    *,
    reporter_user_id: str,
    post_id: str | None,
    contact_request_id: str | None,
    reason: str,
    details: str | None,
) -> dict[str, Any]:
    return execute_one(
        connection,
        """
        INSERT INTO migration_board_reports (
            reporter_user_id,
            post_id,
            contact_request_id,
            reason,
            details
        )
        VALUES (%s::uuid, %s::uuid, %s::uuid, %s, %s)
        RETURNING
            id::text AS id,
            post_id::text AS post_id,
            contact_request_id::text AS contact_request_id,
            reason,
            details,
            status,
            created_at,
            reviewed_at,
            resolution_note
        """,
        (reporter_user_id, post_id, contact_request_id, reason, details),
    )


def get_report_by_id(
    connection: Connection[Any], report_id: str
) -> dict[str, Any] | None:
    return fetch_one(
        connection,
        """
        SELECT
            id::text AS id,
            reporter_user_id::text AS reporter_user_id,
            post_id::text AS post_id,
            contact_request_id::text AS contact_request_id,
            reason,
            details,
            status,
            created_at,
            reviewed_by::text AS reviewed_by,
            reviewed_at,
            resolution_note
        FROM migration_board_reports
        WHERE id::text = %s
        """,
        (report_id,),
    )


def list_reports_for_moderation(
    connection: Connection[Any], *, status: str | None, limit: int, offset: int
) -> list[dict[str, Any]]:
    filters = []
    params: list[Any] = []
    if status is not None:
        filters.append("status = %s")
        params.append(status)
    where_sql = " AND ".join(filters) if filters else "TRUE"
    return fetch_all(
        connection,
        f"""
        SELECT
            id::text AS id,
            post_id::text AS post_id,
            contact_request_id::text AS contact_request_id,
            reason,
            details,
            status,
            created_at,
            reviewed_at,
            resolution_note,
            COUNT(*) OVER() AS total_count
        FROM migration_board_reports
        WHERE {where_sql}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """,
        (*params, limit, offset),
    )


def update_report_status(
    connection: Connection[Any],
    *,
    report_id: str,
    status: str,
    reviewed_by: str,
    resolution_note: str | None,
) -> dict[str, Any] | None:
    row = fetch_one(
        connection,
        """
        UPDATE migration_board_reports
        SET
            status = %s,
            reviewed_by = %s::uuid,
            reviewed_at = NOW(),
            resolution_note = %s
        WHERE id::text = %s AND status IN ('pending', 'reviewing')
        RETURNING id::text AS id
        """,
        (status, reviewed_by, resolution_note, report_id),
    )
    return get_report_by_id(connection, report_id) if row is not None else None


def existing_pending_report_exists(
    connection: Connection[Any],
    *,
    reporter_user_id: str,
    post_id: str | None,
    contact_request_id: str | None,
) -> bool:
    if post_id is not None:
        row = fetch_one(
            connection,
            """
            SELECT 1
            FROM migration_board_reports
            WHERE reporter_user_id::text = %s
              AND post_id::text = %s
              AND status IN ('pending', 'reviewing')
            """,
            (reporter_user_id, post_id),
        )
        return row is not None
    row = fetch_one(
        connection,
        """
        SELECT 1
        FROM migration_board_reports
        WHERE reporter_user_id::text = %s
          AND contact_request_id::text = %s
          AND status IN ('pending', 'reviewing')
        """,
        (reporter_user_id, contact_request_id),
    )
    return row is not None


def count_reports_created_today(connection: Connection[Any], user_id: str) -> int:
    row = fetch_one(
        connection,
        """
        SELECT COUNT(*) AS total
        FROM migration_board_reports
        WHERE reporter_user_id::text = %s AND created_at >= NOW() - INTERVAL '1 day'
        """,
        (user_id,),
    )
    return int(row["total"]) if row else 0


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
        WHERE blocker_user_id::text = %s AND blocked_user_id::text = %s
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
            blocker_user_id::text = %s AND blocked_user_id::text = %s
        ) OR (
            blocker_user_id::text = %s AND blocked_user_id::text = %s
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
        WHERE mbb.blocker_user_id::text = %s
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
            {POST_SELECT}
        {POST_JOINS}
        WHERE mbp.status = 'published'
          AND mbp.moderation_status = 'approved'
          AND mbp.visibility IN ('public', 'members_only')
          AND mbp.user_id::text <> %s
          AND mbp.destination_country_id::text = %s
          AND NOT EXISTS (
              SELECT 1
              FROM migration_board_blocks mbb
              WHERE (
                  mbb.blocker_user_id::text = %s
                  AND mbb.blocked_user_id = mbp.user_id
              ) OR (
                  mbb.blocked_user_id::text = %s
                  AND mbb.blocker_user_id = mbp.user_id
              )
          )
        ORDER BY
            (mbp.route_id::text = %s) DESC,
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
        WHERE id::text = %s
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
    row = fetch_one(connection, "SELECT 1 FROM users WHERE id::text = %s", (user_id,))
    return row is not None


def _public_filters(
    *,
    filters: dict[str, Any],
    include_members_only: bool,
    include_private_for_user_id: str | None,
) -> tuple[str, tuple[Any, ...]]:
    clauses = ["mbp.status = 'published'", "mbp.moderation_status = 'approved'"]
    params: list[Any] = []
    visibility_clause = ["mbp.visibility = 'public'"]
    if include_members_only:
        visibility_clause.append("mbp.visibility = 'members_only'")
    if include_private_for_user_id is not None:
        visibility_clause.append(
            "(mbp.visibility = 'private' AND mbp.user_id::text = %s)"
        )
        params.append(include_private_for_user_id)
    clauses.append("(" + " OR ".join(visibility_clause) + ")")
    mapping = {
        "destination_country_slug": "dc.slug = %s",
        "origin_country_slug": "oc.slug = %s",
        "route_id": "mbp.route_id::text = %s",
        "scenario_slug": "mbp.scenario_slug = %s",
        "persona_slug": "mbp.persona_slug = %s",
        "timeline_window": "mbp.timeline_window = %s",
        "migration_stage": "mbp.migration_stage = %s",
        "companion_goal": "mbp.companion_goal = %s",
        "household_type": "mbp.household_type = %s",
        "preferred_language": "mbp.preferred_language = %s",
        "visibility": "mbp.visibility = %s",
    }
    for key, clause in mapping.items():
        value = filters.get(key)
        if value:
            clauses.append(clause)
            params.append(value)
    if filters.get("tag"):
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM migration_board_post_tags mbpt_filter
                WHERE mbpt_filter.post_id = mbp.id AND mbpt_filter.tag = %s
            )
            """
        )
        params.append(filters["tag"])
    return " AND ".join(clauses), tuple(params)
