-- Migration 048: Rights and capabilities v2 introduces per-user capability grants, widens the
-- audit_events action vocabulary to cover moderation actions already emitted by migration board,
-- and seeds the auto-hide report threshold used by the new moderation safety net.
CREATE TABLE IF NOT EXISTS user_capabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    capability TEXT NOT NULL,
    granted_by UUID NOT NULL REFERENCES users(id),
    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked_at TIMESTAMPTZ,
    note TEXT,
    CONSTRAINT user_capabilities_capability_check
        CHECK (BTRIM(capability) <> ''),
    CONSTRAINT uq_user_capability UNIQUE (user_id, capability)
);

CREATE INDEX IF NOT EXISTS idx_user_capabilities_active_by_user
    ON user_capabilities (user_id)
    WHERE revoked_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_user_capabilities_active_by_capability
    ON user_capabilities (capability)
    WHERE revoked_at IS NULL;

ALTER TABLE audit_events
    DROP CONSTRAINT IF EXISTS audit_events_action_check;

ALTER TABLE audit_events
    ADD CONSTRAINT audit_events_action_check
    CHECK (
        action IN (
            'created',
            'updated',
            'submitted_for_review',
            'published',
            'archived',
            'rejected',
            'hidden',
            'report_created',
            'report_resolved',
            'report_dismissed',
            'granted',
            'revoked'
        )
    );

INSERT INTO methodology_parameters (
    version,
    param_key,
    value_numeric,
    description
)
VALUES
    (
        'v1.0',
        'board.auto_hide_report_threshold',
        3,
        'Number of resolved (confirmed) reports against a migration board post that triggers automatic hiding for post-review.'
    )
ON CONFLICT (version, param_key) DO UPDATE
SET
    value_numeric = EXCLUDED.value_numeric,
    description = EXCLUDED.description;
