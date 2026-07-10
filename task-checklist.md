# Чек-лист задачи: конвейер синтетических данных — Этап 3 (контент и сценарии)

Источник: `docs/synthetic_data/synthetic_data_pipeline_technical_specification.md`,
раздел 23, «Этап 3 — пользователи, контент и сценарии тестирования».
Зависимость: Этап 1 (основание) и Этап 2 (страны и временная динамика) —
уже реализованы и смержены в `main`.

Ветка: `feat/synthetic-data-stage3-content-v1`.

## Подготовка

- [+] Перечитан раздел 23 «Этап 3» техзадания (состав работ + критерии
      перехода) и раздел 6.3 (люди и контент), 8.1-8.2 (блоки и рецепты
      документов), 9 (формат сценариев).
- [+] Изучено текущее состояние `scripts/synthetic_data/core/`:
      `world_models.py`, `world_input.py`, `world_generator.py`,
      `world_validation.py`, `seed.py`, `cli.py`, `world_config.json`.
      Подтверждено: Этапы 1-2 закрыты (Pydantic-модели, детерминированный
      seed, генератор архетипов, валидатор диапазонов/связности).

## Реализация — канонические модели (`world_models.py`)

- [ ] `SyntheticUser` (user_id, display_name, email на `example.test`,
      role, locale).
- [ ] `SyntheticAuthor` (author_id, user_id, display_name, reputation,
      specialization, bio).
- [ ] `SyntheticArticle` (article_id, author_id, country_id, title,
      summary, source_ids, published_as_of).
- [ ] `SyntheticComment` (comment_id, article_id, user_id, body,
      created_as_of, moderation_status).
- [ ] `SyntheticLegalSignal` (signal_id, country_id, event_id,
      effective_as_of, impact, confidence, source_id,
      affected_country_ids).
- [ ] `ResolvedBlock` + `SyntheticDocumentRecipe` (recipe_id,
      document_type, country_id, blocks — рецепт как ссылки на факты
      и текстовые блоки, не как независимый шаблон).
- [ ] `ScenarioStep`, `ScenarioExpectedResult`, `SyntheticScenario`
      (машиночитаемый формат: исходное состояние, действия, ожидаемый
      результат, связанные артефакты, метки риска).
- [ ] `SyntheticWorld` расширен новыми полями: users, authors, articles,
      comments, legal_signals, document_recipes, scenarios.

## Реализация — входные данные (`world_input.py` + `world_config.json`)

- [ ] `user_given_names`/`user_family_names` — словари вымышленных имён
      (без совпадений с реальными людьми, техническая генерация).
- [ ] `document_blocks` — библиотека текстовых блоков (id, kind,
      applies_to, requires, variants) для локали `en-US`.
- [ ] `document_recipes` — рецепты (id/document_type, упорядоченный
      список block id).
- [ ] Расширены существующие проверки `_ensure_input_is_safe` — новые
      секции конфигурации проходят ту же проверку на PII/секреты/URL.

## Реализация — генерация

- [ ] Новый `core/content_generator.py`: детерминированная генерация
      пользователей, авторов, статей, комментариев (с разными статусами
      модерации — approved/pending/hidden), правовых сигналов (привязаны
      к уже существующему событию страны — связность по правилу 7.2).
- [ ] Новый `core/document_recipes.py`: разрешение рецепта в
      `ResolvedBlock` по фактам конкретной страны; ошибка при ссылке на
      несуществующий факт.
- [ ] Новый `core/scenario_generator.py`: генерация ≥3 базовых сценариев
      (сравнение стран; работа с источником/комментарием; изменение
      данных + watchlist + fake-уведомление) плюс сценарий с неполными/
      конфликтующими/устаревшими данными (страна с минимальным
      `data_confidence`).
- [ ] `world_generator.py`: оркестрация — сборка контента и сценариев
      поверх уже сгенерированных стран, сборка итогового `SyntheticWorld`.

## Реализация — валидация (`world_validation.py`)

- [ ] Все `author.user_id`, `article.author_id`/`country_id`/`source_ids`,
      `comment.article_id`/`user_id`, `legal_signal.country_id`/
      `event_id`/`source_id`, `document_recipe.country_id`,
      `scenario.related_artifacts` — ссылаются на существующие сущности.
- [ ] Email пользователей оканчиваются на `example.test`.
- [ ] `moderation_status` — из допустимого множества, встречаются не
      менее двух разных статусов в мире.
- [ ] Документный рецепт: каждый `requires` блока разрешим на фактах
      страны, иначе ошибка валидации.
- [ ] Сценарии: минимум 3 сценария, каждый со непустыми `steps` и
      `expected_results`; отдельно проверено наличие сценария с меткой
      неполных/устаревших данных.

## Тесты

- [ ] `tests/test_world_models.py`: новые модели, JSON Schema.
- [ ] `tests/test_world_input.py`: парсинг новых секций конфигурации,
      отклонение PII/секретов в них же.
- [ ] `tests/test_world_generator.py`: пользователи/авторы/статьи/
      комментарии/правовые сигналы связаны с существующими странами;
      воспроизводимость по seed сохраняется.
- [ ] Новый `tests/test_document_recipes.py`.
- [ ] Новый `tests/test_scenario_generator.py`.
- [ ] `tests/test_world_validation.py`: новые невалидные миры (чужой
      author_id, несуществующий факт в рецепте, сценарий без шагов) —
      каждый ловится валидатором с понятной ошибкой.
- [ ] Ручной прогон `validate`/`plan`/`generate` — новый контент виден
      в выводе `plan` и в `synthetic_world.json`.

## Проверка

- [ ] `py -3.12 -m pytest scripts/synthetic_data/tests/ -q` зелёный.
- [ ] `py -3.12 -m mypy scripts/synthetic_data` чистый.
- [ ] `py -3.12 -m ruff check scripts/synthetic_data` / `ruff format --check` чистые.
- [ ] Полный `py -3.12 -m pytest tests/ -q` (весь проект) зелёный.
- [ ] Полный quality gate (`python dev_tools_scripts_runner.py full-check`)
      зелёный.

## Завершение

- [ ] Чек-лист заполнен `+`/`-`.
- [ ] Раздел 23 «Этап 3» техзадания: статус обновлён на «реализовано»
      с честной записью отступлений (если будут).
- [ ] Финальный отчёт написан.
- [ ] Коммит на ветке. Merge в `main` и push на `origin/main` — только
      после отдельного явного подтверждения владельца (по аналогии с
      AE-4 в этой же сессии: «реализуй этап 3» само по себе не было
      командой на мердж/пуш).
