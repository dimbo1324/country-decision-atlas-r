# Чек-лист задачи: Эпизод 4 — `feat/author-metrics-v1` (авторские метрики)

Цель: открыть систему метрик сообществу — создание, премодерация, публикация,
подписки, форки, производная репутация авторов. Платформенный CII
неприкосновенен (инварианты §5.2, §5.22).

## 0. Подготовка

```text
[ ] Ветка feat/author-metrics-v1 создана от свежего main
[ ] origin/main был актуален на момент создания ветки
[ ] Прочитан раздел «Эпизод 4» в 01_План_реализации.md
[ ] Прочитан реестр инвариантов 02_Реестр_инвариантов.md
[ ] Прочитана модель прав 03_Модель_прав_и_ролей.md
[ ] Архитектурная карта переиспользуемых паттернов собрана
    (lifecycle, RBAC, methodology_config, PII-скан, recompute-скрипт,
    audit, feature flags, package layout, DQ, contracts, тесты)
```

## 1. Миграция 049

```text
[ ] database/migrations/049_author_metrics_v1.sql создана
[ ] author_metric_definitions (author_user_id, slug, name_en/ru,
    methodology_en/ru, polarity, scale_min/max, license, status,
    visibility, forked_from_id, version, timestamps, UNIQUE(author_user_id, slug))
[ ] author_metric_values (metric_id, country_id, value, source_url,
    is_personal_experience, note, valid_as_of, updated_at,
    UNIQUE(metric_id, country_id), CHECK source_url IS NOT NULL OR is_personal_experience)
[ ] author_subscriptions (user_id, metric_id NULL, author_user_id NULL,
    CHECK metric_id IS NOT NULL OR author_user_id IS NOT NULL)
[ ] author_reputation (author_user_id PK, coverage/freshness/sourcing_score,
    subscriber_count, published_metric_count, computed_at, methodology_version)
[ ] Индексы на внешних ключах (author_user_id, metric_id, country_id)
[ ] Миграция идемпотентна (IF NOT EXISTS / ON CONFLICT)
[ ] Миграция sqlfluff-clean
[ ] Новые methodology_parameters добавлены (мин. длина методологии,
    мин. покрытие стран для публикации) через ON CONFLICT DO NOTHING
[ ] Feature flag author_metrics_enabled добавлен (status/access_tier/default_enabled
    + feature_access_rules) по образцу последней миграции с флагами
```

## 2. Сервисный пакет `services/author_metrics/`

```text
[ ] helpers.py (общие приватные хелперы, квалифицированный доступ из подмодулей)
[ ] definitions.py — CRUD + lifecycle draft→review→published→archived(+rejected)
[ ] definitions.py — submit требует методологию не короче порога
[ ] definitions.py — publish требует покрытие >= N стран (methodology_config)
[ ] definitions.py — PII-скан name/methodology текстов при submit
[ ] values.py — bulk-upsert значений, валидация шкалы scale_min/max
[ ] values.py — CHECK source_url OR is_personal_experience применяется в сервисе тоже (422 без источника/пометки)
[ ] subscriptions.py — подписка на метрику/автора, отписка, лента подписок
[ ] reputation.py — расчёт coverage/freshness/sourcing по образцу trust
[ ] overlay.py — авторский слой для страницы страны/сравнения, ОТДЕЛЬНЫЕ эндпоинты
[ ] forks.py — форк копирует определение+методологию, forked_from_id, автор сам заполняет значения
[ ] __init__.py — re-export публичного API пакета
```

## 3. Repository layer

```text
[ ] repositories/author_metrics.py — SQL-only, параметризованный
[ ] CRUD для author_metric_definitions
[ ] CRUD для author_metric_values (upsert)
[ ] CRUD для author_subscriptions
[ ] CRUD/upsert для author_reputation
[ ] list/count с фильтрами (status, author, country)
```

## 4. Схемы и API

```text
[ ] schemas/author_metrics.py — Pydantic-схемы (definition, value, subscription,
    reputation, overlay-ответ)
[ ] api/v1/author_metrics.py (публичный + /me роутер)
[ ] GET/POST/PATCH /me/author-metrics (+submit/archive)
[ ] PUT /me/author-metrics/{id}/values (bulk)
[ ] POST /author-metrics/{id}/fork
[ ] GET /authors/{user_id}/metrics
[ ] GET /countries/{slug}/author-metrics
[ ] POST/DELETE /me/subscriptions
[ ] GET /me/subscriptions/feed
[ ] api/v1/admin_author_metrics.py — GET /admin/author-metrics?status=review
[ ] Права: создание/ведение — require_capability("author.metrics"), свои объекты
[ ] Права: премодерация — require_capability_or_roles("moderator.metrics", ...)
[ ] Права: конфликт интересов на модерации (assert_no_moderation_conflict)
[ ] Каждое привилегированное действие — audit_events
[ ] Feature flag author_metrics_enabled проверяется на каждой поверхности
```

## 5. Recompute-скрипт

```text
[ ] scripts/recompute_author_reputation.py по образцу recompute_trust_scores.py
[ ] --dry-run поддержан
[ ] JSON-сводка на выходе
[ ] Зарегистрирован в dev_tools_scripts_runner.py
```

## 6. Инварианты ядра (закреплены тестами)

```text
[ ] Snapshot-тест: ответы CII/decision/compare идентичны до/после сида
    авторских метрик (§5.2, §5.22 реестра инвариантов)
[ ] Ни один файл decision_engine/CII не импортирует services/author_metrics
[ ] Публикация без методологии невозможна (422)
[ ] Каждое значение — источник ИЛИ личный опыт (422 иначе)
[ ] Форк несёт forked_from_id
```

## 7. Data Quality

```text
[ ] repositories/data_quality/author_metrics.py — dq-запросы домена
[ ] services/data_quality/author_metrics_checks.py — _append_author_metrics_checks
[ ] Подключено в services/data_quality/report.py
[ ] install_clean_report_fakes() в tests/test_data_quality_validation.py
    обновлён новыми функциями (известная ловушка — иначе ~90 тестов падают)
```

## 8. Contracts

```text
[ ] OpenAPI обновлён (paths + schemas для author-metrics/subscriptions/admin)
[ ] pnpm contracts:generate выполнен
[ ] packages/contracts/generated/types.ts обновлён и закоммичен
```

## 9. Тесты

```text
[ ] Unit: definitions lifecycle (draft/review/published/archived/rejected)
[ ] Unit: values validation (scale, source-or-personal-experience)
[ ] Unit: subscriptions CRUD
[ ] Unit: reputation расчёт
[ ] Unit: forks (lineage, независимые значения)
[ ] API: RBAC-матрица (user без гранта / +author.metrics / moderator.metrics / owner)
[ ] API: deny-by-default на каждом привилегированном роутере
[ ] API: overlay-эндпоинты не ломают публичные country/decision эндпоинты
[ ] DQ: тесты новых проверок (чистая база / нарушения)
[ ] Инвариант: snapshot CII/decision до-после (см. блок 6)

```

## 10. Полный quality gate

```text
[ ] python -m pytest
[ ] python -m mypy apps packages scripts tests
[ ] python -m ruff check . / ruff format --check .
[ ] python -m sqlfluff lint database --dialect postgres
[ ] pnpm contracts:generate (без незакоммиченного дифа)
[ ] pnpm quality (format/lint/typecheck/build)
[ ] python dev_tools_scripts_runner.py (полный гейт)
[ ] Docker clean DB chain, если затронуто раннее покрытие
[ ] git status / git diff --check чистые
```

## 11. Closeout

```text
[ ] **Статус.** добавлен под Эпизодом 4 в 01_План_реализации.md
[ ] 02_Текущее_состояние_системы.md обновлён, если структура системы меняется
[ ] Чек-лист заполнен +/- перед финальным коммитом
[ ] Финальный отчёт написан
[ ] Merge --ff-only в main выполнен (после подтверждения владельца)
[ ] Push в origin/main выполнен (после подтверждения владельца)
```
