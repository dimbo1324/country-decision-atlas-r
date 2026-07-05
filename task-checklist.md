# Чек-лист задачи: фронтенд-прототип «Intelligence Platform» (Vite)

Цель: перенести дизайн-систему и макет из
`docs/_ideas_and_concepts_/full_v1/` в изолированный React+Vite прототип
(`apps/web-prototype`), не трогая рабочее Next.js-приложение `apps/web`.
Горизонтальная навигация без скролла, карточки с drawer'ами, живые canvas-
графики, палитра/типографика/анимации — по образцу дизайн-системы.

## 1. Изучение материалов

```text
[+] countryatlas_design_system.md изучен полностью
[+] countryatlas_platform.html изучен (структура зон, компоненты, JS-логика)
[+] frontend_libs.md изучен, выбраны конкретные библиотеки
[+] Текущая структура apps/web изучена (для совместимости токенов/типов)
```

## 2. Архитектура прототипа

```text
[+] apps/web-prototype создан как отдельный pnpm workspace-пакет
[+] Стек: Vite + React 19 + TypeScript + Tailwind CSS
[+] pnpm-workspace.yaml обновлён
[+] Прототип не подключён к root quality gate (изолирован по решению владельца)
[+] Реальный backend не требуется — витрина на реалистичных фикстурах
```

## 3. Дизайн-система

```text
[+] Цветовые токены (bg/text/gold/blue/terra/sage/plum) как CSS-переменные
[+] Шрифты подключены (Playfair Display, Crimson Text, IM Fell English, mono)
[+] Базовые примитивы: Button, Card (tilt + top-accent reveal), Drawer
[+] SectionSlide / HorizontalPager — постраничная горизонтальная навигация
    без скролла (стрелки, точки-индикаторы, клавиатура, свайп)
[+] Живые canvas-графики с lerp-анимацией (радар, velocity/drift, heatmap)
[+] prefers-reduced-motion: анимации отключаются
[+] Только inline SVG-иконки (lucide-react, без иконочных веб-шрифтов)
```

## 4. Флагманская страница

```text
[+] Hero-слайд (лого, тэглайн, live-статистика)
[+] CII Radar слайд
[+] Legal Velocity / Country Drift слайд(ы)
[+] Scenario Matrix (heatmap) слайд
[+] Trust & Transparency слайд
[+] Community / Catalog слайд с карточками -> drawer с деталями
[+] Ни горизонтального, ни вертикального скроллбара на десктопе
[+] Мобильная деградация: нативный горизонтальный scroll-snap
```

## 5. Проверки и завершение

```text
[+] pnpm --filter web-prototype build проходит
[+] pnpm --filter web-prototype typecheck проходит
[+] pnpm --filter web-prototype lint проходит
[+] Ручная проверка в браузере (preview_* инструменты): десктоп + мобильная ширина
[+] Чек-лист заполнен отметками +/-
[+] Коммит(ы) осмысленные
[ ] Слияние в main выполнено fast-forward (следующий шаг)
[ ] Push в origin/main выполнен (следующий шаг)
[ ] Итоговый отчёт написан (следующий шаг)
```

## Найдено и исправлено в процессе проверки

- Реальный баг: стрелки prev/next в `HorizontalPager` были подключены к
  отдельному, несвязанному состоянию хука `usePager`, а не к управляемым
  пропам `index`/`onIndexChange` — клики по стрелкам не двигали видимый
  слайд. Хук `usePager` удалён, навигация переведена на единый источник
  истины (`index` состояние в `App`).
- Ограничение среды: инструмент `preview_screenshot` стабильно уходит в
  таймаут на этой странице из-за непрерывных `requestAnimationFrame`-циклов
  canvas-графики (фон + активный график). Проверка сделана через
  accessibility snapshot, computed styles и прямые клики/`eval` — этого
  достаточно для подтверждения корректности, но визуальный скриншот для
  отчёта не получен.
