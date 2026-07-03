-- Migration 044: Auth, RBAC, and web personalization: adds authentication and role columns to the users table.
ALTER TABLE users
ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'active',
ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS last_seen_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS metadata JSONB NOT NULL DEFAULT '{}'::jsonb;

ALTER TABLE users
DROP CONSTRAINT IF EXISTS users_role_check;

ALTER TABLE users
ADD CONSTRAINT users_role_check
    CHECK (role IN ('user', 'editor', 'moderator', 'admin', 'owner'));

ALTER TABLE users
DROP CONSTRAINT IF EXISTS users_status_check;

ALTER TABLE users
ADD CONSTRAINT users_status_check
    CHECK (status IN ('active', 'suspended', 'deleted'));

ALTER TABLE users
DROP CONSTRAINT IF EXISTS users_metadata_object_check;

ALTER TABLE users
ADD CONSTRAINT users_metadata_object_check
    CHECK (jsonb_typeof(metadata) = 'object');

CREATE TABLE IF NOT EXISTS user_auth_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    credential_type TEXT NOT NULL DEFAULT 'password',
    password_hash TEXT,
    password_updated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT user_auth_credentials_user_type_unique
        UNIQUE (user_id, credential_type),
    CONSTRAINT user_auth_credentials_type_check
        CHECK (credential_type IN ('password'))
);

CREATE TABLE IF NOT EXISTS auth_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    last_seen_at TIMESTAMPTZ,
    user_agent_hash TEXT,
    ip_hash TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT auth_sessions_metadata_object_check
        CHECK (jsonb_typeof(metadata) = 'object')
);

CREATE INDEX IF NOT EXISTS idx_auth_sessions_user_id
    ON auth_sessions (user_id);

CREATE INDEX IF NOT EXISTS idx_auth_sessions_active
    ON auth_sessions (user_id, expires_at)
    WHERE revoked_at IS NULL;

CREATE TABLE IF NOT EXISTS user_telegram_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    telegram_user_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'linked',
    linked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    unlinked_at TIMESTAMPTZ,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT user_telegram_links_unique_active
        UNIQUE (telegram_user_id),
    CONSTRAINT user_telegram_links_status_check
        CHECK (status IN ('linked', 'unlinked')),
    CONSTRAINT user_telegram_links_metadata_object_check
        CHECK (jsonb_typeof(metadata) = 'object')
);

CREATE INDEX IF NOT EXISTS idx_user_telegram_links_user_id
    ON user_telegram_links (user_id);

ALTER TABLE watchlists
ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'active',
ADD COLUMN IF NOT EXISTS notify_legal_signals BOOLEAN NOT NULL DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS notify_drift_changes BOOLEAN NOT NULL DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS notify_route_updates BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS notes TEXT,
ADD COLUMN IF NOT EXISTS created_source TEXT NOT NULL DEFAULT 'web',
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS archived_at TIMESTAMPTZ;

ALTER TABLE watchlists
DROP CONSTRAINT IF EXISTS watchlists_status_check;

ALTER TABLE watchlists
ADD CONSTRAINT watchlists_status_check
    CHECK (status IN ('active', 'archived'));

ALTER TABLE watchlists
DROP CONSTRAINT IF EXISTS watchlists_created_source_check;

ALTER TABLE watchlists
ADD CONSTRAINT watchlists_created_source_check
    CHECK (created_source IN ('web', 'telegram_linked', 'imported', 'admin'));

ALTER TABLE watchlists
DROP CONSTRAINT IF EXISTS watchlists_notes_length_check;

ALTER TABLE watchlists
ADD CONSTRAINT watchlists_notes_length_check
    CHECK (notes IS NULL OR char_length(notes) <= 2000);

CREATE INDEX IF NOT EXISTS idx_watchlists_user_status
    ON watchlists (user_id, status);

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
        'auth_enabled',
        'Web authentication',
        'Enables web user registration, login, and session-based auth.',
        'enabled',
        'public',
        TRUE,
        '{"episode":"auth-rbac-web-personalization-v1"}'::jsonb
    ),
    (
        'web_watchlist_enabled',
        'Web watchlist',
        'Enables authenticated users to save countries to a personal watchlist.',
        'enabled',
        'public',
        TRUE,
        '{"episode":"auth-rbac-web-personalization-v1"}'::jsonb
    ),
    (
        'telegram_web_link_enabled',
        'Telegram web linking',
        'Enables linking a Telegram identity to a web account.',
        'enabled',
        'public',
        TRUE,
        '{"episode":"auth-rbac-web-personalization-v1"}'::jsonb
    ),
    (
        'rbac_admin_enabled',
        'RBAC admin gating',
        'Marks role-based access control as the active admin access mechanism.',
        'enabled',
        'public',
        TRUE,
        '{"episode":"auth-rbac-web-personalization-v1"}'::jsonb
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
    ('auth_enabled', 'public', TRUE),
    ('web_watchlist_enabled', 'public', TRUE),
    ('telegram_web_link_enabled', 'public', TRUE),
    ('rbac_admin_enabled', 'public', TRUE)
ON CONFLICT (feature_key, access_tier) DO UPDATE
SET
    is_enabled = EXCLUDED.is_enabled;
