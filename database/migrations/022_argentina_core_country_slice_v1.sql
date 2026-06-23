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
VALUES (
    'argentina',
    'AR',
    'ARG',
    'Argentina',
    'Argentine Republic',
    'Americas',
    'South America',
    'Buenos Aires',
    'ARS'
)
ON CONFLICT (slug) DO UPDATE SET
    iso2 = EXCLUDED.iso2,
    iso3 = EXCLUDED.iso3,
    name = EXCLUDED.name,
    official_name = EXCLUDED.official_name,
    region = EXCLUDED.region,
    subregion = EXCLUDED.subregion,
    capital = EXCLUDED.capital,
    currency_code = EXCLUDED.currency_code,
    is_active = TRUE,
    updated_at = NOW();

INSERT INTO translations (entity_type, entity_id, field_name, locale_id, translated_value, status)
SELECT 'country', c.id, 'name', l.id, 'Аргентина', 'approved'
FROM countries c
CROSS JOIN locales l
WHERE c.slug = 'argentina' AND l.code = 'ru'
ON CONFLICT (entity_type, entity_id, field_name, locale_id) DO UPDATE
SET translated_value = EXCLUDED.translated_value,
    status = EXCLUDED.status;

INSERT INTO country_cards (
    country_id,
    locale,
    executive_summary,
    migration_overview,
    tax_overview,
    cost_of_living_overview,
    business_overview,
    safety_overview,
    legal_signals_summary,
    risk_summary,
    source_summary,
    status
)
SELECT
    c.id,
    cards.locale,
    cards.executive_summary,
    cards.migration_overview,
    cards.tax_overview,
    cards.cost_of_living_overview,
    cards.business_overview,
    cards.safety_overview,
    cards.legal_signals_summary,
    cards.risk_summary,
    cards.source_summary,
    'published'
FROM countries c
CROSS JOIN (
    VALUES
        (
            'en',
            'Argentina is included as an onboarding country for initial residence and lifestyle screening. This card is a baseline data entry and does not constitute legal advice.',
            'Residence planning for Argentina requires verification of current immigration procedures through the Dirección Nacional de Migraciones (DNM). Temporary and permanent residence pathways exist but documentation requirements vary by applicant profile.',
            'Tax obligations in Argentina are subject to significant regulatory change. The AFIP administers federal tax collection. Freelancers and remote workers should verify current monotributo and income tax rules with qualified local advisors.',
            'Cost of living in Buenos Aires varies significantly by neighborhood and lifestyle. Currency conditions, including inflation dynamics, affect day-to-day purchasing power and require ongoing monitoring.',
            'Business formation and self-employment in Argentina involve registration with AFIP and, depending on activity, provincial registration. Banking access for foreigners and currency transfer conditions are material factors to verify before relocating.',
            'Argentina has a moderate safety profile depending on city and neighborhood. Buenos Aires has elevated crime rates in some zones; official government travel advisories should be consulted before relocation.',
            'Legal signals for Argentina are not yet fully onboarded. The country is currently in the screening onboarding phase and initial signals will be added in subsequent blocks.',
            'Primary risks for Argentina include regulatory volatility, currency instability, inflation, and procedural complexity in immigration and tax administration.',
            'Sources are initial baseline records for onboarding purposes. Full source depth will be added in subsequent onboarding blocks.'
        ),
        (
            'ru',
            'Аргентина включена как страна в процессе онбординга для начального скрининга по проживанию и образу жизни. Эта карточка является базовой записью и не является юридической консультацией.',
            'Планирование проживания в Аргентине требует проверки актуальных иммиграционных процедур через Национальное управление по миграции (DNM). Существуют пути временного и постоянного проживания, однако требования к документам зависят от профиля заявителя.',
            'Налоговые обязательства в Аргентине подвержены значительным регуляторным изменениям. AFIP управляет федеральным сбором налогов. Фрилансеры и удалённые работники должны проверять актуальные правила monotributo и НДФЛ у квалифицированных местных консультантов.',
            'Стоимость жизни в Буэнос-Айресе существенно варьируется в зависимости от района и образа жизни. Валютные условия, включая динамику инфляции, влияют на повседневную покупательную способность и требуют постоянного мониторинга.',
            'Создание бизнеса и самозанятость в Аргентине предполагают регистрацию в AFIP и, в зависимости от деятельности, провинциальную регистрацию. Доступ к банковским услугам для иностранцев и валютные условия — существенные факторы для проверки перед релокацией.',
            'Аргентина имеет умеренный профиль безопасности в зависимости от города и района. В Буэнос-Айресе некоторые зоны имеют повышенный уровень преступности; перед релокацией следует ознакомиться с официальными предупреждениями.',
            'Правовые сигналы для Аргентины ещё не полностью добавлены. Страна находится в фазе онбординга, начальные сигналы будут добавлены в последующих блоках.',
            'Основные риски для Аргентины включают волатильность регулирования, нестабильность валюты, инфляцию и процессуальную сложность в иммиграционном и налоговом администрировании.',
            'Источники являются начальными базовыми записями для целей онбординга. Полная глубина источников будет добавлена в последующих блоках.'
        )
) AS cards(
    locale,
    executive_summary,
    migration_overview,
    tax_overview,
    cost_of_living_overview,
    business_overview,
    safety_overview,
    legal_signals_summary,
    risk_summary,
    source_summary
)
WHERE c.slug = 'argentina'
ON CONFLICT (country_id, locale) DO UPDATE SET
    executive_summary = EXCLUDED.executive_summary,
    migration_overview = EXCLUDED.migration_overview,
    tax_overview = EXCLUDED.tax_overview,
    cost_of_living_overview = EXCLUDED.cost_of_living_overview,
    business_overview = EXCLUDED.business_overview,
    safety_overview = EXCLUDED.safety_overview,
    legal_signals_summary = EXCLUDED.legal_signals_summary,
    risk_summary = EXCLUDED.risk_summary,
    source_summary = EXCLUDED.source_summary,
    status = EXCLUDED.status,
    updated_at = NOW();

WITH arg AS (
    SELECT id FROM countries WHERE slug = 'argentina'
)
INSERT INTO sources (
    country_id,
    title,
    url,
    source_type,
    publisher,
    language,
    reliability_level,
    confidence,
    status,
    published_at,
    accessed_at,
    last_checked_at,
    notes
)
SELECT
    arg.id,
    sr.title,
    sr.url,
    sr.source_type,
    sr.publisher,
    sr.language,
    sr.reliability_level,
    sr.confidence,
    'published',
    sr.published_at,
    CURRENT_DATE,
    CURRENT_DATE,
    sr.notes
FROM arg
CROSS JOIN (
    VALUES
        (
            'Dirección Nacional de Migraciones — Residencia en Argentina',
            'https://www.argentina.gob.ar/interior/migraciones',
            'official',
            'Dirección Nacional de Migraciones',
            'es',
            'high',
            'high',
            DATE '2024-01-01',
            'Primary official source for immigration and residence procedures in Argentina.'
        ),
        (
            'AFIP — Administración Federal de Ingresos Públicos',
            'https://www.afip.gob.ar',
            'official',
            'AFIP',
            'es',
            'high',
            'high',
            DATE '2024-01-01',
            'Federal tax authority source for fiscal registration and compliance in Argentina.'
        ),
        (
            'Cancillería Argentina — Visas y requisitos de entrada',
            'https://www.cancilleria.gob.ar/en/tourism-and-travel/visas',
            'official',
            'Cancillería Argentina',
            'en',
            'high',
            'high',
            DATE '2024-01-01',
            'Official visa and entry requirements from the Argentine Ministry of Foreign Affairs.'
        ),
        (
            'INDEC — Instituto Nacional de Estadística y Censos',
            'https://www.indec.gob.ar',
            'official',
            'INDEC',
            'es',
            'high',
            'high',
            DATE '2024-01-01',
            'National statistics institute providing economic and demographic data for Argentina.'
        ),
        (
            'World Bank — Argentina Country Data',
            'https://data.worldbank.org/country/AR',
            'dataset',
            'World Bank',
            'en',
            'high',
            'high',
            DATE '2024-01-01',
            'World Bank country data including economic and governance indicators for Argentina.'
        ),
        (
            'Freedom House — Argentina: Freedom in the World 2024',
            'https://freedomhouse.org/country/argentina/freedom-world/2024',
            'research',
            'Freedom House',
            'en',
            'medium',
            'medium',
            DATE '2024-01-01',
            'Political rights and civil liberties assessment for Argentina, relevant for political risk screening.'
        )
) AS sr(
    title,
    url,
    source_type,
    publisher,
    language,
    reliability_level,
    confidence,
    published_at,
    notes
)
ON CONFLICT (url) DO UPDATE SET
    country_id = EXCLUDED.country_id,
    title = EXCLUDED.title,
    source_type = EXCLUDED.source_type,
    publisher = EXCLUDED.publisher,
    language = EXCLUDED.language,
    reliability_level = EXCLUDED.reliability_level,
    confidence = EXCLUDED.confidence,
    status = EXCLUDED.status,
    published_at = EXCLUDED.published_at,
    accessed_at = EXCLUDED.accessed_at,
    last_checked_at = EXCLUDED.last_checked_at,
    notes = EXCLUDED.notes,
    updated_at = NOW();

INSERT INTO evidence_items (
    id,
    country_id,
    source_id,
    title,
    summary,
    claim,
    excerpt,
    evidence_type,
    confidence,
    confidence_level,
    status,
    published_at
)
SELECT
    ev.ev_id::uuid,
    c.id,
    s.id,
    ev.title,
    ev.summary,
    ev.claim,
    ev.excerpt,
    ev.evidence_type,
    ev.confidence,
    ev.confidence,
    'published',
    DATE '2024-01-15'
FROM countries c
CROSS JOIN (
    VALUES
        (
            'e8a2b1c4-0022-4000-a000-000000000001',
            'https://www.argentina.gob.ar/interior/migraciones',
            'DNM — Argentina residence application overview',
            'The Dirección Nacional de Migraciones (DNM) manages all residence applications in Argentina, including temporary and permanent categories with defined documentation requirements.',
            'Argentina provides formal immigration pathways through the DNM with defined documentation requirements.',
            'La DNM gestiona las solicitudes de residencia temporal y permanente en Argentina.',
            'source_note',
            'high'
        ),
        (
            'e8a2b1c4-0022-4000-a000-000000000002',
            'https://www.afip.gob.ar',
            'AFIP — Federal tax registration for residents and self-employed',
            'AFIP manages federal tax registration including monotributo and income tax regimes. Foreign residents must obtain a CUIL or CUIT identification number for tax compliance.',
            'Tax registration in Argentina requires AFIP enrollment and a CUIL/CUIT identification number.',
            'La inscripción tributaria en AFIP es obligatoria para residentes con actividad económica en Argentina.',
            'source_note',
            'high'
        ),
        (
            'e8a2b1c4-0022-4000-a000-000000000003',
            'https://www.cancilleria.gob.ar/en/tourism-and-travel/visas',
            'Cancillería — Visa categories and entry requirements for Argentina',
            'The Argentine Ministry of Foreign Affairs publishes visa categories and entry requirements, including tourist, residence, and work-related entry options for foreign nationals.',
            'Entry requirements and visa categories for Argentina are published by the Cancillería and subject to regulatory change.',
            'Las categorías de visa y requisitos de entrada están publicados por la Cancillería Argentina.',
            'procedure',
            'high'
        ),
        (
            'e8a2b1c4-0022-4000-a000-000000000004',
            'https://www.indec.gob.ar',
            'INDEC — Economic and demographic indicators for Argentina',
            'INDEC publishes national statistics including CPI, population, and economic activity data relevant for cost-of-living and financial planning screening.',
            'National statistics including inflation and cost indicators for Argentina are maintained by INDEC.',
            'INDEC publica estadísticas nacionales incluyendo IPC y actividad económica relevantes para el screening.',
            'dataset',
            'high'
        ),
        (
            'e8a2b1c4-0022-4000-a000-000000000005',
            'https://data.worldbank.org/country/AR',
            'World Bank — Argentina economic and governance country data',
            'World Bank country profile provides economic indicators for Argentina including GDP growth, inflation, and governance scores relevant for long-term risk assessment.',
            'External economic and governance indicators for Argentina are available through World Bank country data.',
            'Los indicadores económicos y de gobernanza de Argentina están disponibles en el Banco Mundial.',
            'dataset',
            'high'
        ),
        (
            'e8a2b1c4-0022-4000-a000-000000000006',
            'https://freedomhouse.org/country/argentina/freedom-world/2024',
            'Freedom House — Argentina political rights and civil liberties assessment',
            'Freedom House assesses political rights and civil liberties in Argentina annually. The 2024 report is relevant for political risk screening and long-term stability assessment.',
            'Argentina receives a Freedom House rating that is relevant for long-term political risk assessment.',
            'Freedom House evalúa derechos políticos y libertades civiles en Argentina anualmente.',
            'research',
            'medium'
        )
) AS ev(
    ev_id,
    source_url,
    title,
    summary,
    claim,
    excerpt,
    evidence_type,
    confidence
)
JOIN sources s ON s.url = ev.source_url
WHERE c.slug = 'argentina'
ON CONFLICT (id) DO NOTHING;

INSERT INTO translation_units (
    entity_type,
    entity_id,
    field_name,
    original_locale_code,
    source_hash
)
SELECT
    'country_card',
    ru_card.id,
    field_data.field_name,
    'ru',
    ENCODE(DIGEST(field_data.ru_text, 'sha256'), 'hex')
FROM country_cards ru_card
JOIN countries c ON c.id = ru_card.country_id
CROSS JOIN LATERAL (
    VALUES
        ('executive_summary', ru_card.executive_summary),
        ('migration_overview', ru_card.migration_overview),
        ('tax_overview', ru_card.tax_overview),
        ('cost_of_living_overview', ru_card.cost_of_living_overview),
        ('business_overview', ru_card.business_overview),
        ('safety_overview', ru_card.safety_overview),
        ('legal_signals_summary', ru_card.legal_signals_summary),
        ('risk_summary', ru_card.risk_summary),
        ('source_summary', ru_card.source_summary)
) AS field_data(field_name, ru_text)
WHERE ru_card.locale = 'ru'
  AND c.slug = 'argentina'
  AND NULLIF(BTRIM(field_data.ru_text), '') IS NOT NULL
ON CONFLICT (entity_type, entity_id, field_name) DO UPDATE
SET
    source_hash = EXCLUDED.source_hash,
    is_active = TRUE,
    updated_at = NOW();

INSERT INTO translation_variants (
    translation_unit_id,
    locale_code,
    text,
    status,
    method,
    source_locale_code,
    source_hash,
    is_original
)
SELECT
    tu.id,
    'ru',
    field_data.ru_text,
    'original',
    'legacy',
    'ru',
    tu.source_hash,
    TRUE
FROM country_cards ru_card
JOIN countries c ON c.id = ru_card.country_id
JOIN translation_units tu
    ON tu.entity_type = 'country_card'
    AND tu.entity_id = ru_card.id
CROSS JOIN LATERAL (
    VALUES
        ('executive_summary', ru_card.executive_summary),
        ('migration_overview', ru_card.migration_overview),
        ('tax_overview', ru_card.tax_overview),
        ('cost_of_living_overview', ru_card.cost_of_living_overview),
        ('business_overview', ru_card.business_overview),
        ('safety_overview', ru_card.safety_overview),
        ('legal_signals_summary', ru_card.legal_signals_summary),
        ('risk_summary', ru_card.risk_summary),
        ('source_summary', ru_card.source_summary)
) AS field_data(field_name, ru_text)
WHERE ru_card.locale = 'ru'
  AND c.slug = 'argentina'
  AND tu.field_name = field_data.field_name
  AND NULLIF(BTRIM(field_data.ru_text), '') IS NOT NULL
ON CONFLICT (translation_unit_id, locale_code) DO UPDATE
SET
    text = EXCLUDED.text,
    status = EXCLUDED.status,
    source_hash = EXCLUDED.source_hash,
    is_original = EXCLUDED.is_original,
    updated_at = NOW();

INSERT INTO translation_variants (
    translation_unit_id,
    locale_code,
    text,
    status,
    method,
    source_locale_code,
    source_hash,
    is_original
)
SELECT
    tu.id,
    'en',
    field_data.en_text,
    'needs_review',
    'legacy',
    'ru',
    tu.source_hash,
    FALSE
FROM country_cards ru_card
JOIN country_cards en_card
    ON en_card.country_id = ru_card.country_id
    AND en_card.locale = 'en'
JOIN countries c ON c.id = ru_card.country_id
JOIN translation_units tu
    ON tu.entity_type = 'country_card'
    AND tu.entity_id = ru_card.id
CROSS JOIN LATERAL (
    VALUES
        ('executive_summary', en_card.executive_summary),
        ('migration_overview', en_card.migration_overview),
        ('tax_overview', en_card.tax_overview),
        ('cost_of_living_overview', en_card.cost_of_living_overview),
        ('business_overview', en_card.business_overview),
        ('safety_overview', en_card.safety_overview),
        ('legal_signals_summary', en_card.legal_signals_summary),
        ('risk_summary', en_card.risk_summary),
        ('source_summary', en_card.source_summary)
) AS field_data(field_name, en_text)
WHERE ru_card.locale = 'ru'
  AND c.slug = 'argentina'
  AND tu.field_name = field_data.field_name
  AND NULLIF(BTRIM(field_data.en_text), '') IS NOT NULL
ON CONFLICT (translation_unit_id, locale_code) DO NOTHING;
