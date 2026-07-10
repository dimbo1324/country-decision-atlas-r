# Чек-лист задачи: AE-4 «Целостность при конкурентности»

Цель: закрыть Аудит-эпизод 4 (`docs/_arch_/09_План_устранения_аудита.md`,
находки P1-1, P1-2, P1-3, P2-9) — убрать гонки «check-then-act» и длинную
транзакцию, блокирующую БД внешним сервисом (Kafka).

Ветка: `fix/concurrency-integrity-v1` (совпадает с именем из плана эпизода).
Решения владельца не требуется — эпизод независим.

## Подготовка

- [+] Прочитан раздел «Аудит-эпизод 4» плана устранения аудита.
- [+] Изучены: `scripts/outbox_relay_runner.py`,
      `repositories/domain_events.py`, `services/migration_board/*.py`,
      `services/auth.py` (register), `services/country_contribution/
      proposals.py`, `services/author_metrics/definitions.py`,
      `services/weight_profiles.py` (образец UniqueViolation-обработки),
      `core/database.py::get_connection`.
- [+] Подтверждено: `countries.slug/iso2/iso3`, `country_proposals.slug`,
      `users.email`, `author_metric_definitions (author_user_id, slug)` —
      все настоящие UNIQUE-констрейнты в БД (гонка реальна, не мнимая).
- [+] Подтверждено эмпирически (AST-скан `api/v1/*.py`): 13 мутирующих
      эндпоинтов не вызывают `connection.commit()` и корректно полагаются на
      неявный commit пула (`ConnectionPool.connection()` коммитит на чистом
      выходе, откатывает на исключении) — П2-9 не баг, а нефиксированная
      конвенция; решение зафиксировано ниже без риска механической правки
      40+ файлов.

## Реализация — P1-1: relay вне длинной транзакции

- [+] Миграция `053_domain_events_in_flight.sql`: колонка `locked_at`,
      расширение `domain_events_status_check` значением `in_flight`.
- [+] `repositories/domain_events.py`: новые
      `lock_and_mark_in_flight_domain_events` (короткая транзакция:
      `SELECT ... FOR UPDATE SKIP LOCKED` + `UPDATE ... SET status =
      'in_flight'`), `requeue_stale_in_flight_domain_events` (восстановление
      «зависших» in_flight после падения процесса).
- [+] `scripts/outbox_relay_runner.py::run_relay`: короткая транзакция на
      lock+mark-in-flight, `publisher.publish()` вне транзакции, отдельная
      короткая транзакция на relayed/failed на каждое событие; dry-run
      переведён на не блокирующий `list_pending_domain_events` (не трогает
      состояние).
- [+] `KafkaPublisher`: явные `message.timeout.ms`/`delivery.timeout.ms`
      вместо дефолтных 300с.
- [+] Обновлены `tests/test_outbox_relay.py` под новые функции репозитория;
      добавлен тест на requeue зависшего `in_flight`.

## Реализация — P1-2: advisory-lock на дневные лимиты

- [+] `services/migration_board/helpers.py`:
      `with_daily_limit_lock(connection, user_id, scope)` —
      `pg_advisory_xact_lock(hashtext(...))`.
- [+] `threads.py::send_thread_message`, `posts.py::create_user_post`,
      `contacts.py::create_contact_request`,
      `reporting.py::_create_report` — count+insert обёрнуты в
      `with connection.transaction():` с предварительным
      `with_daily_limit_lock`.
- [-] Конкурентный тест (threading, N потоков) на лимит сообщений треда —
      частично: написаны unit-тесты, подтверждающие, что lock приобретается
      до count-check в каждой из 4 точек (`tests/
      test_migration_board_concurrency_lock.py`), но НЕ настоящий
      многопоточный тест против реального Postgres — этот тестовый слой
      мокает репозиторий целиком (та же архитектурная граница, что
      зафиксирована как долг в AE-8/P2-7); честно отмечено как ограничение,
      не как «сделано полностью».

## Реализация — P1-3: UniqueViolation вместо 500

- [+] `services/auth.py::register_user` — `create_user`/
      `set_password_credential` обёрнуты в `try/except UniqueViolation` →
      тот же 409 `email_already_registered`.
- [+] `services/country_contribution/proposals.py::create_proposal` —
      транзакционный блок обёрнут в `try/except UniqueViolation`,
      маппинг по имени констрейнта на `country_slug_taken`/
      `country_iso_taken`.
- [+] `services/author_metrics/definitions.py::create_my_definition` —
      `create_definition` обёрнут в `try/except UniqueViolation` → 409
      `author_metric_slug_taken`.
- [+] Тесты: параллельный (двойной) register/create_proposal/
      create_my_definition — ровно один успех, второй — чистый 409, не 500.

## Реализация — P2-9: конвенция коммита

- [+] Решение: пул (`ConnectionPool.connection()`) уже коммитит на чистом
      выходе / откатывает на исключении — это подтверждённый, безопасный
      и неявный контракт `get_connection`. Явные `connection.commit()` в
      40+ роутерах избыточны, но безвредны; 13 существующих эндпоинтов уже
      полагаются только на неявный коммит и работают корректно. Механическая
      правка 40+ файлов ради чисто косметической консистентности — вне
      объёма (не баг, не риск). Решение задокументировано в docstring
      `get_connection` и в финальном отчёте; тест-инвариант не заводится,
      т.к. любой вариант конвенции корректен и запись строгого теста была
      бы произвольной.
- [+] `core/database.py::get_connection` — добавлен docstring,
      фиксирующий контракт явно.

## Тесты

- [+] Полный `py -3.12 -m pytest tests/ -q` зелёный.
- [+] `py -3.12 -m mypy apps scripts tests` чистый.
- [+] `py -3.12 -m ruff check` / `ruff format --check` чистые.
- [+] Полный quality gate (`python dev_tools_scripts_runner.py full-check`)
      зелёный, включая Playwright E2E 283/283 (первый прогон дал один
      flaky-фейл в `web-mvp-decision-passport.spec.ts` — тест не связан ни
      с одним изменением эпизода; повторный прогон подтвердил 283/283
      чисто).

## Завершение

- [+] Чек-лист заполнен `+`/`-`.
- [+] `docs/_arch_/09_План_устранения_аудита.md`: статус AE-4 обновлён.
- [+] Финальный отчёт написан (включая явно обозначенное решение по P2-9).
- [+] Коммит на ветке; merge в `main` и push на `origin/main` — по прямому
      запросу владельца (дан явно после завершения эпизода).
