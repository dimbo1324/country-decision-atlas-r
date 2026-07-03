-- Migration 002: Seeds initial reference data: locales, countries, country profiles, scenarios, scenario criteria, and sources.
INSERT INTO locales (code, name, native_name)
VALUES
    ('en', 'English', 'English'),
    ('ru', 'Russian', 'Русский')
ON CONFLICT (code) DO UPDATE
SET name = EXCLUDED.name,
    native_name = EXCLUDED.native_name,
    is_active = TRUE;
INSERT INTO countries (
    slug,
    iso2,
    iso3,
    name,
    official_name,
    region,
    subregion,
    capital,
    currency_code
)
VALUES
    (
        'russia',
        'RU',
        'RUS',
        'Russia',
        'Russian Federation',
        'Europe/Asia',
        'Eastern Europe / Northern Asia',
        'Moscow',
        'RUB'
    ),
    (
        'uruguay',
        'UY',
        'URY',
        'Uruguay',
        'Oriental Republic of Uruguay',
        'Americas',
        'South America',
        'Montevideo',
        'UYU'
    )
ON CONFLICT (slug) DO UPDATE
SET iso2 = EXCLUDED.iso2,
    iso3 = EXCLUDED.iso3,
    name = EXCLUDED.name,
    official_name = EXCLUDED.official_name,
    region = EXCLUDED.region,
    subregion = EXCLUDED.subregion,
    capital = EXCLUDED.capital,
    currency_code = EXCLUDED.currency_code,
    is_active = TRUE;
INSERT INTO country_profiles (
    country_id,
    summary,
    residence_overview,
    citizenship_overview,
    tax_overview,
    business_overview,
    quality_of_life_overview,
    risk_overview
)
SELECT
    countries.id,
    CONCAT(countries.name, ' placeholder profile for early product validation.'),
    'Residence pathways require source-backed review before production use.',
    'Citizenship information is stored as neutral placeholder content.',
    'Tax notes are intentionally generic until verified source data is added.',
    'Business setup overview is available as a draft planning field.',
    'Quality of life notes are placeholder content for schema validation.',
    'Risk overview must be replaced with sourced analysis before launch.'
FROM countries
WHERE countries.slug IN ('russia', 'uruguay')
ON CONFLICT (country_id) DO UPDATE
SET summary = EXCLUDED.summary,
    residence_overview = EXCLUDED.residence_overview,
    citizenship_overview = EXCLUDED.citizenship_overview,
    tax_overview = EXCLUDED.tax_overview,
    business_overview = EXCLUDED.business_overview,
    quality_of_life_overview = EXCLUDED.quality_of_life_overview,
    risk_overview = EXCLUDED.risk_overview;
INSERT INTO scenarios (slug, name, description)
VALUES
    ('residence', 'Резидентство', 'Оценка путей к ВНЖ и практических требований.'),
    ('citizenship', 'Гражданство', 'Оценка натурализации и сигналов планирования гражданства.'),
    ('digital-nomad', 'Цифровой кочевник', 'Оценка подходящих условий для удалённой работы и временного пребывания.'),
    ('business', 'Бизнес', 'Оценка возможностей регистрации компании и деловой среды.'),
    ('family-relocation', 'Семейная релокация', 'Оценка условий для семейной релокации и потребностей иждивенцев.')
ON CONFLICT (slug) DO UPDATE
SET name = EXCLUDED.name,
    description = EXCLUDED.description,
    is_active = TRUE;
INSERT INTO scenario_criteria (scenario_id, key, label, weight, is_required)
SELECT scenarios.id, criteria.key, criteria.label, criteria.weight, criteria.is_required
FROM scenarios
JOIN (
    VALUES
        ('residence', 'pathway_clarity', 'Понятность пути', 1.50, TRUE),
        ('residence', 'processing_predictability', 'Предсказуемость сроков', 1.00, FALSE),
        ('citizenship', 'timeline', 'Сроки', 1.20, TRUE),
        ('citizenship', 'eligibility_clarity', 'Понятность требований', 1.10, TRUE),
        ('digital-nomad', 'remote_work_fit', 'Пригодность для удалённой работы', 1.40, TRUE),
        ('business', 'company_setup', 'Регистрация компании', 1.30, TRUE),
        ('family-relocation', 'dependent_support', 'Поддержка иждивенцев', 1.30, TRUE)
) AS criteria(scenario_slug, key, label, weight, is_required)
    ON criteria.scenario_slug = scenarios.slug
ON CONFLICT (scenario_id, key) DO UPDATE
SET label = EXCLUDED.label,
    weight = EXCLUDED.weight,
    is_required = EXCLUDED.is_required;
INSERT INTO sources (
    title,
    url,
    source_type,
    publisher,
    country_id,
    locale_id,
    reliability_level,
    accessed_at
)
SELECT
    source_rows.title,
    source_rows.url,
    source_rows.source_type,
    source_rows.publisher,
    countries.id,
    locales.id,
    source_rows.reliability_level,
    CURRENT_DATE
FROM (
    VALUES
        (
            'Россия: официальный placeholder-источник по миграции',
            'https://example.invalid/sources/russia-migration-placeholder',
            'official',
            'Placeholder publisher',
            'russia',
            'en',
            'medium'
        ),
        (
            'Уругвай: официальный placeholder-источник по резидентству',
            'https://example.invalid/sources/uruguay-residence-placeholder',
            'official',
            'Placeholder publisher',
            'uruguay',
            'en',
            'medium'
        ),
        (
            'Региональный placeholder-источник по релокации',
            'https://example.invalid/sources/regional-relocation-placeholder',
            'research',
            'Placeholder research desk',
            NULL,
            'en',
            'low'
        )
) AS source_rows(title, url, source_type, publisher, country_slug, locale_code, reliability_level)
LEFT JOIN countries ON countries.slug = source_rows.country_slug
JOIN locales ON locales.code = source_rows.locale_code
ON CONFLICT (url) DO UPDATE
SET title = EXCLUDED.title,
    source_type = EXCLUDED.source_type,
    publisher = EXCLUDED.publisher,
    country_id = EXCLUDED.country_id,
    locale_id = EXCLUDED.locale_id,
    reliability_level = EXCLUDED.reliability_level,
    accessed_at = EXCLUDED.accessed_at;
INSERT INTO evidence_items (
    source_id,
    country_id,
    title,
    summary,
    url,
    quote,
    evidence_type,
    confidence_level,
    published_at
)
SELECT
    sources.id,
    countries.id,
    evidence_rows.title,
    evidence_rows.summary,
    evidence_rows.url,
    evidence_rows.quote,
    evidence_rows.evidence_type,
    evidence_rows.confidence_level,
    CURRENT_DATE
FROM (
    VALUES
        (
            'russia',
            'https://example.invalid/sources/russia-migration-placeholder',
            'Россия: placeholder-доказательство по миграционной политике',
            'Нейтральное placeholder-доказательство для начальной проверки API.',
            'https://example.invalid/evidence/russia-policy-placeholder',
            'Placeholder-цитата; не является фактическим правовым утверждением.',
            'policy_note',
            'low'
        ),
        (
            'uruguay',
            'https://example.invalid/sources/uruguay-residence-placeholder',
            'Уругвай: placeholder-доказательство по пути к резидентству',
            'Нейтральное placeholder-доказательство для начальной проверки API.',
            'https://example.invalid/evidence/uruguay-residence-placeholder',
            'Placeholder-цитата; не является фактическим правовым утверждением.',
            'policy_note',
            'low'
        ),
        (
            'uruguay',
            'https://example.invalid/sources/regional-relocation-placeholder',
            'Региональное placeholder-доказательство для сравнительного анализа релокации',
            'Черновое сравнительное доказательство для проверки таблиц связей.',
            'https://example.invalid/evidence/regional-comparison-placeholder',
            'Placeholder-цитата; не является фактическим правовым утверждением.',
            'research_note',
            'low'
        )
) AS evidence_rows(
    country_slug,
    source_url,
    title,
    summary,
    url,
    quote,
    evidence_type,
    confidence_level
)
JOIN sources ON sources.url = evidence_rows.source_url
JOIN countries ON countries.slug = evidence_rows.country_slug
WHERE NOT EXISTS (
    SELECT 1 FROM evidence_items WHERE evidence_items.url = evidence_rows.url
);
INSERT INTO legal_signals (
    country_id,
    title,
    summary,
    signal_type,
    sentiment,
    severity,
    status,
    confidence_level,
    effective_date,
    published_at
)
SELECT
    countries.id,
    signal_rows.title,
    signal_rows.summary,
    signal_rows.signal_type,
    signal_rows.sentiment,
    signal_rows.severity,
    signal_rows.status,
    signal_rows.confidence_level,
    CURRENT_DATE,
    CURRENT_DATE
FROM (
    VALUES
        (
            'russia',
            'Черновой административный сигнал по миграции',
            'Placeholder-сигнал для проверки хранения правовых сигналов.',
            'administrative_change',
            'neutral',
            'medium',
            'draft',
            'low'
        ),
        (
            'uruguay',
            'Черновой сигнал по пути к резидентству',
            'Placeholder-сигнал для проверки отслеживания резидентства.',
            'policy',
            'neutral',
            'low',
            'draft',
            'low'
        ),
        (
            'uruguay',
            'Черновой сигнал по бизнес-релокации',
            'Placeholder-сигнал для проверки доказательств бизнес-сценария.',
            'other',
            'mixed',
            'low',
            'draft',
            'low'
        )
) AS signal_rows(
    country_slug,
    title,
    summary,
    signal_type,
    sentiment,
    severity,
    status,
    confidence_level
)
JOIN countries ON countries.slug = signal_rows.country_slug
ON CONFLICT (country_id, title) DO UPDATE
SET summary = EXCLUDED.summary,
    signal_type = EXCLUDED.signal_type,
    sentiment = EXCLUDED.sentiment,
    severity = EXCLUDED.severity,
    status = EXCLUDED.status,
    confidence_level = EXCLUDED.confidence_level,
    effective_date = EXCLUDED.effective_date,
    published_at = EXCLUDED.published_at;
INSERT INTO legal_signal_evidence (legal_signal_id, evidence_item_id)
SELECT legal_signals.id, evidence_items.id
FROM legal_signals
JOIN countries ON countries.id = legal_signals.country_id
JOIN evidence_items ON evidence_items.country_id = countries.id
WHERE legal_signals.status = 'draft'
ON CONFLICT DO NOTHING;
INSERT INTO country_scores (country_id, scenario_id, score, score_label, summary)
SELECT
    countries.id,
    scenarios.id,
    score_rows.score,
    score_rows.score_label,
    score_rows.summary
FROM (
    VALUES
        ('russia', 'residence', 45.00, 'Черновик', 'Placeholder-оценка; не для продакшена.'),
        ('russia', 'citizenship', 40.00, 'Черновик', 'Placeholder-оценка; не для продакшена.'),
        ('russia', 'digital-nomad', 35.00, 'Черновик', 'Placeholder-оценка; не для продакшена.'),
        ('russia', 'business', 42.00, 'Черновик', 'Placeholder-оценка; не для продакшена.'),
        ('russia', 'family-relocation', 38.00, 'Черновик', 'Placeholder-оценка; не для продакшена.'),
        ('uruguay', 'residence', 62.00, 'Черновик', 'Placeholder-оценка; не для продакшена.'),
        ('uruguay', 'citizenship', 58.00, 'Черновик', 'Placeholder-оценка; не для продакшена.'),
        ('uruguay', 'digital-nomad', 64.00, 'Черновик', 'Placeholder-оценка; не для продакшена.'),
        ('uruguay', 'business', 60.00, 'Черновик', 'Placeholder-оценка; не для продакшена.'),
        ('uruguay', 'family-relocation', 63.00, 'Черновик', 'Placeholder-оценка; не для продакшена.')
) AS score_rows(country_slug, scenario_slug, score, score_label, summary)
JOIN countries ON countries.slug = score_rows.country_slug
JOIN scenarios ON scenarios.slug = score_rows.scenario_slug
ON CONFLICT (country_id, scenario_id) DO UPDATE
SET score = EXCLUDED.score,
    score_label = EXCLUDED.score_label,
    summary = EXCLUDED.summary;
INSERT INTO translations (entity_type, entity_id, field_name, locale_id, translated_value, status)
SELECT entity_type, entity_id, field_name, locale_id, translated_value, 'approved'
FROM (
    SELECT 'country', countries.id, 'name', locales.id, 'Россия'
    FROM countries, locales
    WHERE countries.slug = 'russia' AND locales.code = 'ru'
    UNION ALL
    SELECT 'country', countries.id, 'name', locales.id, 'Уругвай'
    FROM countries, locales
    WHERE countries.slug = 'uruguay' AND locales.code = 'ru'
    UNION ALL
    SELECT 'scenario', scenarios.id, 'name', locales.id, 'ВНЖ'
    FROM scenarios, locales
    WHERE scenarios.slug = 'residence' AND locales.code = 'ru'
    UNION ALL
    SELECT 'scenario', scenarios.id, 'name', locales.id, 'Гражданство'
    FROM scenarios, locales
    WHERE scenarios.slug = 'citizenship' AND locales.code = 'ru'
    UNION ALL
    SELECT 'scenario', scenarios.id, 'name', locales.id, 'Цифровой кочевник'
    FROM scenarios, locales
    WHERE scenarios.slug = 'digital-nomad' AND locales.code = 'ru'
    UNION ALL
    SELECT 'scenario', scenarios.id, 'name', locales.id, 'Бизнес'
    FROM scenarios, locales
    WHERE scenarios.slug = 'business' AND locales.code = 'ru'
    UNION ALL
    SELECT 'scenario', scenarios.id, 'name', locales.id, 'Семейная релокация'
    FROM scenarios, locales
    WHERE scenarios.slug = 'family-relocation' AND locales.code = 'ru'
) AS translation_rows(entity_type, entity_id, field_name, locale_id, translated_value)
ON CONFLICT (entity_type, entity_id, field_name, locale_id) DO UPDATE
SET translated_value = EXCLUDED.translated_value,
    status = EXCLUDED.status;
INSERT INTO translation_glossary (
    source_locale_id,
    target_locale_id,
    source_term,
    target_term,
    context
)
SELECT source_locale.id, target_locale.id, 'residence', 'ВНЖ', 'scenario'
FROM locales AS source_locale
JOIN locales AS target_locale ON target_locale.code = 'ru'
WHERE source_locale.code = 'en'
ON CONFLICT (source_locale_id, target_locale_id, source_term, context) DO UPDATE
SET target_term = EXCLUDED.target_term;
