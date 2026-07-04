# Технический проект: система как есть и этапы реализации

> Документ для инженера. Часть I описывает реализованную систему — архитектуру, домены, конвенции, инварианты — как факт, от которого строим. Часть II — этапы новой линии разработки, с первого. Часть III — сквозные инженерные темы. Продуктовое обоснование и спорные вопросы — в `ARCHITECT_REVIEW.md`; здесь — как это устроено и как это строить.
>
> Все утверждения Части I проверены по коду репозитория, а не по документации. Дата: 2026-07-04.

---

# Часть I. Система как она есть

## 1. Общая архитектура

```
                    ┌─────────────────────────────────────────────────┐
                    │                КЛИЕНТЫ                          │
                    │   Next.js 15 (apps/web)      Telegram-бот       │
                    └───────────┬─────────────────────────▲───────────┘
                                │ REST /api/v1 (OpenAPI)  │ уведомления
                    ┌───────────▼─────────────────────────┼───────────┐
                    │   FastAPI (apps/api) — модульный монолит        │
                    │   34 роутера → 64 сервиса → 47 репозиториев     │
                    │   Redis-кэш (mode: null|redis)                  │
                    └───────┬──────────────────────┬──────────────────┘
                            │ SQL (psycopg)        │ INSERT domain_events
                    ┌───────▼───────┐      ┌───────▼────────┐
                    │  PostgreSQL   │      │ outbox: table  │
                    │ source of     │      │ domain_events  │
                    │ truth, 45     │      └───────┬────────┘
                    │ миграций      │              │ scripts/outbox_relay.py
                    └───────────────┘              ▼ (batch, идемпотентность
                                            ┌────────────┐   по event_key,
                                            │ Kafka      │   NOTIFY_AFTER-отсечка,
                                            │ (Redpanda) │   fake|kafka publisher)
                                            └─────┬──────┘
                                                  ▼
                    ┌─────────────────────────────────────────────────┐
                    │  Go-нотификатор (apps/notifier)                 │
                    │  Kafka-consumer → каналы (абстракция) → Telegram│
                    │  Mongo — производное состояние (delivery log,   │
                    │  перестраиваемое), DLQ, метрики, health,        │
                    │  gRPC-сервер подписок (линковка Telegram↔web)   │
                    └─────────────────────────────────────────────────┘
```

Принципы, зафиксированные как инварианты (реестр — `docs/_arch_/09_План_реализации_проекта.md` §6, соблюдены в коде):

- PostgreSQL — единственный source of truth; Go/Kafka/Mongo — только доставка и производное состояние.
- Формула CII, scenario-веса и decision-scoring неизменны; всё новое — слои поверх (Persona, Drift, Trust, кастомные веса).
- Производные метрики (LVI/SSRS/Contradiction, Trust) в агрегированный CII не примешиваются.
- Внешние системы (LLM, Telegram) — через провайдерный шов, Fake-by-default, переключение настройкой.
- Outbox: события на переходе в `published`, идемпотентность по `event_key`, `notifiable=FALSE` для сидов.
- Source-backed и «не юридическая консультация» — на всём публичном контенте.

`docker-compose`: postgres, redis, api, redpanda, mongo, notifier.

## 2. Слои и конвенции кода

| Слой | Где | Правило |
|---|---|---|
| Роутеры | `apps/api/app/api/v1/*.py` | Тонкие: парсинг, зависимости (auth/RBAC/connection), вызов сервиса |
| Сервисы | `apps/api/app/services/` | Вся бизнес-логика. Крупные домены — пакетами (`migration_board/`, `decision_engine/`, `data_quality/`) с re-export публичной поверхности через `__init__.py` |
| Репозитории | `apps/api/app/repositories/` | Только SQL (есть тесты «repository is SQL-only»), без FastAPI-зависимостей |
| Схемы | `apps/api/app/schemas/` | Pydantic; OpenAPI-контракт → генерация TS-типов (`pnpm contracts:generate`) |
| Ядро | `apps/api/app/core/` | config (Settings), database (fetch_one/fetch_all/execute_one), errors (`api_error` → единый формат `{detail: {error: {code, message, details}}}`), auth (CurrentUser), rbac (require_roles) |

Ключевые конвенции (детально — `CLAUDE.md`):

- **Локализация — overlay на чтении**: `overlay_localized_fields(connection, rows, entity_type, id_field, mapping, locale)` накладывает переводы из translation-слоя поверх строк read-модели; статусы `source|translated|fallback|missing` отдаются клиенту. Легаси-колонки `*_ru/*_en` сохраняются (инвариант).
- **Пакетная декомпозиция**: файлы >800 строк режутся на пакет; кросс-катящие приватные хелперы — в `helpers.py` с квалифицированным доступом (`helpers.fn()`), иначе monkeypatch в тестах перестаёт перехватывать вызовы (задокументированная ловушка).
- **Feature flags**: `ensure_feature_enabled(connection, key, message)` — 403 `feature_disabled`; флаги с статусами enabled/disabled/internal/deprecated и тирами public/beta/internal/admin + правила.
- **Тесты**: ~150 файлов (~1.8 тыс. тестов); паттерны — MagicMock-connection, monkeypatch на модуль репозитория, `_assert_error` для кодов ошибок; migration-тесты читают SQL-файлы; dq-тесты мокают репозиторий data quality.

## 3. Карта доменов и возможностей

### 3.1 Контент-ядро (эталонные данные, редактируются владельцем)

| Домен | Таблицы (ключевые) | API | Особенности |
|---|---|---|---|
| Страны и карточки | countries, country_profiles, country_cards | `/countries`, `/countries/{slug}`, `/countries/{slug}/card` | 3 страны (RU/UY/AR), RU/EN, publication lifecycle |
| Источники и доказательства | sources, evidence_items | `/sources`, `/sources/{id}/evidence` | Тип/язык/confidence, только published наружу |
| Правовые сигналы | legal_signals (+legal_status), legal_signal_events | `/legal-signals`, timeline | Impact direction/level, таймлайн по годам, source-backed |
| Маршруты | routes, route_documents, route_sources, route_evidence, route_checklist_items | `/routes/*`, `/countries/{slug}/routes` | Чек-лист шага: документы, стоимость, сроки, официальные требования — с источниками |
| Пары стран | country_pair_compatibility (+sources, +evidence) | `/country-pairs/*` | origin→destination: визы/налоги/банкинг/перелёты/язык/ограничения; основа origin-aware решений |
| Справочное | glossary, methodology_sections, data journal | `/glossary`, `/methodology`, `/data-journal` | |

### 3.2 Решения (детерминированное ядро + слои)

| Возможность | Механика |
|---|---|
| `/decision/run` | 5 сценариев × 7 критериев; сохранённые score breakdowns; ранжирование `(-score, -confidence, slug)`; strengths ≥70 / weaknesses ≤50; risk warnings из сигналов; всё с source_ids |
| Кастомные веса | per-request; нормализация, валидация (полнота, диапазон, сумма>0); пересчёт runtime-скора без записи; аналитическое событие |
| Persona | Слой: модификаторы метрик (−0.5…+0.5) → adjusted weights (сумма=1, неотрицательность — проверяется) → persona-adjusted ранжирование |
| Origin-aware | При origin_country: pair-контексты подмешиваются в результаты + статус контекста |
| Сравнение | `/decision/compare`: winner/tie (дельта <3 — tie/low, <10 — medium, иначе high), объяснение |
| Паспорта | `/decision/passports`: снапшот запроса+результата; público-токен (в БД — hash+prefix), TTL, 410 на истёкший |
| Wizard | Цель → сценарий, слайдеры → веса |

### 3.3 Вычисляемые слои (производные, версионируемые)

| Слой | Хранение | Пересчёт |
|---|---|---|
| CII | cii_metric_definitions (полярность, источник, active), country_metric_values, scenario_metric_weights (**version**), country_cii_scores (formula_version, aggregation_method=geometric) | сид + admin recompute |
| Platform metrics (LVI, SSRS, Contradiction) | country_platform_metrics (methodology_version) | `recompute_platform_metrics.py`, идемпотентно, dry-run |
| Trust Score | country_trust_scores (label, confidence, components, expires_at) | recompute-скрипт; из counts/freshness/contradiction |
| Drift | country_drift_snapshots (period, label, confidence) | из legal_signal_events (direction×level×веса), confidence downgrade при малых данных |

### 3.4 Платформа и пользователь

- **Auth/RBAC**: PBKDF2-SHA256 (260k итераций), сессии с TTL и revoke-all, роли user/editor/moderator/owner, правила промоции (owner-only), регистрация за флагом; Telegram-линковка через gRPC к нотификатору (код-подтверждение).
- **Watchlists** (за флагом), **What changed** (окно/`since`, по стране), **Search** (search_documents + GIN, `build_search_vector`, rebuild-скрипт, локали раздельно), **Analytics** (hash сессий, санитизация metadata, запрещённые ключи), **Feature flags API**, **Cache** (null|redis, ключи включают response-affecting параметры).

### 3.5 Сообщество

- **Q&A**: вопросы/ответы pending→published (модерация), консенсус прозрачной формулой (взвешивание + бонус source-backed + детект «спорного» по разбросу).
- **User stories**: структурированные, verification status, synthetic-маркировка; рейтинги историй по 6 осям; репорты ошибок данных.
- **Миграционная доска**: посты (draft→review→published lifecycle + модерация approve/reject/hide), видимость public/members_only/private, PII-детектор (email/телефон/@handle/URL) на публичных текстах, контакт-запросы (взаимное согласие, дневной лимит 20), блокировки, репорты (лимит 20/день, дедупликация pending), companion matching по destination/route/timeline/scenario с причинами совпадения, приватная публичная проекция (`_public_post` не отдаёт user_id/email).

### 3.6 AI-контур (инструментальный, Fake-by-default)

- Провайдерный шов `ai_providers.py`; контекст — только из published search documents + сохранённых метрик (без пересчёта); `/ai/ask` (цитаты, отказ без контекста), `/ai/explain-number` (без запуска движка), `/ai/decision-intent` (хинты, не решение); драфты → `needs_review`, к read-моделям не прикасаются; contradiction candidates → на review; interaction logs с ограничениями на metadata.

### 3.7 Редакция и операции

Admin CRUD с publication lifecycle и audit_events на переходах; **data quality** — отчёт `valid/invalid`, 60+ проверок пакетом `services/data_quality/` (по доменам: mvp/content/publication/timeline/cii/routes/persona/platform/trust/drift/personalization/passport/pairs/checklists/what-changed/search/ai/auth/board); translation jobs + worker foundation; outbox relay (batch, max attempts, метрики); квоты и лимиты через код-константы.

## 4. Операционный контур

- **Миграции**: `database/migrations/NNN_name.sql`, применение `scripts/apply_migrations.py` по glob-порядку; `schema_migrations(version=имя файла, checksum sha256)` — переименование/правка применённого файла ломает трекинг (требует сброса локального тома).
- **Quality gate**: `python dev_tools_scripts_runner.py [--profile quick|backend|frontend|docker|full|ci] [--doctor] [--fix]` — оркестратор → `scripts/dev_tools/full_check.py` (диагностика системы/сети/Docker, тулчейн, зависимости, статика ruff/mypy/sqlfluff, pytest, Go vet/test, Docker-стек+миграции+runtime-смоки+E2E Playwright, pre-commit, отчёты в `full-check-reports/`).
- **CI**: `.github/workflows/quality.yml` — ruff/mypy/pytest/sqlfluff + фронтенд.
- Ручной набор: `ruff check|format`, `mypy apps packages scripts tests`, `sqlfluff lint database --dialect postgres`, `pytest`, `pnpm quality`, `pre_commit run --all-files`.

## 5. Инвентаризация «жёсткости» (вход в Этап 1)

| Параметр | Значение | Где зашито | Целевое состояние |
|---|---|---|---|
| Пороги score labels | 30/50/70/85 | `services/score_labels.py` | Конфигурация в БД, версия |
| Strengths/weaknesses | ≥70 / ≤50 | `decision_engine/decision_runner.py` | Конфигурация в БД |
| Confidence-границы | ≥2.5 high, ≥1.7 medium | `decision_engine/helpers.py` | Конфигурация в БД |
| Compare-дельты | <3 tie, <10 medium | `decision_runner._recommend` | Конфигурация в БД |
| Кастомные веса | per-request, не сохраняются | `schemas/decision_engine.py` | Сохраняемые профили пользователя |
| Лимиты доски | 5 постов, 20 контактов/д, 20 репортов/д | `migration_board/helpers.py` | Конфигурация в БД (админ-настройка) |
| Enum-словари доски | теги, окна, цели | там же | Остаются в коде (валидация схемы), но ревизия при UI |
| Веса/метрики CII | v1.0 | **уже в БД, версионировано** | Открыть авторам (Этап 3) |
| Persona-модификаторы | −0.5…0.5 | **уже в БД** | Без изменений |

---

# Часть II. Этапы новой линии реализации

Нумерация — с первого. Каждый этап: отдельная ветка `feat/<slug>-v1`, миграции продолжают счётчик (046+), новые поверхности за feature-флагами (выключены до acceptance), data-quality пакет с первого дня, полный quality gate перед merge. Формат унаследован от рабочего стандарта проекта: цель → модель данных → сервисный слой → API → интеграции → тесты → acceptance → сознательно не делаем.

---

## Этап 1 — `feat/flexible-methodology-v1`: гибкая методология

**Цель.** Убрать пороги из кода в версионируемую конфигурацию; дать пользователю сохраняемые профили весов. Нулевое изменение поведения по умолчанию.

### Модель данных (миграция 046)

```sql
CREATE TABLE methodology_parameters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version TEXT NOT NULL DEFAULT 'v1.0',
    param_key TEXT NOT NULL,            -- 'score_label.weak_below', 'strength.min_score', ...
    value_numeric NUMERIC,
    value_json JSONB,
    description TEXT NOT NULL,
    effective_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_methodology_param UNIQUE (version, param_key)
);
-- сид: все значения из таблицы §I.5 под version='v1.0'

CREATE TABLE user_weight_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    scenario_slug TEXT,                  -- NULL = применим к любому сценарию
    weights JSONB NOT NULL,              -- {criterion: weight}
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at/updated_at TIMESTAMPTZ,
    CONSTRAINT uq_profile_name UNIQUE (user_id, name)
);
```

### Сервисный слой

- Новый `services/methodology_config.py`: `get_params(connection, version=ACTIVE) -> MethodologyParams` (типизированный объект), кэш через существующий cache-слой (инвалидация по версии). Потребители (`score_labels`, `decision_engine.helpers`, `_recommend`, лимиты доски) читают из него; сигнатуры чистых функций получают параметры аргументами (сохраняя тестируемость).
- Новый `services/weight_profiles.py`: CRUD профилей; валидация — переиспользовать `decision_personalization.validate_custom_weights` (полнота/диапазон/сумма — уже реализовано).
- `decision/run`: принимает `weight_profile_id` ИЛИ inline `custom_weights` (взаимоисключимо); паспорт решения дополняется `methodology_version` + `weight_profile_snapshot` (значения, не ссылка — воспроизводимость).

### API

```
GET    /api/v1/me/weight-profiles
POST   /api/v1/me/weight-profiles
PATCH  /api/v1/me/weight-profiles/{id}
DELETE /api/v1/me/weight-profiles/{id}
POST   /api/v1/decision/run          # + weight_profile_id
GET    /api/v1/methodology/parameters # публичное чтение активной версии (прозрачность)
```

### Тесты и acceptance

- Регрессия «бит-в-бит»: весь существующий набор тестов проходит без правок ожиданий (сид = текущие константы).
- Unit: чтение параметров, fallback при отсутствии версии — жёсткая ошибка (не тихие дефолты в двух местах).
- Профили: CRUD, применение в run, снапшот в паспорте, изоляция между пользователями.
- dq-проверки: активная версия существует и полна (все ключи), значения в допустимых диапазонах.

**Acceptance:** дефолтное поведение неотличимо от текущего; пользователь сохраняет профиль, применяет его, паспорт воспроизводит расчёт после смены профиля. **Не делаем:** пользовательские пороги, влияющие на чужие просмотры; UI редактирования параметров платформы (только чтение + admin-сид).

**Объём:** 1 миграция, 2 небольших сервиса, правки 4–5 потребителей, ~25–35 тестов.

---

## Этап 2 — `feat/trip-planner-v1`: планировщик переезда

**Цель.** Личный контур ежедневного использования: план → точки → чек-лист → предупреждения правилами → напоминания в Telegram → экспорт/шаринг. Без карты-UI.

### Модель данных (миграция 047)

```sql
CREATE TABLE trips (
    id UUID PK, user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    scenario_slug TEXT,                       -- связь с decision-контуром
    origin_country_id UUID REFERENCES countries(id),
    status TEXT NOT NULL DEFAULT 'draft',     -- draft|active|completed|abandoned
    confidence_tier TEXT NOT NULL DEFAULT 'declared',  -- declared|active|confirmed (Этап 4)
    visibility TEXT NOT NULL DEFAULT 'private',        -- private|link (public не нужен в v1)
    share_token_hash TEXT UNIQUE, share_token_prefix TEXT,   -- паттерн паспортов
    created_at/updated_at/completed_at TIMESTAMPTZ
);

CREATE TABLE trip_waypoints (
    id UUID PK, trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    position INT NOT NULL,
    country_id UUID NOT NULL REFERENCES countries(id),   -- связь со ВСЕМ ядром данных
    city TEXT, kind TEXT NOT NULL DEFAULT 'destination', -- transit|destination|stopover
    planned_from DATE, planned_to DATE,
    notes TEXT,
    CONSTRAINT uq_trip_position UNIQUE (trip_id, position)
);

CREATE TABLE trip_checklist_items (
    id UUID PK, trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    waypoint_id UUID REFERENCES trip_waypoints(id) ON DELETE SET NULL,
    title TEXT NOT NULL, description TEXT,
    due_date DATE, status TEXT NOT NULL DEFAULT 'todo',  -- todo|in_progress|done|skipped
    origin_kind TEXT NOT NULL DEFAULT 'manual',          -- manual|route_template|author_template
    origin_ref UUID,                                     -- route_checklist_items.id и т.п.
    position INT NOT NULL, created_at/updated_at
);

CREATE TABLE trip_reminders (
    id UUID PK, trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    checklist_item_id UUID REFERENCES trip_checklist_items(id) ON DELETE CASCADE,
    remind_at TIMESTAMPTZ NOT NULL,
    channel TEXT NOT NULL DEFAULT 'telegram',
    status TEXT NOT NULL DEFAULT 'scheduled',            -- scheduled|sent|cancelled
    sent_at TIMESTAMPTZ
);

CREATE TABLE trip_annotations (                          -- «стрелочки и пометки»
    id UUID PK, trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    waypoint_id UUID REFERENCES trip_waypoints(id) ON DELETE CASCADE,
    kind TEXT NOT NULL,                                  -- note|item_to_bring|warning_ack
    body TEXT NOT NULL, position INT
);
```

### Сервисный слой — пакет `services/trip_planner/`

```
__init__.py      # re-export публичной поверхности
trips.py         # CRUD планов/точек, статусные переходы, «я переехал» (→ Этап 4/дневник)
checklist.py     # CRUD шагов; импорт из route_checklist_items (published, по стране/маршруту)
warnings.py      # правило-движок: сегменты → country_pair_compatibility + legal_signals
                 #   → [{code, severity, message, source_ids, pair_ref}]
reminders.py     # планирование; выборка due → outbox-событие
sharing.py       # генерация/ревокация токена, публичная PII-безопасная проекция
exports.py       # JSON (полный), ICS (VTODO/VEVENT по дедлайнам, stdlib-генерация), GeoJSON (точки)
helpers.py       # ensure_feature_enabled-обёртки, сериализаторы, _audit/_track_event
```

Правило-движок `warnings.py` — чистая функция над данными пары/сигналов, **без AI**; параметры серьёзности — из methodology_parameters (Этап 1). AI-кнопки («объясни», «черновик чек-листа») — отдельными эндпоинтами через существующий AI-шов, помечены, опциональны.

### Напоминания — через существующий асинхронный контур

1. Cron/скрипт `scripts/dispatch_trip_reminders.py` (по образцу recompute-скриптов): выбирает `scheduled` с `remind_at <= now`, пишет `domain_events(event_type='trip_reminder_due', notifiable=TRUE, event_key='trip_reminder:{id}')`, помечает `sent` транзакционно.
2. Relay доставляет в Kafka → Go-нотификатор: новый тип события в `internal/events` + рендер шаблона → Telegram-канал (линковка уже есть; при отсутствии линковки — событие в DLQ-лог «нет канала», без падения).

### API (все за флагом `trip_planner_enabled`)

```
GET/POST           /api/v1/me/trips
GET/PATCH/DELETE   /api/v1/me/trips/{id}
POST               /api/v1/me/trips/{id}/waypoints            (+PATCH/DELETE/reorder)
GET                /api/v1/me/trips/{id}/warnings              # правило-движок, on-read
GET/POST/PATCH     /api/v1/me/trips/{id}/checklist             (+bulk-import из route)
POST               /api/v1/me/trips/{id}/checklist/import      {route_id}
POST/DELETE        /api/v1/me/trips/{id}/reminders
POST/DELETE        /api/v1/me/trips/{id}/share                 # выдать/отозвать токен
GET                /api/v1/trips/shared/{token}                # публичная проекция
GET                /api/v1/me/trips/{id}/export?format=json|ics|geojson
```

### Интеграции с существующим

- Watchlist: страны плана автоматически добавляются (идемпотентно) — алерты Drift/сигналов начинают работать на план.
- What changed: `GET /me/trips/{id}/what-changed` — прокси к существующему механизму по странам плана.
- Decision: кнопка «создать план из паспорта решения» — waypoint = выбранная страна, scenario подтягивается.

### Тесты и acceptance

- Unit: warnings-движок (матрица: пара с визовой нотой / без пары / сигнал high-impact); статусные переходы; PII-фильтр shared-проекции (перечень запрещённых полей — тест-инвариант).
- Интеграционные (mock-repo): импорт чек-листа, экспорое ICS (валидность структуры), reminder → payload события.
- dq: план без точек — warning; напоминание в прошлом при создании — reject; shared-проекция не содержит user_id/email (автотест).

**Acceptance:** полный цикл «создал план Россия→Уругвай → получил предупреждение из pair-данных с источником → импортировал шаги маршрута → назначил напоминание → получил его в Telegram (fake-режим: запись в delivery log) → отметил шаг выполненным → экспортировал ICS» — без участия AI. **Не делаем:** карту-UI, совместное редактирование, OAuth-календари, публичный каталог планов.

**Объём:** 1 миграция (5 таблиц), пакет из ~7 модулей, 1 скрипт, +1 тип события в notifier, ~50–70 тестов.

---

## Этап 3 — `feat/author-metrics-v1`: авторские метрики

**Цель.** Открыть систему метрик сообществу: создание, модерация, публикация, подписка, форк. Платформенный CII неприкосновенен.

### Модель данных (миграция 048)

```sql
CREATE TABLE author_metric_definitions (
    id UUID PK,
    author_user_id UUID NOT NULL REFERENCES users(id),
    slug TEXT NOT NULL,                       -- уникален в рамках автора
    name_en/name_ru TEXT NOT NULL,
    methodology_en/methodology_ru TEXT NOT NULL,   -- ОБЯЗАТЕЛЬНА к публикации
    polarity TEXT NOT NULL,                   -- positive|negative
    scale_min NUMERIC NOT NULL DEFAULT 0, scale_max NUMERIC NOT NULL DEFAULT 100,
    status TEXT NOT NULL DEFAULT 'draft',     -- существующий lifecycle
    visibility TEXT NOT NULL DEFAULT 'public',
    forked_from_id UUID REFERENCES author_metric_definitions(id),  -- провенанс дерева
    version INT NOT NULL DEFAULT 1,
    created_at/updated_at/published_at,
    CONSTRAINT uq_author_metric UNIQUE (author_user_id, slug)
);

CREATE TABLE author_metric_values (
    id UUID PK, metric_id UUID NOT NULL REFERENCES author_metric_definitions(id) ON DELETE CASCADE,
    country_id UUID NOT NULL REFERENCES countries(id),
    value NUMERIC NOT NULL,
    source_url TEXT,                          -- NULL допустим:
    is_personal_experience BOOLEAN NOT NULL DEFAULT FALSE,  -- но тогда этот флаг обязан быть TRUE (CHECK)
    note TEXT, valid_as_of DATE NOT NULL,
    updated_at TIMESTAMPTZ,
    CONSTRAINT uq_metric_country UNIQUE (metric_id, country_id),
    CONSTRAINT chk_provenance CHECK (source_url IS NOT NULL OR is_personal_experience)
);

CREATE TABLE author_subscriptions (
    id UUID PK, user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    metric_id UUID REFERENCES author_metric_definitions(id) ON DELETE CASCADE,
    author_user_id UUID REFERENCES users(id) ON DELETE CASCADE,  -- подписка на всё автора
    created_at, CONSTRAINT chk_target CHECK (metric_id IS NOT NULL OR author_user_id IS NOT NULL)
);

CREATE TABLE author_reputation (              -- производная, пересчитываемая
    author_user_id UUID PK REFERENCES users(id),
    coverage_score/freshness_score/sourcing_score NUMERIC,
    subscriber_count INT, published_metric_count INT,
    computed_at TIMESTAMPTZ, methodology_version TEXT
);
```

### Сервисный слой — пакет `services/author_metrics/`

`definitions.py` (CRUD+lifecycle: submit→review→publish через существующие переходы; PII-скан текстов методологии — переиспользовать паттерны доски), `values.py` (bulk-upsert значений, валидация шкалы/полярности), `subscriptions.py`, `reputation.py` (recompute-скрипт по образцу trust), `overlay.py` (выдача авторских слоёв для страны/сравнения — **отдельные эндпоинты**, не примесь к CII), `forks.py` (форк копирует определение+методологию с `forked_from_id`; значения НЕ копируются — автор заполняет сам), `helpers.py`.

### API (флаг `author_metrics_enabled`)

```
GET/POST           /api/v1/me/author-metrics                (+PATCH, submit, archive)
PUT                /api/v1/me/author-metrics/{id}/values     # bulk
POST               /api/v1/author-metrics/{id}/fork
GET                /api/v1/authors/{user_id}/metrics         # публичный профиль автора
GET                /api/v1/countries/{slug}/author-metrics   # слои для страницы страны
POST/DELETE        /api/v1/me/subscriptions
GET                /api/v1/me/subscriptions/feed             # обновления подписок
Admin:             /admin/author-metrics?status=review       # премодерация
```

### Ключевые инварианты (закрепить тестами)

1. Ни один платформенный эндпоинт CII/decision/compare не меняет ответ от существования любых авторских метрик (инвариант-тест: снапшот ответов до/после сида авторских данных).
2. Публикация невозможна без методологии и хотя бы N стран покрытия (параметр из Этапа 1).
3. Каждое значение: источник ИЛИ явная пометка «личный опыт» (CHECK + dq).
4. Форк всегда несёт видимую родословную.

### dq-пакет `author_metrics_checks.py`

Значения в шкале; свежесть (valid_as_of старше X — warning); published-метрика без значений — critical; методология короче минимума — critical; осиротевшие подписки.

**Acceptance:** автор проводит метрику draft→review→published; подписчик видит слой на странице страны с подписью «автор, версия, обновлено»; форк наследует родословную; инвариант-тест ядра зелёный. **Не делаем:** монетизацию, «топы авторов», комментарии к метрикам, примешивание к CII.

**Объём:** 1 миграция (4 таблицы), пакет ~7 модулей, 1 recompute-скрипт, admin-роутер, ~60–80 тестов.

---

## Этап 4 — `feat/migration-flows-v1`: потоки и статистика направлений

**Цель.** Агрегированная картина «кто куда движется» с жёсткой анонимизацией; уровни достоверности планов без документов.

### Модель данных (миграция 049)

```sql
CREATE TABLE migration_flow_aggregates (      -- материализуется джобой, не считается на лету
    id UUID PK,
    origin_country_id/destination_country_id UUID NOT NULL REFERENCES countries(id),
    period TEXT NOT NULL,                     -- '2026-Q3'
    trip_count INT NOT NULL,                  -- только если >= k-порога, иначе строка не пишется
    weighted_count NUMERIC NOT NULL,          -- с весами достоверности
    computed_at, methodology_version TEXT,
    CONSTRAINT uq_flow UNIQUE (origin_country_id, destination_country_id, period)
);
```

Достоверность — уже поле `trips.confidence_tier`: `declared` (создан) → `active` (эвристика: ≥X выполненных шагов чек-листа + возраст аккаунта — параметры из Этапа 1) → `confirmed` (пользователь отметил «переехал»; связка с «дневником»: trip → черновик structured user story). Никаких загрузок документов — инвариант.

### Сервис и скрипт

`services/migration_flows.py` (чистый агрегатор: trips active/confirmed + опубликованные посты доски → пары×кварталы; отбрасывание групп < k; веса по тирам) + `scripts/recompute_migration_flows.py` (по образцу recompute_platform_metrics: идемпотентно, dry-run, сводка). API: `GET /api/v1/migration-flows?origin=&destination=&period=` и `GET /me/trips/{id}/flow-context` («в вашем направлении в этом квартале: ≥N планов» + ссылка на доску попутчиков).

### Privacy-инварианты (тесты обязательны)

- Ни при каких параметрах API не возвращает группу меньше k (порог — параметр методологии; рекомендация k=20).
- Только страна→страна×квартал: без городов, дат, любых ID.
- Пересчёт не логирует состав групп.

**Acceptance:** агрегаты соответствуют сидовым данным; группа k−1 не видна; тир повышается по правилам; «дневник» создаёт черновик истории из завершённого плана. **Не делаем:** публичные списки участников направлений; realtime-счётчики; хранение документов (навсегда).

**Объём:** 1 миграция, 1 сервис + скрипт, ~25–35 тестов.

---

## Этап 5 — `feat/community-threads-v1`: треды на принятых контактах

**Цель.** Лёгкий обмен сообщениями строго между взаимно согласившимися (принятый contact request), плюс Telegram deep-link. Не мессенджер.

### Модель данных (миграция 050)

```sql
CREATE TABLE contact_threads (
    id UUID PK,
    contact_request_id UUID NOT NULL UNIQUE REFERENCES migration_board_contact_requests(id),
    status TEXT NOT NULL DEFAULT 'open',      -- open|closed_by_a|closed_by_b|frozen(модерация)
    created_at
);
CREATE TABLE thread_messages (
    id UUID PK, thread_id UUID NOT NULL REFERENCES contact_threads(id) ON DELETE CASCADE,
    sender_user_id UUID NOT NULL REFERENCES users(id),
    body TEXT NOT NULL,                        -- лимит длины; PII-скан НЕ применяем (приватный канал),
    created_at                                 -- но rate limit и report — применяем
);
```

Правила: тред создаётся только на `accepted` контакт; лимит сообщений/день (параметр); любая сторона закрывает тред; блокировка (существующая) замораживает тред; репорт треда → модерация видит переписку только по репорту (зафиксировать в политике приватности). Доставка — polling (`GET .../messages?after=`), никакого WebSocket в v1. Telegram deep-link: если обе стороны линкованы — кнопка «продолжить в Telegram» (обмен username по явному согласию обеих сторон, двухшаговое подтверждение).

**Acceptance:** переписка возможна только в принятом контакте; закрытие/блокировка/репорт работают; лимиты применяются. **Не делаем:** вложения, групповые чаты, realtime, поиск по переписке.

**Объём:** 1 миграция, расширение пакета migration_board (thread-модуль), ~20–30 тестов.

---

## Порядок и зависимости этапов

```
Этап 1 (параметры/профили) ──→ используется всеми последующими (пороги, лимиты, k)
Этап 2 (планировщик) ────────→ Этап 4 (потоки питаются trips)
Этап 3 (авторские метрики) ──→ независим; после 2 по продуктовым причинам (retention до аудитории)
Этап 5 (треды) ──────────────→ независим; по мере роста контактов на доске
```

Рекомендуемая последовательность: **1 → 2 → 3 → 4 → 5**. После них — большой визуальный транш (витрина, инфографика, карта на Leaflet/OSM) как отдельная линия.

---

# Часть III. Сквозные инженерные темы

## 1. Приватность как программа

- **Private-first**: всё личное создаётся приватным; публикация — явное действие с предпросмотром публичной проекции.
- **Чего не храним никогда** (инварианты): проездные документы/брони/сканы; сырые share-токены (только hash+prefix); IP/user-agent в аналитике (уже так).
- **k-анонимность** всех агрегатов о людях (Этап 4 — образец).
- **Права пользователя**: экспорт всех своих данных (JSON) и каскадное удаление аккаунта — оформить отдельной задачей в Этапе 2 (когда появляются первые «тяжёлые» личные данные), не откладывать.
- Retention: interaction-логи и аналитика — политика хранения параметром методологии.

## 2. Производительность и вычислительный стек

Правило: **Postgres до триггера**. Все расчёты — за чистыми функциональными швами (образцы: `cii_score_aggregator`, `trust_score`, drift). Триггеры пересмотра: агрегатный запрос стабильно >1с на реальных данных; batch-пересчёт не влезает в окно; тогда — точечная замена одного модуля (NumPy-джоба или Rust-бинарь за CLI/FFI), контракт не меняется. PyTorch — вне повестки (нет ML-задач по архитектурной позиции проекта).

## 3. Чек-лист нового домена (закреплённая практика)

1. Ветка `feat/<slug>-v1`; миграция со следующим номером + header-комментарий.
2. Пакет в `services/` по house style (`helpers.py` + квалифицированный доступ, re-export в `__init__.py`).
3. Feature flag (выключен) + `ensure_feature_enabled` на каждой поверхности.
4. События — только через outbox (`event_key`-идемпотентность).
5. dq-модуль `_append_<domain>_checks` + подключение в отчёт.
6. Тесты: unit (чистая логика), API (mock-repo), migration-тест схемы, privacy-инварианты где применимо.
7. Полный quality gate (`dev_tools_scripts_runner.py --profile full`) перед merge; пуш в main — только с явного подтверждения владельца.

## 4. Наблюдаемость новых контуров

Каждый новый домен пишет analytics-события по существующему паттерну (hash-сессии, безопасные metadata): created/updated/shared для trips, published/subscribed/forked для метрик, reminder_sent (из relay-метрик). Счётчики пересчётов — в вывод recompute-скриптов (образец: platform metrics summary).

## 5. Технические риски

| Риск | Митигация |
|---|---|
| Рост outbox-трафика (напоминания) | Батчинг relay уже есть; отдельный event_type и, при необходимости, отдельный топик — решение на уровне конфигурации |
| Kafka/Mongo-контур обязателен для напоминаний в dev | Fake-publisher уже поддержан relay'ем; в тестах события проверяются на уровне таблицы domain_events |
| Взрыв авторских данных низкого качества | Премодерация + dq-пороги публикации + лимиты на автора (параметры Этапа 1) |
| Дрейф методологии при «гибких» порогах | Единственный источник — methodology_parameters; запрет дублирования дефолтов в коде (ревью-правило); версия в каждом ответе и паспорте |
| Переименование применённых миграций | Уже задокументировано в CLAUDE.md: имя+checksum в schema_migrations; никогда не трогать применённые файлы |

---

*Связанные документы: `ARCHITECT_REVIEW.md` (продуктовое обоснование и открытые вопросы), `docs/_arch_/09_План_реализации_проекта.md` (исторический план реализованной базы, его реестр инвариантов остаётся в силе), `CLAUDE.md` (конвенции кодовой базы).*
