CREATE TABLE IF NOT EXISTS routes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_id UUID NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
    route_type TEXT NOT NULL,
    slug TEXT NOT NULL,
    title TEXT NOT NULL,
    title_ru TEXT,
    summary TEXT,
    summary_ru TEXT,
    eligibility_summary TEXT,
    eligibility_summary_ru TEXT,
    income_requirement_note TEXT,
    income_requirement_note_ru TEXT,
    fees_note TEXT,
    fees_note_ru TEXT,
    processing_time_note TEXT,
    processing_time_note_ru TEXT,
    stay_period_note TEXT,
    stay_period_note_ru TEXT,
    renewal_note TEXT,
    renewal_note_ru TEXT,
    tax_warning TEXT,
    tax_warning_ru TEXT,
    legal_warning TEXT,
    legal_warning_ru TEXT,
    allows_work TEXT NOT NULL DEFAULT 'unknown',
    allows_family TEXT NOT NULL DEFAULT 'unknown',
    leads_to_pr TEXT NOT NULL DEFAULT 'unknown',
    leads_to_citizenship TEXT NOT NULL DEFAULT 'unknown',
    requires_income_proof TEXT NOT NULL DEFAULT 'unknown',
    requires_local_address TEXT NOT NULL DEFAULT 'unknown',
    requires_criminal_record_check TEXT NOT NULL DEFAULT 'unknown',
    status TEXT NOT NULL DEFAULT 'draft',
    legal_status TEXT NOT NULL DEFAULT 'unknown',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS route_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    route_id UUID NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    name_ru TEXT,
    is_mandatory BOOLEAN NOT NULL DEFAULT TRUE,
    note TEXT,
    note_ru TEXT,
    display_order INT NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS route_sources (
    route_id UUID NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    PRIMARY KEY (route_id, source_id)
);

CREATE TABLE IF NOT EXISTS route_evidence (
    route_id UUID NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
    evidence_item_id UUID NOT NULL REFERENCES evidence_items(id) ON DELETE CASCADE,
    PRIMARY KEY (route_id, evidence_item_id)
);

ALTER TABLE routes
    DROP CONSTRAINT IF EXISTS routes_country_slug_unique;

ALTER TABLE routes
    ADD CONSTRAINT routes_country_slug_unique UNIQUE (country_id, slug);

ALTER TABLE routes
    DROP CONSTRAINT IF EXISTS routes_route_type_check;

ALTER TABLE routes
    ADD CONSTRAINT routes_route_type_check CHECK (
        route_type IN (
            'temporary_residence',
            'permanent_residence',
            'citizenship',
            'digital_nomad',
            'work',
            'business',
            'study',
            'investment'
        )
    );

ALTER TABLE routes
    DROP CONSTRAINT IF EXISTS routes_status_check;

ALTER TABLE routes
    ADD CONSTRAINT routes_status_check CHECK (
        status IN ('draft', 'review', 'published', 'archived', 'rejected')
    );

ALTER TABLE routes
    DROP CONSTRAINT IF EXISTS routes_legal_status_check;

ALTER TABLE routes
    ADD CONSTRAINT routes_legal_status_check CHECK (
        legal_status IN ('proposed', 'adopted', 'effective', 'expired', 'revoked', 'unknown')
    );

ALTER TABLE routes
    DROP CONSTRAINT IF EXISTS routes_allows_work_check;

ALTER TABLE routes
    ADD CONSTRAINT routes_allows_work_check CHECK (allows_work IN ('yes', 'no', 'unknown'));

ALTER TABLE routes
    DROP CONSTRAINT IF EXISTS routes_allows_family_check;

ALTER TABLE routes
    ADD CONSTRAINT routes_allows_family_check CHECK (allows_family IN ('yes', 'no', 'unknown'));

ALTER TABLE routes
    DROP CONSTRAINT IF EXISTS routes_leads_to_pr_check;

ALTER TABLE routes
    ADD CONSTRAINT routes_leads_to_pr_check CHECK (leads_to_pr IN ('yes', 'no', 'unknown'));

ALTER TABLE routes
    DROP CONSTRAINT IF EXISTS routes_leads_to_citizenship_check;

ALTER TABLE routes
    ADD CONSTRAINT routes_leads_to_citizenship_check CHECK (
        leads_to_citizenship IN ('yes', 'no', 'unknown')
    );

ALTER TABLE routes
    DROP CONSTRAINT IF EXISTS routes_requires_income_proof_check;

ALTER TABLE routes
    ADD CONSTRAINT routes_requires_income_proof_check CHECK (
        requires_income_proof IN ('yes', 'no', 'unknown')
    );

ALTER TABLE routes
    DROP CONSTRAINT IF EXISTS routes_requires_local_address_check;

ALTER TABLE routes
    ADD CONSTRAINT routes_requires_local_address_check CHECK (
        requires_local_address IN ('yes', 'no', 'unknown')
    );

ALTER TABLE routes
    DROP CONSTRAINT IF EXISTS routes_requires_criminal_record_check_check;

ALTER TABLE routes
    ADD CONSTRAINT routes_requires_criminal_record_check_check CHECK (
        requires_criminal_record_check IN ('yes', 'no', 'unknown')
    );

ALTER TABLE route_documents
    DROP CONSTRAINT IF EXISTS route_documents_route_name_unique;

ALTER TABLE route_documents
    ADD CONSTRAINT route_documents_route_name_unique UNIQUE (route_id, name);

CREATE INDEX IF NOT EXISTS idx_routes_country_status
    ON routes (country_id, status);

CREATE INDEX IF NOT EXISTS idx_routes_route_type
    ON routes (route_type);

CREATE INDEX IF NOT EXISTS idx_routes_status
    ON routes (status);

CREATE INDEX IF NOT EXISTS idx_routes_country_route_type
    ON routes (country_id, route_type);

CREATE INDEX IF NOT EXISTS idx_routes_published_country_type
    ON routes (country_id, route_type)
    WHERE status = 'published';

CREATE INDEX IF NOT EXISTS idx_route_documents_route_id
    ON route_documents (route_id);

CREATE INDEX IF NOT EXISTS idx_route_sources_source_id
    ON route_sources (source_id);

CREATE INDEX IF NOT EXISTS idx_route_evidence_evidence_item_id
    ON route_evidence (evidence_item_id);

WITH route_rows AS (
    SELECT *
    FROM (
        VALUES
            (
                'russia',
                'permanent-residence-status-review',
                'permanent_residence',
                'Permanent residence status review',
                'Проверка статуса постоянного проживания',
                'A source-backed route for reviewing long-term residence status under the foreign-citizen legal framework.',
                'Маршрут для проверки долгосрочного статуса проживания на базе закона о правовом положении иностранных граждан.',
                'Use this route to identify the official legal baseline, then verify the current procedure and document package before filing.',
                'Используйте маршрут для определения правовой основы, а затем отдельно проверяйте актуальную процедуру и пакет документов.',
                'The seed source does not establish a universal income threshold.',
                'Seed-источник не задает универсальный порог дохода.',
                'Official fee amounts must be checked in the current filing procedure.',
                'Размеры пошлин нужно проверять в актуальной процедуре подачи.',
                'Processing time depends on the current procedure and filing channel.',
                'Срок обработки зависит от текущей процедуры и канала подачи.',
                'Stay rights depend on the status granted and must be verified against the current law.',
                'Срок пребывания зависит от предоставленного статуса и требует проверки по действующему праву.',
                'Renewal or maintenance rules require current procedure review.',
                'Правила продления или поддержания статуса требуют проверки актуальной процедуры.',
                NULL,
                NULL,
                'Residence status does not by itself answer tax, banking, sanctions or employment-permission questions.',
                'Статус проживания сам по себе не отвечает на вопросы налогов, банков, санкций или разрешения на работу.',
                'unknown',
                'unknown',
                'yes',
                'unknown',
                'unknown',
                'unknown',
                'unknown',
                'published',
                'effective'
            ),
            (
                'russia',
                'citizenship-law-review',
                'citizenship',
                'Citizenship law review',
                'Проверка закона о гражданстве',
                'A long-term route for users who need to evaluate citizenship eligibility separately from residence planning.',
                'Долгосрочный маршрут для отдельной оценки гражданства после планирования проживания.',
                'Use this route as a legal review checklist rather than as an automatic eligibility decision.',
                'Используйте маршрут как чек-лист правовой проверки, а не как автоматическое решение о праве на гражданство.',
                'The route does not define a universal income requirement.',
                'Маршрут не задает универсальное требование к доходу.',
                'Fee details must be verified through the filing authority.',
                'Пошлины нужно проверять через орган подачи.',
                'Processing time is not derived from the seed source.',
                'Срок обработки не выводится из seed-источника.',
                'Citizenship is a status outcome, not a temporary stay permission.',
                'Гражданство является итоговым статусом, а не разрешением на временное пребывание.',
                'Repeat applications or additional filings need separate legal review.',
                'Повторные заявления или дополнительные подачи требуют отдельной правовой проверки.',
                NULL,
                NULL,
                'Citizenship eligibility must be reviewed case by case and should not be inferred from residence status alone.',
                'Право на гражданство нужно проверять индивидуально и не выводить только из факта проживания.',
                'unknown',
                'unknown',
                'no',
                'yes',
                'unknown',
                'unknown',
                'unknown',
                'published',
                'effective'
            ),
            (
                'russia',
                'professional-income-tax-self-employment',
                'business',
                'Professional income tax self-employment route',
                'Маршрут самозанятости через налог на профессиональный доход',
                'A business and tax-compliance route anchored in the official professional income tax portal.',
                'Маршрут для бизнес- и налоговой проверки на базе официального портала налога на профессиональный доход.',
                'Use this route to separate tax registration research from immigration permission and residence status.',
                'Используйте маршрут, чтобы отделить налоговую регистрацию от миграционного разрешения и статуса проживания.',
                'Income category and eligibility require current tax review.',
                'Категория дохода и применимость требуют актуальной налоговой проверки.',
                'Tax and registration costs must be checked in the official portal.',
                'Налоговые и регистрационные расходы нужно проверять на официальном портале.',
                'Processing depends on the digital registration channel.',
                'Срок зависит от цифрового канала регистрации.',
                'This route is not a residence permission.',
                'Этот маршрут не является разрешением на проживание.',
                'Ongoing eligibility must be monitored under tax rules.',
                'Продолжение применения режима нужно отслеживать по налоговым правилам.',
                'Tax registration does not replace immigration, banking or employment-permission review.',
                'Налоговая регистрация не заменяет миграционную, банковскую или трудовую проверку.',
                'Professional income tax status does not by itself create residence or citizenship rights.',
                'Статус НПД сам по себе не создает права на проживание или гражданство.',
                'yes',
                'unknown',
                'no',
                'no',
                'unknown',
                'unknown',
                'unknown',
                'published',
                'effective'
            ),
            (
                'uruguay',
                'temporary-legal-residence',
                'temporary_residence',
                'Temporary legal residence',
                'Временная легальная резиденция',
                'A first-step residence route anchored in Uruguay’s official temporary residence procedure.',
                'Первичный маршрут резиденции на базе официальной процедуры временного проживания в Уругвае.',
                'Use this route to review the official procedure and confirm the filing package before starting relocation.',
                'Используйте маршрут для проверки официальной процедуры и пакета подачи до релокации.',
                'The route does not establish a single income threshold.',
                'Маршрут не задает единый порог дохода.',
                'Procedure fees must be checked on the official procedure page.',
                'Пошлины нужно проверять на официальной странице процедуры.',
                'Processing time must be checked in the current procedure.',
                'Срок обработки нужно проверять в актуальной процедуре.',
                'Temporary stay length must be verified in the official procedure.',
                'Срок временного пребывания нужно проверять в официальной процедуре.',
                'Renewal conditions require current procedure review.',
                'Условия продления требуют проверки актуальной процедуры.',
                NULL,
                NULL,
                'Temporary residence should not be treated as a guaranteed permanent residence or citizenship outcome.',
                'Временную резиденцию нельзя считать гарантией ПМЖ или гражданства.',
                'unknown',
                'unknown',
                'yes',
                'unknown',
                'unknown',
                'unknown',
                'unknown',
                'published',
                'effective'
            ),
            (
                'uruguay',
                'migration-law-residence-baseline',
                'permanent_residence',
                'Migration law residence baseline',
                'Правовая основа резиденции по миграционному закону',
                'A residence route anchored in Uruguay’s migration law for long-term status analysis.',
                'Маршрут резиденции на базе миграционного закона Уругвая для долгосрочной оценки статуса.',
                'Use this route to connect procedure research with the statutory baseline before relying on long-term assumptions.',
                'Используйте маршрут, чтобы связать процедуру с правовой основой до долгосрочных выводов.',
                'The migration law source does not define a universal income figure in this seed.',
                'Seed-источник не задает универсальную сумму дохода.',
                'Fee details must be checked in the current procedure.',
                'Пошлины нужно проверять в актуальной процедуре.',
                'Processing time depends on the active procedure.',
                'Срок обработки зависит от действующей процедуры.',
                'Stay and status maintenance should be checked against current law and procedure.',
                'Срок и поддержание статуса нужно проверять по действующему праву и процедуре.',
                'Renewal or status maintenance requires legal review.',
                'Продление или поддержание статуса требует правовой проверки.',
                NULL,
                NULL,
                'The statutory baseline does not replace case-specific filing review.',
                'Правовая основа не заменяет индивидуальную проверку подачи.',
                'unknown',
                'unknown',
                'yes',
                'unknown',
                'unknown',
                'unknown',
                'unknown',
                'published',
                'effective'
            ),
            (
                'uruguay',
                'tax-administration-business-check',
                'business',
                'Tax administration business check',
                'Бизнес-проверка через налоговую администрацию',
                'A business and tax due-diligence route backed by Uruguay’s tax administration source.',
                'Маршрут бизнес- и налоговой проверки на базе источника налоговой администрации Уругвая.',
                'Use this route to verify tax registration and compliance questions separately from residence eligibility.',
                'Используйте маршрут для отдельной проверки налоговой регистрации и комплаенса, не смешивая их с резиденцией.',
                'Income proof depends on the tax or business scenario.',
                'Подтверждение дохода зависит от налогового или бизнес-сценария.',
                'Tax and filing costs must be checked in the current tax guidance.',
                'Налоговые и регистрационные расходы нужно проверять в актуальных налоговых материалах.',
                'Processing depends on the relevant registration channel.',
                'Срок зависит от соответствующего канала регистрации.',
                'This route is not a stay permission.',
                'Этот маршрут не является разрешением на пребывание.',
                'Ongoing obligations require current tax review.',
                'Текущие обязанности требуют актуальной налоговой проверки.',
                'Tax registration does not replace migration or work-authorization review.',
                'Налоговая регистрация не заменяет миграционную проверку или проверку права на работу.',
                'Business compliance should be reviewed separately from residence and citizenship expectations.',
                'Бизнес-комплаенс нужно проверять отдельно от ожиданий по резиденции и гражданству.',
                'unknown',
                'unknown',
                'no',
                'no',
                'unknown',
                'unknown',
                'unknown',
                'published',
                'effective'
            ),
            (
                'argentina',
                'temporary-residence-dnm',
                'temporary_residence',
                'Temporary residence through DNM',
                'Временное проживание через DNM',
                'A residence route backed by Argentina’s national migration authority source.',
                'Маршрут проживания на базе источника Национального управления миграции Аргентины.',
                'Use this route to verify the DNM procedure and documentation before assuming eligibility.',
                'Используйте маршрут для проверки процедуры DNM и документов до выводов о праве на подачу.',
                'The seed source does not define a universal income threshold.',
                'Seed-источник не задает универсальный порог дохода.',
                'Official fee details must be checked with the current DNM procedure.',
                'Пошлины нужно проверять в актуальной процедуре DNM.',
                'Processing time depends on the current DNM procedure.',
                'Срок обработки зависит от актуальной процедуры DNM.',
                'Stay period depends on the residence category granted.',
                'Срок пребывания зависит от предоставленной категории проживания.',
                'Renewal rules require current DNM review.',
                'Правила продления требуют актуальной проверки DNM.',
                NULL,
                NULL,
                'Temporary residence should not be treated as automatic citizenship eligibility.',
                'Временное проживание нельзя считать автоматическим правом на гражданство.',
                'unknown',
                'unknown',
                'yes',
                'unknown',
                'unknown',
                'unknown',
                'unknown',
                'published',
                'effective'
            ),
            (
                'argentina',
                'citizenship-two-year-residence-review',
                'citizenship',
                'Citizenship residence-period review',
                'Проверка срока проживания для гражданства',
                'A citizenship route backed by the official nationality and entry-requirements source.',
                'Маршрут гражданства на базе официального источника по гражданству и требованиям въезда.',
                'Use this route to check the residence-period signal and then verify the full court or authority process separately.',
                'Используйте маршрут для проверки сигнала о сроке проживания, а затем отдельно проверяйте полный процесс.',
                'The route does not establish a universal income requirement.',
                'Маршрут не задает универсальное требование к доходу.',
                'Fee and filing costs require current process review.',
                'Пошлины и расходы подачи требуют проверки актуального процесса.',
                'Processing time is not derived from the seed source.',
                'Срок обработки не выводится из seed-источника.',
                'Citizenship is a status outcome, not a temporary stay permission.',
                'Гражданство является итоговым статусом, а не разрешением на временное пребывание.',
                'Repeated or supplemented filings require legal review.',
                'Повторные или дополненные подачи требуют правовой проверки.',
                NULL,
                NULL,
                'A residence-period signal is not a complete citizenship eligibility decision.',
                'Сигнал о сроке проживания не является полным решением о праве на гражданство.',
                'unknown',
                'unknown',
                'no',
                'yes',
                'unknown',
                'unknown',
                'unknown',
                'published',
                'effective'
            ),
            (
                'argentina',
                'monotributo-self-employment',
                'business',
                'Monotributo self-employment route',
                'Маршрут самозанятости через monotributo',
                'A business and tax route backed by AFIP’s simplified tax regime source.',
                'Бизнес- и налоговый маршрут на базе источника AFIP по упрощенному режиму monotributo.',
                'Use this route to verify tax registration for small contributors separately from immigration status.',
                'Используйте маршрут для проверки налоговой регистрации малых налогоплательщиков отдельно от миграционного статуса.',
                'Category and income limits require current AFIP review.',
                'Категории и лимиты дохода требуют актуальной проверки AFIP.',
                'Tax amounts and registration costs must be checked in AFIP guidance.',
                'Налоговые суммы и расходы регистрации нужно проверять в материалах AFIP.',
                'Processing depends on AFIP registration flow.',
                'Срок зависит от процесса регистрации AFIP.',
                'This route is not a residence permission.',
                'Этот маршрут не является разрешением на проживание.',
                'Ongoing eligibility depends on current tax rules.',
                'Продолжение применения зависит от действующих налоговых правил.',
                'Tax enrollment does not replace immigration or work-authorization review.',
                'Налоговая регистрация не заменяет миграционную проверку или проверку права на работу.',
                'Monotributo status does not by itself create residence or citizenship rights.',
                'Статус monotributo сам по себе не создает права на проживание или гражданство.',
                'yes',
                'unknown',
                'no',
                'no',
                'yes',
                'unknown',
                'unknown',
                'published',
                'effective'
            )
    ) AS rows(
        country_slug,
        slug,
        route_type,
        title,
        title_ru,
        summary,
        summary_ru,
        eligibility_summary,
        eligibility_summary_ru,
        income_requirement_note,
        income_requirement_note_ru,
        fees_note,
        fees_note_ru,
        processing_time_note,
        processing_time_note_ru,
        stay_period_note,
        stay_period_note_ru,
        renewal_note,
        renewal_note_ru,
        tax_warning,
        tax_warning_ru,
        legal_warning,
        legal_warning_ru,
        allows_work,
        allows_family,
        leads_to_pr,
        leads_to_citizenship,
        requires_income_proof,
        requires_local_address,
        requires_criminal_record_check,
        status,
        legal_status
    )
)
INSERT INTO routes (
    country_id,
    slug,
    route_type,
    title,
    title_ru,
    summary,
    summary_ru,
    eligibility_summary,
    eligibility_summary_ru,
    income_requirement_note,
    income_requirement_note_ru,
    fees_note,
    fees_note_ru,
    processing_time_note,
    processing_time_note_ru,
    stay_period_note,
    stay_period_note_ru,
    renewal_note,
    renewal_note_ru,
    tax_warning,
    tax_warning_ru,
    legal_warning,
    legal_warning_ru,
    allows_work,
    allows_family,
    leads_to_pr,
    leads_to_citizenship,
    requires_income_proof,
    requires_local_address,
    requires_criminal_record_check,
    status,
    legal_status
)
SELECT
    c.id,
    rr.slug,
    rr.route_type,
    rr.title,
    rr.title_ru,
    rr.summary,
    rr.summary_ru,
    rr.eligibility_summary,
    rr.eligibility_summary_ru,
    rr.income_requirement_note,
    rr.income_requirement_note_ru,
    rr.fees_note,
    rr.fees_note_ru,
    rr.processing_time_note,
    rr.processing_time_note_ru,
    rr.stay_period_note,
    rr.stay_period_note_ru,
    rr.renewal_note,
    rr.renewal_note_ru,
    rr.tax_warning,
    rr.tax_warning_ru,
    rr.legal_warning,
    rr.legal_warning_ru,
    rr.allows_work,
    rr.allows_family,
    rr.leads_to_pr,
    rr.leads_to_citizenship,
    rr.requires_income_proof,
    rr.requires_local_address,
    rr.requires_criminal_record_check,
    rr.status,
    rr.legal_status
FROM route_rows rr
JOIN countries c ON c.slug = rr.country_slug
ON CONFLICT (country_id, slug) DO UPDATE
SET
    route_type = EXCLUDED.route_type,
    title = EXCLUDED.title,
    title_ru = EXCLUDED.title_ru,
    summary = EXCLUDED.summary,
    summary_ru = EXCLUDED.summary_ru,
    eligibility_summary = EXCLUDED.eligibility_summary,
    eligibility_summary_ru = EXCLUDED.eligibility_summary_ru,
    income_requirement_note = EXCLUDED.income_requirement_note,
    income_requirement_note_ru = EXCLUDED.income_requirement_note_ru,
    fees_note = EXCLUDED.fees_note,
    fees_note_ru = EXCLUDED.fees_note_ru,
    processing_time_note = EXCLUDED.processing_time_note,
    processing_time_note_ru = EXCLUDED.processing_time_note_ru,
    stay_period_note = EXCLUDED.stay_period_note,
    stay_period_note_ru = EXCLUDED.stay_period_note_ru,
    renewal_note = EXCLUDED.renewal_note,
    renewal_note_ru = EXCLUDED.renewal_note_ru,
    tax_warning = EXCLUDED.tax_warning,
    tax_warning_ru = EXCLUDED.tax_warning_ru,
    legal_warning = EXCLUDED.legal_warning,
    legal_warning_ru = EXCLUDED.legal_warning_ru,
    allows_work = EXCLUDED.allows_work,
    allows_family = EXCLUDED.allows_family,
    leads_to_pr = EXCLUDED.leads_to_pr,
    leads_to_citizenship = EXCLUDED.leads_to_citizenship,
    requires_income_proof = EXCLUDED.requires_income_proof,
    requires_local_address = EXCLUDED.requires_local_address,
    requires_criminal_record_check = EXCLUDED.requires_criminal_record_check,
    status = EXCLUDED.status,
    legal_status = EXCLUDED.legal_status,
    updated_at = NOW();

WITH document_rows AS (
    SELECT *
    FROM (
        VALUES
            ('russia', 'permanent-residence-status-review', 'Identity document', 'Документ, удостоверяющий личность', TRUE, 'Verify accepted identity formats in the current procedure.', 'Проверьте допустимые форматы документа в актуальной процедуре.', 1),
            ('russia', 'permanent-residence-status-review', 'Residence-status filing package', 'Пакет подачи по статусу проживания', TRUE, 'Use the official procedure to confirm the exact package.', 'Используйте официальную процедуру для проверки точного пакета.', 2),
            ('russia', 'citizenship-law-review', 'Identity document', 'Документ, удостоверяющий личность', TRUE, 'Confirm accepted identity records before filing.', 'Проверьте допустимые документы до подачи.', 1),
            ('russia', 'citizenship-law-review', 'Residence and nationality records', 'Документы проживания и гражданского статуса', TRUE, 'The full package must be reviewed case by case.', 'Полный пакет нужно проверять индивидуально.', 2),
            ('russia', 'professional-income-tax-self-employment', 'Taxpayer registration data', 'Данные налоговой регистрации', TRUE, 'Verify registration eligibility in the official tax portal.', 'Проверьте право на регистрацию на официальном налоговом портале.', 1),
            ('russia', 'professional-income-tax-self-employment', 'Activity and income records', 'Сведения о деятельности и доходах', FALSE, 'Category and income treatment require tax review.', 'Категория и учет доходов требуют налоговой проверки.', 2),
            ('uruguay', 'temporary-legal-residence', 'Identity document', 'Документ, удостоверяющий личность', TRUE, 'Confirm accepted identity formats in the current procedure.', 'Проверьте допустимые документы в актуальной процедуре.', 1),
            ('uruguay', 'temporary-legal-residence', 'Temporary residence application package', 'Пакет заявления на временную резиденцию', TRUE, 'Use the procedure page for the current filing package.', 'Используйте страницу процедуры для актуального пакета подачи.', 2),
            ('uruguay', 'migration-law-residence-baseline', 'Identity document', 'Документ, удостоверяющий личность', TRUE, 'Confirm identity and status records before filing.', 'Проверьте документы личности и статуса до подачи.', 1),
            ('uruguay', 'migration-law-residence-baseline', 'Residence basis records', 'Документы основания резиденции', TRUE, 'The statutory baseline must be paired with current procedure review.', 'Правовую основу нужно связать с актуальной процедурой.', 2),
            ('uruguay', 'tax-administration-business-check', 'Tax registration records', 'Документы налоговой регистрации', TRUE, 'Confirm registration requirements with the tax authority.', 'Проверьте требования регистрации в налоговом органе.', 1),
            ('uruguay', 'tax-administration-business-check', 'Business activity records', 'Сведения о предпринимательской деятельности', FALSE, 'The exact package depends on the tax or business scenario.', 'Точный пакет зависит от налогового или бизнес-сценария.', 2),
            ('argentina', 'temporary-residence-dnm', 'Identity document', 'Документ, удостоверяющий личность', TRUE, 'Confirm accepted identity formats in the DNM procedure.', 'Проверьте допустимые документы в процедуре DNM.', 1),
            ('argentina', 'temporary-residence-dnm', 'Residence application package', 'Пакет заявления на проживание', TRUE, 'DNM procedure should define the current package.', 'Актуальный пакет должна определять процедура DNM.', 2),
            ('argentina', 'citizenship-two-year-residence-review', 'Identity document', 'Документ, удостоверяющий личность', TRUE, 'Confirm accepted identity and civil records before filing.', 'Проверьте документы личности и гражданского состояния до подачи.', 1),
            ('argentina', 'citizenship-two-year-residence-review', 'Residence-period records', 'Документы срока проживания', TRUE, 'Residence-period evidence must be checked in the current process.', 'Подтверждение срока проживания нужно проверять в актуальном процессе.', 2),
            ('argentina', 'monotributo-self-employment', 'Tax identification records', 'Документы налоговой идентификации', TRUE, 'Verify CUIT or CUIL requirements through AFIP.', 'Проверьте требования CUIT или CUIL через AFIP.', 1),
            ('argentina', 'monotributo-self-employment', 'Activity and category records', 'Сведения о деятельности и категории', FALSE, 'Category eligibility must be checked in the current AFIP rules.', 'Право на категорию нужно проверять по действующим правилам AFIP.', 2)
    ) AS rows(
        country_slug,
        route_slug,
        name,
        name_ru,
        is_mandatory,
        note,
        note_ru,
        display_order
    )
)
INSERT INTO route_documents (
    route_id,
    name,
    name_ru,
    is_mandatory,
    note,
    note_ru,
    display_order
)
SELECT
    r.id,
    dr.name,
    dr.name_ru,
    dr.is_mandatory,
    dr.note,
    dr.note_ru,
    dr.display_order
FROM document_rows dr
JOIN countries c ON c.slug = dr.country_slug
JOIN routes r ON r.country_id = c.id AND r.slug = dr.route_slug
ON CONFLICT (route_id, name) DO UPDATE
SET
    name_ru = EXCLUDED.name_ru,
    is_mandatory = EXCLUDED.is_mandatory,
    note = EXCLUDED.note,
    note_ru = EXCLUDED.note_ru,
    display_order = EXCLUDED.display_order;

WITH source_rows AS (
    SELECT *
    FROM (
        VALUES
            ('russia', 'permanent-residence-status-review', 'https://www.consultant.ru/document/cons_doc_LAW_37868/'),
            ('russia', 'citizenship-law-review', 'https://www.consultant.ru/document/cons_doc_LAW_445998/'),
            ('russia', 'professional-income-tax-self-employment', 'https://npd.nalog.ru/'),
            ('russia', 'professional-income-tax-self-employment', 'https://www.nalog.gov.ru/eng/'),
            ('uruguay', 'temporary-legal-residence', 'https://www.gub.uy/tramites/residencia-legal-temporaria'),
            ('uruguay', 'temporary-legal-residence', 'https://www.gub.uy/ministerio-interior/comunicacion/publicaciones/types-of-residencies-in-uruguay'),
            ('uruguay', 'migration-law-residence-baseline', 'https://www.impo.com.uy/bases/leyes/18250-2008'),
            ('uruguay', 'migration-law-residence-baseline', 'https://www.gub.uy/tramites/residencia-legal-permanente'),
            ('uruguay', 'tax-administration-business-check', 'https://www.gub.uy/direccion-general-impositiva/'),
            ('uruguay', 'tax-administration-business-check', 'https://www.liveinuruguay.uy/tax-residence'),
            ('argentina', 'temporary-residence-dnm', 'https://www.argentina.gob.ar/interior/migraciones'),
            ('argentina', 'citizenship-two-year-residence-review', 'https://www.cancilleria.gob.ar/en/tourism-and-travel/visas'),
            ('argentina', 'monotributo-self-employment', 'https://www.afip.gob.ar/monotributo/')
    ) AS rows(country_slug, route_slug, source_url)
)
INSERT INTO route_sources (route_id, source_id)
SELECT
    r.id,
    s.id
FROM source_rows sr
JOIN countries c ON c.slug = sr.country_slug
JOIN routes r ON r.country_id = c.id AND r.slug = sr.route_slug
JOIN sources s ON s.country_id = c.id AND s.url = sr.source_url
ON CONFLICT (route_id, source_id) DO NOTHING;

WITH evidence_source_rows AS (
    SELECT *
    FROM (
        VALUES
            ('russia', 'permanent-residence-status-review', 'https://www.consultant.ru/document/cons_doc_LAW_37868/'),
            ('russia', 'citizenship-law-review', 'https://www.consultant.ru/document/cons_doc_LAW_445998/'),
            ('russia', 'professional-income-tax-self-employment', 'https://www.nalog.gov.ru/eng/'),
            ('uruguay', 'temporary-legal-residence', 'https://www.gub.uy/ministerio-interior/comunicacion/publicaciones/types-of-residencies-in-uruguay'),
            ('uruguay', 'migration-law-residence-baseline', 'https://www.gub.uy/tramites/residencia-legal-permanente'),
            ('uruguay', 'tax-administration-business-check', 'https://www.liveinuruguay.uy/tax-residence'),
            ('argentina', 'temporary-residence-dnm', 'https://www.argentina.gob.ar/interior/migraciones'),
            ('argentina', 'citizenship-two-year-residence-review', 'https://www.cancilleria.gob.ar/en/tourism-and-travel/visas'),
            ('argentina', 'monotributo-self-employment', 'https://www.afip.gob.ar/monotributo/')
    ) AS rows(country_slug, route_slug, source_url)
),
ranked_evidence AS (
    SELECT
        r.id AS route_id,
        ei.id AS evidence_item_id,
        ROW_NUMBER() OVER (
            PARTITION BY r.id
            ORDER BY COALESCE(ei.retrieved_at, ei.created_at) DESC NULLS LAST, ei.id
        ) AS evidence_rank
    FROM evidence_source_rows esr
    JOIN countries c ON c.slug = esr.country_slug
    JOIN routes r ON r.country_id = c.id AND r.slug = esr.route_slug
    JOIN sources s ON s.country_id = c.id AND s.url = esr.source_url
    JOIN evidence_items ei ON ei.source_id = s.id AND ei.country_id = c.id
    WHERE ei.status = 'published'
)
INSERT INTO route_evidence (route_id, evidence_item_id)
SELECT
    route_id,
    evidence_item_id
FROM ranked_evidence
WHERE evidence_rank = 1
ON CONFLICT (route_id, evidence_item_id) DO NOTHING;
