# Чек-лист задачи: Эпизод 5 — `feat/country-contribution-v1` (контрибуция стран)

Цель: открыть контент-ядро сообществу — пайплайн предложения и наполнения
стран под кураторством редактора, решить судьбу тестовых стран (RU/UY/AR).
Полная реализация по плану (`docs/_arch_/02_План/01_План_реализации.md`,
раздел «Эпизод 5»), миграция 050.

## 0. Развилки, решённые владельцем перед стартом

```text
[+] Сценарные скоринги страны (country_scores/country_score_breakdowns —
    5 сценариев × 7 критериев, объяснения+источники) сегодня не имеют вообще
    никакого API записи (только ручные SQL-миграции RU/UY/Argentina).
    Решение владельца: заполняет ТОЛЬКО куратор-редактор через новый
    editor-gated эндпоинт — не контрибутор.
[+] Значения CII-метрик страны (country_metric_values, 6 показателей) —
    тоже нет CRUD сегодня, но объём на порядок меньше. Решение владельца:
    заполняет контрибутор (часть наполнения по плану).
```

## 1. Архитектурные решения (зафиксированы здесь, не в коде — код без комментариев)

```text
[ ] countries.is_active переиспользуется как единственный переключатель
    видимости черновика-предложения (draft/review страна создаётся с
    is_active=FALSE — это автоматически скрывает её везде, где уже
    сегодня фильтруется `is_active = TRUE`, без правок в ~20 файлах).
    ВАЖНО: evaluate_country_onboarding() возвращает mvp_ready=False для
    is_active=FALSE — поэтому на публикации is_active флипается в TRUE
    ДО финального прогона гейта (гейт должен видеть страну как активную).
[ ] countries.is_demo — НОВЫЙ отдельный флаг, TRUE только у russia/uruguay/
    argentina. НЕ переиспользует is_active (демо-страны обязаны оставаться
    is_active=TRUE, иначе они провалят onboarding-гейт как «первые пациенты»
    пайплайна — прямое требование плана). Скрытие демо со всех публичных
    поверхностей реализуется явным добавлением `AND is_demo = FALSE` в
    публичные read-репозитории (список ниже, п.8) — точечно, не через
    is_active.
[ ] Контрибуторские правки (card/sources/evidence/legal-signals/timeline
    events/CII-значения) идут через НОВЫЕ выделенные `/me/country-
    proposals/{id}/...` эндпоинты нового пакета `country_contribution`,
    переиспользующие существующие сервисные функции admin_content.py
    (create_source/patch_source/create_evidence_item/patch_evidence_item/
    create_legal_signal/patch_legal_signal) через обёртку с проверкой
    владения (proposer_user_id == current_user AND статус='draft') и
    принудительным status='draft' на входе (контрибутор никогда не может
    сам выставить published/review — это ломало бы кураторский гейт).
    НЕ трогаем /admin/sources и т.п. — существующее поведение редактора
    не меняется.
[ ] country_cards (карточка) и country_metric_values (CII) не имеют вообще
    никакого API записи сегодня — новые repository/service функции
    добавляются в country_contribution (card) и admin_content.py
    (create_country_profile, естественное соседство с patch_country_profile,
    но НЕ подключается в admin.py — только через новый эндпоинт контрибуции,
    чтобы не расширять публичный контракт /admin без необходимости).
[ ] Публикация страны — жёсткий гейт на уровне сервиса (инвариант 25):
    curator_user_id IS NOT NULL И свежий evaluate_country_onboarding(...)
    .mvp_ready is True, иначе 409/422. Не полагаемся только на readiness_
    snapshot (может быть устаревшим) — на publish гейт прогоняется заново.
[ ] Фича-флаг country_contribution_enabled: default_enabled=TRUE, по
    прецеденту ВСЕХ существующих флагов проекта (флаг ≠ право; реальный
    доступ контролирует invite-only грант contributor.countries).
[ ] Никаких новых methodology_parameters — валидация полей (justification
    непустая и т.п.) — обычные Pydantic/CHECK-ограничения, не тюнингуемые
    пороги (не тот случай, что author_metrics).
```

## 2. Миграция 050

```text
[ ] ALTER TABLE countries ADD COLUMN is_demo BOOLEAN NOT NULL DEFAULT FALSE
[ ] CREATE TABLE country_proposals (id, proposer_user_id, country_id UNIQUE,
    slug UNIQUE, name_en, name_ru, iso2, iso3, justification, status
    (стандартный CHECK draft/review/published/archived/rejected),
    curator_user_id, readiness_snapshot JSONB, moderated_by, moderated_at,
    moderation_reason, created_at/updated_at/published_at) + индексы
    (status, proposer, curator) + updated_at trigger
[ ] UPDATE countries SET is_demo = TRUE WHERE slug IN
    ('russia','uruguay','argentina') — БЕЗ удаления/деактивации
[ ] feature_flags + feature_access_rules: country_contribution_enabled
[ ] sqlfluff-чисто, идемпотентно (IF NOT EXISTS/ON CONFLICT)
```

## 3. Репозитории (`repositories/country_contribution/`)

```text
[ ] proposals.py — CRUD country_proposals, создание countries-строки
    (is_active=FALSE, is_demo=FALSE) + translations(ru) в одной транзакции,
    флип is_active при публикации
[ ] content.py — create_country_card (country_cards), create/list
    legal_signal_events (timeline), upsert country_metric_values (CII)
[ ] scores.py — upsert country_scores + country_score_breakdowns
    (curator only)
[ ] __init__.py re-export
```

## 4. Сервисы (`services/country_contribution/`)

```text
[ ] helpers.py — FEATURE_KEY, ensure_feature_enabled, get_owner_proposal_
    or_404, get_proposal_or_404, _require_draft_editable, response shaping
    (_mine/_admin/_public), _audit
[ ] proposals.py — create/patch/list/get (contributor), submit_for_review
[ ] content.py — контрибуторские card/sources/evidence/legal-signals/
    timeline-events/CII-values (ownership-gated обёртки над admin_content +
    новыми repo-функциями)
[ ] curation.py — list/get для куратора, assign_curator (self-assign,
    editor+), run_readiness_check (evaluate_country_onboarding), publish
    (жёсткий гейт), reject, request_changes
[ ] scores.py — curator-only upsert сценарного скоринга (7 критериев,
    вес суммируется в 1, score_label через существующий services/
    score_labels.py, overall confidence = минимум из breakdown-конфиденсов)
[ ] __init__.py re-export
```

## 5. API

```text
[ ] api/v1/country_contribution.py — /me/country-proposals (CRUD,
    submit) + /me/country-proposals/{id}/card|sources|evidence-items|
    legal-signals|timeline-events|metric-values, require_capability
    (CONTRIBUTOR_COUNTRIES)
[ ] api/v1/admin_country_contribution.py — /admin/country-proposals
    (list/get, require_editor), assign-curator, readiness-check,
    scenario-scores, publish, reject, request-changes
[ ] Атрибуция контрибутора на публичной странице страны («данные при
    участии …») — минимальное поле в существующем country read-model
```

## 6. Data quality

```text
[ ] services/data_quality/country_contribution_checks.py +
    repositories/data_quality/country_contribution.py:
    - published-предложение без curator_user_id (critical, инвариант 25)
    - published-предложение, чья countries.is_active = FALSE (critical,
      рассинхрон)
    - curator_user_id указывает на пользователя не editor/admin/owner (high)
[ ] Подключение в services/data_quality/report.py (_append_*_checks)
```

## 7. Демо-набор и публичные поверхности

```text
[ ] Аудит всех публичных read-путей на `FROM countries` (countries.py/
    country_read_model.py, decision_engine.py, search, home.py,
    country_pairs.py, cii.py, country_drift.py, platform_metrics.py,
    trust.py, legal_signal_events.py) — добавить `AND is_demo = FALSE`
    туда, где сегодня уже фильтруется is_active = TRUE для публичного
    ответа; admin/DQ/onboarding-пути не трогать (должны видеть всё)
[ ] Тест-инвариант: ни один публичный эндпоинт не возвращает demo-страну
```

## 8. Фикстуры и restore-инструмент

```text
[ ] scripts/dev_tools/export_demo_countries.py — дамп is_demo=TRUE стран +
    связанных таблиц (country_cards, country_profiles, sources,
    evidence_items, legal_signals, legal_signal_events, country_metric_
    values, country_cii_scores, country_scores+breakdowns, routes+
    children+checklist_items, country_pair_compatibility) в
    database/fixtures/demo_countries/*.json
[ ] scripts/dev_tools/restore_demo_countries.py — идемпотентное
    восстановление (upsert по natural key), --dry-run, сводка
[ ] Регистрация restore-скрипта в dev_tools_scripts_runner.py (ScriptInfo)
[ ] Прогон экспорта против реальной БД (Docker) для генерации фикстур
```

## 9. Контракты

```text
[ ] contracts/openapi.yaml — новые схемы/эндпоинты
[ ] pnpm contracts:generate — commit обновлённого types.ts
```

## 10. Тесты (~50-70 с учётом расширенного объёма)

```text
[ ] Миграция: схема применяется, идемпотентна
[ ] Contributor: создание proposal (countries+translations+proposal
    транзакционно), scoping (нельзя писать в чужую/демо страну), lock
    после submit, PII/статус-инъекция невозможна (payload.status
    игнорируется)
[ ] Curator: self-assign, readiness-check зелёный/красный, publish без
    curator_user_id -> 409, publish с красным гейтом -> 422, publish
    флипает is_active, reject/request_changes
[ ] Scenario scores: 7 критериев, вес=1 валидация, score_label,
    confidence=min
[ ] DQ: 3 новые проверки (позитив/негатив)
[ ] Demo conservation: is_demo=TRUE на RU/UY/AR не удаляет данные;
    invisibility-тест по каждой публичной поверхности из §7
[ ] restore_demo_countries.py: идемпотентность, восстановленный набор
    проходит onboarding-гейт
[ ] Acceptance E2E: proposal -> наполнение (card/sources/evidence/signals/
    timeline/CII) -> curator scenario scores -> readiness-check ->
    publish -> появляется в /countries, /decision/run, /search
[ ] Rights-инвариант: deny-by-default на каждом новом роутере
```

## 11. Документация

```text
[ ] Статус-строка под Эпизодом 5 в 01_План_реализации.md
[ ] 02_Текущее_состояние_системы.md — карта доменов, инвентаризация п.6
```

## 12. Quality gate

```text
[ ] python -m pytest
[ ] python -m ruff check / format --check
[ ] python -m mypy apps packages scripts tests
[ ] python -m sqlfluff lint database --dialect postgres
[ ] pnpm contracts:generate (без диффа) / pnpm quality
[ ] python dev_tools_scripts_runner.py (полный гейт)
```

## 13. Завершение

```text
[ ] Чек-лист заполнен +/-
[ ] Финальный отчёт
[ ] Merge --ff-only в main и push — ТОЛЬКО после явного подтверждения
    владельца
```
