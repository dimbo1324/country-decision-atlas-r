-- Migration 017: Hardens CII methodology: adds formula/method tracking columns and indexes to country_cii_scores.
ALTER TABLE country_cii_scores
    ADD COLUMN IF NOT EXISTS formula_version  TEXT NOT NULL DEFAULT 'cii-v1.0',
    ADD COLUMN IF NOT EXISTS aggregation_method TEXT NOT NULL DEFAULT 'geometric';

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'aggregation_method_check'
          AND conrelid = 'country_cii_scores'::regclass
    ) THEN
        ALTER TABLE country_cii_scores
            ADD CONSTRAINT aggregation_method_check
            CHECK (aggregation_method IN ('linear', 'geometric', 'manual_override'));
    END IF;
END$$;

UPDATE country_cii_scores ccs
SET
    overall_score = sub.geo_score,
    metric_scores = sub.new_metric_scores,
    formula_version = 'cii-v1.0',
    aggregation_method = 'geometric',
    calculated_at = NOW(),
    updated_at = NOW()
FROM (
    SELECT
        c.id AS country_id,
        ROUND(
            CAST(
                EXP(
                    SUM(smw.weight * LN(GREATEST(cmv.normalized_value, 1.0)))
                    / SUM(smw.weight)
                ) AS NUMERIC
            ),
            2
        ) AS geo_score,
        jsonb_agg(
            jsonb_build_object(
                'slug',          m.slug,
                'name_en',       m.name_en,
                'name_ru',       m.name_ru,
                'score',         cmv.normalized_value,
                'weight',        smw.weight,
                'weighted_score', ROUND(
                    CAST(
                        smw.weight * LN(GREATEST(cmv.normalized_value, 1.0))
                        AS NUMERIC
                    ),
                    4
                ),
                'data_year',     cmv.data_year,
                'source_name',   cmv.source_name,
                'reliability',   cmv.reliability
            )
            ORDER BY m.display_order
        ) AS new_metric_scores
    FROM countries c
    JOIN country_metric_values cmv ON cmv.country_id = c.id
    JOIN cii_metric_definitions m  ON m.id = cmv.metric_id AND m.is_active = TRUE
    JOIN scenario_metric_weights smw ON smw.metric_id = cmv.metric_id AND smw.version = 'v1.0'
    GROUP BY c.id
) sub
WHERE ccs.country_id = sub.country_id
  AND ccs.version = 'v1.0';

CREATE INDEX IF NOT EXISTS idx_country_cii_scores_formula
    ON country_cii_scores(formula_version);

CREATE INDEX IF NOT EXISTS idx_country_cii_scores_method
    ON country_cii_scores(aggregation_method);
