-- Migration 045: Migration Board Companions v1: adds migration_board_posts and related contact/report/block tables.
CREATE TABLE IF NOT EXISTS migration_board_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    origin_country_id UUID REFERENCES countries(id) ON DELETE SET NULL,
    destination_country_id UUID NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
    route_id UUID REFERENCES routes(id) ON DELETE SET NULL,
    scenario_slug TEXT REFERENCES scenarios(slug) ON DELETE SET NULL,
    persona_slug TEXT REFERENCES personas(slug) ON DELETE SET NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    target_city TEXT,
    target_month DATE,
    timeline_window TEXT NOT NULL DEFAULT 'unknown',
    budget_range TEXT NOT NULL DEFAULT 'undisclosed',
    household_type TEXT NOT NULL DEFAULT 'undisclosed',
    migration_stage TEXT NOT NULL DEFAULT 'researching',
    companion_goal TEXT NOT NULL DEFAULT 'info_exchange',
    preferred_language TEXT NOT NULL DEFAULT 'undisclosed',
    visibility TEXT NOT NULL DEFAULT 'members_only',
    status TEXT NOT NULL DEFAULT 'draft',
    moderation_status TEXT NOT NULL DEFAULT 'pending',
    risk_acknowledged BOOLEAN NOT NULL DEFAULT FALSE,
    legal_disclaimer_acknowledged BOOLEAN NOT NULL DEFAULT FALSE,
    contact_requests_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    submitted_at TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    archived_at TIMESTAMPTZ,
    rejected_at TIMESTAMPTZ,
    moderated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    moderated_at TIMESTAMPTZ,
    moderation_reason TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT migration_board_posts_title_length_check
        CHECK (char_length(title) BETWEEN 6 AND 140),
    CONSTRAINT migration_board_posts_summary_length_check
        CHECK (char_length(summary) BETWEEN 30 AND 1200),
    CONSTRAINT migration_board_posts_target_city_length_check
        CHECK (target_city IS NULL OR char_length(target_city) <= 120),
    CONSTRAINT migration_board_posts_moderation_reason_length_check
        CHECK (moderation_reason IS NULL OR char_length(moderation_reason) <= 1000),
    CONSTRAINT migration_board_posts_timeline_window_check
        CHECK (
            timeline_window IN (
                '0_3_months',
                '3_6_months',
                '6_12_months',
                '12_plus_months',
                'unknown'
            )
        ),
    CONSTRAINT migration_board_posts_budget_range_check
        CHECK (budget_range IN ('low', 'medium', 'high', 'undisclosed')),
    CONSTRAINT migration_board_posts_household_type_check
        CHECK (
            household_type IN ('solo', 'couple', 'family', 'friends', 'undisclosed')
        ),
    CONSTRAINT migration_board_posts_migration_stage_check
        CHECK (
            migration_stage IN (
                'researching',
                'preparing_documents',
                'applying',
                'waiting_decision',
                'relocating_soon',
                'already_relocated',
                'on_hold'
            )
        ),
    CONSTRAINT migration_board_posts_companion_goal_check
        CHECK (
            companion_goal IN (
                'info_exchange',
                'travel_together',
                'housing_search',
                'document_support',
                'study_group',
                'business_network',
                'family_network',
                'other'
            )
        ),
    CONSTRAINT migration_board_posts_visibility_check
        CHECK (visibility IN ('public', 'members_only', 'private')),
    CONSTRAINT migration_board_posts_status_check
        CHECK (status IN ('draft', 'review', 'published', 'archived', 'rejected')),
    CONSTRAINT migration_board_posts_moderation_status_check
        CHECK (moderation_status IN ('pending', 'approved', 'rejected', 'flagged', 'hidden')),
    CONSTRAINT migration_board_posts_metadata_object_check
        CHECK (jsonb_typeof(metadata) = 'object'),
    CONSTRAINT migration_board_posts_published_state_check
        CHECK (
            status <> 'published'
            OR (
                moderation_status = 'approved'
                AND risk_acknowledged IS TRUE
                AND legal_disclaimer_acknowledged IS TRUE
            )
        )
);

CREATE INDEX IF NOT EXISTS idx_migration_board_posts_user_id
    ON migration_board_posts (user_id);

CREATE INDEX IF NOT EXISTS idx_migration_board_posts_destination
    ON migration_board_posts (destination_country_id);

CREATE INDEX IF NOT EXISTS idx_migration_board_posts_origin
    ON migration_board_posts (origin_country_id);

CREATE INDEX IF NOT EXISTS idx_migration_board_posts_route
    ON migration_board_posts (route_id);

CREATE INDEX IF NOT EXISTS idx_migration_board_posts_status
    ON migration_board_posts (status, moderation_status);

CREATE INDEX IF NOT EXISTS idx_migration_board_posts_published_at
    ON migration_board_posts (published_at DESC, id);

CREATE INDEX IF NOT EXISTS idx_migration_board_posts_public_listing
    ON migration_board_posts (destination_country_id, published_at DESC)
    WHERE status = 'published'
        AND moderation_status = 'approved'
        AND visibility IN ('public', 'members_only');

CREATE TABLE IF NOT EXISTS migration_board_contact_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES migration_board_posts(id) ON DELETE CASCADE,
    from_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    to_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    responded_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    response_note TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT migration_board_contact_requests_message_length_check
        CHECK (char_length(message) BETWEEN 20 AND 800),
    CONSTRAINT migration_board_contact_requests_status_check
        CHECK (
            status IN (
                'pending',
                'accepted',
                'declined',
                'cancelled',
                'expired',
                'reported'
            )
        ),
    CONSTRAINT migration_board_contact_requests_no_self_check
        CHECK (from_user_id <> to_user_id),
    CONSTRAINT migration_board_contact_requests_metadata_object_check
        CHECK (jsonb_typeof(metadata) = 'object')
);

CREATE INDEX IF NOT EXISTS idx_migration_board_contact_requests_post
    ON migration_board_contact_requests (post_id);

CREATE INDEX IF NOT EXISTS idx_migration_board_contact_requests_from_user
    ON migration_board_contact_requests (from_user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_migration_board_contact_requests_to_user
    ON migration_board_contact_requests (to_user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_migration_board_contact_requests_status
    ON migration_board_contact_requests (status);

CREATE UNIQUE INDEX IF NOT EXISTS idx_migration_board_contact_requests_one_pending
    ON migration_board_contact_requests (post_id, from_user_id)
    WHERE status = 'pending';

CREATE TABLE IF NOT EXISTS migration_board_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reporter_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    post_id UUID REFERENCES migration_board_posts(id) ON DELETE CASCADE,
    contact_request_id UUID REFERENCES migration_board_contact_requests(id)
        ON DELETE CASCADE,
    reason TEXT NOT NULL,
    details TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reviewed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMPTZ,
    resolution_note TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT migration_board_reports_target_check
        CHECK (post_id IS NOT NULL OR contact_request_id IS NOT NULL),
    CONSTRAINT migration_board_reports_reason_check
        CHECK (
            reason IN (
                'spam',
                'scam',
                'abuse',
                'privacy',
                'misleading',
                'unsafe_contact',
                'off_topic',
                'other'
            )
        ),
    CONSTRAINT migration_board_reports_status_check
        CHECK (status IN ('pending', 'reviewing', 'resolved', 'dismissed')),
    CONSTRAINT migration_board_reports_details_length_check
        CHECK (details IS NULL OR char_length(details) <= 1000),
    CONSTRAINT migration_board_reports_metadata_object_check
        CHECK (jsonb_typeof(metadata) = 'object')
);

CREATE INDEX IF NOT EXISTS idx_migration_board_reports_post
    ON migration_board_reports (post_id);

CREATE INDEX IF NOT EXISTS idx_migration_board_reports_contact_request
    ON migration_board_reports (contact_request_id);

CREATE INDEX IF NOT EXISTS idx_migration_board_reports_status
    ON migration_board_reports (status, created_at DESC);

CREATE UNIQUE INDEX IF NOT EXISTS idx_migration_board_reports_unique_post_report
    ON migration_board_reports (reporter_user_id, post_id)
    WHERE post_id IS NOT NULL
        AND status IN ('pending', 'reviewing');

CREATE UNIQUE INDEX IF NOT EXISTS idx_migration_board_reports_unique_contact_report
    ON migration_board_reports (reporter_user_id, contact_request_id)
    WHERE contact_request_id IS NOT NULL
        AND status IN ('pending', 'reviewing');

CREATE TABLE IF NOT EXISTS migration_board_blocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blocker_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    blocked_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reason TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT migration_board_blocks_no_self_check
        CHECK (blocker_user_id <> blocked_user_id),
    CONSTRAINT migration_board_blocks_unique_pair
        UNIQUE (blocker_user_id, blocked_user_id),
    CONSTRAINT migration_board_blocks_metadata_object_check
        CHECK (jsonb_typeof(metadata) = 'object')
);

CREATE INDEX IF NOT EXISTS idx_migration_board_blocks_blocker
    ON migration_board_blocks (blocker_user_id);

CREATE INDEX IF NOT EXISTS idx_migration_board_blocks_blocked
    ON migration_board_blocks (blocked_user_id);

CREATE TABLE IF NOT EXISTS migration_board_post_tags (
    post_id UUID NOT NULL REFERENCES migration_board_posts(id) ON DELETE CASCADE,
    tag TEXT NOT NULL,
    PRIMARY KEY (post_id, tag),
    CONSTRAINT migration_board_post_tags_tag_check
        CHECK (
            tag IN (
                'pets',
                'children',
                'remote_work',
                'business',
                'study',
                'documents',
                'housing',
                'tax',
                'banking',
                'language_exchange',
                'safety',
                'low_budget'
            )
        )
);

CREATE INDEX IF NOT EXISTS idx_migration_board_post_tags_tag
    ON migration_board_post_tags (tag);

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
        'migration_board_enabled',
        'Migration board',
        'Enables privacy-first migration intention board endpoints.',
        'enabled',
        'public',
        TRUE,
        '{"episode":"migration-board-companions-v1"}'::jsonb
    ),
    (
        'companion_matching_enabled',
        'Companion matching',
        'Enables non-scored companion discovery for similar migration intentions.',
        'enabled',
        'public',
        TRUE,
        '{"episode":"migration-board-companions-v1"}'::jsonb
    ),
    (
        'contact_requests_enabled',
        'Migration board contact requests',
        'Enables platform-mediated contact requests for migration board posts.',
        'enabled',
        'public',
        TRUE,
        '{"episode":"migration-board-companions-v1"}'::jsonb
    ),
    (
        'migration_board_public_listing_enabled',
        'Migration board public listing',
        'Enables privacy-safe public listing for approved migration board posts.',
        'enabled',
        'public',
        TRUE,
        '{"episode":"migration-board-companions-v1"}'::jsonb
    ),
    (
        'migration_board_moderation_enabled',
        'Migration board moderation',
        'Enables moderator approval and report review for migration board posts.',
        'enabled',
        'public',
        TRUE,
        '{"episode":"migration-board-companions-v1"}'::jsonb
    )
ON CONFLICT (key) DO NOTHING;

INSERT INTO feature_access_rules (
    feature_key,
    access_tier,
    is_enabled
)
VALUES
    ('migration_board_enabled', 'public', TRUE),
    ('companion_matching_enabled', 'public', TRUE),
    ('contact_requests_enabled', 'public', TRUE),
    ('migration_board_public_listing_enabled', 'public', TRUE),
    ('migration_board_moderation_enabled', 'public', TRUE)
ON CONFLICT (feature_key, access_tier) DO NOTHING;
