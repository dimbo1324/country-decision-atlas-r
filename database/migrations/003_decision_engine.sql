-- Migration 003: Adds the decision engine's country_cards and country_score_breakdowns tables plus supporting country/scenario columns.
CREATE TABLE IF NOT EXISTS country_cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_id UUID NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
    locale TEXT NOT NULL DEFAULT 'en',
    executive_summary TEXT NOT NULL,
    migration_overview TEXT NOT NULL,
    tax_overview TEXT NOT NULL,
    cost_of_living_overview TEXT NOT NULL,
    business_overview TEXT NOT NULL,
    safety_overview TEXT NOT NULL,
    legal_signals_summary TEXT NOT NULL,
    risk_summary TEXT NOT NULL,
    source_summary TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT country_cards_locale_check CHECK (locale IN ('en', 'ru')),
    CONSTRAINT country_cards_status_check CHECK (
        status IN (
            'draft',
            'editor_reviewed',
            'expert_review_required',
            'published',
            'archived'
        )
    ),
    CONSTRAINT country_cards_unique_country_locale UNIQUE (country_id, locale)
);

ALTER TABLE
    scenarios
ADD
    COLUMN IF NOT EXISTS title_en TEXT,
ADD
    COLUMN IF NOT EXISTS title_ru TEXT,
ADD
    COLUMN IF NOT EXISTS description_en TEXT,
ADD
    COLUMN IF NOT EXISTS description_ru TEXT,
ADD
    COLUMN IF NOT EXISTS weights JSONB NOT NULL DEFAULT '{}' :: jsonb;

UPDATE
    scenarios
SET
    title_en = COALESCE(title_en, name),
    description_en = COALESCE(description_en, description),
    title_ru = COALESCE(title_ru, name),
    description_ru = COALESCE(description_ru, description)
WHERE
    title_en IS NULL
    OR description_en IS NULL
    OR title_ru IS NULL
    OR description_ru IS NULL;

ALTER TABLE
    country_scores
ADD
    COLUMN IF NOT EXISTS explanation_en TEXT,
ADD
    COLUMN IF NOT EXISTS explanation_ru TEXT,
ADD
    COLUMN IF NOT EXISTS confidence TEXT NOT NULL DEFAULT 'medium',
ADD
    COLUMN IF NOT EXISTS calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

ALTER TABLE
    country_scores DROP CONSTRAINT IF EXISTS country_scores_confidence_check;

ALTER TABLE
    country_scores
ADD
    CONSTRAINT country_scores_confidence_check CHECK (confidence IN ('high', 'medium', 'low'));

CREATE TABLE IF NOT EXISTS country_score_breakdowns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_score_id UUID NOT NULL REFERENCES country_scores(id) ON DELETE CASCADE,
    criterion TEXT NOT NULL,
    score NUMERIC(5, 2) NOT NULL,
    weight NUMERIC(5, 4) NOT NULL,
    weighted_score NUMERIC(7, 4) NOT NULL,
    explanation_en TEXT NOT NULL,
    explanation_ru TEXT NOT NULL,
    source_ids JSONB NOT NULL DEFAULT '[]' :: jsonb,
    confidence TEXT NOT NULL DEFAULT 'medium',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT country_score_breakdowns_score_check CHECK (
        score >= 0
        AND score <= 100
    ),
    CONSTRAINT country_score_breakdowns_weight_check CHECK (
        weight >= 0
        AND weight <= 1
    ),
    CONSTRAINT country_score_breakdowns_confidence_check CHECK (confidence IN ('high', 'medium', 'low')),
    CONSTRAINT country_score_breakdowns_criterion_check CHECK (
        criterion IN (
            'legalization_score',
            'long_term_status_score',
            'cost_of_living_score',
            'safety_score',
            'business_score',
            'legal_stability_score',
            'source_quality_score'
        )
    ),
    CONSTRAINT country_score_breakdowns_unique_criterion UNIQUE (country_score_id, criterion)
);

ALTER TABLE
    legal_signals
ADD
    COLUMN IF NOT EXISTS title_en TEXT,
ADD
    COLUMN IF NOT EXISTS title_ru TEXT,
ADD
    COLUMN IF NOT EXISTS summary_en TEXT,
ADD
    COLUMN IF NOT EXISTS summary_ru TEXT,
ADD
    COLUMN IF NOT EXISTS impact_direction TEXT NOT NULL DEFAULT 'neutral',
ADD
    COLUMN IF NOT EXISTS impact_level TEXT NOT NULL DEFAULT 'low',
ADD
    COLUMN IF NOT EXISTS affected_groups JSONB NOT NULL DEFAULT '[]' :: jsonb,
ADD
    COLUMN IF NOT EXISTS published_date DATE,
ADD
    COLUMN IF NOT EXISTS source_id UUID REFERENCES sources(id) ON DELETE
SET
    NULL,
ADD
    COLUMN IF NOT EXISTS confidence TEXT NOT NULL DEFAULT 'medium';

UPDATE
    legal_signals
SET
    title_en = COALESCE(title_en, title),
    title_ru = COALESCE(title_ru, title),
    summary_en = COALESCE(summary_en, summary),
    summary_ru = COALESCE(summary_ru, summary),
    published_date = COALESCE(published_date, published_at)
WHERE
    title_en IS NULL
    OR title_ru IS NULL
    OR summary_en IS NULL
    OR summary_ru IS NULL
    OR published_date IS NULL;

ALTER TABLE
    legal_signals DROP CONSTRAINT IF EXISTS legal_signals_signal_type_check,
    DROP CONSTRAINT IF EXISTS legal_signals_status_check,
    DROP CONSTRAINT IF EXISTS legal_signals_confidence_check,
    DROP CONSTRAINT IF EXISTS legal_signals_impact_direction_check,
    DROP CONSTRAINT IF EXISTS legal_signals_impact_level_check;

ALTER TABLE
    legal_signals
ADD
    CONSTRAINT legal_signals_signal_type_check CHECK (
        signal_type IN (
            'law',
            'bill',
            'policy',
            'court_decision',
            'administrative_change',
            'political_signal',
            'other',
            'migration',
            'residence',
            'citizenship',
            'tax',
            'business',
            'banking',
            'property',
            'safety',
            'freedom',
            'rule_of_law',
            'political_risk',
            'cost_of_living',
            'education',
            'healthcare'
        )
    ),
ADD
    CONSTRAINT legal_signals_status_check CHECK (
        status IN (
            'draft',
            'proposed',
            'adopted',
            'rejected',
            'active',
            'expired',
            'unknown',
            'editor_reviewed',
            'expert_review_required',
            'published',
            'archived'
        )
    ),
ADD
    CONSTRAINT legal_signals_confidence_check CHECK (confidence IN ('high', 'medium', 'low')),
ADD
    CONSTRAINT legal_signals_impact_direction_check CHECK (
        impact_direction IN (
            'positive',
            'negative',
            'neutral',
            'mixed',
            'uncertain'
        )
    ),
ADD
    CONSTRAINT legal_signals_impact_level_check CHECK (
        impact_level IN ('low', 'medium', 'high', 'critical')
    );

ALTER TABLE
    sources
ADD
    COLUMN IF NOT EXISTS language TEXT,
ADD
    COLUMN IF NOT EXISTS last_checked_at DATE,
ADD
    COLUMN IF NOT EXISTS confidence TEXT NOT NULL DEFAULT 'medium',
ADD
    COLUMN IF NOT EXISTS notes TEXT;

UPDATE
    sources
SET
    language = COALESCE(language, 'en'),
    last_checked_at = COALESCE(last_checked_at, accessed_at, CURRENT_DATE)
WHERE
    language IS NULL
    OR last_checked_at IS NULL;

ALTER TABLE
    sources DROP CONSTRAINT IF EXISTS sources_confidence_check,
    DROP CONSTRAINT IF EXISTS sources_source_type_check;

ALTER TABLE
    sources
ADD
    CONSTRAINT sources_confidence_check CHECK (confidence IN ('high', 'medium', 'low')),
ADD
    CONSTRAINT sources_source_type_check CHECK (
        source_type IN (
            'official',
            'expert',
            'media',
            'community',
            'dataset',
            'research'
        )
    );

ALTER TABLE
    evidence_items
ADD
    COLUMN IF NOT EXISTS legal_signal_id UUID REFERENCES legal_signals(id) ON DELETE
SET
    NULL,
ADD
    COLUMN IF NOT EXISTS claim TEXT,
ADD
    COLUMN IF NOT EXISTS excerpt TEXT,
ADD
    COLUMN IF NOT EXISTS retrieved_at DATE,
ADD
    COLUMN IF NOT EXISTS confidence TEXT NOT NULL DEFAULT 'medium';

UPDATE
    evidence_items
SET
    claim = COALESCE(claim, title),
    excerpt = COALESCE(excerpt, quote, summary),
    retrieved_at = COALESCE(retrieved_at, published_at, CURRENT_DATE)
WHERE
    claim IS NULL
    OR excerpt IS NULL
    OR retrieved_at IS NULL;

ALTER TABLE
    evidence_items DROP CONSTRAINT IF EXISTS evidence_items_confidence_check;

ALTER TABLE
    evidence_items
ADD
    CONSTRAINT evidence_items_confidence_check CHECK (confidence IN ('high', 'medium', 'low'));

CREATE TABLE IF NOT EXISTS user_stories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    origin_country_id UUID REFERENCES countries(id) ON DELETE
    SET
        NULL,
        destination_country_id UUID NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
        city TEXT,
        year INTEGER,
        scenario TEXT NOT NULL,
        budget_initial_usd NUMERIC(12, 2),
        budget_monthly_usd NUMERIC(12, 2),
        legal_path TEXT,
        documents_used JSONB NOT NULL DEFAULT '[]' :: jsonb,
        problems TEXT,
        positive_outcome TEXT,
        negative_outcome TEXT,
        advice TEXT,
        satisfaction_score NUMERIC(4, 2),
        verification_status TEXT NOT NULL DEFAULT 'synthetic',
        status TEXT NOT NULL DEFAULT 'draft',
        is_synthetic BOOLEAN NOT NULL DEFAULT TRUE,
        notes TEXT NOT NULL DEFAULT 'Synthetic example for MVP demonstration only.',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        CONSTRAINT user_stories_year_check CHECK (
            year IS NULL
            OR (
                year >= 1990
                AND year <= 2100
            )
        ),
        CONSTRAINT user_stories_satisfaction_check CHECK (
            satisfaction_score IS NULL
            OR (
                satisfaction_score >= 0
                AND satisfaction_score <= 10
            )
        ),
        CONSTRAINT user_stories_status_check CHECK (
            status IN (
                'draft',
                'editor_reviewed',
                'expert_review_required',
                'published',
                'archived'
            )
        ),
        CONSTRAINT user_stories_verification_check CHECK (
            verification_status IN (
                'synthetic',
                'unverified',
                'editor_reviewed',
                'expert_reviewed'
            )
        )
);

CREATE TABLE IF NOT EXISTS user_story_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_story_id UUID NOT NULL REFERENCES user_stories(id) ON DELETE CASCADE,
    document_type TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT,
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_country_cards_country_locale ON country_cards(country_id, locale);

CREATE INDEX IF NOT EXISTS idx_country_score_breakdowns_score_id ON country_score_breakdowns(country_score_id);

CREATE INDEX IF NOT EXISTS idx_legal_signals_source_id ON legal_signals(source_id);

CREATE INDEX IF NOT EXISTS idx_legal_signals_signal_type ON legal_signals(signal_type);

CREATE INDEX IF NOT EXISTS idx_sources_country_language ON sources(country_id, language);

CREATE INDEX IF NOT EXISTS idx_evidence_items_legal_signal_id ON evidence_items(legal_signal_id);

CREATE INDEX IF NOT EXISTS idx_user_stories_destination_country_id ON user_stories(destination_country_id);

CREATE INDEX IF NOT EXISTS idx_user_stories_scenario ON user_stories(scenario);

CREATE INDEX IF NOT EXISTS idx_user_story_documents_story_id ON user_story_documents(user_story_id);

DO $$
DECLARE
    target_table TEXT;
BEGIN
    FOREACH target_table IN ARRAY ARRAY[
        'country_cards',
        'country_score_breakdowns',
        'user_stories',
        'user_story_documents'
    ] LOOP
        EXECUTE format(
            'DROP TRIGGER IF EXISTS trg_%I_updated_at ON %I',
            target_table,
            target_table
        );

        EXECUTE format(
            'CREATE TRIGGER trg_%I_updated_at BEFORE UPDATE ON %I
             FOR EACH ROW EXECUTE FUNCTION set_updated_at()',
            target_table,
            target_table
        );
    END LOOP;
END;
$$;
