-- Migration 028: Fixes columns on domain_events found during the audit pass.
UPDATE legal_signals
SET
    legal_status = CASE status
        WHEN 'proposed' THEN 'proposed'
        WHEN 'adopted' THEN 'adopted'
        WHEN 'active' THEN 'effective'
        WHEN 'effective' THEN 'effective'
        WHEN 'expired' THEN 'expired'
        WHEN 'revoked' THEN 'revoked'
        ELSE legal_status
    END,
    status = 'published'
WHERE status IN ('proposed', 'adopted', 'active', 'effective', 'expired', 'revoked');

DROP TRIGGER IF EXISTS trg_routes_updated_at ON routes;
CREATE TRIGGER trg_routes_updated_at
    BEFORE UPDATE ON routes
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

ALTER TABLE domain_events
    DROP CONSTRAINT IF EXISTS domain_events_event_type_check;

ALTER TABLE domain_events
    ADD CONSTRAINT domain_events_event_type_check CHECK (
        event_type IN (
            'legal_signal.published',
            'legal_signal_event.published',
            'route.published',
            'user_story.published'
        )
    );
