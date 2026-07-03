-- Migration 033: Adds a feature flag and access rules gating the self-computed intelligence feature.
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
        'self_computed_intelligence',
        'Self-computed intelligence',
        'Self-computed intelligence metrics: Legal Velocity Index, Scenario-Specific Risk Score, and Contradiction Score.',
        'enabled',
        'public',
        TRUE
    )
ON CONFLICT (key) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    status = EXCLUDED.status,
    access_tier = EXCLUDED.access_tier,
    default_enabled = EXCLUDED.default_enabled,
    updated_at = NOW();

INSERT INTO feature_access_rules (
    feature_key,
    access_tier,
    is_enabled
)
VALUES
    (
        'self_computed_intelligence',
        'public',
        TRUE
    )
ON CONFLICT (feature_key, access_tier) DO UPDATE SET
    is_enabled = EXCLUDED.is_enabled;
