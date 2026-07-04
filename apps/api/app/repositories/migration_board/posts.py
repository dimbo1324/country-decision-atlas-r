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
        raise RuntimeError(
            "Expected migration board post to exist after insert."
        )
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


def get_post_by_id(
    connection: Connection[Any], post_id: str
) -> dict[str, Any] | None:
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


def list_user_posts(
    connection: Connection[Any], user_id: str
) -> list[dict[str, Any]]:
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


def archive_post(
    connection: Connection[Any], post_id: str
) -> dict[str, Any] | None:
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
