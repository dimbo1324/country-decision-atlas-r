-- Migration 050: Country contribution v1 opens the content core to the community: a proposal
-- lifecycle with curator assignment, and conservation of the RU/UY/AR demo set via is_demo.
ALTER TABLE countries
    ADD COLUMN IF NOT EXISTS is_demo BOOLEAN NOT NULL DEFAULT FALSE;

CREATE TABLE IF NOT EXISTS country_proposals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposer_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    country_id UUID NOT NULL UNIQUE REFERENCES countries(id) ON DELETE CASCADE,
    slug TEXT NOT NULL UNIQUE,
    name_en TEXT NOT NULL,
    name_ru TEXT NOT NULL,
    iso2 CHAR(2) NOT NULL,
    iso3 CHAR(3) NOT NULL,
    justification TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    curator_user_id UUID REFERENCES users(id),
    readiness_snapshot JSONB,
    moderated_by UUID REFERENCES users(id),
    moderated_at TIMESTAMPTZ,
    moderation_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    CONSTRAINT country_proposals_slug_check CHECK (slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$'),
    CONSTRAINT country_proposals_name_en_check CHECK (BTRIM(name_en) <> ''),
    CONSTRAINT country_proposals_name_ru_check CHECK (BTRIM(name_ru) <> ''),
    CONSTRAINT country_proposals_justification_check CHECK (BTRIM(justification) <> ''),
    CONSTRAINT country_proposals_status_check
        CHECK (status IN ('draft', 'review', 'published', 'archived', 'rejected'))
);

CREATE INDEX IF NOT EXISTS idx_country_proposals_status
    ON country_proposals (status);

CREATE INDEX IF NOT EXISTS idx_country_proposals_proposer
    ON country_proposals (proposer_user_id);

CREATE INDEX IF NOT EXISTS idx_country_proposals_curator
    ON country_proposals (curator_user_id)
    WHERE curator_user_id IS NOT NULL;

DROP TRIGGER IF EXISTS trg_country_proposals_updated_at ON country_proposals;
CREATE TRIGGER trg_country_proposals_updated_at
    BEFORE UPDATE ON country_proposals
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Decision R-1: demo countries are never deleted, only hidden from public surfaces.
-- is_active stays TRUE so they keep passing the onboarding gate as the pipeline's first patients.
UPDATE countries SET is_demo = TRUE WHERE slug IN ('russia', 'uruguay', 'argentina');

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
    'country_contribution_enabled',
    'Country contribution',
    'Enables community country proposals: contributor-scoped content filling, curator review, and the onboarding-gated publish pipeline.',
    'enabled',
    'public',
    TRUE,
    '{"episode":"country-contribution-v1"}'::jsonb
)
ON CONFLICT (key) DO NOTHING;

INSERT INTO feature_access_rules (
    feature_key,
    access_tier,
    is_enabled
)
VALUES
    ('country_contribution_enabled', 'public', TRUE)
ON CONFLICT (feature_key, access_tier) DO NOTHING;
