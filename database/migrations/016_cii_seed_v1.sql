INSERT INTO cii_metric_definitions
    (slug, name_en, name_ru, description_en, description_ru, polarity, source_name, source_url, display_order)
VALUES
    (
        'rule_of_law',
        'Rule of Law',
        'Верховенство права',
        'Extent to which agents have confidence in and abide by the rules of society.',
        'Степень уверенности общества в соблюдении правовых норм.',
        'positive',
        'World Bank WGI 2023',
        'https://info.worldbank.org/governance/wgi/',
        1
    ),
    (
        'economic_freedom',
        'Economic Freedom',
        'Экономическая свобода',
        'Degree of personal choice, voluntary exchange, and freedom to compete in markets.',
        'Степень личного выбора, свободного обмена и конкуренции на рынках.',
        'positive',
        'Heritage Foundation Index of Economic Freedom 2024',
        'https://www.heritage.org/index/',
        2
    ),
    (
        'political_stability',
        'Political Stability',
        'Политическая стабильность',
        'Likelihood that the government will be destabilized by unconstitutional or violent means.',
        'Вероятность дестабилизации правительства неконституционными или насильственными методами.',
        'positive',
        'World Bank WGI 2023',
        'https://info.worldbank.org/governance/wgi/',
        3
    ),
    (
        'safety',
        'Physical Safety',
        'Физическая безопасность',
        'Level of personal safety and absence of organized conflict.',
        'Уровень личной безопасности и отсутствие организованных конфликтов.',
        'positive',
        'Global Peace Index 2023',
        'https://www.visionofhumanity.org/maps/#/',
        4
    ),
    (
        'corruption',
        'Anti-Corruption',
        'Антикоррупционность',
        'Perceived levels of public sector corruption.',
        'Воспринимаемый уровень коррупции в государственном секторе.',
        'positive',
        'Transparency International CPI 2023',
        'https://www.transparency.org/en/cpi/2023',
        5
    ),
    (
        'digital_access',
        'Digital Access',
        'Цифровой доступ',
        'Internet penetration and digital freedom of the country.',
        'Проникновение интернета и цифровая свобода в стране.',
        'positive',
        'Freedom House: Freedom on the Net 2023',
        'https://freedomhouse.org/report/freedom-net',
        6
    )
ON CONFLICT (slug) DO NOTHING;

INSERT INTO scenario_metric_weights (version, metric_id, weight)
SELECT
    'v1.0',
    id,
    ROUND(1.0 / 6, 4)
FROM cii_metric_definitions
WHERE is_active = TRUE
ON CONFLICT (version, metric_id) DO NOTHING;

INSERT INTO country_metric_values
    (country_id, metric_id, raw_value, normalized_value, data_year, source_name, source_url, reliability)
SELECT
    c.id,
    m.id,
    v.raw_value,
    v.normalized_value,
    v.data_year,
    v.source_name,
    v.source_url,
    v.reliability
FROM countries c
CROSS JOIN (
    VALUES
        ('russia', 'rule_of_law',       20.00, 20.00, 2023, 'World Bank WGI 2023',                      'https://info.worldbank.org/governance/wgi/',        'high'),
        ('russia', 'economic_freedom',  54.20, 54.20, 2024, 'Heritage Foundation Index 2024',            'https://www.heritage.org/index/',                  'high'),
        ('russia', 'political_stability', 13.00, 13.00, 2023, 'World Bank WGI 2023',                    'https://info.worldbank.org/governance/wgi/',        'high'),
        ('russia', 'safety',            38.00, 38.00, 2023, 'Global Peace Index 2023 (inverted)',        'https://www.visionofhumanity.org/maps/#/',          'high'),
        ('russia', 'corruption',        26.00, 26.00, 2023, 'Transparency International CPI 2023',      'https://www.transparency.org/en/cpi/2023',         'high'),
        ('russia', 'digital_access',    21.00, 21.00, 2023, 'Freedom House: Freedom on the Net 2023',   'https://freedomhouse.org/report/freedom-net',      'high'),

        ('uruguay', 'rule_of_law',       72.00, 72.00, 2023, 'World Bank WGI 2023',                     'https://info.worldbank.org/governance/wgi/',        'high'),
        ('uruguay', 'economic_freedom',  68.10, 68.10, 2024, 'Heritage Foundation Index 2024',           'https://www.heritage.org/index/',                  'high'),
        ('uruguay', 'political_stability', 76.00, 76.00, 2023, 'World Bank WGI 2023',                   'https://info.worldbank.org/governance/wgi/',        'high'),
        ('uruguay', 'safety',            63.00, 63.00, 2023, 'Global Peace Index 2023 (inverted)',       'https://www.visionofhumanity.org/maps/#/',          'high'),
        ('uruguay', 'corruption',        73.00, 73.00, 2023, 'Transparency International CPI 2023',     'https://www.transparency.org/en/cpi/2023',         'high'),
        ('uruguay', 'digital_access',    62.00, 62.00, 2023, 'Freedom House: Freedom on the Net 2023',  'https://freedomhouse.org/report/freedom-net',      'high')
) AS v(country_slug, metric_slug, raw_value, normalized_value, data_year, source_name, source_url, reliability)
JOIN cii_metric_definitions m ON m.slug = v.metric_slug
WHERE c.slug = v.country_slug
ON CONFLICT (country_id, metric_id) DO NOTHING;

INSERT INTO country_cii_scores
    (country_id, version, overall_score, confidence, drift, metric_scores, calculated_at)
SELECT
    c.id,
    'v1.0',
    ROUND(
        (
            SELECT SUM(cmv.normalized_value * smw.weight)
            FROM country_metric_values cmv
            JOIN scenario_metric_weights smw ON smw.metric_id = cmv.metric_id AND smw.version = 'v1.0'
            WHERE cmv.country_id = c.id
        ),
        2
    ),
    'high',
    NULL,
    COALESCE(
        (
            SELECT jsonb_agg(
                jsonb_build_object(
                    'slug', m.slug,
                    'name_en', m.name_en,
                    'name_ru', m.name_ru,
                    'score', cmv.normalized_value,
                    'weight', smw.weight,
                    'weighted_score', ROUND(cmv.normalized_value * smw.weight, 2),
                    'data_year', cmv.data_year,
                    'source_name', cmv.source_name,
                    'reliability', cmv.reliability
                )
                ORDER BY m.display_order
            )
            FROM country_metric_values cmv
            JOIN cii_metric_definitions m ON m.id = cmv.metric_id
            JOIN scenario_metric_weights smw ON smw.metric_id = cmv.metric_id AND smw.version = 'v1.0'
            WHERE cmv.country_id = c.id
        ),
        '[]'::jsonb
    ),
    NOW()
FROM countries c
WHERE c.slug IN ('russia', 'uruguay')
ON CONFLICT (country_id, version) DO UPDATE
    SET overall_score  = EXCLUDED.overall_score,
        metric_scores  = EXCLUDED.metric_scores,
        calculated_at  = EXCLUDED.calculated_at,
        updated_at     = NOW();
