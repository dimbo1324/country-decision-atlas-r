-- Migration 010: Adds Russian-language content translations.
UPDATE country_profiles cp
SET
    summary = CASE c.slug
        WHEN 'russia' THEN 'Россия является контекстом с высоким уровнем риска для сравнительного анализа, с существенной правовой, банковской, политической и мобильной неопределённостью.'
        WHEN 'uruguay' THEN 'Уругвай является кандидатом с ориентацией на стабильность для планирования места проживания и образа жизни, с важными компромиссами по стоимости жизни, бюрократии и банковскому обслуживанию.'
    END,
    residence_overview = CASE c.slug
        WHEN 'russia' THEN 'Вопросы проживания и легального пребывания требуют актуальной проверки документов и не должны выводиться из общих правил.'
        WHEN 'uruguay' THEN 'Планирование резидентства сравнительно понятно, однако готовность документов и актуальные проверки процедур остаются необходимыми.'
    END,
    citizenship_overview = CASE c.slug
        WHEN 'russia' THEN 'Долгосрочный статус и планирование гражданства крайне индивидуальны и чувствительны к изменениям правил.'
        WHEN 'uruguay' THEN 'Долгосрочное резидентство и гражданство могут быть реальными, однако сроки и правила непрерывности проживания требуют проверки.'
    END,
    tax_overview = CASE c.slug
        WHEN 'russia' THEN 'Налоговая нагрузка зависит от резидентства, источников дохода, валютных ограничений и договорного контекста.'
        WHEN 'uruguay' THEN 'Налоговый режим зависит от статуса резидентства, источника дохода и текущих профессиональных рекомендаций.'
    END,
    business_overview = CASE c.slug
        WHEN 'russia' THEN 'Предпринимательская деятельность сталкивается с ограничениями банковского доступа, платёжной инфраструктуры, санкций и комплаенса.'
        WHEN 'uruguay' THEN 'Малый бизнес и самозанятость возможны, однако требуют планирования банковского обслуживания и комплаенса.'
    END,
    quality_of_life_overview = CASE c.slug
        WHEN 'russia' THEN 'Качество жизни варьируется по регионам, однако институциональные и мобильные риски доминируют в модели принятия решений.'
        WHEN 'uruguay' THEN 'Качество жизни может быть высоким для пользователей, ориентированных на стабильность, тогда как стоимость жилья в Монтевидео может стать ограничением.'
    END,
    risk_overview = CASE c.slug
        WHEN 'russia' THEN 'Основные риски: административная непредсказуемость, геополитическая уязвимость, банковские ограничения и низкая персональная определённость.'
        WHEN 'uruguay' THEN 'Основные риски: стоимость жизни, административные задержки, ограничения рынка труда, жильё и банковские трудности.'
    END
FROM countries c
WHERE cp.country_id = c.id
  AND c.slug IN ('russia', 'uruguay');

UPDATE sources
SET title = CASE url
    WHEN 'https://evisa.kdmid.ru/' THEN 'МИД России: портал электронной визы'
    WHEN 'https://www.nalog.gov.ru/eng/' THEN 'ФНС России: официальный портал'
    WHEN 'https://www.cbr.ru/eng/' THEN 'Банк России: официальный портал'
    WHEN 'https://www.gosuslugi.ru/' THEN 'Портал государственных услуг России'
    WHEN 'https://data.worldbank.org/country/russian-federation' THEN 'Всемирный банк: данные по России'
    WHEN 'https://freedomhouse.org/country/russia/freedom-world/2026' THEN 'Freedom House: профиль страны Россия 2026'
    WHEN 'https://worldjusticeproject.org/rule-of-law-index/downloads/2025/WJPIndex2025.pdf' THEN 'World Justice Project: Индекс верховенства права 2025'
    WHEN 'https://archive.doingbusiness.org/en/data/exploreeconomies/russia' THEN 'Всемирный банк: архив Doing Business, Россия'
    WHEN 'https://www.consultant.ru/document/cons_doc_LAW_19671/' THEN 'КонсультантПлюс: Налоговый кодекс РФ'
    WHEN 'http://government.ru/en/' THEN 'Официальный сайт Правительства России'
    WHEN 'https://www.gub.uy/ministerio-interior/comunicacion/publicaciones/types-of-residencies-in-uruguay' THEN 'МВД Уругвая: типы резиденции'
    WHEN 'https://www.gub.uy/tramites/residencia-legal-permanente' THEN 'Уругвай: процедура постоянного легального резидентства'
    WHEN 'https://www.liveinuruguay.uy/tax-residence' THEN 'Uruguay XXI: обзор налогового резидентства'
    WHEN 'https://www.gub.uy/direccion-nacional-migracion/' THEN 'Национальная дирекция миграции Уругвая'
    WHEN 'https://www.bcu.gub.uy/' THEN 'Центральный банк Уругвая'
    WHEN 'https://www.gub.uy/ministerio-economia-finanzas/' THEN 'Министерство экономики и финансов Уругвая'
    WHEN 'https://data.worldbank.org/country/uruguay' THEN 'Всемирный банк: данные по Уругваю'
    WHEN 'https://www.worldbank.org/ext/en/country/uruguay' THEN 'Всемирный банк: обзор страны Уругвай'
    WHEN 'https://freedomhouse.org/country/uruguay/freedom-world/2024' THEN 'Freedom House: профиль страны Уругвай 2024'
    WHEN 'https://worldjusticeproject.org/rule-of-law-index/global/2025' THEN 'World Justice Project: Глобальный индекс верховенства права 2025'
    WHEN 'https://www.consultant.ru/document/cons_doc_LAW_37868/' THEN 'КонсультантПлюс: Закон о правовом положении иностранных граждан'
    WHEN 'https://www.consultant.ru/document/cons_doc_LAW_445998/' THEN 'КонсультантПлюс: Федеральный закон о гражданстве РФ'
    WHEN 'https://npd.nalog.ru/' THEN 'ФНС России: портал налога на профессиональный доход'
    WHEN 'https://www.nalog.gov.ru/rn77/taxation/taxes/ndfl/' THEN 'ФНС России: страница НДФЛ'
    WHEN 'https://www.cbr.ru/eng/psystem/' THEN 'Банк России: Национальная платёжная система'
    WHEN 'https://www.cbr.ru/eng/banking_sector/' THEN 'Банк России: банковский сектор'
    WHEN 'https://data.worldbank.org/indicator/NY.GDP.PCAP.CD?locations=RU' THEN 'Всемирный банк: ВВП на душу населения, Россия'
    WHEN 'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=RU' THEN 'Всемирный банк: инфляция, Россия'
    WHEN 'https://data.worldbank.org/indicator/PV.EST?locations=RU' THEN 'Всемирный банк: политическая стабильность, Россия'
    WHEN 'https://www.gosuslugi.ru/600100/1/form' THEN 'Госуслуги: форма подачи по вопросам проживания'
    WHEN 'https://www.gub.uy/tramites/residencia-legal-temporaria' THEN 'Уругвай: процедура временного легального резидентства'
    WHEN 'https://www.impo.com.uy/bases/leyes/18250-2008' THEN 'IMPO Уругвай: Закон о миграции 18250'
    WHEN 'https://www.gub.uy/direccion-general-impositiva/' THEN 'Налоговая дирекция Уругвая (DGI)'
    WHEN 'https://www.gub.uy/instituto-nacional-estadistica/' THEN 'Национальный статистический институт Уругвая (INE)'
    WHEN 'https://data.worldbank.org/indicator/NY.GDP.PCAP.CD?locations=UY' THEN 'Всемирный банк: ВВП на душу населения, Уругвай'
    WHEN 'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=UY' THEN 'Всемирный банк: инфляция, Уругвай'
    WHEN 'https://data.worldbank.org/indicator/PV.EST?locations=UY' THEN 'Всемирный банк: политическая стабильность, Уругвай'
    WHEN 'https://www.bcu.gub.uy/Servicios-Financieros-SSF/Paginas/Default.aspx' THEN 'Центральный банк Уругвая: надзор за финансовыми услугами'
    WHEN 'https://archive.doingbusiness.org/en/data/exploreeconomies/uruguay' THEN 'Всемирный банк: архив Doing Business, Уругвай'
    WHEN 'https://www.impo.com.uy/bases/constitucion/1967-1967' THEN 'IMPO Уругвай: Конституция'
    ELSE title
END
WHERE url IN (
    'https://evisa.kdmid.ru/',
    'https://www.nalog.gov.ru/eng/',
    'https://www.cbr.ru/eng/',
    'https://www.gosuslugi.ru/',
    'https://data.worldbank.org/country/russian-federation',
    'https://freedomhouse.org/country/russia/freedom-world/2026',
    'https://worldjusticeproject.org/rule-of-law-index/downloads/2025/WJPIndex2025.pdf',
    'https://archive.doingbusiness.org/en/data/exploreeconomies/russia',
    'https://www.consultant.ru/document/cons_doc_LAW_19671/',
    'http://government.ru/en/',
    'https://www.gub.uy/ministerio-interior/comunicacion/publicaciones/types-of-residencies-in-uruguay',
    'https://www.gub.uy/tramites/residencia-legal-permanente',
    'https://www.liveinuruguay.uy/tax-residence',
    'https://www.gub.uy/direccion-nacional-migracion/',
    'https://www.bcu.gub.uy/',
    'https://www.gub.uy/ministerio-economia-finanzas/',
    'https://data.worldbank.org/country/uruguay',
    'https://www.worldbank.org/ext/en/country/uruguay',
    'https://freedomhouse.org/country/uruguay/freedom-world/2024',
    'https://worldjusticeproject.org/rule-of-law-index/global/2025',
    'https://www.consultant.ru/document/cons_doc_LAW_37868/',
    'https://www.consultant.ru/document/cons_doc_LAW_445998/',
    'https://npd.nalog.ru/',
    'https://www.nalog.gov.ru/rn77/taxation/taxes/ndfl/',
    'https://www.cbr.ru/eng/psystem/',
    'https://www.cbr.ru/eng/banking_sector/',
    'https://data.worldbank.org/indicator/NY.GDP.PCAP.CD?locations=RU',
    'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=RU',
    'https://data.worldbank.org/indicator/PV.EST?locations=RU',
    'https://www.gosuslugi.ru/600100/1/form',
    'https://www.gub.uy/tramites/residencia-legal-temporaria',
    'https://www.impo.com.uy/bases/leyes/18250-2008',
    'https://www.gub.uy/direccion-general-impositiva/',
    'https://www.gub.uy/instituto-nacional-estadistica/',
    'https://data.worldbank.org/indicator/NY.GDP.PCAP.CD?locations=UY',
    'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=UY',
    'https://data.worldbank.org/indicator/PV.EST?locations=UY',
    'https://www.bcu.gub.uy/Servicios-Financieros-SSF/Paginas/Default.aspx',
    'https://archive.doingbusiness.org/en/data/exploreeconomies/uruguay',
    'https://www.impo.com.uy/bases/constitucion/1967-1967'
);

UPDATE sources
SET notes = CASE url
    WHEN 'https://evisa.kdmid.ru/' THEN 'Официальный визовый портал МИД используется как высококонфидентный миграционный источник.'
    WHEN 'https://www.nalog.gov.ru/eng/' THEN 'Официальный портал налогового органа используется для скрининга налогового контекста.'
    WHEN 'https://www.cbr.ru/eng/' THEN 'Официальный источник центрального банка для банковского и финансово-системного контекста.'
    WHEN 'https://www.gosuslugi.ru/' THEN 'Официальный портал государственных услуг; достоверность средняя для обезличенных решений.'
    WHEN 'https://data.worldbank.org/country/russian-federation' THEN 'Институциональный набор данных для макроэкономических и страновых скрининговых показателей.'
    WHEN 'https://freedomhouse.org/country/russia/freedom-world/2026' THEN 'Институциональный исследовательский источник для контекста политических прав и гражданских свобод.'
    WHEN 'https://worldjusticeproject.org/rule-of-law-index/downloads/2025/WJPIndex2025.pdf' THEN 'Институциональный набор данных верховенства права для сравнительного скрининга правовой стабильности.'
    WHEN 'https://archive.doingbusiness.org/en/data/exploreeconomies/russia' THEN 'Архивный набор данных деловой среды, используется осторожно для исторического контекста.'
    WHEN 'https://www.consultant.ru/document/cons_doc_LAW_19671/' THEN 'Правовой справочный источник для скрининга налогового кодекса, не заменяет юридическую консультацию.'
    WHEN 'http://government.ru/en/' THEN 'Официальный информационный портал правительства для институционального контекста.'
    WHEN 'https://www.gub.uy/ministerio-interior/comunicacion/publicaciones/types-of-residencies-in-uruguay' THEN 'Официальный миграционный источник для скрининга категорий резидентства.'
    WHEN 'https://www.gub.uy/tramites/residencia-legal-permanente' THEN 'Официальная процедурная страница для постоянного легального резидентства.'
    WHEN 'https://www.liveinuruguay.uy/tax-residence' THEN 'Государственный источник по продвижению инвестиций для скрининга налогового резидентства.'
    WHEN 'https://www.gub.uy/direccion-nacional-migracion/' THEN 'Официальный портал миграционного органа.'
    WHEN 'https://www.bcu.gub.uy/' THEN 'Официальный источник для финансово-системного и банковского контекста.'
    WHEN 'https://www.gub.uy/ministerio-economia-finanzas/' THEN 'Официальный источник для экономического и налогово-политического контекста.'
    WHEN 'https://data.worldbank.org/country/uruguay' THEN 'Институциональный набор данных для макроэкономических и страновых скрининговых показателей.'
    WHEN 'https://www.worldbank.org/ext/en/country/uruguay' THEN 'Институциональный обзор страны для экономического и контекста развития.'
    WHEN 'https://freedomhouse.org/country/uruguay/freedom-world/2024' THEN 'Институциональный исследовательский источник для контекста политических прав и гражданских свобод.'
    WHEN 'https://worldjusticeproject.org/rule-of-law-index/global/2025' THEN 'Институциональный набор данных верховенства права для сравнительного скрининга правовой стабильности.'
    WHEN 'https://www.consultant.ru/document/cons_doc_LAW_37868/' THEN 'Основной правовой источник для проверки статуса иностранных граждан в России и требований к проживанию.'
    WHEN 'https://www.consultant.ru/document/cons_doc_LAW_445998/' THEN 'Основной правовой источник для путей натурализации и правил статуса гражданства.'
    WHEN 'https://npd.nalog.ru/' THEN 'Официальный портал ФНС для режима налога на профессиональный доход.'
    WHEN 'https://www.nalog.gov.ru/rn77/taxation/taxes/ndfl/' THEN 'Официальный справочный материал ФНС по налогу на доходы физических лиц.'
    WHEN 'https://www.cbr.ru/eng/psystem/' THEN 'Официальный справочный материал центрального банка по надзору за платёжной системой.'
    WHEN 'https://www.cbr.ru/eng/banking_sector/' THEN 'Официальный справочный материал центрального банка по надзору за банковским сектором.'
    WHEN 'https://data.worldbank.org/indicator/NY.GDP.PCAP.CD?locations=RU' THEN 'Страновой показатель Всемирного банка по ВВП на душу населения.'
    WHEN 'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=RU' THEN 'Страновой показатель Всемирного банка по инфляции потребительских цен.'
    WHEN 'https://data.worldbank.org/indicator/PV.EST?locations=RU' THEN 'Страновой показатель управления Всемирного банка по политической стабильности.'
    WHEN 'https://www.gosuslugi.ru/600100/1/form' THEN 'Официальная точка входа государственных услуг для процедуры, связанной с проживанием.'
    WHEN 'https://www.gub.uy/tramites/residencia-legal-temporaria' THEN 'Официальная государственная процедурная страница временного легального резидентства.'
    WHEN 'https://www.impo.com.uy/bases/leyes/18250-2008' THEN 'Официальный текст миграционного закона Уругвая.'
    WHEN 'https://www.gub.uy/direccion-general-impositiva/' THEN 'Официальный источник налогового органа для налогового администрирования и руководства.'
    WHEN 'https://www.gub.uy/instituto-nacional-estadistica/' THEN 'Официальный источник национальной статистики для демографического и экономического контекста.'
    WHEN 'https://data.worldbank.org/indicator/NY.GDP.PCAP.CD?locations=UY' THEN 'Страновой показатель Всемирного банка по ВВП на душу населения.'
    WHEN 'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=UY' THEN 'Страновой показатель Всемирного банка по инфляции потребительских цен.'
    WHEN 'https://data.worldbank.org/indicator/PV.EST?locations=UY' THEN 'Страновой показатель управления Всемирного банка по политической стабильности.'
    WHEN 'https://www.bcu.gub.uy/Servicios-Financieros-SSF/Paginas/Default.aspx' THEN 'Официальный надзорный источник для регулируемых финансовых услуг.'
    WHEN 'https://archive.doingbusiness.org/en/data/exploreeconomies/uruguay' THEN 'Архивный набор данных Всемирного банка по регулированию бизнеса в Уругвае.'
    WHEN 'https://www.impo.com.uy/bases/constitucion/1967-1967' THEN 'Официальный конституционный текст для контекста правовой стабильности.'
    ELSE notes
END
WHERE url IN (
    'https://evisa.kdmid.ru/',
    'https://www.nalog.gov.ru/eng/',
    'https://www.cbr.ru/eng/',
    'https://www.gosuslugi.ru/',
    'https://data.worldbank.org/country/russian-federation',
    'https://freedomhouse.org/country/russia/freedom-world/2026',
    'https://worldjusticeproject.org/rule-of-law-index/downloads/2025/WJPIndex2025.pdf',
    'https://archive.doingbusiness.org/en/data/exploreeconomies/russia',
    'https://www.consultant.ru/document/cons_doc_LAW_19671/',
    'http://government.ru/en/',
    'https://www.gub.uy/ministerio-interior/comunicacion/publicaciones/types-of-residencies-in-uruguay',
    'https://www.gub.uy/tramites/residencia-legal-permanente',
    'https://www.liveinuruguay.uy/tax-residence',
    'https://www.gub.uy/direccion-nacional-migracion/',
    'https://www.bcu.gub.uy/',
    'https://www.gub.uy/ministerio-economia-finanzas/',
    'https://data.worldbank.org/country/uruguay',
    'https://www.worldbank.org/ext/en/country/uruguay',
    'https://freedomhouse.org/country/uruguay/freedom-world/2024',
    'https://worldjusticeproject.org/rule-of-law-index/global/2025',
    'https://www.consultant.ru/document/cons_doc_LAW_37868/',
    'https://www.consultant.ru/document/cons_doc_LAW_445998/',
    'https://npd.nalog.ru/',
    'https://www.nalog.gov.ru/rn77/taxation/taxes/ndfl/',
    'https://www.cbr.ru/eng/psystem/',
    'https://www.cbr.ru/eng/banking_sector/',
    'https://data.worldbank.org/indicator/NY.GDP.PCAP.CD?locations=RU',
    'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=RU',
    'https://data.worldbank.org/indicator/PV.EST?locations=RU',
    'https://www.gosuslugi.ru/600100/1/form',
    'https://www.gub.uy/tramites/residencia-legal-temporaria',
    'https://www.impo.com.uy/bases/leyes/18250-2008',
    'https://www.gub.uy/direccion-general-impositiva/',
    'https://www.gub.uy/instituto-nacional-estadistica/',
    'https://data.worldbank.org/indicator/NY.GDP.PCAP.CD?locations=UY',
    'https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=UY',
    'https://data.worldbank.org/indicator/PV.EST?locations=UY',
    'https://www.bcu.gub.uy/Servicios-Financieros-SSF/Paginas/Default.aspx',
    'https://archive.doingbusiness.org/en/data/exploreeconomies/uruguay',
    'https://www.impo.com.uy/bases/constitucion/1967-1967'
);

UPDATE evidence_items
SET
    title = CASE title
        WHEN 'Russia foreign citizen law baseline' THEN 'Россия: Закон о статусе иностранных граждан — базовый источник'
        WHEN 'Russia residence process public-services touchpoint' THEN 'Россия: Госуслуги — административная процедура проживания'
        WHEN 'Russia electronic visa source' THEN 'Россия: Электронная виза МИД'
        WHEN 'Russia citizenship law baseline' THEN 'Россия: Закон о гражданстве — базовый источник'
        WHEN 'Russia residence-to-status dependency' THEN 'Россия: Зависимость статуса от проживания'
        WHEN 'Russia long-term risk context' THEN 'Россия: Контекст долгосрочного риска'
        WHEN 'Russia self-employed tax portal evidence' THEN 'Россия: Портал НПД ФНС'
        WHEN 'Russia personal income tax evidence' THEN 'Россия: НДФЛ — официальный источник ФНС'
        WHEN 'Russia banking context for freelancers' THEN 'Россия: Банковский контекст для фрилансеров'
        WHEN 'Russia payment-system evidence' THEN 'Россия: Платёжная система Банка России'
        WHEN 'Russia banking-sector evidence' THEN 'Россия: Банковский сектор'
        WHEN 'Russia financial administration evidence' THEN 'Россия: Финансовое администрирование'
        WHEN 'Russia political stability dataset evidence' THEN 'Россия: Показатель политической стабильности (Всемирный банк)'
        WHEN 'Russia Freedom House evidence' THEN 'Россия: Данные Freedom House'
        WHEN 'Russia rule-of-law evidence' THEN 'Россия: Индекс верховенства права WJP'
        WHEN 'Uruguay temporary residence procedure evidence' THEN 'Уругвай: Процедура временной резиденции'
        WHEN 'Uruguay permanent residence procedure evidence' THEN 'Уругвай: Процедура постоянной резиденции'
        WHEN 'Uruguay migration authority evidence' THEN 'Уругвай: Национальная дирекция миграции'
        WHEN 'Uruguay migration law evidence' THEN 'Уругвай: Миграционный закон 18250'
        WHEN 'Uruguay residence-type overview evidence' THEN 'Уругвай: Обзор типов резиденции'
        WHEN 'Uruguay constitutional context evidence' THEN 'Уругвай: Конституционный контекст'
        WHEN 'Uruguay tax authority evidence' THEN 'Уругвай: Налоговый орган (DGI)'
        WHEN 'Uruguay economy ministry evidence' THEN 'Уругвай: Министерство экономики и финансов'
        WHEN 'Uruguay inflation dataset evidence' THEN 'Уругвай: Показатель инфляции (Всемирный банк)'
        WHEN 'Uruguay financial supervisor evidence' THEN 'Уругвай: Надзор за финансовыми услугами ЦБ'
        WHEN 'Uruguay central bank evidence' THEN 'Уругвай: Центральный банк'
        WHEN 'Uruguay business-regulation archive evidence' THEN 'Уругвай: Архив данных по регулированию бизнеса'
        WHEN 'Uruguay constitution evidence' THEN 'Уругвай: Конституция'
        WHEN 'Uruguay rule-of-law index evidence' THEN 'Уругвай: Индекс верховенства права WJP'
        WHEN 'Uruguay freedom profile evidence' THEN 'Уругвай: Профиль Freedom House'
        ELSE title
    END,
    summary = CASE title
        WHEN 'Russia foreign citizen law baseline' THEN 'Закон о правовом положении иностранных граждан является первичным источником для оценки пребывания, проживания и статусных обязательств.'
        WHEN 'Russia residence process public-services touchpoint' THEN 'Форма госуслуг даёт практический процессуальный контекст для административных процедур, связанных с проживанием.'
        WHEN 'Russia electronic visa source' THEN 'Портал электронной визы МИД полезен для проверки краткосрочного въезда, но не заменяет консультацию по проживанию.'
        WHEN 'Russia citizenship law baseline' THEN 'Закон о гражданстве создаёт отдельную правовую основу для натурализации и гражданского статуса.'
        WHEN 'Russia residence-to-status dependency' THEN 'Правила проживания и статуса иностранных граждан сохраняют актуальность до рассмотрения любого пути к гражданству.'
        WHEN 'Russia long-term risk context' THEN 'Данные по политической стабильности добавляют риск-контекст для долгосрочных решений.'
        WHEN 'Russia self-employed tax portal evidence' THEN 'Портал ФНС предоставляет официальный источник для скрининга налога на профессиональный доход.'
        WHEN 'Russia personal income tax evidence' THEN 'Страница ФНС по НДФЛ актуальна для индивидуальной налоговой нагрузки.'
        WHEN 'Russia banking context for freelancers' THEN 'Контекст надзора за банковским сектором важен для фрилансеров и пользователей малого бизнеса.'
        WHEN 'Russia payment-system evidence' THEN 'Страница платёжной системы центрального банка поддерживает скрининг доступности карт, переводов и платежей.'
        WHEN 'Russia banking-sector evidence' THEN 'Источник по банковскому сектору поддерживает финансово-системную проверку.'
        WHEN 'Russia financial administration evidence' THEN 'Источник ФНС добавляет контекст государственного администрирования для финансовых и налоговых процессов.'
        WHEN 'Russia political stability dataset evidence' THEN 'Показатель политической стабильности Всемирного банка предоставляет внешние данные для оценки рисков.'
        WHEN 'Russia Freedom House evidence' THEN 'Профиль Freedom House добавляет внешний источник по гражданским и политическим правам.'
        WHEN 'Russia rule-of-law evidence' THEN 'Набор данных WJP добавляет контекст верховенства права для оценки правовой стабильности.'
        WHEN 'Uruguay temporary residence procedure evidence' THEN 'Официальная процедурная страница поддерживает первичный скрининг резидентства.'
        WHEN 'Uruguay permanent residence procedure evidence' THEN 'Процедура постоянной резиденции даёт связанный источник долгосрочного статуса.'
        WHEN 'Uruguay migration authority evidence' THEN 'Источник миграционного органа поддерживает маршрутизацию проверок, связанных с резидентством.'
        WHEN 'Uruguay migration law evidence' THEN 'Миграционный закон 18250 предоставляет законодательную основу для анализа миграции и резидентства.'
        WHEN 'Uruguay residence-type overview evidence' THEN 'Обзор Министерства внутренних дел помогает различать категории резидентства.'
        WHEN 'Uruguay constitutional context evidence' THEN 'Конституция предоставляет первичный правовой контекст для анализа долгосрочной стабильности.'
        WHEN 'Uruguay tax authority evidence' THEN 'Источник DGI является основным якорем налогового администрирования для скрининга пользователей.'
        WHEN 'Uruguay economy ministry evidence' THEN 'Источник Министерства экономики и финансов добавляет официальный фискальный контекст.'
        WHEN 'Uruguay inflation dataset evidence' THEN 'Показатель инфляции добавляет внешний контекст для планирования расходов и налогов.'
        WHEN 'Uruguay financial supervisor evidence' THEN 'Источник надзора центрального банка поддерживает финансово-сервисную проверку.'
        WHEN 'Uruguay central bank evidence' THEN 'Источник центрального банка закрепляет денежный и банковский контекст.'
        WHEN 'Uruguay business-regulation archive evidence' THEN 'Архив Doing Business предоставляет исторический контекст регулирования бизнеса.'
        WHEN 'Uruguay constitution evidence' THEN 'Конституция является первичным источником для контекста правовой стабильности.'
        WHEN 'Uruguay rule-of-law index evidence' THEN 'Глобальный индекс WJP добавляет сравнительный контекст верховенства права.'
        WHEN 'Uruguay freedom profile evidence' THEN 'Страновой профиль Freedom House добавляет внешний контекст политических прав.'
        ELSE summary
    END,
    claim = CASE title
        WHEN 'Russia foreign citizen law baseline' THEN 'Статус иностранных граждан в России регулируется специальным федеральным законом.'
        WHEN 'Russia residence process public-services touchpoint' THEN 'Планирование проживания включает проверку процедур через государственные услуги и правовые нормы.'
        WHEN 'Russia electronic visa source' THEN 'Проверку краткосрочного въезда следует отделять от анализа резидентства.'
        WHEN 'Russia citizenship law baseline' THEN 'Гражданство России регулируется специальным федеральным законом о гражданстве.'
        WHEN 'Russia residence-to-status dependency' THEN 'Скрининг долгосрочного статуса зависит как от правовых уровней проживания, так и гражданства.'
        WHEN 'Russia long-term risk context' THEN 'Долгосрочное планирование должно учитывать внешние данные по управлению и политическим рискам.'
        WHEN 'Russia self-employed tax portal evidence' THEN 'Налог на профессиональный доход имеет официальный цифровой информационный источник.'
        WHEN 'Russia personal income tax evidence' THEN 'НДФЛ остаётся отдельным скрининговым элементом, обеспеченным источниками.'
        WHEN 'Russia banking context for freelancers' THEN 'Планирование независимой работы также зависит от доступности банковских услуг.'
        WHEN 'Russia payment-system evidence' THEN 'Скрининг релокации должен включать проверку готовности платёжной системы.'
        WHEN 'Russia banking-sector evidence' THEN 'Надзор за банковским сектором актуален для ежедневного финансового доступа.'
        WHEN 'Russia financial administration evidence' THEN 'Налоговые и банковские процессы взаимодействуют при практическом планировании релокации.'
        WHEN 'Russia political stability dataset evidence' THEN 'Данные по политической стабильности актуальны для оценки безопасности и правовой стабильности.'
        WHEN 'Russia Freedom House evidence' THEN 'Внешние оценки свободы являются частью набора риск-доказательств.'
        WHEN 'Russia rule-of-law evidence' THEN 'Доказательства верховенства права дополняют данные политической стабильности.'
        WHEN 'Uruguay temporary residence procedure evidence' THEN 'Временная резиденция описана на официальной государственной процедурной странице.'
        WHEN 'Uruguay permanent residence procedure evidence' THEN 'Планирование резидентства может сравнивать источники по временным и постоянным процедурам.'
        WHEN 'Uruguay migration authority evidence' THEN 'Проверки процедур резидентства должны опираться на миграционный орган.'
        WHEN 'Uruguay migration law evidence' THEN 'Скрининг миграции Уругвая имеет официальный законодательный якорь.'
        WHEN 'Uruguay residence-type overview evidence' THEN 'Руководство по типам резидентства улучшает ориентированные на решения резюме.'
        WHEN 'Uruguay constitutional context evidence' THEN 'Скрининг правовой стабильности может ссылаться на конституционный текст.'
        WHEN 'Uruguay tax authority evidence' THEN 'Налоговое администрирование Уругвая имеет официальный источник.'
        WHEN 'Uruguay economy ministry evidence' THEN 'Фискальный контекст поддерживает скрининг налогов и стоимости жизни.'
        WHEN 'Uruguay inflation dataset evidence' THEN 'Данные по инфляции поддерживают скрининг стоимости жизни.'
        WHEN 'Uruguay financial supervisor evidence' THEN 'Данные финансового надзора актуальны для скрининга готовности счетов.'
        WHEN 'Uruguay central bank evidence' THEN 'Охват источниками центрального банка укрепляет контекст финансовой системы.'
        WHEN 'Uruguay business-regulation archive evidence' THEN 'Архивные данные по регулированию бизнеса остаются полезными как фоновый контекст.'
        WHEN 'Uruguay constitution evidence' THEN 'Анализ верховенства права должен включать первичный правовой текст.'
        WHEN 'Uruguay rule-of-law index evidence' THEN 'Скрининг правовой стабильности должен сочетать первичное право со сравнительными наборами данных.'
        WHEN 'Uruguay freedom profile evidence' THEN 'Оценки свободы дополняют доказательства правовой стабильности.'
        ELSE claim
    END,
    excerpt = CASE title
        WHEN 'Russia foreign citizen law baseline' THEN 'Первичный правовой источник для скрининга проживания и статусных требований.'
        WHEN 'Russia residence process public-services touchpoint' THEN 'Государственные услуги используются для скрининга административных процедур.'
        WHEN 'Russia electronic visa source' THEN 'Официальный источник электронной визы для контекстных доказательств въезда.'
        WHEN 'Russia citizenship law baseline' THEN 'Первичный источник по гражданству для скрининга долгосрочного статуса.'
        WHEN 'Russia residence-to-status dependency' THEN 'Первичный источник по проживанию как зависимость для скрининга гражданства.'
        WHEN 'Russia long-term risk context' THEN 'Показатель управления Всемирного банка используется для риск-контекста.'
        WHEN 'Russia self-employed tax portal evidence' THEN 'Официальный источник ФНС для скрининга самозанятости.'
        WHEN 'Russia personal income tax evidence' THEN 'Официальный налоговый источник ФНС для скрининга индивидуального налогообложения.'
        WHEN 'Russia banking context for freelancers' THEN 'Источник центрального банка для контекста финансовой операционности.'
        WHEN 'Russia payment-system evidence' THEN 'Источник центрального банка для доказательств платёжной системы.'
        WHEN 'Russia banking-sector evidence' THEN 'Источник центрального банка для доказательств банковского сектора.'
        WHEN 'Russia financial administration evidence' THEN 'Официальный налоговый источник для контекста финансового администрирования.'
        WHEN 'Russia political stability dataset evidence' THEN 'Государственный источник Всемирного банка для доказательств политических рисков.'
        WHEN 'Russia Freedom House evidence' THEN 'Источник Freedom House для контекста безопасности и свободы.'
        WHEN 'Russia rule-of-law evidence' THEN 'Источник WJP для доказательств правовой стабильности.'
        WHEN 'Uruguay temporary residence procedure evidence' THEN 'Официальный процедурный источник для скрининга релокации.'
        WHEN 'Uruguay permanent residence procedure evidence' THEN 'Официальный процедурный источник для контекста долгосрочного статуса.'
        WHEN 'Uruguay migration authority evidence' THEN 'Официальный источник миграционного органа для процессного контекста.'
        WHEN 'Uruguay migration law evidence' THEN 'Официальный правовой источник для доказательств миграционного закона.'
        WHEN 'Uruguay residence-type overview evidence' THEN 'Официальный обзорный источник для скрининга категорий.'
        WHEN 'Uruguay constitutional context evidence' THEN 'Официальный конституционный источник для правового контекста.'
        WHEN 'Uruguay tax authority evidence' THEN 'Официальный налоговый источник для скрининга резидентства и бизнеса.'
        WHEN 'Uruguay economy ministry evidence' THEN 'Официальный министерский источник для фискального контекста.'
        WHEN 'Uruguay inflation dataset evidence' THEN 'Источник Всемирного банка для ценового контекста.'
        WHEN 'Uruguay financial supervisor evidence' THEN 'Источник центрального банка для банковских доказательств.'
        WHEN 'Uruguay central bank evidence' THEN 'Источник центрального банка для институциональных доказательств.'
        WHEN 'Uruguay business-regulation archive evidence' THEN 'Архивный источник Всемирного банка для деловых контекстуальных доказательств.'
        WHEN 'Uruguay constitution evidence' THEN 'Официальный конституционный источник для доказательств правовой стабильности.'
        WHEN 'Uruguay rule-of-law index evidence' THEN 'Источник WJP для сравнительных доказательств правовой стабильности.'
        WHEN 'Uruguay freedom profile evidence' THEN 'Источник Freedom House для риск-контекста.'
        ELSE excerpt
    END,
    quote = CASE title
        WHEN 'Russia foreign citizen law baseline' THEN 'Источник следует изучить перед принятием простого пути резидентства.'
        WHEN 'Russia residence process public-services touchpoint' THEN 'Процедурный уровень следует проверять по законодательной базе.'
        WHEN 'Russia electronic visa source' THEN 'Разрешение на въезд и статус резидентства являются отдельными уровнями скрининга.'
        WHEN 'Russia citizenship law baseline' THEN 'Анализ гражданства не должен выводиться только из оценки резидентства.'
        WHEN 'Russia residence-to-status dependency' THEN 'Долгосрочный путь начинается с отдельного уровня соблюдения требований проживания.'
        WHEN 'Russia long-term risk context' THEN 'Долгосрочный статус должен учитывать показатели рисков управления.'
        WHEN 'Russia self-employed tax portal evidence' THEN 'Соответствие требованиям и взаимодействие с налоговым резидентством всё равно требуют проверки.'
        WHEN 'Russia personal income tax evidence' THEN 'Личное налогообложение следует проверять наряду с любым специальным режимом.'
        WHEN 'Russia banking context for freelancers' THEN 'Налоговое планирование следует сочетать с проверкой банковской готовности.'
        WHEN 'Russia payment-system evidence' THEN 'Платёжная инфраструктура может влиять на практическую осуществимость релокации.'
        WHEN 'Russia banking-sector evidence' THEN 'Доступ к счетам и регулируемый банковский контекст следует проверять заблаговременно.'
        WHEN 'Russia financial administration evidence' THEN 'Финансовая готовность включает точки контакта с налоговым администрированием.'
        WHEN 'Russia political stability dataset evidence' THEN 'Внешние данные управления должны быть видны в риск-чувствительных решениях.'
        WHEN 'Russia Freedom House evidence' THEN 'Данные по правам и свободам должны учитываться в риск-предупреждениях.'
        WHEN 'Russia rule-of-law evidence' THEN 'Контекст верховенства права должен быть виден при долгосрочной оценке рисков.'
        WHEN 'Uruguay temporary residence procedure evidence' THEN 'Пользователи могут начать с конкретного государственного процедурного источника.'
        WHEN 'Uruguay permanent residence procedure evidence' THEN 'Временный и постоянный статус следует рассматривать отдельно.'
        WHEN 'Uruguay migration authority evidence' THEN 'Охват источниками на уровне органа улучшает прослеживаемость.'
        WHEN 'Uruguay migration law evidence' THEN 'Процедурные источники следует читать вместе с законодательством.'
        WHEN 'Uruguay residence-type overview evidence' THEN 'Категории резидентства не следует сводить к одному общему пути.'
        WHEN 'Uruguay constitutional context evidence' THEN 'Миграционный анализ выигрывает от более широкого источника правовой стабильности.'
        WHEN 'Uruguay tax authority evidence' THEN 'Налоговое планирование следует проверять по официальным материалам DGI.'
        WHEN 'Uruguay economy ministry evidence' THEN 'Налоговые и фискальные проверки должны использовать министерские источники там, где это применимо.'
        WHEN 'Uruguay inflation dataset evidence' THEN 'Планирование расходов должно включать подкреплённый данными контекст инфляции.'
        WHEN 'Uruguay financial supervisor evidence' THEN 'Банковская готовность должна включать проверки регулируемого сектора.'
        WHEN 'Uruguay central bank evidence' THEN 'Банковские проверки должны использовать семейство источников центрального банка.'
        WHEN 'Uruguay business-regulation archive evidence' THEN 'Скрининг создания бизнеса должен отличать архивный контекст наборов данных от текущей юридической консультации.'
        WHEN 'Uruguay constitution evidence' THEN 'Охват конституционными источниками поддерживает скрининг верховенства права.'
        WHEN 'Uruguay rule-of-law index evidence' THEN 'Сравнительные данные верховенства права дополняют первичный правовой текст.'
        WHEN 'Uruguay freedom profile evidence' THEN 'Источники прав и свобод должны быть видны при оценке рисков.'
        ELSE quote
    END
WHERE title IN (
    'Russia foreign citizen law baseline',
    'Russia residence process public-services touchpoint',
    'Russia electronic visa source',
    'Russia citizenship law baseline',
    'Russia residence-to-status dependency',
    'Russia long-term risk context',
    'Russia self-employed tax portal evidence',
    'Russia personal income tax evidence',
    'Russia banking context for freelancers',
    'Russia payment-system evidence',
    'Russia banking-sector evidence',
    'Russia financial administration evidence',
    'Russia political stability dataset evidence',
    'Russia Freedom House evidence',
    'Russia rule-of-law evidence',
    'Uruguay temporary residence procedure evidence',
    'Uruguay permanent residence procedure evidence',
    'Uruguay migration authority evidence',
    'Uruguay migration law evidence',
    'Uruguay residence-type overview evidence',
    'Uruguay constitutional context evidence',
    'Uruguay tax authority evidence',
    'Uruguay economy ministry evidence',
    'Uruguay inflation dataset evidence',
    'Uruguay financial supervisor evidence',
    'Uruguay central bank evidence',
    'Uruguay business-regulation archive evidence',
    'Uruguay constitution evidence',
    'Uruguay rule-of-law index evidence',
    'Uruguay freedom profile evidence'
);

UPDATE evidence_items
SET
    claim = CASE
        WHEN claim LIKE '% evidence claim A' THEN REPLACE(claim, ' evidence claim A', ' — доказательство А')
        WHEN claim LIKE '% evidence claim B' THEN REPLACE(claim, ' evidence claim B', ' — доказательство Б')
        ELSE claim
    END,
    excerpt = CASE excerpt
        WHEN 'Synthetic MVP excerpt A. Verify source before use.' THEN 'Синтетическое MVP-извлечение А. Перед использованием проверьте источник.'
        WHEN 'Synthetic MVP excerpt B. Not legal advice.' THEN 'Синтетическое MVP-извлечение Б. Не является юридической консультацией.'
        ELSE excerpt
    END
WHERE excerpt IN (
    'Synthetic MVP excerpt A. Verify source before use.',
    'Synthetic MVP excerpt B. Not legal advice.'
);

UPDATE user_stories
SET
    legal_path = CASE legal_path
        WHEN 'Residence planning' THEN 'Планирование резидентства'
        WHEN 'Self-employment setup' THEN 'Оформление самозанятости'
        WHEN 'Temporary stay planning' THEN 'Планирование временного пребывания'
        WHEN 'Family relocation planning' THEN 'Планирование семейной релокации'
        WHEN 'Residence planning with document preparation and professional review.' THEN 'Планирование резидентства с подготовкой документов и профессиональной проверкой.'
        WHEN 'Self-employment exploration with tax and banking review.' THEN 'Изучение самозанятости с налоговой и банковской проверкой.'
        WHEN 'Short-term stay used to test budget and housing assumptions.' THEN 'Краткосрочное пребывание для проверки бюджетных и жилищных предположений.'
        WHEN 'Long-term residence planning with staged document collection.' THEN 'Долгосрочное планирование резидентства с поэтапным сбором документов.'
        ELSE legal_path
    END,
    problems = CASE problems
        WHEN 'Budget planning and document timing were the main simulated problems.' THEN 'Планирование бюджета и сроки документов были основными смоделированными проблемами.'
        WHEN 'Banking assumptions were uncertain in the simulation.' THEN 'Банковские предположения были неопределёнными в симуляции.'
        WHEN 'City-level cost assumptions were hard to compare.' THEN 'Предположения о расходах на уровне города было сложно сравнивать.'
        WHEN 'School and family logistics needed more source depth.' THEN 'Логистика школы и семьи требовала более глубокой проработки источников.'
        WHEN 'Housing search, Spanish-language paperwork, and banking onboarding took longer than expected.' THEN 'Поиск жилья, испаноязычное оформление документов и открытие банковских счетов заняли больше времени, чем ожидалось.'
        WHEN 'Bank onboarding and tax-residence questions required local professional support.' THEN 'Открытие банковских счетов и вопросы налогового резидентства потребовали местной профессиональной поддержки.'
        WHEN 'Seasonal housing costs made the budget less predictable.' THEN 'Сезонные расходы на жильё сделали бюджет менее предсказуемым.'
        WHEN 'Document timelines and translation requirements created friction.' THEN 'Сроки оформления документов и требования к переводу создали дополнительные трудности.'
        ELSE problems
    END,
    positive_outcome = CASE positive_outcome
        WHEN 'The simulated user achieved a clearer decision path.' THEN 'Смоделированный пользователь получил более чёткий путь принятия решений.'
        WHEN 'The simulated user identified business setup questions early.' THEN 'Смоделированный пользователь выявил вопросы регистрации бизнеса на раннем этапе.'
        WHEN 'The simulated user built a clearer budget checklist.' THEN 'Смоделированный пользователь составил более чёткий бюджетный чеклист.'
        WHEN 'The simulated family prioritized stability signals.' THEN 'Смоделированная семья приоритизировала сигналы стабильности.'
        WHEN 'The family obtained a clearer residence plan and reduced political-risk exposure.' THEN 'Семья получила более чёткий план резидентства и снизила политические риски.'
        WHEN 'The user found a more stable operating base for client work.' THEN 'Пользователь нашёл более стабильную базу для работы с клиентами.'
        WHEN 'The user confirmed that Uruguay felt stable and administratively understandable.' THEN 'Пользователь подтвердил, что Уругвай воспринимается как стабильный и административно понятный.'
        WHEN 'The household created a realistic multi-year status plan.' THEN 'Семья создала реалистичный многолетний план получения статуса.'
        ELSE positive_outcome
    END,
    negative_outcome = CASE negative_outcome
        WHEN 'The process still required expert review.' THEN 'Процесс всё равно потребовал экспертной проверки.'
        WHEN 'Costs were higher than expected.' THEN 'Расходы оказались выше ожидаемых.'
        WHEN 'Legal path remained uncertain.' THEN 'Правовой путь остался неопределённым.'
        WHEN 'Timeline uncertainty remained.' THEN 'Неопределённость сроков сохранилась.'
        WHEN 'Costs were higher than the initial budget, especially housing and setup expenses.' THEN 'Расходы превысили начальный бюджет, особенно на жильё и оформление.'
        WHEN 'Setup was slower and more expensive than expected.' THEN 'Процесс занял больше времени и оказался дороже, чем ожидалось.'
        WHEN 'The country was not as low-cost as expected.' THEN 'Страна оказалась не такой дешёвой, как ожидалось.'
        WHEN 'Citizenship expectations had to be made more conservative.' THEN 'Ожидания относительно гражданства пришлось скорректировать в сторону консерватизма.'
        ELSE negative_outcome
    END,
    advice = CASE advice
        WHEN 'Validate every document requirement before travel.' THEN 'Проверяйте каждое документальное требование перед поездкой.'
        WHEN 'Separate residence, tax, and banking advice.' THEN 'Разделяйте консультации по резидентству, налогам и банковским вопросам.'
        WHEN 'Treat cost comparisons as city-specific.' THEN 'Рассматривайте сравнения расходов в контексте конкретного города.'
        WHEN 'Use the card as a question list for expert review.' THEN 'Используйте карточку как список вопросов для экспертной проверки.'
        WHEN 'Prepare documents before arrival and budget for slower administrative steps.' THEN 'Подготовьте документы до приезда и закладывайте в бюджет время на медленные административные процедуры.'
        WHEN 'Validate banking and tax assumptions before committing to the move.' THEN 'Проверьте банковские и налоговые предположения до принятия окончательного решения о переезде.'
        WHEN 'Test the city and season before treating Uruguay as a low-budget destination.' THEN 'Проверьте город и сезон, прежде чем считать Уругвай бюджетным направлением.'
        WHEN 'Separate residence planning from citizenship assumptions and verify every timeline.' THEN 'Разделите планирование резидентства и гражданства, и проверяйте каждый срок.'
        ELSE advice
    END,
    notes = CASE notes
        WHEN 'Synthetic example for MVP demonstration only.' THEN 'Синтетический пример только для MVP-демонстрации.'
        ELSE notes
    END
WHERE is_synthetic = TRUE;

UPDATE country_scores
SET
    score_label = CASE score_label
        WHEN 'Draft' THEN 'Черновик'
        WHEN 'MVP decision score' THEN 'MVP-оценка подбора'
        WHEN 'Source-aware MVP decision score' THEN 'MVP-оценка с учётом источников'
        WHEN 'Source-backed screening score' THEN 'Скрининговая оценка с источниками'
        ELSE score_label
    END,
    summary = CASE summary
        WHEN 'Placeholder score; not production guidance.' THEN 'Placeholder-оценка; не для продакшена.'
        WHEN 'Stored editor score for the MVP decision engine.' THEN 'Редакторская оценка для MVP-движка подбора.'
        WHEN 'Stored v0 score built from seven explainable criteria and linked source quality.' THEN 'Версия 0 оценки по семи критериям с учётом качества источников.'
        WHEN 'Source-backed screening highlights high procedural friction.' THEN 'Скрининг источниками указывает на высокую процедурную нагрузку.'
        WHEN 'Long-term planning needs separate legal and risk review.' THEN 'Долгосрочное планирование требует отдельной правовой и риск-проверки.'
        WHEN 'Cost screening is data-backed but city-sensitive.' THEN 'Скрининг расходов подкреплён данными, но чувствителен к уровню города.'
        WHEN 'Business route is source-backed but review-heavy.' THEN 'Бизнес-маршрут подкреплён источниками, но требует интенсивной проверки.'
        WHEN 'Risk datasets drive a cautious safety score.' THEN 'Наборы риск-данных определяют осторожную оценку безопасности.'
        WHEN 'Residence route has stronger public traceability.' THEN 'Путь к резидентству имеет более сильную публичную прослеживаемость.'
        WHEN 'Long-term status is comparatively traceable.' THEN 'Долгосрочный статус сравнительно прослеживаем.'
        WHEN 'Cost screen has solid dataset coverage.' THEN 'Скрининг расходов имеет надёжное покрытие наборами данных.'
        WHEN 'Business screening has multiple official anchors.' THEN 'Бизнес-скрининг имеет несколько официальных якорей.'
        WHEN 'Risk profile is supported by official and external sources.' THEN 'Риск-профиль поддержан официальными и внешними источниками.'
        ELSE summary
    END
WHERE score_label IN (
    'Draft',
    'MVP decision score',
    'Source-aware MVP decision score',
    'Source-backed screening score'
);

UPDATE user_story_documents
SET title = 'Синтетический чеклист документов для ' || REPLACE(
    REPLACE(
        REPLACE(
            REPLACE(
                REPLACE(scenario, 'relocation_residence', 'Релокация и ВНЖ'),
            'permanent_residence_citizenship', 'ПМЖ и гражданство'),
        'low_budget_living', 'Жизнь с ограниченным бюджетом'),
    'business_self_employment', 'Бизнес и самозанятость'),
'safety_political_risk', 'Безопасность и политический риск')
FROM user_stories us
WHERE user_story_documents.user_story_id = us.id
  AND us.is_synthetic = TRUE
  AND user_story_documents.title LIKE 'Synthetic document checklist for %';

UPDATE sources
SET notes = 'Демонстрационный источник MVP. Перед использованием в продакшене проверяйте первичные материалы.'
WHERE notes = 'MVP demonstration source. Verify against primary material before production use.'
  AND status != 'published';
