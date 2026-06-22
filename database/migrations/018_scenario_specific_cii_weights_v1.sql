ALTER TABLE scenario_metric_weights
    ADD COLUMN IF NOT EXISTS scenario_slug TEXT NOT NULL DEFAULT '';

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_scenario_metric_weight'
          AND conrelid = 'scenario_metric_weights'::regclass
    ) THEN
        ALTER TABLE scenario_metric_weights DROP CONSTRAINT uq_scenario_metric_weight;
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_scenario_metric_weight_v2'
          AND conrelid = 'scenario_metric_weights'::regclass
    ) THEN
        ALTER TABLE scenario_metric_weights
            ADD CONSTRAINT uq_scenario_metric_weight_v2
            UNIQUE (version, scenario_slug, metric_id);
    END IF;
END$$;

ALTER TABLE country_cii_scores
    ADD COLUMN IF NOT EXISTS scenario_slug TEXT NOT NULL DEFAULT '';

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_country_cii_version'
          AND conrelid = 'country_cii_scores'::regclass
    ) THEN
        ALTER TABLE country_cii_scores DROP CONSTRAINT uq_country_cii_version;
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_country_cii_version_scenario'
          AND conrelid = 'country_cii_scores'::regclass
    ) THEN
        ALTER TABLE country_cii_scores
            ADD CONSTRAINT uq_country_cii_version_scenario
            UNIQUE (country_id, version, scenario_slug);
    END IF;
END$$;

INSERT INTO scenario_metric_weights (version, scenario_slug, metric_id, weight)
SELECT
    'v1.0',
    w.scenario_slug,
    m.id,
    w.weight
FROM cii_metric_definitions m
JOIN (
    VALUES
        ('relocation_residence',            'safety',              0.2500),
        ('relocation_residence',            'political_stability',  0.2000),
        ('relocation_residence',            'rule_of_law',          0.2000),
        ('relocation_residence',            'corruption',           0.1500),
        ('relocation_residence',            'economic_freedom',     0.1000),
        ('relocation_residence',            'digital_access',       0.1000),

        ('permanent_residence_citizenship', 'rule_of_law',          0.2500),
        ('permanent_residence_citizenship', 'political_stability',  0.2500),
        ('permanent_residence_citizenship', 'corruption',           0.2000),
        ('permanent_residence_citizenship', 'safety',              0.1500),
        ('permanent_residence_citizenship', 'economic_freedom',     0.1000),
        ('permanent_residence_citizenship', 'digital_access',       0.0500),

        ('low_budget_living',               'economic_freedom',     0.2000),
        ('low_budget_living',               'safety',              0.2000),
        ('low_budget_living',               'corruption',           0.2000),
        ('low_budget_living',               'rule_of_law',          0.1500),
        ('low_budget_living',               'political_stability',  0.1500),
        ('low_budget_living',               'digital_access',       0.1000),

        ('business_self_employment',        'economic_freedom',     0.3500),
        ('business_self_employment',        'rule_of_law',          0.2500),
        ('business_self_employment',        'corruption',           0.1500),
        ('business_self_employment',        'digital_access',       0.1500),
        ('business_self_employment',        'political_stability',  0.0700),
        ('business_self_employment',        'safety',              0.0300),

        ('safety_political_risk',           'safety',              0.3000),
        ('safety_political_risk',           'political_stability',  0.3000),
        ('safety_political_risk',           'rule_of_law',          0.2000),
        ('safety_political_risk',           'corruption',           0.1500),
        ('safety_political_risk',           'economic_freedom',     0.0300),
        ('safety_political_risk',           'digital_access',       0.0200)
) AS w(scenario_slug, metric_slug, weight)
ON m.slug = w.metric_slug AND m.is_active = TRUE
ON CONFLICT (version, scenario_slug, metric_id) DO NOTHING;

WITH scenario_weights AS (
    SELECT smw.scenario_slug, smw.metric_id, smw.weight
    FROM scenario_metric_weights smw
    WHERE smw.version = 'v1.0'
      AND smw.scenario_slug != ''
),
computed_scores AS (
    SELECT
        c.id                                                                         AS country_id,
        sw.scenario_slug,
        ROUND(
            CAST(
                EXP(
                    SUM(sw.weight * LN(GREATEST(cmv.normalized_value::float, 1.0)))
                    / NULLIF(SUM(sw.weight), 0)
                ) AS NUMERIC
            ),
            2
        )                                                                            AS overall_score,
        jsonb_agg(
            jsonb_build_object(
                'slug',           m.slug,
                'name_en',        m.name_en,
                'name_ru',        m.name_ru,
                'score',          cmv.normalized_value,
                'weight',         sw.weight,
                'weighted_score', ROUND(
                    CAST(
                        sw.weight * LN(GREATEST(cmv.normalized_value::float, 1.0))
                        AS NUMERIC
                    ),
                    4
                ),
                'data_year',      cmv.data_year,
                'source_name',    cmv.source_name,
                'reliability',    cmv.reliability
            )
            ORDER BY m.display_order
        )                                                                            AS metric_scores
    FROM countries c
    JOIN country_metric_values cmv ON cmv.country_id = c.id
    JOIN cii_metric_definitions m  ON m.id = cmv.metric_id AND m.is_active = TRUE
    JOIN scenario_weights sw        ON sw.metric_id = cmv.metric_id
    WHERE c.slug IN ('russia', 'uruguay')
    GROUP BY c.id, sw.scenario_slug
)
INSERT INTO country_cii_scores
    (country_id, version, scenario_slug, overall_score, confidence, drift,
     metric_scores, formula_version, aggregation_method, calculated_at)
SELECT
    country_id,
    'v1.0',
    scenario_slug,
    overall_score,
    'high',
    NULL,
    metric_scores,
    'cii-v1.0',
    'geometric',
    NOW()
FROM computed_scores
ON CONFLICT (country_id, version, scenario_slug) DO UPDATE
    SET overall_score      = EXCLUDED.overall_score,
        metric_scores      = EXCLUDED.metric_scores,
        formula_version    = EXCLUDED.formula_version,
        aggregation_method = EXCLUDED.aggregation_method,
        calculated_at      = EXCLUDED.calculated_at,
        updated_at         = NOW();

CREATE INDEX IF NOT EXISTS idx_scenario_metric_weights_scenario
    ON scenario_metric_weights (scenario_slug);

CREATE INDEX IF NOT EXISTS idx_country_cii_scores_scenario
    ON country_cii_scores (scenario_slug);
