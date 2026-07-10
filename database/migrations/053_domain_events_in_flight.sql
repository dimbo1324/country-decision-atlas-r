-- Migration 053: Domain events in-flight status lets the outbox relay release row locks
-- before the blocking Kafka publish call, instead of holding them for the full transaction.
ALTER TABLE domain_events
ADD COLUMN IF NOT EXISTS locked_at TIMESTAMPTZ;

ALTER TABLE domain_events
    DROP CONSTRAINT IF EXISTS domain_events_status_check;

ALTER TABLE domain_events
    ADD CONSTRAINT domain_events_status_check
    CHECK (
        status IN ('pending', 'in_flight', 'relayed', 'skipped', 'failed')
    );

CREATE INDEX IF NOT EXISTS idx_domain_events_in_flight
    ON domain_events (locked_at)
    WHERE status = 'in_flight';
