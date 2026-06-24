# 07. Data Model and Content Governance

## Основной принцип данных

Проект должен быть data-first.

Главный источник доверия — не AI и не мнение автора, а связка:

**claim → evidence → source → date → confidence → editorial status.**

## Основные сущности

| Сущность | Назначение |
|---|---|
| Country | страна |
| CountryProfile | расширенный профиль страны |
| CountryCard | published read-model карточки |
| LegalSignal | правовой/политический/административный сигнал |
| Source | источник |
| EvidenceItem | доказательство конкретного утверждения |
| Scenario | сценарий пользователя |
| CountryScore | оценка страны по сценарию |
| ScoreBreakdown | расшифровка оценки по критериям |
| UserStory | структурированный пользовательский опыт |
| Translation | перевод контента |
| TranslationJob | задача перевода |
| AuditEvent | событие изменения данных |

## Нормализация

Рекомендуемая база — 3НФ.

Почему 3НФ достаточно:

- данные имеют много связей;
- нужна фильтрация;
- нужны источники и evidence;
- важно избегать дублирования;
- проект ещё MVP, 4НФ может усложнить разработку.

4НФ можно применять позже точечно, если появятся независимые многозначные зависимости, которые начнут создавать дублирование и аномалии обновления.

## JSONB

JSONB допустим только точечно:

- metadata;
- flexible attributes;
- provider payloads;
- temporary ingestion output;
- audit changes;
- AI extraction drafts.

Не использовать JSONB как замену нормальной реляционной модели.

## Publication lifecycle

Для важных сущностей:

- `draft`;
- `review`;
- `published`;
- `archived`;
- `rejected`.

Published data должны проходить минимальные проверки.

## Data Quality Rules

### Country

- published country должна иметь profile;
- MVP countries должны иметь cards;
- Russia и Uruguay должны иметь scores по всем 5 scenarios.

### Source

Published source должен иметь:

- title;
- url;
- publisher;
- source_type;
- language;
- confidence.

### Legal Signal

Published legal signal должен иметь:

- country;
- title;
- summary;
- signal_type;
- impact_direction;
- impact_level;
- source;
- confidence.

### Evidence

Evidence должен иметь:

- source;
- country;
- claim;
- confidence;
- traceability.

### Score

Country score должен иметь:

- country;
- scenario;
- score;
- confidence;
- explanation;
- breakdown.

### User Story

Synthetic story должна быть явно помечена как synthetic.

## Audit Trail

Audit events нужны для:

- создания;
- обновления;
- публикации;
- архивирования;
- отклонения;
- изменения критичных данных.

Цель audit trail — понимать, кто и когда изменил важную информацию.

## Editorial Governance

Юридически важные данные нельзя публиковать без источника.

AI-generated или machine-translated content не должен автоматически становиться trusted content.

Редакторская модель должна различать:

- official source;
- expert interpretation;
- community report;
- synthetic story;
- machine translation;
- human-reviewed translation;
- outdated content.
