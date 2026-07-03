-- Migration 019: Adds the legal_signal_events timeline table with indexes for country/date/impact queries.
CREATE TABLE IF NOT EXISTS legal_signal_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    legal_signal_id UUID NOT NULL REFERENCES legal_signals(id) ON DELETE CASCADE,
    country_id UUID NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
    event_date DATE NOT NULL,
    event_type TEXT NOT NULL,
    impact_direction TEXT NOT NULL,
    impact_level TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    source_id UUID REFERENCES sources(id) ON DELETE SET NULL,
    evidence_item_id UUID REFERENCES evidence_items(id) ON DELETE SET NULL,
    affected_groups JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT legal_signal_events_event_type_check CHECK (
        event_type IN ('created', 'updated', 'amended', 'effective', 'expired', 'confirmed')
    ),
    CONSTRAINT legal_signal_events_impact_direction_check CHECK (
        impact_direction IN ('positive', 'negative', 'neutral', 'mixed', 'uncertain')
    ),
    CONSTRAINT legal_signal_events_impact_level_check CHECK (
        impact_level IN ('low', 'medium', 'high', 'critical')
    ),
    CONSTRAINT legal_signal_events_signal_date_type_unique UNIQUE (
        legal_signal_id,
        event_date,
        event_type
    )
);

CREATE INDEX IF NOT EXISTS idx_legal_signal_events_country_date
    ON legal_signal_events(country_id, event_date DESC);

CREATE INDEX IF NOT EXISTS idx_legal_signal_events_legal_signal
    ON legal_signal_events(legal_signal_id);

CREATE INDEX IF NOT EXISTS idx_legal_signal_events_date
    ON legal_signal_events(event_date DESC);

CREATE INDEX IF NOT EXISTS idx_legal_signal_events_impact_direction
    ON legal_signal_events(impact_direction);

CREATE INDEX IF NOT EXISTS idx_legal_signal_events_impact_level
    ON legal_signal_events(impact_level);

CREATE INDEX IF NOT EXISTS idx_legal_signal_events_event_type
    ON legal_signal_events(event_type);

CREATE INDEX IF NOT EXISTS idx_legal_signal_events_source
    ON legal_signal_events(source_id);

CREATE INDEX IF NOT EXISTS idx_legal_signal_events_evidence
    ON legal_signal_events(evidence_item_id);

INSERT INTO legal_signal_events (
    legal_signal_id,
    country_id,
    event_date,
    event_type,
    impact_direction,
    impact_level,
    title,
    summary,
    source_id,
    evidence_item_id,
    affected_groups
)
SELECT
    ls.id,
    ls.country_id,
    COALESCE(
        CASE
            WHEN ls.effective_date <= CURRENT_DATE THEN ls.effective_date
        END,
        CASE
            WHEN ls.published_date <= CURRENT_DATE THEN ls.published_date
        END,
        ls.created_at::date
    ),
    'confirmed',
    CASE
        WHEN ls.impact_direction = 'unknown' THEN 'uncertain'
        ELSE ls.impact_direction
    END,
    ls.impact_level,
    COALESCE(ls.title_en, ls.title),
    COALESCE(ls.summary_en, ls.summary),
    ls.source_id,
    evidence.id,
    COALESCE(ls.affected_groups, '[]'::jsonb)
FROM legal_signals ls
JOIN countries c ON c.id = ls.country_id
LEFT JOIN LATERAL (
    SELECT ei.id
    FROM evidence_items ei
    WHERE ei.legal_signal_id = ls.id
      AND ei.status = 'published'
    ORDER BY ei.published_at DESC NULLS LAST, ei.created_at DESC
    LIMIT 1
) evidence ON TRUE
WHERE ls.status = 'published'
  AND c.slug IN ('russia', 'uruguay')
ON CONFLICT (legal_signal_id, event_date, event_type) DO UPDATE
SET
    country_id = EXCLUDED.country_id,
    impact_direction = EXCLUDED.impact_direction,
    impact_level = EXCLUDED.impact_level,
    title = EXCLUDED.title,
    summary = EXCLUDED.summary,
    source_id = EXCLUDED.source_id,
    evidence_item_id = EXCLUDED.evidence_item_id,
    affected_groups = EXCLUDED.affected_groups,
    updated_at = NOW();
