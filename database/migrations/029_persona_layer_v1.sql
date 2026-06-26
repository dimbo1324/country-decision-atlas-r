CREATE TABLE IF NOT EXISTS personas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    name_ru TEXT NOT NULL,
    description TEXT,
    description_ru TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    display_order INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT personas_slug_check CHECK (slug ~ '^[a-z0-9_]+$'),
    CONSTRAINT personas_name_check CHECK (BTRIM(name) <> ''),
    CONSTRAINT personas_name_ru_check CHECK (BTRIM(name_ru) <> '')
);

CREATE INDEX IF NOT EXISTS idx_personas_active_order
    ON personas (is_active, display_order, slug);

CREATE TABLE IF NOT EXISTS persona_metric_modifiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version TEXT NOT NULL DEFAULT 'v1.0',
    persona_slug TEXT NOT NULL REFERENCES personas(slug) ON DELETE CASCADE,
    metric_id UUID NOT NULL REFERENCES cii_metric_definitions(id) ON DELETE CASCADE,
    modifier NUMERIC(5, 4) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT persona_modifier_unique UNIQUE (version, persona_slug, metric_id),
    CONSTRAINT persona_modifier_range CHECK (modifier >= -0.5 AND modifier <= 0.5),
    CONSTRAINT persona_modifier_version_check CHECK (BTRIM(version) <> '')
);

CREATE INDEX IF NOT EXISTS idx_persona_metric_modifiers_persona_version
    ON persona_metric_modifiers (persona_slug, version);

CREATE INDEX IF NOT EXISTS idx_persona_metric_modifiers_metric
    ON persona_metric_modifiers (metric_id);

INSERT INTO personas (
    slug,
    name,
    name_ru,
    description,
    description_ru,
    is_active,
    display_order
)
VALUES
    (
        'digital_nomad',
        'Digital nomad',
        'Цифровой кочевник',
        'Remote worker focused on digital access, safety, and practical residence options.',
        'Удалённый специалист, которому важны цифровая инфраструктура, безопасность и практичные варианты легального пребывания.',
        TRUE,
        10
    ),
    (
        'family',
        'Family',
        'Семья',
        'Household relocating with dependants and prioritising safety, stability, and long-term planning.',
        'Семья с иждивенцами, для которой важны безопасность, стабильность и долгосрочное планирование.',
        TRUE,
        20
    ),
    (
        'student',
        'Student',
        'Студент',
        'Person evaluating study, affordability, safety, and future long-term options.',
        'Человек, который оценивает обучение, доступность жизни, безопасность и будущие долгосрочные варианты.',
        TRUE,
        30
    ),
    (
        'entrepreneur',
        'Entrepreneur',
        'Предприниматель',
        'Founder or self-employed person focused on business conditions, banking, legal stability, and digital access.',
        'Предприниматель или самозанятый специалист, которому важны условия для бизнеса, банковская доступность, правовая стабильность и цифровая инфраструктура.',
        TRUE,
        40
    ),
    (
        'low_budget_migrant',
        'Low-budget migrant',
        'Мигрант с ограниченным бюджетом',
        'Person prioritising practical affordability, safety, and accessible residence planning.',
        'Человек с ограниченным бюджетом, для которого важны практическая доступность жизни, безопасность и понятный путь легализации.',
        TRUE,
        50
    ),
    (
        'investor',
        'Investor',
        'Инвестор',
        'Person evaluating legal predictability, economic openness, stability, and long-term capital safety.',
        'Человек, который оценивает правовую предсказуемость, экономическую открытость, стабильность и долгосрочную сохранность капитала.',
        TRUE,
        60
    ),
    (
        'skilled_worker',
        'Skilled worker',
        'Квалифицированный специалист',
        'Professional focused on economic opportunity, digital infrastructure, stability, and residence practicality.',
        'Квалифицированный специалист, которому важны экономические возможности, цифровая инфраструктура, стабильность и практичность легализации.',
        TRUE,
        70
    )
ON CONFLICT (slug) DO UPDATE
SET
    name = EXCLUDED.name,
    name_ru = EXCLUDED.name_ru,
    description = EXCLUDED.description,
    description_ru = EXCLUDED.description_ru,
    is_active = EXCLUDED.is_active,
    display_order = EXCLUDED.display_order,
    updated_at = NOW();

WITH modifier_rows (
    persona_slug,
    metric_slug,
    modifier
) AS (
    VALUES
        ('digital_nomad', 'rule_of_law', 0.0500::NUMERIC),
        ('digital_nomad', 'economic_freedom', 0.0500::NUMERIC),
        ('digital_nomad', 'political_stability', 0.0500::NUMERIC),
        ('digital_nomad', 'safety', 0.1500::NUMERIC),
        ('digital_nomad', 'corruption', 0.0000::NUMERIC),
        ('digital_nomad', 'digital_access', 0.2500::NUMERIC),
        ('family', 'rule_of_law', 0.1500::NUMERIC),
        ('family', 'economic_freedom', -0.0500::NUMERIC),
        ('family', 'political_stability', 0.1500::NUMERIC),
        ('family', 'safety', 0.2500::NUMERIC),
        ('family', 'corruption', 0.0500::NUMERIC),
        ('family', 'digital_access', 0.0000::NUMERIC),
        ('student', 'rule_of_law', 0.0500::NUMERIC),
        ('student', 'economic_freedom', -0.0500::NUMERIC),
        ('student', 'political_stability', 0.0500::NUMERIC),
        ('student', 'safety', 0.1500::NUMERIC),
        ('student', 'corruption', 0.0000::NUMERIC),
        ('student', 'digital_access', 0.1000::NUMERIC),
        ('entrepreneur', 'rule_of_law', 0.1500::NUMERIC),
        ('entrepreneur', 'economic_freedom', 0.2500::NUMERIC),
        ('entrepreneur', 'political_stability', 0.0500::NUMERIC),
        ('entrepreneur', 'safety', 0.0000::NUMERIC),
        ('entrepreneur', 'corruption', 0.1500::NUMERIC),
        ('entrepreneur', 'digital_access', 0.1500::NUMERIC),
        ('low_budget_migrant', 'rule_of_law', 0.0500::NUMERIC),
        ('low_budget_migrant', 'economic_freedom', -0.1000::NUMERIC),
        ('low_budget_migrant', 'political_stability', 0.0500::NUMERIC),
        ('low_budget_migrant', 'safety', 0.1500::NUMERIC),
        ('low_budget_migrant', 'corruption', 0.0500::NUMERIC),
        ('low_budget_migrant', 'digital_access', 0.0000::NUMERIC),
        ('investor', 'rule_of_law', 0.2500::NUMERIC),
        ('investor', 'economic_freedom', 0.2000::NUMERIC),
        ('investor', 'political_stability', 0.2000::NUMERIC),
        ('investor', 'safety', 0.0500::NUMERIC),
        ('investor', 'corruption', 0.2000::NUMERIC),
        ('investor', 'digital_access', 0.0000::NUMERIC),
        ('skilled_worker', 'rule_of_law', 0.1000::NUMERIC),
        ('skilled_worker', 'economic_freedom', 0.1500::NUMERIC),
        ('skilled_worker', 'political_stability', 0.1000::NUMERIC),
        ('skilled_worker', 'safety', 0.0500::NUMERIC),
        ('skilled_worker', 'corruption', 0.0500::NUMERIC),
        ('skilled_worker', 'digital_access', 0.1500::NUMERIC)
)
INSERT INTO persona_metric_modifiers (
    version,
    persona_slug,
    metric_id,
    modifier
)
SELECT
    'v1.0',
    modifier_rows.persona_slug,
    cii_metric_definitions.id,
    modifier_rows.modifier
FROM modifier_rows
INNER JOIN personas
    ON personas.slug = modifier_rows.persona_slug
INNER JOIN cii_metric_definitions
    ON cii_metric_definitions.slug = modifier_rows.metric_slug
    AND cii_metric_definitions.is_active = TRUE
ON CONFLICT (version, persona_slug, metric_id) DO UPDATE
SET
    modifier = EXCLUDED.modifier,
    updated_at = NOW();
