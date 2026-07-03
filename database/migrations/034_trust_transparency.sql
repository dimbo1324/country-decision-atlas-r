-- Migration 034: Trust and transparency surface: adds country_trust_scores and methodology_sections tables.
CREATE TABLE IF NOT EXISTS country_trust_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_id UUID NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
    trust_score NUMERIC(5, 2),
    trust_label TEXT NOT NULL,
    confidence TEXT NOT NULL,
    freshness_status TEXT NOT NULL,
    source_count INT NOT NULL DEFAULT 0,
    evidence_count INT NOT NULL DEFAULT 0,
    legal_signal_count INT NOT NULL DEFAULT 0,
    route_count INT NOT NULL DEFAULT 0,
    platform_metric_count INT NOT NULL DEFAULT 0,
    contradiction_score NUMERIC(5, 2),
    freshness_score NUMERIC(5, 2),
    evidence_depth_score NUMERIC(5, 2),
    source_quality_score NUMERIC(5, 2),
    review_coverage_score NUMERIC(5, 2),
    last_verified_at TIMESTAMPTZ,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    methodology_version TEXT NOT NULL DEFAULT 'v1.0',
    input_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT country_trust_scores_country_unique UNIQUE (country_id),
    CONSTRAINT country_trust_score_range CHECK (
        trust_score IS NULL OR (trust_score >= 0 AND trust_score <= 100)
    ),
    CONSTRAINT country_trust_label_check CHECK (
        trust_label IN (
            'very_low',
            'low',
            'medium',
            'high',
            'very_high',
            'insufficient_data'
        )
    ),
    CONSTRAINT country_trust_confidence_check CHECK (
        confidence IN ('low', 'medium', 'high')
    ),
    CONSTRAINT country_trust_freshness_check CHECK (
        freshness_status IN ('fresh', 'aging', 'stale', 'unknown')
    ),
    CONSTRAINT country_trust_counts_check CHECK (
        source_count >= 0
        AND evidence_count >= 0
        AND legal_signal_count >= 0
        AND route_count >= 0
        AND platform_metric_count >= 0
    ),
    CONSTRAINT country_trust_input_summary_object_check CHECK (
        jsonb_typeof(input_summary) = 'object'
    )
);

CREATE INDEX IF NOT EXISTS idx_country_trust_scores_country
    ON country_trust_scores (country_id);

CREATE INDEX IF NOT EXISTS idx_country_trust_scores_label
    ON country_trust_scores (trust_label);

CREATE INDEX IF NOT EXISTS idx_country_trust_scores_computed_at
    ON country_trust_scores (computed_at);

CREATE INDEX IF NOT EXISTS idx_country_trust_scores_expires_at
    ON country_trust_scores (expires_at);

CREATE TABLE IF NOT EXISTS methodology_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    title_ru TEXT NOT NULL,
    summary TEXT NOT NULL,
    summary_ru TEXT NOT NULL,
    body TEXT NOT NULL,
    body_ru TEXT NOT NULL,
    section_type TEXT NOT NULL,
    display_order INT NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'published',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT methodology_section_type_check CHECK (
        section_type IN (
            'index',
            'score',
            'metric',
            'trust',
            'risk',
            'source',
            'disclaimer'
        )
    ),
    CONSTRAINT methodology_status_check CHECK (
        status IN ('draft', 'review', 'published', 'archived', 'rejected')
    )
);

CREATE INDEX IF NOT EXISTS idx_methodology_sections_slug
    ON methodology_sections (slug);

CREATE INDEX IF NOT EXISTS idx_methodology_sections_status_order
    ON methodology_sections (status, display_order);

CREATE TABLE IF NOT EXISTS glossary_terms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT NOT NULL UNIQUE,
    term TEXT NOT NULL,
    term_ru TEXT NOT NULL,
    definition TEXT NOT NULL,
    definition_ru TEXT NOT NULL,
    category TEXT NOT NULL,
    related_terms JSONB NOT NULL DEFAULT '[]'::jsonb,
    display_order INT NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'published',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT glossary_category_check CHECK (
        category IN (
            'migration',
            'legal',
            'analytics',
            'trust',
            'source',
            'decision',
            'route',
            'persona'
        )
    ),
    CONSTRAINT glossary_related_terms_array_check CHECK (
        jsonb_typeof(related_terms) = 'array'
    ),
    CONSTRAINT glossary_status_check CHECK (
        status IN ('draft', 'review', 'published', 'archived', 'rejected')
    )
);

CREATE INDEX IF NOT EXISTS idx_glossary_terms_slug
    ON glossary_terms (slug);

CREATE INDEX IF NOT EXISTS idx_glossary_terms_category_status
    ON glossary_terms (category, status);

INSERT INTO methodology_sections (
    slug, title, title_ru, summary, summary_ru, body, body_ru,
    section_type, display_order, status
) VALUES
    (
        'what_is_cii',
        'What is the Country Integration Index?',
        'Что такое Country Integration Index?',
        'The CII is a composite score measuring how well a country supports different migration scenarios.',
        'CII — это составной показатель, который измеряет, насколько страна поддерживает различные миграционные сценарии.',
        'The Country Integration Index (CII) is a weighted geometric mean of 6 metrics: rule of law, economic openness, social integration, digital infrastructure, healthcare access, and political stability. Each metric is scored 0–100. The geometric mean ensures that a very low score in any single metric pulls the overall score down significantly.',
        'Country Integration Index (CII) — это взвешенное геометрическое среднее 6 метрик: верховенство закона, экономическая открытость, социальная интеграция, цифровая инфраструктура, доступность здравоохранения и политическая стабильность. Каждая метрика оценивается по шкале 0–100. Геометрическое среднее гарантирует, что очень низкий балл по любой отдельной метрике существенно снижает общий показатель.',
        'score', 10, 'published'
    ),
    (
        'what_is_decision_score',
        'What is the Decision Score?',
        'Что такое Decision Score?',
        'The Decision Score ranks countries for your specific scenario and persona.',
        'Decision Score — это ранжирование стран по вашему конкретному сценарию и персоне.',
        'The Decision Score is a persona-adjusted, scenario-specific ranking. It takes the CII scenario score and applies persona modifier weights based on your selected persona. This means two people with different personas may rank the same countries differently. The Decision Score does not change the underlying CII formula or data.',
        'Decision Score — это ранжирование, скорректированное под персону и конкретный сценарий. Он берёт сценарный балл CII и применяет веса модификаторов персоны на основе выбранной персоны. Это означает, что два человека с разными персонами могут по-разному ранжировать одни и те же страны. Decision Score не меняет базовую формулу CII или данные.',
        'score', 20, 'published'
    ),
    (
        'what_is_persona',
        'What is a Persona?',
        'Что такое Persona?',
        'A persona represents your situation and adjusts how CII metrics are weighted for your decision.',
        'Персона представляет вашу ситуацию и корректирует вес метрик CII при принятии решения.',
        'Personas are predefined profiles (e.g. Remote Worker, Entrepreneur, Family Relocator) that adjust the relative importance of CII metrics. For example, a Remote Worker values digital infrastructure more, while a Family Relocator prioritizes healthcare and social integration. Persona modifiers are applied multiplicatively to metric scores before computing the Decision Score.',
        'Персоны — это предопределённые профили (например, Удалённый работник, Предприниматель, Семейный переезд), которые корректируют относительную важность метрик CII. Например, удалённый работник больше ценит цифровую инфраструктуру, а семейный переезд приоритизирует здравоохранение и социальную интеграцию. Модификаторы персоны применяются мультипликативно к баллам метрик перед вычислением Decision Score.',
        'score', 30, 'published'
    ),
    (
        'what_is_route',
        'What is a Route?',
        'Что такое Route?',
        'A route is a verified legal pathway for immigration or residency in a country.',
        'Маршрут — это проверенный юридический путь для иммиграции или получения вида на жительство в стране.',
        'Routes describe specific legal pathways: visa categories, residence permit types, citizenship tracks. Each route is source-backed with references to official government sources or verified legal information. Routes include eligibility criteria, processing times, required documents, and legal status.',
        'Маршруты описывают конкретные юридические пути: категории виз, типы разрешений на проживание, пути к гражданству. Каждый маршрут подкреплён ссылками на официальные государственные источники или проверенную юридическую информацию. Маршруты включают критерии приемлемости, сроки рассмотрения, необходимые документы и правовой статус.',
        'source', 40, 'published'
    ),
    (
        'what_is_legal_velocity',
        'What is the Legal Velocity Index?',
        'Что такое Legal Velocity Index?',
        'The LVI measures how fast the legal environment in a country has been changing.',
        'LVI измеряет, как быстро меняется правовая среда в стране.',
        'The Legal Velocity Index (LVI) is a self-computed metric that measures the rate and direction of legal changes based on legal signal events in the timeline. High LVI means many recent legal changes. Low LVI means a stable legal environment. LVI does not change the CII score.',
        'Legal Velocity Index (LVI) — это самовычисляемая метрика, которая измеряет скорость и направление юридических изменений на основе событий в временной шкале правовых сигналов. Высокий LVI означает много недавних юридических изменений. Низкий LVI означает стабильную правовую среду. LVI не изменяет балл CII.',
        'metric', 50, 'published'
    ),
    (
        'what_is_scenario_risk',
        'What is the Scenario-Specific Risk Score?',
        'Что такое Scenario-Specific Risk Score?',
        'The SSRS measures risk for your specific scenario in a country.',
        'SSRS измеряет риск для вашего конкретного сценария в стране.',
        'The Scenario-Specific Risk Score (SSRS) is a self-computed metric that aggregates risk signals relevant to a particular migration scenario (e.g. business_self_employment). It uses evidence items, legal signals, and timeline events tagged to that scenario. High SSRS means elevated risk for that scenario. SSRS does not change decision ranking.',
        'Scenario-Specific Risk Score (SSRS) — это самовычисляемая метрика, которая агрегирует сигналы риска, относящиеся к конкретному миграционному сценарию (например, business_self_employment). Она использует элементы доказательств, правовые сигналы и события временной шкалы, помеченные для этого сценария. Высокий SSRS означает повышенный риск для этого сценария. SSRS не меняет ранжирование решений.',
        'metric', 60, 'published'
    ),
    (
        'what_is_contradiction_score',
        'What is the Contradiction Score?',
        'Что такое Contradiction Score?',
        'The Contradiction Score measures how consistent the legal signals are for a country.',
        'Contradiction Score измеряет, насколько согласованы правовые сигналы для страны.',
        'The Contradiction Score detects when legal signals in a country point in conflicting directions. For example, if some signals indicate improving conditions while others indicate worsening, the contradiction score is high. A high contradiction score means data may be inconsistent or the legal environment is rapidly shifting. It does not change the CII.',
        'Contradiction Score выявляет случаи, когда правовые сигналы в стране указывают в противоположных направлениях. Например, если одни сигналы указывают на улучшение условий, а другие — на ухудшение, показатель противоречий высок. Высокий Contradiction Score означает, что данные могут быть несогласованными или правовая среда быстро меняется. Он не меняет CII.',
        'metric', 70, 'published'
    ),
    (
        'what_is_trust_score',
        'What is the Trust Score?',
        'Что такое Trust Score?',
        'The Trust Score indicates how reliable and up-to-date the data is for a country.',
        'Trust Score показывает, насколько надёжны и актуальны данные для страны.',
        'The Trust Score is a data quality indicator, not a measure of how good a country is. It reflects how many sources back the data, how recent the evidence is, how complete the review coverage is, and whether legal signals are consistent. A country with Trust = High has well-sourced, fresh, consistent data. A country with Trust = Low needs more data verification. Trust does not affect CII or decision ranking.',
        'Trust Score — это индикатор качества данных, а не показатель того, насколько хороша страна. Он отражает, сколько источников подтверждают данные, насколько свежи доказательства, насколько полно покрытие проверок и согласованы ли правовые сигналы. Страна с Trust = High имеет хорошо обоснованные, свежие, согласованные данные. Страна с Trust = Low нуждается в дополнительной проверке данных. Trust не влияет на CII или ранжирование решений.',
        'trust', 80, 'published'
    ),
    (
        'what_is_confidence',
        'What is Confidence?',
        'Что такое Confidence?',
        'Confidence indicates how much data was available when computing a metric.',
        'Confidence указывает, сколько данных было доступно при вычислении метрики.',
        'Confidence (low/medium/high) reflects the volume of underlying data. High confidence means many sources, evidence items, and legal signals contributed to the score. Low confidence means the score is based on limited data and should be interpreted cautiously.',
        'Confidence (low/medium/high) отражает объём базовых данных. Высокий confidence означает, что к баллу способствовали многие источники, элементы доказательств и правовые сигналы. Низкий confidence означает, что балл основан на ограниченных данных и должен интерпретироваться с осторожностью.',
        'trust', 90, 'published'
    ),
    (
        'what_is_freshness',
        'What is Freshness?',
        'Что такое Freshness?',
        'Freshness shows how recently the underlying data was verified.',
        'Freshness показывает, как недавно были проверены базовые данные.',
        'Freshness (fresh/aging/stale/unknown) reflects the age of the most recent data verification. Fresh means verified within 180 days. Aging means 181–365 days. Stale means over a year. Unknown means no explicit verification timestamp is available. Stale or unknown data should be cross-checked with official sources.',
        'Freshness (fresh/aging/stale/unknown) отражает возраст последней верификации данных. Fresh означает верификацию в течение 180 дней. Aging — 181–365 дней. Stale — более года. Unknown означает отсутствие явного временного штампа верификации. Устаревшие или неизвестные данные следует перепроверить по официальным источникам.',
        'trust', 100, 'published'
    ),
    (
        'source_backed_methodology',
        'Source-backed methodology',
        'Методология, основанная на источниках',
        'All data is backed by verifiable sources.',
        'Все данные подкреплены проверяемыми источниками.',
        'Every legal signal, evidence item, and route in the platform must reference at least one published source. Sources include official government portals, legal databases, and verified news outlets. The source count and evidence count are visible in the Trust Score breakdown.',
        'Каждый правовой сигнал, элемент доказательств и маршрут на платформе должен ссылаться как минимум на один опубликованный источник. Источники включают официальные государственные порталы, правовые базы данных и проверенные новостные ресурсы. Количество источников и доказательств видно в разбивке Trust Score.',
        'source', 110, 'published'
    ),
    (
        'legal_disclaimer',
        'Legal Disclaimer',
        'Правовой дисклеймер',
        'This platform provides analytical information only. It is not legal advice.',
        'Эта платформа предоставляет только аналитическую информацию. Это не юридическая консультация.',
        'The information on this platform is for informational and analytical purposes only. It does not constitute legal, financial, or immigration advice. Requirements change frequently. Always verify with official government sources and consult a qualified immigration lawyer before making decisions.',
        'Информация на этой платформе предназначена только для информационных и аналитических целей. Она не является юридической, финансовой или иммиграционной консультацией. Требования часто меняются. Всегда проверяйте официальные государственные источники и консультируйтесь с квалифицированным иммиграционным юристом перед принятием решений.',
        'disclaimer', 999, 'published'
    )
ON CONFLICT (slug) DO UPDATE SET
    title = EXCLUDED.title,
    title_ru = EXCLUDED.title_ru,
    summary = EXCLUDED.summary,
    summary_ru = EXCLUDED.summary_ru,
    body = EXCLUDED.body,
    body_ru = EXCLUDED.body_ru,
    section_type = EXCLUDED.section_type,
    display_order = EXCLUDED.display_order,
    status = EXCLUDED.status,
    updated_at = NOW();

INSERT INTO glossary_terms (
    slug, term, term_ru, definition, definition_ru,
    category, related_terms, display_order, status
) VALUES
    ('residence', 'Residence', 'Вид на жительство', 'The legal right to live in a country for an extended period.', 'Юридическое право проживать в стране в течение длительного периода.', 'migration', '["permanent_residence", "route"]', 10, 'published'),
    ('permanent_residence', 'Permanent Residence', 'Постоянное место жительства', 'A status allowing indefinite residence in a country without becoming a citizen.', 'Статус, позволяющий проживать в стране бессрочно без получения гражданства.', 'migration', '["residence", "citizenship"]', 20, 'published'),
    ('citizenship', 'Citizenship', 'Гражданство', 'Full legal membership in a country, including the right to a passport and voting rights.', 'Полноправное юридическое членство в стране, включая право на паспорт и право голоса.', 'migration', '["permanent_residence"]', 30, 'published'),
    ('legal_signal', 'Legal Signal', 'Правовой сигнал', 'A tracked legal event or regulatory change relevant to migration.', 'Отслеживаемое юридическое событие или регуляторное изменение, относящееся к миграции.', 'legal', '["evidence", "legal_velocity_index"]', 40, 'published'),
    ('evidence', 'Evidence', 'Доказательство', 'A documented item supporting or contextualizing a legal signal.', 'Задокументированный элемент, подтверждающий или контекстуализирующий правовой сигнал.', 'legal', '["source", "legal_signal"]', 50, 'published'),
    ('source', 'Source', 'Источник', 'A published, verifiable reference used to back platform data.', 'Опубликованная, верифицируемая ссылка, используемая для подтверждения данных платформы.', 'source', '["evidence", "source_backed"]', 60, 'published'),
    ('source_backed', 'Source-backed', 'Подкреплённый источниками', 'Data or claims that reference at least one published source.', 'Данные или утверждения, ссылающиеся как минимум на один опубликованный источник.', 'source', '["source"]', 70, 'published'),
    ('confidence', 'Confidence', 'Уверенность', 'An indicator of how much underlying data contributed to a metric score.', 'Индикатор того, сколько базовых данных способствовало оценке метрики.', 'trust', '["trust_score", "freshness"]', 80, 'published'),
    ('freshness', 'Freshness', 'Свежесть', 'How recently the underlying data was verified or updated.', 'Как недавно базовые данные были проверены или обновлены.', 'trust', '["trust_score", "confidence"]', 90, 'published'),
    ('contradiction', 'Contradiction', 'Противоречие', 'When legal signals for a country point in conflicting directions.', 'Когда правовые сигналы для страны указывают в противоположных направлениях.', 'analytics', '["contradiction_score", "legal_signal"]', 100, 'published'),
    ('trust_score', 'Trust Score', 'Trust Score', 'A data quality indicator for a country, reflecting source coverage, freshness, and consistency.', 'Индикатор качества данных для страны, отражающий покрытие источников, свежесть и согласованность.', 'trust', '["confidence", "freshness", "contradiction"]', 110, 'published'),
    ('cii', 'Country Integration Index', 'Country Integration Index', 'A composite score measuring how well a country supports migration scenarios.', 'Составной показатель, измеряющий, насколько страна поддерживает миграционные сценарии.', 'analytics', '["scenario", "decision_score"]', 120, 'published'),
    ('scenario', 'Scenario', 'Сценарий', 'A specific migration goal such as relocation, permanent residence, or business setup.', 'Конкретная миграционная цель, например переезд, постоянное проживание или открытие бизнеса.', 'decision', '["cii", "persona"]', 130, 'published'),
    ('persona', 'Persona', 'Персона', 'A predefined profile that adjusts how CII metrics are weighted in the decision.', 'Предопределённый профиль, корректирующий вес метрик CII при принятии решения.', 'persona', '["scenario", "decision_score"]', 140, 'published'),
    ('route', 'Route', 'Маршрут', 'A specific legal pathway for immigration or residency in a country.', 'Конкретный юридический путь для иммиграции или получения вида на жительство в стране.', 'route', '["source_backed", "legal_signal"]', 150, 'published'),
    ('platform_metric', 'Platform Metric', 'Метрика платформы', 'A self-computed metric such as LVI, SSRS, or Contradiction Score.', 'Самовычисляемая метрика, такая как LVI, SSRS или Contradiction Score.', 'analytics', '["legal_velocity_index", "scenario_specific_risk_score", "contradiction_score"]', 160, 'published'),
    ('legal_velocity_index', 'Legal Velocity Index', 'Legal Velocity Index', 'A metric measuring the rate and direction of legal changes in a country.', 'Метрика, измеряющая скорость и направление юридических изменений в стране.', 'analytics', '["legal_signal", "platform_metric"]', 170, 'published'),
    ('scenario_specific_risk_score', 'Scenario-Specific Risk Score', 'Scenario-Specific Risk Score', 'A metric measuring risk for a particular migration scenario in a country.', 'Метрика, измеряющая риск для конкретного миграционного сценария в стране.', 'analytics', '["scenario", "platform_metric"]', 180, 'published'),
    ('decision_score', 'Decision Score', 'Decision Score', 'A persona-adjusted, scenario-specific ranking of countries for a given migration goal.', 'Ранжирование стран по конкретному миграционному сценарию с учётом персоны.', 'decision', '["cii", "persona", "scenario"]', 190, 'published')
ON CONFLICT (slug) DO UPDATE SET
    term = EXCLUDED.term,
    term_ru = EXCLUDED.term_ru,
    definition = EXCLUDED.definition,
    definition_ru = EXCLUDED.definition_ru,
    category = EXCLUDED.category,
    related_terms = EXCLUDED.related_terms,
    display_order = EXCLUDED.display_order,
    status = EXCLUDED.status,
    updated_at = NOW();

UPDATE feature_flags
SET
    status = 'enabled',
    access_tier = 'public',
    default_enabled = TRUE,
    updated_at = NOW()
WHERE key = 'trust_surface_enabled';

INSERT INTO feature_access_rules (feature_key, access_tier, is_enabled)
VALUES ('trust_surface_enabled', 'public', TRUE)
ON CONFLICT (feature_key, access_tier) DO UPDATE SET
    is_enabled = EXCLUDED.is_enabled;
