ALTER TABLE legal_signals
    ADD COLUMN IF NOT EXISTS legal_status TEXT NOT NULL DEFAULT 'unknown';

ALTER TABLE legal_signals
    DROP CONSTRAINT IF EXISTS legal_signals_legal_status_check;

ALTER TABLE legal_signals
    ADD CONSTRAINT legal_signals_legal_status_check CHECK (
        legal_status IN (
            'proposed',
            'adopted',
            'effective',
            'expired',
            'revoked',
            'unknown'
        )
    );

UPDATE legal_signals
SET
    legal_status = CASE status
        WHEN 'proposed' THEN 'proposed'
        WHEN 'adopted' THEN 'adopted'
        WHEN 'active' THEN 'effective'
        WHEN 'effective' THEN 'effective'
        WHEN 'expired' THEN 'expired'
        WHEN 'revoked' THEN 'revoked'
        ELSE 'unknown'
    END,
    status = CASE
        WHEN status IN ('proposed', 'adopted', 'active', 'effective', 'expired', 'revoked') THEN 'published'
        ELSE status
    END
WHERE
    status IN ('proposed', 'adopted', 'active', 'effective', 'expired', 'revoked')
    AND legal_status = 'unknown';

ALTER TABLE legal_signals
    DROP CONSTRAINT IF EXISTS legal_signals_status_check;

ALTER TABLE legal_signals
    ADD CONSTRAINT legal_signals_status_check CHECK (
        status IN ('draft', 'review', 'published', 'archived', 'rejected')
    );

CREATE TABLE IF NOT EXISTS domain_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_key TEXT NOT NULL,
    event_type TEXT NOT NULL,
    aggregate_type TEXT NOT NULL,
    aggregate_id UUID NOT NULL,
    country_slug TEXT,
    payload JSONB NOT NULL DEFAULT '{}'::JSONB,
    status TEXT NOT NULL DEFAULT 'pending',
    notifiable BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    relayed_at TIMESTAMPTZ,
    attempts INT NOT NULL DEFAULT 0,
    last_error TEXT,
    CONSTRAINT domain_events_event_key_unique UNIQUE (event_key),
    CONSTRAINT domain_events_status_check CHECK (
        status IN ('pending', 'relayed', 'skipped', 'failed')
    ),
    CONSTRAINT domain_events_event_type_check CHECK (
        event_type IN (
            'legal_signal.published',
            'legal_signal_event.published',
            'route.published',
            'user_story.published',
            'drift.changed'
        )
    )
);

CREATE INDEX IF NOT EXISTS idx_domain_events_pending
    ON domain_events (created_at)
    WHERE status = 'pending';

CREATE INDEX IF NOT EXISTS idx_domain_events_aggregate
    ON domain_events (aggregate_type, aggregate_id);

CREATE INDEX IF NOT EXISTS idx_domain_events_country_slug
    ON domain_events (country_slug)
    WHERE country_slug IS NOT NULL;

ALTER TABLE domain_events
    DROP CONSTRAINT IF EXISTS domain_events_attempts_non_negative;

ALTER TABLE domain_events
    ADD CONSTRAINT domain_events_attempts_non_negative CHECK (attempts >= 0);
