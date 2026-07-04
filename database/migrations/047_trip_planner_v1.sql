-- Migration 047: Trip Planner v1: private relocation plans, checklist items, reminders, sharing, and exports.
CREATE TABLE IF NOT EXISTS trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    scenario_slug TEXT REFERENCES scenarios(slug),
    origin_country_id UUID REFERENCES countries(id),
    status TEXT NOT NULL DEFAULT 'draft',
    confidence_tier TEXT NOT NULL DEFAULT 'declared',
    visibility TEXT NOT NULL DEFAULT 'private',
    share_token_hash TEXT UNIQUE,
    share_token_prefix TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    CONSTRAINT trips_title_check CHECK (BTRIM(title) <> ''),
    CONSTRAINT trips_status_check
        CHECK (status IN ('draft', 'active', 'completed', 'abandoned')),
    CONSTRAINT trips_confidence_tier_check
        CHECK (confidence_tier IN ('declared', 'active', 'confirmed')),
    CONSTRAINT trips_visibility_check CHECK (visibility IN ('private', 'link')),
    CONSTRAINT trips_share_token_state_check CHECK (
        (
            visibility = 'private'
            AND share_token_hash IS NULL
            AND share_token_prefix IS NULL
        )
        OR (
            visibility = 'link'
            AND share_token_hash IS NOT NULL
            AND share_token_prefix IS NOT NULL
        )
    ),
    CONSTRAINT trips_completed_state_check CHECK (
        (status = 'completed' AND completed_at IS NOT NULL)
        OR (status <> 'completed')
    )
);

CREATE TABLE IF NOT EXISTS trip_waypoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    position INT NOT NULL,
    country_id UUID NOT NULL REFERENCES countries(id),
    city TEXT,
    kind TEXT NOT NULL DEFAULT 'destination',
    planned_from DATE,
    planned_to DATE,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_trip_position UNIQUE (trip_id, position),
    CONSTRAINT trip_waypoints_position_check CHECK (position > 0),
    CONSTRAINT trip_waypoints_kind_check
        CHECK (kind IN ('transit', 'destination', 'stopover')),
    CONSTRAINT trip_waypoints_dates_check CHECK (
        planned_from IS NULL
        OR planned_to IS NULL
        OR planned_from <= planned_to
    )
);

CREATE TABLE IF NOT EXISTS trip_checklist_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    waypoint_id UUID REFERENCES trip_waypoints(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT,
    due_date DATE,
    status TEXT NOT NULL DEFAULT 'todo',
    origin_kind TEXT NOT NULL DEFAULT 'manual',
    origin_ref UUID,
    position INT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT trip_checklist_items_title_check CHECK (BTRIM(title) <> ''),
    CONSTRAINT trip_checklist_items_status_check
        CHECK (status IN ('todo', 'in_progress', 'done', 'skipped')),
    CONSTRAINT trip_checklist_items_origin_kind_check
        CHECK (origin_kind IN ('manual', 'route_template', 'author_template')),
    CONSTRAINT trip_checklist_items_position_check CHECK (position > 0)
);

CREATE TABLE IF NOT EXISTS trip_reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    checklist_item_id UUID REFERENCES trip_checklist_items(id) ON DELETE CASCADE,
    remind_at TIMESTAMPTZ NOT NULL,
    channel TEXT NOT NULL DEFAULT 'telegram',
    status TEXT NOT NULL DEFAULT 'scheduled',
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT trip_reminders_channel_check CHECK (channel IN ('telegram')),
    CONSTRAINT trip_reminders_status_check
        CHECK (status IN ('scheduled', 'sent', 'cancelled')),
    CONSTRAINT trip_reminders_sent_state_check CHECK (
        (status = 'sent' AND sent_at IS NOT NULL)
        OR (status <> 'sent')
    )
);

CREATE TABLE IF NOT EXISTS trip_annotations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    waypoint_id UUID REFERENCES trip_waypoints(id) ON DELETE CASCADE,
    kind TEXT NOT NULL,
    body TEXT NOT NULL,
    position INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT trip_annotations_kind_check
        CHECK (kind IN ('note', 'item_to_bring', 'warning_ack')),
    CONSTRAINT trip_annotations_body_check CHECK (BTRIM(body) <> ''),
    CONSTRAINT trip_annotations_position_check
        CHECK (position IS NULL OR position > 0)
);

CREATE INDEX IF NOT EXISTS idx_trips_user_status
    ON trips (user_id, status, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_trips_share_token_hash
    ON trips (share_token_hash)
    WHERE share_token_hash IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_trip_waypoints_trip_position
    ON trip_waypoints (trip_id, position);

CREATE INDEX IF NOT EXISTS idx_trip_checklist_items_trip_position
    ON trip_checklist_items (trip_id, position);

CREATE INDEX IF NOT EXISTS idx_trip_reminders_due
    ON trip_reminders (remind_at, status)
    WHERE status = 'scheduled';

DROP TRIGGER IF EXISTS trg_trips_updated_at ON trips;
CREATE TRIGGER trg_trips_updated_at
    BEFORE UPDATE ON trips
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_trip_waypoints_updated_at ON trip_waypoints;
CREATE TRIGGER trg_trip_waypoints_updated_at
    BEFORE UPDATE ON trip_waypoints
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_trip_checklist_items_updated_at ON trip_checklist_items;
CREATE TRIGGER trg_trip_checklist_items_updated_at
    BEFORE UPDATE ON trip_checklist_items
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_trip_reminders_updated_at ON trip_reminders;
CREATE TRIGGER trg_trip_reminders_updated_at
    BEFORE UPDATE ON trip_reminders
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_trip_annotations_updated_at ON trip_annotations;
CREATE TRIGGER trg_trip_annotations_updated_at
    BEFORE UPDATE ON trip_annotations
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

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
    'trip_planner_enabled',
    'Trip planner',
    'Enables private relocation trip planning, checklist, warnings, reminders, sharing, and exports.',
    'enabled',
    'public',
    TRUE,
    '{"episode":"trip-planner-v1"}'::jsonb
)
ON CONFLICT (key) DO NOTHING;

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
        'trip.warning.high_impact_min_rank',
        3,
        NULL,
        'Minimum legal signal impact rank that becomes a high-severity trip warning.'
    ),
    (
        'v1.0',
        'trip.warning.restrictive_pair_severity_rank',
        3,
        NULL,
        'Severity rank for restrictive published country-pair compatibility warnings.'
    ),
    (
        'v1.0',
        'trip.warning.missing_pair_severity_rank',
        2,
        NULL,
        'Severity rank for missing country-pair compatibility context warnings.'
    )
ON CONFLICT (version, param_key) DO NOTHING;

ALTER TABLE domain_events
    DROP CONSTRAINT IF EXISTS domain_events_event_type_check;

ALTER TABLE domain_events
    ADD CONSTRAINT domain_events_event_type_check CHECK (
        event_type IN (
            'legal_signal.published',
            'legal_signal_event.published',
            'route.published',
            'user_story.published',
            'ai_draft.ready',
            'contradiction_candidate.created',
            'community_question.submitted',
            'community_answer.submitted',
            'data_error_report.submitted',
            'trip_reminder_due'
        )
    );
