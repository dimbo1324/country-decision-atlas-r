# Task: Тотальный аудит проекта + правки (2026-07-20)

Владелец попросил полный аудит всех слоёв (фронт/бэк/БД/API/взаимодействие),
устранить ошибки/коллизии перед ручным тестированием, оформить результаты в
`.md` в корне и запушить. Работа велась прямо в `main` по прямому указанию
владельца (переопределяет обычный branch-workflow).

## Preparation

- [+] Ориентировка: `git status`/`git log` — HEAD `7a54510`, чисто,
      в синхроне с origin. Мой прошлый Stage-13 merge (`effc39d`) — предок.
- [+] Поднят live-стек: Docker (api/redis), миграции (до
      `056_web_dossier_v2_flag`), read-models, демо-страны, поисковый индекс.
- [+] Собрана и запущена web (dev + prod build) для live-диагностики.

## Findings & fixes

- [+] **F-1 (High)** hydration mismatch в шапке: `NextIntlClientProvider`
      без явного `locale` → next-intl `<Link>` строил `/en/...` на `/ru`.
      Root cause подтверждён live (server `/ru/login` vs client `/en/login`).
      Фикс: `locale={locale}` в провайдере (`app/[locale]/layout.tsx`).
- [+] **F-2 (Medium)** обрезание широких таблиц на мобильном: `DataTable`
      без scroll-обёртки + `w-[100vw]` подчёркивание. Фикс: `overflow-x-auto`
      + перепривязка sweep к строке (`packages/ui/.../DataTable.tsx`).
- [+] Бэкенд: проверены RBAC, IDOR (user_id из сессии), SQL (параметризация),
      секреты (`_forbid_default_secrets_in_production`) — здорово, без правок.
- [+] Контракты: `pnpm contracts:generate` без диффа — синхрон.
- [+] Отчёт: `AUDIT_2026-07-20.md` в корне.

## Verification

- [+] web typecheck / lint — чисто.
- [+] ui typecheck / lint / test (8) — чисто.
- [+] web test (86) — чисто.
- [+] prod build — 47 маршрутов, exit 0.
- [+] Оба фикса подтверждены live в браузере (dev-сервер).

## Notes / not done

- [-] Приложенная владельцем картинка с «наслоением» в чат не пришла —
      визуальные коллизии проверены программно (overflow/z-index) на desktop
      и mobile; адресную проверку конкретного экрана можно сделать по указанию.
- [-] Скриншот-тул таймаутил из-за rAF в `BackgroundFX` — диагностика велась
      через замеры DOM (точнее для overflow/коллизий).
- [-] Мелочь (не правил): захардкоженная локаль `"ru"` в
      `RecomputePanelView` таймстампах — вынесено в отчёт как наблюдение.

## Completion

- [+] Commit + push в `main` (по прямому указанию владельца).
- [+] Final report — в чате + `AUDIT_2026-07-20.md`.
