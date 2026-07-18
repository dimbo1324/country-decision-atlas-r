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

## Stage 2 — packages/ui strategy (done)

- [+] Checked each of the 11 originally-flagged files individually rather
      than assuming one strategy fits all:
      - **`ModerationQueue`** — excluded. Confirmed internal-only (used
        exclusively by `/internal/*` admin/moderation pages), out of the
        owner's explicit public-surface scope.
      - **`PassportCard`** — excluded. Grepped `apps/web/src` for actual
        usage: the only hit is a *comment* in the decision-passport page
        noting its perforated-edge/stamp styling was manually
        recreated there, not imported. The component itself is never
        rendered anywhere in the real product (Storybook-only showcase)
        — dead code from a real user's perspective, so translating its
        ~15 hardcoded strings would have zero user-facing effect. Left
        untouched; documented here rather than silently skipped.
      - **`AnalysisOverlay`** — already fully prop-driven (`label` prop
        with a Russian default) since it was first written. No change
        needed; the translated value gets wired in during the Decision
        flow content stage.
      - **Breadcrumbs, Drawer, Pagination, DossierRail, DivergingMeter,
        LegalSignalTimeline** — added one or a few optional string props
        each (`ariaLabel`, `closeLabel`, `previousLabel`/`nextLabel`,
        `scaleLabel`, …), all defaulting to the existing Russian text so
        Storybook and any not-yet-migrated caller keep working unchanged.
      - **`HorizontalPager`** — same pattern, five new props
        (`prevLabel`/`nextLabel`/`prevTooltipPrefix`/`nextTooltipPrefix`/
        `slidesGroupAriaLabel`); the `NavArrow` sub-component's tooltip
        text (`"Назад"`/`"Далее"` hardcoded by direction) also became a
        `tooltipPrefix` prop.
      - **`DriftBoard`** — the one with real volume (7 strings: eyebrow
        prefix, two stat labels, two chart-axis labels, a methodology
        paragraph, a legal-disclaimer line) — bundled into one
        `labels?: Partial<DriftBoardLabels>` prop merged over a
        `DEFAULT_LABELS` object, rather than 7 separate props.
- [+] None of these are wired up to translated values yet — that happens
      per-area during Stage 3, at the `apps/web` call site that already
      has the right `useTranslations()` context (this package still has
      none of its own, deliberately, since Storybook renders every story
      with zero i18n provider).
- [+] Verify: `packages/ui` typecheck/lint clean, Vitest 8/8, Storybook
      `build-storybook` clean (defaults preserve current behavior for
      every untouched story); `apps/web` typecheck clean and `next build`
      clean (confirms the widened prop signatures don't break any
      existing call site).

## Stage 3 — Content migration (154 files, by feature area)

Each sub-stage: extract hardcoded strings into `useTranslations()` calls
against new message-catalog namespaces (en/ru/es), verify, commit.

- [+] `shared/**` (16 files) — badges, empty/error states. Done early;
      many feature files depend on these.
      - Two strategies, chosen per file rather than one blanket rule:
        - **Enum-keyed label maps** (`TrustBadge`, `ConfidenceBadge`,
          `FreshnessBadge`, `ImpactBadge`, `StatusBadge`,
          `entity-type-labels.ts`, `glossary-labels.ts`,
          `localization-labels.ts`) stay `Record<SupportedLocale,
          Record<string,string>>` dictionaries (the `decision-wizard-labels.ts`
          Stage-1 pattern) rather than next-intl `useTranslations()` — these
          all need a `?? rawValue` fallback for enum values the frontend
          doesn't recognize yet (defensive against the backend sending
          something new), and next-intl's `t()` throws on an unknown key
          unless wrapped in try/catch at every call site. Badge components
          read the locale themselves via `useAppLocale()` (zero call-site
          changes); the plain-function exports (`trustLabel`, renamed from
          `trustLabelRu`; `confidenceLabel`, renamed from `confidenceLabelRu`;
          `entityTypeLabel`; `glossaryCategoryLabel`;
          `getLocalizationBadgeLabel`/`getLocalizationBadgeTitle`) gained a
          `locale: SupportedLocale` parameter, touching 6 call-site feature
          files to pass it in (`CommandPalette`, `SearchResultCard`,
          `GlossaryTerm`, `GlossaryTermEntry`, `GlossaryFilters`,
          `TrustSurfaceBlock`, `CountryOverviewCards`, `SourcesFilters`) —
          only the specific line calling the shared function, not those
          files' own remaining hardcoded strings (those stay for their own
          later stage). `TrustSurfaceBlock` needed care: its `locale` prop is
          the *API* locale (already `toApiLocale`-mapped from Stage 1), not
          the real interface locale, so the label lookup uses a separate
          `useAppLocale()` call, not the prop.
        - **Static-text components** (`EvidenceCard`, `ErrorBoundary`,
          `LoadingState`, `EmptyState`, `DisclaimerNotice`, `ErrorState`,
          `LastVerifiedAt`) use `useTranslations()` against 7 new namespaces
          added to `messages/{en,ru,es}.json` (104 keys total, parity
          verified) — no unknown-key fallback needed since these aren't
          enum lookups. `ErrorBoundary` stays a class component
          (`componentDidCatch` has no hook equivalent) but now delegates its
          rendered fallback to a new function component
          (`ErrorBoundaryFallback`) so the translated text can use the hook.
          `LastVerifiedAt` also maps the interface locale to a
          `toLocaleDateString` tag (`en-US`/`ru-RU`/`es-ES`).
      - `LocalizationBadge.tsx` (not one of the original 16, but the sole
        consumer of `localization-labels.ts` and used by `EvidenceCard`)
        pulled into scope as a natural extension — leaving it uncalled with
        the new `locale` parameter would have left it broken, not just
        untranslated.
      - `shared/api/http.ts`'s two network-error fallback messages
        (`request_timeout`/`network_error`) can't take a `locale` argument
        normally — they're reached from ~70 data-fetching modules with no
        natural place to thread one through. Instead they read the locale
        straight from `window.location.pathname`'s first segment (always
        the interface locale, guaranteed by `routing.ts`'s
        `localePrefix: "always"`), falling back to the default locale
        during SSR where these messages are never shown to a user.
      - Verify: `apps/web` typecheck/lint clean; `pnpm format` clean;
        Vitest 84/84 (14 files) — including the two renamed/re-parametrized
        test files (`semantic-labels.test.tsx`,
        `localization-labels.test.ts`/`entity-type-labels.test.ts` now
        assert all 3 locales, not just Russian); fresh `next build` clean
        (same route list, confirming every `useTranslations()`/`useAppLocale()`
        addition landed inside an existing client boundary without needing
        a new explicit `"use client"`); `i18n_parity_check.py` reports
        104/104 keys matching across en/ru/es.
- [+] Home, Catalog, Compare (14 files + 2 pages).
      - `home-overview` (7): new `home` namespace (48 keys) covers
        `HomeOverviewView`, `HomeDeck` (slide nav labels + `HorizontalPager`
        prop wiring — Stage 2 left these on Russian defaults, this stage
        wires the real translated strings through), `HomeMatrixPreview`,
        `KeyInsightsPanel`, `LatestLegalEventsPanel`, `ScenarioWinnersPanel`,
        `CountryOverviewCards` (finished; Stage 3a only touched its
        `confidenceLabel` call site).
      - `country-catalog` (3): new `countryCatalog` namespace; also wired
        translated labels into `Pagination` (another Stage-2 prop-only
        component) in `CountryCatalogView`.
      - `compare-matrix` (4 of 6 — `MatrixCell`/`CountryScenarioMatrix` have
        no hardcoded text): new `compareMatrix` namespace.
      - `scenarios/page.tsx` (`scenariosPage` namespace) and
        `compare/page.tsx` (`comparePage` namespace) — both Server
        Components, using `getTranslations()` from `next-intl/server`
        (this codebase's first use of it) rather than the `useTranslations`
        hook.
      - **Real bug found and fixed, not just a translation gap**:
        `CompareMatrixView` cast the raw interface `locale` prop straight to
        the backend's `LocaleCode` type and called the API with it directly
        — worked by accident while only `en`/`ru` existed, but silently
        broke `/es/compare` (API call fails, matrix renders as "could not
        load") once `es` became a real interface locale. Fixed by mapping
        through `toApiLocale(asSupportedLocale(locale))` for the data
        fetch, while leaving the original `locale` prop unchanged for
        `MatrixCell`'s URL building (`getPathname`) — the same
        interface-locale-vs-data-locale distinction as Stage 1's
        `DecisionPassportActions.tsx`, just not caught until this stage
        actually exercised `/es/compare` in the browser.
      - **Extended scope, done deliberately**: `shared/lib/format.ts`'s
        `formatDate`/`formatDateTime` (17 call sites app-wide, `ru-RU`
        hardcoded) is exactly the kind of foundational shared infra Stage
        3a already set the precedent for touching early. Gave both an
        optional `locale: SupportedLocale = "ru"` parameter — defaulting to
        `"ru"` (not the interface's own `en` default) so the untouched
        `/internal/**` caller (`UsersAdminView.tsx`, confirmed
        internal-only, out of scope) and `DataQualityReportView.tsx`
        (confirmed internal-only via its sole page)
        keep their exact current output with zero required edit. Touched
        the ~13 real non-internal call sites (`WhatChangedItemCard`,
        `CountryWhatChanged`, `SubscriptionsView`, `SourceCard` x2,
        `DataJournalEntryCard`, the decision-passport page x2,
        `CountryDriftBlock`, `DecisionResults`, `CountrySources` x2,
        `CountryLegalSignals` x2, `AccountView` x2,
        `methodology/parameters/page.tsx`) to pass the real interface
        locale — only the one line calling `formatDate`/`formatDateTime`,
        not those files' own remaining hardcoded strings (deferred to their
        own later stage). `LatestLegalEventsPanel.tsx` had its own
        near-duplicate local `formatDate` (deliberately appending
        `T00:00:00` to avoid a UTC-midnight timezone rollback for
        date-only strings) — kept that behavior, renamed to
        `formatEventDate`, parameterized by locale, and exported
        `DATE_FORMAT_LOCALE` from `format.ts` so this and
        `HomeOverviewView.tsx`'s own datetime formatter share one map
        instead of three near-identical copies.
      - `DecisionResults.tsx` needed a `uiLocale` **prop**, not
        `useAppLocale()` internally — it renders from both a client tree
        (`DecisionRunForm`) and directly from a Server Component (the
        decision-passport page), and hooks aren't available in the latter;
        wired both callers to pass the correct locale (`useAppLocale()`’s
        value client-side, `asSupportedLocale(await getLocale())`
        server-side).
      - Verify: typecheck/lint/format clean; Vitest 86/86 (14 files); fresh
        `next build` clean (same route list — confirms the mixed
        server/client `DecisionResults` prop approach and the two new
        `getTranslations()` Server-Component pages compile correctly);
        `i18n_parity_check.py` 186/186 keys; browser walkthrough of `/en`,
        `/ru`, `/es` home pages (chrome fully translated, backend data
        correctly still English for `/es` per the Stage 1 `toApiLocale`
        fallback design), `/es/countries` catalog, and `/es/compare`
        (confirmed the locale-cast bug fix: matrix loads instead of
        erroring, and matrix-cell links resolve to `/es/countries/...`,
        not `/en/...`).
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
