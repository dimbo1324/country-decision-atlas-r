# Чек-лист задачи: конвейер синтетических данных — Этап 6
# (безопасные SQL-fixtures и изолированная загрузка)

Источник: `docs/synthetic_data/synthetic_data_pipeline_technical_specification.md`,
раздел 23, «Этап 6 — безопасные SQL-fixtures и изолированная загрузка».
Зависимость: Этапы 2–3 (обязательные) и Этап 5 (для полной комплектации) —
уже реализованы и смержены в `main`.

Ветка: `feat/synthetic-data-stage6-sql-fixtures-v1`.

## Подготовка

- [+] Перечитан раздел 23 «Этап 6», раздел 11 (SQL-fixtures и безопасность БД)
      техзадания.
- [+] Живая схема БД сверена напрямую через `information_schema`/
      `pg_constraint` на поднятом локальном Postgres (после
      `scripts/apply_migrations.py`) — миграции с 001 по 055, а не только
      исходная `CREATE TABLE` (схема успела уйти вперёд через `ALTER TABLE`
      в более поздних миграциях).
- [+] Определён минимальный набор таблиц v1: `countries`, `country_profiles`,
      `sources`, `legal_signals`. Явно оставлены вне SQL v1: пользователи/
      авторы/статьи/комментарии/сценарии (нет соответствующих таблиц),
      `country_metric_values`/`cii_metric_definitions` (общий, реальный CII-
      расчёт — фиктивные значения повредили бы методологический инвариант),
      индексация поиска (отдельный существующий dev-tools шаг).

## Состав работ

- [+] Модуль генерации SQL из канонического `SyntheticWorld` без подключения
      к БД (`core/sql_fixture.py`, `psycopg.sql` для безопасного
      экранирования — офлайн, без live connection).
- [+] Идемпотентный `seed_synthetic_world.sql`: `INSERT ... ON CONFLICT ...
      DO UPDATE` по стабильным (детерминированным из `dataset_id`) UUID.
- [+] Отдельный `cleanup_synthetic_world.sql`: удаляет только строки
      известных id этого конкретного датасета, никогда не трогает схему;
      DELETE в порядке, безопасном для FK (legal_signals → sources →
      country_profiles → countries), плюс `AND is_demo = FALSE` guard.
- [+] CLI: `world load-sql --dataset <id> --confirm` и `world cleanup-sql
      --dataset <id> --confirm` — явное подтверждение, блокировка
      `APP_ENV=production` (и unset) до подключения к БД, чтение
      `DATABASE_URL` из окружения или `--database-url`.
- [+] Не изменены, не удалены, не перегенерированы существующие миграции.
- [+] `generate`/`render` теперь также пишут `sql/seed_synthetic_world.sql`
      и `sql/cleanup_synthetic_world.sql` в датасет (раздел 10), включены
      в `manifest.json` и ZIP-пакет.

## Проверка и критерий перехода

- [+] Fixture применяется к чистой локальной тестовой БД после миграций —
      проверено вручную: `docker compose up postgres redis` +
      `scripts/apply_migrations.py` (001..055) + `world load-sql`.
- [+] Повторное применение (тот же `dataset_id`) не создаёт дубликатов —
      повторный `load-sql` на той же БД прошёл без ошибок и без роста
      количества строк.
- [+] Cleanup удаляет только записи нужного `dataset_id`, не трогает
      демо-страны (`is_demo=true`) и другие данные — проверено: countries
      8→3 (ровно демо russia/uruguay/argentina остались), sources/
      legal_signals/country_profiles уменьшились ровно на 5 каждая.
- [+] Попытка запуска при `APP_ENV=production` завершается до подключения
      к БД — проверено и вручную (реальный `--database-url` на
      недостижимый хост, ошибка возникает до сетевого вызова), и тестами.
- [+] Сценарии из Этапа 3 находят созданные SQL-данные по ожидаемым
      идентификаторам (страна по `slug`, источник/сигнал по `title`/`url`,
      привязка через `country_id`) — проверено прямыми SELECT на реальной БД.

## Тесты

- [+] `tests/test_sql_fixture.py` — эскейпинг, детерминированные id,
      структура INSERT/ON CONFLICT/DELETE, порядок DELETE, зарезервированные
      ISO-коды, маркировка, без БД (13 тестов).
- [+] `tests/test_sql_loader.py` — `ensure_not_production()`/
      `execute_sql_file()` отказы (production, unset, missing file), без БД
      (5 тестов).
- [+] `tests/test_world_cli.py` — `load-sql` без `--dataset`/`--confirm`/
      `DATABASE_URL`, блокировка production через CLI (5 новых тестов).
- [-] Автоматический pytest-интеграционный тест против реального Postgres —
      НЕ добавлен; вместо этого — честно задокументированная ручная проверка
      (см. выше) и отступление в техзадании: в проекте нет установленного
      паттерна pytest+живая БД (`pytest tests/` в quality gate проходит до
      подъёма Docker-стека), заводить такую инфраструктуру ради одного
      модуля счёл непропорциональным риском.

## Завершение

- [+] Раздел 23 «Этап 6» техзадания: статус обновлён на «реализовано» с
      честной записью отступлений.
- [+] `python -m mypy scripts/synthetic_data` чистый (82 файла).
- [+] `python -m ruff check`/`ruff format --check` чистые.
- [+] Полный `py -3.12 -m pytest tests/ -q` (весь проект) зелёный.
- [+] Полный quality gate (`python dev_tools_scripts_runner.py full-check`):
      77 OK / 3 WARN (устаревшие локальные кеш-директории, безопасны) /
      1 FAIL / 1 SKIP (protoc, committed .pb.go используются как есть).
      Единственный FAIL — `go test` из-за `-race requires cgo` на этой
      Windows-машине без mingw/gcc — то же заранее задокументированное
      ограничение (`.ai/project/11-commands.md`), не связанное с этой
      задачей: в диффе нет ни одного `.go`-файла. Docker-стек, миграции,
      все runtime/semantic смоуки, Playwright E2E и pre-commit — все
      прошли.
- [+] Финальный отчёт написан.
- [ ] Коммит на ветке. Merge в `main` и push на `origin/main` — только
      после отдельного явного подтверждения владельца.
