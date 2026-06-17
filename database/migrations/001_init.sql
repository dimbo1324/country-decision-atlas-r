CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TABLE IF NOT EXISTS locales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    native_name TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT locales_code_format CHECK (code ~ '^[a-z]{2}(-[A-Z]{2})?$')
);
CREATE TABLE IF NOT EXISTS countries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT NOT NULL UNIQUE,
    iso2 CHAR(2) NOT NULL UNIQUE,
    iso3 CHAR(3) NOT NULL UNIQUE,
    name TEXT NOT NULL,
    official_name TEXT,
    region TEXT,
    subregion TEXT,
    capital TEXT,
    currency_code CHAR(3),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT countries_slug_format CHECK (slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$')
);
CREATE TABLE IF NOT EXISTS country_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_id UUID NOT NULL UNIQUE REFERENCES countries(id) ON DELETE CASCADE,
    summary TEXT NOT NULL,
    residence_overview TEXT,
    citizenship_overview TEXT,
    tax_overview TEXT,
    business_overview TEXT,
    quality_of_life_overview TEXT,
    risk_overview TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    source_type TEXT NOT NULL,
    publisher TEXT,
    country_id UUID REFERENCES countries(id) ON DELETE SET NULL,
    locale_id UUID REFERENCES locales(id) ON DELETE SET NULL,
    reliability_level TEXT NOT NULL DEFAULT 'medium',
    published_at DATE,
    accessed_at DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT sources_reliability_level_check CHECK (reliability_level IN ('low', 'medium', 'high'))
);
CREATE TABLE IF NOT EXISTS evidence_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    country_id UUID REFERENCES countries(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    url TEXT,
    quote TEXT,
    evidence_type TEXT NOT NULL DEFAULT 'source_note',
    confidence_level TEXT NOT NULL DEFAULT 'medium',
    published_at DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT evidence_confidence_level_check CHECK (confidence_level IN ('low', 'medium', 'high'))
);
CREATE TABLE IF NOT EXISTS legal_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_id UUID NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    signal_type TEXT NOT NULL,
    sentiment TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT NOT NULL,
    confidence_level TEXT NOT NULL,
    effective_date DATE,
    published_at DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT legal_signals_signal_type_check CHECK (
        signal_type IN (
            'law',
            'bill',
            'policy',
            'court_decision',
            'administrative_change',
            'political_signal',
            'other'
        )
    ),
    CONSTRAINT legal_signals_sentiment_check CHECK (
        sentiment IN ('positive', 'neutral', 'negative', 'mixed', 'unknown')
    ),
    CONSTRAINT legal_signals_severity_check CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    CONSTRAINT legal_signals_status_check CHECK (
        status IN ('draft', 'proposed', 'adopted', 'rejected', 'active', 'expired', 'unknown')
    ),
    CONSTRAINT legal_signals_confidence_check CHECK (confidence_level IN ('low', 'medium', 'high')),
    CONSTRAINT legal_signals_country_title_unique UNIQUE (country_id, title)
);
CREATE TABLE IF NOT EXISTS legal_signal_evidence (
    legal_signal_id UUID NOT NULL REFERENCES legal_signals(id) ON DELETE CASCADE,
    evidence_item_id UUID NOT NULL REFERENCES evidence_items(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (legal_signal_id, evidence_item_id)
);
CREATE TABLE IF NOT EXISTS scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT scenarios_slug_format CHECK (slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$')
);
CREATE TABLE IF NOT EXISTS scenario_criteria (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID NOT NULL REFERENCES scenarios(id) ON DELETE CASCADE,
    key TEXT NOT NULL,
    label TEXT NOT NULL,
    weight NUMERIC(5, 2) NOT NULL DEFAULT 1.00,
    is_required BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT scenario_criteria_weight_check CHECK (weight >= 0),
    CONSTRAINT scenario_criteria_unique_key UNIQUE (scenario_id, key)
);
CREATE TABLE IF NOT EXISTS country_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_id UUID NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
    scenario_id UUID NOT NULL REFERENCES scenarios(id) ON DELETE CASCADE,
    score NUMERIC(5, 2) NOT NULL,
    score_label TEXT NOT NULL,
    summary TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT country_scores_score_check CHECK (score >= 0 AND score <= 100),
    CONSTRAINT country_scores_unique_country_scenario UNIQUE (country_id, scenario_id)
);
CREATE TABLE IF NOT EXISTS translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    field_name TEXT NOT NULL,
    locale_id UUID NOT NULL REFERENCES locales(id) ON DELETE CASCADE,
    translated_value TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT translations_status_check CHECK (status IN ('draft', 'reviewed', 'approved', 'missing')),
    CONSTRAINT translations_unique_field UNIQUE (entity_type, entity_id, field_name, locale_id)
);
CREATE TABLE IF NOT EXISTS translation_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    source_locale_id UUID REFERENCES locales(id) ON DELETE SET NULL,
    target_locale_id UUID NOT NULL REFERENCES locales(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'queued',
    provider TEXT,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT translation_jobs_status_check CHECK (
        status IN ('queued', 'running', 'completed', 'failed', 'cancelled')
    )
);
CREATE TABLE IF NOT EXISTS translation_glossary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_locale_id UUID NOT NULL REFERENCES locales(id) ON DELETE CASCADE,
    target_locale_id UUID NOT NULL REFERENCES locales(id) ON DELETE CASCADE,
    source_term TEXT NOT NULL,
    target_term TEXT NOT NULL,
    context TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT translation_glossary_unique_term UNIQUE (
        source_locale_id,
        target_locale_id,
        source_term,
        context
    )
);
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT users_role_check CHECK (role IN ('user', 'editor', 'admin'))
);
CREATE TABLE IF NOT EXISTS watchlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    country_id UUID NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT watchlists_unique_user_country UNIQUE (user_id, country_id)
);
CREATE INDEX IF NOT EXISTS idx_locales_code ON locales(code);
CREATE INDEX IF NOT EXISTS idx_countries_slug ON countries(slug);
CREATE INDEX IF NOT EXISTS idx_countries_iso2 ON countries(iso2);
CREATE INDEX IF NOT EXISTS idx_countries_iso3 ON countries(iso3);
CREATE INDEX IF NOT EXISTS idx_sources_country_id ON sources(country_id);
CREATE INDEX IF NOT EXISTS idx_sources_locale_id ON sources(locale_id);
CREATE INDEX IF NOT EXISTS idx_evidence_items_source_id ON evidence_items(source_id);
CREATE INDEX IF NOT EXISTS idx_evidence_items_country_id ON evidence_items(country_id);
CREATE INDEX IF NOT EXISTS idx_legal_signals_country_id ON legal_signals(country_id);
CREATE INDEX IF NOT EXISTS idx_legal_signals_status ON legal_signals(status);
CREATE INDEX IF NOT EXISTS idx_scenarios_slug ON scenarios(slug);
CREATE INDEX IF NOT EXISTS idx_scenario_criteria_scenario_id ON scenario_criteria(scenario_id);
CREATE INDEX IF NOT EXISTS idx_country_scores_country_id ON country_scores(country_id);
CREATE INDEX IF NOT EXISTS idx_country_scores_scenario_id ON country_scores(scenario_id);
CREATE INDEX IF NOT EXISTS idx_translations_entity_key ON translations(
    entity_type,
    entity_id,
    field_name,
    locale_id
);
CREATE INDEX IF NOT EXISTS idx_translation_jobs_status ON translation_jobs(status);
CREATE INDEX IF NOT EXISTS idx_watchlists_user_id ON watchlists(user_id);
DO $$
DECLARE
    table_name TEXT;
BEGIN
    FOREACH table_name IN ARRAY ARRAY[
        'locales',
        'countries',
        'country_profiles',
        'sources',
        'evidence_items',
        'legal_signals',
        'scenarios',
        'scenario_criteria',
        'country_scores',
        'translations',
        'translation_jobs',
        'translation_glossary',
        'users'
    ]
    LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS trg_%I_updated_at ON %I', table_name, table_name);
        EXECUTE format(
            'CREATE TRIGGER trg_%I_updated_at BEFORE UPDATE ON %I
             FOR EACH ROW EXECUTE FUNCTION set_updated_at()',
            table_name,
            table_name
        );
    END LOOP;
END $$;
