-- Migration 055: async admin recompute (Аудит-эпизод 5, P2-3)
--
-- Adds 'recompute_requested' to the allowed domain_events.event_type values
-- so the trust/platform-metrics/country-drift "recompute all" admin
-- endpoints can record the request instead of looping over every country
-- inline in the HTTP request.
--
-- Also restores 'drift.changed', dropped by 047_trip_planner_v1.sql's
-- rewrite of this same constraint (it replaced the whole allowed list
-- instead of extending it, silently removing a value production code at
-- services/country_drift.py still inserts). No existing test caught it
-- because domain_events tests mock the connection rather than hitting a
-- real constraint. Found and fixed while touching this constraint for
-- P2-3 - not part of the original P2-3 scope, but the same table and the
-- same statement shape, so fixing it here avoids a second migration for a
-- one-line list edit.

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
            'trip_reminder_due',
            'drift.changed',
            'recompute_requested'
        )
    );
