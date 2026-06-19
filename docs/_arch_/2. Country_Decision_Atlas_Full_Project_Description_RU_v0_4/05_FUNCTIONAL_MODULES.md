# 05. Functional Modules

## 1. Country Cards

Country Card — центральная единица продукта.

Карточка страны должна включать:

- базовый country block;
- executive summary;
- migration overview;
- residence overview;
- citizenship overview;
- tax overview;
- cost of living overview;
- business overview;
- safety overview;
- legal signals summary;
- risk summary;
- scores по scenarios;
- score breakdowns;
- legal signals;
- sources;
- evidence summary;
- user stories summary;
- locale/fallback status.

## 2. Scenario Decision Engine

Decision Engine отвечает на вопрос:

> какая страна лучше подходит под выбранный сценарий и почему?

Вход:

- origin country;
- candidate countries;
- scenario;
- locale.

Выход:

- ranking;
- score;
- score label;
- summary;
- strengths;
- weaknesses;
- risk warnings;
- breakdown;
- confidence;
- sources;
- locale status.

## 3. Legal Signals

Legal Signal — структурированное описание закона, политического изменения, административной практики или риска.

Поля:

- country;
- title;
- summary;
- signal_type;
- impact_direction;
- impact_level;
- affected_groups;
- published/effective date;
- source;
- confidence;
- status.

Legal signals — одна из главных уникальных частей платформы.

## 4. Sources

Source — источник информации:

- официальный сайт;
- база законов;
- international index;
- legal analysis;
- statistics;
- government portal;
- expert/legal firm;
- structured community report.

Source должен иметь:

- title;
- url;
- publisher;
- source_type;
- language;
- confidence;
- last_checked_at;
- status.

## 5. Evidence Items

Evidence item подтверждает конкретное утверждение.

Он должен отвечать на вопрос:

> какое конкретное утверждение подтверждается каким источником?

## 6. User Stories

User stories должны быть структурированными, а не хаотичными комментариями.

Поля:

- origin country;
- destination country;
- city;
- year;
- scenario;
- budget;
- legal path;
- documents;
- problems;
- outcome;
- advice;
- satisfaction;
- verification_status;
- is_synthetic.

## 7. Data Quality

Модуль качества данных должен проверять:

- наличие profiles;
- наличие scores;
- наличие breakdowns;
- source requirements;
- evidence traceability;
- published legal signal rules;
- synthetic user story marking;
- stable country card response;
- decision engine readiness.

## 8. Content Management

Backend должен позволять управлять:

- sources;
- evidence;
- legal signals;
- country profiles;
- user stories;
- publication statuses;
- audit events.

## 9. Multilingual Content

Сейчас:

- English — основной язык;
- Russian — второй язык.

Позже:

- Spanish;
- German;
- Chinese;
- Korean;
- Portuguese;
- French;
- Arabic;
- другие языки до 15–20+.

## 10. Future AI Layer

AI должен появляться только после качественного data layer.

Будущие функции:

- source-backed summaries;
- legal signal extraction;
- contradiction detection;
- country brief;
- translation assistance;
- scenario explanation improvement;
- user-facing AI assistant.
