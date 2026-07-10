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
[ ] model_validator(mode="after") в Settings: RuntimeError при
    app_env=="production" и (database_url содержит change-me ИЛИ
    analytics_salt == дефолт ИЛИ notifier_internal_auth_token in
    (None, "dev-grpc-token"))
[ ] tests/conftest.py: APP_ENV=local по умолчанию для тестового процесса
    (не трогает CI/Docker — там APP_ENV уже задаётся явно/через
    docker-compose default)
[ ] Тесты: production+дефолты -> RuntimeError; local+дефолты -> не падает;
    production+реальные значения -> не падает
```

## 3. P2-4 — настраиваемый пул БД

```text
[ ] database_pool_min_size/max_size/timeout_seconds в Settings (текущие
    значения как дефолт)
[ ] open_database_pool использует эти настройки
[ ] get_pool_stats() — обёртка над ConnectionPool.get_stats(), для
    будущего /metrics (AE-7)
[ ] Тесты на конфигурацию пула и get_pool_stats
```

## 4. P2-10 — прод-оверлей compose + бэкапы

```text
[ ] docker-compose.prod.yml: restart: unless-stopped везде, Redis
    requirepass, Mongo auth, порты Redis/Mongo не публикуются, mem_limit/
    cpus хотя бы для api/redpanda
[ ] .env.example: новые prod-only переменные задокументированы
[ ] scripts/backup_postgres.py (pg_dump, cron-совместимый, --dry-run)
[ ] scripts/restore_postgres_check.py (восстановление в scratch-контейнер
    + проверка целостности)
[ ] Регистрация обоих в dev_tools_scripts_runner.py
[ ] Тесты на конструирование команд и --dry-run (mocked subprocess)
```

## 5. Проверка

```text
[ ] python -m pytest tests/ -q
[ ] ruff check / ruff format --check / mypy / sqlfluff
[ ] docker compose -f docker-compose.yml -f docker-compose.prod.yml config
    — валиден
[ ] backup_postgres.py --dry-run — smoke
[ ] restore_postgres_check.py — smoke на локальном dev-стеке
[ ] python dev_tools_scripts_runner.py --profile full
```

## 6. Документация и завершение

```text
[ ] docs/_arch_/09_План_устранения_аудита.md: статус АЕ-6
[ ] Коммит
[ ] Финальный отчёт
```
