# 14. Acceptance Criteria for First MVP

## Product Acceptance

Первый MVP можно считать состоявшимся, если пользователь может:

- понять, что делает платформа;
- открыть список стран;
- открыть карточку России;
- открыть карточку Уругвая;
- прочитать profile sections;
- увидеть scores;
- увидеть legal signals;
- увидеть sources;
- запустить decision run;
- получить ranking и объяснение;
- переключить English/Russian;
- увидеть data quality/internal status.

## Backend Acceptance

- `/api/v1/countries` работает;
- `/api/v1/countries/{slug}/card` работает;
- `/api/v1/decision/run` работает;
- `/api/v1/legal-signals` работает;
- `/api/v1/sources` работает;
- `/api/v1/admin/data-quality/report` работает;
- OpenAPI актуален;
- TypeScript types генерируются;
- tests проходят;
- data-quality report без critical issues;
- locale/fallback работает.

## Frontend Acceptance

- `/countries` работает;
- `/countries/russia` работает;
- `/countries/uruguay` работает;
- `/decision` работает;
- `/legal-signals` работает;
- `/sources` работает;
- `/internal/data-quality` работает;
- en/ru переключение работает;
- loading/error/empty states есть;
- build проходит;
- lint проходит;
- typecheck проходит.

## Content Acceptance

- Russia и Uruguay имеют country profiles;
- есть 5 scenarios;
- есть scores;
- есть score breakdowns;
- есть sources;
- есть evidence;
- есть legal signals;
- есть user stories summary;
- данные имеют confidence/status.

## UX Acceptance

Пользователь должен не просто видеть данные, а понимать:

- какая страна перед ним;
- почему score такой;
- какие есть риски;
- какие источники используются;
- какой вариант лучше для сценария.

## Что не обязательно для первого MVP

- AI;
- auth;
- payments;
- mobile app;
- full admin panel;
- advanced charts;
- search engine;
- notifications;
- marketplace;
- 15–20 languages;
- 50+ countries.
