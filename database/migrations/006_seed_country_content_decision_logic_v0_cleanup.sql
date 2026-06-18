DELETE FROM
    evidence_items evidence
USING
    sources source,
    countries country
WHERE
    evidence.source_id = source.id
    AND source.country_id = country.id
    AND country.slug IN ('russia', 'uruguay')
    AND source.url LIKE 'https://example.invalid/%';

DELETE FROM
    legal_signals signal
USING
    sources source,
    countries country
WHERE
    signal.source_id = source.id
    AND source.country_id = country.id
    AND country.slug IN ('russia', 'uruguay')
    AND source.url LIKE 'https://example.invalid/%';

DELETE FROM
    legal_signals signal
USING
    countries country
WHERE
    signal.country_id = country.id
    AND country.slug IN ('russia', 'uruguay')
    AND signal.source_id IS NULL;

DELETE FROM
    sources source
USING
    countries country
WHERE
    source.country_id = country.id
    AND country.slug IN ('russia', 'uruguay')
    AND source.url LIKE 'https://example.invalid/%';

DELETE FROM
    country_scores score
USING
    countries country,
    scenarios scenario
WHERE
    score.country_id = country.id
    AND score.scenario_id = scenario.id
    AND country.slug IN ('russia', 'uruguay')
    AND scenario.slug NOT IN (
        'relocation_residence',
        'permanent_residence_citizenship',
        'low_budget_living',
        'business_self_employment',
        'safety_political_risk'
    );

DELETE FROM
    user_stories story
USING
    countries origin,
    countries destination
WHERE
    story.origin_country_id = origin.id
    AND story.destination_country_id = destination.id
    AND origin.slug IN ('russia', 'uruguay')
    AND destination.slug IN ('russia', 'uruguay')
    AND story.is_synthetic = TRUE;

WITH story_rows AS (
    SELECT *
    FROM (
        VALUES
            (
                'russia',
                'uruguay',
                'Montevideo',
                2026,
                'relocation_residence',
                9500,
                2800,
                'Residence planning with document preparation and professional review.',
                '["passports","birth_certificates","income_records","apostilled_documents"]',
                'Housing search, Spanish-language paperwork, and banking onboarding took longer than expected.',
                'The family obtained a clearer residence plan and reduced political-risk exposure.',
                'Costs were higher than the initial budget, especially housing and setup expenses.',
                'Prepare documents before arrival and budget for slower administrative steps.',
                7.4
            ),
            (
                'russia',
                'uruguay',
                'Montevideo',
                2026,
                'business_self_employment',
                12000,
                3200,
                'Self-employment exploration with tax and banking review.',
                '["passports","income_records","business_contracts","bank_statements"]',
                'Bank onboarding and tax-residence questions required local professional support.',
                'The user found a more stable operating base for client work.',
                'Setup was slower and more expensive than expected.',
                'Validate banking and tax assumptions before committing to the move.',
                7.0
            ),
            (
                'russia',
                'uruguay',
                'Punta del Este',
                2026,
                'low_budget_living',
                7000,
                2400,
                'Short-term stay used to test budget and housing assumptions.',
                '["passports","rental_agreement","income_records"]',
                'Seasonal housing costs made the budget less predictable.',
                'The user confirmed that Uruguay felt stable and administratively understandable.',
                'The country was not as low-cost as expected.',
                'Test the city and season before treating Uruguay as a low-budget destination.',
                6.8
            ),
            (
                'russia',
                'uruguay',
                'Montevideo',
                2026,
                'permanent_residence_citizenship',
                11000,
                3000,
                'Long-term residence planning with staged document collection.',
                '["passports","civil_records","income_records","police_certificates"]',
                'Document timelines and translation requirements created friction.',
                'The household created a realistic multi-year status plan.',
                'Citizenship expectations had to be made more conservative.',
                'Separate residence planning from citizenship assumptions and verify every timeline.',
                7.2
            )
    ) AS story(
        origin_slug,
        destination_slug,
        city,
        year,
        scenario,
        budget_initial_usd,
        budget_monthly_usd,
        legal_path,
        documents_used,
        problems,
        positive_outcome,
        negative_outcome,
        advice,
        satisfaction_score
    )
)
INSERT INTO
    user_stories (
        origin_country_id,
        destination_country_id,
        city,
        year,
        scenario,
        budget_initial_usd,
        budget_monthly_usd,
        legal_path,
        documents_used,
        problems,
        positive_outcome,
        negative_outcome,
        advice,
        satisfaction_score,
        verification_status,
        status,
        is_synthetic,
        notes
    )
SELECT
    origin.id,
    destination.id,
    story.city,
    story.year,
    story.scenario,
    story.budget_initial_usd,
    story.budget_monthly_usd,
    story.legal_path,
    story.documents_used::jsonb,
    story.problems,
    story.positive_outcome,
    story.negative_outcome,
    story.advice,
    story.satisfaction_score,
    'synthetic',
    'published',
    TRUE,
    'Synthetic example for MVP demonstration only.'
FROM
    story_rows story
    JOIN countries origin ON origin.slug = story.origin_slug
    JOIN countries destination ON destination.slug = story.destination_slug;
