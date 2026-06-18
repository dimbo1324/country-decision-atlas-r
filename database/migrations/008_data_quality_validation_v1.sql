UPDATE
    sources
SET
    status = 'review'
WHERE
    status = 'published'
    AND (
        title IS NULL
        OR title = ''
        OR url IS NULL
        OR url = ''
        OR publisher IS NULL
        OR publisher = ''
        OR source_type IS NULL
        OR source_type = ''
        OR COALESCE(confidence, reliability_level) IS NULL
    );

UPDATE
    legal_signals
SET
    status = 'review'
WHERE
    status = 'published'
    AND (
        country_id IS NULL
        OR COALESCE(title_en, title) IS NULL
        OR COALESCE(title_en, title) = ''
        OR COALESCE(summary_en, summary) IS NULL
        OR COALESCE(summary_en, summary) = ''
        OR signal_type IS NULL
        OR impact_direction IS NULL
        OR impact_level IS NULL
        OR source_id IS NULL
        OR COALESCE(confidence, confidence_level) IS NULL
    );

UPDATE
    evidence_items
SET
    status = 'review'
WHERE
    status = 'published'
    AND (
        source_id IS NULL
        OR country_id IS NULL
        OR COALESCE(claim, title) IS NULL
        OR COALESCE(claim, title) = ''
        OR COALESCE(confidence, confidence_level) IS NULL
    );

UPDATE
    user_stories
SET
    status = 'review'
WHERE
    status = 'published'
    AND is_synthetic = TRUE
    AND (
        verification_status <> 'synthetic'
        OR notes IS NULL
        OR notes = ''
        OR (
            LOWER(notes) NOT LIKE '%synthetic%'
            AND LOWER(notes) NOT LIKE '%demo%'
        )
    );

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'country_scores_score_range_check'
    ) THEN
        ALTER TABLE country_scores
        ADD CONSTRAINT country_scores_score_range_check
        CHECK (score >= 0 AND score <= 100);
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'country_score_breakdowns_score_range_check'
    ) THEN
        ALTER TABLE country_score_breakdowns
        ADD CONSTRAINT country_score_breakdowns_score_range_check
        CHECK (score >= 0 AND score <= 100);
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'country_score_breakdowns_weight_range_check'
    ) THEN
        ALTER TABLE country_score_breakdowns
        ADD CONSTRAINT country_score_breakdowns_weight_range_check
        CHECK (weight >= 0 AND weight <= 1);
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'sources_published_quality_check'
    ) THEN
        ALTER TABLE sources
        ADD CONSTRAINT sources_published_quality_check
        CHECK (
            status <> 'published'
            OR (
                title IS NOT NULL
                AND title <> ''
                AND url IS NOT NULL
                AND url <> ''
                AND publisher IS NOT NULL
                AND publisher <> ''
                AND source_type IS NOT NULL
                AND source_type <> ''
                AND COALESCE(confidence, reliability_level) IS NOT NULL
            )
        );
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'legal_signals_published_quality_check'
    ) THEN
        ALTER TABLE legal_signals
        ADD CONSTRAINT legal_signals_published_quality_check
        CHECK (
            status <> 'published'
            OR (
                country_id IS NOT NULL
                AND COALESCE(title_en, title) IS NOT NULL
                AND COALESCE(title_en, title) <> ''
                AND COALESCE(summary_en, summary) IS NOT NULL
                AND COALESCE(summary_en, summary) <> ''
                AND signal_type IS NOT NULL
                AND impact_direction IS NOT NULL
                AND impact_level IS NOT NULL
                AND source_id IS NOT NULL
                AND COALESCE(confidence, confidence_level) IS NOT NULL
            )
        );
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'evidence_items_published_quality_check'
    ) THEN
        ALTER TABLE evidence_items
        ADD CONSTRAINT evidence_items_published_quality_check
        CHECK (
            status <> 'published'
            OR (
                source_id IS NOT NULL
                AND country_id IS NOT NULL
                AND COALESCE(claim, title) IS NOT NULL
                AND COALESCE(claim, title) <> ''
                AND COALESCE(confidence, confidence_level) IS NOT NULL
            )
        );
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'user_stories_synthetic_quality_check'
    ) THEN
        ALTER TABLE user_stories
        ADD CONSTRAINT user_stories_synthetic_quality_check
        CHECK (
            is_synthetic = FALSE
            OR (
                verification_status = 'synthetic'
                AND notes IS NOT NULL
                AND notes <> ''
                AND (
                    LOWER(notes) LIKE '%synthetic%'
                    OR LOWER(notes) LIKE '%demo%'
                )
            )
        );
    END IF;
END $$;
