-- Migration 011: Content localization foundation: reworks the locales table (direction, active/default flags) and seeds locale rows.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

ALTER TABLE locales
ADD COLUMN IF NOT EXISTS is_default BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS fallback_locale_code TEXT,
ADD COLUMN IF NOT EXISTS direction TEXT NOT NULL DEFAULT 'ltr';

ALTER TABLE locales DROP CONSTRAINT IF EXISTS locales_code_format;

ALTER TABLE locales DROP CONSTRAINT IF EXISTS locales_direction_check;

ALTER TABLE locales
ADD CONSTRAINT locales_code_format CHECK (
    code ~ '^[a-z]{2,3}(-[A-Za-z0-9]{2,8})*$'
),
ADD CONSTRAINT locales_direction_check CHECK (direction IN ('ltr', 'rtl'));

INSERT INTO locales (code, name, native_name, is_active, is_default, direction)
VALUES
    ('ru', 'Russian', 'Русский', TRUE, TRUE, 'ltr'),
    ('en', 'English', 'English', TRUE, FALSE, 'ltr')
ON CONFLICT (code) DO UPDATE
SET
    is_active = EXCLUDED.is_active,
    direction = EXCLUDED.direction,
    updated_at = NOW();

UPDATE locales
SET
    is_default = code = 'ru',
    fallback_locale_code = CASE WHEN code = 'en' THEN 'ru' END,
    updated_at = NOW()
WHERE code IN ('ru', 'en') OR is_default = TRUE;

CREATE UNIQUE INDEX IF NOT EXISTS idx_locales_single_default
ON locales(is_default)
WHERE is_default = TRUE;

CREATE TABLE IF NOT EXISTS translation_units (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    field_name TEXT NOT NULL,
    original_locale_code TEXT NOT NULL REFERENCES locales(code),
    source_hash TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT translation_units_unique_field UNIQUE (
        entity_type,
        entity_id,
        field_name
    )
);

CREATE TABLE IF NOT EXISTS translation_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    translation_unit_id UUID NOT NULL REFERENCES translation_units(id) ON DELETE CASCADE,
    locale_code TEXT NOT NULL REFERENCES locales(code),
    text TEXT NOT NULL,
    status TEXT NOT NULL,
    method TEXT NOT NULL DEFAULT 'human',
    provider TEXT,
    provider_model TEXT,
    source_locale_code TEXT REFERENCES locales(code),
    source_hash TEXT NOT NULL,
    is_original BOOLEAN NOT NULL DEFAULT FALSE,
    reviewed_by TEXT,
    reviewed_at TIMESTAMPTZ,
    quality_score NUMERIC(5, 2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT translation_variants_unique_locale UNIQUE (
        translation_unit_id,
        locale_code
    ),
    CONSTRAINT translation_variants_status_check CHECK (
        status IN (
            'original',
            'human_authored',
            'machine_translated',
            'human_reviewed',
            'needs_review',
            'stale',
            'fallback',
            'missing'
        )
    ),
    CONSTRAINT translation_variants_method_check CHECK (
        method IN ('human', 'machine', 'imported', 'legacy', 'system')
    ),
    CONSTRAINT translation_variants_quality_score_check CHECK (
        quality_score IS NULL
        OR (quality_score >= 0 AND quality_score <= 100)
    )
);

ALTER TABLE translation_jobs
ADD COLUMN IF NOT EXISTS translation_unit_id UUID REFERENCES translation_units(id) ON DELETE CASCADE,
ADD COLUMN IF NOT EXISTS source_locale_code TEXT REFERENCES locales(code),
ADD COLUMN IF NOT EXISTS target_locale_code TEXT REFERENCES locales(code),
ADD COLUMN IF NOT EXISTS priority INTEGER NOT NULL DEFAULT 100,
ADD COLUMN IF NOT EXISTS attempts INTEGER NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS started_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS completed_at TIMESTAMPTZ;

ALTER TABLE translation_jobs DROP CONSTRAINT IF EXISTS translation_jobs_status_check;

ALTER TABLE translation_jobs
ADD CONSTRAINT translation_jobs_status_check CHECK (
    status IN (
        'queued',
        'running',
        'pending',
        'processing',
        'completed',
        'failed',
        'cancelled'
    )
);

CREATE INDEX IF NOT EXISTS idx_translation_units_entity
ON translation_units(entity_type, entity_id);

CREATE INDEX IF NOT EXISTS idx_translation_units_field
ON translation_units(entity_type, entity_id, field_name);

CREATE INDEX IF NOT EXISTS idx_translation_variants_unit_locale
ON translation_variants(translation_unit_id, locale_code);

CREATE INDEX IF NOT EXISTS idx_translation_variants_status
ON translation_variants(status);

CREATE UNIQUE INDEX IF NOT EXISTS idx_translation_variants_single_original
ON translation_variants(translation_unit_id)
WHERE is_original = TRUE;

CREATE INDEX IF NOT EXISTS idx_translation_jobs_unit_status
ON translation_jobs(translation_unit_id, status);

DROP TRIGGER IF EXISTS trg_translation_units_updated_at ON translation_units;

CREATE TRIGGER trg_translation_units_updated_at
BEFORE UPDATE ON translation_units
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_translation_variants_updated_at ON translation_variants;

CREATE TRIGGER trg_translation_variants_updated_at
BEFORE UPDATE ON translation_variants
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TEMPORARY TABLE localization_backfill_stage (
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    field_name TEXT NOT NULL,
    ru_text TEXT NOT NULL,
    en_text TEXT,
    PRIMARY KEY (entity_type, entity_id, field_name)
) ON COMMIT DROP;

INSERT INTO localization_backfill_stage (
    entity_type,
    entity_id,
    field_name,
    ru_text,
    en_text
)
SELECT
    'country_card',
    ru_card.id,
    field_data.field_name,
    field_data.ru_text,
    field_data.en_text
FROM country_cards AS ru_card
LEFT JOIN country_cards AS en_card
    ON en_card.country_id = ru_card.country_id
    AND en_card.locale = 'en'
CROSS JOIN LATERAL (
    VALUES
        ('executive_summary', ru_card.executive_summary, en_card.executive_summary),
        ('migration_overview', ru_card.migration_overview, en_card.migration_overview),
        ('tax_overview', ru_card.tax_overview, en_card.tax_overview),
        (
            'cost_of_living_overview',
            ru_card.cost_of_living_overview,
            en_card.cost_of_living_overview
        ),
        ('business_overview', ru_card.business_overview, en_card.business_overview),
        ('safety_overview', ru_card.safety_overview, en_card.safety_overview),
        (
            'legal_signals_summary',
            ru_card.legal_signals_summary,
            en_card.legal_signals_summary
        ),
        ('risk_summary', ru_card.risk_summary, en_card.risk_summary),
        ('source_summary', ru_card.source_summary, en_card.source_summary)
) AS field_data(field_name, ru_text, en_text)
WHERE ru_card.locale = 'ru'
    AND NULLIF(BTRIM(field_data.ru_text), '') IS NOT NULL;

INSERT INTO localization_backfill_stage (
    entity_type,
    entity_id,
    field_name,
    ru_text,
    en_text
)
SELECT
    'legal_signal',
    legal_signals.id,
    field_data.field_name,
    field_data.ru_text,
    field_data.en_text
FROM legal_signals
CROSS JOIN LATERAL (
    VALUES
        ('title', COALESCE(title_ru, title), title_en),
        ('summary', COALESCE(summary_ru, summary), summary_en)
) AS field_data(field_name, ru_text, en_text)
WHERE NULLIF(BTRIM(field_data.ru_text), '') IS NOT NULL;

INSERT INTO localization_backfill_stage (
    entity_type,
    entity_id,
    field_name,
    ru_text,
    en_text
)
SELECT
    'evidence_item',
    evidence_items.id,
    field_data.field_name,
    field_data.ru_text,
    NULL
FROM evidence_items
CROSS JOIN LATERAL (
    VALUES
        ('title', title),
        ('summary', summary),
        ('claim', claim),
        ('excerpt', excerpt),
        ('quote', quote)
) AS field_data(field_name, ru_text)
WHERE NULLIF(BTRIM(field_data.ru_text), '') IS NOT NULL;

INSERT INTO localization_backfill_stage (
    entity_type,
    entity_id,
    field_name,
    ru_text,
    en_text
)
SELECT
    'source',
    sources.id,
    field_data.field_name,
    field_data.ru_text,
    NULL
FROM sources
CROSS JOIN LATERAL (
    VALUES
        ('title', title),
        ('notes', notes)
) AS field_data(field_name, ru_text)
WHERE NULLIF(BTRIM(field_data.ru_text), '') IS NOT NULL;

INSERT INTO localization_backfill_stage (
    entity_type,
    entity_id,
    field_name,
    ru_text,
    en_text
)
SELECT
    'scenario',
    scenarios.id,
    field_data.field_name,
    field_data.ru_text,
    field_data.en_text
FROM scenarios
CROSS JOIN LATERAL (
    VALUES
        ('title', COALESCE(title_ru, name), title_en),
        ('description', COALESCE(description_ru, description), description_en)
) AS field_data(field_name, ru_text, en_text)
WHERE NULLIF(BTRIM(field_data.ru_text), '') IS NOT NULL;

INSERT INTO localization_backfill_stage (
    entity_type,
    entity_id,
    field_name,
    ru_text,
    en_text
)
SELECT
    'country_score',
    country_scores.id,
    field_data.field_name,
    field_data.ru_text,
    field_data.en_text
FROM country_scores
CROSS JOIN LATERAL (
    VALUES
        ('summary', summary, NULL),
        ('explanation', explanation_ru, explanation_en)
) AS field_data(field_name, ru_text, en_text)
WHERE NULLIF(BTRIM(field_data.ru_text), '') IS NOT NULL;

INSERT INTO localization_backfill_stage (
    entity_type,
    entity_id,
    field_name,
    ru_text,
    en_text
)
SELECT
    'country_score_breakdown',
    breakdown.id,
    'explanation',
    breakdown.explanation_ru,
    breakdown.explanation_en
FROM country_score_breakdowns AS breakdown
WHERE NULLIF(BTRIM(breakdown.explanation_ru), '') IS NOT NULL;

INSERT INTO localization_backfill_stage (
    entity_type,
    entity_id,
    field_name,
    ru_text,
    en_text
)
SELECT
    'user_story',
    user_stories.id,
    field_data.field_name,
    field_data.ru_text,
    NULL
FROM user_stories
CROSS JOIN LATERAL (
    VALUES
        ('legal_path', legal_path),
        ('problems', problems),
        ('positive_outcome', positive_outcome),
        ('negative_outcome', negative_outcome),
        ('advice', advice),
        ('notes', notes)
) AS field_data(field_name, ru_text)
WHERE NULLIF(BTRIM(field_data.ru_text), '') IS NOT NULL;

INSERT INTO translation_units (
    entity_type,
    entity_id,
    field_name,
    original_locale_code,
    source_hash
)
SELECT
    entity_type,
    entity_id,
    field_name,
    'ru',
    ENCODE(DIGEST(ru_text, 'sha256'), 'hex')
FROM localization_backfill_stage
ON CONFLICT (entity_type, entity_id, field_name) DO UPDATE
SET
    original_locale_code = EXCLUDED.original_locale_code,
    source_hash = EXCLUDED.source_hash,
    is_active = TRUE,
    updated_at = NOW();

INSERT INTO translation_variants (
    translation_unit_id,
    locale_code,
    text,
    status,
    method,
    source_locale_code,
    source_hash,
    is_original
)
SELECT
    translation_units.id,
    'ru',
    localization_backfill_stage.ru_text,
    'original',
    'legacy',
    'ru',
    translation_units.source_hash,
    TRUE
FROM localization_backfill_stage
JOIN translation_units
    ON translation_units.entity_type = localization_backfill_stage.entity_type
    AND translation_units.entity_id = localization_backfill_stage.entity_id
    AND translation_units.field_name = localization_backfill_stage.field_name
ON CONFLICT (translation_unit_id, locale_code) DO UPDATE
SET
    text = EXCLUDED.text,
    status = EXCLUDED.status,
    method = EXCLUDED.method,
    source_locale_code = EXCLUDED.source_locale_code,
    source_hash = EXCLUDED.source_hash,
    is_original = EXCLUDED.is_original,
    updated_at = NOW();

INSERT INTO translation_variants (
    translation_unit_id,
    locale_code,
    text,
    status,
    method,
    source_locale_code,
    source_hash,
    is_original
)
SELECT
    translation_units.id,
    'en',
    localization_backfill_stage.en_text,
    'needs_review',
    'legacy',
    'ru',
    translation_units.source_hash,
    FALSE
FROM localization_backfill_stage
JOIN translation_units
    ON translation_units.entity_type = localization_backfill_stage.entity_type
    AND translation_units.entity_id = localization_backfill_stage.entity_id
    AND translation_units.field_name = localization_backfill_stage.field_name
WHERE NULLIF(BTRIM(localization_backfill_stage.en_text), '') IS NOT NULL
ON CONFLICT (translation_unit_id, locale_code) DO NOTHING;

CREATE OR REPLACE VIEW stale_translation_variants AS
SELECT
    variant.id,
    variant.translation_unit_id,
    variant.locale_code,
    variant.text,
    variant.status,
    variant.method,
    variant.provider,
    variant.provider_model,
    variant.source_locale_code,
    variant.source_hash,
    variant.is_original,
    variant.reviewed_by,
    variant.reviewed_at,
    variant.quality_score,
    variant.created_at,
    variant.updated_at
FROM translation_variants AS variant
JOIN translation_units AS unit
    ON unit.id = variant.translation_unit_id
WHERE variant.is_original = FALSE
    AND variant.source_hash <> unit.source_hash;
