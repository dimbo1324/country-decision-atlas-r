-- Migration 021: Fixes an evidence gap in Uruguay's content.
DO $$
DECLARE
    v_country_id UUID;
    v_source_id UUID;
BEGIN
    SELECT id INTO v_country_id FROM countries WHERE slug = 'uruguay';

    SELECT id INTO v_source_id
    FROM sources
    WHERE country_id = v_country_id AND status = 'published'
    ORDER BY created_at
    LIMIT 1;

    IF NOT EXISTS (
        SELECT 1 FROM evidence_items WHERE id = 'e8a2b1c4-0000-4000-a000-000000000021'::uuid
    ) THEN
        INSERT INTO evidence_items (
            id, country_id, source_id, title, summary, claim, excerpt,
            evidence_type, confidence, confidence_level, status, published_at
        ) VALUES (
            'e8a2b1c4-0000-4000-a000-000000000021'::uuid,
            v_country_id,
            v_source_id,
            'Residency application process — official DNM guidance',
            'The Uruguayan National Directorate of Migration (DNM) outlines the legal steps for obtaining temporary and permanent residency, including required documentation and processing timelines.',
            'Uruguay provides a formal, multi-stage legal pathway to permanent residency through the DNM, with defined documentation requirements.',
            'La DNM establece los requisitos para la residencia legal en Uruguay.',
            'source_note',
            'high',
            'high',
            'published',
            '2024-01-15'
        );
    END IF;
END;
$$;
