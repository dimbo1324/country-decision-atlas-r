# 06. Backend Architecture

## Основной backend-стек

Текущий ориентир проекта:

- Python;
- FastAPI;
- PostgreSQL;
- Redis;
- OpenAPI;
- generated TypeScript contracts;
- Docker Compose;
- raw SQL migrations / controlled migrations;
- pytest;
- ruff;
- mypy;
- sqlfluff;
- pre-commit.

## Архитектурный стиль

На текущем этапе проект должен оставаться modular monolith.

Не нужны:

- микросервисы;
- Kubernetes;
- сложная event-driven архитектура;
- отдельные сервисы под каждую функцию;
- преждевременная production-инфраструктура.

## Главные backend-домены

- countries;
- country cards;
- legal signals;
- sources;
- evidence;
- scenarios;
- decision engine;
- scores;
- user stories;
- translations;
- content management;
- data quality;
- audit events;
- admin/internal endpoints.

## API-принципы

API должен быть:

- versioned: `/api/v1`;
- OpenAPI-first;
- typed for frontend;
- predictable;
- locale-aware;
- fallback-aware;
- consistent in error format;
- filterable;
- paginated;
- sortable.

## Главные endpoints

- `GET /api/v1/countries`;
- `GET /api/v1/countries/{slug}`;
- `GET /api/v1/countries/{slug}/card`;
- `GET /api/v1/legal-signals`;
- `GET /api/v1/sources`;
- `GET /api/v1/evidence-items`;
- `GET /api/v1/scenarios`;
- `GET /api/v1/user-stories`;
- `POST /api/v1/decision/run`;
- `GET /api/v1/admin/data-quality/report`.

## Admin/content endpoints

На MVP-этапе admin endpoints могут быть защищены временным `X-Admin-Token`.

В будущем это должно быть заменено на RBAC:

- user;
- editor;
- moderator;
- admin;
- owner.

## Decision Engine

Decision Engine v1 должен быть deterministic и explainable.

Он не должен зависеть от AI.

Использует:

- country_scores;
- score_breakdowns;
- legal_signals;
- sources;
- evidence;
- scenario defaults;
- confidence aggregation.

## Что важно не сломать

- `/countries/{slug}/card`;
- `/decision/run`;
- locale/fallback;
- data-quality report;
- generated TypeScript contracts;
- frontend API client compatibility.

## Когда backend считать достаточным для MVP

Backend достаточен для первого frontend cycle, если:

- country card работает;
- decision run работает;
- legal signals/sources доступны;
- data-quality checks работают;
- OpenAPI актуален;
- TypeScript contracts генерируются;
- smoke/regression tests проходят;
- frontend получает стабильные структуры.
