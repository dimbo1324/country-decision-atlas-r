-- Migration 024: Seeds Argentina's legal timeline evidence: sources, legal signals, evidence items, and legal signal events.
WITH arg AS (SELECT id FROM countries WHERE slug = 'argentina')
INSERT INTO sources (
    country_id, title, url, source_type, publisher, language,
    reliability_level, confidence, status, published_at,
    accessed_at, last_checked_at, notes
)
SELECT
    arg.id,
    sr.title, sr.url, sr.source_type, sr.publisher, sr.language,
    sr.reliability_level, sr.confidence, 'published',
    sr.published_at, CURRENT_DATE, CURRENT_DATE, sr.notes
FROM arg
CROSS JOIN (
    VALUES
        (
            'BCRA — Banco Central de la República Argentina',
            'https://www.bcra.gob.ar/',
            'official',
            'Banco Central de la República Argentina',
            'es',
            'high',
            'high',
            DATE '2024-01-01',
            'Central bank regulatory reference for banking and financial system oversight in Argentina.'
        ),
        (
            'IGJ — Inspección General de Justicia',
            'https://www.argentina.gob.ar/justicia/igj',
            'official',
            'Inspección General de Justicia',
            'es',
            'high',
            'high',
            DATE '2024-01-01',
            'Official source for business registration and corporate legal requirements in Argentina.'
        ),
        (
            'AFIP — Monotributo: Régimen simplificado para pequeños contribuyentes',
            'https://www.afip.gob.ar/monotributo/',
            'official',
            'AFIP',
            'es',
            'high',
            'high',
            DATE '2024-01-01',
            'Official AFIP source for the monotributo simplified tax regime for freelancers and self-employed in Argentina.'
        ),
        (
            'Transparency International — Corruption Perceptions Index 2023',
            'https://www.transparency.org/en/cpi/2023',
            'research',
            'Transparency International',
            'en',
            'high',
            'high',
            DATE '2024-01-15',
            'Transparency International CPI 2023, relevant for corruption risk screening in Argentina.'
        )
) AS sr(
    title, url, source_type, publisher, language,
    reliability_level, confidence, published_at, notes
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

WITH legal_signal_data AS (
    SELECT *
    FROM (
        VALUES
            (
                'https://www.argentina.gob.ar/interior/migraciones',
                'Temporary residence for foreigners requires DNM processing',
                'Временное проживание для иностранцев требует обработки через DNM',
                'Temporary and permanent residence in Argentina is processed through the Dirección Nacional de Migraciones. Documentation requirements are substantial and procedurally complex.',
                'Временное и постоянное проживание в Аргентине оформляется через Национальное управление по миграции. Требования к документам значительны и процессуально сложны.',
                'residence',
                'mixed',
                'medium',
                'mixed',
                'medium',
                '["relocators", "remote_workers", "long_term_residents"]'::jsonb,
                DATE '2024-01-01',
                NULL::date,
                'high'
            ),
            (
                'https://www.cancilleria.gob.ar/en/tourism-and-travel/visas',
                'Argentine citizenship requires two years of legal residence',
                'Гражданство Аргентины требует двух лет законного проживания',
                'Foreign nationals may apply for Argentine citizenship after two years of legal residence. The Cancillería manages nationality-related procedures and documentation.',
                'Иностранные граждане могут подать заявление на гражданство Аргентины после двух лет законного проживания. Канцелярия управляет процедурами и документацией, связанными с гражданством.',
                'citizenship',
                'positive',
                'medium',
                'positive',
                'medium',
                '["long_term_residents", "families"]'::jsonb,
                DATE '2024-01-01',
                NULL::date,
                'high'
            ),
            (
                'https://www.afip.gob.ar/monotributo/',
                'Monotributo simplified tax regime available for freelancers',
                'Режим monotributo доступен для фрилансеров и самозанятых',
                'The AFIP monotributo is a simplified tax regime for small contributors and self-employed individuals. Foreign residents with CUIL or CUIT can enroll, though category and eligibility verification is required.',
                'Monotributo AFIP — упрощённый налоговый режим для малых налогоплательщиков и самозанятых. Иностранные резиденты с CUIL или CUIT могут зарегистрироваться, однако требуется проверка категории и права на применение.',
                'tax',
                'positive',
                'medium',
                'positive',
                'medium',
                '["freelancers", "self_employed", "remote_workers"]'::jsonb,
                DATE '2024-01-01',
                NULL::date,
                'high'
            ),
            (
                'https://www.bcra.gob.ar/',
                'Banking access for foreigners subject to BCRA regulatory conditions',
                'Доступ к банкингу для иностранцев зависит от регулирования BCRA',
                'The BCRA regulates banking and financial services access in Argentina. Foreigners may face restrictions on account opening and currency exchange under current regulatory conditions.',
                'BCRA регулирует доступ к банковским и финансовым услугам в Аргентине. Иностранцы могут столкнуться с ограничениями при открытии счёта и обмене валюты в условиях текущего регулирования.',
                'banking',
                'mixed',
                'high',
                'mixed',
                'high',
                '["relocators", "remote_workers", "business_owners"]'::jsonb,
                DATE '2024-01-01',
                NULL::date,
                'high'
            ),
            (
                'https://www.argentina.gob.ar/justicia/igj',
                'Business registration requires IGJ enrollment and AFIP CUIT',
                'Регистрация бизнеса требует регистрации в IGJ и получения CUIT в AFIP',
                'Companies operating in Argentina must register with the IGJ and obtain a CUIT from AFIP. Procedural complexity and bureaucratic requirements should be verified before committing to business formation.',
                'Компании, работающие в Аргентине, должны зарегистрироваться в IGJ и получить CUIT в AFIP. Процессуальную сложность и бюрократические требования следует проверить до принятия решения о создании бизнеса.',
                'business',
                'mixed',
                'medium',
                'mixed',
                'medium',
                '["business_owners", "self_employed"]'::jsonb,
                DATE '2024-01-01',
                NULL::date,
                'high'
            ),
            (
                'https://data.worldbank.org/country/AR',
                'Political stability and regulatory volatility pose elevated risk',
                'Политическая нестабильность и регуляторная волатильность создают повышенные риски',
                'Argentina faces recurring political instability and significant regulatory volatility. External datasets consistently rate governance and political risk as elevated, requiring ongoing monitoring for long-term relocation decisions.',
                'Аргентина сталкивается с периодической политической нестабильностью и значительной регуляторной волатильностью. Внешние базы данных стабильно оценивают риски управления и политической стабильности как повышенные.',
                'political_risk',
                'negative',
                'high',
                'negative',
                'high',
                '["risk_sensitive_users", "families", "business_owners"]'::jsonb,
                DATE '2024-01-01',
                NULL::date,
                'high'
            )
    ) AS v(
        source_url, title_en, title_ru,
        summary_en, summary_ru,
        signal_type, sentiment, severity,
        impact_direction, impact_level,
        affected_groups, published_date, effective_date, confidence
    )
)
INSERT INTO legal_signals (
    country_id, source_id,
    title, summary,
    title_en, title_ru, summary_en, summary_ru,
    signal_type, sentiment, severity,
    status, confidence_level, confidence,
    impact_direction, impact_level, affected_groups,
    published_date, effective_date, published_at
)
SELECT
    c.id,
    s.id,
    d.title_en,
    d.summary_en,
    d.title_en,
    d.title_ru,
    d.summary_en,
    d.summary_ru,
    d.signal_type,
    d.sentiment,
    d.severity,
    'published',
    d.confidence,
    d.confidence,
    d.impact_direction,
    d.impact_level,
    d.affected_groups,
    d.published_date,
    d.effective_date,
    d.published_date
FROM legal_signal_data d
JOIN countries c ON c.slug = 'argentina'
JOIN sources s ON s.url = d.source_url
ON CONFLICT (country_id, title) DO UPDATE SET
    source_id          = EXCLUDED.source_id,
    summary            = EXCLUDED.summary,
    title_en           = EXCLUDED.title_en,
    title_ru           = EXCLUDED.title_ru,
    summary_en         = EXCLUDED.summary_en,
    summary_ru         = EXCLUDED.summary_ru,
    signal_type        = EXCLUDED.signal_type,
    sentiment          = EXCLUDED.sentiment,
    severity           = EXCLUDED.severity,
    status             = EXCLUDED.status,
    confidence_level   = EXCLUDED.confidence_level,
    confidence         = EXCLUDED.confidence,
    impact_direction   = EXCLUDED.impact_direction,
    impact_level       = EXCLUDED.impact_level,
    affected_groups    = EXCLUDED.affected_groups,
    published_date     = EXCLUDED.published_date,
    effective_date     = EXCLUDED.effective_date,
    published_at       = EXCLUDED.published_at,
    updated_at         = NOW();

WITH evidence_data AS (
    SELECT *
    FROM (
        VALUES
            (
                'https://www.argentina.gob.ar/interior/migraciones',
                'Временное проживание для иностранцев требует обработки через DNM',
                'Argentina DNM residence procedure overview',
                'The DNM manages residence applications including temporary and permanent categories. Processing times and documentation requirements are subject to regulatory changes.',
                'procedure',
                'high',
                DATE '2024-01-01',
                'Residence applications in Argentina are handled by the Dirección Nacional de Migraciones.',
                'La DNM es la autoridad central para la tramitación de residencias en Argentina.'
            ),
            (
                'https://www.argentina.gob.ar/interior/migraciones',
                'Временное проживание для иностранцев требует обработки через DNM',
                'Argentina residence documentation complexity note',
                'Argentina residence applications require substantial documentation including criminal background checks, health certificates, and financial solvency proof. Requirements vary by residency category.',
                'source_note',
                'high',
                DATE '2024-01-01',
                'Documentation requirements for Argentine residence are multi-layered and category-dependent.',
                'Los requisitos documentales para la residencia argentina son complejos y varían por categoría.'
            ),
            (
                'https://www.cancilleria.gob.ar/en/tourism-and-travel/visas',
                'Гражданство Аргентины требует двух лет законного проживания',
                'Argentina citizenship two-year legal residence requirement',
                'Argentine nationality law requires two years of continuous legal residence before citizenship application. The Cancillería administers nationality procedures and required documentation.',
                'legal_basis',
                'high',
                DATE '2024-01-01',
                'Argentine citizenship eligibility requires two years of prior legal residence.',
                'La ciudadanía argentina requiere dos años de residencia legal continua previa a la solicitud.'
            ),
            (
                'https://www.cancilleria.gob.ar/en/tourism-and-travel/visas',
                'Гражданство Аргентины требует двух лет законного проживания',
                'Argentina Cancillería nationality documentation source note',
                'The Cancillería publishes information on entry, visa, and residency pathways as preconditions for nationality applications. Users should verify current requirements directly with the Cancillería.',
                'procedure',
                'high',
                DATE '2024-01-01',
                'Nationality preconditions include valid entry and residency status managed by the Cancillería.',
                'La Cancillería gestiona los requisitos de entrada y residencia previos a la naturalización.'
            ),
            (
                'https://www.afip.gob.ar/monotributo/',
                'Режим monotributo доступен для фрилансеров и самозанятых',
                'Argentina AFIP monotributo enrollment overview',
                'AFIP administers the monotributo simplified tax regime. Freelancers and self-employed individuals with a CUIL or CUIT can enroll in the appropriate category based on annual income and activity type.',
                'procedure',
                'high',
                DATE '2024-01-01',
                'The monotributo regime is the primary simplified tax option for self-employed residents in Argentina.',
                'El monotributo AFIP es el régimen simplificado para autónomos y pequeños contribuyentes.'
            ),
            (
                'https://www.afip.gob.ar/monotributo/',
                'Режим monotributo доступен для фрилансеров и самозанятых',
                'Argentina AFIP CUIL CUIT requirement for tax enrollment',
                'Foreign residents in Argentina must obtain a CUIL or CUIT from AFIP to comply with tax registration requirements and access the monotributo regime.',
                'source_note',
                'high',
                DATE '2024-01-01',
                'CUIL or CUIT is required for all tax-registered individuals and self-employed in Argentina.',
                'El CUIL o CUIT es obligatorio para la inscripción tributaria en AFIP en Argentina.'
            ),
            (
                'https://www.bcra.gob.ar/',
                'Доступ к банкингу для иностранцев зависит от регулирования BCRA',
                'Argentina BCRA banking regulation context for foreigners',
                'The BCRA regulates financial and banking services in Argentina, including currency exchange controls and account access conditions. Foreign residents may face restrictions under active regulatory measures.',
                'source_note',
                'high',
                DATE '2024-01-01',
                'Banking access in Argentina depends on BCRA regulatory conditions, including current currency controls.',
                'El acceso bancario en Argentina depende de las condiciones regulatorias del BCRA, incluyendo restricciones cambiarias.'
            ),
            (
                'https://www.argentina.gob.ar/justicia/igj',
                'Регистрация бизнеса требует регистрации в IGJ и получения CUIT в AFIP',
                'Argentina IGJ business registration requirements overview',
                'Companies formed in Argentina must register with the Inspección General de Justicia and obtain a CUIT from AFIP. The registration process involves notarized documents and procedural compliance steps.',
                'procedure',
                'high',
                DATE '2024-01-01',
                'Business formation in Argentina requires IGJ registration and AFIP CUIT enrollment.',
                'La formación empresarial en Argentina requiere registro en IGJ y CUIT de AFIP.'
            ),
            (
                'https://data.worldbank.org/country/AR',
                'Политическая нестабильность и регуляторная волатильность создают повышенные риски',
                'Argentina World Bank governance and political stability indicators',
                'World Bank governance indicators for Argentina show moderate-to-low scores for political stability and rule of law. These external datasets provide context for long-term relocation risk assessment.',
                'dataset',
                'high',
                DATE '2024-01-01',
                'External governance datasets rate Argentina with elevated political and regulatory risk.',
                'Los indicadores de gobernanza del Banco Mundial sitúan a Argentina con riesgo político y regulatorio elevado.'
            )
    ) AS v(
        source_url,
        legal_signal_title_ru,
        title,
        summary,
        evidence_type,
        confidence,
        published_at,
        claim,
        excerpt
    )
),
resolved AS (
    SELECT
        c.id     AS country_id,
        s.id     AS source_id,
        ls.id    AS legal_signal_id,
        d.title,
        d.summary,
        d.evidence_type,
        d.confidence,
        d.published_at,
        d.claim,
        d.excerpt
    FROM evidence_data d
    JOIN countries c ON c.slug = 'argentina'
    JOIN sources s ON s.url = d.source_url
    JOIN legal_signals ls
        ON ls.country_id = c.id
        AND ls.title_ru = d.legal_signal_title_ru
)
INSERT INTO evidence_items (
    source_id, country_id, legal_signal_id,
    title, summary,
    evidence_type, confidence_level, confidence,
    status, published_at, retrieved_at,
    claim, excerpt
)
SELECT
    r.source_id,
    r.country_id,
    r.legal_signal_id,
    r.title,
    r.summary,
    r.evidence_type,
    r.confidence,
    r.confidence,
    'published',
    r.published_at,
    CURRENT_DATE,
    r.claim,
    r.excerpt
FROM resolved r
WHERE NOT EXISTS (
    SELECT 1
    FROM evidence_items existing
    WHERE existing.country_id = r.country_id
      AND existing.title = r.title
);

INSERT INTO legal_signal_evidence (legal_signal_id, evidence_item_id)
SELECT ls.id, ei.id
FROM legal_signals ls
JOIN countries c ON c.id = ls.country_id
JOIN evidence_items ei ON ei.legal_signal_id = ls.id
WHERE c.slug = 'argentina'
ON CONFLICT (legal_signal_id, evidence_item_id) DO NOTHING;

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
  AND c.slug = 'argentina'
ON CONFLICT (legal_signal_id, event_date, event_type) DO UPDATE
SET
    country_id       = EXCLUDED.country_id,
    impact_direction = EXCLUDED.impact_direction,
    impact_level     = EXCLUDED.impact_level,
    title            = EXCLUDED.title,
    summary          = EXCLUDED.summary,
    source_id        = EXCLUDED.source_id,
    evidence_item_id = EXCLUDED.evidence_item_id,
    affected_groups  = EXCLUDED.affected_groups,
    updated_at       = NOW();

UPDATE country_cards
SET
    legal_signals_summary = 'Argentina has six source-backed legal signals covering residence, citizenship, tax, banking, business registration, and political risk. All signals include timeline events with full source traceability.',
    source_summary        = 'Argentina is supported by 10 published sources covering immigration, taxation, banking, business registration, statistical data, and political risk assessment.',
    updated_at            = NOW()
WHERE country_id = (SELECT id FROM countries WHERE slug = 'argentina')
  AND locale = 'en';

UPDATE country_cards
SET
    legal_signals_summary = 'Аргентина имеет шесть правовых сигналов, подкреплённых источниками, охватывающих проживание, гражданство, налоги, банкинг, регистрацию бизнеса и политические риски. Все сигналы включают события временной шкалы с полной прослеживаемостью источников.',
    source_summary        = 'Аргентина поддерживается 10 опубликованными источниками, охватывающими иммиграцию, налогообложение, банкинг, регистрацию бизнеса, статистические данные и оценку политических рисков.',
    updated_at            = NOW()
WHERE country_id = (SELECT id FROM countries WHERE slug = 'argentina')
  AND locale = 'ru';
