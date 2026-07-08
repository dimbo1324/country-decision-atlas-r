# Чек-лист задачи: Эпизод 7 — `feat/community-threads-v1` (треды на контактах)

Цель: лёгкая переписка строго между сторонами с ПРИНЯТЫМ contact request на
доске попутчиков (не мессенджер): polling-доставка, лимит сообщений/день,
закрытие любой стороной, заморозка при блокировке, репорт, модераторский
доступ к переписке только в контексте поданного репорта с аудитом каждого
обращения. Полная реализация по плану
(`docs/_arch_/02_План/01_План_реализации.md`, раздел «Эпизод 7»).
Ветка создана НЕ от `main`, а от текущей рабочей ветки
`fix/demo-country-fresh-db-visibility` — по прямому указанию владельца
(она ещё не смерджена, но уже является «актуальной»). В конце задачи —
явно запрошенный владельцем merge + push в `main` (не требует повторного
подтверждения).

## 0. Архитектурные решения, принятые самостоятельно

```text
[+] Номер миграции — 051, а не 052, как в тексте плана. Плановый текст
    предполагал, что Эпизод 6 (`feat/migration-flows-v1`, тоже
    использующий номер 051) будет смерджен первым. Эта ветка растёт не
    от Эпизода 6, а от отдельной fix-ветки поверх main (main — только по
    050 включительно), поэтому следующий реальный номер здесь — 051.
    Когда/если Эпизод 6 будет смерджен позже, его миграцию потребуется
    переномеровать (051 → следующий свободный) — миграция ещё не
    применена ни в одном реальном окружении, переномерование до merge
    разрешено правилами проекта. Явно зафиксировано здесь, чтобы не
    потерялось.
[+] Статусы треда упрощены до `open|closed|frozen` вместо буквальных
    `open|closed_by_a|closed_by_b|frozen` из наброска плана. Кто именно
    закрыл — отдельная колонка `closed_by_user_id` + `closed_at` (более
    точная запись факта, чем условное разделение на «сторону A/B»).
    Acceptance («любая сторона закрывает») выполняется полностью.
[+] Тред создаётся АВТОМАТИЧЕСКИ в момент принятия contact request
    (внутри `accept_contact_request`), а не отдельным действием — план
    говорит «тред — только на accepted контакт», отдельного «создать
    тред» действия не описано и не нужно: 1:1 связь с contact_request
    (UNIQUE) делает автосоздание естественным и исключает состояние
    «контакт принят, а треда нет».
[+] Заморозка при блокировке — расширение существующего `block_user`
    (services/migration_board/contacts.py): все open-треды между этими
    двумя пользователями переводятся в `frozen`.
[+] Репорт треда переиспользует УЖЕ СУЩЕСТВУЮЩИЙ
    `report_contact_request`/`POST .../contact-requests/{id}/report` —
    тред 1:1 с contact_request, значит репорт на contact_request и есть
    репорт на тред. Отдельного `POST /me/threads/{id}/report` не
    заводим (переиспользование, не переизобретение).
[+] Модераторский доступ к сообщениям треда — новый admin-эндпоинт,
    требующий `report_id` в query: сервис проверяет, что репорт с этим
    id существует и `report.contact_request_id` совпадает с
    `thread.contact_request_id` (без ограничения на статус репорта —
    инвариант требует «в контексте поданного репорта», не «только пока
    репорт не рассмотрен»), плюс `assert_no_moderation_conflict`.
    Каждое обращение — отдельная audit-запись (не только первое).
[+] Лимит сообщений/день — новый параметр методологии
    `board.max_thread_messages_per_day`, добавлен в существующий
    `BoardLimits` (это расширение пакета migration_board, не новый
    домен параметров).
[+] PII-фильтр НЕ применяется к телу сообщений треда (в отличие от
    публичных постов доски) — переписка приватна и видна только двум
    согласившимся сторонам (+ модератору по репорту), фильтрация PII
    предназначена для ПУБЛИЧНЫХ поверхностей (инвариант «PII-фильтр на
    публичных проекциях», не на приватных каналах).
[+] Auth-зависимость — `require_user` (не `get_current_active_user`),
    по конвенции остального пакета migration_board/api/v1/
    migration_board.py.
```

## 1. Миграция 051

```text
[+] CREATE TABLE contact_threads (id, contact_request_id UNIQUE FK,
    status open|closed|frozen, closed_by_user_id, closed_at,
    created_at, updated_at)
[+] CREATE TABLE thread_messages (id, thread_id FK CASCADE,
    sender_user_id FK, body NOT NULL non-empty, created_at) + индекс
    (thread_id, created_at, id) для polling
[+] INSERT methodology_parameters: board.max_thread_messages_per_day
[+] INSERT feature_flags + feature_access_rules: community_threads_enabled
[+] sqlfluff-чисто, идемпотентно (schema-тесты — отдельным пунктом
    в §7, test_community_threads_mig.py)
```

## 2. Methodology config

```text
[+] services/methodology_config.py: BOARD_MAX_THREAD_MESSAGES_PER_DAY,
    поле в BoardLimits, REQUIRED_NUMERIC_KEYS, build_methodology_config
[+] repositories/data_quality/methodology_config.py: диапазон в
    REQUIRED_NUMERIC_PARAMETER_SQL
[+] tests/methodology_test_helpers.py + test_flexible_methodology_v1.py:
    обновлены под новый обязательный параметр
```

## 3. Репозиторий (`repositories/migration_board/threads.py`)

```text
[+] create_thread_for_contact_request, get_thread_by_id,
    get_thread_for_contact_request, list_messages (after/limit),
    create_message, count_messages_created_since, close_thread,
    freeze_threads_between_users, list_my_threads
[+] Ре-экспорт в repositories/migration_board/__init__.py
```

## 4. Сервисы

```text
[+] services/migration_board/threads.py — list_my_threads,
    get_thread_messages, send_message (ownership+status+лимит+аудит),
    close_thread (ownership+аудит), get_thread_for_moderation
    (report_id-гейт+no-conflict+аудит на каждый вызов)
[+] services/migration_board/contacts.py — accept_contact_request
    создаёт тред; block_user замораживает открытые треды
```

## 5. API и контракты

```text
[+] schemas/migration_board.py — Thread*/ThreadMessage* модели
[+] api/v1/migration_board.py — GET /me/threads, GET /me/threads/
    {id}/messages, POST /me/threads/{id}/messages, POST /me/threads/
    {id}/close (require_user)
[+] api/v1/admin_migration_board.py — GET /admin/migration-board/
    threads/{id}/messages?report_id= (require_capability(MODERATOR_BOARD))
[+] contracts/openapi.yaml — точечная вставка 4 путей + 6 схем (сверено
    байт-в-байт с app.openapi() через test_committed_openapi_matches_
    runtime_paths_and_schemas), pnpm contracts:generate — types.ts
    перегенерирован, pnpm typecheck/lint фронтенда зелёные
```

## 6. Data quality

```text
[+] Расширение services/data_quality/migration_board_checks.py +
    repositories/data_quality/migration_board.py новыми проверками:
    list_open_threads_without_active_contact (открытый тред без
    accepted контакта), list_thread_messages_after_thread_closed
    (сообщение после closed_at), list_thread_messages_after_block
    (сообщение после блокировки — прокси для заморозки, так как в
    contact_threads нет отдельной колонки frozen_at)
```

## 7. Тесты (~20-30 по плану)

```text
[+] test_community_threads_mig.py (5 тестов: таблицы, lifecycle-констрейнты,
    polling-индекс, сид параметра методологии, сид feature flag)
[+] test_community_threads_service.py (19 тестов: counterpart-имя,
    ownership на чтении/отправке/закрытии, thread_not_open, empty body,
    дневной лимит, close→409 если уже не open, moderator report-гейт +
    conflict-of-interest + audit на КАЖДЫЙ вызов, автосоздание треда в
    accept_contact_request, freeze_threads_between_users в block_user)
[+] test_community_threads_api.py (10 тестов: 401 без auth, polling
    after/limit прокидываются, 404/409/422 из сервиса корректно всплывают,
    RBAC на admin-эндпоинте — 403 без capability, 422 без report_id)
[+] test_community_threads_dq.py (4 теста: регистрация обеих проверок +
    открытый тред без активного контакта + сообщение после закрытия +
    сообщение после блокировки; полный набор DQ-тестов зелёный, 24 passed)

Итого 38 новых тестов; полный `pytest tests/` зелёный за вычетом уже
известного (не связанного с этой секцией) контрактного разрыва — см. §9.
```

## 8. Документация

```text
[+] Статус-строка под Эпизодом 7 в 01_План_реализации.md (включая
    пояснение про номер миграции 051 вместо 052, упрощённые статусы,
    отказ от Telegram deep-link в v1)
[+] 02_Текущее_состояние_системы.md — обновление раздела 3.5 (новый
    буллет «Треды на контактах»)
```

## 8а. Внепланово: root-cause фикс full quality gate (не задача Эпизода 7)

```text
[+] Полный gate на реально пересобранном стеке (docker compose up
    --build) вскрыл, что restore_demo_countries.py --visible падает на
    UniqueViolation countries_slug_key — countries.id / locales.id /
    scenarios.id / cii_metric_definitions.id назначаются
    gen_random_uuid() без фиксированного сида, поэтому экспортированный
    фикстур embeds id, которые СВЕЖАЯ база миграций никогда не
    воспроизведёт. Это баг основания текущей ветки (fix/demo-country-
    fresh-db-visibility), не Эпизода 7, но он блокировал обязательный
    gate этой задачи — исправлено здесь и явно вынесено отдельным
    пунктом, а не спрятано внутри диффа треда.
[+] Добавлен generic remap по natural key (slug/code) для countries +
    трёх внешних lookup-таблиц (locales.code, scenarios.slug,
    cii_metric_definitions.slug), применяется ко всем строкам всех
    demo-таблиц перед upsert. Экспорт дополнен sidecar-файлами
    (_lookup_locales.json и т.п.). Фикстуры переэкспортированы с текущего
    стека. 8 новых юнит-тестов на remap-логику.
[+] Попутно исправлен Path.write_text() без newline="\n" — на Windows
    транслировал \n в CRLF, из-за чего mixed-line-ending каждый раз
    «чинил» экспортированные фикстуры и валил pre-commit.
[+] Прогнан заново на живом стеке: countries=3, все 3 /trust endpoint'а
    200, Playwright E2E зелёный, pre-commit run --all-files зелёный.
```

## 9. Полный quality gate и завершение

```text
[+] python dev_tools_scripts_runner.py (full-check, профиль по
    умолчанию): OK 78, WARN 3 (только stale .mypy_cache/.ruff_cache/
    .tmp — некритично), FAIL 0, SKIP 1 (protoc generate — по конвенции
    проекта, .pb.go закоммичены как есть)
[+] Чек-лист заполнен +/-
[+] Финальный отчёт (в ответе владельцу по завершении задачи)
[+] Merge --ff-only в main и push — ЯВНО запрошено владельцем в этой
    задаче, подтверждение повторно не требуется
```
