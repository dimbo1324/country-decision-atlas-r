# 08. Frontend Product and UX

## Текущая роль frontend

Frontend должен доказать, что backend уже создаёт продуктовую ценность.

Сейчас не нужен финальный дизайн. Нужен понятный MVP-интерфейс.

## Основные страницы

### Главная

Должна объяснять:

- что это за платформа;
- какую проблему решает;
- с чего начать;
- как перейти к countries и decision.

### Countries

Показывает:

- Russia;
- Uruguay;
- name;
- ISO;
- region;
- status;
- link to card;
- locale.

### Country Card

Главная страница страны.

Показывает:

- country header;
- profile sections;
- scores;
- breakdowns;
- legal signals;
- sources;
- evidence summary;
- user stories summary;
- locale/fallback status.

### Decision

Главный decision flow.

Пользователь выбирает:

- origin country;
- candidate countries;
- scenario.

Получает:

- ranking;
- score;
- summary;
- strengths;
- weaknesses;
- warnings;
- breakdown;
- sources.

### Legal Signals

Показывает:

- list;
- country filter;
- signal_type;
- impact_direction;
- impact_level;
- confidence;
- dates;
- status.

### Sources

Показывает:

- title;
- publisher;
- source_type;
- language;
- confidence;
- dates;
- external URL.

### Internal Data Quality

Внутренняя страница для владельца/разработчика.

Показывает:

- overall status;
- critical issues;
- warnings;
- checked_at;
- issue list.

## UX-цель первого MVP

Пользователь должен быстро понять:

1. какие страны доступны;
2. что известно о стране;
3. какие риски есть;
4. какие источники используются;
5. какая страна лучше подходит под сценарий;
6. почему decision engine дал такой вывод.

## Следующий UX/UI-уровень

После технического MVP нужно улучшать:

- главную страницу;
- визуальную иерархию country card;
- decision result presentation;
- badges;
- risk/positive/negative colour logic;
- navigation;
- breadcrumbs;
- loading skeletons;
- empty/error states;
- mobile readability.

## Чего пока не нужно

- сложные анимации;
- финальный брендбук;
- графики на canvas/SVG;
- AI-chat UI;
- личный кабинет;
- сложная админка;
- mobile app;
- browser extension.
