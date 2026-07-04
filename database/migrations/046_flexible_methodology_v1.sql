-- Migration 046: Flexible methodology v1 stores interpretation thresholds, product limits, and saved user weight profiles.
CREATE TABLE IF NOT EXISTS methodology_parameters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version TEXT NOT NULL DEFAULT 'v1.0',
    param_key TEXT NOT NULL,
    value_numeric NUMERIC,
    value_json JSONB,
    description TEXT NOT NULL,
    effective_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT methodology_parameters_version_check
        CHECK (BTRIM(version) <> ''),
    CONSTRAINT methodology_parameters_param_key_check
        CHECK (BTRIM(param_key) <> ''),
    CONSTRAINT methodology_parameters_description_check
        CHECK (BTRIM(description) <> ''),
    CONSTRAINT methodology_parameters_single_value_check
        CHECK (
            (value_numeric IS NOT NULL AND value_json IS NULL)
            OR (value_numeric IS NULL AND value_json IS NOT NULL)
        ),
    CONSTRAINT uq_methodology_param UNIQUE (version, param_key)
);

CREATE INDEX IF NOT EXISTS idx_methodology_parameters_active
    ON methodology_parameters (effective_from DESC, version, param_key);

CREATE TABLE IF NOT EXISTS user_weight_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    scenario_slug TEXT,
    weights JSONB NOT NULL,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT user_weight_profiles_name_check
        CHECK (BTRIM(name) <> '' AND char_length(name) <= 120),
    CONSTRAINT user_weight_profiles_scenario_slug_check
        CHECK (scenario_slug IS NULL OR BTRIM(scenario_slug) <> ''),
    CONSTRAINT user_weight_profiles_weights_object_check
        CHECK (jsonb_typeof(weights) = 'object'),
    CONSTRAINT uq_profile_name UNIQUE (user_id, name)
);

CREATE INDEX IF NOT EXISTS idx_user_weight_profiles_user
    ON user_weight_profiles (user_id, created_at DESC);

CREATE UNIQUE INDEX IF NOT EXISTS uq_user_weight_profiles_default_scope
    ON user_weight_profiles (user_id, COALESCE(scenario_slug, ''))
    WHERE is_default IS TRUE;

INSERT INTO methodology_parameters (
    version,
    param_key,
    value_numeric,
    description
)
VALUES
    (
        'v1.0',
        'score_label.weak_below',
        30,
        'Scores below this value are labelled weak.'
    ),
    (
        'v1.0',
        'score_label.limited_below',
        50,
        'Scores below this value and at least score_label.weak_below are labelled limited.'
    ),
    (
        'v1.0',
        'score_label.moderate_below',
        70,
        'Scores below this value and at least score_label.limited_below are labelled moderate.'
    ),
    (
        'v1.0',
        'score_label.strong_below',
        85,
        'Scores below this value and at least score_label.moderate_below are labelled strong.'
    ),
    (
        'v1.0',
        'strength.min_score',
        70,
        'Minimum criterion score shown as a country strength in decision output.'
    ),
    (
        'v1.0',
        'weakness.max_score',
        50,
        'Maximum criterion score shown as a country weakness in decision output.'
    ),
    (
        'v1.0',
        'confidence.high_min_average',
        2.5,
        'Minimum averaged confidence bucket value that maps to high confidence.'
    ),
    (
        'v1.0',
        'confidence.medium_min_average',
        1.7,
        'Minimum averaged confidence bucket value that maps to medium confidence.'
    ),
    (
        'v1.0',
        'recommendation.tie_delta_below',
        3,
        'Country comparison score delta below this value is treated as a tie.'
    ),
    (
        'v1.0',
        'recommendation.medium_confidence_delta_below',
        10,
        'Winning comparison delta below this value is medium confidence instead of high.'
    ),
    (
        'v1.0',
        'board.max_active_posts',
        5,
        'Maximum active migration board posts per user.'
    ),
    (
        'v1.0',
        'board.max_contact_requests_per_day',
        20,
        'Maximum migration board contact requests a user can create per day.'
    ),
    (
        'v1.0',
        'board.max_reports_per_day',
        20,
        'Maximum migration board reports a user can create per day.'
    ),
    (
        'v1.0',
        'flows.k_anonymity',
        20,
        'Minimum group size for future anonymized human-flow aggregates.'
    )
ON CONFLICT (version, param_key) DO UPDATE
SET
    value_numeric = EXCLUDED.value_numeric,
    value_json = EXCLUDED.value_json,
    description = EXCLUDED.description,
    effective_from = EXCLUDED.effective_from;
