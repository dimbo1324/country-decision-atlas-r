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
                'КонсультантПлюс: Закон о правовом положении иностранных граждан',
                'https://www.consultant.ru/document/cons_doc_LAW_37868/',
                'official',
                'ConsultantPlus',
                'ru',
                'high',
                'high',
                DATE '2002-07-25',
                'Основной правовой источник для проверки статуса иностранных граждан в России и требований к проживанию.'
            ),
            (
                'russia',
                'КонсультантПлюс: Федеральный закон о гражданстве РФ',
                'https://www.consultant.ru/document/cons_doc_LAW_445998/',
                'official',
                'ConsultantPlus',
                'ru',
                'high',
                'high',
                DATE '2023-04-28',
                'Основной правовой источник для путей натурализации и правил статуса гражданства.'
            ),
            (
                'russia',
                'ФНС России: портал налога на профессиональный доход',
                'https://npd.nalog.ru/',
                'official',
                'Federal Tax Service of Russia',
                'ru',
                'high',
                'high',
                NULL,
                'Официальный портал ФНС для режима налога на профессиональный доход.'
            ),
            (
                'russia',
                'ФНС России: страница НДФЛ',
                'https://www.nalog.gov.ru/rn77/taxation/taxes/ndfl/',
                'official',
                'Federal Tax Service of Russia',
                'ru',
                'high',
                'high',
                NULL,
                'Официальный справочный материал ФНС по налогу на доходы физических лиц.'
            ),
            (
                'russia',
                'Банк России: Национальная платёжная система',
                'https://www.cbr.ru/eng/psystem/',
                'official',
                'Bank of Russia',
                'en',
                'high',
                'high',
                NULL,
                'Официальный справочный материал центрального банка по надзору за платёжной системой.'
            ),
            (
                'russia',
                'Банк России: банковский сектор',
                'https://www.cbr.ru/eng/banking_sector/',
                'official',
                'Bank of Russia',
                'en',
                'high',
                'high',
                NULL,
                'Официальный справочный материал центрального банка по надзору за банковским сектором.'
            ),
            (
                'russia',
                'Всемирный банк: ВВП на душу населения, Россия',
                'https://data.worldbank.org/indicator/NY.GDP.PCAP.CD?locations=RU',
                'dataset',
                'World Bank',
                'en',
                'high',
                'high',
                NULL,
                'Страновой показатель Всемирного банка по ВВП на душу населения.'
            ),
            (
                'russia',
                'Всемирный банк: инфляция, Россия',
                'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=RU',
                'dataset',
                'World Bank',
                'en',
                'high',
                'high',
                NULL,
                'Страновой показатель Всемирного банка по инфляции потребительских цен.'
            ),
            (
                'russia',
                'Всемирный банк: политическая стабильность, Россия',
                'https://data.worldbank.org/indicator/PV.EST?locations=RU',
                'dataset',
                'World Bank',
                'en',
                'high',
                'high',
                NULL,
                'Страновой показатель управления Всемирного банка по политической стабильности.'
            ),
            (
                'russia',
                'Госуслуги: форма подачи по вопросам проживания',
                'https://www.gosuslugi.ru/600100/1/form',
                'official',
                'Gosuslugi',
                'ru',
                'medium',
                'medium',
                NULL,
                'Официальная точка входа государственных услуг для процедуры, связанной с проживанием.'
            ),
            (
                'uruguay',
                'Уругвай: процедура временного легального резидентства',
                'https://www.gub.uy/tramites/residencia-legal-temporaria',
                'official',
                'Government of Uruguay',
                'es',
                'high',
                'high',
                NULL,
                'Официальная государственная процедурная страница временного легального резидентства.'
            ),
            (
                'uruguay',
                'IMPO Уругвай: Закон о миграции 18250',
                'https://www.impo.com.uy/bases/leyes/18250-2008',
                'official',
                'IMPO Uruguay',
                'es',
                'high',
                'high',
                DATE '2008-01-06',
                'Официальный текст миграционного закона Уругвая.'
            ),
            (
                'uruguay',
                'Налоговая дирекция Уругвая (DGI)',
                'https://www.gub.uy/direccion-general-impositiva/',
                'official',
                'Direccion General Impositiva',
                'es',
                'high',
                'high',
                NULL,
                'Официальный источник налогового органа для налогового администрирования и руководства.'
            ),
            (
                'uruguay',
                'Национальный статистический институт Уругвая (INE)',
                'https://www.gub.uy/instituto-nacional-estadistica/',
                'official',
                'Instituto Nacional de Estadistica',
                'es',
                'high',
                'high',
                NULL,
                'Официальный источник национальной статистики для демографического и экономического контекста.'
            ),
            (
                'uruguay',
                'Всемирный банк: ВВП на душу населения, Уругвай',
                'https://data.worldbank.org/indicator/NY.GDP.PCAP.CD?locations=UY',
                'dataset',
                'World Bank',
                'en',
                'high',
                'high',
                NULL,
                'Страновой показатель Всемирного банка по ВВП на душу населения.'
            ),
            (
                'uruguay',
                'Всемирный банк: инфляция, Уругвай',
                'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=UY',
                'dataset',
                'World Bank',
                'en',
                'high',
                'high',
                NULL,
                'Страновой показатель Всемирного банка по инфляции потребительских цен.'
            ),
            (
                'uruguay',
                'Всемирный банк: политическая стабильность, Уругвай',
                'https://data.worldbank.org/indicator/PV.EST?locations=UY',
                'dataset',
                'World Bank',
                'en',
                'high',
                'high',
                NULL,
                'Страновой показатель управления Всемирного банка по политической стабильности.'
            ),
            (
                'uruguay',
                'Центральный банк Уругвая: надзор за финансовыми услугами',
                'https://www.bcu.gub.uy/Servicios-Financieros-SSF/Paginas/Default.aspx',
                'official',
                'Central Bank of Uruguay',
                'es',
                'high',
                'high',
                NULL,
                'Официальный надзорный источник для регулируемых финансовых услуг.'
            ),
            (
                'uruguay',
                'Всемирный банк: архив Doing Business, Уругвай',
                'https://archive.doingbusiness.org/en/data/exploreeconomies/uruguay',
                'dataset',
                'World Bank',
                'en',
                'medium',
                'medium',
                NULL,
                'Архивный набор данных Всемирного банка по регулированию бизнеса в Уругвае.'
            ),
            (
                'uruguay',
                'IMPO Уругвай: Конституция',
                'https://www.impo.com.uy/bases/constitucion/1967-1967',
                'official',
                'IMPO Uruguay',
                'es',
                'high',
                'high',
                DATE '1967-02-15',
                'Официальный конституционный текст для контекста правовой стабильности.'
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
            ('russia', 'https://www.consultant.ru/document/cons_doc_LAW_37868/', 'Статус иностранцев остается законодательно регулируемым', 'Russia foreign citizen law baseline', 'Закон о правовом положении является первичным источником для анализа пребывания, проживания и статусных обязательств.', 'https://www.consultant.ru/document/cons_doc_LAW_37868/', 'Источник следует изучить перед принятием простого пути резидентства.', 'legal_basis', 'high', DATE '2026-06-19', 'Статус иностранных граждан в России регулируется специальным федеральным законом.', 'Первичный правовой источник для скрининга резидентства и статуса.'),
            ('russia', 'https://www.gosuslugi.ru/600100/1/form', 'Статус иностранцев остается законодательно регулируемым', 'Russia residence process public-services touchpoint', 'Форма госуслуг даёт практический процессуальный контекст для административных процедур, связанных с проживанием.', 'https://www.gosuslugi.ru/600100/1/form', 'Процедурный уровень следует проверять по законодательной базе.', 'procedure', 'medium', DATE '2026-06-19', 'Планирование проживания включает проверку государственных процедур наряду с правовыми нормами.', 'Источник государственных услуг для скрининга административных процессов.'),
            ('russia', 'https://evisa.kdmid.ru/', 'Статус иностранцев остается законодательно регулируемым', 'Russia electronic visa source', 'Портал электронной визы МИД полезен для проверки краткосрочного въезда, но не заменяет консультацию по проживанию.', 'https://evisa.kdmid.ru/', 'Разрешение на въезд и статус резидентства являются отдельными уровнями скрининга.', 'procedure', 'high', DATE '2026-06-19', 'Проверку краткосрочного въезда следует отделять от анализа резидентства.', 'Официальный источник электронной визы для доказательств въездного контекста.'),
            ('russia', 'https://www.consultant.ru/document/cons_doc_LAW_445998/', 'Гражданство требует отдельной правовой проверки', 'Russia citizenship law baseline', 'Закон о гражданстве создаёт отдельную правовую основу для натурализации и гражданского статуса.', 'https://www.consultant.ru/document/cons_doc_LAW_445998/', 'Анализ гражданства не должен выводиться только из оценки резидентства.', 'legal_basis', 'high', DATE '2026-06-19', 'Гражданство России регулируется специальным федеральным законом о гражданстве.', 'Первичный источник по гражданству для скрининга долгосрочного статуса.'),
            ('russia', 'https://www.consultant.ru/document/cons_doc_LAW_37868/', 'Гражданство требует отдельной правовой проверки', 'Russia residence-to-status dependency', 'Правила проживания и статуса иностранных граждан сохраняют актуальность до рассмотрения любого пути к гражданству.', 'https://www.consultant.ru/document/cons_doc_LAW_37868/', 'Долгосрочный путь начинается с отдельного уровня соблюдения требований проживания.', 'legal_basis', 'high', DATE '2026-06-19', 'Скрининг долгосрочного статуса зависит как от правовых уровней проживания, так и гражданства.', 'Первичный источник по проживанию как зависимость для скрининга гражданства.'),
            ('russia', 'https://data.worldbank.org/indicator/PV.EST?locations=RU', 'Гражданство требует отдельной правовой проверки', 'Russia long-term risk context', 'Данные по политической стабильности добавляют риск-контекст для долгосрочных решений.', 'https://data.worldbank.org/indicator/PV.EST?locations=RU', 'Долгосрочный статус должен учитывать показатели рисков управления.', 'dataset', 'high', DATE '2026-06-19', 'Долгосрочное планирование должно учитывать внешние данные по управлению.', 'Показатель управления Всемирного банка для риск-контекста.'),
            ('russia', 'https://npd.nalog.ru/', 'Налог на профессиональный доход имеет официальное цифровое руководство', 'Russia self-employed tax portal evidence', 'Портал ФНС предоставляет официальный источник для скрининга налога на профессиональный доход.', 'https://npd.nalog.ru/', 'Соответствие требованиям и взаимодействие с налоговым резидентством всё равно требуют проверки.', 'tax', 'high', DATE '2026-06-19', 'Налог на профессиональный доход имеет официальный цифровой информационный источник.', 'Официальный источник ФНС для скрининга самозанятости.'),
            ('russia', 'https://www.nalog.gov.ru/rn77/taxation/taxes/ndfl/', 'Налог на профессиональный доход имеет официальное цифровое руководство', 'Russia personal income tax evidence', 'Страница ФНС по НДФЛ актуальна для индивидуальной налоговой нагрузки.', 'https://www.nalog.gov.ru/rn77/taxation/taxes/ndfl/', 'Личное налогообложение следует проверять наряду с любым специальным режимом.', 'tax', 'high', DATE '2026-06-19', 'НДФЛ остаётся отдельным скрининговым элементом, обеспеченным источниками.', 'Официальный налоговый источник ФНС для скрининга индивидуального налогообложения.'),
            ('russia', 'https://www.cbr.ru/eng/banking_sector/', 'Налог на профессиональный доход имеет официальное цифровое руководство', 'Russia banking context for freelancers', 'Контекст надзора за банковским сектором важен для фрилансеров и пользователей малого бизнеса.', 'https://www.cbr.ru/eng/banking_sector/', 'Налоговое планирование следует сочетать с проверкой банковской готовности.', 'banking', 'high', DATE '2026-06-19', 'Планирование независимой работы также зависит от доступности банковских услуг.', 'Источник центрального банка для контекста финансовой операционности.'),
            ('russia', 'https://www.cbr.ru/eng/psystem/', 'Контекст платёжной системы следует проверить до релокации', 'Russia payment-system evidence', 'Страница центрального банка по платёжной системе поддерживает скрининг доступности карт, переводов и платежей.', 'https://www.cbr.ru/eng/psystem/', 'Платёжная инфраструктура может влиять на практическую осуществимость релокации.', 'banking', 'high', DATE '2026-06-19', 'Скрининг релокации должен включать проверку готовности платёжной системы.', 'Источник центрального банка для доказательств платёжной системы.'),
            ('russia', 'https://www.cbr.ru/eng/banking_sector/', 'Контекст платёжной системы следует проверить до релокации', 'Russia banking-sector evidence', 'Источник по банковскому сектору поддерживает финансово-системную проверку.', 'https://www.cbr.ru/eng/banking_sector/', 'Доступ к счетам и регулируемый банковский контекст следует проверять заблаговременно.', 'banking', 'high', DATE '2026-06-19', 'Надзор за банковским сектором актуален для ежедневного финансового доступа.', 'Источник центрального банка для доказательств банковского сектора.'),
            ('russia', 'https://www.nalog.gov.ru/eng/', 'Контекст платёжной системы следует проверить до релокации', 'Russia financial administration evidence', 'Источник ФНС добавляет контекст государственного администрирования для финансовых и налоговых процессов.', 'https://www.nalog.gov.ru/eng/', 'Финансовая готовность включает точки контакта с налоговым администрированием.', 'tax', 'high', DATE '2026-06-19', 'Налоговые и банковские процессы взаимодействуют при практическом планировании релокации.', 'Официальный налоговый источник для контекста финансового администрирования.'),
            ('russia', 'https://data.worldbank.org/indicator/PV.EST?locations=RU', 'Набор данных по политической стабильности добавляет внешний риск-контекст', 'Russia political stability dataset evidence', 'Показатель политической стабильности Всемирного банка предоставляет внешние данные для оценки рисков.', 'https://data.worldbank.org/indicator/PV.EST?locations=RU', 'Внешние данные по управлению должны быть видны в риск-чувствительных решениях.', 'dataset', 'high', DATE '2026-06-19', 'Данные по политической стабильности актуальны для оценки безопасности и правовой стабильности.', 'Источник управления Всемирного банка для доказательств политических рисков.'),
            ('russia', 'https://freedomhouse.org/country/russia/freedom-world/2026', 'Набор данных по политической стабильности добавляет внешний риск-контекст', 'Russia Freedom House evidence', 'Профиль Freedom House добавляет внешний источник по гражданским и политическим правам.', 'https://freedomhouse.org/country/russia/freedom-world/2026', 'Данные по правам и свободам должны учитываться в риск-предупреждениях.', 'research', 'medium', DATE '2026-06-19', 'Внешние оценки свободы являются частью набора риск-доказательств.', 'Источник Freedom House для контекста безопасности и свободы.'),
            ('russia', 'https://worldjusticeproject.org/rule-of-law-index/downloads/2025/WJPIndex2025.pdf', 'Набор данных по политической стабильности добавляет внешний риск-контекст', 'Russia rule-of-law evidence', 'Набор данных WJP добавляет контекст верховенства права для оценки правовой стабильности.', 'https://worldjusticeproject.org/rule-of-law-index/downloads/2025/WJPIndex2025.pdf', 'Контекст верховенства права должен быть виден при долгосрочной оценке рисков.', 'dataset', 'high', DATE '2026-06-19', 'Доказательства верховенства права дополняют данные политической стабильности.', 'Источник WJP для доказательств правовой стабильности.'),
            ('uruguay', 'https://www.gub.uy/tramites/residencia-legal-temporaria', 'Временная легальная резиденция имеет официальную процедурную страницу', 'Uruguay temporary residence procedure evidence', 'Официальная процедурная страница поддерживает первичный скрининг резидентства.', 'https://www.gub.uy/tramites/residencia-legal-temporaria', 'Пользователи могут начать с конкретного государственного процедурного источника.', 'procedure', 'high', DATE '2026-06-19', 'Временная резиденция описана на официальной государственной процедурной странице.', 'Официальный процедурный источник для скрининга релокации.'),
            ('uruguay', 'https://www.gub.uy/tramites/residencia-legal-permanente', 'Временная легальная резиденция имеет официальную процедурную страницу', 'Uruguay permanent residence procedure evidence', 'Процедура постоянной резиденции даёт связанный источник долгосрочного статуса.', 'https://www.gub.uy/tramites/residencia-legal-permanente', 'Временный и постоянный статус следует рассматривать отдельно.', 'procedure', 'high', DATE '2026-06-19', 'Планирование резидентства может сравнивать источники по временным и постоянным процедурам.', 'Официальный процедурный источник для контекста долгосрочного статуса.'),
            ('uruguay', 'https://www.gub.uy/direccion-nacional-migracion/', 'Временная легальная резиденция имеет официальную процедурную страницу', 'Uruguay migration authority evidence', 'Источник миграционного органа поддерживает маршрутизацию проверок, связанных с резидентством.', 'https://www.gub.uy/direccion-nacional-migracion/', 'Охват источниками на уровне органа улучшает прослеживаемость.', 'procedure', 'high', DATE '2026-06-19', 'Проверки процедур резидентства должны опираться на миграционный орган.', 'Официальный источник миграционного органа для процессного контекста.'),
            ('uruguay', 'https://www.impo.com.uy/bases/leyes/18250-2008', 'Миграционный закон обеспечивает стабильную законодательную основу', 'Uruguay migration law evidence', 'Миграционный закон 18250 предоставляет законодательную основу для анализа миграции и резидентства.', 'https://www.impo.com.uy/bases/leyes/18250-2008', 'Процедурные источники следует читать вместе с законодательством.', 'legal_basis', 'high', DATE '2026-06-19', 'Скрининг миграции Уругвая имеет официальный законодательный якорь.', 'Официальный правовой источник для доказательств миграционного закона.'),
            ('uruguay', 'https://www.gub.uy/ministerio-interior/comunicacion/publicaciones/types-of-residencies-in-uruguay', 'Миграционный закон обеспечивает стабильную законодательную основу', 'Uruguay residence-type overview evidence', 'Обзор Министерства внутренних дел помогает различать категории резидентства.', 'https://www.gub.uy/ministerio-interior/comunicacion/publicaciones/types-of-residencies-in-uruguay', 'Категории резидентства не следует сводить к одному общему пути.', 'procedure', 'high', DATE '2026-06-19', 'Руководство по типам резидентства улучшает ориентированные на решения резюме.', 'Официальный обзорный источник для скрининга категорий.'),
            ('uruguay', 'https://www.impo.com.uy/bases/constitucion/1967-1967', 'Миграционный закон обеспечивает стабильную законодательную основу', 'Uruguay constitutional context evidence', 'Конституция предоставляет первичный правовой контекст для анализа долгосрочной стабильности.', 'https://www.impo.com.uy/bases/constitucion/1967-1967', 'Миграционный анализ выигрывает от более широкого источника правовой стабильности.', 'legal_basis', 'high', DATE '2026-06-19', 'Скрининг правовой стабильности может ссылаться на конституционный текст.', 'Официальный конституционный источник для правового контекста.'),
            ('uruguay', 'https://www.gub.uy/direccion-general-impositiva/', 'Налоговое администрирование имеет специальный официальный источник', 'Uruguay tax authority evidence', 'Источник DGI является основным якорем налогового администрирования для скрининга пользователей.', 'https://www.gub.uy/direccion-general-impositiva/', 'Налоговое планирование следует проверять по официальным материалам DGI.', 'tax', 'high', DATE '2026-06-19', 'Налоговое администрирование Уругвая имеет официальный источник.', 'Официальный налоговый источник для скрининга резидентства и бизнеса.'),
            ('uruguay', 'https://www.gub.uy/ministerio-economia-finanzas/', 'Налоговое администрирование имеет специальный официальный источник', 'Uruguay economy ministry evidence', 'Источник Министерства экономики и финансов добавляет официальный фискальный контекст.', 'https://www.gub.uy/ministerio-economia-finanzas/', 'Налоговые и фискальные проверки должны использовать министерские источники там, где это применимо.', 'tax', 'high', DATE '2026-06-19', 'Фискальный контекст поддерживает скрининг налогов и стоимости жизни.', 'Официальный министерский источник для фискального контекста.'),
            ('uruguay', 'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=UY', 'Налоговое администрирование имеет специальный официальный источник', 'Uruguay inflation dataset evidence', 'Показатель инфляции добавляет внешний контекст для планирования расходов и налогов.', 'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=UY', 'Планирование расходов должно включать подкреплённый данными контекст инфляции.', 'dataset', 'high', DATE '2026-06-19', 'Данные по инфляции поддерживают скрининг стоимости жизни.', 'Источник Всемирного банка для ценового контекста.'),
            ('uruguay', 'https://www.bcu.gub.uy/Servicios-Financieros-SSF/Paginas/Default.aspx', 'Надзор за финансовыми услугами поддерживает банковские проверки', 'Uruguay financial supervisor evidence', 'Источник надзора центрального банка поддерживает финансово-сервисную проверку.', 'https://www.bcu.gub.uy/Servicios-Financieros-SSF/Paginas/Default.aspx', 'Банковская готовность должна включать проверки регулируемого сектора.', 'banking', 'high', DATE '2026-06-19', 'Данные финансового надзора актуальны для скрининга готовности счетов.', 'Источник центрального банка для банковских доказательств.'),
            ('uruguay', 'https://www.bcu.gub.uy/', 'Надзор за финансовыми услугами поддерживает банковские проверки', 'Uruguay central bank evidence', 'Источник центрального банка закрепляет денежный и банковский контекст.', 'https://www.bcu.gub.uy/', 'Банковские проверки должны использовать семейство источников центрального банка.', 'banking', 'high', DATE '2026-06-19', 'Охват источниками центрального банка укрепляет контекст финансовой системы.', 'Источник центрального банка для институциональных доказательств.'),
            ('uruguay', 'https://archive.doingbusiness.org/en/data/exploreeconomies/uruguay', 'Надзор за финансовыми услугами поддерживает банковские проверки', 'Uruguay business-regulation archive evidence', 'Архив Doing Business предоставляет исторический контекст регулирования бизнеса.', 'https://archive.doingbusiness.org/en/data/exploreeconomies/uruguay', 'Скрининг создания бизнеса должен отличать архивный контекст наборов данных от текущей юридической консультации.', 'dataset', 'medium', DATE '2026-06-19', 'Архивные данные по регулированию бизнеса остаются полезными как фоновый контекст.', 'Архивный источник Всемирного банка для бизнес-контекстных доказательств.'),
            ('uruguay', 'https://www.impo.com.uy/bases/constitucion/1967-1967', 'Конституционный текст закрепляет контекст верховенства права', 'Uruguay constitution evidence', 'Конституция является первичным источником для контекста правовой стабильности.', 'https://www.impo.com.uy/bases/constitucion/1967-1967', 'Охват конституционными источниками поддерживает скрининг верховенства права.', 'legal_basis', 'high', DATE '2026-06-19', 'Анализ верховенства права должен включать первичный правовой текст.', 'Официальный конституционный источник для доказательств правовой стабильности.'),
            ('uruguay', 'https://worldjusticeproject.org/rule-of-law-index/global/2025', 'Конституционный текст закрепляет контекст верховенства права', 'Uruguay rule-of-law index evidence', 'Глобальный индекс WJP добавляет сравнительный контекст верховенства права.', 'https://worldjusticeproject.org/rule-of-law-index/global/2025', 'Сравнительные данные верховенства права дополняют первичный правовой текст.', 'dataset', 'high', DATE '2026-06-19', 'Скрининг правовой стабильности должен сочетать первичное право со сравнительными наборами данных.', 'Источник WJP для сравнительных доказательств правовой стабильности.'),
            ('uruguay', 'https://freedomhouse.org/country/uruguay/freedom-world/2024', 'Конституционный текст закрепляет контекст верховенства права', 'Uruguay freedom profile evidence', 'Страновой профиль Freedom House добавляет внешний контекст политических прав.', 'https://freedomhouse.org/country/uruguay/freedom-world/2024', 'Источники прав и свобод должны быть видны при оценке рисков.', 'research', 'medium', DATE '2026-06-19', 'Оценки свободы дополняют доказательства правовой стабильности.', 'Источник Freedom House для риск-контекста.')
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
            ('russia', 'https://www.consultant.ru/document/cons_doc_LAW_37868/', 'Статус иностранцев остается законодательно регулируемым', 'Russia foreign citizen law baseline', 'Закон о правовом положении является первичным источником для анализа пребывания, проживания и статусных обязательств.', 'https://www.consultant.ru/document/cons_doc_LAW_37868/', 'Источник следует изучить перед принятием простого пути резидентства.', 'legal_basis', 'high', DATE '2026-06-19', 'Статус иностранных граждан в России регулируется специальным федеральным законом.', 'Первичный правовой источник для скрининга резидентства и статуса.'),
            ('russia', 'https://www.gosuslugi.ru/600100/1/form', 'Статус иностранцев остается законодательно регулируемым', 'Russia residence process public-services touchpoint', 'Форма госуслуг даёт практический процессуальный контекст для административных процедур, связанных с проживанием.', 'https://www.gosuslugi.ru/600100/1/form', 'Процедурный уровень следует проверять по законодательной базе.', 'procedure', 'medium', DATE '2026-06-19', 'Планирование проживания включает проверку государственных процедур наряду с правовыми нормами.', 'Источник государственных услуг для скрининга административных процессов.'),
            ('russia', 'https://evisa.kdmid.ru/', 'Статус иностранцев остается законодательно регулируемым', 'Russia electronic visa source', 'Портал электронной визы МИД полезен для проверки краткосрочного въезда, но не заменяет консультацию по проживанию.', 'https://evisa.kdmid.ru/', 'Разрешение на въезд и статус резидентства являются отдельными уровнями скрининга.', 'procedure', 'high', DATE '2026-06-19', 'Проверку краткосрочного въезда следует отделять от анализа резидентства.', 'Официальный источник электронной визы для доказательств въездного контекста.'),
            ('russia', 'https://www.consultant.ru/document/cons_doc_LAW_445998/', 'Гражданство требует отдельной правовой проверки', 'Russia citizenship law baseline', 'Закон о гражданстве создаёт отдельную правовую основу для натурализации и гражданского статуса.', 'https://www.consultant.ru/document/cons_doc_LAW_445998/', 'Анализ гражданства не должен выводиться только из оценки резидентства.', 'legal_basis', 'high', DATE '2026-06-19', 'Гражданство России регулируется специальным федеральным законом о гражданстве.', 'Первичный источник по гражданству для скрининга долгосрочного статуса.'),
            ('russia', 'https://www.consultant.ru/document/cons_doc_LAW_37868/', 'Гражданство требует отдельной правовой проверки', 'Russia residence-to-status dependency', 'Правила проживания и статуса иностранных граждан сохраняют актуальность до рассмотрения любого пути к гражданству.', 'https://www.consultant.ru/document/cons_doc_LAW_37868/', 'Долгосрочный путь начинается с отдельного уровня соблюдения требований проживания.', 'legal_basis', 'high', DATE '2026-06-19', 'Скрининг долгосрочного статуса зависит как от правовых уровней проживания, так и гражданства.', 'Первичный источник по проживанию как зависимость для скрининга гражданства.'),
            ('russia', 'https://data.worldbank.org/indicator/PV.EST?locations=RU', 'Гражданство требует отдельной правовой проверки', 'Russia long-term risk context', 'Данные по политической стабильности добавляют риск-контекст для долгосрочных решений.', 'https://data.worldbank.org/indicator/PV.EST?locations=RU', 'Долгосрочный статус должен учитывать показатели рисков управления.', 'dataset', 'high', DATE '2026-06-19', 'Долгосрочное планирование должно учитывать внешние данные по управлению.', 'Показатель управления Всемирного банка для риск-контекста.'),
            ('russia', 'https://npd.nalog.ru/', 'Налог на профессиональный доход имеет официальное цифровое руководство', 'Russia self-employed tax portal evidence', 'Портал ФНС предоставляет официальный источник для скрининга налога на профессиональный доход.', 'https://npd.nalog.ru/', 'Соответствие требованиям и взаимодействие с налоговым резидентством всё равно требуют проверки.', 'tax', 'high', DATE '2026-06-19', 'Налог на профессиональный доход имеет официальный цифровой информационный источник.', 'Официальный источник ФНС для скрининга самозанятости.'),
            ('russia', 'https://www.nalog.gov.ru/rn77/taxation/taxes/ndfl/', 'Налог на профессиональный доход имеет официальное цифровое руководство', 'Russia personal income tax evidence', 'Страница ФНС по НДФЛ актуальна для индивидуальной налоговой нагрузки.', 'https://www.nalog.gov.ru/rn77/taxation/taxes/ndfl/', 'Личное налогообложение следует проверять наряду с любым специальным режимом.', 'tax', 'high', DATE '2026-06-19', 'НДФЛ остаётся отдельным скрининговым элементом, обеспеченным источниками.', 'Официальный налоговый источник ФНС для скрининга индивидуального налогообложения.'),
            ('russia', 'https://www.cbr.ru/eng/banking_sector/', 'Налог на профессиональный доход имеет официальное цифровое руководство', 'Russia banking context for freelancers', 'Контекст надзора за банковским сектором важен для фрилансеров и пользователей малого бизнеса.', 'https://www.cbr.ru/eng/banking_sector/', 'Налоговое планирование следует сочетать с проверкой банковской готовности.', 'banking', 'high', DATE '2026-06-19', 'Планирование независимой работы также зависит от доступности банковских услуг.', 'Источник центрального банка для контекста финансовой операционности.'),
            ('russia', 'https://www.cbr.ru/eng/psystem/', 'Контекст платёжной системы следует проверить до релокации', 'Russia payment-system evidence', 'Страница центрального банка по платёжной системе поддерживает скрининг доступности карт, переводов и платежей.', 'https://www.cbr.ru/eng/psystem/', 'Платёжная инфраструктура может влиять на практическую осуществимость релокации.', 'banking', 'high', DATE '2026-06-19', 'Скрининг релокации должен включать проверку готовности платёжной системы.', 'Источник центрального банка для доказательств платёжной системы.'),
            ('russia', 'https://www.cbr.ru/eng/banking_sector/', 'Контекст платёжной системы следует проверить до релокации', 'Russia banking-sector evidence', 'Источник по банковскому сектору поддерживает финансово-системную проверку.', 'https://www.cbr.ru/eng/banking_sector/', 'Доступ к счетам и регулируемый банковский контекст следует проверять заблаговременно.', 'banking', 'high', DATE '2026-06-19', 'Надзор за банковским сектором актуален для ежедневного финансового доступа.', 'Источник центрального банка для доказательств банковского сектора.'),
            ('russia', 'https://www.nalog.gov.ru/eng/', 'Контекст платёжной системы следует проверить до релокации', 'Russia financial administration evidence', 'Источник ФНС добавляет контекст государственного администрирования для финансовых и налоговых процессов.', 'https://www.nalog.gov.ru/eng/', 'Финансовая готовность включает точки контакта с налоговым администрированием.', 'tax', 'high', DATE '2026-06-19', 'Налоговые и банковские процессы взаимодействуют при практическом планировании релокации.', 'Официальный налоговый источник для контекста финансового администрирования.'),
            ('russia', 'https://data.worldbank.org/indicator/PV.EST?locations=RU', 'Набор данных по политической стабильности добавляет внешний риск-контекст', 'Russia political stability dataset evidence', 'Показатель политической стабильности Всемирного банка предоставляет внешние данные для оценки рисков.', 'https://data.worldbank.org/indicator/PV.EST?locations=RU', 'Внешние данные по управлению должны быть видны в риск-чувствительных решениях.', 'dataset', 'high', DATE '2026-06-19', 'Данные по политической стабильности актуальны для оценки безопасности и правовой стабильности.', 'Источник управления Всемирного банка для доказательств политических рисков.'),
            ('russia', 'https://freedomhouse.org/country/russia/freedom-world/2026', 'Набор данных по политической стабильности добавляет внешний риск-контекст', 'Russia Freedom House evidence', 'Профиль Freedom House добавляет внешний источник по гражданским и политическим правам.', 'https://freedomhouse.org/country/russia/freedom-world/2026', 'Данные по правам и свободам должны учитываться в риск-предупреждениях.', 'research', 'medium', DATE '2026-06-19', 'Внешние оценки свободы являются частью набора риск-доказательств.', 'Источник Freedom House для контекста безопасности и свободы.'),
            ('russia', 'https://worldjusticeproject.org/rule-of-law-index/downloads/2025/WJPIndex2025.pdf', 'Набор данных по политической стабильности добавляет внешний риск-контекст', 'Russia rule-of-law evidence', 'Набор данных WJP добавляет контекст верховенства права для оценки правовой стабильности.', 'https://worldjusticeproject.org/rule-of-law-index/downloads/2025/WJPIndex2025.pdf', 'Контекст верховенства права должен быть виден при долгосрочной оценке рисков.', 'dataset', 'high', DATE '2026-06-19', 'Доказательства верховенства права дополняют данные политической стабильности.', 'Источник WJP для доказательств правовой стабильности.'),
            ('uruguay', 'https://www.gub.uy/tramites/residencia-legal-temporaria', 'Временная легальная резиденция имеет официальную процедурную страницу', 'Uruguay temporary residence procedure evidence', 'Официальная процедурная страница поддерживает первичный скрининг резидентства.', 'https://www.gub.uy/tramites/residencia-legal-temporaria', 'Пользователи могут начать с конкретного государственного процедурного источника.', 'procedure', 'high', DATE '2026-06-19', 'Временная резиденция описана на официальной государственной процедурной странице.', 'Официальный процедурный источник для скрининга релокации.'),
            ('uruguay', 'https://www.gub.uy/tramites/residencia-legal-permanente', 'Временная легальная резиденция имеет официальную процедурную страницу', 'Uruguay permanent residence procedure evidence', 'Процедура постоянной резиденции даёт связанный источник долгосрочного статуса.', 'https://www.gub.uy/tramites/residencia-legal-permanente', 'Временный и постоянный статус следует рассматривать отдельно.', 'procedure', 'high', DATE '2026-06-19', 'Планирование резидентства может сравнивать источники по временным и постоянным процедурам.', 'Официальный процедурный источник для контекста долгосрочного статуса.'),
            ('uruguay', 'https://www.gub.uy/direccion-nacional-migracion/', 'Временная легальная резиденция имеет официальную процедурную страницу', 'Uruguay migration authority evidence', 'Источник миграционного органа поддерживает маршрутизацию проверок, связанных с резидентством.', 'https://www.gub.uy/direccion-nacional-migracion/', 'Охват источниками на уровне органа улучшает прослеживаемость.', 'procedure', 'high', DATE '2026-06-19', 'Проверки процедур резидентства должны опираться на миграционный орган.', 'Официальный источник миграционного органа для процессного контекста.'),
            ('uruguay', 'https://www.impo.com.uy/bases/leyes/18250-2008', 'Миграционный закон обеспечивает стабильную законодательную основу', 'Uruguay migration law evidence', 'Миграционный закон 18250 предоставляет законодательную основу для анализа миграции и резидентства.', 'https://www.impo.com.uy/bases/leyes/18250-2008', 'Процедурные источники следует читать вместе с законодательством.', 'legal_basis', 'high', DATE '2026-06-19', 'Скрининг миграции Уругвая имеет официальный законодательный якорь.', 'Официальный правовой источник для доказательств миграционного закона.'),
            ('uruguay', 'https://www.gub.uy/ministerio-interior/comunicacion/publicaciones/types-of-residencies-in-uruguay', 'Миграционный закон обеспечивает стабильную законодательную основу', 'Uruguay residence-type overview evidence', 'Обзор Министерства внутренних дел помогает различать категории резидентства.', 'https://www.gub.uy/ministerio-interior/comunicacion/publicaciones/types-of-residencies-in-uruguay', 'Категории резидентства не следует сводить к одному общему пути.', 'procedure', 'high', DATE '2026-06-19', 'Руководство по типам резидентства улучшает ориентированные на решения резюме.', 'Официальный обзорный источник для скрининга категорий.'),
            ('uruguay', 'https://www.impo.com.uy/bases/constitucion/1967-1967', 'Миграционный закон обеспечивает стабильную законодательную основу', 'Uruguay constitutional context evidence', 'Конституция предоставляет первичный правовой контекст для анализа долгосрочной стабильности.', 'https://www.impo.com.uy/bases/constitucion/1967-1967', 'Миграционный анализ выигрывает от более широкого источника правовой стабильности.', 'legal_basis', 'high', DATE '2026-06-19', 'Скрининг правовой стабильности может ссылаться на конституционный текст.', 'Официальный конституционный источник для правового контекста.'),
            ('uruguay', 'https://www.gub.uy/direccion-general-impositiva/', 'Налоговое администрирование имеет специальный официальный источник', 'Uruguay tax authority evidence', 'Источник DGI является основным якорем налогового администрирования для скрининга пользователей.', 'https://www.gub.uy/direccion-general-impositiva/', 'Налоговое планирование следует проверять по официальным материалам DGI.', 'tax', 'high', DATE '2026-06-19', 'Налоговое администрирование Уругвая имеет официальный источник.', 'Официальный налоговый источник для скрининга резидентства и бизнеса.'),
            ('uruguay', 'https://www.gub.uy/ministerio-economia-finanzas/', 'Налоговое администрирование имеет специальный официальный источник', 'Uruguay economy ministry evidence', 'Источник Министерства экономики и финансов добавляет официальный фискальный контекст.', 'https://www.gub.uy/ministerio-economia-finanzas/', 'Налоговые и фискальные проверки должны использовать министерские источники там, где это применимо.', 'tax', 'high', DATE '2026-06-19', 'Фискальный контекст поддерживает скрининг налогов и стоимости жизни.', 'Официальный министерский источник для фискального контекста.'),
            ('uruguay', 'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=UY', 'Налоговое администрирование имеет специальный официальный источник', 'Uruguay inflation dataset evidence', 'Показатель инфляции добавляет внешний контекст для планирования расходов и налогов.', 'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=UY', 'Планирование расходов должно включать подкреплённый данными контекст инфляции.', 'dataset', 'high', DATE '2026-06-19', 'Данные по инфляции поддерживают скрининг стоимости жизни.', 'Источник Всемирного банка для ценового контекста.'),
            ('uruguay', 'https://www.bcu.gub.uy/Servicios-Financieros-SSF/Paginas/Default.aspx', 'Надзор за финансовыми услугами поддерживает банковские проверки', 'Uruguay financial supervisor evidence', 'Источник надзора центрального банка поддерживает финансово-сервисную проверку.', 'https://www.bcu.gub.uy/Servicios-Financieros-SSF/Paginas/Default.aspx', 'Банковская готовность должна включать проверки регулируемого сектора.', 'banking', 'high', DATE '2026-06-19', 'Данные финансового надзора актуальны для скрининга готовности счетов.', 'Источник центрального банка для банковских доказательств.'),
            ('uruguay', 'https://www.bcu.gub.uy/', 'Надзор за финансовыми услугами поддерживает банковские проверки', 'Uruguay central bank evidence', 'Источник центрального банка закрепляет денежный и банковский контекст.', 'https://www.bcu.gub.uy/', 'Банковские проверки должны использовать семейство источников центрального банка.', 'banking', 'high', DATE '2026-06-19', 'Охват источниками центрального банка укрепляет контекст финансовой системы.', 'Источник центрального банка для институциональных доказательств.'),
            ('uruguay', 'https://archive.doingbusiness.org/en/data/exploreeconomies/uruguay', 'Надзор за финансовыми услугами поддерживает банковские проверки', 'Uruguay business-regulation archive evidence', 'Архив Doing Business предоставляет исторический контекст регулирования бизнеса.', 'https://archive.doingbusiness.org/en/data/exploreeconomies/uruguay', 'Скрининг создания бизнеса должен отличать архивный контекст наборов данных от текущей юридической консультации.', 'dataset', 'medium', DATE '2026-06-19', 'Архивные данные по регулированию бизнеса остаются полезными как фоновый контекст.', 'Архивный источник Всемирного банка для бизнес-контекстных доказательств.'),
            ('uruguay', 'https://www.impo.com.uy/bases/constitucion/1967-1967', 'Конституционный текст закрепляет контекст верховенства права', 'Uruguay constitution evidence', 'Конституция является первичным источником для контекста правовой стабильности.', 'https://www.impo.com.uy/bases/constitucion/1967-1967', 'Охват конституционными источниками поддерживает скрининг верховенства права.', 'legal_basis', 'high', DATE '2026-06-19', 'Анализ верховенства права должен включать первичный правовой текст.', 'Официальный конституционный источник для доказательств правовой стабильности.'),
            ('uruguay', 'https://worldjusticeproject.org/rule-of-law-index/global/2025', 'Конституционный текст закрепляет контекст верховенства права', 'Uruguay rule-of-law index evidence', 'Глобальный индекс WJP добавляет сравнительный контекст верховенства права.', 'https://worldjusticeproject.org/rule-of-law-index/global/2025', 'Сравнительные данные верховенства права дополняют первичный правовой текст.', 'dataset', 'high', DATE '2026-06-19', 'Скрининг правовой стабильности должен сочетать первичное право со сравнительными наборами данных.', 'Источник WJP для сравнительных доказательств правовой стабильности.'),
            ('uruguay', 'https://freedomhouse.org/country/uruguay/freedom-world/2024', 'Конституционный текст закрепляет контекст верховенства права', 'Uruguay freedom profile evidence', 'Страновой профиль Freedom House добавляет внешний контекст политических прав.', 'https://freedomhouse.org/country/uruguay/freedom-world/2024', 'Источники прав и свобод должны быть видны при оценке рисков.', 'research', 'medium', DATE '2026-06-19', 'Оценки свободы дополняют доказательства правовой стабильности.', 'Источник Freedom House для риск-контекста.')
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
            ('russia', 'relocation_residence', 'Russia has official entry and residence sources, but the legal-status baseline, procedure burden and banking checks keep relocation suitability limited without expert review.', 'У России есть официальные источники по въезду и проживанию, но закон о статусе иностранцев, процедурная нагрузка и банковские проверки ограничивают пригодность без экспертной проверки.', 'Скрининг источниками указывает на высокую процедурную нагрузку.'),
            ('russia', 'permanent_residence_citizenship', 'Long-term status is weaker because residence and citizenship are separate legal layers and external governance datasets add material risk context.', 'Долгосрочный статус слабее, потому что проживание и гражданство являются отдельными правовыми слоями, а внешние governance-данные добавляют существенный риск.', 'Долгосрочное планирование требует отдельной правовой и риск-проверки.'),
            ('russia', 'low_budget_living', 'Cost indicators are available, but practical budgeting depends on city, payment access and inflation context, so the score remains a cautious screening estimate.', 'Показатели стоимости доступны, но практический бюджет зависит от города, платежного доступа и инфляционного контекста, поэтому оценка остается осторожной.', 'Скрининг расходов подкреплён данными, но чувствителен к уровню города.'),
            ('russia', 'business_self_employment', 'Official self-employed tax and banking sources improve visibility, yet account access, tax residency and compliance questions make the route review-heavy.', 'Официальные источники по НПД и банковскому сектору повышают прозрачность, но доступ к счетам, налоговое резидентство и комплаенс требуют глубокой проверки.', 'Бизнес-маршрут подкреплён источниками, но требует интенсивной проверки.'),
            ('russia', 'safety_political_risk', 'External political-stability, freedom and rule-of-law datasets make risk warnings central to the score, even where official administrative sources are available.', 'Внешние данные по политической стабильности, свободам и верховенству права делают риск-предупреждения центральными для оценки, даже при наличии официальных административных источников.', 'Наборы риск-данных определяют осторожную оценку безопасности.'),
            ('uruguay', 'relocation_residence', 'Uruguay has official temporary and permanent residence procedure pages plus a migration-law source, supporting a stronger relocation screening score.', 'У Уругвая есть официальные страницы временной и постоянной резиденции, а также миграционный закон, что поддерживает более сильную релокационную оценку.', 'Путь к резидентству имеет более сильную публичную прослеживаемость.'),
            ('uruguay', 'permanent_residence_citizenship', 'Long-term planning benefits from migration law, permanent-residence procedure sources and constitutional context, while still requiring case-specific confirmation.', 'Долгосрочное планирование опирается на миграционный закон, процедуры постоянной резиденции и конституционный контекст, но все равно требует индивидуального подтверждения.', 'Долгосрочный статус сравнительно прослеживаем.'),
            ('uruguay', 'low_budget_living', 'World Bank and national statistical sources support cost screening, but housing and private-service costs still need city-level validation.', 'Источники World Bank и национальной статистики поддерживают оценку стоимости, но жилье и частные услуги нужно проверять по конкретному городу.', 'Скрининг расходов имеет надёжное покрытие наборами данных.'),
            ('uruguay', 'business_self_employment', 'Tax authority, economy ministry, central-bank and archived business-regulation sources give Uruguay a stronger business-readiness evidence base.', 'Налоговый орган, министерство экономики, центральный банк и архивные бизнес-данные дают Уругваю более сильную доказательную базу для бизнеса.', 'Бизнес-скрининг имеет несколько официальных якорей.'),
            ('uruguay', 'safety_political_risk', 'Freedom, rule-of-law, governance and constitutional sources support a comparatively stronger risk-sensitive profile, with normal filing and verification risk remaining.', 'Источники по свободам, верховенству права, governance и конституции поддерживают более сильный профиль для риск-чувствительных решений, при сохранении обычных процедурных рисков.', 'Риск-профиль поддержан официальными и внешними источниками.')
    ) AS rows(country_slug, scenario_slug, explanation_en, explanation_ru, summary)
)
UPDATE country_scores cs
SET
    explanation_en = sr.explanation_en,
    explanation_ru = sr.explanation_ru,
    summary = sr.summary,
    score_label = 'Скрининговая оценка с источниками',
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
