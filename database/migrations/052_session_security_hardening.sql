-- Migration 052: Session security hardening adds token rotation, device visibility, and
-- new-device login notifications to auth_sessions (Audit episode 3, variant B + hardening).
ALTER TABLE auth_sessions
ADD COLUMN IF NOT EXISTS previous_token_hash TEXT,
ADD COLUMN IF NOT EXISTS previous_token_expires_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS rotated_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS device_label TEXT,
ADD COLUMN IF NOT EXISTS ip_display TEXT,
ADD COLUMN IF NOT EXISTS device_fingerprint_hash TEXT;

CREATE INDEX IF NOT EXISTS idx_auth_sessions_previous_token_hash
    ON auth_sessions (previous_token_hash)
    WHERE previous_token_hash IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_auth_sessions_user_fingerprint
    ON auth_sessions (user_id, device_fingerprint_hash);

CREATE TABLE IF NOT EXISTS user_security_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID REFERENCES auth_sessions(id) ON DELETE SET NULL,
    event_type TEXT NOT NULL,
    device_label TEXT,
    ip_display TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    CONSTRAINT user_security_notifications_event_type_check
        CHECK (event_type IN ('new_device_login'))
);

CREATE INDEX IF NOT EXISTS idx_user_security_notifications_unacked
    ON user_security_notifications (user_id)
    WHERE acknowledged_at IS NULL;

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
            'revoked',
            'new_device_login'
        )
    );
