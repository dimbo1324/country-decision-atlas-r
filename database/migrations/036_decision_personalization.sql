-- Migration 036: Decision personalization v1: adds a feature flag and access rules for persona-adjusted decision scoring.
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
        'decision_personalization_enabled',
        'Decision personalization',
        'Enables runtime custom decision weights without changing base scoring.',
        'enabled',
        'public',
        TRUE,
        '{"episode":"decision-personalization-v1"}'::jsonb
    ),
    (
        'decision_wizard_enabled',
        'Decision wizard',
        'Enables guided decision setup flow.',
        'disabled',
        'public',
        FALSE,
        '{"episode":"decision-personalization-v1"}'::jsonb
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
    (
        'decision_personalization_enabled',
        'public',
        TRUE
    ),
    (
        'decision_wizard_enabled',
        'public',
        FALSE
    )
ON CONFLICT (feature_key, access_tier)
DO UPDATE SET
    is_enabled = EXCLUDED.is_enabled;
