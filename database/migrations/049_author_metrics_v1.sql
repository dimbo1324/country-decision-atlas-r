-- Migration 049: Author metrics v1 opens the metrics system to the community: definitions, values,
-- subscriptions, and a derived author reputation, kept entirely separate from the platform CII.
CREATE TABLE IF NOT EXISTS author_metric_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    slug TEXT NOT NULL,
    name_en TEXT NOT NULL,
    name_ru TEXT NOT NULL,
    methodology_en TEXT NOT NULL DEFAULT '',
    methodology_ru TEXT NOT NULL DEFAULT '',
    polarity TEXT NOT NULL DEFAULT 'higher_is_better',
    scale_min NUMERIC NOT NULL DEFAULT 0,
    scale_max NUMERIC NOT NULL DEFAULT 100,
    license TEXT NOT NULL DEFAULT 'platform',
    status TEXT NOT NULL DEFAULT 'draft',
    visibility TEXT NOT NULL DEFAULT 'private',
    forked_from_id UUID REFERENCES author_metric_definitions(id) ON DELETE SET NULL,
    version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    submitted_at TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    archived_at TIMESTAMPTZ,
    rejected_at TIMESTAMPTZ,
    moderated_by UUID REFERENCES users(id),
    moderated_at TIMESTAMPTZ,
    moderation_reason TEXT,
    CONSTRAINT uq_author_metric_definitions_author_slug UNIQUE (author_user_id, slug),
    CONSTRAINT author_metric_definitions_slug_check CHECK (BTRIM(slug) <> ''),
    CONSTRAINT author_metric_definitions_name_en_check CHECK (BTRIM(name_en) <> ''),
    CONSTRAINT author_metric_definitions_name_ru_check CHECK (BTRIM(name_ru) <> ''),
    CONSTRAINT author_metric_definitions_polarity_check
        CHECK (polarity IN ('higher_is_better', 'lower_is_better')),
    CONSTRAINT author_metric_definitions_scale_check CHECK (scale_min < scale_max),
    CONSTRAINT author_metric_definitions_license_check
        CHECK (license IN ('platform', 'cc_by_sa')),
    CONSTRAINT author_metric_definitions_status_check
        CHECK (
            status IN ('draft', 'review', 'published', 'archived', 'rejected')
        ),
    CONSTRAINT author_metric_definitions_visibility_check
        CHECK (visibility IN ('private', 'public'))
);

CREATE TABLE IF NOT EXISTS author_metric_values (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_id UUID NOT NULL REFERENCES author_metric_definitions(id) ON DELETE CASCADE,
    country_id UUID NOT NULL REFERENCES countries(id),
    value NUMERIC NOT NULL,
    source_url TEXT,
    is_personal_experience BOOLEAN NOT NULL DEFAULT FALSE,
    note TEXT,
    valid_as_of DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_author_metric_values_metric_country UNIQUE (metric_id, country_id),
    CONSTRAINT author_metric_values_source_check
        CHECK (source_url IS NOT NULL OR is_personal_experience)
);

CREATE TABLE IF NOT EXISTS author_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    metric_id UUID REFERENCES author_metric_definitions(id) ON DELETE CASCADE,
    author_user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT author_subscriptions_target_check
        CHECK (metric_id IS NOT NULL OR author_user_id IS NOT NULL)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_author_subscriptions_user_metric
    ON author_subscriptions (user_id, metric_id)
    WHERE metric_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_author_subscriptions_user_author
    ON author_subscriptions (user_id, author_user_id)
    WHERE author_user_id IS NOT NULL;

CREATE TABLE IF NOT EXISTS author_reputation (
    author_user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    coverage_score NUMERIC NOT NULL DEFAULT 0,
    freshness_score NUMERIC NOT NULL DEFAULT 0,
    sourcing_score NUMERIC NOT NULL DEFAULT 0,
    subscriber_count INT NOT NULL DEFAULT 0,
    published_metric_count INT NOT NULL DEFAULT 0,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    methodology_version TEXT NOT NULL DEFAULT 'v1.0'
);

CREATE INDEX IF NOT EXISTS idx_author_metric_definitions_author_status
    ON author_metric_definitions (author_user_id, status);

CREATE INDEX IF NOT EXISTS idx_author_metric_definitions_status
    ON author_metric_definitions (status);

CREATE INDEX IF NOT EXISTS idx_author_metric_definitions_forked_from
    ON author_metric_definitions (forked_from_id)
    WHERE forked_from_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_author_metric_values_metric
    ON author_metric_values (metric_id);

CREATE INDEX IF NOT EXISTS idx_author_metric_values_country
    ON author_metric_values (country_id);

CREATE INDEX IF NOT EXISTS idx_author_subscriptions_user
    ON author_subscriptions (user_id);

CREATE INDEX IF NOT EXISTS idx_author_subscriptions_metric
    ON author_subscriptions (metric_id)
    WHERE metric_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_author_subscriptions_author
    ON author_subscriptions (author_user_id)
    WHERE author_user_id IS NOT NULL;

DROP TRIGGER IF EXISTS trg_author_metric_definitions_updated_at
    ON author_metric_definitions;
CREATE TRIGGER trg_author_metric_definitions_updated_at
    BEFORE UPDATE ON author_metric_definitions
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_author_metric_values_updated_at
    ON author_metric_values;
CREATE TRIGGER trg_author_metric_values_updated_at
    BEFORE UPDATE ON author_metric_values
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

INSERT INTO feature_flags (
    key,
    name,
    description,
    status,
    access_tier,
    default_enabled,
    metadata
)
VALUES (
    'author_metrics_enabled',
    'Author metrics',
    'Enables community-authored metric definitions, values, subscriptions, and forks.',
    'enabled',
    'public',
    TRUE,
    '{"episode":"author-metrics-v1"}'::jsonb
)
ON CONFLICT (key) DO NOTHING;

INSERT INTO feature_access_rules (
    feature_key,
    access_tier,
    is_enabled
)
VALUES
    ('author_metrics_enabled', 'public', TRUE)
ON CONFLICT (feature_key, access_tier) DO NOTHING;

INSERT INTO methodology_parameters (
    version,
    param_key,
    value_numeric,
    description
)
VALUES
    (
        'v1.0',
        'author_metrics.min_methodology_length',
        120,
        'Minimum combined methodology text length (characters) required to submit an author metric definition for review.'
    ),
    (
        'v1.0',
        'author_metrics.min_country_coverage',
        5,
        'Minimum number of countries with values required to publish an author metric definition.'
    )
ON CONFLICT (version, param_key) DO NOTHING;
