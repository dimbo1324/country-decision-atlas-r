# 11. Roadmap by Phases

## Phase 0 — Research and Product Foundation

Статус: в основном завершено.

Содержит:

- market research;
- competitors;
- migration trends;
- user pains;
- initial product vision;
- data model;
- OpenAPI foundation;
- PostgreSQL foundation.

## Phase 1 — Backend Foundation

Статус: завершено/почти завершено.

Содержит:

- FastAPI;
- PostgreSQL;
- migrations;
- seed data;
- OpenAPI;
- generated types;
- locale/fallback;
- read API;
- country card endpoint;
- decision engine;
- admin/content management foundation;
- data quality;
- smoke tests;
- diagnostics.

## Phase 2 — Minimal Web App Foundation

Статус: реализован по последнему обсуждению.

Содержит:

- frontend shell;
- API client layer;
- country list;
- country card;
- decision page;
- legal signals page;
- sources page;
- internal data quality page;
- en/ru switch;
- loading/error/empty states.

## Phase 3 — MVP UX/UI Polish

Следующий логичный frontend-слой.

Цели:

- улучшить главную страницу;
- усилить country card readability;
- улучшить decision result;
- добавить визуальную систему badges;
- сделать navigation понятнее;
- улучшить empty/error/loading states;
- сделать интерфейс похожим на реальный продукт.

## Phase 4 — Data Depth v1

Углубить данные по Russia/Uruguay:

- больше sources;
- больше evidence;
- больше legal signals;
- better score explanations;
- richer country profiles;
- real user stories;
- source freshness.

## Phase 5 — Search Foundation

Добавить:

- поиск по countries;
- поиск по legal signals;
- поиск по sources;
- фильтры;
- возможно Meilisearch или PostgreSQL full-text first.

## Phase 6 — Auth and Roles

Добавить:

- user;
- editor;
- moderator;
- admin;
- owner;
- secure admin routes;
- session/auth provider.

## Phase 7 — Translation Workflow

Добавить:

- translation jobs;
- translation review;
- glossary;
- machine draft;
- human reviewed;
- auto-outdated translations.

## Phase 8 — AI Summary Pipeline

Добавить AI только поверх источников:

- source summary;
- legal signal summary;
- country brief;
- contradiction detection;
- decision explanation improvement.

## Phase 9 — Watchlist and Alerts

Добавить:

- watchlist;
- legal change alerts;
- country risk alerts;
- email/push later;
- user preferences.

## Phase 10 — Expansion

Добавить новые страны:

- Argentina;
- Paraguay;
- Spain;
- Portugal;
- Germany;
- Netherlands;
- Serbia;
- Georgia;
- Armenia;
- UAE;
- Canada;
- etc.

Но только после того, как Russia/Uruguay доказали модель.
