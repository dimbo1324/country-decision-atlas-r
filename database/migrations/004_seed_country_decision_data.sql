ALTER TABLE scenarios DROP CONSTRAINT IF EXISTS scenarios_slug_format;

ALTER TABLE
    scenarios
ADD
    CONSTRAINT scenarios_slug_format CHECK (slug ~ '^[a-z0-9]+(?:[-_][a-z0-9]+)*$');

WITH scenario_defaults AS (
    SELECT
        '{
          "legalization_score": 0.25,
          "long_term_status_score": 0.20,
          "cost_of_living_score": 0.15,
          "safety_score": 0.15,
          "business_score": 0.10,
          "legal_stability_score": 0.10,
          "source_quality_score": 0.05
        }' :: jsonb AS weights
)
INSERT INTO
    scenarios (
        slug,
        name,
        description,
        title_en,
        title_ru,
        description_en,
        description_ru,
        weights
    )
SELECT
    scenario_rows.slug,
    scenario_rows.title_en,
    scenario_rows.description_en,
    scenario_rows.title_en,
    scenario_rows.title_ru,
    scenario_rows.description_en,
    scenario_rows.description_ru,
    scenario_defaults.weights
FROM
    (
        VALUES
            (
                'relocation_residence',
                'Relocation and residence',
                'Релокация и ВНЖ',
                'Compare countries for a first long-term relocation and residence path.',
                'Сравнение стран для первичной долгосрочной релокации и пути к ВНЖ.'
            ),
            (
                'permanent_residence_citizenship',
                'Permanent residence and citizenship',
                'ПМЖ и гражданство',
                'Compare long-term status, permanent residence, and citizenship planning fit.',
                'Сравнение долгосрочного статуса, ПМЖ и планирования гражданства.'
            ),
            (
                'low_budget_living',
                'Low-budget living',
                'Жизнь с ограниченным бюджетом',
                'Compare affordability, practical costs, and basic stability.',
                'Сравнение доступности, практических расходов и базовой стабильности.'
            ),
            (
                'business_self_employment',
                'Business and self-employment',
                'Бизнес и самозанятость',
                'Compare countries for small business, self-employment, and banking practicality.',
                'Сравнение стран для малого бизнеса, самозанятости и банковской практичности.'
            ),
            (
                'safety_political_risk',
                'Safety and political risk',
                'Безопасность и политический риск',
                'Compare safety, rule-of-law, freedom, and political-risk signals.',
                'Сравнение безопасности, правовой стабильности, свобод и политических рисков.'
            )
    ) AS scenario_rows(
        slug,
        title_en,
        title_ru,
        description_en,
        description_ru
    )
    CROSS JOIN scenario_defaults ON CONFLICT (slug) DO
UPDATE
SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    title_en = EXCLUDED.title_en,
    title_ru = EXCLUDED.title_ru,
    description_en = EXCLUDED.description_en,
    description_ru = EXCLUDED.description_ru,
    weights = EXCLUDED.weights,
    is_active = TRUE;

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
    'en',
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
    countries c
    JOIN (
        VALUES
            (
                'russia',
                'Russia is included as a baseline country for origin, risk, and long-term-status comparison. This MVP card is demonstration content, not legal advice.',
                'Migration suitability depends heavily on personal status, timing, and source verification.',
                'Tax treatment requires expert review and current source checks before any decision.',
                'Cost signals are mixed and must be interpreted with city-level context.',
                'Business practicality depends on banking, compliance, and sanctions-sensitive workflows.',
                'Safety and political-risk signals require careful review for each user profile.',
                'Current MVP signals emphasize administrative, safety, and political-risk traceability.',
                'Primary risks: legal uncertainty, changing administrative practice, and source volatility.',
                'Sources are MVP demonstration records with traceable URLs and review timestamps.'
            ),
            (
                'uruguay',
                'Uruguay is included as a candidate country for residence, lifestyle stability, and business comparison. This MVP card is demonstration content, not legal advice.',
                'Residence planning appears comparatively structured in this MVP model but still requires expert verification.',
                'Tax treatment depends on residence status, income source, and current professional advice.',
                'Cost signals vary by city and lifestyle; Montevideo may differ from smaller locations.',
                'Business practicality is scored through banking, setup clarity, and source quality signals.',
                'Safety and political-risk scoring is comparatively stronger in this MVP data set.',
                'Current MVP signals emphasize residence planning, business, banking, and stability.',
                'Primary risks: cost assumptions, processing variability, and incomplete source depth.',
                'Sources are MVP demonstration records with traceable URLs and review timestamps.'
            )
    ) AS card(
        slug,
        executive_summary,
        migration_overview,
        tax_overview,
        cost_of_living_overview,
        business_overview,
        safety_overview,
        legal_signals_summary,
        risk_summary,
        source_summary
    ) ON card.slug = c.slug ON CONFLICT (country_id, locale) DO
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
    src.title,
    src.url,
    src.source_type,
    src.publisher,
    c.id,
    src.language,
    src.confidence,
    src.confidence,
    DATE '2026-01-15',
    CURRENT_DATE,
    CURRENT_DATE,
    'MVP demonstration source. Verify against primary material before production use.'
FROM
    (
        VALUES
            (
                'russia_official_migration_overview',
                'Russia official migration overview demo source',
                'https://example.invalid/russia/official-migration-overview',
                'official',
                'Demo official registry',
                'russia',
                'en',
                'medium'
            ),
            (
                'russia_residence_process_note',
                'Russia residence process demo source',
                'https://example.invalid/russia/residence-process',
                'official',
                'Demo migration authority',
                'russia',
                'en',
                'medium'
            ),
            (
                'russia_citizenship_status_note',
                'Russia citizenship status demo source',
                'https://example.invalid/russia/citizenship-status',
                'official',
                'Demo civic registry',
                'russia',
                'en',
                'medium'
            ),
            (
                'russia_tax_residence_note',
                'Russia tax residence demo source',
                'https://example.invalid/russia/tax-residence',
                'expert',
                'Demo tax expert desk',
                'russia',
                'en',
                'low'
            ),
            (
                'russia_cost_living_dataset',
                'Russia cost-of-living demo dataset',
                'https://example.invalid/russia/cost-living-dataset',
                'dataset',
                'Demo data lab',
                'russia',
                'en',
                'low'
            ),
            (
                'russia_business_setup_note',
                'Russia business setup demo source',
                'https://example.invalid/russia/business-setup',
                'expert',
                'Demo business desk',
                'russia',
                'en',
                'low'
            ),
            (
                'russia_banking_practicality_note',
                'Russia banking practicality demo source',
                'https://example.invalid/russia/banking-practicality',
                'expert',
                'Demo banking desk',
                'russia',
                'en',
                'low'
            ),
            (
                'russia_safety_signal_note',
                'Russia safety signal demo source',
                'https://example.invalid/russia/safety-signal',
                'media',
                'Demo risk monitor',
                'russia',
                'en',
                'low'
            ),
            (
                'russia_rule_law_note',
                'Russia rule-of-law demo source',
                'https://example.invalid/russia/rule-of-law',
                'dataset',
                'Demo governance dataset',
                'russia',
                'en',
                'low'
            ),
            (
                'russia_political_risk_note',
                'Russia political-risk demo source',
                'https://example.invalid/russia/political-risk',
                'media',
                'Demo political monitor',
                'russia',
                'en',
                'low'
            ),
            (
                'uruguay_official_residence_overview',
                'Uruguay official residence overview demo source',
                'https://example.invalid/uruguay/official-residence-overview',
                'official',
                'Demo residence authority',
                'uruguay',
                'en',
                'medium'
            ),
            (
                'uruguay_permanent_residence_note',
                'Uruguay permanent residence demo source',
                'https://example.invalid/uruguay/permanent-residence',
                'official',
                'Demo civil registry',
                'uruguay',
                'en',
                'medium'
            ),
            (
                'uruguay_citizenship_status_note',
                'Uruguay citizenship planning demo source',
                'https://example.invalid/uruguay/citizenship-planning',
                'official',
                'Demo civic authority',
                'uruguay',
                'en',
                'medium'
            ),
            (
                'uruguay_tax_residence_note',
                'Uruguay tax residence demo source',
                'https://example.invalid/uruguay/tax-residence',
                'expert',
                'Demo tax expert desk',
                'uruguay',
                'en',
                'low'
            ),
            (
                'uruguay_cost_living_dataset',
                'Uruguay cost-of-living demo dataset',
                'https://example.invalid/uruguay/cost-living-dataset',
                'dataset',
                'Demo data lab',
                'uruguay',
                'en',
                'low'
            ),
            (
                'uruguay_business_setup_note',
                'Uruguay business setup demo source',
                'https://example.invalid/uruguay/business-setup',
                'expert',
                'Demo business desk',
                'uruguay',
                'en',
                'medium'
            ),
            (
                'uruguay_banking_practicality_note',
                'Uruguay banking practicality demo source',
                'https://example.invalid/uruguay/banking-practicality',
                'expert',
                'Demo banking desk',
                'uruguay',
                'en',
                'low'
            ),
            (
                'uruguay_safety_signal_note',
                'Uruguay safety signal demo source',
                'https://example.invalid/uruguay/safety-signal',
                'dataset',
                'Demo safety dataset',
                'uruguay',
                'en',
                'medium'
            ),
            (
                'uruguay_rule_law_note',
                'Uruguay rule-of-law demo source',
                'https://example.invalid/uruguay/rule-of-law',
                'dataset',
                'Demo governance dataset',
                'uruguay',
                'en',
                'medium'
            ),
            (
                'uruguay_political_risk_note',
                'Uruguay political-risk demo source',
                'https://example.invalid/uruguay/political-risk',
                'media',
                'Demo political monitor',
                'uruguay',
                'en',
                'medium'
            )
    ) AS src(
        key,
        title,
        url,
        source_type,
        publisher,
        country_slug,
        language,
        confidence
    )
    JOIN countries c ON c.slug = src.country_slug ON CONFLICT (url) DO
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
    sig.title_en,
    sig.summary_en,
    sig.title_en,
    sig.title_ru,
    sig.summary_en,
    sig.summary_ru,
    sig.signal_type,
    CASE
        WHEN sig.impact_direction = 'uncertain' THEN 'unknown'
        ELSE sig.impact_direction
    END,
    sig.impact_level,
    'published',
    sig.confidence,
    sig.impact_direction,
    sig.impact_level,
    sig.affected_groups :: jsonb,
    DATE '2026-01-15',
    DATE '2026-01-15',
    DATE '2026-01-15',
    s.id,
    sig.confidence
FROM
    (
        VALUES
            (
                'russia',
                'https://example.invalid/russia/official-migration-overview',
                'Migration status requires case-specific verification',
                'Миграционный статус требует индивидуальной проверки',
                'MVP signal: administrative requirements should be checked before relying on any pathway.',
                'MVP-сигнал: административные требования нужно проверять перед выбором маршрута.',
                'migration',
                'mixed',
                'medium',
                '["relocators","families"]',
                'medium'
            ),
            (
                'russia',
                'https://example.invalid/russia/residence-process',
                'Residence processing uncertainty',
                'Неопределённость процесса ВНЖ',
                'MVP signal: processing predictability is treated as a risk factor in this model.',
                'MVP-сигнал: предсказуемость процесса учитывается как риск.',
                'residence',
                'negative',
                'medium',
                '["residence_applicants"]',
                'low'
            ),
            (
                'russia',
                'https://example.invalid/russia/citizenship-status',
                'Long-term status requires expert review',
                'Долгосрочный статус требует экспертной проверки',
                'MVP signal: long-term status planning should not rely on placeholder content.',
                'MVP-сигнал: планирование долгосрочного статуса не должно опираться на демо-данные.',
                'citizenship',
                'uncertain',
                'medium',
                '["citizenship_applicants"]',
                'low'
            ),
            (
                'russia',
                'https://example.invalid/russia/banking-practicality',
                'Banking practicality may affect business planning',
                'Банковская практичность может влиять на бизнес-планирование',
                'MVP signal: banking and compliance friction should be reviewed for each profile.',
                'MVP-сигнал: банковские и compliance-ограничения нужно проверять по профилю.',
                'banking',
                'negative',
                'high',
                '["entrepreneurs","remote_workers"]',
                'low'
            ),
            (
                'russia',
                'https://example.invalid/russia/political-risk',
                'Political-risk sensitivity is material',
                'Политический риск является существенным фактором',
                'MVP signal: political-risk exposure is relevant for relocation decisions.',
                'MVP-сигнал: политический риск важен для решений о релокации.',
                'political_risk',
                'negative',
                'high',
                '["families","entrepreneurs","students"]',
                'low'
            ),
            (
                'uruguay',
                'https://example.invalid/uruguay/official-residence-overview',
                'Residence pathway appears comparatively structured',
                'Путь к ВНЖ выглядит сравнительно структурированным',
                'MVP signal: residence planning is modeled as comparatively clear, pending expert verification.',
                'MVP-сигнал: путь к ВНЖ моделируется как сравнительно понятный, нужна экспертная проверка.',
                'residence',
                'positive',
                'medium',
                '["residence_applicants","families"]',
                'medium'
            ),
            (
                'uruguay',
                'https://example.invalid/uruguay/permanent-residence',
                'Long-term status planning is a core review area',
                'Планирование долгосрочного статуса требует отдельной проверки',
                'MVP signal: permanent residence planning should be reviewed with current sources.',
                'MVP-сигнал: планирование ПМЖ нужно проверять по актуальным источникам.',
                'citizenship',
                'mixed',
                'medium',
                '["long_term_relocators"]',
                'medium'
            ),
            (
                'uruguay',
                'https://example.invalid/uruguay/business-setup',
                'Business setup is relevant for self-employed users',
                'Открытие бизнеса важно для самозанятых пользователей',
                'MVP signal: business setup looks relevant but still depends on banking and tax details.',
                'MVP-сигнал: бизнес-регистрация выглядит релевантной, но зависит от банков и налогов.',
                'business',
                'positive',
                'medium',
                '["entrepreneurs","self_employed"]',
                'medium'
            ),
            (
                'uruguay',
                'https://example.invalid/uruguay/safety-signal',
                'Safety and stability signal is comparatively stronger',
                'Сигнал безопасности и стабильности сравнительно сильнее',
                'MVP signal: safety and stability contribute positively to decision output.',
                'MVP-сигнал: безопасность и стабильность положительно влияют на решение.',
                'safety',
                'positive',
                'medium',
                '["families","retirees","students"]',
                'medium'
            ),
            (
                'uruguay',
                'https://example.invalid/uruguay/cost-living-dataset',
                'Cost of living requires city-level validation',
                'Стоимость жизни требует проверки на уровне города',
                'MVP signal: cost assumptions should be checked against current city-level budgets.',
                'MVP-сигнал: предположения о расходах нужно сверять с актуальными городскими бюджетами.',
                'cost_of_living',
                'mixed',
                'medium',
                '["low_budget_users"]',
                'low'
            )
    ) AS sig(
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
    JOIN countries c ON c.slug = sig.country_slug
    JOIN sources s ON s.url = sig.source_url ON CONFLICT (country_id, title) DO
UPDATE
SET
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
    c.id,
    ls.id,
    ev.claim,
    ev.claim,
    s.url || '/evidence/' || ev.n :: text,
    ev.excerpt,
    'decision_evidence',
    s.confidence,
    DATE '2026-01-15',
    ev.claim,
    ev.excerpt,
    CURRENT_DATE,
    s.confidence
FROM
    legal_signals ls
    JOIN countries c ON c.id = ls.country_id
    JOIN sources s ON s.id = ls.source_id
    JOIN LATERAL (
        VALUES
            (
                1,
                ls.title_en || ' evidence claim A',
                'Synthetic MVP excerpt A. Verify source before use.'
            ),
            (
                2,
                ls.title_en || ' evidence claim B',
                'Synthetic MVP excerpt B. Not legal advice.'
            )
    ) AS ev(n, claim, excerpt) ON TRUE
WHERE
    ls.status = 'published'
    AND NOT EXISTS (
        SELECT
            1
        FROM
            evidence_items ei
        WHERE
            ei.url = s.url || '/evidence/' || ev.n :: text
    );

WITH score_rows AS (
    SELECT
        c.id AS country_id,
        sc.id AS scenario_id,
        c.slug AS country_slug,
        sc.slug AS scenario_slug,
        CASE
            WHEN c.slug = 'uruguay'
            AND sc.slug = 'relocation_residence' THEN 72
            WHEN c.slug = 'russia'
            AND sc.slug = 'relocation_residence' THEN 43
            WHEN c.slug = 'uruguay'
            AND sc.slug = 'permanent_residence_citizenship' THEN 68
            WHEN c.slug = 'russia'
            AND sc.slug = 'permanent_residence_citizenship' THEN 41
            WHEN c.slug = 'uruguay'
            AND sc.slug = 'low_budget_living' THEN 61
            WHEN c.slug = 'russia'
            AND sc.slug = 'low_budget_living' THEN 49
            WHEN c.slug = 'uruguay'
            AND sc.slug = 'business_self_employment' THEN 66
            WHEN c.slug = 'russia'
            AND sc.slug = 'business_self_employment' THEN 38
            WHEN c.slug = 'uruguay'
            AND sc.slug = 'safety_political_risk' THEN 74
            ELSE 34
        END :: numeric(5, 2) AS score
    FROM
        countries c
        CROSS JOIN scenarios sc
    WHERE
        c.slug IN ('russia', 'uruguay')
        AND sc.slug IN (
            'relocation_residence',
            'permanent_residence_citizenship',
            'low_budget_living',
            'business_self_employment',
            'safety_political_risk'
        )
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
    country_id,
    scenario_id,
    score,
    'MVP-оценка подбора',
    'Редакторская оценка для MVP-движка подбора.',
    'Score is based on seeded breakdown criteria, legal signals, evidence links, and source quality. It is not legal advice.',
    'Оценка основана на демо-критериях, правовых сигналах, evidence-связях и качестве источников. Это не юридическая консультация.',
    'medium',
    NOW()
FROM
    score_rows ON CONFLICT (country_id, scenario_id) DO
UPDATE
SET
    score = EXCLUDED.score,
    score_label = EXCLUDED.score_label,
    summary = EXCLUDED.summary,
    explanation_en = EXCLUDED.explanation_en,
    explanation_ru = EXCLUDED.explanation_ru,
    confidence = EXCLUDED.confidence,
    calculated_at = EXCLUDED.calculated_at;

WITH breakdown_seed AS (
    SELECT
        cs.id AS country_score_id,
        c.slug AS country_slug,
        sc.slug AS scenario_slug,
        criteria.criterion,
        criteria.weight,
        CASE
            WHEN c.slug = 'uruguay' THEN criteria.uruguay_score
            ELSE criteria.russia_score
        END :: numeric(5, 2) AS criterion_score
    FROM
        country_scores cs
        JOIN countries c ON c.id = cs.country_id
        JOIN scenarios sc ON sc.id = cs.scenario_id
        CROSS JOIN (
            VALUES
                ('legalization_score', 0.25, 72, 43),
                ('long_term_status_score', 0.20, 68, 41),
                ('cost_of_living_score', 0.15, 58, 55),
                ('safety_score', 0.15, 76, 35),
                ('business_score', 0.10, 66, 39),
                ('legal_stability_score', 0.10, 72, 34),
                ('source_quality_score', 0.05, 70, 48)
        ) AS criteria(criterion, weight, uruguay_score, russia_score)
    WHERE
        c.slug IN ('russia', 'uruguay')
        AND sc.slug IN (
            'relocation_residence',
            'permanent_residence_citizenship',
            'low_budget_living',
            'business_self_employment',
            'safety_political_risk'
        )
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
    country_score_id,
    criterion,
    criterion_score,
    weight,
    ROUND(criterion_score * weight, 4),
    'MVP criterion explanation for ' || criterion || '. Linked source references are demonstration data and require expert review.',
    'MVP-объяснение критерия ' || criterion || '. Связанные источники являются демо-данными и требуют экспертной проверки.',
    COALESCE(
        (
            SELECT
                jsonb_agg(id :: text)
            FROM
                (
                    SELECT
                        sources.id
                    FROM
                        sources
                        JOIN countries ON countries.id = sources.country_id
                    WHERE
                        countries.slug = breakdown_seed.country_slug
                    ORDER BY
                        sources.title
                    LIMIT
                        3
                ) AS source_subset
        ),
        '[]' :: jsonb
    ),
    'medium'
FROM
    breakdown_seed ON CONFLICT (country_score_id, criterion) DO
UPDATE
SET
    score = EXCLUDED.score,
    weight = EXCLUDED.weight,
    weighted_score = EXCLUDED.weighted_score,
    explanation_en = EXCLUDED.explanation_en,
    explanation_ru = EXCLUDED.explanation_ru,
    source_ids = EXCLUDED.source_ids,
    confidence = EXCLUDED.confidence;

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
    2026,
    story.scenario,
    story.budget_initial_usd,
    story.budget_monthly_usd,
    story.legal_path,
    story.documents_used :: jsonb,
    story.problems,
    story.positive_outcome,
    story.negative_outcome,
    story.advice,
    story.satisfaction_score,
    'synthetic',
    'published',
    TRUE,
    'Синтетический пример только для MVP-демонстрации.'
FROM
    (
        VALUES
            (
                'russia',
                'uruguay',
                'Montevideo',
                'relocation_residence',
                12000,
                2500,
                'Планирование резидентства',
                '["passport","apostilled_records","income_evidence"]',
                'Планирование бюджета и сроки документов были основными смоделированными проблемами.',
                'Смоделированный пользователь получил более чёткий путь принятия решений.',
                'Процесс всё равно потребовал экспертной проверки.',
                'Проверяйте каждое документальное требование перед поездкой.',
                7.5
            ),
            (
                'russia',
                'uruguay',
                'Punta del Este',
                'business_self_employment',
                18000,
                3200,
                'Оформление самозанятости',
                '["passport","business_plan","bank_reference"]',
                'Банковские предположения были неопределёнными в симуляции.',
                'Смоделированный пользователь выявил вопросы регистрации бизнеса на раннем этапе.',
                'Расходы оказались выше ожидаемых.',
                'Разделяйте консультации по резидентству, налогам и банковским вопросам.',
                6.8
            ),
            (
                'uruguay',
                'russia',
                'Moscow',
                'low_budget_living',
                7000,
                1600,
                'Планирование временного пребывания',
                '["passport","insurance","rental_agreement"]',
                'Предположения о расходах на уровне города было сложно сравнивать.',
                'Смоделированный пользователь составил более чёткий бюджетный чеклист.',
                'Правовой путь остался неопределённым.',
                'Рассматривайте сравнения расходов в контексте конкретного города.',
                5.9
            ),
            (
                'russia',
                'uruguay',
                'Montevideo',
                'safety_political_risk',
                15000,
                2800,
                'Планирование семейной релокации',
                '["passport","birth_certificates","school_records"]',
                'Логистика школы и семьи требовала более глубокой проработки источников.',
                'Смоделированная семья приоритизировала сигналы стабильности.',
                'Неопределённость сроков сохранилась.',
                'Используйте карточку как список вопросов для экспертной проверки.',
                7.2
            )
    ) AS story(
        origin_slug,
        destination_slug,
        city,
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
    JOIN countries origin ON origin.slug = story.origin_slug
    JOIN countries destination ON destination.slug = story.destination_slug
WHERE
    NOT EXISTS (
        SELECT
            1
        FROM
            user_stories existing
        WHERE
            existing.destination_country_id = destination.id
            AND existing.city = story.city
            AND existing.scenario = story.scenario
            AND existing.is_synthetic = TRUE
    );

INSERT INTO
    user_story_documents (
        user_story_id,
        document_type,
        title,
        url,
        is_public
    )
SELECT
    us.id,
    'checklist',
    'Synthetic document checklist for ' || us.scenario,
    'https://example.invalid/user-stories/' || us.id :: text || '/checklist',
    FALSE
FROM
    user_stories us
WHERE
    us.is_synthetic = TRUE
    AND NOT EXISTS (
        SELECT
            1
        FROM
            user_story_documents usd
        WHERE
            usd.user_story_id = us.id
            AND usd.document_type = 'checklist'
    );
