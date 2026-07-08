# Чек-лист задачи: `feat/synthetic-data-generator-app`

Цель: отдельное, автономное Python-приложение в `scripts/synthetic_data/`,
генерирующее файлы-заглушки (PDF в двух видах, DOCX смешанный, XLSX,
Markdown, JSON) со случайным контентом, не связанным с доменом проекта.
Результаты кладутся в `docs/synthetic_data/` (гитигнорируется), рассортированы
по типу. Заложена (но не подключена) основа для .zip-архивации. На этом этапе
**без** привязки к `dev_tools_scripts_runner.py` — только фундамент под неё.

## 0. Подготовка

```text
[ ] Ветка feat/synthetic-data-generator-app создана от актуального main
[ ] Чек-лист закоммичен и запушен до основной работы
```

## 1. Зависимости

```text
[ ] pyproject.toml: новая extras-группа synthetic-data (reportlab, Pillow,
    python-docx, openpyxl, pypdf)
[ ] mypy overrides (ignore_missing_imports) для reportlab.*, docx.*,
    openpyxl.*, PIL.*
[ ] Зависимости установлены локально (Python 3.12, тот же интерпретатор,
    что использует проект) для разработки и прогона тестов
```

## 2. Структура приложения (`scripts/synthetic_data/`)

```text
[ ] core/: models.py (FileFormat, GeneratedArtifact), output_layout.py
    (docs/synthetic_data/<тип> с автосозданием папок), random_content.py
    (свой генератор случайных слов/предложений/абзацев/таблиц — без
    сторонних библиотек), text_image_renderer.py (Pillow: рендер текста в
    картинку, переиспользуется PDF-нечитаемым генератором и DOCX)
[ ] generators/: base.py (протокол Generator), json_generator.py,
    markdown_generator.py, excel_generator.py, docx_generator.py (один
    документ: обычный редактируемый текст + отдельный абзац-картинка),
    pdf/copyable.py (reportlab, настоящий текстовый слой), pdf/
    noncopyable.py (Pillow: вся страница — картинка, текстового слоя нет)
[ ] core/registry.py — сопоставление FileFormat -> генератор
[ ] archive/zip_archiver.py — рабочая, но НЕ подключённая к CLI функция
    create_zip_archive (только stdlib zipfile) — основа под будущее
[ ] cli.py — argparse (--formats, --count, --seed, --output-root,
    --dry-run), sys.path bootstrap как в scripts/dev_tools/*, чтобы позже
    без переделок запускаться из dev_tools_scripts_runner.py
```

## 3. Вывод в docs/

```text
[ ] docs/synthetic_data/{json,markdown,xlsx,docx,pdf/copyable,
    pdf/non_copyable}/ создаются по требованию при генерации
[ ] .gitignore: docs/synthetic_data/ добавлен ПОСЛЕ существующих
    !docs/**/*.pdf и !docs/_arch_/** негаций (git: последнее совпадение
    побеждает), чтобы содержимое папки игнорировалось независимо от
    расширения
```

## 4. Тесты (`scripts/synthetic_data/tests/`, отдельно от корневых tests/)

```text
[ ] conftest.py — фикстуры: временный output-root, фиксированный seed
[ ] По одному тесту на генератор + registry + cli + zip_archiver
[ ] PDF copyable: pypdf извлекает непустой текст
[ ] PDF non-copyable: pypdf извлекает ПУСТОЙ текст, но страница содержит
    вложенное изображение (XObject / page.images)
[ ] DOCX: есть непустой обычный параграф (редактируемый текст) И есть
    вставленная картинка (inline shape)
```

## 5. Проверка качества

```text
[ ] python -m ruff format scripts/synthetic_data
[ ] python -m ruff check scripts/synthetic_data
[ ] python -m mypy scripts/synthetic_data (strict, как весь репозиторий)
[ ] python -m pytest scripts/synthetic_data/tests -q
[ ] Ручной прогон CLI — реальные файлы в docs/synthetic_data/, git status
    подтверждает, что они игнорируются
```

## 6. Завершение

```text
[ ] Чек-лист заполнен +/-
[ ] Финальный отчёт
[ ] Merge в main — НЕ выполняется в рамках этой задачи (отдельным явным
    запросом владельца, по конвенции репозитория)
```
