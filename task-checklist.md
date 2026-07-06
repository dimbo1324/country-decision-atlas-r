# Чек-лист задачи: аудит и исправление эпизодов 1–4

Цель: аудит `feat/flexible-methodology-v1`, `feat/trip-planner-v1`,
`feat/rights-capabilities-v1`, `feat/author-metrics-v1` силами 4 параллельных
`country-atlas-quality-reviewer` агентов; исправление найденных багов и
уязвимостей высокой критичности в отдельной ветке.

## 0. Аудит

```text
[+] 4 параллельных агента-ревьюера запущены (по одному на эпизод)
[+] Отчёты собраны и приоритизированы (critical/high/medium/low)
[+] Сводка представлена владельцу
```

## 1. Найденные проблемы (сводка)

```text
Эпизод 1 (methodology):
[+] HIGH — DQ-проверка обязательных параметров не покрывает все ключи из
    REQUIRED_NUMERIC_KEYS (board.auto_hide_report_threshold, оба параметра
    author_metrics) — отчёт качества остаётся зелёным при сломанном конфиге
[+] MEDIUM — нет кросс-проверки strength_min_score > weakness_max_score
[-] LOW — потокобезопасность in-process кеша конфигурации — не трогаем
    (assignment атомарен в CPython, риск чисто теоретический)
[-] LOW — clear_methodology_config_cache не вызывается нигде в проде —
    не трогаем (нет admin-эндпоинта записи параметров, дремлющий риск)

Эпизод 2 (trip planner):
[+] HIGH — reorder_waypoints ломается почти на любой непоследовательной
    перестановке (UNIQUE(trip_id, position) не DEFERRABLE, построчная запись)
[+] MEDIUM — та же экспозиция на одиночном PATCH position для waypoint/
    checklist item

Эпизод 3 (rights/capabilities):
[+] HIGH — moderated_by/reviewed_by в admin_community.py берутся из тела
    запроса клиента, а не из current_user.id — подделываемый audit-трейл
[-] HIGH — assert_no_moderation_conflict не применяется в модерации
    сообщества — ОЦЕНЕНО, НЕ ПРИМЕНИМО в текущем виде: контент сообщества
    авторизуется анонимными/telegram-идентичностями (created_by_identity_type/
    _id), не platform user_id; сравнивать current_user.id не с чем без
    более крупного редизайна (привязка реального user_id к контенту
    сообщества) — вне рамок этого фикс-прохода, зафиксировано как открытый
    вопрос для будущего эпизода
[-] MEDIUM — CONTRIBUTOR_COUNTRIES объявлена, но нигде не используется —
    НЕ БАГ: заготовка под Эпизод 5 (feat/country-contribution-v1), не трогаем
[-] LOW — re-grant после revoke теряет историю строки в user_capabilities
    (audit_events сохраняет действия отдельно) — не трогаем, решение владельца

Эпизод 4 (author metrics):
[+] HIGH — bulk_upsert_values позволяет дублирующийся country_slug в одном
    запросе — тихая перезапись последним значением без ошибки
[+] MEDIUM — двухпроходная валидация не resolve'ит country_slug в первом
    проходе — validate-then-write работает только благодаря транзакции,
    не по конструкции
[-] LOW — формула coverage_score (плоское усреднение) — продуктовый вопрос,
    не баг, не трогаем
[-] LOW — author_metrics_enabled включён по умолчанию — соответствует
    паттерну ВСЕХ существующих флагов в проекте, не отклонение, не трогаем
[-] LOW — миграция 049 не проверялась на чистой БД (Docker недоступен) —
    уже задокументировано в предыдущем отчёте, вне рамок этого фикса
```

## 2. Исправления

```text
[ ] Эп.1: services/data_quality/methodology_config_checks.py +
    repositories/data_quality/methodology_config.py — список обязательных
    параметров генерируется из REQUIRED_NUMERIC_KEYS (единый источник истины)
[ ] Эп.1: methodology_config.py — _validate_thresholds проверяет
    strength_min_score > weakness_max_score
[ ] Эп.2: repositories/trip_planner/waypoints.py + services — реордер через
    двухфазную запись (временное смещение позиций) без падения UNIQUE
[ ] Эп.2: repositories/trip_planner/checklist.py — аналогичная защита для
    checklist items, если применимо к их reorder-паттерну
[ ] Эп.3: api/v1/admin_community.py — moderated_by/reviewed_by выводятся из
    current_user.id, убраны из тел запросов (CommunityStatusUpdateRequest,
    DataErrorReportStatusUpdateRequest, UserStoryRatingStatusUpdateRequest)
[ ] Эп.4: schemas/author_metrics.py — BulkUpsertAuthorMetricValuesRequest
    отклоняет дублирующийся country_slug (422)
[ ] Эп.4: services/author_metrics/values.py — resolve country_slug в первом
    проходе (validate-then-write по конструкции, а не по случайности)
```

## 3. Тесты

```text
[ ] Регрессионный тест на дублирующийся country_slug в bulk-upsert (422)
[ ] Тест на реордер waypoints, не являющийся чистым добавлением в конец
[ ] Тест: moderated_by/reviewed_by в ответе — это id аутентифицированного
    модератора, а не то, что прислал клиент
[ ] Тест: DQ-проверка обязательных параметров реагирует на любой ключ из
    REQUIRED_NUMERIC_KEYS, не только на захардкоженный список
[ ] Тест: strength_min_score <= weakness_max_score -> MethodologyConfigError
[ ] Все существующие тесты по затронутым доменам зелёные
```

## 4. Contracts

```text
[ ] Если тела запросов схем изменились (community/data-error/user-story) —
    contracts/openapi.yaml обновлён вручную + pnpm contracts:generate
```

## 5. Полный quality gate

```text
[ ] python -m pytest
[ ] python -m mypy apps packages scripts tests
[ ] python -m ruff check . / ruff format --check .
[ ] python -m sqlfluff lint database --dialect postgres
[ ] pnpm contracts:generate (без незакоммиченного дифа)
[ ] pnpm quality
[ ] python dev_tools_scripts_runner.py (полный гейт)
```

## 6. Closeout

```text
[ ] Чек-лист заполнен +/- перед финальным коммитом
[ ] Финальный отчёт написан
[ ] Merge --ff-only в main выполнен (после подтверждения владельца)
[ ] Push в origin/main выполнен (после подтверждения владельца)
```
