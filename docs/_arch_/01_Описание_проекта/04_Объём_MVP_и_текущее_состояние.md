# 04. MVP Scope and Current State

## MVP-границы

Текущий MVP ограничен намеренно:

- страны: Russia и Uruguay;
- языки: English и Russian;
- сценарии: 5 основных decision scenarios;
- backend: FastAPI + PostgreSQL;
- frontend: минимальный web-интерфейс;
- данные: seed/content layer с sources, evidence, legal signals, scores;
- AI: не используется;
- форум: не используется;
- marketplace: не используется;
- auth/RBAC: не production-level;
- новые страны: пока не добавляются.

## Пять сценариев MVP

| Slug | Назначение |
|---|---|
| `relocation_residence` | Переезд / ВНЖ |
| `permanent_residence_citizenship` | ПМЖ / гражданство |
| `low_budget_living` | Жизнь с ограниченным бюджетом |
| `business_self_employment` | Бизнес / самозанятость |
| `safety_political_risk` | Безопасность / политический риск |

## Что уже реализовано по состоянию последнего обсуждения

### Backend

- FastAPI backend;
- PostgreSQL migrations;
- seed data;
- OpenAPI contract;
- generated TypeScript types;
- locale/fallback logic для `en` и `ru`;
- `/api/v1/countries`;
- `/api/v1/countries/{slug}/card`;
- `/api/v1/legal-signals`;
- `/api/v1/sources`;
- `/api/v1/evidence-items`;
- `/api/v1/scenarios`;
- `/api/v1/user-stories`;
- `/api/v1/decision/run`;
- admin/content management foundation;
- audit events;
- data quality report;
- decision engine v1;
- filters/pagination/sorting;
- smoke tests / diagnostics layer.

### Content/Data

- Russia и Uruguay;
- 5 scenarios;
- country profiles;
- legal signals;
- sources;
- evidence items;
- country scores;
- score breakdowns;
- synthetic user stories;
- published country cards in English/Russian;
- data-quality validation v1.

### Frontend

- frontend shell;
- shared UI components;
- locale switcher;
- typed API client layer;
- `/countries`;
- `/countries/russia`;
- `/countries/uruguay`;
- `/decision`;
- `/legal-signals`;
- `/sources`;
- `/internal/data-quality`;
- loading/error/empty states;
- `en/ru` support;
- generated TypeScript types usage.

## Что MVP должен доказать

Первый MVP должен доказать не красоту интерфейса, а продуктовую ценность:

> пользователь может открыть сайт, изучить страну, увидеть источники и правовые сигналы, запустить scenario decision и получить объяснимый результат.

## Что ещё не является целью MVP

- production security;
- массовое покрытие стран;
- автоматический legal scraping;
- AI-ассистент;
- реальные пользовательские аккаунты;
- полноценная админка;
- платёжная система;
- мобильные приложения;
- browser extension;
- сложная аналитика и графики;
- marketplace.
