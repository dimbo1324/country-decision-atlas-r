# 03. Core User Flows

## Первый базовый пользовательский цикл

Минимальный цикл продукта:

1. пользователь открывает платформу;
2. видит краткое объяснение продукта;
3. переходит к списку стран;
4. выбирает страну;
5. открывает карточку страны;
6. смотрит профиль, scores, legal signals, sources;
7. переходит к decision page;
8. выбирает origin country, candidate countries и scenario;
9. запускает decision run;
10. получает ranking, score, strengths, weaknesses, risk warnings, sources.

## Flow 1: изучение страны

Путь:

`Главная → Countries → Uruguay → Country Card`

Пользователь должен понять:

- что представляет собой страна;
- кому она подходит;
- какие есть миграционные возможности;
- какие риски;
- какие правовые сигналы важны;
- какие источники используются;
- насколько данные надёжны.

## Flow 2: сравнение стран

Путь:

`Главная → Decision → выбрать scenario → Run decision`

Пользователь должен получить:

- ranking стран;
- score;
- score label;
- strengths;
- weaknesses;
- risk warnings;
- breakdown;
- sources.

## Flow 3: анализ правовых сигналов

Путь:

`Главная → Legal Signals`

Пользователь должен видеть:

- какие изменения происходят;
- к какой стране они относятся;
- какой тип сигнала;
- направление влияния;
- уровень влияния;
- confidence;
- источники.

## Flow 4: проверка источников

Путь:

`Главная → Sources`

Пользователь должен видеть:

- какие источники используются;
- кто publisher;
- какой тип источника;
- язык;
- confidence;
- дату проверки;
- ссылку на оригинал.

## Flow 5: внутренний контроль качества

Путь:

`Internal → Data Quality`

Это не публичный пользовательский flow. Он нужен владельцу и разработчику.

Показывает:

- overall status;
- critical issues;
- warnings;
- issues list;
- checked_at.

## Будущие flows

Позже появятся:

- user watchlist;
- notifications/alerts;
- user story submission;
- editor review workflow;
- AI country brief;
- source ingestion workflow;
- translation workflow;
- expert marketplace;
- paid report generation.
