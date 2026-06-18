ALTER TABLE
    sources
ADD
    COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'draft';

ALTER TABLE
    evidence_items
ADD
    COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'draft';

ALTER TABLE
    country_profiles
ADD
    COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'draft';

ALTER TABLE
    sources ALTER COLUMN url DROP NOT NULL;

ALTER TABLE
    sources ALTER COLUMN source_type DROP NOT NULL;

ALTER TABLE
    evidence_items ALTER COLUMN source_id DROP NOT NULL;

UPDATE
    sources
SET
    status = 'published'
WHERE
    status IN ('draft', 'active', 'adopted', 'unknown', 'editor_reviewed');

UPDATE
    evidence_items
SET
    status = 'published'
WHERE
    status IN ('draft', 'active', 'adopted', 'unknown', 'editor_reviewed');

UPDATE
    legal_signals
SET
    status = CASE
        WHEN status IN ('active', 'adopted', 'published') THEN 'published'
        WHEN status IN ('proposed', 'editor_reviewed', 'expert_review_required') THEN 'review'
        WHEN status = 'expired' THEN 'archived'
        WHEN status = 'rejected' THEN 'rejected'
        ELSE 'draft'
    END;

UPDATE
    user_stories
SET
    status = CASE
        WHEN status = 'published' THEN 'published'
        WHEN status IN ('editor_reviewed', 'expert_review_required') THEN 'review'
        WHEN status = 'archived' THEN 'archived'
        WHEN status = 'rejected' THEN 'rejected'
        ELSE 'draft'
    END;

UPDATE
    country_cards
SET
    status = CASE
        WHEN status = 'published' THEN 'published'
        WHEN status IN ('editor_reviewed', 'expert_review_required') THEN 'review'
        WHEN status = 'archived' THEN 'archived'
        WHEN status = 'rejected' THEN 'rejected'
        ELSE 'draft'
    END;

UPDATE
    country_profiles
SET
    status = 'published'
WHERE
    status = 'draft';

ALTER TABLE
    sources DROP CONSTRAINT IF EXISTS sources_status_check;

ALTER TABLE
    evidence_items DROP CONSTRAINT IF EXISTS evidence_items_status_check;

ALTER TABLE
    legal_signals DROP CONSTRAINT IF EXISTS legal_signals_status_check;

ALTER TABLE
    user_stories DROP CONSTRAINT IF EXISTS user_stories_status_check;

ALTER TABLE
    country_cards DROP CONSTRAINT IF EXISTS country_cards_status_check;

ALTER TABLE
    country_profiles DROP CONSTRAINT IF EXISTS country_profiles_status_check;

ALTER TABLE
    sources
ADD
    CONSTRAINT sources_status_check CHECK (
        status IN ('draft', 'review', 'published', 'archived', 'rejected')
    );

ALTER TABLE
    evidence_items
ADD
    CONSTRAINT evidence_items_status_check CHECK (
        status IN ('draft', 'review', 'published', 'archived', 'rejected')
    );

ALTER TABLE
    legal_signals
ADD
    CONSTRAINT legal_signals_status_check CHECK (
        status IN ('draft', 'review', 'published', 'archived', 'rejected')
    );

ALTER TABLE
    user_stories
ADD
    CONSTRAINT user_stories_status_check CHECK (
        status IN ('draft', 'review', 'published', 'archived', 'rejected')
    );

ALTER TABLE
    country_cards
ADD
    CONSTRAINT country_cards_status_check CHECK (
        status IN ('draft', 'review', 'published', 'archived', 'rejected')
    );

ALTER TABLE
    country_profiles
ADD
    CONSTRAINT country_profiles_status_check CHECK (
        status IN ('draft', 'review', 'published', 'archived', 'rejected')
    );

ALTER TABLE
    sources ALTER COLUMN status SET DEFAULT 'draft';

ALTER TABLE
    evidence_items ALTER COLUMN status SET DEFAULT 'draft';

ALTER TABLE
    legal_signals ALTER COLUMN status SET DEFAULT 'draft';

ALTER TABLE
    user_stories ALTER COLUMN status SET DEFAULT 'draft';

ALTER TABLE
    country_cards ALTER COLUMN status SET DEFAULT 'draft';

ALTER TABLE
    country_profiles ALTER COLUMN status SET DEFAULT 'draft';

CREATE TABLE IF NOT EXISTS audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    action TEXT NOT NULL,
    changed_by TEXT NOT NULL,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    changes JSONB NOT NULL DEFAULT '{}' :: jsonb,
    CONSTRAINT audit_events_action_check CHECK (
        action IN (
            'created',
            'updated',
            'submitted_for_review',
            'published',
            'archived',
            'rejected'
        )
    )
);

CREATE INDEX IF NOT EXISTS idx_sources_status ON sources(status);

CREATE INDEX IF NOT EXISTS idx_sources_public_filters ON sources(
    country_id,
    source_type,
    language,
    confidence,
    status
);

CREATE INDEX IF NOT EXISTS idx_evidence_items_status ON evidence_items(status);

CREATE INDEX IF NOT EXISTS idx_evidence_items_public_filters ON evidence_items(
    country_id,
    source_id,
    legal_signal_id,
    confidence,
    status
);

CREATE INDEX IF NOT EXISTS idx_legal_signals_public_filters ON legal_signals(
    country_id,
    signal_type,
    impact_direction,
    impact_level,
    status
);

CREATE INDEX IF NOT EXISTS idx_user_stories_public_filters ON user_stories(
    origin_country_id,
    destination_country_id,
    scenario,
    verification_status,
    status
);

CREATE INDEX IF NOT EXISTS idx_audit_events_entity ON audit_events(entity_type, entity_id);

CREATE INDEX IF NOT EXISTS idx_audit_events_changed_at ON audit_events(changed_at DESC);
