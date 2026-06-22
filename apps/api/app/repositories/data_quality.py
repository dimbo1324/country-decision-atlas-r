from app.core.database import fetch_all
from psycopg import Connection
from typing import Any


MVP_COUNTRY_SLUGS = ("russia", "uruguay")
MVP_SCENARIO_SLUGS = (
    "relocation_residence",
    "permanent_residence_citizenship",
    "low_budget_living",
    "business_self_employment",
    "safety_political_risk",
)
MIN_PUBLISHED_SOURCES_PER_MVP_COUNTRY = 15
MIN_PUBLISHED_EVIDENCE_PER_MVP_COUNTRY = 20
MIN_PUBLISHED_LEGAL_SIGNALS_PER_MVP_COUNTRY = 8


def list_missing_mvp_countries(connection: Connection[Any]) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT expected.slug
        FROM unnest(%s::text[]) AS expected(slug)
        LEFT JOIN countries c
            ON c.slug = expected.slug
            AND c.is_active = TRUE
        WHERE c.id IS NULL
        ORDER BY expected.slug
        """,
        (list(MVP_COUNTRY_SLUGS),),
    )


def list_published_countries_without_cards(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            c.id::text AS id,
            c.slug
        FROM countries c
        LEFT JOIN country_cards cc
            ON cc.country_id = c.id
            AND cc.locale = 'en'
            AND cc.status = 'published'
        WHERE c.slug = ANY(%s)
          AND c.is_active = TRUE
          AND cc.id IS NULL
        ORDER BY c.slug
        """,
        (list(MVP_COUNTRY_SLUGS),),
    )


def list_published_countries_without_sources(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            c.id::text AS id,
            c.slug
        FROM countries c
        LEFT JOIN sources s
            ON s.country_id = c.id
            AND s.status = 'published'
        WHERE c.slug = ANY(%s)
          AND c.is_active = TRUE
        GROUP BY c.id, c.slug
        HAVING COUNT(s.id) = 0
        ORDER BY c.slug
        """,
        (list(MVP_COUNTRY_SLUGS),),
    )


def list_mvp_countries_with_too_few_published_sources(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            c.id::text AS id,
            c.slug,
            COUNT(s.id)::int AS published_sources_count,
            %s::int AS required_sources_count
        FROM countries c
        LEFT JOIN sources s
            ON s.country_id = c.id
            AND s.status = 'published'
        WHERE c.slug = ANY(%s)
          AND c.is_active = TRUE
        GROUP BY c.id, c.slug
        HAVING COUNT(s.id) < %s
        ORDER BY c.slug
        """,
        (
            MIN_PUBLISHED_SOURCES_PER_MVP_COUNTRY,
            list(MVP_COUNTRY_SLUGS),
            MIN_PUBLISHED_SOURCES_PER_MVP_COUNTRY,
        ),
    )


def list_mvp_countries_with_too_few_published_evidence(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            c.id::text AS id,
            c.slug,
            COUNT(e.id)::int AS published_evidence_count,
            %s::int AS required_evidence_count
        FROM countries c
        LEFT JOIN evidence_items e
            ON e.country_id = c.id
            AND e.status = 'published'
        WHERE c.slug = ANY(%s)
          AND c.is_active = TRUE
        GROUP BY c.id, c.slug
        HAVING COUNT(e.id) < %s
        ORDER BY c.slug
        """,
        (
            MIN_PUBLISHED_EVIDENCE_PER_MVP_COUNTRY,
            list(MVP_COUNTRY_SLUGS),
            MIN_PUBLISHED_EVIDENCE_PER_MVP_COUNTRY,
        ),
    )


def list_mvp_countries_with_too_few_published_legal_signals(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            c.id::text AS id,
            c.slug,
            COUNT(ls.id)::int AS published_legal_signals_count,
            %s::int AS required_legal_signals_count
        FROM countries c
        LEFT JOIN legal_signals ls
            ON ls.country_id = c.id
            AND ls.status = 'published'
        WHERE c.slug = ANY(%s)
          AND c.is_active = TRUE
        GROUP BY c.id, c.slug
        HAVING COUNT(ls.id) < %s
        ORDER BY c.slug
        """,
        (
            MIN_PUBLISHED_LEGAL_SIGNALS_PER_MVP_COUNTRY,
            list(MVP_COUNTRY_SLUGS),
            MIN_PUBLISHED_LEGAL_SIGNALS_PER_MVP_COUNTRY,
        ),
    )


def list_missing_country_scores_for_required_scenarios(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            country_scope.slug AS country_slug,
            scenario_scope.slug AS scenario_slug
        FROM unnest(%s::text[]) AS country_scope(slug)
        CROSS JOIN unnest(%s::text[]) AS scenario_scope(slug)
        LEFT JOIN countries c
            ON c.slug = country_scope.slug
            AND c.is_active = TRUE
        LEFT JOIN scenarios s
            ON s.slug = scenario_scope.slug
            AND s.is_active = TRUE
        LEFT JOIN country_scores cs
            ON cs.country_id = c.id
            AND cs.scenario_id = s.id
        WHERE c.id IS NULL
           OR s.id IS NULL
           OR cs.id IS NULL
        ORDER BY country_scope.slug, scenario_scope.slug
        """,
        (list(MVP_COUNTRY_SLUGS), list(MVP_SCENARIO_SLUGS)),
    )


def list_scores_without_breakdowns(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cs.id::text AS country_score_id,
            c.slug AS country_slug,
            s.slug AS scenario_slug
        FROM country_scores cs
        JOIN countries c ON c.id = cs.country_id
        JOIN scenarios s ON s.id = cs.scenario_id
        LEFT JOIN country_score_breakdowns csb
            ON csb.country_score_id = cs.id
        WHERE c.slug = ANY(%s)
          AND s.slug = ANY(%s)
        GROUP BY cs.id, c.slug, s.slug
        HAVING COUNT(csb.id) = 0
        ORDER BY c.slug, s.slug
        """,
        (list(MVP_COUNTRY_SLUGS), list(MVP_SCENARIO_SLUGS)),
    )


def list_scores_with_incomplete_breakdowns(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cs.id::text AS country_score_id,
            c.slug AS country_slug,
            s.slug AS scenario_slug,
            COUNT(csb.id)::int AS breakdown_count
        FROM country_scores cs
        JOIN countries c ON c.id = cs.country_id
        JOIN scenarios s ON s.id = cs.scenario_id
        LEFT JOIN country_score_breakdowns csb
            ON csb.country_score_id = cs.id
        WHERE c.slug = ANY(%s)
          AND s.slug = ANY(%s)
        GROUP BY cs.id, c.slug, s.slug
        HAVING COUNT(csb.id) <> 7
        ORDER BY c.slug, s.slug
        """,
        (list(MVP_COUNTRY_SLUGS), list(MVP_SCENARIO_SLUGS)),
    )


def list_scores_with_invalid_weight_sum(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cs.id::text AS country_score_id,
            c.slug AS country_slug,
            s.slug AS scenario_slug,
            COALESCE(SUM(csb.weight), 0)::float AS weight_sum
        FROM country_scores cs
        JOIN countries c ON c.id = cs.country_id
        JOIN scenarios s ON s.id = cs.scenario_id
        LEFT JOIN country_score_breakdowns csb
            ON csb.country_score_id = cs.id
        WHERE c.slug = ANY(%s)
          AND s.slug = ANY(%s)
        GROUP BY cs.id, c.slug, s.slug
        HAVING ABS(COALESCE(SUM(csb.weight), 0) - 1.0) > 0.001
        ORDER BY c.slug, s.slug
        """,
        (list(MVP_COUNTRY_SLUGS), list(MVP_SCENARIO_SLUGS)),
    )


def list_published_score_breakdowns_without_source_ids(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            csb.id::text AS id,
            cs.id::text AS country_score_id,
            c.slug AS country_slug,
            s.slug AS scenario_slug,
            csb.criterion
        FROM country_score_breakdowns csb
        JOIN country_scores cs ON cs.id = csb.country_score_id
        JOIN countries c ON c.id = cs.country_id
        JOIN scenarios s ON s.id = cs.scenario_id
        WHERE c.slug = ANY(%s)
          AND s.slug = ANY(%s)
          AND (
              csb.source_ids IS NULL
              OR jsonb_typeof(csb.source_ids) <> 'array'
              OR jsonb_array_length(csb.source_ids) = 0
          )
        ORDER BY c.slug, s.slug, csb.criterion
        """,
        (list(MVP_COUNTRY_SLUGS), list(MVP_SCENARIO_SLUGS)),
    )


def list_published_legal_signals_without_source(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            title,
            country_id::text AS country_id
        FROM legal_signals
        WHERE status = 'published'
          AND source_id IS NULL
        ORDER BY title
        """,
    )


def list_published_legal_signals_without_evidence(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            ls.id::text AS id,
            ls.title,
            ls.country_id::text AS country_id
        FROM legal_signals ls
        LEFT JOIN evidence_items e
            ON e.legal_signal_id = ls.id
            AND e.status = 'published'
        WHERE ls.status = 'published'
        GROUP BY ls.id, ls.title, ls.country_id
        HAVING COUNT(e.id) = 0
        ORDER BY ls.title
        """,
    )


def list_published_legal_signals_without_timeline_event(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT ls.id::text AS id, ls.title, c.slug AS country_slug
        FROM legal_signals ls
        JOIN countries c ON c.id = ls.country_id
        LEFT JOIN legal_signal_events lse ON lse.legal_signal_id = ls.id
        WHERE ls.status = 'published'
        GROUP BY ls.id, ls.title, c.slug
        HAVING COUNT(lse.id) = 0
        ORDER BY c.slug, ls.title
        """,
    )


def list_timeline_events_with_invalid_date(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT id::text AS id, legal_signal_id::text AS legal_signal_id
        FROM legal_signal_events
        WHERE event_date IS NULL
        ORDER BY id
        """,
    )


def list_timeline_events_with_invalid_impact_direction(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT id::text AS id, impact_direction
        FROM legal_signal_events
        WHERE impact_direction NOT IN ('positive', 'negative', 'neutral', 'mixed', 'uncertain')
        ORDER BY id
        """,
    )


def list_timeline_events_with_invalid_impact_level(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT id::text AS id, impact_level
        FROM legal_signal_events
        WHERE impact_level NOT IN ('low', 'medium', 'high', 'critical')
        ORDER BY id
        """,
    )


def list_timeline_events_with_country_mismatch(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            lse.id::text AS id,
            lse.country_id::text AS event_country_id,
            ls.country_id::text AS signal_country_id
        FROM legal_signal_events lse
        JOIN legal_signals ls ON ls.id = lse.legal_signal_id
        WHERE lse.country_id <> ls.country_id
        ORDER BY lse.id
        """,
    )


def list_timeline_events_without_traceability(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT id::text AS id, legal_signal_id::text AS legal_signal_id
        FROM legal_signal_events
        WHERE source_id IS NULL AND evidence_item_id IS NULL
        ORDER BY id
        """,
    )


def list_unplanned_future_timeline_events(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT id::text AS id, event_date, event_type
        FROM legal_signal_events
        WHERE event_date > CURRENT_DATE
        ORDER BY event_date
        """,
    )


def list_evidence_without_source(connection: Connection[Any]) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            title,
            claim
        FROM evidence_items
        WHERE source_id IS NULL
        ORDER BY id
        """,
    )


def list_evidence_without_country(connection: Connection[Any]) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            title,
            claim
        FROM evidence_items
        WHERE country_id IS NULL
        ORDER BY id
        """,
    )


def list_published_sources_with_missing_required_fields(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            title,
            CASE
                WHEN title IS NULL OR title = '' THEN 'title'
                WHEN url IS NULL OR url = '' THEN 'url'
                WHEN publisher IS NULL OR publisher = '' THEN 'publisher'
                WHEN source_type IS NULL OR source_type = '' THEN 'source_type'
                WHEN COALESCE(confidence, reliability_level) IS NULL THEN 'confidence'
                ELSE 'unknown'
            END AS missing_field
        FROM sources
        WHERE status = 'published'
          AND (
              title IS NULL
              OR title = ''
              OR url IS NULL
              OR url = ''
              OR publisher IS NULL
              OR publisher = ''
              OR source_type IS NULL
              OR source_type = ''
              OR COALESCE(confidence, reliability_level) IS NULL
          )
        ORDER BY title
        """,
    )


def list_published_sources_with_example_invalid_url(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            title,
            url
        FROM sources
        WHERE status = 'published'
          AND LOWER(COALESCE(url, '')) LIKE '%%example.invalid%%'
        ORDER BY title
        """,
    )


def list_invalid_synthetic_user_stories(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            id::text AS id,
            verification_status,
            is_synthetic,
            notes
        FROM user_stories
        WHERE is_synthetic = TRUE
          AND (
              verification_status = 'verified'
              OR notes IS NULL
              OR notes = ''
              OR (
                  POSITION('synthetic' IN LOWER(notes)) = 0
                  AND POSITION('demo' IN LOWER(notes)) = 0
              )
          )
        ORDER BY created_at DESC
        """,
    )


def list_country_cards_with_empty_major_sections(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cc.id::text AS id,
            c.slug AS country_slug,
            cc.locale
        FROM country_cards cc
        JOIN countries c ON c.id = cc.country_id
        WHERE c.slug = ANY(%s)
          AND cc.status = 'published'
          AND (
              COALESCE(cc.executive_summary, '') = ''
              OR COALESCE(cc.migration_overview, '') = ''
              OR COALESCE(cc.tax_overview, '') = ''
              OR COALESCE(cc.cost_of_living_overview, '') = ''
              OR COALESCE(cc.business_overview, '') = ''
              OR COALESCE(cc.safety_overview, '') = ''
              OR COALESCE(cc.legal_signals_summary, '') = ''
              OR COALESCE(cc.risk_summary, '') = ''
              OR COALESCE(cc.source_summary, '') = ''
          )
        ORDER BY c.slug, cc.locale
        """,
        (list(MVP_COUNTRY_SLUGS),),
    )


def list_country_cards_with_demo_source_summary(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            cc.id::text AS id,
            c.slug AS country_slug,
            cc.locale,
            cc.source_summary
        FROM country_cards cc
        JOIN countries c ON c.id = cc.country_id
        WHERE c.slug = ANY(%s)
          AND cc.status = 'published'
          AND (
              LOWER(COALESCE(cc.source_summary, '')) LIKE '%%demo%%'
              OR LOWER(COALESCE(cc.source_summary, '')) LIKE '%%placeholder%%'
              OR LOWER(COALESCE(cc.source_summary, '')) LIKE '%%example.invalid%%'
              OR LOWER(COALESCE(cc.source_summary, '')) LIKE '%%mvp demonstration%%'
          )
        ORDER BY c.slug, cc.locale
        """,
        (list(MVP_COUNTRY_SLUGS),),
    )


def list_mvp_countries_missing_cii(connection: Connection[Any]) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT c.slug AS country_slug
        FROM countries c
        WHERE c.slug = ANY(%s)
          AND c.is_active = TRUE
          AND NOT EXISTS (
              SELECT 1 FROM country_cii_scores ccs
              WHERE ccs.country_id = c.id AND ccs.version = 'v1.0'
          )
        ORDER BY c.slug
        """,
        (list(MVP_COUNTRY_SLUGS),),
    )


def list_cii_scores_missing_formula_metadata(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            c.slug AS country_slug,
            ccs.version,
            ccs.formula_version,
            ccs.aggregation_method
        FROM country_cii_scores ccs
        JOIN countries c ON c.id = ccs.country_id
        WHERE c.slug = ANY(%s)
          AND (
              ccs.formula_version IS NULL
              OR ccs.formula_version = ''
              OR ccs.aggregation_method IS NULL
              OR ccs.aggregation_method = ''
          )
        ORDER BY c.slug
        """,
        (list(MVP_COUNTRY_SLUGS),),
    )


def list_cii_metric_weights_with_invalid_sum(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            version,
            scenario_slug,
            ROUND(SUM(weight)::numeric, 4) AS weight_sum
        FROM scenario_metric_weights
        GROUP BY version, scenario_slug
        HAVING ABS(SUM(weight) - 1.0) > 0.001
        ORDER BY version, scenario_slug
        """,
        (),
    )


def list_mvp_scenarios_missing_cii_weights(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT expected.scenario_slug, m.slug AS metric_slug
        FROM unnest(%s::text[]) AS expected(scenario_slug)
        CROSS JOIN cii_metric_definitions m
        LEFT JOIN scenario_metric_weights smw
            ON smw.scenario_slug = expected.scenario_slug
           AND smw.metric_id = m.id
           AND smw.version = 'v1.0'
        WHERE m.is_active = TRUE
          AND smw.id IS NULL
        ORDER BY expected.scenario_slug, m.display_order
        """,
        (list(MVP_SCENARIO_SLUGS),),
    )


def list_cii_scenario_weights_with_negative_values(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT smw.scenario_slug, m.slug AS metric_slug, smw.weight::float AS weight
        FROM scenario_metric_weights smw
        JOIN cii_metric_definitions m ON m.id = smw.metric_id
        WHERE smw.scenario_slug = ANY(%s)
          AND smw.weight < 0
        ORDER BY smw.scenario_slug, m.display_order
        """,
        (list(MVP_SCENARIO_SLUGS),),
    )


def list_cii_scenario_weights_exceeding_one(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT smw.scenario_slug, m.slug AS metric_slug, smw.weight::float AS weight
        FROM scenario_metric_weights smw
        JOIN cii_metric_definitions m ON m.id = smw.metric_id
        WHERE smw.scenario_slug = ANY(%s)
          AND smw.weight > 1
        ORDER BY smw.scenario_slug, m.display_order
        """,
        (list(MVP_SCENARIO_SLUGS),),
    )


def list_mvp_scenarios_missing_cii_scores(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT expected_c.country_slug, expected_s.scenario_slug
        FROM unnest(%s::text[]) AS expected_c(country_slug)
        CROSS JOIN unnest(%s::text[]) AS expected_s(scenario_slug)
        LEFT JOIN countries c
            ON c.slug = expected_c.country_slug AND c.is_active = TRUE
        LEFT JOIN country_cii_scores ccs
            ON ccs.country_id = c.id
           AND ccs.scenario_slug = expected_s.scenario_slug
           AND ccs.version = 'v1.0'
        WHERE c.id IS NULL OR ccs.id IS NULL
        ORDER BY expected_c.country_slug, expected_s.scenario_slug
        """,
        (list(MVP_COUNTRY_SLUGS), list(MVP_SCENARIO_SLUGS)),
    )


def list_cii_scenario_scores_missing_formula_metadata(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            c.slug AS country_slug,
            ccs.version,
            ccs.scenario_slug,
            ccs.formula_version,
            ccs.aggregation_method
        FROM country_cii_scores ccs
        JOIN countries c ON c.id = ccs.country_id
        WHERE c.slug = ANY(%s)
          AND ccs.scenario_slug = ANY(%s)
          AND (
              ccs.formula_version IS NULL
              OR ccs.formula_version = ''
              OR ccs.aggregation_method IS NULL
              OR ccs.aggregation_method = ''
          )
        ORDER BY c.slug, ccs.scenario_slug
        """,
        (list(MVP_COUNTRY_SLUGS), list(MVP_SCENARIO_SLUGS)),
    )


def list_mvp_metrics_missing_values(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            expected.country_slug,
            m.slug AS metric_slug
        FROM unnest(%s::text[]) AS expected(country_slug)
        CROSS JOIN cii_metric_definitions m
        LEFT JOIN country_metric_values cmv
            ON cmv.country_id = (
                SELECT id FROM countries
                WHERE slug = expected.country_slug AND is_active = TRUE
                LIMIT 1
            )
            AND cmv.metric_id = m.id
        WHERE m.is_active = TRUE
          AND cmv.id IS NULL
        ORDER BY expected.country_slug, m.display_order
        """,
        (list(MVP_COUNTRY_SLUGS),),
    )


def list_cii_scores_out_of_range(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return fetch_all(
        connection,
        """
        SELECT
            c.slug AS country_slug,
            ccs.version,
            ccs.overall_score
        FROM country_cii_scores ccs
        JOIN countries c ON c.id = ccs.country_id
        WHERE c.slug = ANY(%s)
          AND (ccs.overall_score < 0 OR ccs.overall_score > 100)
        ORDER BY c.slug
        """,
        (list(MVP_COUNTRY_SLUGS),),
    )
