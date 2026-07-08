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
[+] countries.is_active переиспользуется как единственный переключатель
    видимости черновика-предложения (draft/review страна создаётся с
    is_active=FALSE — скрывает её везде, где уже фильтруется
    is_active = TRUE, без правок в ~20 файлах). На publish is_active
    флипается в TRUE ДО финального прогона онбординг-гейта (гейт требует
    активную страну), внутри одной транзакции.
[+] countries.is_demo — отдельный флаг, TRUE только у russia/uruguay/
    argentina. НЕ переиспользует is_active (демо обязаны остаться активными,
    иначе провалят онбординг-гейт как «первые пациенты» пайплайна). Скрытие
    демо со всех публичных поверхностей — явный `AND is_demo = FALSE` в
    публичных read-репозиториях; recompute/admin/DQ-пути НЕ трогаем (важное
    уточнение по ходу работы: часть репозиторных функций общая между
    публичным чтением и recompute-скриптом — is_demo добавлен точечно только
    в публичную ветку/роутер, не в шаред-функцию, где это ломало бы
    пересчёт для демо-стран — см. country_drift.py/platform_metrics.py).
[+] Контрибуторские правки (card/sources/evidence/legal-signals/timeline-
    events/CII-значения) идут через новые `/me/country-proposals/{id}/...`
    эндпоинты, переиспользующие services/admin_content.py через
    ownership-gated обёртку (proposer_user_id==current_user, статус=draft)
    с принудительным status=draft на входе. /admin/sources и т.п. не
    тронуты.
[+] country_cards (карточка) и country_metric_values (CII) не имели вообще
    никакого API записи — новые repo/service функции добавлены в
    country_contribution (не в admin_content.py/admin.py — чтобы не
    расширять публичный /admin контракт без необходимости).
[+] Публикация — жёсткий гейт на уровне сервиса (инвариант 25):
    curator_user_id IS NOT NULL И свежий evaluate_country_onboarding(...)
    .mvp_ready внутри одной транзакции с флипом is_active и записью
    readiness_snapshot.
[+] Фича-флаг country_contribution_enabled: default_enabled=TRUE, по
    прецеденту всех существующих флагов (флаг ≠ право; доступ — invite-only
    грант contributor.countries).
[+] Никаких новых methodology_parameters — обычные Pydantic/CHECK-
    ограничения.
```

## 2. Миграция 050

```text
[+] ALTER TABLE countries ADD COLUMN is_demo BOOLEAN NOT NULL DEFAULT FALSE
[+] CREATE TABLE country_proposals (id, proposer_user_id, country_id UNIQUE,
    slug UNIQUE, name_en, name_ru, iso2, iso3, justification, status
    (CHECK draft/review/published/archived/rejected), curator_user_id,
    readiness_snapshot JSONB, moderated_by, moderated_at, moderation_reason,
    timestamps) + индексы (status, proposer, curator) + updated_at trigger
[+] UPDATE countries SET is_demo = TRUE WHERE slug IN
    ('russia','uruguay','argentina') — без DELETE/деактивации
[+] feature_flags + feature_access_rules: country_contribution_enabled
[+] sqlfluff-чисто, идемпотентно (IF NOT EXISTS/ON CONFLICT); схема-тесты
    в tests/test_country_contribution_mig.py (7 тестов)
```

## 3. Репозитории (`repositories/country_contribution/`)

```text
[+] proposals.py, content.py, scores.py, __init__.py — как спланировано
```

## 4. Сервисы (`services/country_contribution/`)

```text
[+] helpers.py, proposals.py, content.py, curation.py, scores.py,
    __init__.py — как спланировано
```

## 5. API

```text
[+] api/v1/country_contribution.py — /me/country-proposals + вложенные
    card/sources/evidence-items/legal-signals/timeline-events/metric-values
[+] api/v1/admin_country_contribution.py — /admin/country-proposals +
    assign-curator/readiness-check/scenario-scores/publish/reject/
    request-changes/archive
[-] Атрибуция контрибутора на публичной странице страны («данные при
    участии …») — НЕ сделано в этом проходе: страница страны читает через
    services/country_read_model.py, которое не подключает
    country_proposals; минимальное добавление поля оставлено как открытый
    пункт (не блокирует остальной эпизод, публикация и гейт работают без
    него). Атрибуция сохраняется в БД (proposer_user_id на country_proposals
    остаётся после publish), но не выведена в публичный ответ API.
```

## 6. Data quality

```text
[+] services/data_quality/country_contribution_checks.py +
    repositories/data_quality/country_contribution.py — 3 проверки, все
    подключены в services/data_quality/report.py
```

## 7. Демо-набор и публичные поверхности

```text
[+] Аудит и правки: countries.py, decision_engine.py, cii.py,
    country_pairs.py, legal_signal_events.py, search_sources.py, trust.py —
    is_demo=FALSE добавлен напрямую в SQL. country_drift.py/
    platform_metrics.py — is_demo добавлен в SELECT, проверка на уровне
    роутера (эти repo-функции общие с recompute-скриптами, которые обязаны
    видеть демо-страны)
[+] 26 тестов на invisibility (SQL-текст + router-level), включая
    подтверждение, что recompute-пути (trust_runtime, platform_metrics_
    runtime, country_drift compute) по-прежнему видят демо-страны
```

## 8. Фикстуры и restore-инструмент

```text
[+] scripts/dev_tools/export_demo_countries.py — дамп 20 таблиц (countries,
    translations, country_profiles, country_cards, sources, evidence_items,
    legal_signals, legal_signal_events, country_metric_values,
    country_cii_scores, country_scores+breakdowns, routes+documents+
    sources+evidence+checklist_items, country_pair_compatibility+sources+
    evidence) через общий TABLE_SPECS-реестр
[+] scripts/dev_tools/restore_demo_countries.py — общий идемпотентный
    upsert (динамические касты по information_schema.columns), --dry-run;
    5 юнит-тестов на сборку SQL и dry-run-семантику
[+] Регистрация в dev_tools_scripts_runner.py (ключ "7", ScriptInfo)
[-] Прогон экспорта против реальной БД (Docker) для генерации
    database/fixtures/demo_countries/*.json — НЕ ВЫПОЛНЕН. Docker Desktop
    в этой сессии не отвечал на команды (docker ps/start зависали без
    ошибки и без прогресса даже после ~20 минут ожидания и повторных
    попыток — вероятно, специфика окружения). Экспорт/restore-логика
    покрыта юнит-тестами с фейковым соединением, но НИ РАЗУ не прогонялась
    против настоящего Postgres. Каталог database/fixtures/demo_countries/
    пока пуст. Требуется отдельный проход: поднять docker-compose postgres,
    накатить миграции, выполнить
    `python dev_tools_scripts_runner.py restore-demo-countries` заменить на
    `python scripts/dev_tools/export_demo_countries.py` один раз на
    заполненной локальной БД, закоммитить получившиеся JSON.
```

## 9. Контракты

```text
[+] contracts/openapi.yaml — 21 новый путь, 20 новых схем (точечная
    вставка без реформата остального файла — проверено побайтовым сравнением
    с исходником минус вставленные блоки)
[+] pnpm contracts:generate — packages/contracts/generated/types.ts
    обновлён и закоммичен
```

## 10. Тесты (72 новых теста для эпизода 5)

```text
[+] Миграция: 7 тестов (test_country_contribution_mig.py)
[+] Contributor lifecycle + scoping: test_country_contribution_service.py
    (create/patch/submit, cross-country rejection, draft-lock, forced
    draft-status на создании контента, duplicate metric_slug, timeline
    source-required)
[+] Curator: self-assign, already-assigned, publish без curator -> 409,
    publish с красным гейтом -> 422, publish флипает is_active, reject
    invalid-transition
[+] Scenario scores: неполный набор критериев, сумма весов ≠ 1, расчёт
    overall score + weakest confidence
[+] DQ: 4 теста (test_country_contribution_dq.py) — clean state + 3
    негативных сценария
[+] Demo conservation: 26 тестов (test_demo_country_conservation.py) —
    SQL-фильтр на каждой публичной функции + router-level проверка для
    country_drift/platform_metrics + явное подтверждение, что recompute-
    пути не затронуты
[+] API RBAC: 7 тестов (test_country_contribution_api.py) — deny-by-default,
    401/403/200 на contributor- и curator-эндпоинтах
[+] Restore-скрипт: 5 юнит-тестов на генерацию SQL/касты/dry-run
[-] Acceptance E2E (proposal -> наполнение -> curator scores ->
    readiness-check -> publish -> виден в /countries, /decision/run,
    /search) — НЕ написан как Playwright/integration-тест против реальной
    БД (см. §8 — то же ограничение Docker). Путь покрыт по частям юнит-
    тестами каждого шага, но нет сквозного прогона на реальных данных.
[+] Rights-инвариант deny-by-default — есть на обоих новых роутерах
[+] Весь существующий набор тестов (2011 прежних + 72 новых = 2083) зелёный,
    0 регрессий
```

## 11. Документация

```text
[+] Статус-строка под Эпизодом 5 в 01_План_реализации.md (включая
    зафиксированные решения владельца и архитектурные развилки)
[+] 02_Текущее_состояние_системы.md — строка о is_demo в §3.1, новый абзац
    о контрибуции стран в §3.5
```

## 12. Quality gate

```text
[+] python -m pytest — 2011 passed, 29 skipped (профиль quick) — зелёно
[+] python -m ruff check / format --check — чисто (527 файлов apps/api +
    scripts + tests)
[+] python -m mypy apps packages scripts tests — чисто (527 файлов)
[+] python -m sqlfluff lint database --dialect postgres — чисто
[+] pnpm quality (format:check+lint+typecheck+build) — зелёно, включая
    Next.js production build с обновлёнными сгенерированными типами
[+] python dev_tools_scripts_runner.py --profile quick — 27 OK / 3 WARN
    (стейл кэш-директории, косметика) / 0 FAIL
[~] python dev_tools_scripts_runner.py (полный гейт, Docker-стек +
    миграции + рантайм-смоки + E2E) — запущен в фоне, статус на момент
    закрытия задачи см. в финальном отчёте; НЕ переподтверждён перед
    merge — владелец явно решил слить и запушить без повторного прогона
    полного гейта (2026-07-08), опираясь на уже зелёные quick-гейт и
    статические проверки выше
```

## 13. Завершение

```text
[+] Чек-лист заполнен +/-
[+] Финальный отчёт
[+] Merge --ff-only в main и push выполнены (2026-07-08, подтверждено
    владельцем) — main теперь на a9569f1, идентичен origin/main
```
