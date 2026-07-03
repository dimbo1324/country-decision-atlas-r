-- Migration 042: AI drafts and community foundation: adds ai_drafts and contradiction_candidates tables plus community Q&A tables.
CREATE TABLE IF NOT EXISTS ai_drafts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    draft_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'needs_review',
    country_slug TEXT,
    route_id UUID,
    legal_signal_id UUID,
    source_id UUID REFERENCES sources(id) ON DELETE SET NULL,
    evidence_item_id UUID REFERENCES evidence_items(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    summary TEXT,
    detected_issue TEXT,
    provider TEXT NOT NULL DEFAULT 'fake',
    model_name TEXT NOT NULL DEFAULT 'fake-grounded-v1',
    model_version TEXT NOT NULL DEFAULT 'v1',
    input_context JSONB NOT NULL DEFAULT '{}'::jsonb,
    citations JSONB NOT NULL DEFAULT '[]'::jsonb,
    confidence TEXT NOT NULL DEFAULT 'low',
    reviewed_by TEXT,
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ai_drafts_draft_type_check
        CHECK (draft_type IN (
            'summary',
            'contradiction_candidate',
            'explanation',
            'source_digest',
            'evidence_digest'
        )),
    CONSTRAINT ai_drafts_status_check
        CHECK (status IN (
            'needs_review',
            'approved',
            'rejected',
            'archived'
        )),
    CONSTRAINT ai_drafts_confidence_check
        CHECK (confidence IN ('low', 'medium', 'high')),
    CONSTRAINT ai_drafts_input_context_object_check
        CHECK (jsonb_typeof(input_context) = 'object'),
    CONSTRAINT ai_drafts_citations_array_check
        CHECK (jsonb_typeof(citations) = 'array')
);

CREATE INDEX IF NOT EXISTS idx_ai_drafts_type
    ON ai_drafts (draft_type);

CREATE INDEX IF NOT EXISTS idx_ai_drafts_status
    ON ai_drafts (status);

CREATE INDEX IF NOT EXISTS idx_ai_drafts_country
    ON ai_drafts (country_slug)
    WHERE country_slug IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_ai_drafts_created_at
    ON ai_drafts (created_at DESC);

CREATE TABLE IF NOT EXISTS contradiction_candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_slug TEXT,
    topic TEXT NOT NULL,
    entity_type TEXT,
    entity_id UUID,
    severity TEXT NOT NULL DEFAULT 'medium',
    status TEXT NOT NULL DEFAULT 'needs_review',
    summary TEXT NOT NULL,
    claim_a TEXT NOT NULL,
    claim_b TEXT NOT NULL,
    source_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    evidence_item_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    detected_by TEXT NOT NULL DEFAULT 'fake_ai',
    provider TEXT NOT NULL DEFAULT 'fake',
    model_name TEXT NOT NULL DEFAULT 'fake-grounded-v1',
    model_version TEXT NOT NULL DEFAULT 'v1',
    confidence TEXT NOT NULL DEFAULT 'low',
    reviewed_at TIMESTAMPTZ,
    reviewed_by TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT contradiction_candidates_severity_check
        CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    CONSTRAINT contradiction_candidates_status_check
        CHECK (status IN (
            'needs_review',
            'confirmed',
            'dismissed',
            'archived'
        )),
    CONSTRAINT contradiction_candidates_confidence_check
        CHECK (confidence IN ('low', 'medium', 'high')),
    CONSTRAINT contradiction_candidates_source_ids_array_check
        CHECK (jsonb_typeof(source_ids) = 'array'),
    CONSTRAINT contradiction_candidates_evidence_item_ids_array_check
        CHECK (jsonb_typeof(evidence_item_ids) = 'array')
);

CREATE INDEX IF NOT EXISTS idx_contradiction_candidates_country
    ON contradiction_candidates (country_slug)
    WHERE country_slug IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_contradiction_candidates_status
    ON contradiction_candidates (status);

CREATE INDEX IF NOT EXISTS idx_contradiction_candidates_severity
    ON contradiction_candidates (severity);

CREATE INDEX IF NOT EXISTS idx_contradiction_candidates_created_at
    ON contradiction_candidates (created_at DESC);

ALTER TABLE domain_events
    DROP CONSTRAINT IF EXISTS domain_events_event_type_check;

ALTER TABLE domain_events
    ADD CONSTRAINT domain_events_event_type_check CHECK (
        event_type IN (
            'legal_signal.published',
            'legal_signal_event.published',
            'route.published',
            'user_story.published',
            'ai_draft.ready',
            'contradiction_candidate.created',
            'community_question.submitted',
            'community_answer.submitted',
            'data_error_report.submitted'
        )
    );

CREATE TABLE IF NOT EXISTS qna_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_slug TEXT,
    route_id UUID,
    legal_signal_id UUID,
    topic TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_by_identity_type TEXT NOT NULL,
    created_by_identity_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    moderated_at TIMESTAMPTZ,
    moderated_by TEXT,
    CONSTRAINT qna_questions_status_check
        CHECK (status IN ('pending', 'review', 'published', 'rejected', 'archived')),
    CONSTRAINT qna_questions_identity_type_check
        CHECK (created_by_identity_type IN ('telegram', 'anonymous_session', 'system'))
);

CREATE TABLE IF NOT EXISTS qna_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL REFERENCES qna_questions(id) ON DELETE CASCADE,
    body TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    source_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    evidence_item_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_by_identity_type TEXT NOT NULL,
    created_by_identity_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    moderated_at TIMESTAMPTZ,
    moderated_by TEXT,
    CONSTRAINT qna_answers_status_check
        CHECK (status IN ('pending', 'review', 'published', 'rejected', 'archived')),
    CONSTRAINT qna_answers_identity_type_check
        CHECK (created_by_identity_type IN ('telegram', 'anonymous_session', 'system')),
    CONSTRAINT qna_answers_source_ids_array_check
        CHECK (jsonb_typeof(source_ids) = 'array'),
    CONSTRAINT qna_answers_evidence_item_ids_array_check
        CHECK (jsonb_typeof(evidence_item_ids) = 'array')
);

CREATE TABLE IF NOT EXISTS qna_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    answer_id UUID NOT NULL REFERENCES qna_answers(id) ON DELETE CASCADE,
    vote_type TEXT NOT NULL,
    identity_type TEXT NOT NULL,
    identity_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT qna_votes_vote_type_check
        CHECK (vote_type IN ('up', 'down', 'helpful', 'outdated')),
    CONSTRAINT qna_votes_identity_type_check
        CHECK (identity_type IN ('telegram', 'anonymous_session', 'system')),
    CONSTRAINT qna_votes_unique_identity_vote
        UNIQUE (answer_id, vote_type, identity_type, identity_id)
);

CREATE INDEX IF NOT EXISTS idx_qna_questions_country
    ON qna_questions (country_slug)
    WHERE country_slug IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_qna_questions_status
    ON qna_questions (status);

CREATE INDEX IF NOT EXISTS idx_qna_questions_created_at
    ON qna_questions (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_qna_answers_question
    ON qna_answers (question_id);

CREATE INDEX IF NOT EXISTS idx_qna_answers_status
    ON qna_answers (status);

CREATE INDEX IF NOT EXISTS idx_qna_votes_answer
    ON qna_votes (answer_id);

CREATE TABLE IF NOT EXISTS data_error_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL,
    entity_id UUID,
    country_slug TEXT,
    route_id UUID,
    report_type TEXT NOT NULL,
    message TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_by_identity_type TEXT NOT NULL,
    created_by_identity_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ,
    reviewed_by TEXT,
    resolution_note TEXT,
    CONSTRAINT data_error_reports_type_check
        CHECK (report_type IN (
            'outdated',
            'wrong',
            'missing_source',
            'contradiction',
            'translation_issue',
            'other'
        )),
    CONSTRAINT data_error_reports_status_check
        CHECK (status IN ('pending', 'review', 'resolved', 'rejected', 'archived')),
    CONSTRAINT data_error_reports_identity_type_check
        CHECK (created_by_identity_type IN ('telegram', 'anonymous_session', 'system'))
);

CREATE INDEX IF NOT EXISTS idx_data_error_reports_status
    ON data_error_reports (status);

CREATE INDEX IF NOT EXISTS idx_data_error_reports_country
    ON data_error_reports (country_slug)
    WHERE country_slug IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_data_error_reports_entity
    ON data_error_reports (entity_type, entity_id);

CREATE INDEX IF NOT EXISTS idx_data_error_reports_created_at
    ON data_error_reports (created_at DESC);

CREATE TABLE IF NOT EXISTS user_story_ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_story_id UUID,
    country_slug TEXT,
    route_id UUID,
    official_expectation_score INTEGER,
    real_experience_score INTEGER,
    bureaucracy_score INTEGER,
    cost_surprise_score INTEGER,
    banking_difficulty_score INTEGER,
    safety_feeling_score INTEGER,
    comment TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_by_identity_type TEXT,
    created_by_identity_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ,
    reviewed_by TEXT,
    CONSTRAINT user_story_ratings_status_check
        CHECK (status IN ('pending', 'review', 'published', 'rejected', 'archived')),
    CONSTRAINT user_story_ratings_score_range_check
        CHECK (
            (official_expectation_score IS NULL OR official_expectation_score BETWEEN 0 AND 100)
            AND (real_experience_score IS NULL OR real_experience_score BETWEEN 0 AND 100)
            AND (bureaucracy_score IS NULL OR bureaucracy_score BETWEEN 0 AND 100)
            AND (cost_surprise_score IS NULL OR cost_surprise_score BETWEEN 0 AND 100)
            AND (banking_difficulty_score IS NULL OR banking_difficulty_score BETWEEN 0 AND 100)
            AND (safety_feeling_score IS NULL OR safety_feeling_score BETWEEN 0 AND 100)
        ),
    CONSTRAINT user_story_ratings_identity_type_check
        CHECK (
            created_by_identity_type IS NULL
            OR created_by_identity_type IN ('telegram', 'anonymous_session', 'system')
        )
);

CREATE INDEX IF NOT EXISTS idx_user_story_ratings_status
    ON user_story_ratings (status);

CREATE INDEX IF NOT EXISTS idx_user_story_ratings_country
    ON user_story_ratings (country_slug)
    WHERE country_slug IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_user_story_ratings_route
    ON user_story_ratings (route_id)
    WHERE route_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_user_story_ratings_created_at
    ON user_story_ratings (created_at DESC);

INSERT INTO feature_flags (
    key,
    name,
    description,
    status,
    access_tier,
    default_enabled,
    metadata
)
VALUES
    (
        'community_enabled',
        'Community intelligence',
        'Master switch for structured community Q&A, error reports, and story ratings.',
        'enabled',
        'public',
        TRUE,
        '{"episode":"ai-drafts-community-foundation-v1"}'::jsonb
    ),
    (
        'community_qna_enabled',
        'Community Q&A',
        'Structured community questions, answers, and votes.',
        'enabled',
        'public',
        TRUE,
        '{"episode":"ai-drafts-community-foundation-v1"}'::jsonb
    ),
    (
        'community_error_reports_enabled',
        'Community data error reports',
        'Users can report suspected data errors for editorial review.',
        'enabled',
        'public',
        TRUE,
        '{"episode":"ai-drafts-community-foundation-v1"}'::jsonb
    ),
    (
        'community_story_ratings_enabled',
        'Community story ratings',
        'Structured user story rating inputs for the future Expat Reality Gap.',
        'enabled',
        'public',
        TRUE,
        '{"episode":"ai-drafts-community-foundation-v1"}'::jsonb
    )
ON CONFLICT (key) DO UPDATE
SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    status = EXCLUDED.status,
    access_tier = EXCLUDED.access_tier,
    default_enabled = EXCLUDED.default_enabled,
    metadata = EXCLUDED.metadata,
    updated_at = NOW();

INSERT INTO feature_access_rules (
    feature_key,
    access_tier,
    is_enabled
)
VALUES
    ('community_enabled', 'public', TRUE),
    ('community_qna_enabled', 'public', TRUE),
    ('community_error_reports_enabled', 'public', TRUE),
    ('community_story_ratings_enabled', 'public', TRUE)
ON CONFLICT (feature_key, access_tier)
DO UPDATE SET
    is_enabled = EXCLUDED.is_enabled;
