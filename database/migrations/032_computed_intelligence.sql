-- Migration 032: Self-computed intelligence v1: adds the country_platform_metrics table for server-computed metrics.
CREATE TABLE IF NOT EXISTS country_platform_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_id UUID NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
    metric_key TEXT NOT NULL,
    scenario_slug TEXT NOT NULL DEFAULT '__global__',
    value NUMERIC(5, 2),
    label TEXT NOT NULL,
    confidence TEXT NOT NULL,
    freshness_status TEXT NOT NULL,
    window_days INT NOT NULL,
    methodology_version TEXT NOT NULL,
    input_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
    source_count INT NOT NULL DEFAULT 0,
    evidence_count INT NOT NULL DEFAULT 0,
    signal_count INT NOT NULL DEFAULT 0,
    event_count INT NOT NULL DEFAULT 0,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT country_platform_metrics_metric_key_check
        CHECK (metric_key IN (
            'legal_velocity_index',
            'scenario_specific_risk_score',
            'contradiction_score'
        )),
    CONSTRAINT country_platform_metrics_scenario_slug_check
        CHECK (
            scenario_slug = '__global__'
            OR scenario_slug ~ '^[a-z0-9_]+$'
        ),
    CONSTRAINT country_platform_metrics_value_check
        CHECK (value IS NULL OR (value >= 0 AND value <= 100)),
    CONSTRAINT country_platform_metrics_label_check
        CHECK (label IN (
            'insufficient_data',
            'low',
            'moderate',
            'elevated',
            'high',
            'critical'
        )),
    CONSTRAINT country_platform_metrics_confidence_check
        CHECK (confidence IN ('low', 'medium', 'high')),
    CONSTRAINT country_platform_metrics_freshness_status_check
        CHECK (freshness_status IN ('fresh', 'stale', 'unknown')),
    CONSTRAINT country_platform_metrics_window_days_check
        CHECK (window_days > 0),
    CONSTRAINT country_platform_metrics_methodology_version_check
        CHECK (BTRIM(methodology_version) <> ''),
    CONSTRAINT country_platform_metrics_counts_check
        CHECK (
            source_count >= 0
            AND evidence_count >= 0
            AND signal_count >= 0
            AND event_count >= 0
        ),
    CONSTRAINT country_platform_metrics_input_summary_object_check
        CHECK (jsonb_typeof(input_summary) = 'object'),
    CONSTRAINT country_platform_metrics_unique
        UNIQUE (
            country_id,
            metric_key,
            scenario_slug,
            methodology_version
        )
);

CREATE INDEX IF NOT EXISTS idx_country_platform_metrics_country
    ON country_platform_metrics (country_id);

CREATE INDEX IF NOT EXISTS idx_country_platform_metrics_metric_key
    ON country_platform_metrics (metric_key);

CREATE INDEX IF NOT EXISTS idx_country_platform_metrics_scenario
    ON country_platform_metrics (scenario_slug);

CREATE INDEX IF NOT EXISTS idx_country_platform_metrics_computed_at
    ON country_platform_metrics (computed_at DESC);

CREATE INDEX IF NOT EXISTS idx_country_platform_metrics_country_metric
    ON country_platform_metrics (country_id, metric_key);

CREATE INDEX IF NOT EXISTS idx_country_platform_metrics_country_metric_scenario
    ON country_platform_metrics (
        country_id,
        metric_key,
        scenario_slug
    );
