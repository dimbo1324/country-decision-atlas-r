-- Migration 037: Closeout pass for decision personalization: additional feature access rules.
UPDATE feature_flags
SET
    status = 'enabled',
    access_tier = 'public',
    default_enabled = TRUE,
    updated_at = NOW()
WHERE key = 'decision_wizard_enabled';

INSERT INTO feature_access_rules (
    feature_key,
    access_tier,
    is_enabled
)
VALUES
    (
        'decision_wizard_enabled',
        'public',
        TRUE
    )
ON CONFLICT (feature_key, access_tier)
DO UPDATE SET
    is_enabled = EXCLUDED.is_enabled;
