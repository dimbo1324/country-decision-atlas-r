-- Migration 039: Adds the decision_passports table capturing a snapshot of a decision run and what changed since.
CREATE TABLE IF NOT EXISTS decision_passports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    public_token_hash TEXT NOT NULL UNIQUE,
    public_token_prefix TEXT NOT NULL,
    locale TEXT NOT NULL DEFAULT 'ru',
    scenario_slug TEXT NOT NULL,
    persona_slug TEXT,
    origin_country_slug TEXT,
    candidate_country_slugs JSONB NOT NULL DEFAULT '[]'::jsonb,
    selected_country_slug TEXT,
    decision_request JSONB NOT NULL DEFAULT '{}'::jsonb,
    decision_result_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    methodology_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    source_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    route_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    disclaimer TEXT NOT NULL DEFAULT 'This is not legal advice.',
    status TEXT NOT NULL DEFAULT 'active',
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT decision_passports_status_check
        CHECK (status IN ('active', 'expired', 'revoked')),
    CONSTRAINT decision_passports_locale_check
        CHECK (locale IN ('ru', 'en')),
    CONSTRAINT decision_passports_candidate_country_slugs_array_check
        CHECK (jsonb_typeof(candidate_country_slugs) = 'array'),
    CONSTRAINT decision_passports_decision_request_object_check
        CHECK (jsonb_typeof(decision_request) = 'object'),
    CONSTRAINT decision_passports_result_snapshot_object_check
        CHECK (jsonb_typeof(decision_result_snapshot) = 'object'),
    CONSTRAINT decision_passports_methodology_snapshot_object_check
        CHECK (jsonb_typeof(methodology_snapshot) = 'object'),
    CONSTRAINT decision_passports_source_ids_array_check
        CHECK (jsonb_typeof(source_ids) = 'array'),
    CONSTRAINT decision_passports_route_ids_array_check
        CHECK (jsonb_typeof(route_ids) = 'array')
);

CREATE INDEX IF NOT EXISTS idx_decision_passports_scenario
    ON decision_passports (scenario_slug);

CREATE INDEX IF NOT EXISTS idx_decision_passports_persona
    ON decision_passports (persona_slug);

CREATE INDEX IF NOT EXISTS idx_decision_passports_origin
    ON decision_passports (origin_country_slug);

CREATE INDEX IF NOT EXISTS idx_decision_passports_selected_country
    ON decision_passports (selected_country_slug);

CREATE INDEX IF NOT EXISTS idx_decision_passports_generated_at
    ON decision_passports (generated_at DESC);

CREATE INDEX IF NOT EXISTS idx_decision_passports_status
    ON decision_passports (status);
