UPDATE sources
SET
    status = 'review',
    notes = COALESCE(notes, 'Removed from public source set because placeholder URLs are not allowed.'),
    updated_at = NOW()
WHERE status = 'published'
  AND LOWER(COALESCE(url, '')) LIKE '%example' || '.invalid%';

WITH source_rows AS (
    SELECT *
    FROM (
        VALUES
            (
                'russia',
                'ConsultantPlus Federal Law on Foreign Citizens',
                'https://www.consultant.ru/document/cons_doc_LAW_37868/',
                'official',
                'ConsultantPlus',
                'ru',
                'high',
                'high',
                DATE '2002-07-25',
                'Primary legal reference for the Russian rules on the status of foreign citizens.'
            ),
            (
                'russia',
                'ConsultantPlus Federal Law on Russian Citizenship',
                'https://www.consultant.ru/document/cons_doc_LAW_445998/',
                'official',
                'ConsultantPlus',
                'ru',
                'high',
                'high',
                DATE '2023-04-28',
                'Primary legal reference for citizenship pathways and status rules.'
            ),
            (
                'russia',
                'Federal Tax Service self-employed tax portal',
                'https://npd.nalog.ru/',
                'official',
                'Federal Tax Service of Russia',
                'ru',
                'high',
                'high',
                NULL,
                'Official FTS portal for the professional income tax regime.'
            ),
            (
                'russia',
                'Federal Tax Service personal income tax page',
                'https://www.nalog.gov.ru/rn77/taxation/taxes/ndfl/',
                'official',
                'Federal Tax Service of Russia',
                'ru',
                'high',
                'high',
                NULL,
                'Official FTS reference for personal income tax.'
            ),
            (
                'russia',
                'Bank of Russia National Payment System',
                'https://www.cbr.ru/eng/psystem/',
                'official',
                'Bank of Russia',
                'en',
                'high',
                'high',
                NULL,
                'Official central bank reference for payment-system oversight.'
            ),
            (
                'russia',
                'Bank of Russia banking sector page',
                'https://www.cbr.ru/eng/banking_sector/',
                'official',
                'Bank of Russia',
                'en',
                'high',
                'high',
                NULL,
                'Official central bank reference for banking-sector supervision.'
            ),
            (
                'russia',
                'World Bank GDP per capita Russia',
                'https://data.worldbank.org/indicator/NY.GDP.PCAP.CD?locations=RU',
                'dataset',
                'World Bank',
                'en',
                'high',
                'high',
                NULL,
                'Country-specific World Bank indicator for GDP per capita.'
            ),
            (
                'russia',
                'World Bank inflation Russia',
                'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=RU',
                'dataset',
                'World Bank',
                'en',
                'high',
                'high',
                NULL,
                'Country-specific World Bank indicator for consumer-price inflation.'
            ),
            (
                'russia',
                'World Bank political stability Russia',
                'https://data.worldbank.org/indicator/PV.EST?locations=RU',
                'dataset',
                'World Bank',
                'en',
                'high',
                'high',
                NULL,
                'Country-specific World Bank governance indicator for political stability.'
            ),
            (
                'russia',
                'Gosuslugi residence-related service form',
                'https://www.gosuslugi.ru/600100/1/form',
                'official',
                'Gosuslugi',
                'ru',
                'medium',
                'medium',
                NULL,
                'Official public-services entry point for a residence-related procedure.'
            ),
            (
                'uruguay',
                'Uruguay temporary legal residence procedure',
                'https://www.gub.uy/tramites/residencia-legal-temporaria',
                'official',
                'Government of Uruguay',
                'es',
                'high',
                'high',
                NULL,
                'Official government procedure page for temporary legal residence.'
            ),
            (
                'uruguay',
                'IMPO Uruguay Migration Law 18250',
                'https://www.impo.com.uy/bases/leyes/18250-2008',
                'official',
                'IMPO Uruguay',
                'es',
                'high',
                'high',
                DATE '2008-01-06',
                'Official legal text for Uruguay migration law.'
            ),
            (
                'uruguay',
                'Uruguay Tax Directorate',
                'https://www.gub.uy/direccion-general-impositiva/',
                'official',
                'Direccion General Impositiva',
                'es',
                'high',
                'high',
                NULL,
                'Official tax authority source for tax administration and guidance.'
            ),
            (
                'uruguay',
                'Uruguay National Statistics Institute',
                'https://www.gub.uy/instituto-nacional-estadistica/',
                'official',
                'Instituto Nacional de Estadistica',
                'es',
                'high',
                'high',
                NULL,
                'Official national statistics source for demographic and economic context.'
            ),
            (
                'uruguay',
                'World Bank GDP per capita Uruguay',
                'https://data.worldbank.org/indicator/NY.GDP.PCAP.CD?locations=UY',
                'dataset',
                'World Bank',
                'en',
                'high',
                'high',
                NULL,
                'Country-specific World Bank indicator for GDP per capita.'
            ),
            (
                'uruguay',
                'World Bank inflation Uruguay',
                'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=UY',
                'dataset',
                'World Bank',
                'en',
                'high',
                'high',
                NULL,
                'Country-specific World Bank indicator for consumer-price inflation.'
            ),
            (
                'uruguay',
                'World Bank political stability Uruguay',
                'https://data.worldbank.org/indicator/PV.EST?locations=UY',
                'dataset',
                'World Bank',
                'en',
                'high',
                'high',
                NULL,
                'Country-specific World Bank governance indicator for political stability.'
            ),
            (
                'uruguay',
                'Uruguay Central Bank financial services supervisor',
                'https://www.bcu.gub.uy/Servicios-Financieros-SSF/Paginas/Default.aspx',
                'official',
                'Central Bank of Uruguay',
                'es',
                'high',
                'high',
                NULL,
                'Official supervisory source for regulated financial services.'
            ),
            (
                'uruguay',
                'World Bank Doing Business Uruguay archive',
                'https://archive.doingbusiness.org/en/data/exploreeconomies/uruguay',
                'dataset',
                'World Bank',
                'en',
                'medium',
                'medium',
                NULL,
                'Archived World Bank business-regulation dataset for Uruguay.'
            ),
            (
                'uruguay',
                'IMPO Constitution of Uruguay',
                'https://www.impo.com.uy/bases/constitucion/1967-1967',
                'official',
                'IMPO Uruguay',
                'es',
                'high',
                'high',
                DATE '1967-02-15',
                'Official constitutional text used for legal-stability context.'
            )
    ) AS rows(
        country_slug,
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
    c.id,
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
FROM source_rows sr
JOIN countries c ON c.slug = sr.country_slug
ON CONFLICT (url) DO UPDATE
SET
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

WITH legal_signal_rows AS (
    SELECT *
    FROM (
        VALUES
            (
                'russia',
                'https://www.consultant.ru/document/cons_doc_LAW_37868/',
                'Foreign-citizen status remains statute-led',
                'Статус иностранцев остается законодательно регулируемым',
                'The legal-status law is the main baseline for residence and stay analysis, so relocation screening should treat procedure and status maintenance as document-heavy.',
                'Закон о правовом положении иностранных граждан остается базовой точкой для оценки проживания и пребывания, поэтому релокационный скрининг должен учитывать высокую документальную нагрузку.',
                'residence',
                'mixed',
                'high',
                'mixed',
                'high',
                '["relocators", "long_term_residents"]'::jsonb,
                DATE '2026-06-19',
                DATE '2002-07-25',
                'high'
            ),
            (
                'russia',
                'https://www.consultant.ru/document/cons_doc_LAW_445998/',
                'Citizenship pathway needs separate legal review',
                'Гражданство требует отдельной правовой проверки',
                'The citizenship law creates a separate decision layer after residence planning, making long-term status less suitable for quick self-service assumptions.',
                'Закон о гражданстве формирует отдельный слой решения после планирования проживания, поэтому долгосрочный статус хуже подходит для быстрых самостоятельных предположений.',
                'citizenship',
                'mixed',
                'high',
                'mixed',
                'high',
                '["long_term_residents", "families"]'::jsonb,
                DATE '2026-06-19',
                DATE '2023-04-28',
                'high'
            ),
            (
                'russia',
                'https://npd.nalog.ru/',
                'Professional income tax has official digital guidance',
                'Налог на профессиональный доход имеет официальный цифровой контур',
                'The official self-employed tax portal improves source visibility for small-scale independent work, while eligibility still requires case-specific tax review.',
                'Официальный портал НПД повышает прозрачность для небольшой самостоятельной деятельности, но применимость режима все равно требует индивидуальной налоговой проверки.',
                'tax',
                'positive',
                'medium',
                'positive',
                'medium',
                '["freelancers", "self_employed"]'::jsonb,
                DATE '2026-06-19',
                NULL,
                'high'
            ),
            (
                'russia',
                'https://www.cbr.ru/eng/psystem/',
                'Payment-system context should be checked before relocation',
                'Платежную инфраструктуру нужно проверять до переезда',
                'Central-bank payment-system materials are relevant for banking readiness, especially where card access, transfers and account usability affect daily life.',
                'Материалы Банка России по платежной системе важны для банковской готовности, особенно когда доступ к картам, переводам и счетам влияет на повседневную жизнь.',
                'banking',
                'neutral',
                'medium',
                'mixed',
                'medium',
                '["relocators", "remote_workers", "business_owners"]'::jsonb,
                DATE '2026-06-19',
                NULL,
                'high'
            ),
            (
                'russia',
                'https://data.worldbank.org/indicator/PV.EST?locations=RU',
                'Political-stability dataset adds external risk context',
                'Показатель политической стабильности добавляет внешний риск-контекст',
                'World Bank governance data gives an external dataset for risk scoring, but it should complement legal and practical checks rather than replace them.',
                'Данные Всемирного банка по управлению дают внешний набор данных для риск-оценки, но должны дополнять правовые и практические проверки, а не заменять их.',
                'political_risk',
                'negative',
                'high',
                'negative',
                'high',
                '["risk_sensitive_users", "families", "business_owners"]'::jsonb,
                DATE '2026-06-19',
                NULL,
                'high'
            ),
            (
                'uruguay',
                'https://www.gub.uy/tramites/residencia-legal-temporaria',
                'Temporary legal residence has an official procedure page',
                'Временная легальная резиденция описана на официальной странице',
                'The official temporary residence procedure improves first-step relocation clarity and gives users a concrete source for eligibility and filing review.',
                'Официальная процедура временной резиденции повышает ясность первого шага релокации и дает пользователям конкретный источник для проверки условий и подачи.',
                'residence',
                'positive',
                'medium',
                'positive',
                'medium',
                '["relocators", "remote_workers"]'::jsonb,
                DATE '2026-06-19',
                NULL,
                'high'
            ),
            (
                'uruguay',
                'https://www.impo.com.uy/bases/leyes/18250-2008',
                'Migration law provides a stable statutory baseline',
                'Миграционный закон дает стабильную правовую базу',
                'The official migration law is a primary anchor for residence analysis and supports stronger confidence than a procedure-only source set.',
                'Официальный миграционный закон является первичной опорой для анализа резиденции и повышает уверенность по сравнению с набором только процедурных источников.',
                'migration',
                'positive',
                'medium',
                'positive',
                'medium',
                '["relocators", "long_term_residents", "families"]'::jsonb,
                DATE '2026-06-19',
                DATE '2008-01-06',
                'high'
            ),
            (
                'uruguay',
                'https://www.gub.uy/direccion-general-impositiva/',
                'Tax administration has a dedicated official source',
                'Налоговое администрирование имеет отдельный официальный источник',
                'The DGI source strengthens tax due-diligence coverage for residence, freelance and company planning.',
                'Источник DGI усиливает налоговую проверку для резиденции, фриланса и планирования компании.',
                'tax',
                'positive',
                'medium',
                'positive',
                'medium',
                '["tax_residents", "freelancers", "business_owners"]'::jsonb,
                DATE '2026-06-19',
                NULL,
                'high'
            ),
            (
                'uruguay',
                'https://www.bcu.gub.uy/Servicios-Financieros-SSF/Paginas/Default.aspx',
                'Financial services supervision supports banking checks',
                'Надзор за финансовыми услугами помогает проверять банковские вопросы',
                'The central-bank supervisor source gives a public reference point for financial-sector oversight and account-readiness research.',
                'Источник надзора центрального банка дает публичную точку опоры для оценки финансового сектора и готовности банковских услуг.',
                'banking',
                'positive',
                'medium',
                'positive',
                'medium',
                '["relocators", "remote_workers", "business_owners"]'::jsonb,
                DATE '2026-06-19',
                NULL,
                'high'
            ),
            (
                'uruguay',
                'https://www.impo.com.uy/bases/constitucion/1967-1967',
                'Constitutional text anchors rule-of-law context',
                'Конституционный текст закрепляет контекст верховенства права',
                'The official constitutional text adds a primary legal source for legal-stability screening, alongside rule-of-law and freedom datasets.',
                'Официальный конституционный текст добавляет первичный правовой источник для оценки правовой стабильности наряду с индексами верховенства права и свободы.',
                'rule_of_law',
                'positive',
                'medium',
                'positive',
                'medium',
                '["risk_sensitive_users", "families", "business_owners"]'::jsonb,
                DATE '2026-06-19',
                DATE '1967-02-15',
                'high'
            )
    ) AS rows(
        country_slug,
        source_url,
        title_en,
        title_ru,
        summary_en,
        summary_ru,
        signal_type,
        sentiment,
        severity,
        impact_direction,
        impact_level,
        affected_groups,
        published_date,
        effective_date,
        confidence
    )
)
INSERT INTO legal_signals (
    country_id,
    source_id,
    title,
    summary,
    title_en,
    title_ru,
    summary_en,
    summary_ru,
    signal_type,
    sentiment,
    severity,
    status,
    confidence_level,
    confidence,
    impact_direction,
    impact_level,
    affected_groups,
    published_date,
    effective_date,
    published_at
)
SELECT
    c.id,
    s.id,
    lsr.title_en,
    lsr.summary_en,
    lsr.title_en,
    lsr.title_ru,
    lsr.summary_en,
    lsr.summary_ru,
    lsr.signal_type,
    lsr.sentiment,
    lsr.severity,
    'published',
    lsr.confidence,
    lsr.confidence,
    lsr.impact_direction,
    lsr.impact_level,
    lsr.affected_groups,
    lsr.published_date,
    lsr.effective_date,
    lsr.published_date
FROM legal_signal_rows lsr
JOIN countries c ON c.slug = lsr.country_slug
JOIN sources s ON s.url = lsr.source_url
ON CONFLICT (country_id, title) DO UPDATE
SET
    source_id = EXCLUDED.source_id,
    summary = EXCLUDED.summary,
    title_en = EXCLUDED.title_en,
    title_ru = EXCLUDED.title_ru,
    summary_en = EXCLUDED.summary_en,
    summary_ru = EXCLUDED.summary_ru,
    signal_type = EXCLUDED.signal_type,
    sentiment = EXCLUDED.sentiment,
    severity = EXCLUDED.severity,
    status = EXCLUDED.status,
    confidence_level = EXCLUDED.confidence_level,
    confidence = EXCLUDED.confidence,
    impact_direction = EXCLUDED.impact_direction,
    impact_level = EXCLUDED.impact_level,
    affected_groups = EXCLUDED.affected_groups,
    published_date = EXCLUDED.published_date,
    effective_date = EXCLUDED.effective_date,
    published_at = EXCLUDED.published_at,
    updated_at = NOW();

WITH evidence_rows AS (
    SELECT *
    FROM (
        VALUES
            ('russia', 'https://www.consultant.ru/document/cons_doc_LAW_37868/', 'Foreign-citizen status remains statute-led', 'Russia foreign citizen law baseline', 'The legal-status law is a primary source for stay, residence and status obligations.', 'https://www.consultant.ru/document/cons_doc_LAW_37868/', 'The source should be reviewed before assuming a simple residence path.', 'legal_basis', 'high', DATE '2026-06-19', 'Foreign-citizen status in Russia is governed through a dedicated federal law.', 'Primary law source used for residence and status screening.'),
            ('russia', 'https://www.gosuslugi.ru/600100/1/form', 'Foreign-citizen status remains statute-led', 'Russia residence process public-services touchpoint', 'The public-services form gives practical process context for residence-related administration.', 'https://www.gosuslugi.ru/600100/1/form', 'The procedure layer should be checked against the statutory baseline.', 'procedure', 'medium', DATE '2026-06-19', 'Residence planning includes public-service procedure checks as well as legal status rules.', 'Government service source used for administrative process screening.'),
            ('russia', 'https://evisa.kdmid.ru/', 'Foreign-citizen status remains statute-led', 'Russia electronic visa source', 'The MFA e-visa portal is useful for short-stay entry checks, not a substitute for residence advice.', 'https://evisa.kdmid.ru/', 'Entry permission and residence status are separate screening layers.', 'procedure', 'high', DATE '2026-06-19', 'Short-stay entry checks should be separated from residence analysis.', 'Official e-visa source used for entry-context evidence.'),
            ('russia', 'https://www.consultant.ru/document/cons_doc_LAW_445998/', 'Citizenship pathway needs separate legal review', 'Russia citizenship law baseline', 'The citizenship law provides a separate legal framework for naturalisation and citizenship status.', 'https://www.consultant.ru/document/cons_doc_LAW_445998/', 'Citizenship analysis should not be inferred from residence score alone.', 'legal_basis', 'high', DATE '2026-06-19', 'Russian citizenship status is governed by a dedicated federal citizenship law.', 'Primary citizenship source used for long-term status screening.'),
            ('russia', 'https://www.consultant.ru/document/cons_doc_LAW_37868/', 'Citizenship pathway needs separate legal review', 'Russia residence-to-status dependency', 'Residence and foreign-citizen status rules remain relevant before any citizenship pathway is assessed.', 'https://www.consultant.ru/document/cons_doc_LAW_37868/', 'The long-term path starts with a separate residence compliance layer.', 'legal_basis', 'high', DATE '2026-06-19', 'Long-term status screening depends on both residence and citizenship legal layers.', 'Primary residence-law source used as a dependency for citizenship screening.'),
            ('russia', 'https://data.worldbank.org/indicator/PV.EST?locations=RU', 'Citizenship pathway needs separate legal review', 'Russia long-term risk context', 'Political-stability data adds risk context for long-horizon decisions.', 'https://data.worldbank.org/indicator/PV.EST?locations=RU', 'Long-term status should consider governance risk indicators.', 'dataset', 'high', DATE '2026-06-19', 'Long-term planning should incorporate external governance data.', 'World Bank governance indicator used for risk context.'),
            ('russia', 'https://npd.nalog.ru/', 'Professional income tax has official digital guidance', 'Russia self-employed tax portal evidence', 'The FTS portal gives an official source for professional income tax screening.', 'https://npd.nalog.ru/', 'Eligibility and tax-residency interaction still need case review.', 'tax', 'high', DATE '2026-06-19', 'Professional income tax has an official digital information source.', 'Official FTS source used for self-employment screening.'),
            ('russia', 'https://www.nalog.gov.ru/rn77/taxation/taxes/ndfl/', 'Professional income tax has official digital guidance', 'Russia personal income tax evidence', 'The FTS personal-income-tax page is relevant for individual tax exposure.', 'https://www.nalog.gov.ru/rn77/taxation/taxes/ndfl/', 'Personal tax treatment should be checked alongside any special regime.', 'tax', 'high', DATE '2026-06-19', 'Personal income tax remains a separate source-backed screening item.', 'Official FTS tax source used for individual tax screening.'),
            ('russia', 'https://www.cbr.ru/eng/banking_sector/', 'Professional income tax has official digital guidance', 'Russia banking context for freelancers', 'Banking-sector supervision context matters for freelancers and small business users.', 'https://www.cbr.ru/eng/banking_sector/', 'Tax planning should be paired with banking-readiness checks.', 'banking', 'high', DATE '2026-06-19', 'Independent work planning also depends on banking usability.', 'Central-bank source used for financial-operability context.'),
            ('russia', 'https://www.cbr.ru/eng/psystem/', 'Payment-system context should be checked before relocation', 'Russia payment-system evidence', 'The central bank payment-system page supports screening of card, transfer and payment usability.', 'https://www.cbr.ru/eng/psystem/', 'Payment infrastructure can affect daily relocation feasibility.', 'banking', 'high', DATE '2026-06-19', 'Relocation screening should include payment-system readiness.', 'Central-bank source used for payment-system evidence.'),
            ('russia', 'https://www.cbr.ru/eng/banking_sector/', 'Payment-system context should be checked before relocation', 'Russia banking-sector evidence', 'The banking-sector source supports financial-system due diligence.', 'https://www.cbr.ru/eng/banking_sector/', 'Account access and regulated banking context should be checked early.', 'banking', 'high', DATE '2026-06-19', 'Banking-sector supervision is relevant for daily financial access.', 'Central-bank source used for banking-sector evidence.'),
            ('russia', 'https://www.nalog.gov.ru/eng/', 'Payment-system context should be checked before relocation', 'Russia financial administration evidence', 'The FTS source adds public-administration context for financial and tax workflows.', 'https://www.nalog.gov.ru/eng/', 'Financial readiness includes tax-administration touchpoints.', 'tax', 'high', DATE '2026-06-19', 'Tax and banking workflows interact in practical relocation planning.', 'Official tax source used for financial administration context.'),
            ('russia', 'https://data.worldbank.org/indicator/PV.EST?locations=RU', 'Political-stability dataset adds external risk context', 'Russia political stability dataset evidence', 'The World Bank political-stability indicator provides external dataset input for risk scoring.', 'https://data.worldbank.org/indicator/PV.EST?locations=RU', 'External governance datasets should be visible in risk-sensitive decisions.', 'dataset', 'high', DATE '2026-06-19', 'Political-stability data is relevant for safety and legal-stability scoring.', 'World Bank governance source used for political-risk evidence.'),
            ('russia', 'https://freedomhouse.org/country/russia/freedom-world/2026', 'Political-stability dataset adds external risk context', 'Russia Freedom House evidence', 'The Freedom House profile adds an external civil and political rights source.', 'https://freedomhouse.org/country/russia/freedom-world/2026', 'Rights and freedoms data should inform risk warnings.', 'research', 'medium', DATE '2026-06-19', 'External freedom assessments are part of the risk evidence set.', 'Freedom House source used for safety and freedom context.'),
            ('russia', 'https://worldjusticeproject.org/rule-of-law-index/downloads/2025/WJPIndex2025.pdf', 'Political-stability dataset adds external risk context', 'Russia rule-of-law evidence', 'The WJP dataset adds rule-of-law context for legal-stability scoring.', 'https://worldjusticeproject.org/rule-of-law-index/downloads/2025/WJPIndex2025.pdf', 'Rule-of-law context should be visible in long-term risk scoring.', 'dataset', 'high', DATE '2026-06-19', 'Rule-of-law evidence complements political-stability data.', 'WJP source used for legal-stability evidence.'),
            ('uruguay', 'https://www.gub.uy/tramites/residencia-legal-temporaria', 'Temporary legal residence has an official procedure page', 'Uruguay temporary residence procedure evidence', 'The official procedure page supports first-step residence screening.', 'https://www.gub.uy/tramites/residencia-legal-temporaria', 'Users can start from a concrete government procedure source.', 'procedure', 'high', DATE '2026-06-19', 'Temporary residence has an official government procedure page.', 'Official procedure source used for relocation screening.'),
            ('uruguay', 'https://www.gub.uy/tramites/residencia-legal-permanente', 'Temporary legal residence has an official procedure page', 'Uruguay permanent residence procedure evidence', 'The permanent residence procedure gives a related long-term status source.', 'https://www.gub.uy/tramites/residencia-legal-permanente', 'Temporary and permanent status should be considered separately.', 'procedure', 'high', DATE '2026-06-19', 'Residence planning can compare temporary and permanent procedure sources.', 'Official procedure source used for long-term status context.'),
            ('uruguay', 'https://www.gub.uy/direccion-nacional-migracion/', 'Temporary legal residence has an official procedure page', 'Uruguay migration authority evidence', 'The migration authority source supports routing of residence-related checks.', 'https://www.gub.uy/direccion-nacional-migracion/', 'Authority-level source coverage improves traceability.', 'procedure', 'high', DATE '2026-06-19', 'Residence procedure checks should link back to the migration authority.', 'Official migration authority source used for process context.'),
            ('uruguay', 'https://www.impo.com.uy/bases/leyes/18250-2008', 'Migration law provides a stable statutory baseline', 'Uruguay migration law evidence', 'Migration Law 18250 provides the statutory basis for migration and residence analysis.', 'https://www.impo.com.uy/bases/leyes/18250-2008', 'Procedure sources should be read alongside the statute.', 'legal_basis', 'high', DATE '2026-06-19', 'Uruguay migration screening has an official statutory anchor.', 'Official legal source used for migration-law evidence.'),
            ('uruguay', 'https://www.gub.uy/ministerio-interior/comunicacion/publicaciones/types-of-residencies-in-uruguay', 'Migration law provides a stable statutory baseline', 'Uruguay residence-type overview evidence', 'The Ministry of Interior overview helps distinguish residence categories.', 'https://www.gub.uy/ministerio-interior/comunicacion/publicaciones/types-of-residencies-in-uruguay', 'Residence categories should not be collapsed into one generic path.', 'procedure', 'high', DATE '2026-06-19', 'Residence-type guidance improves decision-oriented summaries.', 'Official overview source used for category screening.'),
            ('uruguay', 'https://www.impo.com.uy/bases/constitucion/1967-1967', 'Migration law provides a stable statutory baseline', 'Uruguay constitutional context evidence', 'The constitution provides primary legal context for long-term stability analysis.', 'https://www.impo.com.uy/bases/constitucion/1967-1967', 'Migration analysis benefits from a broader legal-stability source.', 'legal_basis', 'high', DATE '2026-06-19', 'Legal-stability screening can link to constitutional text.', 'Official constitutional source used for legal context.'),
            ('uruguay', 'https://www.gub.uy/direccion-general-impositiva/', 'Tax administration has a dedicated official source', 'Uruguay tax authority evidence', 'The DGI source is the main tax-administration anchor for user screening.', 'https://www.gub.uy/direccion-general-impositiva/', 'Tax planning should be checked against official DGI materials.', 'tax', 'high', DATE '2026-06-19', 'Uruguay tax administration has an official source.', 'Official tax source used for residence and business screening.'),
            ('uruguay', 'https://www.gub.uy/ministerio-economia-finanzas/', 'Tax administration has a dedicated official source', 'Uruguay economy ministry evidence', 'The Ministry of Economy and Finance source adds official fiscal context.', 'https://www.gub.uy/ministerio-economia-finanzas/', 'Tax and fiscal checks should use ministry-level sources where relevant.', 'tax', 'high', DATE '2026-06-19', 'Fiscal context supports tax and cost-of-living screening.', 'Official ministry source used for fiscal context.'),
            ('uruguay', 'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=UY', 'Tax administration has a dedicated official source', 'Uruguay inflation dataset evidence', 'The inflation indicator adds external context for cost and tax planning.', 'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=UY', 'Cost planning should include dataset-backed inflation context.', 'dataset', 'high', DATE '2026-06-19', 'Inflation data supports cost-of-living screening.', 'World Bank source used for cost context.'),
            ('uruguay', 'https://www.bcu.gub.uy/Servicios-Financieros-SSF/Paginas/Default.aspx', 'Financial services supervision supports banking checks', 'Uruguay financial supervisor evidence', 'The central-bank supervisor source supports financial-services due diligence.', 'https://www.bcu.gub.uy/Servicios-Financieros-SSF/Paginas/Default.aspx', 'Banking readiness should include regulated-sector checks.', 'banking', 'high', DATE '2026-06-19', 'Financial supervision data is relevant for account-readiness screening.', 'Central-bank source used for banking evidence.'),
            ('uruguay', 'https://www.bcu.gub.uy/', 'Financial services supervision supports banking checks', 'Uruguay central bank evidence', 'The central bank source anchors monetary and banking context.', 'https://www.bcu.gub.uy/', 'Banking checks should use the central-bank source family.', 'banking', 'high', DATE '2026-06-19', 'Central-bank source coverage strengthens financial-system context.', 'Central-bank source used for institutional evidence.'),
            ('uruguay', 'https://archive.doingbusiness.org/en/data/exploreeconomies/uruguay', 'Financial services supervision supports banking checks', 'Uruguay business-regulation archive evidence', 'The Doing Business archive provides historical business-regulation context.', 'https://archive.doingbusiness.org/en/data/exploreeconomies/uruguay', 'Business setup screening should distinguish archived dataset context from current legal advice.', 'dataset', 'medium', DATE '2026-06-19', 'Archived business-regulation data remains useful as background context.', 'World Bank archive source used for business-context evidence.'),
            ('uruguay', 'https://www.impo.com.uy/bases/constitucion/1967-1967', 'Constitutional text anchors rule-of-law context', 'Uruguay constitution evidence', 'The constitution is a primary source for legal-stability context.', 'https://www.impo.com.uy/bases/constitucion/1967-1967', 'Constitutional source coverage supports rule-of-law screening.', 'legal_basis', 'high', DATE '2026-06-19', 'Rule-of-law analysis should include primary legal text.', 'Official constitutional source used for legal-stability evidence.'),
            ('uruguay', 'https://worldjusticeproject.org/rule-of-law-index/global/2025', 'Constitutional text anchors rule-of-law context', 'Uruguay rule-of-law index evidence', 'The WJP global index adds comparative rule-of-law context.', 'https://worldjusticeproject.org/rule-of-law-index/global/2025', 'Comparative rule-of-law data complements primary legal text.', 'dataset', 'high', DATE '2026-06-19', 'Legal-stability screening should pair primary law with comparative datasets.', 'WJP source used for comparative legal-stability evidence.'),
            ('uruguay', 'https://freedomhouse.org/country/uruguay/freedom-world/2024', 'Constitutional text anchors rule-of-law context', 'Uruguay freedom profile evidence', 'The Freedom House country profile adds external political-rights context.', 'https://freedomhouse.org/country/uruguay/freedom-world/2024', 'Rights and freedom sources should be visible in risk scoring.', 'research', 'medium', DATE '2026-06-19', 'Freedom assessments complement legal-stability evidence.', 'Freedom House source used for risk context.')
    ) AS rows(
        country_slug,
        source_url,
        legal_signal_title,
        title,
        summary,
        url,
        quote,
        evidence_type,
        confidence,
        published_at,
        claim,
        excerpt
    )
),
resolved_evidence_rows AS (
    SELECT
        c.id AS country_id,
        s.id AS source_id,
        ls.id AS legal_signal_id,
        er.title,
        er.summary,
        er.url,
        er.quote,
        er.evidence_type,
        er.confidence,
        er.published_at,
        er.claim,
        er.excerpt
    FROM evidence_rows er
    JOIN countries c ON c.slug = er.country_slug
    JOIN sources s ON s.url = er.source_url
    JOIN legal_signals ls
        ON ls.country_id = c.id
        AND ls.title = er.legal_signal_title
)
INSERT INTO evidence_items (
    source_id,
    country_id,
    legal_signal_id,
    title,
    summary,
    url,
    quote,
    evidence_type,
    confidence_level,
    confidence,
    status,
    published_at,
    retrieved_at,
    claim,
    excerpt
)
SELECT
    rer.source_id,
    rer.country_id,
    rer.legal_signal_id,
    rer.title,
    rer.summary,
    rer.url,
    rer.quote,
    rer.evidence_type,
    rer.confidence,
    rer.confidence,
    'published',
    rer.published_at,
    CURRENT_DATE,
    rer.claim,
    rer.excerpt
FROM resolved_evidence_rows rer
WHERE NOT EXISTS (
    SELECT 1
    FROM evidence_items existing
    WHERE existing.country_id = rer.country_id
      AND existing.title = rer.title
);

WITH evidence_rows AS (
    SELECT *
    FROM (
        VALUES
            ('russia', 'https://www.consultant.ru/document/cons_doc_LAW_37868/', 'Foreign-citizen status remains statute-led', 'Russia foreign citizen law baseline', 'The legal-status law is a primary source for stay, residence and status obligations.', 'https://www.consultant.ru/document/cons_doc_LAW_37868/', 'The source should be reviewed before assuming a simple residence path.', 'legal_basis', 'high', DATE '2026-06-19', 'Foreign-citizen status in Russia is governed through a dedicated federal law.', 'Primary law source used for residence and status screening.'),
            ('russia', 'https://www.gosuslugi.ru/600100/1/form', 'Foreign-citizen status remains statute-led', 'Russia residence process public-services touchpoint', 'The public-services form gives practical process context for residence-related administration.', 'https://www.gosuslugi.ru/600100/1/form', 'The procedure layer should be checked against the statutory baseline.', 'procedure', 'medium', DATE '2026-06-19', 'Residence planning includes public-service procedure checks as well as legal status rules.', 'Government service source used for administrative process screening.'),
            ('russia', 'https://evisa.kdmid.ru/', 'Foreign-citizen status remains statute-led', 'Russia electronic visa source', 'The MFA e-visa portal is useful for short-stay entry checks, not a substitute for residence advice.', 'https://evisa.kdmid.ru/', 'Entry permission and residence status are separate screening layers.', 'procedure', 'high', DATE '2026-06-19', 'Short-stay entry checks should be separated from residence analysis.', 'Official e-visa source used for entry-context evidence.'),
            ('russia', 'https://www.consultant.ru/document/cons_doc_LAW_445998/', 'Citizenship pathway needs separate legal review', 'Russia citizenship law baseline', 'The citizenship law provides a separate legal framework for naturalisation and citizenship status.', 'https://www.consultant.ru/document/cons_doc_LAW_445998/', 'Citizenship analysis should not be inferred from residence score alone.', 'legal_basis', 'high', DATE '2026-06-19', 'Russian citizenship status is governed by a dedicated federal citizenship law.', 'Primary citizenship source used for long-term status screening.'),
            ('russia', 'https://www.consultant.ru/document/cons_doc_LAW_37868/', 'Citizenship pathway needs separate legal review', 'Russia residence-to-status dependency', 'Residence and foreign-citizen status rules remain relevant before any citizenship pathway is assessed.', 'https://www.consultant.ru/document/cons_doc_LAW_37868/', 'The long-term path starts with a separate residence compliance layer.', 'legal_basis', 'high', DATE '2026-06-19', 'Long-term status screening depends on both residence and citizenship legal layers.', 'Primary residence-law source used as a dependency for citizenship screening.'),
            ('russia', 'https://data.worldbank.org/indicator/PV.EST?locations=RU', 'Citizenship pathway needs separate legal review', 'Russia long-term risk context', 'Political-stability data adds risk context for long-horizon decisions.', 'https://data.worldbank.org/indicator/PV.EST?locations=RU', 'Long-term status should consider governance risk indicators.', 'dataset', 'high', DATE '2026-06-19', 'Long-term planning should incorporate external governance data.', 'World Bank governance indicator used for risk context.'),
            ('russia', 'https://npd.nalog.ru/', 'Professional income tax has official digital guidance', 'Russia self-employed tax portal evidence', 'The FTS portal gives an official source for professional income tax screening.', 'https://npd.nalog.ru/', 'Eligibility and tax-residency interaction still need case review.', 'tax', 'high', DATE '2026-06-19', 'Professional income tax has an official digital information source.', 'Official FTS source used for self-employment screening.'),
            ('russia', 'https://www.nalog.gov.ru/rn77/taxation/taxes/ndfl/', 'Professional income tax has official digital guidance', 'Russia personal income tax evidence', 'The FTS personal-income-tax page is relevant for individual tax exposure.', 'https://www.nalog.gov.ru/rn77/taxation/taxes/ndfl/', 'Personal tax treatment should be checked alongside any special regime.', 'tax', 'high', DATE '2026-06-19', 'Personal income tax remains a separate source-backed screening item.', 'Official FTS tax source used for individual tax screening.'),
            ('russia', 'https://www.cbr.ru/eng/banking_sector/', 'Professional income tax has official digital guidance', 'Russia banking context for freelancers', 'Banking-sector supervision context matters for freelancers and small business users.', 'https://www.cbr.ru/eng/banking_sector/', 'Tax planning should be paired with banking-readiness checks.', 'banking', 'high', DATE '2026-06-19', 'Independent work planning also depends on banking usability.', 'Central-bank source used for financial-operability context.'),
            ('russia', 'https://www.cbr.ru/eng/psystem/', 'Payment-system context should be checked before relocation', 'Russia payment-system evidence', 'The central bank payment-system page supports screening of card, transfer and payment usability.', 'https://www.cbr.ru/eng/psystem/', 'Payment infrastructure can affect daily relocation feasibility.', 'banking', 'high', DATE '2026-06-19', 'Relocation screening should include payment-system readiness.', 'Central-bank source used for payment-system evidence.'),
            ('russia', 'https://www.cbr.ru/eng/banking_sector/', 'Payment-system context should be checked before relocation', 'Russia banking-sector evidence', 'The banking-sector source supports financial-system due diligence.', 'https://www.cbr.ru/eng/banking_sector/', 'Account access and regulated banking context should be checked early.', 'banking', 'high', DATE '2026-06-19', 'Banking-sector supervision is relevant for daily financial access.', 'Central-bank source used for banking-sector evidence.'),
            ('russia', 'https://www.nalog.gov.ru/eng/', 'Payment-system context should be checked before relocation', 'Russia financial administration evidence', 'The FTS source adds public-administration context for financial and tax workflows.', 'https://www.nalog.gov.ru/eng/', 'Financial readiness includes tax-administration touchpoints.', 'tax', 'high', DATE '2026-06-19', 'Tax and banking workflows interact in practical relocation planning.', 'Official tax source used for financial administration context.'),
            ('russia', 'https://data.worldbank.org/indicator/PV.EST?locations=RU', 'Political-stability dataset adds external risk context', 'Russia political stability dataset evidence', 'The World Bank political-stability indicator provides external dataset input for risk scoring.', 'https://data.worldbank.org/indicator/PV.EST?locations=RU', 'External governance datasets should be visible in risk-sensitive decisions.', 'dataset', 'high', DATE '2026-06-19', 'Political-stability data is relevant for safety and legal-stability scoring.', 'World Bank governance source used for political-risk evidence.'),
            ('russia', 'https://freedomhouse.org/country/russia/freedom-world/2026', 'Political-stability dataset adds external risk context', 'Russia Freedom House evidence', 'The Freedom House profile adds an external civil and political rights source.', 'https://freedomhouse.org/country/russia/freedom-world/2026', 'Rights and freedoms data should inform risk warnings.', 'research', 'medium', DATE '2026-06-19', 'External freedom assessments are part of the risk evidence set.', 'Freedom House source used for safety and freedom context.'),
            ('russia', 'https://worldjusticeproject.org/rule-of-law-index/downloads/2025/WJPIndex2025.pdf', 'Political-stability dataset adds external risk context', 'Russia rule-of-law evidence', 'The WJP dataset adds rule-of-law context for legal-stability scoring.', 'https://worldjusticeproject.org/rule-of-law-index/downloads/2025/WJPIndex2025.pdf', 'Rule-of-law context should be visible in long-term risk scoring.', 'dataset', 'high', DATE '2026-06-19', 'Rule-of-law evidence complements political-stability data.', 'WJP source used for legal-stability evidence.'),
            ('uruguay', 'https://www.gub.uy/tramites/residencia-legal-temporaria', 'Temporary legal residence has an official procedure page', 'Uruguay temporary residence procedure evidence', 'The official procedure page supports first-step residence screening.', 'https://www.gub.uy/tramites/residencia-legal-temporaria', 'Users can start from a concrete government procedure source.', 'procedure', 'high', DATE '2026-06-19', 'Temporary residence has an official government procedure page.', 'Official procedure source used for relocation screening.'),
            ('uruguay', 'https://www.gub.uy/tramites/residencia-legal-permanente', 'Temporary legal residence has an official procedure page', 'Uruguay permanent residence procedure evidence', 'The permanent residence procedure gives a related long-term status source.', 'https://www.gub.uy/tramites/residencia-legal-permanente', 'Temporary and permanent status should be considered separately.', 'procedure', 'high', DATE '2026-06-19', 'Residence planning can compare temporary and permanent procedure sources.', 'Official procedure source used for long-term status context.'),
            ('uruguay', 'https://www.gub.uy/direccion-nacional-migracion/', 'Temporary legal residence has an official procedure page', 'Uruguay migration authority evidence', 'The migration authority source supports routing of residence-related checks.', 'https://www.gub.uy/direccion-nacional-migracion/', 'Authority-level source coverage improves traceability.', 'procedure', 'high', DATE '2026-06-19', 'Residence procedure checks should link back to the migration authority.', 'Official migration authority source used for process context.'),
            ('uruguay', 'https://www.impo.com.uy/bases/leyes/18250-2008', 'Migration law provides a stable statutory baseline', 'Uruguay migration law evidence', 'Migration Law 18250 provides the statutory basis for migration and residence analysis.', 'https://www.impo.com.uy/bases/leyes/18250-2008', 'Procedure sources should be read alongside the statute.', 'legal_basis', 'high', DATE '2026-06-19', 'Uruguay migration screening has an official statutory anchor.', 'Official legal source used for migration-law evidence.'),
            ('uruguay', 'https://www.gub.uy/ministerio-interior/comunicacion/publicaciones/types-of-residencies-in-uruguay', 'Migration law provides a stable statutory baseline', 'Uruguay residence-type overview evidence', 'The Ministry of Interior overview helps distinguish residence categories.', 'https://www.gub.uy/ministerio-interior/comunicacion/publicaciones/types-of-residencies-in-uruguay', 'Residence categories should not be collapsed into one generic path.', 'procedure', 'high', DATE '2026-06-19', 'Residence-type guidance improves decision-oriented summaries.', 'Official overview source used for category screening.'),
            ('uruguay', 'https://www.impo.com.uy/bases/constitucion/1967-1967', 'Migration law provides a stable statutory baseline', 'Uruguay constitutional context evidence', 'The constitution provides primary legal context for long-term stability analysis.', 'https://www.impo.com.uy/bases/constitucion/1967-1967', 'Migration analysis benefits from a broader legal-stability source.', 'legal_basis', 'high', DATE '2026-06-19', 'Legal-stability screening can link to constitutional text.', 'Official constitutional source used for legal context.'),
            ('uruguay', 'https://www.gub.uy/direccion-general-impositiva/', 'Tax administration has a dedicated official source', 'Uruguay tax authority evidence', 'The DGI source is the main tax-administration anchor for user screening.', 'https://www.gub.uy/direccion-general-impositiva/', 'Tax planning should be checked against official DGI materials.', 'tax', 'high', DATE '2026-06-19', 'Uruguay tax administration has an official source.', 'Official tax source used for residence and business screening.'),
            ('uruguay', 'https://www.gub.uy/ministerio-economia-finanzas/', 'Tax administration has a dedicated official source', 'Uruguay economy ministry evidence', 'The Ministry of Economy and Finance source adds official fiscal context.', 'https://www.gub.uy/ministerio-economia-finanzas/', 'Tax and fiscal checks should use ministry-level sources where relevant.', 'tax', 'high', DATE '2026-06-19', 'Fiscal context supports tax and cost-of-living screening.', 'Official ministry source used for fiscal context.'),
            ('uruguay', 'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=UY', 'Tax administration has a dedicated official source', 'Uruguay inflation dataset evidence', 'The inflation indicator adds external context for cost and tax planning.', 'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=UY', 'Cost planning should include dataset-backed inflation context.', 'dataset', 'high', DATE '2026-06-19', 'Inflation data supports cost-of-living screening.', 'World Bank source used for cost context.'),
            ('uruguay', 'https://www.bcu.gub.uy/Servicios-Financieros-SSF/Paginas/Default.aspx', 'Financial services supervision supports banking checks', 'Uruguay financial supervisor evidence', 'The central-bank supervisor source supports financial-services due diligence.', 'https://www.bcu.gub.uy/Servicios-Financieros-SSF/Paginas/Default.aspx', 'Banking readiness should include regulated-sector checks.', 'banking', 'high', DATE '2026-06-19', 'Financial supervision data is relevant for account-readiness screening.', 'Central-bank source used for banking evidence.'),
            ('uruguay', 'https://www.bcu.gub.uy/', 'Financial services supervision supports banking checks', 'Uruguay central bank evidence', 'The central bank source anchors monetary and banking context.', 'https://www.bcu.gub.uy/', 'Banking checks should use the central-bank source family.', 'banking', 'high', DATE '2026-06-19', 'Central-bank source coverage strengthens financial-system context.', 'Central-bank source used for institutional evidence.'),
            ('uruguay', 'https://archive.doingbusiness.org/en/data/exploreeconomies/uruguay', 'Financial services supervision supports banking checks', 'Uruguay business-regulation archive evidence', 'The Doing Business archive provides historical business-regulation context.', 'https://archive.doingbusiness.org/en/data/exploreeconomies/uruguay', 'Business setup screening should distinguish archived dataset context from current legal advice.', 'dataset', 'medium', DATE '2026-06-19', 'Archived business-regulation data remains useful as background context.', 'World Bank archive source used for business-context evidence.'),
            ('uruguay', 'https://www.impo.com.uy/bases/constitucion/1967-1967', 'Constitutional text anchors rule-of-law context', 'Uruguay constitution evidence', 'The constitution is a primary source for legal-stability context.', 'https://www.impo.com.uy/bases/constitucion/1967-1967', 'Constitutional source coverage supports rule-of-law screening.', 'legal_basis', 'high', DATE '2026-06-19', 'Rule-of-law analysis should include primary legal text.', 'Official constitutional source used for legal-stability evidence.'),
            ('uruguay', 'https://worldjusticeproject.org/rule-of-law-index/global/2025', 'Constitutional text anchors rule-of-law context', 'Uruguay rule-of-law index evidence', 'The WJP global index adds comparative rule-of-law context.', 'https://worldjusticeproject.org/rule-of-law-index/global/2025', 'Comparative rule-of-law data complements primary legal text.', 'dataset', 'high', DATE '2026-06-19', 'Legal-stability screening should pair primary law with comparative datasets.', 'WJP source used for comparative legal-stability evidence.'),
            ('uruguay', 'https://freedomhouse.org/country/uruguay/freedom-world/2024', 'Constitutional text anchors rule-of-law context', 'Uruguay freedom profile evidence', 'The Freedom House country profile adds external political-rights context.', 'https://freedomhouse.org/country/uruguay/freedom-world/2024', 'Rights and freedom sources should be visible in risk scoring.', 'research', 'medium', DATE '2026-06-19', 'Freedom assessments complement legal-stability evidence.', 'Freedom House source used for risk context.')
    ) AS rows(
        country_slug,
        source_url,
        legal_signal_title,
        title,
        summary,
        url,
        quote,
        evidence_type,
        confidence,
        published_at,
        claim,
        excerpt
    )
),
resolved_evidence_rows AS (
    SELECT
        c.id AS country_id,
        s.id AS source_id,
        ls.id AS legal_signal_id,
        er.title,
        er.summary,
        er.url,
        er.quote,
        er.evidence_type,
        er.confidence,
        er.published_at,
        er.claim,
        er.excerpt
    FROM evidence_rows er
    JOIN countries c ON c.slug = er.country_slug
    JOIN sources s ON s.url = er.source_url
    JOIN legal_signals ls
        ON ls.country_id = c.id
        AND ls.title = er.legal_signal_title
)
UPDATE evidence_items ei
SET
    source_id = rer.source_id,
    legal_signal_id = rer.legal_signal_id,
    summary = rer.summary,
    url = rer.url,
    quote = rer.quote,
    evidence_type = rer.evidence_type,
    confidence_level = rer.confidence,
    confidence = rer.confidence,
    status = 'published',
    published_at = rer.published_at,
    retrieved_at = CURRENT_DATE,
    claim = rer.claim,
    excerpt = rer.excerpt,
    updated_at = NOW()
FROM resolved_evidence_rows rer
WHERE ei.country_id = rer.country_id
  AND ei.title = rer.title;

WITH card_rows AS (
    SELECT *
    FROM (
        VALUES
            (
                'russia',
                'en',
                'Russia remains a high-friction option for relocation and long-term status. The strongest public sources are official tax, central-bank, visa and legal references, but the source-backed profile points to heavy procedure review, banking checks and elevated political-risk screening.',
                'Short entry and residence questions should be separated. The MFA e-visa portal helps with entry context, while foreign-citizen and public-service sources frame residence and status compliance.',
                'Tax screening should start with the FTS sources for personal income tax and professional income tax. The available official sources improve transparency, but user-specific residency and business facts remain decisive.',
                'Cost-of-living context is supported by World Bank GDP and inflation indicators, with local conditions requiring city-level verification before budgeting.',
                'Business and self-employment planning has official tax and banking sources, but financial access and compliance checks should be completed before relying on a business route.',
                'Safety and political-risk screening should include Freedom House, WJP and World Bank governance data. The decision score treats these as risk inputs, not as personal safety guarantees.',
                'The most important signals are residence-law complexity, separate citizenship review, self-employed tax source availability, payment-system review and external political-risk data.',
                'Primary risks are legal-process complexity, financial-operability uncertainty and elevated external governance risk. Users should avoid treating any single score as legal advice.',
                'Source base now combines official Russian tax, central-bank, public-services and legal references with World Bank, Freedom House and WJP datasets. It is suitable for screening, with expert review still required before action.'
            ),
            (
                'russia',
                'ru',
                'Россия остается вариантом с высокой процедурной нагрузкой для релокации и долгосрочного статуса. Самые сильные публичные источники относятся к налогам, ЦБ, визам и правовым актам, но профиль указывает на необходимость проверки процедур, банковских вопросов и политического риска.',
                'Вопросы краткого въезда и проживания нужно разделять. Портал МИД по электронной визе помогает с въездным контекстом, а источники по статусу иностранцев и госуслугам задают рамку проживания и соблюдения статуса.',
                'Налоговую проверку стоит начинать с источников ФНС по НДФЛ и налогу на профессиональный доход. Официальные источники повышают прозрачность, но индивидуальные факты резидентства и бизнеса остаются ключевыми.',
                'Контекст стоимости жизни поддержан показателями Всемирного банка по ВВП на душу населения и инфляции, но бюджет нужно уточнять на уровне города.',
                'Для бизнеса и самозанятости есть официальные налоговые и банковские источники, однако доступ к финансовым услугам и комплаенс нужно проверить заранее.',
                'Оценка безопасности и политического риска должна учитывать Freedom House, WJP и данные Всемирного банка. Скоринг использует их как риск-факторы, а не как гарантию личной безопасности.',
                'Ключевые сигналы: сложность закона о статусе иностранцев, отдельная проверка гражданства, наличие источника по НПД, необходимость проверки платежной системы и внешний политический риск.',
                'Основные риски связаны со сложностью процедур, неопределенностью финансовой доступности и повышенным внешним governance-рискoм. Нельзя воспринимать скоринг как юридическую консультацию.',
                'База источников теперь сочетает официальные российские налоговые, банковские, сервисные и правовые материалы с данными World Bank, Freedom House и WJP. Этого достаточно для скрининга, но перед действием нужна экспертная проверка.'
            ),
            (
                'uruguay',
                'en',
                'Uruguay is a comparatively stronger source-backed option for residence, long-term planning and risk-sensitive relocation. The profile is supported by official residence procedures, migration law, tax authority materials, central-bank sources and external datasets.',
                'Residence screening can start from official temporary and permanent residence procedure pages, then be checked against the migration law and migration authority materials.',
                'Tax review is anchored by DGI and Ministry of Economy sources. This improves practical traceability for residents, freelancers and business owners, while individual residency facts still matter.',
                'Cost planning is supported by World Bank GDP and inflation indicators and Uruguay statistical sources. Users should still validate housing and private-service costs by city.',
                'Business screening benefits from tax, central-bank and archived business-regulation sources. The score treats Uruguay as more navigable than Russia, but not as paperwork-free.',
                'Safety and institutional context are supported by Freedom House, WJP, World Bank governance data and constitutional sources. These improve confidence for risk-sensitive users.',
                'The strongest signals are official temporary residence procedure coverage, migration-law baseline, tax authority clarity, financial-supervision source availability and constitutional legal context.',
                'Primary risks are ordinary process delays, case-specific tax treatment and the need to distinguish archived business data from current filing requirements.',
                'Source base now combines official government, IMPO, DGI, central-bank, World Bank, Freedom House and WJP sources. It is strong for initial screening and still requires official or professional confirmation before filing.'
            ),
            (
                'uruguay',
                'ru',
                'Уругвай выглядит более сильным вариантом для резиденции, долгосрочного планирования и релокации с учетом рисков. Профиль поддержан официальными процедурами резиденции, миграционным законом, налоговыми источниками, материалами ЦБ и внешними наборами данных.',
                'Проверку резиденции можно начинать с официальных страниц временной и постоянной резиденции, затем сверять с миграционным законом и материалами миграционного органа.',
                'Налоговая проверка опирается на DGI и Министерство экономики. Это повышает практическую прослеживаемость для резидентов, фрилансеров и владельцев бизнеса, но индивидуальные факты резидентства остаются важными.',
                'Планирование расходов поддержано показателями World Bank по ВВП на душу населения и инфляции, а также статистическими источниками Уругвая. Жилье и частные услуги нужно проверять по конкретному городу.',
                'Бизнес-скрининг опирается на налоговые, банковские и архивные источники по регулированию бизнеса. Скоринг считает Уругвай более понятным вариантом, чем Россия, но не вариантом без документов.',
                'Контекст безопасности и институтов поддержан Freedom House, WJP, данными World Bank и конституционными источниками. Это повышает уверенность для пользователей, чувствительных к риску.',
                'Самые сильные сигналы: официальная процедура временной резиденции, миграционный закон, ясность налогового органа, источник по финансовому надзору и конституционный правовой контекст.',
                'Главные риски: обычные задержки процедур, индивидуальный налоговый режим и необходимость отличать архивные бизнес-данные от текущих требований подачи.',
                'База источников теперь сочетает официальные материалы правительства, IMPO, DGI, центрального банка, World Bank, Freedom House и WJP. Она сильна для первичного скрининга, но перед подачей нужна официальная или профессиональная проверка.'
            )
    ) AS rows(
        country_slug,
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
)
UPDATE country_cards cc
SET
    executive_summary = cr.executive_summary,
    migration_overview = cr.migration_overview,
    tax_overview = cr.tax_overview,
    cost_of_living_overview = cr.cost_of_living_overview,
    business_overview = cr.business_overview,
    safety_overview = cr.safety_overview,
    legal_signals_summary = cr.legal_signals_summary,
    risk_summary = cr.risk_summary,
    source_summary = cr.source_summary,
    status = 'published',
    updated_at = NOW()
FROM card_rows cr
JOIN countries c ON c.slug = cr.country_slug
WHERE cc.country_id = c.id
  AND cc.locale = cr.locale;

WITH score_rows AS (
    SELECT *
    FROM (
        VALUES
            ('russia', 'relocation_residence', 'Russia has official entry and residence sources, but the legal-status baseline, procedure burden and banking checks keep relocation suitability limited without expert review.', 'У России есть официальные источники по въезду и проживанию, но закон о статусе иностранцев, процедурная нагрузка и банковские проверки ограничивают пригодность без экспертной проверки.', 'Source-backed screening highlights high procedural friction.'),
            ('russia', 'permanent_residence_citizenship', 'Long-term status is weaker because residence and citizenship are separate legal layers and external governance datasets add material risk context.', 'Долгосрочный статус слабее, потому что проживание и гражданство являются отдельными правовыми слоями, а внешние governance-данные добавляют существенный риск.', 'Long-term planning needs separate legal and risk review.'),
            ('russia', 'low_budget_living', 'Cost indicators are available, but practical budgeting depends on city, payment access and inflation context, so the score remains a cautious screening estimate.', 'Показатели стоимости доступны, но практический бюджет зависит от города, платежного доступа и инфляционного контекста, поэтому оценка остается осторожной.', 'Cost screening is data-backed but city-sensitive.'),
            ('russia', 'business_self_employment', 'Official self-employed tax and banking sources improve visibility, yet account access, tax residency and compliance questions make the route review-heavy.', 'Официальные источники по НПД и банковскому сектору повышают прозрачность, но доступ к счетам, налоговое резидентство и комплаенс требуют глубокой проверки.', 'Business route is source-backed but review-heavy.'),
            ('russia', 'safety_political_risk', 'External political-stability, freedom and rule-of-law datasets make risk warnings central to the score, even where official administrative sources are available.', 'Внешние данные по политической стабильности, свободам и верховенству права делают риск-предупреждения центральными для оценки, даже при наличии официальных административных источников.', 'Risk datasets drive a cautious safety score.'),
            ('uruguay', 'relocation_residence', 'Uruguay has official temporary and permanent residence procedure pages plus a migration-law source, supporting a stronger relocation screening score.', 'У Уругвая есть официальные страницы временной и постоянной резиденции, а также миграционный закон, что поддерживает более сильную релокационную оценку.', 'Residence route has stronger public traceability.'),
            ('uruguay', 'permanent_residence_citizenship', 'Long-term planning benefits from migration law, permanent-residence procedure sources and constitutional context, while still requiring case-specific confirmation.', 'Долгосрочное планирование опирается на миграционный закон, процедуры постоянной резиденции и конституционный контекст, но все равно требует индивидуального подтверждения.', 'Long-term status is comparatively traceable.'),
            ('uruguay', 'low_budget_living', 'World Bank and national statistical sources support cost screening, but housing and private-service costs still need city-level validation.', 'Источники World Bank и национальной статистики поддерживают оценку стоимости, но жилье и частные услуги нужно проверять по конкретному городу.', 'Cost screen has solid dataset coverage.'),
            ('uruguay', 'business_self_employment', 'Tax authority, economy ministry, central-bank and archived business-regulation sources give Uruguay a stronger business-readiness evidence base.', 'Налоговый орган, министерство экономики, центральный банк и архивные бизнес-данные дают Уругваю более сильную доказательную базу для бизнеса.', 'Business screening has multiple official anchors.'),
            ('uruguay', 'safety_political_risk', 'Freedom, rule-of-law, governance and constitutional sources support a comparatively stronger risk-sensitive profile, with normal filing and verification risk remaining.', 'Источники по свободам, верховенству права, governance и конституции поддерживают более сильный профиль для риск-чувствительных решений, при сохранении обычных процедурных рисков.', 'Risk profile is supported by official and external sources.')
    ) AS rows(country_slug, scenario_slug, explanation_en, explanation_ru, summary)
)
UPDATE country_scores cs
SET
    explanation_en = sr.explanation_en,
    explanation_ru = sr.explanation_ru,
    summary = sr.summary,
    score_label = 'Source-backed screening score',
    confidence = CASE WHEN sr.country_slug = 'uruguay' THEN 'high' ELSE 'medium' END,
    updated_at = NOW()
FROM score_rows sr
JOIN countries c ON c.slug = sr.country_slug
JOIN scenarios s ON s.slug = sr.scenario_slug
WHERE cs.country_id = c.id
  AND cs.scenario_id = s.id;

WITH breakdown_rows AS (
    SELECT *
    FROM (
        VALUES
            ('russia', 'legalization_score', 'Legalization remains constrained by statute-led foreign-citizen rules, public-service procedure checks and separate entry sources.', 'Легализация ограничена законом о статусе иностранцев, процедурными проверками через госуслуги и отдельными источниками по въезду.', 'medium'),
            ('russia', 'long_term_status_score', 'Long-term status requires separate review of residence, citizenship and external governance risk rather than extrapolation from entry eligibility.', 'Долгосрочный статус требует отдельной проверки проживания, гражданства и внешнего governance-риска, а не вывода из въездных условий.', 'medium'),
            ('russia', 'cost_of_living_score', 'Cost context is source-backed through GDP and inflation datasets, but city-level budgets and payment access remain practical uncertainties.', 'Стоимость жизни подтверждается наборами данных по ВВП и инфляции, но городские бюджеты и платежный доступ остаются практическими неопределенностями.', 'medium'),
            ('russia', 'safety_score', 'Safety scoring is driven by external freedom, rule-of-law and political-stability sources and should be treated as a risk warning layer.', 'Оценка безопасности опирается на внешние источники по свободам, верховенству права и политической стабильности и должна восприниматься как слой риск-предупреждений.', 'medium'),
            ('russia', 'business_score', 'Business and self-employment have official tax and central-bank sources, but compliance, account access and residency facts lower screening confidence.', 'Бизнес и самозанятость имеют официальные налоговые и банковские источники, но комплаенс, доступ к счетам и факты резидентства снижают уверенность.', 'medium'),
            ('russia', 'legal_stability_score', 'Legal stability uses primary legal references plus WJP and governance datasets, with external indicators keeping the score cautious.', 'Правовая стабильность опирается на первичные правовые источники, WJP и governance-данные, а внешние показатели сохраняют осторожность оценки.', 'medium'),
            ('russia', 'source_quality_score', 'Russia now has a broader official and dataset-backed source base, but several user-critical topics still need expert interpretation.', 'У России теперь шире база официальных источников и данных, но несколько критичных тем все еще требуют экспертной интерпретации.', 'medium'),
            ('uruguay', 'legalization_score', 'Legalization has strong traceability through temporary and permanent residence procedures, migration authority materials and migration law.', 'Легализация хорошо прослеживается через процедуры временной и постоянной резиденции, материалы миграционного органа и миграционный закон.', 'high'),
            ('uruguay', 'long_term_status_score', 'Long-term status benefits from permanent residence procedure sources, migration law and constitutional context, with case-specific checks still required.', 'Долгосрочный статус поддержан источниками по постоянной резиденции, миграционным законом и конституционным контекстом, но индивидуальные проверки сохраняются.', 'high'),
            ('uruguay', 'cost_of_living_score', 'Cost context is backed by World Bank indicators and national statistics, with housing and private services left for city-level verification.', 'Стоимость жизни подтверждается показателями World Bank и национальной статистикой, а жилье и частные услуги требуют городской проверки.', 'high'),
            ('uruguay', 'safety_score', 'Safety and institutional context are supported by freedom, rule-of-law, governance and constitutional sources, giving stronger risk-screening confidence.', 'Безопасность и институциональный контекст поддержаны источниками по свободам, верховенству права, governance и конституции, что повышает уверенность.', 'high'),
            ('uruguay', 'business_score', 'Business readiness is supported by tax, economy-ministry, central-bank and archived regulation sources, while current filing details need confirmation.', 'Готовность к бизнесу поддержана налоговыми, экономическими, банковскими и архивными регуляторными источниками, но актуальные детали подачи нужно подтверждать.', 'high'),
            ('uruguay', 'legal_stability_score', 'Legal stability has primary legal texts and external rule-of-law datasets, supporting a stronger long-term planning score.', 'Правовая стабильность имеет первичные правовые тексты и внешние индексы верховенства права, что поддерживает более сильную долгосрочную оценку.', 'high'),
            ('uruguay', 'source_quality_score', 'Uruguay now has a dense official-source base across residence, tax, banking and law plus external datasets for comparative context.', 'У Уругвая теперь плотная база официальных источников по резиденции, налогам, банкам и праву, а также внешние наборы данных для сравнения.', 'high')
    ) AS rows(country_slug, criterion, explanation_en, explanation_ru, confidence)
),
breakdown_source_rows AS (
    SELECT
        s.id::text AS source_id,
        s.country_id,
        s.title,
        s.confidence,
        s.source_type,
        LOWER(s.title || ' ' || s.url || ' ' || s.publisher) AS source_text
    FROM sources s
    WHERE s.status = 'published'
),
source_matches AS (
    SELECT
        bsr.country_id,
        'source_quality_score' AS criterion,
        bsr.source_id,
        bsr.title,
        bsr.confidence,
        bsr.source_type
    FROM breakdown_source_rows bsr
    UNION ALL
    SELECT
        bsr.country_id,
        'legalization_score',
        bsr.source_id,
        bsr.title,
        bsr.confidence,
        bsr.source_type
    FROM breakdown_source_rows bsr
    WHERE bsr.source_text LIKE '%residence%'
       OR bsr.source_text LIKE '%migration%'
       OR bsr.source_text LIKE '%foreign%'
       OR bsr.source_text LIKE '%visa%'
       OR bsr.source_text LIKE '%600100%'
    UNION ALL
    SELECT
        bsr.country_id,
        'long_term_status_score',
        bsr.source_id,
        bsr.title,
        bsr.confidence,
        bsr.source_type
    FROM breakdown_source_rows bsr
    WHERE bsr.source_text LIKE '%citizenship%'
       OR bsr.source_text LIKE '%permanent%'
       OR bsr.source_text LIKE '%constitucion%'
       OR bsr.source_text LIKE '%constitution%'
       OR bsr.source_text LIKE '%migration law%'
    UNION ALL
    SELECT
        bsr.country_id,
        'cost_of_living_score',
        bsr.source_id,
        bsr.title,
        bsr.confidence,
        bsr.source_type
    FROM breakdown_source_rows bsr
    WHERE bsr.source_text LIKE '%gdp%'
       OR bsr.source_text LIKE '%inflation%'
       OR bsr.source_text LIKE '%statistics%'
       OR bsr.source_text LIKE '%estadistica%'
       OR bsr.source_text LIKE '%world bank%'
    UNION ALL
    SELECT
        bsr.country_id,
        'safety_score',
        bsr.source_id,
        bsr.title,
        bsr.confidence,
        bsr.source_type
    FROM breakdown_source_rows bsr
    WHERE bsr.source_text LIKE '%freedom%'
       OR bsr.source_text LIKE '%rule of law%'
       OR bsr.source_text LIKE '%political stability%'
       OR bsr.source_text LIKE '%constitution%'
    UNION ALL
    SELECT
        bsr.country_id,
        'business_score',
        bsr.source_id,
        bsr.title,
        bsr.confidence,
        bsr.source_type
    FROM breakdown_source_rows bsr
    WHERE bsr.source_text LIKE '%tax%'
       OR bsr.source_text LIKE '%bank%'
       OR bsr.source_text LIKE '%business%'
       OR bsr.source_text LIKE '%impositiva%'
       OR bsr.source_text LIKE '%nalog%'
    UNION ALL
    SELECT
        bsr.country_id,
        'legal_stability_score',
        bsr.source_id,
        bsr.title,
        bsr.confidence,
        bsr.source_type
    FROM breakdown_source_rows bsr
    WHERE bsr.source_text LIKE '%law%'
       OR bsr.source_text LIKE '%constitution%'
       OR bsr.source_text LIKE '%constitucion%'
       OR bsr.source_text LIKE '%rule of law%'
       OR bsr.source_text LIKE '%consultantplus%'
       OR bsr.source_text LIKE '%impo%'
),
ranked_source_matches AS (
    SELECT
        sm.country_id,
        sm.criterion,
        sm.source_id,
        ROW_NUMBER() OVER (
            PARTITION BY sm.country_id, sm.criterion
            ORDER BY
                CASE sm.confidence
                    WHEN 'high' THEN 0
                    WHEN 'medium' THEN 1
                    ELSE 2
                END,
                CASE sm.source_type
                    WHEN 'official' THEN 0
                    WHEN 'dataset' THEN 1
                    WHEN 'research' THEN 2
                    ELSE 3
                END,
                sm.title
        ) AS source_rank
    FROM source_matches sm
),
breakdown_source_ids AS (
    SELECT
        c.slug AS country_slug,
        rsm.criterion,
        jsonb_agg(rsm.source_id ORDER BY rsm.source_rank) AS source_ids
    FROM ranked_source_matches rsm
    JOIN countries c ON c.id = rsm.country_id
    WHERE rsm.source_rank <= 4
    GROUP BY c.slug, rsm.criterion
)
UPDATE country_score_breakdowns csb
SET
    explanation_en = br.explanation_en,
    explanation_ru = br.explanation_ru,
    confidence = br.confidence,
    source_ids = COALESCE(bsi.source_ids, '[]'::jsonb),
    updated_at = NOW()
FROM country_scores cs
JOIN countries c ON c.id = cs.country_id
JOIN scenarios s ON s.id = cs.scenario_id
JOIN breakdown_rows br ON br.country_slug = c.slug
LEFT JOIN breakdown_source_ids bsi
    ON bsi.country_slug = br.country_slug
    AND bsi.criterion = br.criterion
WHERE csb.country_score_id = cs.id
  AND br.criterion = csb.criterion
  AND c.slug IN ('russia', 'uruguay')
  AND s.slug IN (
      'relocation_residence',
      'permanent_residence_citizenship',
      'low_budget_living',
      'business_self_employment',
      'safety_political_risk'
  );
