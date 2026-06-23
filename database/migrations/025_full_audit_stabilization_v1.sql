WITH argentina_scores AS (
    SELECT
        c.id AS country_id,
        s.id AS scenario_id,
        ccs.overall_score AS score
    FROM countries c
    JOIN country_cii_scores ccs
        ON ccs.country_id = c.id
        AND ccs.version = 'v1.0'
    JOIN scenarios s ON s.slug = ccs.scenario_slug
    WHERE c.slug = 'argentina'
      AND ccs.scenario_slug IN (
          'relocation_residence',
          'permanent_residence_citizenship',
          'low_budget_living',
          'business_self_employment',
          'safety_political_risk'
      )
)
INSERT INTO country_scores (
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
    country_id,
    scenario_id,
    score,
    'CII-backed MVP decision score',
    'Сценарная оценка Аргентины на основе CII v1.0.',
    'The score is derived from the published CII v1.0 scenario calculation and its source-attributed metric values. It is a screening aid, not legal advice.',
    'Оценка рассчитана по опубликованной сценарной модели CII v1.0 и значениям метрик с указанием источников. Это инструмент первичного отбора, а не юридическая консультация.',
    'high',
    NOW()
FROM argentina_scores
ON CONFLICT (country_id, scenario_id) DO UPDATE
SET
    score = EXCLUDED.score,
    score_label = EXCLUDED.score_label,
    summary = EXCLUDED.summary,
    explanation_en = EXCLUDED.explanation_en,
    explanation_ru = EXCLUDED.explanation_ru,
    confidence = EXCLUDED.confidence,
    calculated_at = EXCLUDED.calculated_at;

WITH argentina_breakdowns AS (
    SELECT
        cs.id AS country_score_id,
        criterion_data.criterion,
        criterion_data.score::numeric(5, 2) AS score,
        criterion_data.weight::numeric(5, 4) AS weight,
        criterion_data.explanation_en,
        criterion_data.explanation_ru,
        criterion_data.source_urls
    FROM country_scores cs
    JOIN countries c ON c.id = cs.country_id
    JOIN scenarios s ON s.id = cs.scenario_id
    CROSS JOIN (
        VALUES
            (
                'legalization_score',
                38.00,
                0.25,
                'Screening proxy based on the CII rule-of-law metric and official DNM residence guidance. Current requirements must be verified for the applicant profile.',
                'Скрининговый показатель основан на метрике CII верховенства права и официальных материалах DNM о резидентстве. Актуальные требования необходимо проверять для конкретного профиля заявителя.',
                ARRAY['https://info.worldbank.org/governance/wgi/', 'https://www.argentina.gob.ar/interior/migraciones']::text[]
            ),
            (
                'long_term_status_score',
                34.00,
                0.20,
                'Screening proxy combining the CII rule-of-law and political-stability metrics with official immigration guidance. It does not predict an individual residence or citizenship outcome.',
                'Скрининговый показатель сочетает метрики CII верховенства права и политической стабильности с официальными иммиграционными материалами. Он не прогнозирует индивидуальный результат получения резидентства или гражданства.',
                ARRAY['https://info.worldbank.org/governance/wgi/', 'https://www.argentina.gob.ar/interior/migraciones', 'https://www.cancilleria.gob.ar/en/tourism-and-travel/visas']::text[]
            ),
            (
                'cost_of_living_score',
                44.80,
                0.15,
                'Screening proxy using the CII economic-freedom metric and official INDEC country data. It is not a city-level household budget and current prices require separate verification.',
                'Скрининговый показатель использует метрику CII экономической свободы и официальные данные INDEC. Это не городской бюджет домохозяйства; актуальные цены требуют отдельной проверки.',
                ARRAY['https://www.heritage.org/index/', 'https://www.indec.gob.ar', 'https://data.worldbank.org/country/AR']::text[]
            ),
            (
                'safety_score',
                42.50,
                0.15,
                'Screening proxy combining the CII safety and political-stability metrics. Local conditions vary and current official travel guidance remains necessary.',
                'Скрининговый показатель сочетает метрики CII безопасности и политической стабильности. Локальные условия различаются, поэтому необходимо проверять актуальные официальные рекомендации для поездок.',
                ARRAY['https://www.visionofhumanity.org/maps/#/', 'https://info.worldbank.org/governance/wgi/', 'https://freedomhouse.org/country/argentina/freedom-world/2024']::text[]
            ),
            (
                'business_score',
                56.40,
                0.10,
                'Screening proxy combining the CII economic-freedom and digital-access metrics with official AFIP and IGJ registration materials.',
                'Скрининговый показатель сочетает метрики CII экономической свободы и цифрового доступа с официальными материалами AFIP и IGJ о регистрации.',
                ARRAY['https://www.afip.gob.ar', 'https://www.afip.gob.ar/monotributo/', 'https://www.argentina.gob.ar/justicia/igj']::text[]
            ),
            (
                'legal_stability_score',
                35.00,
                0.10,
                'Screening proxy combining the CII rule-of-law, political-stability, and corruption metrics. It represents country-level context rather than legal certainty for a particular case.',
                'Скрининговый показатель сочетает метрики CII верховенства права, политической стабильности и коррупции. Он отражает контекст страны, а не юридическую определённость по конкретному делу.',
                ARRAY['https://info.worldbank.org/governance/wgi/', 'https://www.transparency.org/en/cpi/2023']::text[]
            ),
            (
                'source_quality_score',
                47.13,
                0.05,
                'Screening proxy reflecting the six source-attributed CII metric values used by the v1.0 calculation. Source freshness and methodology still require periodic review.',
                'Скрининговый показатель отражает шесть значений метрик CII с указанными источниками, использованных расчётом v1.0. Актуальность источников и методология требуют периодической проверки.',
                ARRAY['https://info.worldbank.org/governance/wgi/', 'https://www.heritage.org/index/', 'https://www.transparency.org/en/cpi/2023']::text[]
            )
    ) AS criterion_data(
        criterion,
        score,
        weight,
        explanation_en,
        explanation_ru,
        source_urls
    )
    WHERE c.slug = 'argentina'
      AND s.slug IN (
          'relocation_residence',
          'permanent_residence_citizenship',
          'low_budget_living',
          'business_self_employment',
          'safety_political_risk'
      )
)
INSERT INTO country_score_breakdowns (
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
    argentina_breakdowns.country_score_id,
    argentina_breakdowns.criterion,
    argentina_breakdowns.score,
    argentina_breakdowns.weight,
    ROUND(argentina_breakdowns.score * argentina_breakdowns.weight, 4),
    argentina_breakdowns.explanation_en,
    argentina_breakdowns.explanation_ru,
    COALESCE(
        (
            SELECT jsonb_agg(source.id::text ORDER BY source.title)
            FROM sources source
            JOIN countries source_country ON source_country.id = source.country_id
            WHERE source_country.slug = 'argentina'
              AND source.status = 'published'
              AND source.url = ANY(argentina_breakdowns.source_urls)
        ),
        '[]'::jsonb
    ),
    'high'
FROM argentina_breakdowns
ON CONFLICT (country_score_id, criterion) DO UPDATE
SET
    score = EXCLUDED.score,
    weight = EXCLUDED.weight,
    weighted_score = EXCLUDED.weighted_score,
    explanation_en = EXCLUDED.explanation_en,
    explanation_ru = EXCLUDED.explanation_ru,
    source_ids = EXCLUDED.source_ids,
    confidence = EXCLUDED.confidence;

CREATE TEMPORARY TABLE audit_localization_stage (
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    field_name TEXT NOT NULL,
    ru_text TEXT NOT NULL,
    en_text TEXT,
    PRIMARY KEY (entity_type, entity_id, field_name)
) ON COMMIT DROP;

INSERT INTO audit_localization_stage
SELECT 'country_card', cc.id, fields.field_name, fields.ru_text, fields.en_text
FROM country_cards cc
LEFT JOIN country_cards en_card
    ON en_card.country_id = cc.country_id
    AND en_card.locale = 'en'
CROSS JOIN LATERAL (
    VALUES
        ('executive_summary', cc.executive_summary, en_card.executive_summary),
        ('migration_overview', cc.migration_overview, en_card.migration_overview),
        ('tax_overview', cc.tax_overview, en_card.tax_overview),
        ('cost_of_living_overview', cc.cost_of_living_overview, en_card.cost_of_living_overview),
        ('business_overview', cc.business_overview, en_card.business_overview),
        ('safety_overview', cc.safety_overview, en_card.safety_overview),
        ('legal_signals_summary', cc.legal_signals_summary, en_card.legal_signals_summary),
        ('risk_summary', cc.risk_summary, en_card.risk_summary),
        ('source_summary', cc.source_summary, en_card.source_summary)
) AS fields(field_name, ru_text, en_text)
WHERE cc.locale = 'ru'
  AND NULLIF(BTRIM(fields.ru_text), '') IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM translation_units tu
      WHERE tu.entity_type = 'country_card'
        AND tu.entity_id = cc.id
        AND tu.field_name = fields.field_name
        AND tu.is_active = TRUE
  );

INSERT INTO audit_localization_stage
SELECT 'legal_signal', ls.id, fields.field_name, fields.ru_text, fields.en_text
FROM legal_signals ls
CROSS JOIN LATERAL (
    VALUES
        ('title', COALESCE(ls.title_ru, ls.title), ls.title_en),
        ('summary', COALESCE(ls.summary_ru, ls.summary), ls.summary_en)
) AS fields(field_name, ru_text, en_text)
WHERE NULLIF(BTRIM(fields.ru_text), '') IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM translation_units tu
      WHERE tu.entity_type = 'legal_signal'
        AND tu.entity_id = ls.id
        AND tu.field_name = fields.field_name
        AND tu.is_active = TRUE
  );

INSERT INTO audit_localization_stage
SELECT 'evidence_item', evidence.id, fields.field_name, fields.ru_text, NULL
FROM evidence_items evidence
CROSS JOIN LATERAL (
    VALUES
        ('claim', evidence.claim),
        ('excerpt', evidence.excerpt)
) AS fields(field_name, ru_text)
WHERE NULLIF(BTRIM(fields.ru_text), '') IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM translation_units tu
      WHERE tu.entity_type = 'evidence_item'
        AND tu.entity_id = evidence.id
        AND tu.field_name = fields.field_name
        AND tu.is_active = TRUE
  );

INSERT INTO audit_localization_stage
SELECT 'source', source.id, 'title', source.title, NULL
FROM sources source
WHERE NULLIF(BTRIM(source.title), '') IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM translation_units tu
      WHERE tu.entity_type = 'source'
        AND tu.entity_id = source.id
        AND tu.field_name = 'title'
        AND tu.is_active = TRUE
  );

INSERT INTO audit_localization_stage
SELECT 'scenario', scenario.id, fields.field_name, fields.ru_text, fields.en_text
FROM scenarios scenario
CROSS JOIN LATERAL (
    VALUES
        ('title', COALESCE(scenario.title_ru, scenario.name), scenario.title_en),
        ('description', COALESCE(scenario.description_ru, scenario.description), scenario.description_en)
) AS fields(field_name, ru_text, en_text)
WHERE NULLIF(BTRIM(fields.ru_text), '') IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM translation_units tu
      WHERE tu.entity_type = 'scenario'
        AND tu.entity_id = scenario.id
        AND tu.field_name = fields.field_name
        AND tu.is_active = TRUE
  );

INSERT INTO audit_localization_stage
SELECT 'country_score', score.id, 'explanation', score.explanation_ru, score.explanation_en
FROM country_scores score
WHERE NULLIF(BTRIM(score.explanation_ru), '') IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM translation_units tu
      WHERE tu.entity_type = 'country_score'
        AND tu.entity_id = score.id
        AND tu.field_name = 'explanation'
        AND tu.is_active = TRUE
  );

INSERT INTO audit_localization_stage
SELECT 'country_score_breakdown', breakdown.id, 'explanation', breakdown.explanation_ru, breakdown.explanation_en
FROM country_score_breakdowns breakdown
WHERE NULLIF(BTRIM(breakdown.explanation_ru), '') IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM translation_units tu
      WHERE tu.entity_type = 'country_score_breakdown'
        AND tu.entity_id = breakdown.id
        AND tu.field_name = 'explanation'
        AND tu.is_active = TRUE
  );

INSERT INTO translation_units (
    entity_type,
    entity_id,
    field_name,
    original_locale_code,
    source_hash
)
SELECT
    entity_type,
    entity_id,
    field_name,
    'ru',
    ENCODE(DIGEST(ru_text, 'sha256'), 'hex')
FROM audit_localization_stage
ON CONFLICT (entity_type, entity_id, field_name) DO UPDATE
SET
    original_locale_code = EXCLUDED.original_locale_code,
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
    stage.ru_text,
    'original',
    'legacy',
    'ru',
    tu.source_hash,
    TRUE
FROM audit_localization_stage stage
JOIN translation_units tu
    ON tu.entity_type = stage.entity_type
    AND tu.entity_id = stage.entity_id
    AND tu.field_name = stage.field_name
ON CONFLICT (translation_unit_id, locale_code) DO UPDATE
SET
    text = EXCLUDED.text,
    status = EXCLUDED.status,
    method = EXCLUDED.method,
    source_locale_code = EXCLUDED.source_locale_code,
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
    stage.en_text,
    'needs_review',
    'legacy',
    'ru',
    tu.source_hash,
    FALSE
FROM audit_localization_stage stage
JOIN translation_units tu
    ON tu.entity_type = stage.entity_type
    AND tu.entity_id = stage.entity_id
    AND tu.field_name = stage.field_name
WHERE NULLIF(BTRIM(stage.en_text), '') IS NOT NULL
ON CONFLICT (translation_unit_id, locale_code) DO NOTHING;
