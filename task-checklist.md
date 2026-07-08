# Чек-лист задачи: `feat/synthetic-data-generator-app`

Цель: отдельное, автономное Python-приложение в `scripts/synthetic_data/`,
генерирующее файлы-заглушки (PDF в двух видах, DOCX смешанный, XLSX,
Markdown, JSON) со случайным контентом, не связанным с доменом проекта.
Результаты кладутся в `docs/synthetic_data/` (гитигнорируется), рассортированы
по типу. Заложена (но не подключена) основа для .zip-архивации. На этом этапе
**без** привязки к `dev_tools_scripts_runner.py` — только фундамент под неё.

## 0. Подготовка

```text
[+] Ветка feat/synthetic-data-generator-app создана от актуального main
[+] Чек-лист закоммичен и запушен до основной работы
```

## 1. Зависимости

```text
[+] pyproject.toml: новая extras-группа synthetic-data (reportlab, Pillow,
    python-docx, openpyxl, pypdf)
[+] mypy overrides (ignore_missing_imports) для reportlab(.*), docx(.*),
    openpyxl(.*), PIL(.*) — по образцу существующих grpc/grpc.* и т.п.
[+] Зависимости установлены локально в тот же интерпретатор Python 3.12,
    что использует проект (C:\...\Python312\python.exe, без venv — так же,
    как остальные зависимости репозитория)
```

## 2. Структура приложения (`scripts/synthetic_data/`)

```text
[+] core/: models.py (FileFormat StrEnum + from_alias, GeneratedArtifact),
    output_layout.py (docs/synthetic_data/<тип>, автосоздание директорий),
    random_content.py (свой генератор слов/предложений/абзацев/таблиц/
    JSON-деревьев — без сторонних библиотек, намеренно: Faker сочли
    неоправданно тяжёлой зависимостью для этой роли), text_image_renderer.py
    (Pillow: постраничный рендер текста в картинку + рендер отдельного
    сниппета — переиспользуется PDF-нечитаемым генератором и DOCX)
[+] generators/: base.py (BaseGenerator ABC: имя файла, обвязка записи),
    json_generator.py, markdown_generator.py, excel_generator.py (2 листа),
    docx_generator.py (один документ: обычные редактируемые абзацы +
    отдельный абзац-картинка после заголовка «Scanned fragment»),
    pdf/copyable.py (reportlab canvas, настоящий текстовый слой, перенос
    строк и постраничная разбивка), pdf/noncopyable.py (Pillow: вся
    страница — рендеренная картинка через text_image_renderer, PDF
    собирается штатным Pillow PDF-плагином, без текстового слоя вообще)
[+] core/registry.py — GENERATOR_REGISTRY: FileFormat -> генератор,
    get_generator()
[+] archive/zip_archiver.py — рабочая create_zip_archive() (только stdlib
    zipfile, относительные POSIX-arcname), НЕ подключена к cli.py —
    сознательно оставлена как фундамент на будущее
[+] cli.py — argparse (--formats [json|markdown|xlsx|docx|pdf-copyable|
    pdf-non-copyable|pdf|all], --count, --seed, --output-root, --dry-run);
    sys.path bootstrap (ROOT_DIR = parents[2]) по образцу
    scripts/dev_tools/restore_demo_countries.py — без переделок готово к
    регистрации в dev_tools_scripts_runner.py в будущей задаче
```

## 3. Вывод в docs/

```text
[+] docs/synthetic_data/{json,markdown,xlsx,docx,pdf/copyable,
    pdf/non_copyable}/ создаются по требованию при генерации (create=True
    по умолчанию, --dry-run их не создаёт)
[+] .gitignore: docs/synthetic_data/ добавлен в самом конце файла — после
    !docs/**/*.pdf и !docs/_arch_/** (git: последнее совпадение побеждает),
    поэтому содержимое папки игнорируется независимо от расширения.
    Существовавший ранее docs/synthetic_data/.gitkeep (уже был в git до
    этой задачи) остался отслеживаемым — гитигнор не ретроактивен для уже
    закоммиченных файлов, это ожидаемо и не мешает игнорировать новые
    сгенерированные файлы рядом с ним
```

## 4. Тесты (`scripts/synthetic_data/tests/`, отдельно от корневых tests/)

```text
[+] conftest.py — фикстуры rng (фиксированный seed) и output_root
    (tmp_path-based, не трогает реальный docs/)
[+] По одному файлу тестов на: models (from_alias), random_content,
    output_layout, каждый генератор (json/markdown/excel/docx/pdf x2),
    registry, zip_archiver, cli — 24 теста, все зелёные
[+] PDF copyable: pypdf извлекает непустой текст (>50 символов)
[+] PDF non-copyable: pypdf извлекает ПУСТОЙ текст, но page.images
    непустой (проверено и вручную на реальном сгенерированном файле)
[+] DOCX: есть непустые обычные параграфы (document.paragraphs) И есть
    вставленная картинка (document.inline_shapes >= 1) — проверено и
    вручную
```

## 5. Проверка качества

```text
[+] python -m ruff format scripts/synthetic_data — чисто
[+] python -m ruff check scripts/synthetic_data — чисто (после автофикса
    сортировки импортов, StrEnum вместо (str, Enum), устранения B008
    через модульный DEFAULT_PAGE_LAYOUT)
[+] python -m mypy scripts/synthetic_data (strict, как весь репозиторий) —
    чисто, 33 файла (после исправления двух реальных несовпадений типов:
    Pillow ImageFont union, python-docx Document.save ожидает str)
[+] python -m pytest scripts/synthetic_data/tests -q — 24 passed
    (запущено с -p no:cacheprovider --basetemp=<scratchpad>, см. Windows-
    заметку в .ai/project/11-commands.md — то же самое, что и у общего
    гейта)
[+] Ручной прогон CLI (--formats all --seed 20260708) — реальные файлы
    созданы в docs/synthetic_data/{json,markdown,xlsx,docx,pdf/copyable,
    pdf/non_copyable}/; git status/check-ignore подтверждают, что все они
    игнорируются
```

## 6. Завершение

```text
[+] Чек-лист заполнен +/-
[+] Финальный отчёт (см. сообщение по итогам задачи)
[-] Merge в main — НЕ выполняется в рамках этой задачи, по прямому
    указанию владельца («на данном этапе мы работаем только внутри
    scripts/synthetic_data», привязка к dev_tools_scripts_runner.py и,
    соответственно, публикация в main — отдельная будущая задача)
```
