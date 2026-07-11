# Чек-лист задачи: конвейер синтетических данных — эргономика CLI
# (11 небольших улучшений поверх Этапов 1-6, перед Этапом 7)

Источник: собственный аудит `scripts/synthetic_data` по запросу владельца
(не связан напрямую с одним разделом техзадания; ссылки на разделы даны
по месту). Все пункты — аддитивные, не меняющие поведение по умолчанию
там, где это возможно (профиль `balanced` и все существующие флаги должны
остаться такими же).

Ветка: `feat/synthetic-data-cli-ergonomics-v1`.

## Состав работ (11 пунктов)

- [+] 1. Ленивые импорты в `cli.py`: `validate`/`plan`/`list`/`prune`/
      `schema` не тянут reportlab/docx/openpyxl/psycopg —
      `core/document_formats.py` (лёгкий модуль для `ALL_DOCUMENT_FORMATS`),
      `dataset_packager`/`artifact_validation` импортируются лениво только
      внутри `generate`/`render`/`package`.
- [+] 2. `--dry-run` для `load-sql`/`cleanup-sql`: печатает цель (хост/БД,
      путь к файлу), не подключаясь; production-guard проверяется и
      отражается в превью (`blocked_by_production_guard`).
- [+] 3. Команда `list`: обход `--output-root`, вывод dataset_id/seed/
      profile/generated_on/country_count/размера по каждому датасету.
- [+] 4. Команда `package --dataset <id>`: `discover_existing_documents`
      восстанавливает `GeneratedDocument` по файлам на диске (без
      рендеринга), пересобирает manifest+ZIP.
- [+] 5. `tests/test_no_network_imports.py`: запрет `import requests/httpx/
      urllib.request/socket/aiohttp`; отдельная проверка, что `psycopg`
      используется только в `sql_fixture.py`/`sql_loader.py`.
- [+] 6. Команда `prune --keep-last N [--confirm] [--dry-run]`
      (`core/dataset_prune.py`): сортировка по mtime манифеста, удаляет
      только датасеты сверх `--keep-last`.
- [+] 7. Реальная дифференциация профилей (`world_generator._draw_metric`,
      `content_generator.py`): `moderation` — 5 комментариев вместо 3;
      `data_quality` — `data_confidence` смещён к нижней половине диапазона
      архетипа; `crisis` — 90% вероятность отрицательного направления
      (кроме `recovering_country`); `optimistic` — метрики смещены к
      верхней трети диапазона архетипа. `balanced` — побайтово не изменился
      (проверено `git stash`-сравнением до/после и закреплено тестом).
- [+] 8. `core/dataset_discovery.py`: `find_dataset_dir`/
      `available_dataset_ids` — автопоиск по `DEFAULT_OUTPUT_DATA_ROOT`,
      понятная ошибка со списком известных id при неудаче.
- [+] 9. `scripts/synthetic_data/README.md` — quickstart: генерация,
      просмотр (`list`/manifest), загрузка в локальную БД и очистка.
- [+] 10. Команда `schema`: печатает
      `SyntheticWorld.model_json_schema()` в stdout.
- [+] 11. Флаги `--json`/`--quiet` (класс `_Report` в `cli.py`) для всех
      world-команд: `--json` — один структурированный JSON-объект;
      `--quiet` — подавляет обычный текстовый вывод (ошибки — в stderr).

## Проверка

- [+] Профиль `balanced` при фиксированном seed (`42017`) даёт побайтово
      тот же мир, что и до этой задачи — сравнено вручную (`git stash` +
      генерация до/после дала идентичный JSON) и закреплено регресс-тестом
      `test_balanced_profile_world_is_unchanged_across_this_change`.
- [+] `validate`/`plan`/`list`/`prune`/`schema` работают без
      `reportlab`/`python-docx`/`openpyxl`/`psycopg` — подтверждено
      статически: `test_importing_cli_does_not_pull_in_heavy_rendering_or_db_libraries`
      импортирует `cli.py` в чистом подпроцессе и проверяет `sys.modules`.
- [+] `list`, `package`, `prune`, `schema` покрыты тестами (в
      `test_world_cli.py`, `test_dataset_discovery.py`, `test_dataset_prune.py`).
- [+] `--json`/`--quiet` дают валидный, разбираемый вывод — проверено для
      `generate` (`--json`, парсится как JSON) и `plan` (`--quiet`, пустой
      stdout).
- [+] Grep-тест на `import requests` — вручную подтверждено: временная
      вставка строки в `manifest.py` валит тест с точным сообщением о
      файле/строке, откат правки возвращает тест в зелёное состояние.

## Завершение

- [+] `python -m mypy scripts/synthetic_data` чистый (89 файлов).
- [+] `python -m ruff check`/`ruff format --check` чистые.
- [+] Полный `py -3.12 -m pytest tests/ -q` (весь проект) зелёный.
- [+] Полный quality gate (`python dev_tools_scripts_runner.py full-check`)
      зелёный (кроме заранее задокументированного `go test -race`
      Windows/cgo-ограничения, не связанного с этой задачей — в диффе нет
      ни одного `.go`-файла).
- [+] `docs/synthetic_data/synthetic_data_pipeline_technical_specification.md`
      не потребовал изменений: раздел 12 уже описывал именно эту целевую
      CLI-поверхность (`package --dataset <id>`, `--dry-run`, «`validate`
      без тяжёлых библиотек») как нереализованную цель — эта задача её
      выполнила, а не переопределила.
- [+] Финальный отчёт написан.
- [ ] Коммит на ветке. Merge в `main` и push на `origin/main` — только
      после отдельного явного подтверждения владельца.
