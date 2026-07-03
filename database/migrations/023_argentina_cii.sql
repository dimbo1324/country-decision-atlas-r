-- Migration 023: Seeds Argentina's CII integration: country metric values and CII scores.
INSERT INTO country_metric_values
    (country_id, metric_id, raw_value, normalized_value, data_year, source_name, source_url, reliability)
SELECT
    c.id,
    m.id,
    v.raw_value,
    v.normalized_value,
    v.data_year,
    v.source_name,
    v.source_url,
    v.reliability
FROM countries c
CROSS JOIN (
    VALUES
        ('rule_of_law',        38.00, 38.00, 2023, 'World Bank WGI 2023',                      'https://info.worldbank.org/governance/wgi/',        'high'),
        ('economic_freedom',   44.80, 44.80, 2024, 'Heritage Foundation Index 2024',            'https://www.heritage.org/index/',                  'high'),
        ('political_stability', 30.00, 30.00, 2023, 'World Bank WGI 2023',                     'https://info.worldbank.org/governance/wgi/',        'high'),
        ('safety',             55.00, 55.00, 2023, 'Global Peace Index 2023 (inverted)',        'https://www.visionofhumanity.org/maps/#/',          'high'),
        ('corruption',         37.00, 37.00, 2023, 'Transparency International CPI 2023',      'https://www.transparency.org/en/cpi/2023',         'high'),
        ('digital_access',     68.00, 68.00, 2023, 'Freedom House: Freedom on the Net 2023',   'https://freedomhouse.org/report/freedom-net',      'high')
) AS v(metric_slug, raw_value, normalized_value, data_year, source_name, source_url, reliability)
JOIN cii_metric_definitions m ON m.slug = v.metric_slug
WHERE c.slug = 'argentina'
ON CONFLICT (country_id, metric_id) DO UPDATE
    SET normalized_value = EXCLUDED.normalized_value,
        raw_value        = EXCLUDED.raw_value,
        data_year        = EXCLUDED.data_year,
        source_name      = EXCLUDED.source_name,
        source_url       = EXCLUDED.source_url,
        reliability      = EXCLUDED.reliability,
        updated_at       = NOW();

WITH overall_computed AS (
    SELECT
        c.id AS country_id,
        ROUND(
            CAST(
                EXP(
                    SUM(smw.weight * LN(GREATEST(CAST(cmv.normalized_value AS float), 1.0)))
                    / NULLIF(SUM(smw.weight), 0)
                ) AS NUMERIC
            ),
            2
        ) AS overall_score,
        jsonb_agg(
            jsonb_build_object(
                'slug',           m.slug,
                'name_en',        m.name_en,
                'name_ru',        m.name_ru,
                'score',          cmv.normalized_value,
                'weight',         smw.weight,
                'weighted_score', ROUND(
                    CAST(
                        smw.weight * LN(GREATEST(CAST(cmv.normalized_value AS float), 1.0))
                        AS NUMERIC
                    ),
                    4
                ),
                'data_year',      cmv.data_year,
                'source_name',    cmv.source_name,
                'reliability',    cmv.reliability
            )
            ORDER BY m.display_order
        ) AS metric_scores
    FROM countries c
    JOIN country_metric_values cmv ON cmv.country_id = c.id
    JOIN cii_metric_definitions m  ON m.id = cmv.metric_id AND m.is_active = TRUE
    JOIN scenario_metric_weights smw
        ON smw.metric_id = cmv.metric_id
       AND smw.version = 'v1.0'
       AND smw.scenario_slug = ''
    WHERE c.slug = 'argentina'
    GROUP BY c.id
)
INSERT INTO country_cii_scores
    (country_id, version, scenario_slug, overall_score, confidence, drift,
     metric_scores, formula_version, aggregation_method, calculated_at)
SELECT
    country_id,
    'v1.0',
    '',
    overall_score,
    'high',
    NULL,
    metric_scores,
    'cii-v1.0',
    'geometric',
    NOW()
FROM overall_computed
ON CONFLICT (country_id, version, scenario_slug) DO UPDATE
    SET overall_score      = EXCLUDED.overall_score,
        metric_scores      = EXCLUDED.metric_scores,
        formula_version    = EXCLUDED.formula_version,
        aggregation_method = EXCLUDED.aggregation_method,
        calculated_at      = EXCLUDED.calculated_at,
        updated_at         = NOW();

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
                    SUM(sw.weight * LN(GREATEST(CAST(cmv.normalized_value AS float), 1.0)))
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
                        sw.weight * LN(GREATEST(CAST(cmv.normalized_value AS float), 1.0))
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
    WHERE c.slug = 'argentina'
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
