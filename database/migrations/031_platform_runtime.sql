-- Migration 031: Platform runtime foundations: seeds feature access rules for platform runtime features.
UPDATE feature_flags
SET
    status = 'enabled',
    access_tier = 'public',
    default_enabled = TRUE,
    updated_at = NOW()
WHERE key = 'data_journal_enabled';

INSERT INTO feature_access_rules (
    feature_key,
    access_tier,
    is_enabled
)
VALUES
    (
        'data_journal_enabled',
        'public',
        TRUE
    )
ON CONFLICT (feature_key, access_tier)
DO UPDATE SET
    is_enabled = EXCLUDED.is_enabled;
