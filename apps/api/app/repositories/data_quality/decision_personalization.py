from app.repositories import data_quality as data_quality_repository
from psycopg import Connection
from typing import Any


def list_decision_personalization_feature_flag_mismatches(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        WITH expected(feature_key) AS (
            VALUES
                ('decision_personalization_enabled'),
                ('decision_wizard_enabled')
        )
        SELECT
            expected.feature_key,
            ff.status,
            ff.access_tier,
            ff.default_enabled,
            COALESCE(BOOL_OR(far.is_enabled), FALSE) AS has_enabled_rule
        FROM expected
        LEFT JOIN feature_flags ff ON ff.key = expected.feature_key
        LEFT JOIN feature_access_rules far ON far.feature_key = expected.feature_key
        GROUP BY
            expected.feature_key,
            ff.key,
            ff.status,
            ff.access_tier,
            ff.default_enabled
        HAVING
            ff.key IS NULL
            OR ff.status <> 'enabled'
            OR ff.access_tier <> 'public'
            OR ff.default_enabled IS DISTINCT FROM TRUE
            OR COALESCE(BOOL_OR(far.is_enabled), FALSE) IS DISTINCT FROM TRUE
        ORDER BY expected.feature_key
        """,
        (),
    )


def list_decision_scores_missing_required_criteria(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        WITH required_criteria(criterion) AS (
            VALUES
                ('legalization_score'),
                ('long_term_status_score'),
                ('cost_of_living_score'),
                ('safety_score'),
                ('business_score'),
                ('legal_stability_score'),
                ('source_quality_score')
        )
        SELECT
            c.slug AS country_slug,
            ds.slug AS scenario_slug,
            rc.criterion
        FROM country_scores cs
        JOIN countries c ON c.id = cs.country_id
        JOIN scenarios ds ON ds.id = cs.scenario_id
        CROSS JOIN required_criteria rc
        LEFT JOIN country_score_breakdowns csb
            ON csb.country_score_id = cs.id
            AND csb.criterion = rc.criterion
        WHERE c.is_active = TRUE
          AND ds.is_active = TRUE
          AND csb.id IS NULL
        ORDER BY c.slug, ds.slug, rc.criterion
        """,
        (),
    )


def list_decision_wizard_rule_mismatches(
    connection: Connection[Any],
) -> list[dict[str, Any]]:
    return data_quality_repository.fetch_all(
        connection,
        """
        WITH required_scenarios(scenario_slug) AS (
            VALUES
                ('relocation_residence'),
                ('permanent_residence_citizenship'),
                ('low_budget_living'),
                ('business_self_employment'),
                ('safety_political_risk')
        ),
        required_personas(persona_slug) AS (
            VALUES
                ('family'),
                ('entrepreneur'),
                ('digital_nomad'),
                ('student'),
                ('low_budget_migrant'),
                ('investor'),
                ('skilled_worker')
        ),
        missing_scenarios AS (
            SELECT
                'scenario' AS dependency_type,
                rs.scenario_slug AS dependency_slug
            FROM required_scenarios rs
            LEFT JOIN scenarios ds
                ON ds.slug = rs.scenario_slug
                AND ds.is_active = TRUE
            WHERE ds.id IS NULL
        ),
        missing_personas AS (
            SELECT
                'persona' AS dependency_type,
                rp.persona_slug AS dependency_slug
            FROM required_personas rp
            LEFT JOIN personas p
                ON p.slug = rp.persona_slug
                AND p.is_active = TRUE
            WHERE p.id IS NULL
        )
        SELECT dependency_type, dependency_slug FROM missing_scenarios
        UNION ALL
        SELECT dependency_type, dependency_slug FROM missing_personas
        ORDER BY dependency_type, dependency_slug
        """,
        (),
    )
