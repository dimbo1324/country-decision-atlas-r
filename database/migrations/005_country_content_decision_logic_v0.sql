WITH country_card_rows AS (
    SELECT *
    FROM (
        VALUES
            (
                'russia',
                'en',
                'Russia is a high-friction decision context: useful as an origin and risk baseline, but difficult to treat as a simple relocation destination without case-specific legal, banking, tax, and safety review.',
                'Migration and legal stay decisions depend on status, documentation, sanctions exposure, and changing administrative practice. This card treats Russia primarily as a baseline for origin-risk and institutional-risk comparison.',
                'Tax position can change with residency, income source, currency controls, and treaty context. Users should treat tax notes as screening signals only, not personal advice.',
                'Large-city costs can be materially different from regional costs. Affordability may look moderate in some datasets, but risk, payment access, and mobility constraints change the practical picture.',
                'Business and self-employment planning is constrained by banking access, compliance exposure, payment rails, and geopolitical restrictions. Source checks should precede any operational decision.',
                'The main safety issue is not only street-level risk but institutional, political, rule-of-law, and exit-planning uncertainty. Long-term decisions need conservative assumptions.',
                'The strongest signals are political-risk, rule-of-law, banking, migration-documentation, and information-reliability signals.',
                'Main risks: fast-changing rules, banking friction, administrative unpredictability, sanctions-sensitive workflows, and weak confidence for personal outcomes.',
                'Sources emphasize official portals, tax and central-bank material, international indicators, and institutional datasets. This is MVP screening content, not legal advice.'
            ),
            (
                'russia',
                'ru',
                'Россия в этой модели является контекстом с высокой правовой и институциональной сложностью: полезна как страна исхода и риск-бенчмарк, но не как простое направление для релокации без индивидуальной проверки.',
                'Миграционные и статусные решения зависят от документов, текущего положения человека, санкционного контекста и меняющейся административной практики. Карточка использует Россию прежде всего как базовую точку сравнения рисков.',
                'Налоговая позиция зависит от резидентства, источников дохода, валютных ограничений и договорного контекста. Это только первичный аналитический сигнал, не персональная консультация.',
                'Расходы в крупных городах и регионах различаются. Формальная доступность может выглядеть умеренной, но платежи, мобильность и риск-контекст меняют практическую оценку.',
                'Бизнес и самозанятость ограничиваются банковским доступом, комплаенсом, платежной инфраструктурой и геополитическими факторами. Перед действиями нужны актуальные источники.',
                'Ключевой риск связан не только с бытовой безопасностью, но и с институтами, политическим риском, правовой предсказуемостью и возможностью планировать выезд.',
                'Наиболее важные сигналы: политический риск, верховенство права, банковская инфраструктура, миграционные документы и качество источников.',
                'Главные риски: быстрая смена правил, банковские ограничения, административная непредсказуемость, санкционно-чувствительные процессы и низкая персональная определенность.',
                'Источники включают официальные порталы, налоговые и банковские материалы, международные индексы и институциональные данные. Это MVP-скрининг, не юридическая консультация.'
            ),
            (
                'uruguay',
                'en',
                'Uruguay is a comparatively stable candidate for residence-oriented planning, but it is not a low-cost shortcut: housing, bureaucracy, banking, and tax-residence details can materially affect fit.',
                'Uruguay is relatively open as a residence-planning jurisdiction, with official procedures and public-facing migration information. The practical route still depends on documents, timing, income, and professional review.',
                'Tax planning depends on residence status, source of income, and current incentives or exemptions. Treat this as a screening topic for professional advice.',
                'Montevideo and coastal areas can be expensive relative to regional expectations. Uruguay may suit users who value stability more than the lowest possible monthly budget.',
                'Small business and self-employment are plausible, but banking onboarding, local compliance, payment flows, and Spanish-language administration require preparation.',
                'Uruguay scores well as a stability and rule-of-law candidate in the MVP model, with lower political-risk pressure than many alternatives. Personal safety still varies by location.',
                'Relevant signals include residence procedure clarity, tax-residence rules, banking practicality, cost pressure, and institutional stability.',
                'Main risks: cost of living, housing, bureaucracy, slower processes, language friction, and overestimating how easy banking or tax setup will be.',
                'Sources emphasize official government portals, migration material, tax-residence guidance, central-bank material, and international indices. This is MVP screening content, not legal advice.'
            ),
            (
                'uruguay',
                'ru',
                'Уругвай выглядит сравнительно стабильным кандидатом для планирования ВНЖ и долгосрочного проживания, но это не дешевый обходной путь: жилье, бюрократия, банки и налоговое резидентство сильно влияют на итоговую пригодность.',
                'Уругвай сравнительно открыт для планирования резидентства и имеет публичные официальные процедуры. Практический маршрут зависит от документов, сроков, дохода и профессиональной проверки.',
                'Налоговая логика зависит от резидентства, источника дохода и действующих льгот или режимов. Это тема для предварительного скрининга и профессиональной консультации.',
                'Монтевидео и прибрежные зоны могут быть дорогими относительно ожиданий по региону. Уругвай больше подходит тем, кто ценит стабильность выше минимального бюджета.',
                'Малый бизнес и самозанятость возможны, но банковское открытие, локальный комплаенс, платежи и испаноязычная администрация требуют подготовки.',
                'В MVP-модели Уругвай получает сильные оценки по стабильности и правовой среде, с меньшим политическим давлением, чем у многих альтернатив. Бытовая безопасность зависит от места.',
                'Важные сигналы: понятность процедур ВНЖ, налоговое резидентство, банковская практичность, стоимость жизни и институциональная стабильность.',
                'Главные риски: стоимость жизни, жилье, бюрократия, медленные процессы, языковой барьер и переоценка простоты банковской или налоговой настройки.',
                'Источники включают официальные порталы, миграционные материалы, налоговую информацию, центральный банк и международные индексы. Это MVP-скрининг, не юридическая консультация.'
            )
    ) AS card(
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
INSERT INTO
    country_cards (
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
    card.locale,
    card.executive_summary,
    card.migration_overview,
    card.tax_overview,
    card.cost_of_living_overview,
    card.business_overview,
    card.safety_overview,
    card.legal_signals_summary,
    card.risk_summary,
    card.source_summary,
    'published'
FROM
    country_card_rows card
    JOIN countries c ON c.slug = card.country_slug ON CONFLICT (country_id, locale) DO
UPDATE
SET
    executive_summary = EXCLUDED.executive_summary,
    migration_overview = EXCLUDED.migration_overview,
    tax_overview = EXCLUDED.tax_overview,
    cost_of_living_overview = EXCLUDED.cost_of_living_overview,
    business_overview = EXCLUDED.business_overview,
    safety_overview = EXCLUDED.safety_overview,
    legal_signals_summary = EXCLUDED.legal_signals_summary,
    risk_summary = EXCLUDED.risk_summary,
    source_summary = EXCLUDED.source_summary,
    status = EXCLUDED.status;

WITH profile_rows AS (
    SELECT *
    FROM (
        VALUES
            (
                'russia',
                'Russia is a high-risk baseline for country-decision comparison, with material legal, banking, political, and mobility uncertainty.',
                'Residence and legal stay questions require current document review and should not be inferred from generic rules.',
                'Long-term status and citizenship planning are highly case-specific and sensitive to rule changes.',
                'Tax exposure depends on residence, income source, currency restrictions, and treaty context.',
                'Business activity faces banking, payment, sanctions, and compliance friction.',
                'Quality of life varies by location, but institutional and mobility risks dominate the decision model.',
                'Primary risks are administrative unpredictability, geopolitical exposure, banking friction, and weak personal certainty.'
            ),
            (
                'uruguay',
                'Uruguay is a stability-oriented candidate for residence and lifestyle planning, with meaningful tradeoffs around cost, bureaucracy, and banking.',
                'Residence planning is comparatively legible, but document readiness and current procedure checks remain essential.',
                'Long-term residence and citizenship may be realistic, but timelines and continuity rules require verification.',
                'Tax treatment depends on residence status, income source, and current professional guidance.',
                'Small business and self-employment are plausible but need banking and compliance planning.',
                'Quality of life may be strong for stability-oriented users, while Montevideo costs and housing can be constraints.',
                'Primary risks are cost of living, administrative delays, labour-market limits, housing, and banking friction.'
            )
    ) AS profile(
        country_slug,
        summary,
        residence_overview,
        citizenship_overview,
        tax_overview,
        business_overview,
        quality_of_life_overview,
        risk_overview
    )
)
INSERT INTO
    country_profiles (
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
    c.id,
    profile.summary,
    profile.residence_overview,
    profile.citizenship_overview,
    profile.tax_overview,
    profile.business_overview,
    profile.quality_of_life_overview,
    profile.risk_overview
FROM
    profile_rows profile
    JOIN countries c ON c.slug = profile.country_slug ON CONFLICT (country_id) DO
UPDATE
SET
    summary = EXCLUDED.summary,
    residence_overview = EXCLUDED.residence_overview,
    citizenship_overview = EXCLUDED.citizenship_overview,
    tax_overview = EXCLUDED.tax_overview,
    business_overview = EXCLUDED.business_overview,
    quality_of_life_overview = EXCLUDED.quality_of_life_overview,
    risk_overview = EXCLUDED.risk_overview;

WITH source_rows AS (
    SELECT *
    FROM (
        VALUES
            (
                'russia',
                'Russia Ministry of Foreign Affairs electronic visa portal',
                'https://evisa.kdmid.ru/',
                'official',
                'Ministry of Foreign Affairs of the Russian Federation',
                'en',
                'high',
                DATE '2026-06-18',
                'Official entry and visa portal used as a high-confidence migration source.'
            ),
            (
                'russia',
                'Russian Federal Tax Service English portal',
                'https://www.nalog.gov.ru/eng/',
                'official',
                'Federal Tax Service of Russia',
                'en',
                'high',
                DATE '2026-06-18',
                'Official tax authority portal used for tax-context screening.'
            ),
            (
                'russia',
                'Central Bank of Russia English portal',
                'https://www.cbr.ru/eng/',
                'official',
                'Bank of Russia',
                'en',
                'high',
                DATE '2026-06-18',
                'Official central-bank source for banking and financial-system context.'
            ),
            (
                'russia',
                'Russia public services portal',
                'https://www.gosuslugi.ru/',
                'official',
                'Gosuslugi',
                'ru',
                'medium',
                DATE '2026-06-18',
                'Official public services portal; confidence is medium for non-personalized decision use.'
            ),
            (
                'russia',
                'World Bank Russia country data',
                'https://data.worldbank.org/country/russian-federation',
                'dataset',
                'World Bank',
                'en',
                'high',
                DATE '2026-06-18',
                'Institutional dataset for macro and country-level screening indicators.'
            ),
            (
                'russia',
                'Freedom House Russia country profile',
                'https://freedomhouse.org/country/russia/freedom-world/2026',
                'research',
                'Freedom House',
                'en',
                'medium',
                DATE '2026-06-18',
                'Institutional research source for political-rights and civil-liberties context.'
            ),
            (
                'russia',
                'World Justice Project Rule of Law Index',
                'https://worldjusticeproject.org/rule-of-law-index/downloads/2025/WJPIndex2025.pdf',
                'dataset',
                'World Justice Project',
                'en',
                'high',
                DATE '2026-06-18',
                'Institutional rule-of-law dataset for comparative legal-stability screening.'
            ),
            (
                'russia',
                'World Bank Doing Business Russia archive',
                'https://archive.doingbusiness.org/en/data/exploreeconomies/russia',
                'dataset',
                'World Bank',
                'en',
                'medium',
                DATE '2026-06-18',
                'Archived business-environment dataset used cautiously for historical context.'
            ),
            (
                'russia',
                'ConsultantPlus Russian Tax Code reference',
                'https://www.consultant.ru/document/cons_doc_LAW_19671/',
                'expert',
                'ConsultantPlus',
                'ru',
                'medium',
                DATE '2026-06-18',
                'Legal reference source for tax-code screening, not a substitute for legal advice.'
            ),
            (
                'russia',
                'Official Russian government portal',
                'http://government.ru/en/',
                'official',
                'Government of the Russian Federation',
                'en',
                'medium',
                DATE '2026-06-18',
                'Official government information portal used for institutional context.'
            ),
            (
                'uruguay',
                'Uruguay Ministry of Interior residence types',
                'https://www.gub.uy/ministerio-interior/comunicacion/publicaciones/types-of-residencies-in-uruguay',
                'official',
                'Ministry of Interior of Uruguay',
                'en',
                'high',
                DATE '2026-06-18',
                'Official migration source for residence-category screening.'
            ),
            (
                'uruguay',
                'Uruguay permanent legal residence procedure',
                'https://www.gub.uy/tramites/residencia-legal-permanente',
                'official',
                'Government of Uruguay',
                'es',
                'high',
                DATE '2026-06-18',
                'Official procedure page for permanent legal residence.'
            ),
            (
                'uruguay',
                'Live in Uruguay tax residence overview',
                'https://www.liveinuruguay.uy/tax-residence',
                'official',
                'Uruguay XXI',
                'en',
                'medium',
                DATE '2026-06-18',
                'Government investment-promotion source used for tax-residence screening.'
            ),
            (
                'uruguay',
                'Uruguay National Migration Directorate',
                'https://www.gub.uy/direccion-nacional-migracion/',
                'official',
                'National Migration Directorate of Uruguay',
                'es',
                'high',
                DATE '2026-06-18',
                'Official migration authority portal.'
            ),
            (
                'uruguay',
                'Central Bank of Uruguay',
                'https://www.bcu.gub.uy/',
                'official',
                'Central Bank of Uruguay',
                'es',
                'high',
                DATE '2026-06-18',
                'Official source for financial-system and banking context.'
            ),
            (
                'uruguay',
                'Uruguay Ministry of Economy and Finance',
                'https://www.gub.uy/ministerio-economia-finanzas/',
                'official',
                'Ministry of Economy and Finance of Uruguay',
                'es',
                'high',
                DATE '2026-06-18',
                'Official source for economic and tax-policy context.'
            ),
            (
                'uruguay',
                'World Bank Uruguay country data',
                'https://data.worldbank.org/country/uruguay',
                'dataset',
                'World Bank',
                'en',
                'high',
                DATE '2026-06-18',
                'Institutional dataset for macro and country-level screening indicators.'
            ),
            (
                'uruguay',
                'World Bank Uruguay country overview',
                'https://www.worldbank.org/ext/en/country/uruguay',
                'research',
                'World Bank',
                'en',
                'medium',
                DATE '2026-06-18',
                'Institutional country overview for economic and development context.'
            ),
            (
                'uruguay',
                'Freedom House Uruguay country profile',
                'https://freedomhouse.org/country/uruguay/freedom-world/2024',
                'research',
                'Freedom House',
                'en',
                'medium',
                DATE '2026-06-18',
                'Institutional research source for political-rights and civil-liberties context.'
            ),
            (
                'uruguay',
                'World Justice Project Rule of Law Index',
                'https://worldjusticeproject.org/rule-of-law-index/global/2025',
                'dataset',
                'World Justice Project',
                'en',
                'high',
                DATE '2026-06-18',
                'Institutional rule-of-law dataset for comparative legal-stability screening.'
            )
    ) AS source(
        country_slug,
        title,
        url,
        source_type,
        publisher,
        language,
        confidence,
        last_checked_at,
        notes
    )
)
INSERT INTO
    sources (
        title,
        url,
        source_type,
        publisher,
        country_id,
        language,
        reliability_level,
        confidence,
        published_at,
        accessed_at,
        last_checked_at,
        notes
    )
SELECT
    source.title,
    source.url,
    source.source_type,
    source.publisher,
    c.id,
    source.language,
    source.confidence,
    source.confidence,
    DATE '2026-06-18',
    source.last_checked_at,
    source.last_checked_at,
    source.notes
FROM
    source_rows source
    JOIN countries c ON c.slug = source.country_slug ON CONFLICT (url) DO
UPDATE
SET
    title = EXCLUDED.title,
    source_type = EXCLUDED.source_type,
    publisher = EXCLUDED.publisher,
    country_id = EXCLUDED.country_id,
    language = EXCLUDED.language,
    reliability_level = EXCLUDED.reliability_level,
    confidence = EXCLUDED.confidence,
    accessed_at = EXCLUDED.accessed_at,
    last_checked_at = EXCLUDED.last_checked_at,
    notes = EXCLUDED.notes;

WITH signal_rows AS (
    SELECT *
    FROM (
        VALUES
            (
                'russia',
                'https://evisa.kdmid.ru/',
                'Electronic visa process is useful but narrow',
                'Электронная виза полезна, но не заменяет статусный маршрут',
                'Official e-visa infrastructure supports entry screening, but it should not be read as a residence or long-term legalization pathway.',
                'Официальная инфраструктура электронной визы помогает оценить въезд, но не является маршрутом ВНЖ или долгосрочной легализации.',
                'policy',
                'mixed',
                'medium',
                '["relocators","short_term_visitors"]',
                'high'
            ),
            (
                'russia',
                'https://www.nalog.gov.ru/eng/',
                'Tax-residency review is required before planning',
                'Перед планированием нужна проверка налогового резидентства',
                'Russia-related tax exposure depends on residence, income source, and current rule interpretation, so the MVP score treats it as a review-heavy area.',
                'Налоговая позиция, связанная с Россией, зависит от резидентства, источника дохода и актуального толкования правил, поэтому в MVP это зона обязательной проверки.',
                'policy',
                'uncertain',
                'medium',
                '["remote_workers","entrepreneurs","families"]',
                'medium'
            ),
            (
                'russia',
                'https://www.cbr.ru/eng/',
                'Banking access and payment rails are major planning constraints',
                'Банковский доступ и платежи являются ключевыми ограничениями',
                'Central-bank and financial-system context make banking and payment reliability a material constraint for business or relocation planning.',
                'Банковская и финансовая среда делает доступ к платежам и счетам существенным ограничением для бизнеса и релокации.',
                'policy',
                'negative',
                'high',
                '["entrepreneurs","remote_workers","families"]',
                'high'
            ),
            (
                'russia',
                'https://freedomhouse.org/country/russia/freedom-world/2026',
                'Political and civil-liberties risk affects long-term fit',
                'Политические и гражданские риски влияют на долгосрочную пригодность',
                'Institutional risk indicators make Russia a high-risk context for safety, freedom, and long-term predictability in this MVP model.',
                'Институциональные индикаторы делают Россию рискованным контекстом для безопасности, свобод и долгосрочной предсказуемости в MVP-модели.',
                'political_signal',
                'negative',
                'high',
                '["families","entrepreneurs","students"]',
                'medium'
            ),
            (
                'russia',
                'https://worldjusticeproject.org/rule-of-law-index/downloads/2025/WJPIndex2025.pdf',
                'Rule-of-law indicators reduce legal-stability score',
                'Индикаторы верховенства права снижают оценку правовой стабильности',
                'Comparative rule-of-law data supports a conservative legal-stability assessment for Russia.',
                'Сравнительные данные по верховенству права поддерживают консервативную оценку правовой стабильности России.',
                'other',
                'negative',
                'high',
                '["long_term_relocators","investors","families"]',
                'high'
            ),
            (
                'uruguay',
                'https://www.gub.uy/ministerio-interior/comunicacion/publicaciones/types-of-residencies-in-uruguay',
                'Residence categories are publicly documented',
                'Категории резидентства публично описаны',
                'Official public information on residence categories supports Uruguay as a comparatively legible residence-planning jurisdiction.',
                'Официальная публичная информация о категориях резидентства делает Уругвай сравнительно понятной юрисдикцией для планирования ВНЖ.',
                'policy',
                'positive',
                'high',
                '["residence_applicants","families","remote_workers"]',
                'high'
            ),
            (
                'uruguay',
                'https://www.gub.uy/tramites/residencia-legal-permanente',
                'Permanent legal residence has an official procedure path',
                'Постоянное легальное резидентство имеет официальный процедурный маршрут',
                'The official procedure page supports a more structured long-term-status assessment, while individual timing still requires verification.',
                'Официальная процедура поддерживает более структурированную оценку долгосрочного статуса, но индивидуальные сроки требуют проверки.',
                'policy',
                'positive',
                'medium',
                '["long_term_relocators","families"]',
                'high'
            ),
            (
                'uruguay',
                'https://www.liveinuruguay.uy/tax-residence',
                'Tax residence is a planning opportunity and review area',
                'Налоговое резидентство является возможностью и зоной проверки',
                'Tax-residence guidance can be relevant for internationally mobile users, but it remains a professional-advice topic.',
                'Информация о налоговом резидентстве важна для международно мобильных пользователей, но требует профессиональной консультации.',
                'policy',
                'mixed',
                'medium',
                '["remote_workers","entrepreneurs","investors"]',
                'medium'
            ),
            (
                'uruguay',
                'https://www.bcu.gub.uy/',
                'Banking system is institutionally stable but onboarding can matter',
                'Банковская система институционально стабильна, но открытие счетов важно',
                'Central-bank context supports higher financial-system confidence, while practical onboarding may still create friction.',
                'Контекст центрального банка поддерживает доверие к финансовой системе, но практическое открытие счетов может создавать трение.',
                'policy',
                'mixed',
                'medium',
                '["entrepreneurs","remote_workers","investors"]',
                'high'
            ),
            (
                'uruguay',
                'https://worldjusticeproject.org/rule-of-law-index/global/2025',
                'Rule-of-law indicators support stability score',
                'Индикаторы верховенства права поддерживают оценку стабильности',
                'Comparative rule-of-law data supports Uruguay as a stronger legal-stability candidate in the MVP country set.',
                'Сравнительные данные по верховенству права поддерживают Уругвай как более сильного кандидата по правовой стабильности в MVP-наборе.',
                'other',
                'positive',
                'high',
                '["families","long_term_relocators","entrepreneurs"]',
                'high'
            )
    ) AS signal(
        country_slug,
        source_url,
        title_en,
        title_ru,
        summary_en,
        summary_ru,
        signal_type,
        impact_direction,
        impact_level,
        affected_groups,
        confidence
    )
)
INSERT INTO
    legal_signals (
        country_id,
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
        impact_direction,
        impact_level,
        affected_groups,
        published_date,
        published_at,
        effective_date,
        source_id,
        confidence
    )
SELECT
    c.id,
    signal.title_en,
    signal.summary_en,
    signal.title_en,
    signal.title_ru,
    signal.summary_en,
    signal.summary_ru,
    signal.signal_type,
    CASE
        WHEN signal.impact_direction = 'uncertain' THEN 'unknown'
        ELSE signal.impact_direction
    END,
    signal.impact_level,
    'active',
    signal.confidence,
    signal.impact_direction,
    signal.impact_level,
    signal.affected_groups::jsonb,
    DATE '2026-06-18',
    DATE '2026-06-18',
    DATE '2026-06-18',
    s.id,
    signal.confidence
FROM
    signal_rows signal
    JOIN countries c ON c.slug = signal.country_slug
    JOIN sources s ON s.url = signal.source_url ON CONFLICT (country_id, title) DO
UPDATE
SET
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
    impact_direction = EXCLUDED.impact_direction,
    impact_level = EXCLUDED.impact_level,
    affected_groups = EXCLUDED.affected_groups,
    published_date = EXCLUDED.published_date,
    published_at = EXCLUDED.published_at,
    effective_date = EXCLUDED.effective_date,
    source_id = EXCLUDED.source_id,
    confidence = EXCLUDED.confidence;

WITH signal_evidence_rows AS (
    SELECT *
    FROM (
        VALUES
            (
                'Electronic visa process is useful but narrow',
                'Russia e-visa portal is an official entry-screening source.',
                'The source supports short-term entry screening, not residence planning.',
                'high'
            ),
            (
                'Electronic visa process is useful but narrow',
                'E-visa information should not be treated as a long-term legalization route.',
                'The MVP signal separates entry permission from residence or citizenship fit.',
                'medium'
            ),
            (
                'Tax-residency review is required before planning',
                'Russia tax planning requires official-rule review.',
                'The tax authority source supports screening but not personalized advice.',
                'medium'
            ),
            (
                'Tax-residency review is required before planning',
                'Tax exposure may depend on residence and income source.',
                'The evidence is framed as a review trigger rather than a conclusion.',
                'medium'
            ),
            (
                'Banking access and payment rails are major planning constraints',
                'Central-bank context is relevant for financial-system screening.',
                'Banking and payment reliability are material for business and remote-work planning.',
                'high'
            ),
            (
                'Banking access and payment rails are major planning constraints',
                'Banking constraints should be treated as operational risk.',
                'The MVP score lowers business practicality where payment access is uncertain.',
                'medium'
            ),
            (
                'Political and civil-liberties risk affects long-term fit',
                'Institutional political-risk indicators support a conservative safety assessment.',
                'The source is used as a comparative risk signal, not a personal safety forecast.',
                'medium'
            ),
            (
                'Political and civil-liberties risk affects long-term fit',
                'Freedom and institutional indicators influence long-term fit.',
                'The MVP model treats political-risk exposure as material for families and entrepreneurs.',
                'medium'
            ),
            (
                'Rule-of-law indicators reduce legal-stability score',
                'Rule-of-law index data is relevant to legal-stability screening.',
                'The signal supports conservative scoring on predictability and enforcement risk.',
                'high'
            ),
            (
                'Rule-of-law indicators reduce legal-stability score',
                'Comparative legal-institution data supports source-aware scoring.',
                'The evidence connects legal-stability score to institutional datasets.',
                'high'
            ),
            (
                'Residence categories are publicly documented',
                'Uruguay publishes residence-category information through official channels.',
                'Official public information supports a higher residence-planning score.',
                'high'
            ),
            (
                'Residence categories are publicly documented',
                'Residence planning still needs document and timeline checks.',
                'The evidence supports legibility, not a guaranteed outcome.',
                'medium'
            ),
            (
                'Permanent legal residence has an official procedure path',
                'Permanent legal residence has a public procedure page.',
                'The source supports long-term-status screening for Uruguay.',
                'high'
            ),
            (
                'Permanent legal residence has an official procedure path',
                'Procedure visibility does not remove individual eligibility checks.',
                'The signal remains positive but not legal advice.',
                'medium'
            ),
            (
                'Tax residence is a planning opportunity and review area',
                'Uruguay tax-residence guidance is relevant for mobile users.',
                'The evidence supports tax planning as a review area rather than a universal benefit.',
                'medium'
            ),
            (
                'Tax residence is a planning opportunity and review area',
                'Tax-residence treatment depends on current rules and personal facts.',
                'The score keeps tax as mixed because professional advice is required.',
                'medium'
            ),
            (
                'Banking system is institutionally stable but onboarding can matter',
                'Central-bank material supports institutional financial-system confidence.',
                'The evidence raises source confidence while preserving onboarding-friction risk.',
                'high'
            ),
            (
                'Banking system is institutionally stable but onboarding can matter',
                'Banking onboarding can still affect self-employment practicality.',
                'The signal remains mixed because practical account access may vary.',
                'medium'
            ),
            (
                'Rule-of-law indicators support stability score',
                'Rule-of-law index data supports Uruguay stability screening.',
                'The source provides comparative institutional context for legal stability.',
                'high'
            ),
            (
                'Rule-of-law indicators support stability score',
                'Legal-stability indicators are relevant for long-term relocation decisions.',
                'The evidence supports Uruguay scoring higher on long-term predictability.',
                'high'
            )
    ) AS evidence(title_en, claim, excerpt, confidence)
)
INSERT INTO
    evidence_items (
        source_id,
        country_id,
        legal_signal_id,
        title,
        summary,
        url,
        quote,
        evidence_type,
        confidence_level,
        published_at,
        claim,
        excerpt,
        retrieved_at,
        confidence
    )
SELECT
    s.id,
    ls.country_id,
    ls.id,
    evidence.claim,
    evidence.excerpt,
    s.url,
    evidence.excerpt,
    'decision_evidence',
    evidence.confidence,
    DATE '2026-06-18',
    evidence.claim,
    evidence.excerpt,
    DATE '2026-06-18',
    evidence.confidence
FROM
    signal_evidence_rows evidence
    JOIN legal_signals ls ON ls.title_en = evidence.title_en
    JOIN sources s ON s.id = ls.source_id
WHERE
    NOT EXISTS (
        SELECT
            1
        FROM
            evidence_items existing
        WHERE
            existing.legal_signal_id = ls.id
            AND existing.claim = evidence.claim
    );

WITH score_inputs AS (
    SELECT *
    FROM (
        VALUES
            ('russia', 'relocation_residence', 40, 38, 55, 34, 36, 32, 55, 'medium'),
            ('russia', 'permanent_residence_citizenship', 38, 36, 54, 32, 35, 31, 54, 'medium'),
            ('russia', 'low_budget_living', 43, 39, 62, 35, 38, 32, 52, 'medium'),
            ('russia', 'business_self_employment', 35, 34, 50, 31, 32, 30, 52, 'medium'),
            ('russia', 'safety_political_risk', 34, 33, 50, 24, 30, 25, 52, 'medium'),
            ('uruguay', 'relocation_residence', 78, 72, 56, 72, 66, 74, 78, 'high'),
            ('uruguay', 'permanent_residence_citizenship', 72, 70, 55, 70, 64, 73, 77, 'high'),
            ('uruguay', 'low_budget_living', 66, 62, 48, 70, 60, 72, 76, 'medium'),
            ('uruguay', 'business_self_employment', 70, 66, 54, 68, 66, 72, 76, 'medium'),
            ('uruguay', 'safety_political_risk', 74, 70, 55, 78, 64, 78, 78, 'high')
    ) AS score(
        country_slug,
        scenario_slug,
        legalization_score,
        long_term_status_score,
        cost_of_living_score,
        safety_score,
        business_score,
        legal_stability_score,
        source_quality_score,
        confidence
    )
),
scored AS (
    SELECT
        c.id AS country_id,
        s.id AS scenario_id,
        score.country_slug,
        score.scenario_slug,
        score.legalization_score,
        score.long_term_status_score,
        score.cost_of_living_score,
        score.safety_score,
        score.business_score,
        score.legal_stability_score,
        score.source_quality_score,
        score.confidence,
        ROUND(
            (
                score.legalization_score * 0.25
                + score.long_term_status_score * 0.20
                + score.cost_of_living_score * 0.15
                + score.safety_score * 0.15
                + score.business_score * 0.10
                + score.legal_stability_score * 0.10
                + score.source_quality_score * 0.05
            )::numeric,
            2
        ) AS total_score
    FROM
        score_inputs score
        JOIN countries c ON c.slug = score.country_slug
        JOIN scenarios s ON s.slug = score.scenario_slug
)
INSERT INTO
    country_scores (
        country_id,
        scenario_id,
        score,
        score_label,
        summary,
        explanation_en,
        explanation_ru,
        confidence,
        calculated_at
    )
SELECT
    scored.country_id,
    scored.scenario_id,
    scored.total_score,
    'Source-aware MVP decision score',
    'Stored v0 score built from seven explainable criteria and linked source quality.',
    'This v0 score is an editor-seeded screening estimate based on residence, long-term status, budget, safety, business, legal-stability, and source-quality criteria. It is not legal, tax, or immigration advice.',
    'Эта v0-оценка является редакторской скрининговой оценкой по семи критериям: легализация, долгосрочный статус, бюджет, безопасность, бизнес, правовая стабильность и качество источников. Это не юридическая, налоговая или миграционная консультация.',
    scored.confidence,
    NOW()
FROM
    scored ON CONFLICT (country_id, scenario_id) DO
UPDATE
SET
    score = EXCLUDED.score,
    score_label = EXCLUDED.score_label,
    summary = EXCLUDED.summary,
    explanation_en = EXCLUDED.explanation_en,
    explanation_ru = EXCLUDED.explanation_ru,
    confidence = EXCLUDED.confidence,
    calculated_at = EXCLUDED.calculated_at;

WITH score_inputs AS (
    SELECT *
    FROM (
        VALUES
            ('russia', 'relocation_residence', 40, 38, 55, 34, 36, 32, 55, 'medium'),
            ('russia', 'permanent_residence_citizenship', 38, 36, 54, 32, 35, 31, 54, 'medium'),
            ('russia', 'low_budget_living', 43, 39, 62, 35, 38, 32, 52, 'medium'),
            ('russia', 'business_self_employment', 35, 34, 50, 31, 32, 30, 52, 'medium'),
            ('russia', 'safety_political_risk', 34, 33, 50, 24, 30, 25, 52, 'medium'),
            ('uruguay', 'relocation_residence', 78, 72, 56, 72, 66, 74, 78, 'high'),
            ('uruguay', 'permanent_residence_citizenship', 72, 70, 55, 70, 64, 73, 77, 'high'),
            ('uruguay', 'low_budget_living', 66, 62, 48, 70, 60, 72, 76, 'medium'),
            ('uruguay', 'business_self_employment', 70, 66, 54, 68, 66, 72, 76, 'medium'),
            ('uruguay', 'safety_political_risk', 74, 70, 55, 78, 64, 78, 78, 'high')
    ) AS score(
        country_slug,
        scenario_slug,
        legalization_score,
        long_term_status_score,
        cost_of_living_score,
        safety_score,
        business_score,
        legal_stability_score,
        source_quality_score,
        confidence
    )
),
breakdown_rows AS (
    SELECT
        cs.id AS country_score_id,
        score.country_slug,
        score.scenario_slug,
        breakdown.criterion,
        breakdown.score,
        breakdown.weight,
        breakdown.confidence,
        ROUND((breakdown.score * breakdown.weight)::numeric, 4) AS weighted_score
    FROM
        score_inputs score
        JOIN countries c ON c.slug = score.country_slug
        JOIN scenarios s ON s.slug = score.scenario_slug
        JOIN country_scores cs ON cs.country_id = c.id
        AND cs.scenario_id = s.id
        CROSS JOIN LATERAL (
            VALUES
                ('legalization_score', score.legalization_score, 0.25, score.confidence),
                ('long_term_status_score', score.long_term_status_score, 0.20, score.confidence),
                ('cost_of_living_score', score.cost_of_living_score, 0.15, score.confidence),
                ('safety_score', score.safety_score, 0.15, score.confidence),
                ('business_score', score.business_score, 0.10, score.confidence),
                ('legal_stability_score', score.legal_stability_score, 0.10, score.confidence),
                ('source_quality_score', score.source_quality_score, 0.05, score.confidence)
        ) AS breakdown(criterion, score, weight, confidence)
)
INSERT INTO
    country_score_breakdowns (
        country_score_id,
        criterion,
        score,
        weight,
        weighted_score,
        explanation_en,
        explanation_ru,
        source_ids,
        confidence
    )
SELECT
    breakdown.country_score_id,
    breakdown.criterion,
    breakdown.score,
    breakdown.weight,
    breakdown.weighted_score,
    'The ' || breakdown.criterion || ' component is seeded from v0 legal signals, evidence confidence, source quality, and country-specific operational constraints.',
    'Компонент ' || breakdown.criterion || ' заполнен на основе v0-правовых сигналов, доверия к evidence, качества источников и практических ограничений страны.',
    COALESCE(
        (
            SELECT
                jsonb_agg(source_subset.id::text)
            FROM
                (
                    SELECT
                        sources.id
                    FROM
                        sources
                        JOIN countries ON countries.id = sources.country_id
                    WHERE
                        countries.slug = breakdown.country_slug
                    ORDER BY
                        CASE sources.source_type
                            WHEN 'official' THEN 1
                            WHEN 'dataset' THEN 2
                            WHEN 'research' THEN 3
                            ELSE 4
                        END,
                        sources.title
                    LIMIT
                        3
                ) AS source_subset
        ),
        '[]'::jsonb
    ),
    breakdown.confidence
FROM
    breakdown_rows breakdown ON CONFLICT (country_score_id, criterion) DO
UPDATE
SET
    score = EXCLUDED.score,
    weight = EXCLUDED.weight,
    weighted_score = EXCLUDED.weighted_score,
    explanation_en = EXCLUDED.explanation_en,
    explanation_ru = EXCLUDED.explanation_ru,
    source_ids = EXCLUDED.source_ids,
    confidence = EXCLUDED.confidence;

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
    JOIN countries destination ON destination.slug = story.destination_slug
WHERE
    NOT EXISTS (
        SELECT
            1
        FROM
            user_stories existing
        WHERE
            existing.origin_country_id = origin.id
            AND existing.destination_country_id = destination.id
            AND existing.scenario = story.scenario
            AND existing.city = story.city
            AND existing.is_synthetic = TRUE
    );
