# Чек-лист задачи: Аудит-эпизод 7 — наблюдаемость (P2-1)

Ветка: `fix/observability-v1` (от `main`).

## 1. Подготовка

```text
[+] Прочитан docs/_arch_/09_План_устранения_аудита.md, раздел АЕ-7
[+] Изучены main.py (logging.basicConfig), bootstrap/app_factory.py
    (middleware/системные роуты), core/request_context.py, core/database.py
    (get_pool_stats уже есть из AE-6)
```

## 2. RequestIDMiddleware + JSON-логи

```text
[+] core/request_context.py: contextvar _request_id_var +
    bind_request_id/reset_request_id/get_request_id (возвращает "-" вне
    запроса, никогда не бросает)
[+] core/logging_config.py: JsonLogFormatter (level, timestamp, component,
    message, request_id, exception при наличии) + configure_logging() —
    обычный logging.Formatter, без новой зависимости
[+] main.py: logging.basicConfig(...) заменён на configure_logging()
[+] bootstrap/app_factory.py: request_id_middleware зарегистрирован ПЕРВЫМ
    в _register_middleware (Starlette оборачивает LIFO — первый
    зарегистрированный оказывается самым внешним слоем), поэтому оборачивает
    security_headers/csrf/rate_limit — X-Request-ID переживает даже ранний
    403/429 от внутреннего middleware. Эхо входящего X-Request-ID, если
    клиент уже его передал, иначе — новый uuid4()
```

## 3. /metrics

```text
[+] services/metrics.py: request_count по status code, latency-гистограмма
    (9 бакетов), db_pool_connections из AE-6 get_pool_stats() — ручной
    Prometheus text exposition format, без prometheus-client (обоснование:
    ~30 строк учёта счётчиков не оправдывают новую зависимость; сам формат
    простой и стабильно документированный, roll-your-own безопасен)
[+] metrics_middleware в app_factory.py — считает статус+латентность КАЖДОГО
    запроса (второй зарегистрирован, тоже вне security/csrf/rate_limit)
[+] /metrics зарегистрирован как системный роут (как /health, /ready) —
    без аутентификации, тот же принцип, что и у остальных системных
    эндпоинтов; добавлен в исключения rate_limit_middleware (иначе Prometheus-
    скрейпер сам себя может зарейтлимитить)
[+] reset_metrics() — test-only сброс между тестами
```

## 4. pg_stat_statements (dev)

```text
[+] docker-compose.yml: postgres.command добавляет
    shared_preload_libraries=pg_stat_statements +
    pg_stat_statements.track=all/.max=5000 — только dev-compose, не
    docker-compose.prod.yml (по формулировке плана: "добавить в
    docker-compose.yml (dev)"), не мигрция (CREATE EXTENSION в миграции
    сломал бы CI — там простой postgres:16-alpine без preload-override,
    и GitHub Actions services: не поддерживает command-override того же
    рода)
[+] Живая проверка: docker compose up postgres → SHOW
    shared_preload_libraries → CREATE EXTENSION IF NOT EXISTS
    pg_stat_statements → SELECT count(*) FROM pg_stat_statements — все три
    прошли, 25 строк уже накоплено на чистом старте
[+] .ai/project/11-commands.md: новый раздел «Postgres observability (dev)»
    — команда CREATE EXTENSION (разовая, вручную) + top-N по
    total_exec_time
[+] AGENTS.md перегенерирован (python dev_tools_scripts_runner.py
    sync-agents) — модуль .ai/ правился вручную, файл сгенерирован заново
```

## 5. Контракт и тесты

```text
[+] contracts/openapi.yaml: добавлен путь /metrics — найдено тестом
    test_committed_openapi_matches_runtime_paths_and_schemas
    (tests/test_full_audit_stabilization.py), который сверяет закоммиченный
    openapi.yaml С РАНТАЙМ-схемой приложения побайтово; точная схема взята
    прямым вызовом app.openapi() вместо ручного угадывания формата
[+] pnpm contracts:generate — types.ts перегенерирован
[+] tests/test_observability.py (11 тестов): реальный create_app() +
    TestClient (не голый FastAPI() — критерии приёмки требуют проверки
    самого middleware-стека, а не только роутера) —
    X-Request-ID генерируется и уникален на каждый запрос; входящий
    X-Request-ID эхается, не заменяется; contextvar round-trip;
    JsonLogFormatter даёт валидный JSON с ожидаемыми ключами (включая
    exception при наличии); /metrics отдаёт 200 text/plain с ожидаемыми
    именами метрик; /metrics освобождён от rate-limit; reset_metrics()
    чистит состояние
```

## 6. Проверка

```text
[+] pytest tests/ — все тесты зелёные (включая новые 11 + починенный
    test_full_audit_stabilization.py)
[+] ruff check / ruff format --check / mypy — чисто
[+] pnpm quality (format/lint/typecheck/build) — чисто
[+] docker compose config — валиден
[+] python dev_tools_scripts_runner.py --profile full — OK 78, WARN 3
    (стухшие кеш-директории .pytest_cache/.mypy_cache/.ruff_cache,
    безвредно, не связано с этим эпизодом), FAIL 0, SKIP 1 (protoc)
```

## 7. Документация и завершение

```text
[+] docs/_arch_/09_План_устранения_аудита.md: статус АЕ-7 заполнен
[+] Коммит на branch fix/observability-v1
[+] ff-merge в main, push
[+] Финальный отчёт
```
