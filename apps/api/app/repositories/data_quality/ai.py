from app.core.database import fetch_all
from psycopg import Connection
from typing import Any


AI_FEATURE_KEYS = (
    "ai_augmentation",
    "ai_grounded_qa",
    "ai_explain_number",
    "ai_nl_decision",
)


def list_missing_ai_feature_flags(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        WITH expected(feature_key) AS (
            SELECT unnest(%s::text[])
        )
        SELECT expected.feature_key
        FROM expected
        LEFT JOIN feature_flags ff ON ff.key = expected.feature_key
        WHERE ff.key IS NULL
        ORDER BY expected.feature_key
        """,
        (list(AI_FEATURE_KEYS),),
    )


def list_ai_feature_flags_without_public_access_rules(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            ff.key AS feature_key,
            ff.status,
            ff.access_tier
        FROM feature_flags ff
        LEFT JOIN feature_access_rules far
            ON far.feature_key = ff.key
            AND far.access_tier = 'public'
        WHERE ff.key = ANY(%s::text[])
          AND far.feature_key IS NULL
        ORDER BY ff.key
        """,
        (list(AI_FEATURE_KEYS),),
    )


def list_ai_logs_with_forbidden_metadata_keys(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text,
            request_type,
            created_at,
            metadata
        FROM ai_interaction_logs
        WHERE metadata ?| ARRAY[
            'email',
            'phone',
            'name',
            'full_name',
            'telegram_user_id',
            'ip',
            'ip_address',
            'user_agent',
            'token',
            'admin_token',
            'password'
        ]
        ORDER BY created_at DESC
        LIMIT 100
        """,
    )


def list_ai_drafts_without_citations(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text,
            draft_type,
            status,
            country_slug,
            citations
        FROM ai_drafts
        WHERE status IN ('needs_review', 'approved')
          AND (
              citations IS NULL
              OR jsonb_typeof(citations) != 'array'
              OR jsonb_array_length(citations) = 0
          )
        ORDER BY created_at DESC
        LIMIT 100
        """,
    )


def list_ai_drafts_missing_model_metadata(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text,
            draft_type,
            status,
            country_slug,
            provider,
            model_name,
            model_version
        FROM ai_drafts
        WHERE NULLIF(BTRIM(provider), '') IS NULL
           OR NULLIF(BTRIM(model_name), '') IS NULL
           OR NULLIF(BTRIM(model_version), '') IS NULL
        ORDER BY created_at DESC
        LIMIT 100
        """,
    )


def list_ai_drafts_with_invalid_status(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text,
            draft_type,
            status,
            country_slug
        FROM ai_drafts
        WHERE status NOT IN ('needs_review', 'approved', 'rejected', 'archived')
        ORDER BY created_at DESC
        LIMIT 100
        """,
    )


def list_ai_drafts_with_invalid_draft_type(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text,
            draft_type,
            status,
            country_slug
        FROM ai_drafts
        WHERE draft_type NOT IN (
            'summary',
            'contradiction_candidate',
            'explanation',
            'source_digest',
            'evidence_digest'
        )
        ORDER BY created_at DESC
        LIMIT 100
        """,
    )


def list_approved_ai_drafts_without_review(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text,
            draft_type,
            status,
            country_slug,
            reviewed_at,
            reviewed_by
        FROM ai_drafts
        WHERE status = 'approved'
          AND (
              reviewed_at IS NULL
              OR NULLIF(BTRIM(reviewed_by), '') IS NULL
          )
        ORDER BY created_at DESC
        LIMIT 100
        """,
    )


def list_contradiction_candidates_without_traceability(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text,
            country_slug,
            entity_type,
            entity_id::text,
            status,
            source_ids,
            evidence_item_ids
        FROM contradiction_candidates
        WHERE status IN ('needs_review', 'confirmed')
          AND (
              source_ids IS NULL
              OR jsonb_typeof(source_ids) != 'array'
              OR jsonb_array_length(source_ids) = 0
          )
          AND (
              evidence_item_ids IS NULL
              OR jsonb_typeof(evidence_item_ids) != 'array'
              OR jsonb_array_length(evidence_item_ids) = 0
          )
        ORDER BY created_at DESC
        LIMIT 100
        """,
    )


def list_confirmed_contradiction_candidates_without_review(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text,
            country_slug,
            entity_type,
            entity_id::text,
            status,
            reviewed_at,
            reviewed_by
        FROM contradiction_candidates
        WHERE status = 'confirmed'
          AND (
              reviewed_at IS NULL
              OR NULLIF(BTRIM(reviewed_by), '') IS NULL
          )
        ORDER BY created_at DESC
        LIMIT 100
        """,
    )


def list_published_community_questions_without_moderation(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text,
            country_slug,
            route_id::text,
            topic,
            status,
            moderated_at,
            moderated_by
        FROM qna_questions
        WHERE status = 'published'
          AND (
              moderated_at IS NULL
              OR NULLIF(BTRIM(moderated_by), '') IS NULL
          )
        ORDER BY created_at DESC
        LIMIT 100
        """,
    )


def list_published_community_answers_without_moderation(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text,
            question_id::text,
            status,
            moderated_at,
            moderated_by
        FROM qna_answers
        WHERE status = 'published'
          AND (
              moderated_at IS NULL
              OR NULLIF(BTRIM(moderated_by), '') IS NULL
          )
        ORDER BY created_at DESC
        LIMIT 100
        """,
    )


def list_published_qna_questions_without_content(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text,
            country_slug,
            route_id::text,
            topic,
            title,
            body,
            status
        FROM qna_questions
        WHERE status = 'published'
          AND (
              NULLIF(BTRIM(title), '') IS NULL
              OR NULLIF(BTRIM(body), '') IS NULL
          )
        ORDER BY created_at DESC
        LIMIT 100
        """,
    )


def list_published_qna_answers_without_body(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text,
            question_id::text,
            status,
            body
        FROM qna_answers
        WHERE status = 'published'
          AND NULLIF(BTRIM(body), '') IS NULL
        ORDER BY created_at DESC
        LIMIT 100
        """,
    )


def list_published_qna_answers_with_invalid_traceability_refs(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text,
            question_id::text,
            status,
            source_ids,
            evidence_item_ids
        FROM qna_answers
        WHERE status = 'published'
          AND (
              source_ids IS NULL
              OR evidence_item_ids IS NULL
              OR jsonb_typeof(source_ids) != 'array'
              OR jsonb_typeof(evidence_item_ids) != 'array'
          )
        ORDER BY created_at DESC
        LIMIT 100
        """,
    )


def list_qna_votes_with_invalid_type(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text,
            answer_id::text,
            vote_type,
            identity_type,
            identity_id
        FROM qna_votes
        WHERE vote_type NOT IN ('up', 'down', 'helpful', 'outdated')
        ORDER BY created_at DESC
        LIMIT 100
        """,
    )


def list_duplicate_qna_votes(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            answer_id::text,
            vote_type,
            identity_type,
            identity_id,
            COUNT(*) AS duplicate_count
        FROM qna_votes
        GROUP BY answer_id, vote_type, identity_type, identity_id
        HAVING COUNT(*) > 1
        ORDER BY duplicate_count DESC, answer_id
        LIMIT 100
        """,
    )


def list_stale_pending_data_error_reports(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text,
            entity_type,
            entity_id::text,
            country_slug,
            route_id::text,
            report_type,
            status,
            created_at
        FROM data_error_reports
        WHERE status = 'pending'
          AND created_at < NOW() - INTERVAL '30 days'
        ORDER BY created_at ASC
        LIMIT 100
        """,
    )


def list_published_user_story_ratings_without_moderation(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text,
            user_story_id::text,
            country_slug,
            route_id::text,
            status,
            reviewed_at,
            reviewed_by
        FROM user_story_ratings
        WHERE status = 'published'
          AND (
              reviewed_at IS NULL
              OR NULLIF(BTRIM(reviewed_by), '') IS NULL
          )
        ORDER BY created_at DESC
        LIMIT 100
        """,
    )


def list_user_story_ratings_with_invalid_scores(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text,
            user_story_id::text,
            official_expectation_score,
            real_experience_score,
            bureaucracy_score,
            cost_surprise_score,
            banking_difficulty_score,
            safety_feeling_score,
            status
        FROM user_story_ratings
        WHERE official_expectation_score < 0
           OR official_expectation_score > 100
           OR real_experience_score < 0
           OR real_experience_score > 100
           OR bureaucracy_score < 0
           OR bureaucracy_score > 100
           OR cost_surprise_score < 0
           OR cost_surprise_score > 100
           OR banking_difficulty_score < 0
           OR banking_difficulty_score > 100
           OR safety_feeling_score < 0
           OR safety_feeling_score > 100
           OR status NOT IN ('pending', 'review', 'published', 'rejected', 'archived')
        ORDER BY created_at DESC
        LIMIT 100
        """,
    )
