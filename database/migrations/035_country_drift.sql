-- Migration 035: Adds the country_drift_snapshots table tracking direction-of-change signals per country/period.
CREATE TABLE IF NOT EXISTS country_drift_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_id UUID NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    window_days INTEGER NOT NULL DEFAULT 180,
    label TEXT NOT NULL,
    previous_label TEXT,
    confidence TEXT NOT NULL,
    net_score NUMERIC(7, 2),
    positive_weight NUMERIC(10, 2) NOT NULL DEFAULT 0,
    negative_weight NUMERIC(10, 2) NOT NULL DEFAULT 0,
    neutral_weight NUMERIC(10, 2) NOT NULL DEFAULT 0,
    mixed_weight NUMERIC(10, 2) NOT NULL DEFAULT 0,
    uncertain_weight NUMERIC(10, 2) NOT NULL DEFAULT 0,
    total_weight NUMERIC(10, 2) NOT NULL DEFAULT 0,
    event_count INTEGER NOT NULL DEFAULT 0,
    positive_count INTEGER NOT NULL DEFAULT 0,
    negative_count INTEGER NOT NULL DEFAULT 0,
    neutral_count INTEGER NOT NULL DEFAULT 0,
    mixed_count INTEGER NOT NULL DEFAULT 0,
    uncertain_count INTEGER NOT NULL DEFAULT 0,
    methodology_version TEXT NOT NULL DEFAULT 'v1.0',
    input_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT country_drift_snapshots_period_check
        CHECK (period_start <= period_end),
    CONSTRAINT country_drift_snapshots_window_days_check
        CHECK (window_days > 0),
    CONSTRAINT country_drift_snapshots_label_check
        CHECK (label IN (
            'insufficient_data',
            'negative',
            'stable',
            'mildly_positive',
            'positive'
        )),
    CONSTRAINT country_drift_snapshots_previous_label_check
        CHECK (
            previous_label IS NULL
            OR previous_label IN (
                'insufficient_data',
                'negative',
                'stable',
                'mildly_positive',
                'positive'
            )
        ),
    CONSTRAINT country_drift_snapshots_confidence_check
        CHECK (confidence IN ('low', 'medium', 'high')),
    CONSTRAINT country_drift_snapshots_net_score_check
        CHECK (
            net_score IS NULL
            OR (net_score >= -100 AND net_score <= 100)
        ),
    CONSTRAINT country_drift_snapshots_weight_check
        CHECK (
            positive_weight >= 0
            AND negative_weight >= 0
            AND neutral_weight >= 0
            AND mixed_weight >= 0
            AND uncertain_weight >= 0
            AND total_weight >= 0
        ),
    CONSTRAINT country_drift_snapshots_count_check
        CHECK (
            event_count >= 0
            AND positive_count >= 0
            AND negative_count >= 0
            AND neutral_count >= 0
            AND mixed_count >= 0
            AND uncertain_count >= 0
        ),
    CONSTRAINT country_drift_snapshots_input_summary_object_check
        CHECK (jsonb_typeof(input_summary) = 'object'),
    CONSTRAINT country_drift_snapshots_unique_period
        UNIQUE (country_id, period_start, period_end, methodology_version)
);

CREATE INDEX IF NOT EXISTS idx_country_drift_snapshots_country_period
    ON country_drift_snapshots (country_id, period_end DESC);

CREATE INDEX IF NOT EXISTS idx_country_drift_snapshots_label
    ON country_drift_snapshots (label);

CREATE INDEX IF NOT EXISTS idx_country_drift_snapshots_confidence
    ON country_drift_snapshots (confidence);

CREATE INDEX IF NOT EXISTS idx_country_drift_snapshots_computed_at
    ON country_drift_snapshots (computed_at DESC);

CREATE INDEX IF NOT EXISTS idx_country_drift_snapshots_expires_at
    ON country_drift_snapshots (expires_at)
    WHERE expires_at IS NOT NULL;
