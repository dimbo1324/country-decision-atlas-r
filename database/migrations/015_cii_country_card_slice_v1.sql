CREATE TABLE IF NOT EXISTS cii_metric_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT NOT NULL,
    name_en TEXT NOT NULL,
    name_ru TEXT NOT NULL,
    description_en TEXT NOT NULL,
    description_ru TEXT NOT NULL,
    polarity TEXT NOT NULL DEFAULT 'positive',
    source_name TEXT,
    source_url TEXT,
    display_order INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_cii_metric_definitions_slug UNIQUE (slug),
    CONSTRAINT cii_metric_polarity_check CHECK (polarity IN ('positive', 'negative'))
);

CREATE TABLE IF NOT EXISTS country_metric_values (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_id UUID NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
    metric_id UUID NOT NULL REFERENCES cii_metric_definitions(id) ON DELETE CASCADE,
    raw_value NUMERIC(7, 2) NOT NULL,
    normalized_value NUMERIC(5, 2) NOT NULL,
    data_year INT,
    source_name TEXT,
    source_url TEXT,
    reliability TEXT NOT NULL DEFAULT 'medium',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_country_metric_values UNIQUE (country_id, metric_id),
    CONSTRAINT country_metric_reliability_check CHECK (reliability IN ('high', 'medium', 'low')),
    CONSTRAINT normalized_value_range CHECK (normalized_value >= 0 AND normalized_value <= 100)
);

CREATE TABLE IF NOT EXISTS scenario_metric_weights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version TEXT NOT NULL DEFAULT 'v1.0',
    metric_id UUID NOT NULL REFERENCES cii_metric_definitions(id) ON DELETE CASCADE,
    weight NUMERIC(5, 4) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_scenario_metric_weight UNIQUE (version, metric_id),
    CONSTRAINT weight_range CHECK (weight >= 0 AND weight <= 1)
);

CREATE TABLE IF NOT EXISTS country_cii_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_id UUID NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
    version TEXT NOT NULL DEFAULT 'v1.0',
    overall_score NUMERIC(5, 2) NOT NULL,
    confidence TEXT NOT NULL DEFAULT 'medium',
    drift NUMERIC(6, 2),
    metric_scores JSONB NOT NULL DEFAULT '[]'::jsonb,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_country_cii_version UNIQUE (country_id, version),
    CONSTRAINT country_cii_confidence_check CHECK (confidence IN ('high', 'medium', 'low')),
    CONSTRAINT overall_score_range CHECK (overall_score >= 0 AND overall_score <= 100)
);

CREATE INDEX IF NOT EXISTS idx_cii_metric_definitions_slug
    ON cii_metric_definitions(slug);

CREATE INDEX IF NOT EXISTS idx_country_metric_values_country
    ON country_metric_values(country_id);

CREATE INDEX IF NOT EXISTS idx_country_metric_values_metric
    ON country_metric_values(metric_id);

CREATE INDEX IF NOT EXISTS idx_country_cii_scores_country
    ON country_cii_scores(country_id);

CREATE INDEX IF NOT EXISTS idx_country_cii_scores_score
    ON country_cii_scores(overall_score DESC);

CREATE OR REPLACE TRIGGER trg_cii_metric_definitions_updated_at
BEFORE UPDATE ON cii_metric_definitions
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE TRIGGER trg_country_metric_values_updated_at
BEFORE UPDATE ON country_metric_values
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE TRIGGER trg_country_cii_scores_updated_at
BEFORE UPDATE ON country_cii_scores
FOR EACH ROW EXECUTE FUNCTION set_updated_at();
