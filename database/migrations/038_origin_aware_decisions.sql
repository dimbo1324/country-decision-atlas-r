-- Migration 038: Origin-aware decisions: adds country_pair_compatibility tables (with sources/evidence) for origin/destination pairs.
CREATE TABLE IF NOT EXISTS country_pair_compatibility (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    origin_country_id UUID NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
    destination_country_id UUID NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'published',
    visa_note TEXT,
    tax_treaty_note TEXT,
    banking_note TEXT,
    flight_logistics_note TEXT,
    timezone_note TEXT,
    language_note TEXT,
    migration_restriction_note TEXT,
    practical_summary TEXT,
    compatibility_label TEXT NOT NULL DEFAULT 'unknown',
    confidence TEXT NOT NULL DEFAULT 'medium',
    freshness_status TEXT NOT NULL DEFAULT 'current',
    last_verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT country_pair_unique
        UNIQUE (origin_country_id, destination_country_id),
    CONSTRAINT country_pair_not_self_check
        CHECK (origin_country_id <> destination_country_id),
    CONSTRAINT country_pair_status_check
        CHECK (status IN ('draft', 'review', 'published', 'archived', 'rejected')),
    CONSTRAINT country_pair_label_check
        CHECK (compatibility_label IN (
            'favourable',
            'mixed',
            'restrictive',
            'unknown'
        )),
    CONSTRAINT country_pair_confidence_check
        CHECK (confidence IN ('low', 'medium', 'high')),
    CONSTRAINT country_pair_freshness_check
        CHECK (freshness_status IN ('fresh', 'current', 'stale', 'unknown'))
);

CREATE TABLE IF NOT EXISTS country_pair_compatibility_sources (
    country_pair_id UUID NOT NULL REFERENCES country_pair_compatibility(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    PRIMARY KEY (country_pair_id, source_id)
);

CREATE TABLE IF NOT EXISTS country_pair_compatibility_evidence (
    country_pair_id UUID NOT NULL REFERENCES country_pair_compatibility(id) ON DELETE CASCADE,
    evidence_item_id UUID NOT NULL REFERENCES evidence_items(id) ON DELETE CASCADE,
    PRIMARY KEY (country_pair_id, evidence_item_id)
);

CREATE INDEX IF NOT EXISTS idx_country_pair_origin
    ON country_pair_compatibility (origin_country_id);

CREATE INDEX IF NOT EXISTS idx_country_pair_destination
    ON country_pair_compatibility (destination_country_id);

CREATE INDEX IF NOT EXISTS idx_country_pair_status
    ON country_pair_compatibility (status);

CREATE INDEX IF NOT EXISTS idx_country_pair_label
    ON country_pair_compatibility (compatibility_label);

CREATE INDEX IF NOT EXISTS idx_country_pair_sources_source
    ON country_pair_compatibility_sources (source_id);

CREATE INDEX IF NOT EXISTS idx_country_pair_evidence_evidence
    ON country_pair_compatibility_evidence (evidence_item_id);

CREATE TABLE IF NOT EXISTS route_checklist_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    route_id UUID NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
    step_order INT NOT NULL,
    title TEXT NOT NULL,
    title_ru TEXT,
    description TEXT,
    description_ru TEXT,
    document_note TEXT,
    cost_note TEXT,
    timing_note TEXT,
    official_requirement_note TEXT,
    is_required BOOLEAN NOT NULL DEFAULT TRUE,
    status TEXT NOT NULL DEFAULT 'published',
    source_id UUID REFERENCES sources(id) ON DELETE SET NULL,
    evidence_item_id UUID REFERENCES evidence_items(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT route_checklist_step_unique
        UNIQUE (route_id, step_order),
    CONSTRAINT route_checklist_status_check
        CHECK (status IN ('draft', 'review', 'published', 'archived', 'rejected')),
    CONSTRAINT route_checklist_step_order_check
        CHECK (step_order > 0)
);

CREATE INDEX IF NOT EXISTS idx_route_checklist_route
    ON route_checklist_items (route_id, step_order);

CREATE INDEX IF NOT EXISTS idx_route_checklist_status
    ON route_checklist_items (status);

CREATE INDEX IF NOT EXISTS idx_route_checklist_source
    ON route_checklist_items (source_id)
    WHERE source_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_route_checklist_evidence
    ON route_checklist_items (evidence_item_id)
    WHERE evidence_item_id IS NOT NULL;

WITH pair_rows AS (
    SELECT *
    FROM (
        VALUES
            (
                'russia',
                'uruguay',
                'mixed',
                'low',
                'Uruguay''s published temporary and permanent residence procedures do not state a nationality-based bar for Russian citizens, but no dedicated Russia-Uruguay bilateral agreement is present in the currently seeded sources.',
                'No confirmed bilateral tax treaty between Russia and Uruguay is present in the currently seeded sources; verify current treaty status with a qualified tax advisor.',
                'Cross-border banking and card acceptance for Russia-issued documents may face extra compliance checks; verify with the receiving bank before relying on Russian-issued cards or transfers.',
                'Direct flights between Russia and Uruguay are not common; typical routings involve one or more layovers, which increases travel time and cost.',
                'Uruguay is UTC-3 year-round; Moscow is UTC+3, an 6-hour difference that narrows further for other Russian time zones.',
                'Uruguay''s official language is Spanish; Russia''s is Russian, so translated or apostilled documents are typically required for filings.',
                'No blanket migration restriction between Russia and Uruguay is identified in the currently seeded sources; verify current visa/entry policy before travel.',
                'Uruguay''s general residence procedure appears open to foreign nationals, but Russia-Uruguay banking, tax-treaty and logistics friction should be independently verified before relying on this MVP context.',
                '2026-06-01T00:00:00+00:00'
            ),
            (
                'russia',
                'argentina',
                'mixed',
                'low',
                'Argentina''s published DNM residence procedure does not state a nationality-based bar for Russian citizens, but no dedicated Russia-Argentina bilateral agreement is present in the currently seeded sources.',
                'No confirmed bilateral tax treaty between Russia and Argentina is present in the currently seeded sources; verify current treaty status with a qualified tax advisor.',
                'Cross-border banking and card acceptance for Russia-issued documents may face extra compliance checks; verify with the receiving bank before relying on Russian-issued cards or transfers.',
                'Direct flights between Russia and Argentina are not common; typical routings involve one or more layovers, which increases travel time and cost.',
                'Argentina is UTC-3 year-round; Moscow is UTC+3, an 6-hour difference that narrows further for other Russian time zones.',
                'Argentina''s official language is Spanish; Russia''s is Russian, so translated or apostilled documents are typically required for filings.',
                'No blanket migration restriction between Russia and Argentina is identified in the currently seeded sources; verify current visa/entry policy before travel.',
                'Argentina''s general DNM residence procedure appears open to foreign nationals, but Russia-Argentina banking, tax-treaty and logistics friction should be independently verified before relying on this MVP context.',
                '2026-06-01T00:00:00+00:00'
            ),
            (
                'argentina',
                'uruguay',
                'favourable',
                'low',
                'Argentina and Uruguay are neighbouring Mercosur member states; Uruguay''s published residence procedure does not state a nationality-based bar for Argentine citizens.',
                'No confirmed bilateral tax treaty text is present in the currently seeded sources; verify current treaty status with a qualified tax advisor.',
                'Regional bank transfers between Argentina and Uruguay are generally well established, but account-opening requirements should still be confirmed with the receiving bank.',
                'Uruguay and Argentina are close neighbours with frequent direct flights and land/river crossings, keeping logistics friction low.',
                'Both Argentina and Uruguay use UTC-3 year-round, so there is no time-zone adjustment for this pair.',
                'Argentina and Uruguay share Spanish as the official language, reducing translation friction for most filings.',
                'No blanket migration restriction between Argentina and Uruguay is identified in the currently seeded sources; verify current visa/entry policy before travel.',
                'Regional proximity, a shared language and no identified nationality-based bar make this pair comparatively favourable in this MVP context, though bilateral tax and banking specifics should still be verified.',
                '2026-06-01T00:00:00+00:00'
            ),
            (
                'uruguay',
                'argentina',
                'favourable',
                'low',
                'Argentina and Uruguay are neighbouring Mercosur member states; Argentina''s published DNM residence procedure does not state a nationality-based bar for Uruguayan citizens.',
                'No confirmed bilateral tax treaty text is present in the currently seeded sources; verify current treaty status with a qualified tax advisor.',
                'Regional bank transfers between Uruguay and Argentina are generally well established, but account-opening requirements should still be confirmed with the receiving bank.',
                'Uruguay and Argentina are close neighbours with frequent direct flights and land/river crossings, keeping logistics friction low.',
                'Both Uruguay and Argentina use UTC-3 year-round, so there is no time-zone adjustment for this pair.',
                'Uruguay and Argentina share Spanish as the official language, reducing translation friction for most filings.',
                'No blanket migration restriction between Uruguay and Argentina is identified in the currently seeded sources; verify current visa/entry policy before travel.',
                'Regional proximity, a shared language and no identified nationality-based bar make this pair comparatively favourable in this MVP context, though bilateral tax and banking specifics should still be verified.',
                '2026-06-01T00:00:00+00:00'
            )
    ) AS rows(
        origin_slug,
        destination_slug,
        compatibility_label,
        confidence,
        visa_note,
        tax_treaty_note,
        banking_note,
        flight_logistics_note,
        timezone_note,
        language_note,
        migration_restriction_note,
        practical_summary,
        last_verified_at
    )
)
INSERT INTO country_pair_compatibility (
    origin_country_id,
    destination_country_id,
    status,
    visa_note,
    tax_treaty_note,
    banking_note,
    flight_logistics_note,
    timezone_note,
    language_note,
    migration_restriction_note,
    practical_summary,
    compatibility_label,
    confidence,
    freshness_status,
    last_verified_at
)
SELECT
    oc.id,
    dc.id,
    'published',
    pr.visa_note,
    pr.tax_treaty_note,
    pr.banking_note,
    pr.flight_logistics_note,
    pr.timezone_note,
    pr.language_note,
    pr.migration_restriction_note,
    pr.practical_summary,
    pr.compatibility_label,
    pr.confidence,
    'current',
    pr.last_verified_at::timestamptz
FROM pair_rows pr
JOIN countries oc ON oc.slug = pr.origin_slug
JOIN countries dc ON dc.slug = pr.destination_slug
ON CONFLICT (origin_country_id, destination_country_id) DO UPDATE
SET
    status = EXCLUDED.status,
    visa_note = EXCLUDED.visa_note,
    tax_treaty_note = EXCLUDED.tax_treaty_note,
    banking_note = EXCLUDED.banking_note,
    flight_logistics_note = EXCLUDED.flight_logistics_note,
    timezone_note = EXCLUDED.timezone_note,
    language_note = EXCLUDED.language_note,
    migration_restriction_note = EXCLUDED.migration_restriction_note,
    practical_summary = EXCLUDED.practical_summary,
    compatibility_label = EXCLUDED.compatibility_label,
    confidence = EXCLUDED.confidence,
    freshness_status = EXCLUDED.freshness_status,
    last_verified_at = EXCLUDED.last_verified_at,
    updated_at = NOW();

WITH pair_source_rows AS (
    SELECT *
    FROM (
        VALUES
            ('russia', 'uruguay', 'uruguay', 'https://www.gub.uy/tramites/residencia-legal-permanente'),
            ('russia', 'uruguay', 'uruguay', 'https://www.liveinuruguay.uy/tax-residence'),
            ('russia', 'argentina', 'argentina', 'https://www.argentina.gob.ar/interior/migraciones'),
            ('russia', 'argentina', 'argentina', 'https://www.afip.gob.ar/monotributo/'),
            ('argentina', 'uruguay', 'uruguay', 'https://www.gub.uy/tramites/residencia-legal-permanente'),
            ('argentina', 'uruguay', 'uruguay', 'https://www.liveinuruguay.uy/tax-residence'),
            ('uruguay', 'argentina', 'argentina', 'https://www.argentina.gob.ar/interior/migraciones'),
            ('uruguay', 'argentina', 'argentina', 'https://www.afip.gob.ar/monotributo/')
    ) AS rows(origin_slug, destination_slug, source_country_slug, source_url)
)
INSERT INTO country_pair_compatibility_sources (country_pair_id, source_id)
SELECT
    cpc.id,
    s.id
FROM pair_source_rows psr
JOIN countries oc ON oc.slug = psr.origin_slug
JOIN countries dc ON dc.slug = psr.destination_slug
JOIN country_pair_compatibility cpc
    ON cpc.origin_country_id = oc.id AND cpc.destination_country_id = dc.id
JOIN countries sc ON sc.slug = psr.source_country_slug
JOIN sources s ON s.country_id = sc.id AND s.url = psr.source_url
ON CONFLICT (country_pair_id, source_id) DO NOTHING;

WITH pair_evidence_rows AS (
    SELECT *
    FROM (
        VALUES
            ('russia', 'uruguay', 'uruguay', 'https://www.gub.uy/tramites/residencia-legal-permanente'),
            ('russia', 'argentina', 'argentina', 'https://www.argentina.gob.ar/interior/migraciones'),
            ('argentina', 'uruguay', 'uruguay', 'https://www.gub.uy/tramites/residencia-legal-permanente'),
            ('uruguay', 'argentina', 'argentina', 'https://www.argentina.gob.ar/interior/migraciones')
    ) AS rows(origin_slug, destination_slug, source_country_slug, source_url)
),
ranked_pair_evidence AS (
    SELECT
        cpc.id AS country_pair_id,
        ei.id AS evidence_item_id,
        ROW_NUMBER() OVER (
            PARTITION BY cpc.id
            ORDER BY COALESCE(ei.retrieved_at, ei.created_at) DESC NULLS LAST, ei.id
        ) AS evidence_rank
    FROM pair_evidence_rows per
    JOIN countries oc ON oc.slug = per.origin_slug
    JOIN countries dc ON dc.slug = per.destination_slug
    JOIN country_pair_compatibility cpc
        ON cpc.origin_country_id = oc.id AND cpc.destination_country_id = dc.id
    JOIN countries sc ON sc.slug = per.source_country_slug
    JOIN sources s ON s.country_id = sc.id AND s.url = per.source_url
    JOIN evidence_items ei ON ei.source_id = s.id AND ei.country_id = sc.id
    WHERE ei.status = 'published'
)
INSERT INTO country_pair_compatibility_evidence (country_pair_id, evidence_item_id)
SELECT
    country_pair_id,
    evidence_item_id
FROM ranked_pair_evidence
WHERE evidence_rank = 1
ON CONFLICT (country_pair_id, evidence_item_id) DO NOTHING;

WITH checklist_rows AS (
    SELECT *
    FROM (
        VALUES
            (
                'uruguay',
                'temporary-legal-residence',
                1,
                'Confirm the current temporary residence procedure',
                'Проверьте актуальную процедуру временной резиденции',
                'Review the official procedure page before assuming any specific requirement or timeline.',
                'Проверьте официальную страницу процедуры до выводов о требованиях или сроках.',
                'Identity document and civil-status records are typically requested; confirm the exact list in the official procedure.',
                'Procedure fees must be checked on the official page; this checklist does not state a fixed amount.',
                'Processing time depends on the current procedure and case load; verify before planning travel.',
                TRUE,
                'https://www.gub.uy/tramites/residencia-legal-temporaria'
            ),
            (
                'uruguay',
                'temporary-legal-residence',
                2,
                'Prepare and legalise supporting documents',
                'Подготовьте и легализуйте подтверждающие документы',
                'Foreign-issued documents typically need translation and/or apostille before filing.',
                'Иностранные документы обычно требуют перевода и/или апостиля до подачи.',
                'Check whether a certified Spanish translation is required for each document.',
                'Translation and legalisation costs vary by document and provider.',
                NULL,
                TRUE,
                'https://www.gub.uy/tramites/residencia-legal-temporaria'
            ),
            (
                'uruguay',
                'temporary-legal-residence',
                3,
                'File the application and track its status',
                'Подайте заявление и отслеживайте его статус',
                'Submit the completed package through the official channel and keep the filing receipt.',
                'Подайте полный пакет через официальный канал и сохраните расписку о подаче.',
                NULL,
                NULL,
                'Renewal or follow-up deadlines depend on the granted status; verify in the current procedure.',
                FALSE,
                'https://www.gub.uy/tramites/residencia-legal-temporaria'
            ),
            (
                'argentina',
                'temporary-residence-dnm',
                1,
                'Confirm the current DNM residence category',
                'Уточните актуальную категорию проживания по DNM',
                'Review the DNM procedure page to identify the applicable residence category before filing.',
                'Проверьте страницу процедуры DNM, чтобы определить применимую категорию проживания.',
                'Identity document and entry records are typically requested; confirm the exact list with DNM.',
                'Procedure fees must be checked with DNM; this checklist does not state a fixed amount.',
                'Processing time depends on the current DNM procedure; verify before planning travel.',
                TRUE,
                'https://www.argentina.gob.ar/interior/migraciones'
            ),
            (
                'argentina',
                'temporary-residence-dnm',
                2,
                'Prepare and legalise supporting documents',
                'Подготовьте и легализуйте подтверждающие документы',
                'Foreign-issued documents typically need translation and/or apostille before filing with DNM.',
                'Иностранные документы обычно требуют перевода и/или апостиля до подачи в DNM.',
                'Check whether a certified Spanish translation is required for each document.',
                'Translation and legalisation costs vary by document and provider.',
                NULL,
                TRUE,
                'https://www.argentina.gob.ar/interior/migraciones'
            ),
            (
                'argentina',
                'temporary-residence-dnm',
                3,
                'File with DNM and track the resolution',
                'Подайте заявление в DNM и отслеживайте решение',
                'Submit the completed package through the official DNM channel and keep the filing receipt.',
                'Подайте полный пакет через официальный канал DNM и сохраните расписку о подаче.',
                NULL,
                NULL,
                'Renewal or follow-up deadlines depend on the granted category; verify with DNM.',
                FALSE,
                'https://www.argentina.gob.ar/interior/migraciones'
            ),
            (
                'argentina',
                'citizenship-two-year-residence-review',
                1,
                'Verify the residence-period signal before filing',
                'Проверьте сигнал о сроке проживания до подачи',
                'Use the official nationality and entry-requirements source to check the residence-period signal.',
                'Используйте официальный источник по гражданству и требованиям въезда для проверки срока проживания.',
                'Residence and civil-status records are typically requested; confirm the exact list with the competent authority.',
                'Court or filing fees must be verified with the competent authority.',
                'Processing time is case-specific and not derived from this checklist alone.',
                TRUE,
                'https://www.cancilleria.gob.ar/en/tourism-and-travel/visas'
            ),
            (
                'argentina',
                'citizenship-two-year-residence-review',
                2,
                'Consult a qualified professional before filing',
                'Проконсультируйтесь со специалистом до подачи',
                'Citizenship eligibility must be reviewed case by case; this checklist is not a substitute for legal advice.',
                'Право на гражданство нужно проверять индивидуально; чек-лист не заменяет юридическую консультацию.',
                NULL,
                NULL,
                NULL,
                TRUE,
                'https://www.cancilleria.gob.ar/en/tourism-and-travel/visas'
            ),
            (
                'russia',
                'permanent-residence-status-review',
                1,
                'Identify the applicable legal baseline',
                'Определите применимую правовую основу',
                'Use the official legal text to identify the baseline for long-term residence status before relying on assumptions.',
                'Используйте официальный текст закона, чтобы определить основу для долгосрочного статуса проживания.',
                'Identity and residence-history records are typically requested; confirm the exact list in the current procedure.',
                'Official fee amounts must be checked in the current filing procedure.',
                'Processing time depends on the current procedure and filing channel.',
                TRUE,
                'https://www.consultant.ru/document/cons_doc_LAW_37868/'
            ),
            (
                'russia',
                'permanent-residence-status-review',
                2,
                'Verify the current procedure and document package',
                'Проверьте актуальную процедуру и пакет документов',
                'The legal baseline does not by itself list the exact current filing package; verify separately.',
                'Правовая основа сама по себе не определяет точный пакет подачи; проверяйте отдельно.',
                'Confirm the current document package with the filing authority before submission.',
                NULL,
                NULL,
                FALSE,
                'https://www.consultant.ru/document/cons_doc_LAW_37868/'
            ),
            (
                'russia',
                'permanent-residence-status-review',
                3,
                'Review tax and banking implications separately',
                'Отдельно проверьте налоговые и банковские последствия',
                'Residence status does not by itself answer tax or banking questions; use the tax authority source separately.',
                'Статус проживания сам по себе не отвечает на налоговые или банковские вопросы; проверяйте отдельно.',
                NULL,
                NULL,
                NULL,
                FALSE,
                'https://www.nalog.gov.ru/eng/'
            )
    ) AS rows(
        country_slug,
        route_slug,
        step_order,
        title,
        title_ru,
        description,
        description_ru,
        document_note,
        cost_note,
        timing_note,
        is_required,
        source_url
    )
)
INSERT INTO route_checklist_items (
    route_id,
    step_order,
    title,
    title_ru,
    description,
    description_ru,
    document_note,
    cost_note,
    timing_note,
    is_required,
    status,
    source_id
)
SELECT
    r.id,
    cr.step_order,
    cr.title,
    cr.title_ru,
    cr.description,
    cr.description_ru,
    cr.document_note,
    cr.cost_note,
    cr.timing_note,
    cr.is_required,
    'published',
    s.id
FROM checklist_rows cr
JOIN countries c ON c.slug = cr.country_slug
JOIN routes r ON r.country_id = c.id AND r.slug = cr.route_slug
LEFT JOIN sources s ON s.country_id = c.id AND s.url = cr.source_url
ON CONFLICT (route_id, step_order) DO UPDATE
SET
    title = EXCLUDED.title,
    title_ru = EXCLUDED.title_ru,
    description = EXCLUDED.description,
    description_ru = EXCLUDED.description_ru,
    document_note = EXCLUDED.document_note,
    cost_note = EXCLUDED.cost_note,
    timing_note = EXCLUDED.timing_note,
    is_required = EXCLUDED.is_required,
    status = EXCLUDED.status,
    source_id = EXCLUDED.source_id,
    updated_at = NOW();
