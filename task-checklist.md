# Чек-лист задачи: `fix/demo-country-fresh-db-visibility`

Цель: починить регресс, унаследованный от Эпизода 5 (`feat/country-contribution-v1`,
коммит `a9569f1`, уже в `main`). После скрытия демо-стран (`is_demo = FALSE`
во всех паблик-ридерах) свежая БД (CI/новый Docker/новая dev-машина) не
показывает НИ ОДНОЙ страны публично — единственные страны в базовых
сид-миграциях (russia/uruguay/argentina) как раз демо. Экспорт фикстур
(`export_demo_countries.py` → `database/fixtures/demo_countries/*.json`),
обещанный чек-листом Эпизода 5, так и не был прогнан. Обнаружено при полном
Docker-гейте (`full-check-reports/20260708-105319/`): `GET /countries` = 0,
`GET /countries/{russia,uruguay,argentina}/trust` = 404, ~123 упавших
Playwright E2E. Подтверждено: этот разрыв не связан с Эпизодом 6
(`git diff main feat/migration-flows-v1 -- .../countries.py` — пустой).

## 0. Решение владельца

```text
[+] Выбран вариант «тестовая видимость демо-набора»: демо-страны остаются
    скрытыми на паблик-поверхностях по умолчанию (инвариант Эпизода 5,
    решение Р-1, не пересматривается); для CI/dev/full-gate-прогона на
    свежей БД добавляется отдельный режим восстановления с is_demo=FALSE,
    специально для того, чтобы smoke-проверки и E2E продолжили видеть
    контент без переписывания ~123 тестов и smoke-эндпоинтов.
```

## 1. Экспорт демо-фикстур

```text
[+] scripts/dev_tools/export_demo_countries.py прогнан против реально
    заполненной Postgres (тот же контейнер, что поднял предыдущий полный
    гейт) — напрямую с хоста через маппированный порт (5433), т.к.
    api-контейнер запускается non-root и не может писать в
    /app/database (COPY-слой образа, не volume) — поэтому экспорт из
    контейнера был невозможен, а с хоста сработал сразу
[+] database/fixtures/demo_countries/*.json закоммичены (20 таблиц: countries,
    translations, country_profiles, country_cards, sources, evidence_items,
    legal_signals, legal_signal_events, country_metric_values,
    country_cii_scores, country_scores(+breakdowns), routes(+documents/
    sources/evidence/checklist_items), country_pair_compatibility(+sources/
    evidence))
```

## 2. Код

```text
[+] scripts/dev_tools/restore_demo_countries.py — новый флаг --visible:
    при восстановлении таблицы countries построчно переопределяет
    is_demo=False (только для этой таблицы, остальные 19 — без изменений).
    Без флага поведение прежнее (is_demo сохраняется как в фикстуре, т.е.
    True) — обычный dev-restore не трогается
[+] scripts/dev_tools/full_check.py — новый шаг в Docker-бутстрапе между
    bootstrap_runtime_read_models.py и rebuild_search_index.py --all:
    `docker compose exec -T api python scripts/dev_tools/
    restore_demo_countries.py --visible`
```

## 3. Тесты

```text
[+] tests/test_restore_demo_countries_script.py — 2 новых теста:
    --visible переопределяет is_demo на False только для countries;
    без флага is_demo остаётся как в фикстуре (True) — оба через
    monkeypatch на _load_rows/_upsert_table, без реальной БД
[+] Полный набор тестов репозитория — 2013 passed, 29 skipped (2011 + 2
    новых; эта ветка срезана от main, без 50 тестов Эпизода 6)
```

## 4. Ручная проверка на реальном Docker-стеке

```text
[+] docker compose up --build -d api — пересобран образ с новым кодом
    и фикстурами (COPY-слой подхватывает scripts/ и database/ с диска)
[+] docker compose exec -T api python scripts/dev_tools/
    restore_demo_countries.py --visible — восстановлено, is_demo=False
[+] GET /api/v1/countries?locale=ru — теперь возвращает 3 страны
    (было 0)
[+] GET /api/v1/countries/russia/trust?locale=ru — теперь 200 (было 404)
[+] rebuild_search_index.py --all + GET /api/v1/search?q=residence —
    возвращает результаты (20 документов)
[-] Полный снос volume (`docker compose down -v`) для проверки на
    ПОЛНОСТЬЮ чистой БД с нуля — НЕ выполнялся: заблокировано явным
    deny-правилом пользователя на удаление Docker volume. Проверено на
    уже заполненной БД того же контейнера (то же самое семантически:
    restore --visible флипает is_demo и наполняет ровно те же таблицы,
    которые были бы пусты на реально чистой БД) — считаю равнозначной,
    но не идентичной проверкой; итоговое подтверждение "от абсолютно
    нуля" — за владельцем, если требуется дополнительная строгость
```

## 5. Проверка качества

```text
[+] python -m ruff check apps packages scripts tests — чисто
[+] python -m mypy apps packages scripts tests — чисто, 571 файл
[+] python -m pytest — 2013 passed, 29 skipped
[-] Полный python dev_tools_scripts_runner.py (Docker-гейт целиком,
    с нуля) — НЕ перезапущен целиком в рамках этой задачи (см. §4);
    ключевые смоуки, которые он проверяет, подтверждены вручную выше
```

## 6. Завершение

```text
[+] Чек-лист заполнен +/-
[+] Финальный отчёт
[-] Merge в main — по прямому указанию владельца НЕ выполняется в этой
    задаче; работаем дальше в этой ветке (fix/demo-country-fresh-db-
    visibility), коммит и push сделаны
```
