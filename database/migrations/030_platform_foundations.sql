-- Migration 030: Platform foundations: adds the analytics_events table with indexes for event-type/session/country/scenario queries.
CREATE TABLE IF NOT EXISTS analytics_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_hash TEXT NOT NULL,
    event_type TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'web',
    path TEXT,
    locale TEXT,
    country_slug TEXT,
    scenario_slug TEXT,
    persona_slug TEXT,
    route_id UUID,
    entity_type TEXT,
    entity_id UUID,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT analytics_events_session_hash_check
        CHECK (LENGTH(session_hash) BETWEEN 32 AND 128),
    CONSTRAINT analytics_events_type_check
        CHECK (event_type ~ '^[a-z][a-z0-9_]{1,63}$'),
    CONSTRAINT analytics_events_source_check
        CHECK (source IN ('web', 'api', 'worker', 'notifier', 'unknown')),
    CONSTRAINT analytics_events_metadata_object_check
        CHECK (jsonb_typeof(metadata) = 'object'),
    CONSTRAINT analytics_events_metadata_size_check
        CHECK (pg_column_size(metadata) <= 4096),
    CONSTRAINT analytics_events_no_pii_metadata_keys_check
        CHECK (
            NOT metadata ?| ARRAY[
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
        )
);

CREATE INDEX IF NOT EXISTS idx_analytics_events_created_at
    ON analytics_events (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_analytics_events_event_type_created_at
    ON analytics_events (event_type, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_analytics_events_session_created_at
    ON analytics_events (session_hash, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_analytics_events_country_created_at
    ON analytics_events (country_slug, created_at DESC)
    WHERE country_slug IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_analytics_events_scenario_created_at
    ON analytics_events (scenario_slug, created_at DESC)
    WHERE scenario_slug IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_analytics_events_persona_created_at
    ON analytics_events (persona_slug, created_at DESC)
    WHERE persona_slug IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_analytics_events_route_created_at
    ON analytics_events (route_id, created_at DESC)
    WHERE route_id IS NOT NULL;

CREATE TABLE IF NOT EXISTS feature_flags (
    key TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'disabled',
    access_tier TEXT NOT NULL DEFAULT 'public',
    default_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT feature_flags_key_check
        CHECK (key ~ '^[a-z][a-z0-9_]{1,63}$'),
    CONSTRAINT feature_flags_status_check
        CHECK (status IN ('enabled', 'disabled', 'internal', 'deprecated')),
    CONSTRAINT feature_flags_access_tier_check
        CHECK (access_tier IN ('public', 'beta', 'internal', 'admin')),
    CONSTRAINT feature_flags_metadata_object_check
        CHECK (jsonb_typeof(metadata) = 'object')
);

INSERT INTO feature_flags (
    key,
    name,
    description,
    status,
    access_tier,
    default_enabled
)
VALUES
    (
        'analytics_enabled',
        'Anonymous analytics',
        'Anonymous session-based analytics without PII.',
        'enabled',
        'public',
        TRUE
    ),
    (
        'data_journal_enabled',
        'Country data journal',
        'Public country data update journal.',
        'disabled',
        'public',
        FALSE
    ),
    (
        'redis_cache_enabled',
        'Redis read-model cache',
        'Read-model cache for public endpoints.',
        'disabled',
        'internal',
        FALSE
    ),
    (
        'trust_surface_enabled',
        'Trust transparency surface',
        'Trust score and confidence/freshness UI.',
        'disabled',
        'internal',
        FALSE
    ),
    (
        'drift_enabled',
        'Country direction drift',
        'Legal direction drift intelligence.',
        'disabled',
        'internal',
        FALSE
    ),
    (
        'ai_enabled',
        'AI augmentation',
        'Fake-by-default grounded AI assistance.',
        'disabled',
        'internal',
        FALSE
    ),
    (
        'community_enabled',
        'Community intelligence',
        'Q&A, reports and community-derived signals.',
        'disabled',
        'internal',
        FALSE
    )
ON CONFLICT (key) DO NOTHING;

CREATE TABLE IF NOT EXISTS feature_access_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    feature_key TEXT NOT NULL REFERENCES feature_flags(key) ON DELETE CASCADE,
    access_tier TEXT NOT NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT feature_access_rules_unique
        UNIQUE (feature_key, access_tier),
    CONSTRAINT feature_access_rules_tier_check
        CHECK (access_tier IN ('public', 'beta', 'internal', 'admin')),
    CONSTRAINT feature_access_rules_metadata_object_check
        CHECK (jsonb_typeof(metadata) = 'object')
);

INSERT INTO feature_access_rules (
    feature_key,
    access_tier,
    is_enabled
)
SELECT
    key,
    access_tier,
    default_enabled
FROM feature_flags
ON CONFLICT (feature_key, access_tier) DO NOTHING;
