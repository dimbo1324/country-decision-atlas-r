# Task: Three-language interface (English default, Russian, Spanish)

Owner request: the product's *interface* (chrome + every UI label —
explicitly NOT the country/content data pipeline, which stays a separate
future task) should support switching between English (new primary),
Russian (existing), and Spanish (new). Branch
`feat/i18n-three-language-interface` off up-to-date `main`.

Owner-confirmed scope: **public product surface only** — everything under
`apps/web/src/app/[locale]/**`. `/internal/**` (admin/moderation, a
separate route tree not under `[locale]`) is explicitly excluded and not
touched.

## Scope survey (done before implementation)

- [+] Delegated an import-tracing survey (not just folder-name grep) to
      distinguish genuinely public files from folders that mix public and
      admin-only components under one barrel (confirmed real split in
      `author-metrics/`, `migration-board/`, `community/`; confirmed
      `data-quality/` is 100% internal despite no `admin-` prefix, and
      `country-proposals/` is 100% public despite looking admin-adjacent).
- [+] Result: ~154 files in `apps/web` (30 page.tsx + 108 feature files +
      16 shared/** files) contain hardcoded Cyrillic UI text needing
      extraction, plus ~11 `packages/ui` component files rendered on
      public pages (Breadcrumbs, Drawer, ModerationQueue, Pagination,
      PassportCard, DriftBoard, LegalSignalTimeline, DivergingMeter,
      DossierRail, HorizontalPager, AnalysisOverlay) — strategy for those
      still to be decided (task in progress).
- [+] Confirmed backend's `LocaleCode` contract enum is `"en"|"ru"` only —
      no Spanish support and none planned by this task (owner's explicit
      interface-vs-content boundary). Decision: interface locale `es`
      requests backend DATA in `en` as a fallback; UI chrome around it
      still renders in Spanish.

## Stage 1 — Infrastructure (done)

- [+] `SUPPORTED_LOCALES` → `["en", "ru", "es"]`, `DEFAULT_LOCALE` → `"en"`
      (was `"ru"`) in `shared/lib/locale.ts`. `routing.ts`'s
      `localePrefix: "always"` needed no change (every locale, including
      default, already gets a URL prefix).
- [+] New `apps/web/src/messages/es.json` — full, hand-written Spanish
      translation of all 90 existing chrome keys (nav/auth/footer/locale/
      search/error/notFound), matching the register of the existing
      en/ru copy. `next-intl`'s `request.ts` needed zero changes (already
      dynamically imports `../messages/${locale}.json` off `routing`).
- [+] `scripts/dev_tools/i18n_parity_check.py`: generalized from a
      hardcoded en/ru comparison to an N-locale comparison
      (`LOCALES = ("en", "ru", "es")`) — verified 90/90 keys match.
- [+] `LocaleSwitcher.tsx` needed **zero changes** — it already renders
      one button per `SUPPORTED_LOCALES` entry; adding `"es"` to the
      array was enough to get a working 3-way EN/RU/ES switcher for free.
- [+] New `ApiLocale`/`toApiLocale()`/`DEFAULT_API_LOCALE` in
      `shared/lib/locale.ts` (es→en fallback for every backend-facing
      call). Let the TypeScript compiler find every affected call site
      by widening `SupportedLocale` first and fixing each resulting
      error, rather than grepping for usages by hand — safer given ~40
      call sites across ~30 files. Also updated 16 `shared/api/*.ts`
      modules' own internal `DEFAULT_LOCALE` fallback to a new
      `DEFAULT_API_LOCALE` constant (same root cause, same fix, applied
      uniformly since all 16 shared the identical pattern).
- [+] `decision-wizard-labels.ts`'s `Record<SupportedLocale, ...>`
      dictionary needed an actual new `es` entry (not just a type
      loosening) — added a full, hand-written Spanish translation
      alongside the existing ru/en ones.
- [+] Verify: `pnpm typecheck`/`lint` clean (web); fresh `next build`
      clean; browser walkthrough — `/` redirects to `/en` (was `/ru`),
      switcher renders all 3 languages and switching to `/es` renders
      correct Spanish chrome (footer spot-checked verbatim), country
      dossier page loads on `/es/countries/russia` with all 6
      `toApiLocale`-mapped child-block requests (`platform-metrics`,
      `trust`, `drift`, `routes`, `what-changed`, `data-journal`)
      correctly hitting the backend with `locale=en`, `/ru/...` pages
      unaffected (still request `locale=ru`, unaffected functionally).
      Docker stack needed a full rebuild + reseed mid-verification (the
      owner had cleared images/volumes) — migrations, bootstrap,
      demo-country restore, search index rebuild, all re-run cleanly.

## Stage 2 — packages/ui strategy (in progress)

- [ ] Determine whether the ~11 flagged `packages/ui` components take
      text via props already (fix at the apps/web call site) or hardcode
      Cyrillic internally (needs a different approach, since
      `packages/ui` has no `next-intl` context of its own outside
      Storybook).

## Stage 3 — Content migration (154 files, by feature area)

Each sub-stage: extract hardcoded strings into `useTranslations()` calls
against new message-catalog namespaces (en/ru/es), verify, commit.

- [ ] `shared/**` (16 files) — badges, empty/error states. Done early;
      many feature files depend on these.
- [ ] Home, Catalog, Compare (14 files + 2 pages).
- [ ] Country Dossier (21 files + 1 page).
- [ ] Decision flow (15 files + 2 pages).
- [ ] Legal Signals, Sources, Routes (21 files + 3 pages).
- [ ] Cabinet: Trips, Watchlist, Subscriptions, Account/Auth (11 files +
      4 pages).
- [ ] Community: Migration Board, User Stories, Author Metrics, Country
      Proposals (12 files + 6 pages).
- [ ] Knowledge + AI Assistant + Search (14 files + 4 pages).

## Final verification (after all stages land)

- [ ] Full typecheck/lint/format (`ui` + `web`).
- [ ] `next build` clean, JS-budget script passes.
- [ ] Full Vitest, Storybook build.
- [ ] Full Playwright e2e suite + visual regression (expect real, reviewed
      baseline changes this time — English is now the default locale
      shown in every "no explicit locale" screenshot).
- [ ] Contrast + i18n-parity audits (parity now covers 3 locales).
- [ ] Browser walkthrough of all 3 locales across every migrated area.
- [ ] Update `docs/_arch_/08_Открытые_вопросы.md`'s Р-12 (documented
      "ru-only interface, next-intl scoped to chrome" as the accepted
      state) — supersede with the new decision and date.

## Completion

- [ ] Checklist filled (`+`/`-`).
- [ ] Incremental commits on this branch, one per stage.
- [ ] Final report.
