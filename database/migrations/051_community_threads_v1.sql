-- Migration 051: Community threads v1: contact-gated 1:1 messaging between mutually
-- consented migration board members, polling delivery, moderator access only via a filed report.
CREATE TABLE IF NOT EXISTS contact_threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_request_id UUID NOT NULL UNIQUE
        REFERENCES migration_board_contact_requests(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'open',
    closed_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    closed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT contact_threads_status_check
        CHECK (status IN ('open', 'closed', 'frozen')),
    CONSTRAINT contact_threads_closed_state_check CHECK (
        (status = 'closed' AND closed_by_user_id IS NOT NULL AND closed_at IS NOT NULL)
        OR (status <> 'closed')
    )
);

CREATE INDEX IF NOT EXISTS idx_contact_threads_status
    ON contact_threads (status);

CREATE TABLE IF NOT EXISTS thread_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id UUID NOT NULL REFERENCES contact_threads(id) ON DELETE CASCADE,
    sender_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    body TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT thread_messages_body_check CHECK (BTRIM(body) <> '')
);

CREATE INDEX IF NOT EXISTS idx_thread_messages_thread_created
    ON thread_messages (thread_id, created_at, id);

CREATE INDEX IF NOT EXISTS idx_thread_messages_sender_created
    ON thread_messages (sender_user_id, created_at);

DROP TRIGGER IF EXISTS trg_contact_threads_updated_at ON contact_threads;
CREATE TRIGGER trg_contact_threads_updated_at
    BEFORE UPDATE ON contact_threads
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

INSERT INTO methodology_parameters (
    version,
    param_key,
    value_numeric,
    value_json,
    description
)
VALUES (
    'v1.0',
    'board.max_thread_messages_per_day',
    50,
    NULL,
    'Maximum thread messages a single user may send per day across all their community threads.'
)
ON CONFLICT (version, param_key) DO NOTHING;

INSERT INTO feature_flags (
    key,
    name,
    description,
    status,
    access_tier,
    default_enabled,
    metadata
)
VALUES (
    'community_threads_enabled',
    'Community threads',
    'Enables contact-gated 1:1 messaging threads on the migration board.',
    'enabled',
    'public',
    TRUE,
    '{"episode":"community-threads-v1"}'::jsonb
)
ON CONFLICT (key) DO NOTHING;

INSERT INTO feature_access_rules (
    feature_key,
    access_tier,
    is_enabled
)
VALUES ('community_threads_enabled', 'public', TRUE)
ON CONFLICT (feature_key, access_tier) DO NOTHING;
