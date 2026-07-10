# Чек-лист задачи: Аудит-эпизод 6 — прод-готовность и секреты (P1-10, P2-10, P2-4)

Ветка: `fix/prod-readiness-v1` (от `main`).

## 1. Подготовка

```text
[+] Прочитан docs/_arch_/audit_result.txt (P1-10, P2-10, P2-4)
[+] Прочитан docs/_arch_/09_План_устранения_аудита.md, раздел АЕ-6
[+] Изучены core/config.py, core/database.py, docker-compose.yml, .env.example
[+] Обнаружен скрытый конфликт: Settings.app_env по умолчанию = "production"
    (не "local"), а pytest (локально и в CI) не выставляет APP_ENV вовсе —
    наивная реализация fail-fast сломала бы весь тестовый набор
```

## 2. P1-10 — fail-fast на дефолтные секреты

```text
[+] model_validator(mode="after") в Settings: RuntimeError при
    app_env=="production" и (database_url содержит change-me ИЛИ
    analytics_salt == дефолт ИЛИ notifier_internal_auth_token in
    (None, "dev-grpc-token"))
[+] tests/conftest.py: APP_ENV=local по умолчанию для тестового процесса
[+] Тесты (tests/test_config.py, 9 шт.): production+дефолты -> RuntimeError
    (по каждому полю отдельно + все три сразу); local+дефолты -> не падает;
    production+реальные значения -> не падает; "staging" не по инвертированной
    логике feature_flags.py — валидация пропущена намеренно
```

## 3. P2-4 — настраиваемый пул БД

```text
[+] database_pool_min_size/max_size/timeout_seconds в Settings (дефолты
    1/10/30.0 — совпадают со старыми хардкод-значениями, поведение без
    явной конфигурации не меняется)
[+] open_database_pool использует эти настройки
[+] get_pool_stats() — обёртка над ConnectionPool.get_stats(), для
    будущего /metrics (AE-7)
[+] Тесты (tests/test_database.py, 7 шт.): sizing из Settings, дефолты,
    идемпотентность open, close сбрасывает пул, get_pool_stats делегирует
    и падает RuntimeError без инициализации
```

## 4. P2-10 — прод-оверлей compose + бэкапы

```text
[+] docker-compose.prod.yml: restart: unless-stopped везде, Redis
    requirepass, Mongo auth, порты Redis/Mongo убраны через YAML !reset [],
    mem_limit везде + cpus на api/redpanda
[+] .env.example: новые prod-only переменные (REDIS_PASSWORD,
    MONGO_ROOT_USERNAME/_PASSWORD — обязательные; *_MEM_LIMIT/*_CPUS —
    опциональные с дефолтами)
[+] scripts/backup_postgres.py (pg_dump через docker compose exec,
    cron-совместимый, --dry-run)
[+] scripts/restore_postgres_check.py (восстановление в scratch-контейнер
    + проверка schema_migrations; POSTGRES_USER передаётся в scratch-
    контейнер — иначе restore падает на "role does not exist" из-за
    OWNER TO/GRANT в дампе, найдено реальным прогоном)
[+] Регистрация обоих в dev_tools_scripts_runner.py (пункты 9-10)
[+] Тесты (test_backup_postgres.py 6 шт. + test_restore_postgres_check.py
    13 шт.): конструирование команд, --dry-run, реальный успех/провал
    через mocked subprocess, поллинг готовности с таймаутом, останов
    scratch-контейнера даже при падении restore
[+] .gitignore: добавлен backups/ (dump-файлы не должны коммититься)
```

## 5. Проверка

```text
[+] python -m pytest tests/ -q — все тесты зелёные (после починки
    tests/test_health.py: environment в /health больше не хардкод
    "production")
[+] ruff check / ruff format --check / mypy / sqlfluff — чисто
[+] docker compose -f docker-compose.yml -f docker-compose.prod.yml config
    — валиден с фиктивными REDIS_PASSWORD/MONGO_ROOT_USERNAME/_PASSWORD;
    без них падает с понятной ошибкой (:? fail-fast) — так и задумано
[+] backup_postgres.py --dry-run — smoke
[+] backup_postgres.py реальный прогон на локальном dev-стеке — дамп
    1024211 байт
[+] restore_postgres_check.py реальный прогон — после фикса с
    POSTGRES_USER: schema_migrations_count=55, контейнер удалён
[+] python dev_tools_scripts_runner.py --profile full — первая попытка
    провалилась на Playwright E2E (см. раздел 6), вторая попытка: OK 78,
    WARN 4 (стухшие кеш-директории, безвредно), FAIL 0, SKIP 1 (protoc)
```

## 6. Найденные и исправленные отклонения от наброска

```text
[+] CI-ломающий баг: pnpm runtime:bootstrap (bootstrap_runtime_read_
    models.py) запускается на хосте без APP_ENV — получил
    os.environ.setdefault("APP_ENV", "local") на уровне модуля (нет
    правдоподобного сценария реального прод-запуска этого конкретного
    скрипта вручную)
[+] Тот же паттерн ещё в 4 шагах .github/workflows/quality.yml
    (bootstrap runtime read models, restore demo visibility, rebuild
    search index, bootstrap owner account) — исправлено добавлением
    APP_ENV: local в env: этих шагов (не трогая сами скрипты
    create_auth_user.py/rebuild_search_index.py — у них есть
    правдоподобный сценарий реального прод-запуска админом, где
    строгая проверка обязана срабатывать)
[+] Остальные 7 скриптов, трогающих Settings (cleanup_retention.py,
    dispatch_trip_reminders.py, recompute_*.py,
    export_demo_countries.py) нигде не вызываются автоматически —
    оставлены строгими намеренно
[-] Обнаружен orphaned scripts/cleanup_expired_auth_sessions.py (не
    зарегистрирован нигде, вероятно вытеснен cleanup_retention.py из
    АЕ-5) — не тронут, зафиксирован как техдолг для АЕ-10
```

## 7. Документация и завершение

```text
[+] docs/_arch_/09_План_устранения_аудита.md: статус АЕ-6 заполнен,
    карта зависимостей обновлена
[+] Коммит
[+] Финальный отчёт
```
