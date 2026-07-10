-- Migration 054: retention configuration (Аудит-эпизод 5, P1-4)

INSERT INTO methodology_parameters (
    version,
    param_key,
    value_numeric,
    value_json,
    description
)
VALUES
    (
        'v1.0',
        'retention.analytics_days',
        180,
        NULL,
        'Days to keep analytics_events and ai_interaction_logs rows before cleanup_retention.py deletes them.'
    ),
    (
        'v1.0',
        'retention.domain_events_days',
        30,
        NULL,
        'Days to keep relayed domain_events rows (already delivered) before cleanup_retention.py deletes them.'
    ),
    (
        'v1.0',
        'retention.sessions_days',
        30,
        NULL,
        'Days past expiry/revocation to keep auth_sessions rows before cleanup_retention.py deletes them.'
    )
ON CONFLICT (version, param_key) DO NOTHING;
