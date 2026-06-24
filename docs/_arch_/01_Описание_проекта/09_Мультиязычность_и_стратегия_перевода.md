# 09. Multilingual and Translation Strategy

## Текущие языки

На текущем этапе:

- English — основной язык;
- Russian — второй язык.

## Будущие языки

В дальнейшем платформа должна поддерживать 15–20+ языков.

Вероятные следующие языки:

- Spanish;
- German;
- Chinese;
- Korean;
- Portuguese;
- French;
- Arabic;
- Turkish;
- Italian;
- Polish;
- Ukrainian;
- Hindi;
- Japanese;
- others by demand.

## Почему мультиязычность важна

Платформа касается миграции, а миграция по определению международна.

Пользователи будут говорить на разных языках, а источники будут на разных языках:

- официальные сайты;
- законы;
- news/legal analysis;
- community reports;
- user stories.

## Правильная модель переводов

Не хранить переводы только как `title_en`, `title_ru`, `title_es`, потому что список языков будет расти.

Лучше иметь отдельную translation architecture:

- locale;
- translation;
- translation job;
- translation glossary;
- translation memory;
- translation review;
- source language;
- translation status.

## Translation statuses

- `missing`;
- `source`;
- `translated`;
- `fallback`;
- `machine_draft`;
- `human_reviewed`;
- `published`;
- `outdated`;
- `failed`.

## Translation workflow

Правильный workflow:

1. исходный контент создаётся на английском или другом source language;
2. система определяет язык;
3. создаётся translation job;
4. machine translation создаёт draft;
5. юридически важный текст уходит на human review;
6. после проверки перевод публикуется;
7. если original изменился, перевод становится outdated.

## Юридически важный контент

Для legal content нельзя делать:

> machine translation → published truth

Нужно:

> original source → summary → machine translation → human review → published translation → source link remains visible.

## Fallback

Если пользователь запросил `ru`, но русского текста нет:

- возвращается английский;
- явно показывается `translation_status=fallback`;
- frontend может показать notice.

## Источники

Оригинальный legal source должен храниться на оригинальном языке. Перевод не заменяет оригинал.
