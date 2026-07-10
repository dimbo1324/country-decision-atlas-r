# Чек-лист задачи: Аудит-эпизод 8 — CI/CD и тестовый контур (P2-6, P2-7, P1-9)

Ветка: `fix/ci-testing-hardening-v1` (от `main`).

## 1. Подготовка

```text
[+] Прочитан docs/_arch_/09_План_устранения_аудита.md, раздел АЕ-8
[+] Решение владельца по P1-9 получено (08_Открытые_вопросы.md, Р-11):
    механическая часть сейчас, вариант А для P1-9 — после Этапа 6
    scripts/synthetic_data/ (см. связь в §21 спецификации пайплайна)
[+] Изучены apps/api/app/repositories/auth.py, capabilities.py,
    country_contribution/proposals.py, countries.py для интеграционного
    слоя
```

## 2. P2-6 — race, аудит зависимостей, coverage

```text
[+] go test -race ./... в .github/workflows/quality.yml (notifier job) и
    scripts/dev_tools/full_check.py
[+] pip-audit (backend), pnpm audit --prod (frontend), govulncheck
    (notifier) — все три continue-on-error: true (allow-fail на старте)
[+] pip-audit добавлен в pyproject.toml [project.optional-dependencies].dev
[+] Локальный прогон pip-audit: нашёл 2 известные уязвимости в
    sqlfluff 3.5.0 (PYSEC-2026-209/210, dev-only lint-тул, не рантайм) —
    зафиксировано в статусе эпизода, не исправляется в рамках этого
    эпизода (allow-fail — точка триажа, не автофикса)
[+] pytest --cov=apps/api/app/services --cov=apps/api/app/repositories
    --cov-report=xml --cov-report=term-missing в backend-джобе +
    upload-artifact для coverage.xml
[+] [tool.coverage.run]/[tool.coverage.report] в pyproject.toml,
    fail_under = 70 (замер на момент эпизода — 79.10%)
```

## 3. P2-7 — repository-тесты против реального Postgres

```text
[+] tests/repository/conftest.py: connection-фикстура, пропуск через
    RUN_REPOSITORY_INTEGRATION_TESTS != "1" (паттерн
    RUN_RUNTIME_SMOKE_TESTS из tests/smoke/, но в фикстуре, не
    module-level pytestmark — пакет из нескольких файлов)
[+] test_auth_sessions_repository.py — AE-1 JOIN-запрос
    get_session_with_user_by_token_hash (7 тестов: свежий токен,
    неизвестный, отозванная сессия, истёкшая, ротация, grace-period
    по previous_token_hash в обе стороны)
[+] test_capabilities_repository.py — grant/revoke/list (9 тестов,
    включая ON CONFLICT DO UPDATE реактивацию отозванного гранта)
[+] test_country_proposal_transitions_repository.py —
    apply_status_transition optimistic-concurrency guard, published_at
    CASE WHEN, assign_curator once-only guard (9 тестов)
[+] test_countries_list_filters_repository.py — is_active/is_demo
    фильтр на синтетических страна́х (4 теста)
[+] Итого 29 тестов — в диапазоне 20-40 из плана
[+] Подключено в .github/workflows/quality.yml integration-джобе после
    Runtime smoke tests
[-] НЕ подключено в локальный dev_tools_scripts_runner.py --profile full
    (Docker-фаза 5) — api-контейнер не содержит tests/ и dev-зависимости
    (осознанно, чтобы не раздувать прод-образ); честно зафиксировано как
    известное ограничение в статусе эпизода вместе с ручной командой
[+] Реальный прогон против живого Postgres выполнен локально (docker
    compose up -d postgres, порт 5433, apply_migrations.py, затем
    RUN_REPOSITORY_INTEGRATION_TESTS=1 pytest tests/repository/ -v) —
    все 29 зелёные; нашёл и исправил 2 реальных бага в самих тестах
    (moderated_by/curator_user_id сравнивались как str с UUID-объектом —
    PROPOSAL_FIELDS их не кастует в ::text, в отличие от auth.py/
    capabilities.py); повторный прогон подтвердил отсутствие остатков
    между запусками (rollback-изоляция работает)
```

## 4. P1-9 — вариант Б (интерим)

```text
[+] --visible в restore_demo_countries.py остаётся как есть (уже был
    задокументирован в предыдущем эпизоде)
[+] Гарантия скрытости демо по умолчанию — на двух уровнях:
    (1) существующий mock-тест default_uses_fixture_upsert_not_update
    (2) новый repository-тест на реальном is_demo-инварианте
[+] docs/_arch_/08_Открытые_вопросы.md: Р-11 — зафиксирован workaround
    (почему/где/когда заменить), ссылка на синтетический пайплайн
[+] docs/synthetic_data/synthetic_data_pipeline_technical_specification.md
    §21: добавлена связь с P1-9/Р-11 перед пунктами 3-4
```

## 5. Документация и завершение

```text
[+] docs/_arch_/09_План_устранения_аудита.md: статус АЕ-8 заполнен,
    таблица §1 и карта зависимостей обновлены
[+] pytest tests/repository/ -v — 29 тестов, корректно skipped без БД;
    отдельно прогнаны и против реального Postgres (см. выше) — все зелёные
[+] ruff check / ruff format --check / mypy — чисто на все затронутые
    файлы
[+] pytest (весь репозиторий) — зелёный, coverage-порог пройден (79.10%)
[+] python dev_tools_scripts_runner.py full-check — OK 77, WARN 3 (стухшие
    кеш-директории, безвредно, не связано с этим эпизодом), FAIL 1
    (go test — notifier), SKIP 1 (protoc)
[-] go test -race ./... (notifier) падает локально на этой Windows-машине:
    "go: -race requires cgo; enable cgo by setting CGO_ENABLED=1" —
    CGO_ENABLED=0, C-тулчейн не настроен на этой машине. Не код-регрессия:
    go vet чист, TELEGRAM_MODE=fake go test ./... (без -race) зелёный на
    всех пакетах. GitHub Actions ubuntu-latest имеет gcc из коробки — там
    -race отработает штатно; реальная проверка -race в этом эпизоде —
    CI-джоба notifier, не эта локальная машина. Осознанно не отключаю
    -race и не оборачиваю его CGO-детектом — это ослабило бы саму находку
    P2-6, которую эпизод должен закрыть
[+] .ai/project/11-commands.md: команда go test обновлена под -race +
    заметка про локальный CGO-гэп; AGENTS.md перегенерирован
    (sync-agents)
[ ] Коммит на branch fix/ci-testing-hardening-v1
[ ] ff-merge в main, push
[ ] Финальный отчёт с честной пометкой про локальное CGO-ограничение
```
