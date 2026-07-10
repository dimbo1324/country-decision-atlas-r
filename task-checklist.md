# Чек-лист задачи: Аудит-эпизод 5 — жизненный цикл данных (P1-4, P1-7, P1-5, P2-13, P2-3)

Ветка: `fix/data-lifecycle-v1` (от `main`). Работа была начата в предыдущей
сессии и оставлена в незакоммиченном виде (реализация написана, но часть
тестов падала, контракт был рассинхронизирован, фронтенд не собирался).
Эта задача — довести её до состояния "всё работает, все тесты зелёные".

## 1. Разведка

```text
[+] Прочитан docs/_arch_/audit_result.txt (P1-4, P1-7, P1-5, P2-13, P2-3)
[+] Прочитан docs/_arch_/09_План_устранения_аудита.md, раздел АЕ-5
[+] Изучено незакоммиченное состояние ветки: 4 новых модуля
    (repositories/retention.py, services/retention.py,
    services/search_index.py, services/admin_recompute.py), 2 новые
    миграции (054, 055), новый scripts/cleanup_retention.py, правки в
    ~25 существующих файлах
```

## 2. Бизнес-логика — проверка и достройка

```text
[+] P1-4 (retention): cleanup_retention.py, repository/service retention —
    проверены, работают корректно, зарегистрированы в
    dev_tools_scripts_runner.py (пункт 8)
[+] P1-7 (search sync в publish-потоке): admin_content.py — проверено,
    работает; обнаружен и закрыт пробел — services/routes.py::
    change_route_status (публикация/снятие маршрута) не был подключён к
    search_index, хотя "route" — индексируемая сущность с реальным
    admin-путём; добавлен _sync_route_index по образцу
    _sync_legal_signal_index
[+] Подтверждено, что route_checklist_item/country_pair_compatibility/
    methodology/glossary_term не имеют admin-пути записи (сид-контент) —
    rebuild-скрипт для них осознанно остаётся единственным источником
[+] P1-5 (кеш-синглтон): get_cache_backend()/reset_cache_backend() —
    проверено, работает
[+] P2-13 (notifier allow-list): NOTIFIER_ALLOWED_COUNTRIES убран из
    config.go/docker-compose.yml — доубрано из .env.example и
    config_test.go (были пропущены)
[+] P2-3 (async admin recompute): enqueue_recompute_request +
    AdminRecomputeQueuedResponse (202) для trust/platform-metrics/
    country-drift recompute-all — проверено, работает
```

## 3. Исправление незавершённых мест

```text
[+] tests/test_admin_content_publication_flow.py: 5 из 13 тестов падали
    (не хватало стабов insert_audit_event/insert_domain_event, у фикстуры
    country_profile_row отсутствовал country_id) — исправлено
[+] tests/test_trust_api.py, test_platform_metrics_api.py,
    test_country_drift_admin_api.py: ещё проверяли старый синхронный
    контракт (200 + сводка) — переписаны под 202 + enqueue_recompute_request
[+] contracts/openapi.yaml: AdminRecomputeQueuedResponse не содержал
    description (докстринг класса не был перенесён в контракт) —
    добавлено; докстринг в schemas/common.py укорочен и очищен от
    внутреннего аудит-жаргона (он становится публичным API description)
[+] packages/contracts/generated/types.ts: перегенерирован
    (pnpm contracts:generate), потребовалась pnpm install (node_modules
    отсутствовал)
[+] scripts/routes.py: добавлен _sync_route_index + правки
    tests/test_routes_service.py (fixture + 2 новых теста)
[+] .env.example, apps/notifier/internal/config/config_test.go: доубраны
    оставшиеся упоминания NOTIFIER_ALLOWED_COUNTRIES
[+] ruff/mypy: import-порядок и форматирование в затронутых файлах,
    один mypy no_implicit_reexport фикс в rebuild_search_index.py
```

## 4. Проверка

```text
[+] python -m pytest tests/ -q — все тесты зелёные
[+] python -m ruff check / ruff format --check — чисто
[+] python -m mypy apps packages scripts tests — чисто (604 файла)
[+] python -m sqlfluff lint database/migrations/054_*.sql 055_*.sql —
    чисто
[+] cd apps/notifier && go vet ./... && go test -count=1 ./... — чисто
[+] pnpm --filter web typecheck / lint — чисто
[+] python dev_tools_scripts_runner.py --profile full — OK 78, WARN 3
    (только стухший .pytest_cache/.mypy_cache/.ruff_cache — безвредно),
    FAIL 0, SKIP 1 (protoc, ожидаемо); Playwright E2E 283/283
```

## 5. Документация

```text
[+] docs/_arch_/09_План_устранения_аудита.md: Статус АЕ-5 заполнен
    (реализовано), карта зависимостей обновлена
[+] docs/_arch_/01_Продукт/02_Текущее_состояние_системы.md: раздел 3.4
    обновлён (search — incremental sync + rebuild, добавлен Retention)
[-] Тех-долг зафиксирован в финальном отчёте, не исправлялся в этом
    эпизоде: rebuild_search_index.py всегда пишет body="" (не менялось
    этим эпизодом), тогда как инкрементальный country_profile sync пишет
    реальный body — расхождение после полного rebuild; отдельный
    Playwright/smoke E2E на "publish → сразу видно в /search" не добавлен
    (нет admin-панели публикации в текущем фронтенде для его вождения)
```

## 6. Завершение

```text
[+] Коммит с итоговым состоянием (одна ветка `fix/data-lifecycle-v1`, без
    коммитов на момент старта этой задачи — весь эпизод оформлен одним
    коммитом, по образцу АЕ-1..АЕ-4)
[+] Финальный отчёт
[-] Слияние в main / push — не выполнялось: явного запроса владельца на
    публикацию в рамках этой задачи не было
```
