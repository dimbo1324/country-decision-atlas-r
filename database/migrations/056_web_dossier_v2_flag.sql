-- Migration 056: Seeds the web_dossier_v2 feature flag (frontend redesign
-- Stage 1.1 -- tabbed country dossier layout, disabled by default).
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
        'web_dossier_v2',
        'Tabbed country dossier',
        'Groups the country dossier''s sections into tabs (Обзор, Оценки, Доверие, Сигналы, Сообщество) instead of one long vertical stack.',
        'disabled',
        'internal',
        FALSE
    )
ON CONFLICT (key) DO NOTHING;

INSERT INTO feature_access_rules (
    feature_key,
    access_tier,
    is_enabled
)
SELECT
    key,
    access_tier,
    default_enabled
FROM feature_flags
WHERE key = 'web_dossier_v2'
ON CONFLICT (feature_key, access_tier) DO NOTHING;
