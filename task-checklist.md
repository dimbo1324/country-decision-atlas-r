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
- [+] Country Dossier (21 files + 1 page).
      - `country-card` (11): 13 new namespaces (`countryHeader`, `countryCii`,
        `countryEvidenceSummary`, `countryProfileSections`, `countryScores`
        shared with `ScoreBreakdown`, `countryUserStories`, `localeStatus`,
        `countryDossier`). `CountryCiiBlock`'s `METRIC_LABEL_RU` and
        `LocaleStatusBadge`'s `STATUS_LABELS` converted to the
        `Record<SupportedLocale, Record<string,string>>` pattern (unknown-
        value fallback, same reasoning as Stage 3a's badges). `CountryDossier`
        itself is the largest single edit this whole task — 17 section
        titles/rail-labels/tab-labels — all now `t()`-driven inside the
        `useMemo` that builds the section list (added `t` to the deps array).
      - `trust-surface` (1), `country-drift` (2 of 3 —
        `DriftHistoryMiniList.tsx` has no hardcoded text),
        `what-changed` (2), `data-journal` (1 of 3 — `CountryDataJournalBlock`
        and `CountryDataJournalBlock`'s empty-state wrapper have none of
        their own), `platform-intelligence` (4 of 5 —
        `PlatformMetricLabelBadge.tsx` renders the raw enum value directly,
        nothing to translate) — each finishes the strings Stage 3a's
        `toApiLocale`-only pass deliberately left behind (e.g.
        `TrustSurfaceBlock`'s empty-state/contradiction-level text,
        `CountryDriftBlock`'s "events in period/window/computed at" line).
      - `countries/[slug]/page.tsx`: new `countryPage` namespace via
        `getTranslations()` (Server Component, matching Stage 4's page
        pattern).
      - **Two real bugs found via the browser walkthrough, not caught by
        typecheck/lint/tests**:
        1. A genuine typo introduced mid-edit in `CountryDossier.tsx`:
           pasted an extra `<CommunityCountryBlock>` into the
           migration-board section's content (duplicate render, wrong
           section). Caught on self-review before verification even ran.
        2. `shared/lib/useAppLocale.ts` (existing file, untouched since
           before this task) carried a `"use client"` directive that had
           gone unnoticed all the way through Stages 3–4 because every
           prior call site happened to already sit inside a `"use client"`
           ancestor. `CountryHeader.tsx` is the first call site rendered
           **directly** from a Server Component (`countries/[slug]/page.tsx`
           renders `<CountryHeader>` standalone, not through the
           `"use client"` `CountryDossier`) — so `LocalizationBadge`'s
           `useAppLocale()` call (added back in Stage 3a) crashed with
           "Attempted to call useAppLocale() from the server" the moment a
           real country page was browser-tested for the first time since
           Stage 3a. Root cause: next-intl's own `useLocale()` (which
           `useAppLocale` just wraps) is dual-mode-safe in both Server and
           Client Components — same as `useTranslations` — but wrapping it
           in a file explicitly marked `"use client"` blocks that, since
           the directive is a hard module-boundary marker Next.js enforces
           regardless of what the wrapped call actually needs. Fix: dropped
           the stray `"use client"` from `useAppLocale.ts` — it was never
           actually needed.
      - **Test infrastructure gap found and fixed**: `CountryDossier.test.tsx`
        asserts literal Russian tab labels (e.g. `"Обзор"`), and
        `test-utils/render.tsx`'s `renderWithProviders` was passing
        `messages={{}}` to `NextIntlClientProvider` — meaning every
        `useTranslations()` call in a tested component was silently getting
        next-intl's `"namespace.key"` missing-message fallback string
        instead of real text. This had been invisible until this stage
        because the few `useTranslations()` users before now (`AppFooter`
        etc.) had no dedicated component tests exercising their translated
        text. Fixed by importing the real `ru.json` catalog into
        `render.tsx` (matching the hardcoded `locale="ru"`) instead of an
        empty object — every future stage's component tests now get real
        translated text for free, not just this one.
      - Verify: typecheck/lint/format clean; Vitest 86/86 (14 files,
        including the now-meaningful `CountryDossier.test.tsx` assertions);
        fresh `next build` clean; `i18n_parity_check.py` 297/297 keys;
        browser walkthrough of `/en/countries/argentina`,
        `/ru/countries/argentina`, `/es/countries/argentina` (all dossier
        sections render translated, in the correct locale, with backend
        content — country names, source excerpts — correctly still
        following its own data-locale fallback rather than the interface
        locale, exactly per the Stage 1 design).
- [+] Decision flow (15 files + 2 pages).
      - `decision-personalization` (4 + `decision-criteria-labels.ts`):
        `DECISION_CRITERIA_LABELS` converted to the enum-dict pattern; new
        `decisionPersonalization` namespace for the sliders panel and
        summary.
      - `decision-run` (6 of 7 — `DecisionWarnings.tsx` has no hardcoded
        text): `DecisionBreakdown` reuses `countryScores`'s table-column
        keys verbatim (identical table to `ScoreBreakdown.tsx` from
        Stage 5) rather than duplicating them; `DecisionResultCard`'s three
        enum dicts (compatibility/freshness/note-type labels) converted to
        the `Record<SupportedLocale,...>` pattern; `DecisionRunForm` is the
        session's largest single component edit — moved `STEP_LABELS` and
        the personalization-error-message map from module scope into the
        component body so they can call `t()`.
      - `decision-wizard`: **0 files needed changes** — Stage 1's
        `DECISION_WIZARD_LABELS[locale]` dictionary already covers every
        string in this folder's three real components end to end; the
        checklist's original "(1)" estimate turned out to already be fully
        resolved.
      - `decision-visual-comparison` (2 of 6 — the spider chart, summary,
        bars, and winner-list components render only data-driven labels,
        no hardcoded text of their own): new `ciiComparison` namespace.
      - `decision-passports` (2): new `decisionPassports` namespace.
      - `decision/page.tsx` (`decisionPage` namespace) and
        `decision/passports/[token]/page.tsx` (`decisionPassportPage`
        namespace, finishing the strings Stage 4 left behind when it only
        touched this page's date formatting and `uiLocale` prop wiring).
      - **Real bug found via the browser walkthrough** (not caught by
        typecheck/lint/tests): `DecisionResults.tsx` — the component that
        renders the actual ranked outcome after clicking "run" — still had
        entirely untranslated Russian text (`"Сценарий:"`, `"Создано:"`,
        `"Рекомендуемый вариант"`, `"Полный рейтинг"`, the
        screen-reader-only status announcement, etc.). It had only ever
        been touched for its date-formatting/`uiLocale`-prop plumbing back
        in Stage 4, and every prior review of "decision-run (6)" wrongly
        assumed `DecisionWarnings.tsx` was the one file with no text,
        overlooking that `DecisionResults.tsx` still had its own. Not
        caught until actually clicking "Run the decision engine" in the
        browser and reading the result card — typecheck/lint/tests have no
        way to notice a string that was never wrapped in `t()` at all.
        Fixed with a new `decisionResults` namespace (14 keys); this is the
        reason every stage in this task ends with an interactive browser
        walkthrough, not just a page-load check.
      - Verify: typecheck/lint/format clean; Vitest 86/86 (14 files); fresh
        `next build` clean; `i18n_parity_check.py` 411/411 keys; full
        interactive walkthrough (not just page load) of `/en/decision`,
        `/ru/decision`, and `/es/decision` — filled the wizard to step 4 via
        `?step=4`, clicked "Run the decision engine" for real, and read the
        actual result card in all 3 locales (this is what caught the
        `DecisionResults.tsx` gap above).
- [+] Legal Signals, Sources, Routes (21 files + 3 pages).
      - `legal-signals-timeline` (7): new `legalSignalsTimeline` namespace
        for the shared registry view/filters/legend/empty-state (feed +
        chart tabs, both driven by one data-fetch, per the file's own
        header comment); `timelineEventCard` for the event card;
        `legalSignalEvidenceDrawer` for the evidence drawer.
        `TimelineFilters.tsx`'s `SIGNAL_TYPE_LABELS`/
        `IMPACT_DIRECTION_LABELS`/`IMPACT_LEVEL_LABELS` and
        `TimelineEventCard.tsx`'s `TYPE_LABELS` converted to the
        `Record<SupportedLocale, Record<string,string>>` enum-dict pattern.
        **Locale-prop fix**: `TimelineEventCard`/`TimelineYearGroup`'s
        `locale` prop was typed as the backend-only `LocaleCode` (`en`/`ru`)
        even though both components only ever use it for display (date
        formatting, enum labels), never a data fetch — retyped to
        `SupportedLocale` and fixed the caller
        (`LegalSignalsRegistryView.tsx`) to pass the real interface
        `locale` instead of the `apiLocale` it was fetching with. This also
        fixed a real gap: `TimelineEventCard`'s local `formatEventDate` had
        `locale === "ru" ? "ru-RU" : "en-US"` hardcoded, silently mapping
        `es` to English date formatting; now uses the shared
        `DATE_FORMAT_LOCALE` map from `shared/lib/format.ts`.
      - `sources` (5): `sourceCard`, `sourceEvidenceDrawer`,
        `sourcesFilters`, `sourcesView` namespaces.
        `SourcesFilters.tsx`'s `SOURCE_TYPE_LABELS` converted to the same
        enum-dict pattern; its `useAppLocale()` + `confidenceLabel()` reuse
        from Stage 3a's `ConfidenceBadge` left unchanged.
      - `routes` (9 + new `route-labels.ts`): new shared
        `features/routes/route-labels.ts` exporting `ROUTE_TYPE_LABELS`
        (`Record<SupportedLocale, Record<RouteType,string>>`) — created to
        de-duplicate the identical route-type dictionary that was
        previously hardcoded separately in both `RouteDetailView.tsx` and
        `RouteFilters.tsx`; both now import it instead of keeping their own
        copy. `routes` namespace covers `CountryRoutesBlock`,
        `RouteEmptyState`, `RouteFilters` (shared, since all three are
        tightly coupled); `routeCard` for `RouteCard`; `routeDetail`
        (largest new namespace, 45 keys) covers `RouteDetailView`,
        `RouteChecklistList`, `RouteDocumentsList`, `RouteEligibilityBadges`,
        `RouteEvidenceList`, `RouteSourcesList` — `RouteDetailView`'s
        `LEGAL_STATUS_LABELS`/`STATUS_LABELS` and
        `RouteEligibilityBadges`' `LABELS`/`VALUE_LABELS` converted to the
        enum-dict pattern (the latter needed a new `useAppLocale()` call,
        having had no locale access before).
      - `legal-signals/page.tsx` (`legalSignalsPage`), `sources/page.tsx`
        (`sourcesPage`) — both existing Server Components using
        `useTranslations()` directly (confirmed RSC-safe, matching the
        `AppFooter` precedent); `routes/[id]/page.tsx` (`routePage`) —
        Server Component switched to `getTranslations()` from
        `next-intl/server`, matching the Stage 4-6 page pattern.
        `legal-signals/timeline/page.tsx` needed zero changes — confirmed
        it is a pure redirect with no user-facing text.
      - Verify: typecheck/lint clean; `pnpm format:check` clean (4 files
        needed a `prettier --write` pass after editing); Vitest 5/5;
        fresh `next build` clean (same route list); `i18n_parity_check.py`
        529/529 keys across en/ru/es (13 new namespaces added); full
        interactive browser walkthrough of `/legal-signals` (feed +
        timeline tabs, evidence drawer open/empty-state), `/sources`
        (filters, evidence drawer), and a real `/routes/[id]` page
        (Argentina's monotributo route, plus a route-not-found error
        state) across all 3 locales — confirmed chrome fully translated
        while backend content (event titles/summaries, route notes) stays
        in its own data locale per the Stage 1 design, and confirmed the
        still-Russian Migration Board block on the route page and the
        still-Russian watchlist/AI-assistant strings on the country
        dossier are pre-existing gaps already tracked as separate stages
        (#58 Cabinet, #59 Community), not a regression from this stage.
- [+] Cabinet: Trips, Watchlist, Subscriptions, Account/Auth (11 files +
      8 pages — the initial "4 pages" estimate undercounted; the actual
      public route tree has 8 distinct pages in this area).
      - `auth` (`LoginForm.tsx`/`RegisterForm.tsx`): **0 files needed
        changes** — both already fully wired to a pre-existing `auth`
        namespace since Stage 1 (nav/footer labels needed it early), so
        this stage's survey confirmed they were already done end to end.
      - `trips` (7 files + new `features/trips/trip-labels.ts`): new shared
        `TRIP_STATUS_LABELS`/`WAYPOINT_KIND_LABELS` enum dicts (de-duplicates
        what was previously three separate hardcoded Russian copies across
        `TripListView.tsx`, `TripDetailView.tsx`, and the shared-trip page —
        same reasoning as Stage 7's `route-labels.ts`). New namespaces:
        `trips` (shared by `TripListView`/`TripDetailView`), `tripChecklist`,
        `tripReminders`, `tripShareExport`, `tripWarnings`, `tripWaypoints`.
        `TripDetailView.tsx`'s two `next/dynamic` loading fallbacks
        (`TripWaypoints`/`TripReminders`) needed small wrapper components
        (`TripWaypointsLoadingFallback`/`TripRemindersLoadingFallback`)
        since a `dynamic()` loading option can't call `useTranslations()`
        directly — same pattern as Stage 7's `LegalSignalsLoadingFallback`.
        `TripReminders.tsx` had a hardcoded `date-fns/locale`'s `ru` import
        for its reminder-timestamp formatting with zero Spanish/English
        support; added a local `DATE_FNS_LOCALE: Record<SupportedLocale,
        typeof enUS>` map (`enUS`/`ru`/`es` from `date-fns/locale`) — the
        first `date-fns` locale usage in the app, so no shared precedent to
        reuse yet.
      - `watchlist` (2 files): `WatchlistButton.tsx`/`WatchlistView.tsx`
        share one `watchlist` namespace; the three notify-toggle field
        labels use the exact snake_case API field names as translation keys
        (`notify_legal_signals`/`notify_drift_changes`/`notify_route_updates`)
        since the array of toggles is already keyed by those field names.
      - `subscriptions` (1 file): new `subscriptions` namespace; the zod
        refine error message needed the schema built inside the component
        (same "move to component body so `t()` is callable" pattern used
        for the trip/checklist/reminder/waypoint forms and precedented by
        Stage 6's `DecisionRunForm`).
      - `account` (1 file, `AccountView.tsx`): new `account` namespace
        (42 keys, the largest single-file namespace this stage) covering
        profile fields, Telegram link/unlink, security notifications
        (`newDeviceLogin` interpolates `{device}{ip}{date}`), and the
        revoke-all-sessions confirmation dialog.
      - 8 pages, each a thin `Kicker`/`h1` wrapper: `login`, `register`,
        `account`, `trips`, `watchlist`, `subscriptions` (all
        `useTranslations()`, unchanged Server/Client shape); `trips/[id]`
        switched to `getTranslations()` (breadcrumb labels only, matching
        the Stage 7 page pattern); `trips/shared/[token]` (the one Server
        Component with real content, not just a header) switched to
        `getTranslations()` and now imports the shared
        `TRIP_STATUS_LABELS`/`WAYPOINT_KIND_LABELS` from `trip-labels.ts`
        (its own `CHECKLIST_STATUS_LABELS` stayed local — no duplicate
        elsewhere to de-dupe against).
      - Verify: typecheck/lint clean; `pnpm format:check` clean (5 files
        needed a `prettier --write` pass); Vitest 5/5; fresh `next build`
        clean (same route list); `i18n_parity_check.py` 692/692 keys across
        en/ru/es (12 new namespaces + 8 new page namespaces added); full
        interactive browser walkthrough across `/en`, `/ru`, `/es` —
        registered a real throwaway account through the UI, created a
        trip, opened its detail view (route/checklist/reminders/warnings/
        publishing sections), saved a country to the watchlist and
        confirmed the notify-toggle labels, checked the empty
        subscriptions view, created a public share link and verified the
        shared-trip Server Component page (including its not-found error
        state) in all 3 locales, then deleted the trip. Confirmed the
        still-Russian Migration Board block on the trip page and the
        still-Russian scenario names in the trip-creation dropdown are
        pre-existing gaps out of this stage's scope (Community stage #59
        and backend content data respectively), not a regression.
      - Browser-automation note (not a product bug): the in-app browser's
        `form_input`/synthetic-event tools intermittently failed to
        register a click or a `type="datetime-local"` value change with
        this app's React Hook Form + Zod forms on the very first
        interaction after a navigation — a known quirk of dispatching
        synthetic DOM events against React's uncontrolled-ref input
        tracking, not a translation or logic defect. Confirmed each time
        by re-reading the DOM value (correctly set) and by dispatching a
        real `.click()` via `javascript_tool`, which always succeeded.
- [+] Community: Migration Board, User Stories, Author Metrics, Country
      Proposals (13 public feature files + 9 pages — the "12 public files"
      estimate undercounted by one: `features/migration-board/errorMessage.ts`
      is itself a real file needing an edit, distinct from the "6 of 7"
      component count it was listed alongside. The "9 pages" estimate,
      already re-checked at the top of this session against a fresh
      `apps/web/src/app/**/*.tsx` glob, was exactly right this time —
      first stage since 7/8 where the page count didn't need correcting).
      - `features/migration-board/` (6 components + `errorMessage.ts` = 7
        files; `MigrationBoardModerationView.tsx` re-confirmed internal-only
        via its sole importer, `app/internal/migration-board-moderation/page.tsx`,
        touched only for a one-line call-site fix, not translated — see
        below): new shared
        `features/migration-board/migration-board-labels.ts` (the
        route-labels.ts/trip-labels.ts precedent) exporting
        `TIMELINE_LABELS`/`GOAL_LABELS`/`STAGE_LABELS`/`VISIBILITY_LABELS`
        (`Record<SupportedLocale, Record<string,string>>`, `""` included as
        an explicit "any" filter option for `TIMELINE_LABELS`/`GOAL_LABELS`)
        — de-duplicates what was three separate hardcoded Russian copies of
        the same enum sets across `MigrationBoardListView.tsx`'s filters and
        `MigrationBoardFormView.tsx`'s create form (including its inline
        `<option>` literals for stage/visibility, which had never been
        deduplicated against the filter dropdowns at all). New namespaces:
        `migrationBoard` (shared by `MigrationBoardListView`,
        `CountryMigrationBoardBlock`, `RouteMigrationBoardBlock` — all three
        render the same "no posts yet" / "create a post" vocabulary),
        `migrationBoardDetail`, `migrationBoardForm`, `migrationBoardAccount`.
        `errorMessage.ts`'s `migrationBoardErrorMessage()` gained a
        `locale: SupportedLocale` parameter (the Stage 3a `trustLabel`
        shape) backing a `FALLBACK_MESSAGE` dict; all 5 public call sites
        updated to pass the real interface locale, plus the one call site in
        the excluded `MigrationBoardModerationView.tsx` (internal-only, not
        translated) fixed to pass a literal `"ru"` — the same "keep the
        untouched internal caller compiling with its current Russian output"
        pattern as Stage 3a's `formatDate` default.
      - `features/user-stories/UserStoriesView.tsx` (1 file): new
        `userStories` namespace covering the share-story form (including its
        zod schema's two validation messages, moved inside the component body
        to call `t()` — the `DecisionRunForm`/trip-form precedent), the
        community story list, and the story card's advice/satisfaction lines.
      - `features/author-metrics/` (2 of 3 files, `AuthorMetricsModerationView.tsx`
        re-confirmed internal-only): new `authorProfile` and
        `authorMetricsStudio` namespaces.
        `AuthorMetricsStudioView.tsx`'s local `STATUS_LABELS` (draft/
        submitted/published/rejected/archived, with a `?? metric.status`
        fallback) converted to a new **shared** enum-dict,
        `shared/lib/moderation-status-labels.ts`
        (`MODERATION_STATUS_LABELS`/`moderationStatusLabel()`, the
        `entity-type-labels.ts`/`TrustBadge.trustLabel` shape) — not kept
        local, because `CountryProposalListView.tsx` (a different feature
        folder, also touched this stage) has the exact same enum with the
        exact same five values and the exact same defensive-fallback need;
        same "worth extracting" reasoning as `route-labels.ts`/
        `trip-labels.ts`, just cross-feature instead of cross-file-in-one-
        feature this time. **Real bug found and fixed while reading the
        code, before any browser testing**: both `AuthorProfileView.tsx` and
        `AuthorMetricsStudioView.tsx` always rendered a metric's
        `metric.name_ru` (and `AuthorProfileView`'s `methodology_ru ||
        methodology_en`) unconditionally, regardless of interface locale —
        harmless while the interface was Russian-only, but means an
        `en`/`es` visitor to an author's profile would see Russian metric
        names even though the backend's `MyAuthorMetricDefinition` /
        `AuthorMetricDefinitionBase` schemas carry both `name_en` and
        `name_ru` (confirmed in `packages/contracts/generated/types.ts`).
        Fixed both call sites to pick `name_en`/`name_ru` (and
        `methodology_en`/`methodology_ru`) via `toApiLocale(locale) ===
        "ru"`, the same `es`-falls-back-to-`en` rule Stage 1 established for
        every other backend-content read.
      - `features/country-proposals/` (2 files, both public, confirmed
        `app/internal/country-proposals/page.tsx` is a separate internal-only
        page as the plan flagged): new `countryProposals` and
        `countryProposalWizard` namespaces. Same `name_en`/`name_ru`
        locale-aware display fix as author-metrics, applied to
        `CountryProposalListView.tsx`'s list cards and
        `CountryProposalWizardView.tsx`'s header (`CountryProposal` schema
        also carries both fields). `CountryProposalListView.tsx`'s
        `STATUS_LABELS` converted to reuse the same new
        `moderationStatusLabel()` helper; `CountryProposalWizardView.tsx`'s
        `SubmitSection` (`Текущий статус: {status}`) also switched from a
        raw status string to the same helper for consistency, since it's the
        identical enum. `CountryProposalWizardView.tsx`'s `SECTIONS` array
        (rail labels) moved from module scope into the component body so its
        labels can call `t()` — the `DecisionRunForm`/`STEP_LABELS`
        precedent from Stage 6.
      - `features/community/CommunityCountryBlock.tsx` (1 of 2 files,
        `CommunityModerationView.tsx` re-confirmed internal-only): new
        `communityCountryBlock` namespace (46 keys, the largest single
        namespace this stage, including a nested `issueType.*` object for
        the 6 fixed `ReportType` values and a nested `ratingAxis.*` object
        for the 6 fixed reality-gap score fields — both built from an
        exhaustive local `as const` array rather than a backend enum, so
        neither needed the `?? rawValue` defensive-fallback treatment that
        would have pushed them into an enum-dict instead). Unlike every
        other file in this stage, this component's hardcoded strings were
        already in **English**, not Russian (its own header comment already
        called it out as intentionally English-first) — still needed full
        extraction into `t()` calls, since a `ru`/`es` interface visitor was
        getting untranslated English strings for the entire community Q&A
        panel, the data-issue report form, and the reality-gap radar chart
        labels. `RATING_AXES`'s per-field label array was restructured from
        a module-level constant into a `ratingAxes` value built inside the
        component body (`RATING_FIELDS.map((field) => ({ field, label:
        t(\`ratingAxis.${field}\`) }))`), since the labels need `t()`.
      - 9 pages, each a thin `Kicker`/`h1` wrapper switched to
        `getTranslations()` (Server Components, matching the Stage 4-8
        pattern): `migrationBoardPage`, `migrationBoardNewPage`,
        `accountMigrationBoardPage`, `userStoriesPage`,
        `authorProfilePage`, `authorMetricsStudioPage`,
        `countryProposalsPage`, `countryProposalWizardPage` (all simple);
        `migrationBoardPostPage` also carries the page's `AppBreadcrumbs`
        labels (`breadcrumbBoard`/`breadcrumbPost`), the Stage 7
        `routePage` pattern.
      - **Pre-existing cross-cutting gap found, not fixed this stage (out of
        scope for a minimal diff)**: `AppBreadcrumbs`/`Breadcrumbs`'
        `aria-label` defaults to a hardcoded Russian string
        (`"Хлебные крошки"`, set in Stage 2's `packages/ui` pass and never
        wired to a translated value by any later stage) on **every**
        locale, not just `ru` — confirmed via HTTP smoke test on
        `/en/migration-board/[id]` (this stage's own new `AppBreadcrumbs`
        call site) and by grepping all 4 call sites across the app
        (`migration-board/[id]`, `routes/[id]` from Stage 7,
        `trips/[id]` from Stage 8, `decision/passports/[token]` from
        Stage 4). Screen-reader-only, not visible text, and touching it
        properly means either changing the `packages/ui` default or wiring
        an `ariaLabel` prop at 4 call sites spanning 3 already-shipped
        stages — deliberately left as a separately-tracked accessibility gap
        rather than folded into this stage's diff; flagged again in Final
        verification below.
      - **Real bug found and fixed via HTTP-level walkthrough**: the new
        `communityCountryBlock.title` key was translated in `en`/`es` but
        the `ru` entry was accidentally left as the literal English
        "Community intelligence" (copy-paste slip while drafting the
        message catalogs) — caught by curling `/ru/countries/argentina` and
        finding the English string where `subtitle` right below it was
        correctly in Russian. Fixed to "Аналитика сообщества"; re-verified
        via the same curl before moving on.
      - **Browser-automation tooling gap this session**: this session's
        tool access did not include the Browser-pane tools
        (`preview_start`/`navigate`/`computer`/`read_page`) the plan
        prescribes for the interactive walkthrough — only Read/Edit/Write/
        Bash/Grep/Glob were available. Substituted the best available
        equivalent: started the real `pnpm dev` server against the
        already-running Docker stack (API + Postgres + Redis, confirmed
        healthy via `docker ps`), then drove it with `curl` — registered a
        real throwaway account via the auth API, created a real migration
        board post through `/api/v1/me/migration-board/posts` with the
        exact enum values `MigrationBoardFormView.tsx` sends (confirmed
        `3_6_months`/`preparing_documents`/`housing_search`/`members_only`
        are all accepted, not just plausible-looking), hit its detail page
        and confirmed the expected not-yet-moderated 404 in all 3 locales,
        checked the same throwaway user's `/authors/[userId]` profile
        (empty-metrics / reputation-not-computed states) in all 3 locales,
        and checked `CommunityCountryBlock`/`CountryMigrationBoardBlock` on
        a real country page and `RouteMigrationBoardBlock` on a real route
        page in all 3 locales. This caught the `ru` `title` bug above and
        confirmed no leaked `namespace.key` fallback strings anywhere, but
        it is **not** a substitute for an actual interactive click-through
        (no toast/error-state assertions after a real form submit, no
        multi-step wizard interaction, no visual/layout check) — flagged
        here honestly rather than silently claimed as done; a real browser
        walkthrough of this stage's areas is still owed before Final
        verification's full walkthrough, and should be cheap to fold into
        that pass since it covers the same areas plus everything else.
      - Verify: `i18n_parity_check.py` 948/948 keys across en/ru/es (19 new
        namespaces: 10 feature + 9 page namespaces, 256 new keys, from 692
        after Stage 8); `pnpm --filter web typecheck` clean
        (needed the `MigrationBoardModerationView.tsx` one-line fix above to
        pass, since it's a real caller of the now-reparametrized
        `migrationBoardErrorMessage`); `pnpm --filter web lint` clean;
        Vitest 5/5; `pnpm format:check` clean (6 files needed a
        `prettier --write` pass after editing); fresh `next build` clean
        (45 routes, unchanged from before this stage — no route added or
        removed); `python -m pytest tests/test_frontend_contract.py -q`
        clean.
      - **Real browser walkthrough done in a follow-up session**, closing the
        gap flagged above: registered a throwaway account, filled and
        submitted a real migration-board post through the UI (all form
        selects — timeline/stage/goal/visibility — read back correctly),
        confirmed it landed in `/account/migration-board` with translated
        status/action labels, and spot-checked `/migration-board`,
        `/migration-board/new`, `/account/migration-board`,
        `/account/author-metrics`, `/account/country-proposals`, and a
        country page's embedded `CommunityCountryBlock` across `/en`, `/ru`,
        `/es`. **Found and fixed 2 real bugs the HTTP-only pass had missed**:
        (1) `ru.json` had several `migrationBoardAccount`/`migrationBoardForm`
        keys left partially or fully untranslated — `accept`/`decline`/
        `cancel` as literal English, `incomingKicker`/`noIncoming`/
        `outgoingKicker`/`noOutgoing`/`loadingBoard` mixing Russian sentences
        with a bare English "requests"/"migration board" noun,
        `scenarioLabel`/`personaLabel` left as English words, and
        `contactRequestsLabel` mixing "contact requests" into an otherwise
        Russian sentence — while the `es.json` equivalents were fully,
        correctly translated; also `countryProposalWizard.executiveSummaryLabel`
        was left as literal English "Executive summary" in `ru.json`. Fixed
        all of these directly in `ru.json` (`Принять`/`Отклонить`/`Отменить`,
        `Входящие заявки`/`Исходящие заявки`/etc., `Сценарий`/`Персона`,
        `Разрешить заявки на контакт через платформу.`, `Краткое резюме`) —
        left `routeIdLabel`/`slugLabel` ("Route ID"/"Slug") untranslated on
        purpose, matching `es.json`'s own precedent of leaving those specific
        technical field names in Latin script. (2) `CountryDossier.tsx`'s
        Community section (added by this stage) had a hardcoded
        `railLabel: "Community"` and `title="Community"` — never wrapped in
        `t()`, unlike every other section in that file — so the dossier's tab
        rail and section heading stayed literal English "Community" on `/ru`
        and `/es` pages. Fixed by adding `railCommunity`/`titleCommunity` keys
        to the existing `countryDossier` namespace (950/950 parity after) and
        wiring both props through `t()`. Re-ran `pnpm --filter web typecheck`
        and `lint` clean after both fixes; re-verified in the browser that
        `/ru/account/migration-board` and `/ru/countries/argentina` now
        render fully translated. Confirmed the still-English CII/scenario
        methodology disclaimer text and the mixed English/Russian scenario
        names in dropdowns are backend-seeded content data
        (`database/fixtures/demo_countries/country_scores.json`, the
        `scenarios` API), not a frontend gap — same explicit content-vs-chrome
        scope boundary as everywhere else in this task, confirmed by grepping
        the exact disclaimer string to that fixture file and by curling
        `/api/v1/scenarios?locale=en` and finding literal Russian names mixed
        with English ones already at the data layer.

- [+] Knowledge + AI Assistant + Search (14 files + 5 pages — the checklist's
      original "14 files + 4 pages" heading undercounted the pages by one:
      `scenarios/page.tsx` was already fully migrated back in Stage 3b
      (`scenariosPage` namespace), so it was never part of this stage's real
      remaining work; the actual 5 pages were `methodology/page.tsx`,
      `methodology/parameters/page.tsx`, `glossary/page.tsx`,
      `assistant/page.tsx`, `search/page.tsx`. File count of 14 was
      confirmed exactly right this time: `features/ai-assistant/` (7 of 8 —
      `AIDisclaimer.tsx` re-confirmed already fully prop-driven, untouched),
      `features/glossary/` (3 of 4 — `RelatedTermChip.tsx` re-confirmed
      zero hardcoded strings, untouched), `features/methodology/` (2 of 2),
      `features/search/` (2 of 3 — `SearchResultCard.tsx` re-confirmed zero
      hardcoded strings, untouched). `shared/ui/CommandPalette.tsx`
      re-confirmed already fully translated from an earlier stage, not
      touched.
      - `ai-assistant` (7 files): 7 new namespaces, one per component
        (`aiAnswerCard`, `aiAssistantView`, `aiCitationsList`,
        `aiRefusalState`, `aiAskForm`, `aiDecisionIntentHelper`,
        `aiExplainNumberButton` — 32 keys total), matching this task's
        established per-component-namespace granularity for small, tightly
        coupled UI (the `timelineEventCard`/`legalSignalEvidenceDrawer`
        precedent from Stage 7). `AIAskForm.tsx`'s and
        `AIDecisionIntentHelper.tsx`'s hardcoded default textarea values
        (a suggested example question about Uruguay; a sample relocation
        situation) were treated as translatable UI-facing text, not fixed
        content — full, natural translations added for all 3 locales
        (the `country_slug` default value `"uruguay"` itself stayed
        untouched, a data-layer slug, not display text).
        `AIDecisionIntentHelper.tsx`'s `Scenario:`/`Persona:` badge prefixes
        reuse the exact translated wording already established by Stage 6's
        `decisionPersonalization.persona` and Stage 9's
        `migrationBoardForm.scenarioLabel`/`personaLabel`
        (`Сценарий`/`Персона`, `Escenario`/`Persona`) rather than inventing
        new wording for the same concept.
      - `glossary` (3 files): 3 new namespaces (`glossaryFilters`,
        `glossaryTermEntry`, `glossaryView`, 9 keys) — `GlossaryFilters.tsx`
        and `GlossaryTermEntry.tsx` already called `useAppLocale()` without
        their own `"use client"` directive from an earlier stage, confirming
        again (as Stage 3a first established) that files nested inside a
        `"use client"` ancestor tree don't need their own directive to use
        hooks; `useTranslations()` was added the same way, no directive
        needed.
      - `methodology` (2 files): `MethodologyAccordion.tsx`'s
        `SECTION_TYPE_LABELS` (keyed by the backend's `section_type` enum,
        with a `?? section.section_type` fallback) converted to the
        `Record<SupportedLocale, Record<string,string>>` enum-dict pattern
        established since Stage 3a — kept local to the file since nothing
        else in the app reads this specific enum.
        `MethodologyGlossaryTeaser.tsx` is rendered directly from
        `methodology/page.tsx` (a Server Component) with no `"use client"`
        ancestor in its render tree — called `useTranslations()` directly
        without adding a `"use client"` directive of its own (the
        `AppFooter`/Stage 7 `legalSignalsPage` precedent: next-intl's
        `useTranslations()` is dual-mode-safe in Server and Client
        Components as long as the file itself isn't marked `"use client"`;
        only `useAppLocale()`/`useLocale()` had the Stage 5 crash, from a
        stray `"use client"` on that specific wrapper file, not from
        `useTranslations()` itself). New `methodologyGlossaryTeaser`
        namespace (4 keys).
      - `search` (2 files): `SearchFilters.tsx`'s `ENTITY_TYPE_OPTIONS`
        (a second, plural-flavored hardcoded copy of the same
        `SearchResultItem["entity_type"]` enum `entity-type-labels.ts`
        already covers) was **not** turned into a second enum dict —
        reused the existing `entityTypeLabel()`/`ENTITY_TYPE_LABELS` from
        Stage 3a instead (already complete for all 3 locales), the same
        "don't duplicate an enum dict that already exists" reasoning as
        Stage 7's `route-labels.ts` extraction, just in the opposite
        direction (avoiding a new duplicate instead of de-duplicating an
        existing one). New `searchFilters` namespace (3 keys) for the
        filter's own labels (`Result type`/`Country`/`All countries`).
        `SearchView.tsx` reuses and extends the **existing** `search`
        namespace (already used by `CommandPalette.tsx` since an earlier
        stage) rather than creating a new `searchView` namespace from
        scratch — `search.placeholder`/`search.submit`/`search.searching`
        already had exactly the right English/Russian/Spanish wording for
        this component's search input, submit button, and searching state;
        added 7 new keys to the same namespace for the parts `CommandPalette`
        doesn't need (`ariaLabel`, `promptMessage`, `errorTitle`,
        `errorMessage`, `resultsCount`, `emptyState`, `loadingFallback`).
      - 5 pages: `methodologyPage` (4 keys), `methodologyParametersPage`
        (9 keys, including separate `kicker`/`kickerVersioned` keys matching
        the source's own error-state-vs-loaded-state split), `glossaryPage`
        (3 keys), `assistantPage` (3 keys), `searchPage` (2 keys) — all via
        `getTranslations()`/`useTranslations()` from Server Components,
        matching the Stage 4-9 page pattern (`methodologyParametersPage` and
        `assistantPage` needed `getLocale()` alongside `getTranslations()`
        since both also do locale-dependent work — `toApiLocale`/
        `formatDate` and passing `locale` to `AIAssistantView` respectively;
        `glossaryPage` and `searchPage` needed only `useTranslations()`
        directly, the simpler `AppFooter`/`legalSignalsPage`-style pattern,
        since neither has any other locale-dependent logic).
      - No enum-value-map bugs, no typos, and no untranslated-literal
        section-title-prop mistakes found on the explicit self-check for
        this stage (grepped every touched file for remaining Cyrillic — 3
        hits, all false positives: a `·` middle-dot separator character,
        an em dash, and the `MethodologyAccordion.tsx` `ru`/`es` enum-dict
        values themselves, which are supposed to stay non-English; and
        grepped for bare string literals in
        `title=`/`label=`/`railLabel=`/`aria-label=`-shaped props — zero
        hits across all 19 files, unlike Stage 9's real
        `CountryDossier.tsx` miss).
      - Verify: `i18n_parity_check.py` 1023/1023 keys across en/ru/es (17
        new namespaces + 7 new keys added to the pre-existing `search`
        namespace, 73 new keys total, from 950 after Stage 9);
        `pnpm --filter web typecheck` clean; `pnpm --filter web lint`
        clean; Vitest 5/5; `pnpm format:check` clean (6 files needed a
        `prettier --write` pass, all `Prettier`-only reflow of lines this
        stage's edits pushed past the wrap width, no logic change); fresh
        `next build` clean (45 routes, unchanged from Stage 9 — no route
        added or removed); `python -m pytest tests/test_frontend_contract.py -q`
        clean (8/8).
      - **HTTP-level smoke test done, real browser walkthrough still owed**
        (same tooling gap as Stage 9 — this session also had no Browser-pane
        tools, only Read/Edit/Write/Bash/Grep/Glob). Started the real
        `pnpm dev` server against the already-running, healthy Docker stack
        (API + Postgres + Redis, confirmed via `docker ps`), then `curl`ed
        all 5 pages (`/methodology`, `/methodology/parameters`, `/glossary`,
        `/assistant`, `/search`) in all 3 locales — 15 requests, all HTTP
        200. Grepped every response for leaked `namespace.key`
        missing-translation fallback strings — zero found. Spot-checked
        specific translated strings (page titles/headers, form field
        labels, table column headers, the AI-assistant default question
        text, the methodology accordion's enum meta-labels, the glossary's
        "related terms" label) by exact substring match in all 3 locales'
        HTML — all found correctly translated, no stray English on `/ru`
        or `/es`. This confirms no leaked keys and no obviously-missed
        strings, but it is **not** a substitute for a real interactive
        click-through (submitting the AI-assistant ask form and reading a
        real response, opening the AI-explain-number popover on a country
        page, typing in the glossary/search filters and reading live
        results, expanding a methodology accordion section) — flagged here
        honestly, matching Stage 9's own precedent, rather than claimed as
        done; owed before Final verification's full walkthrough.
      - **Real browser walkthrough done in a follow-up session**, closing the
        gap above: `/methodology` (accordion fully translated chrome —
        section meta-labels, glossary teaser, disclaimer — in all 3 locales;
        the accordion's actual question/answer body text is confirmed
        backend content fetched via `toApiLocale()`, correctly Russian on
        `/ru` and correctly falling back to English on `/es` per the Stage 1
        design — verified by reading `MethodologyAccordion.tsx`'s source,
        not just observing the page, since English content appearing on
        `/es` looks identical to a missed-translation bug at a glance),
        `/glossary` (all 19 terms, categories, and the search/filter chrome
        fully translated in all 3 locales), `/assistant` (chrome fully
        translated in all 3 locales; the AI-assistant components themselves
        — `AIAnswerCard`/`AICitationsList`/`AIRefusalState` — could not be
        exercised live, see bug below, but a static re-read confirmed all
        three call `useTranslations()` with zero remaining hardcoded
        strings), `/search` (chrome, result-type filter, and entity-type
        badges on live search results all fully translated in `/ru` and
        `/es`, result content itself correctly staying in its original data
        language). No translation bugs found this pass — Stage 10's own
        self-check held up under real interaction, unlike Stage 9's.
      - **Real, pre-existing functional bug found (unrelated to translation,
        not fixed in this branch — flagged as a separate background task
        instead, per this project's scope-control rule against mixing
        unrelated fixes into one diff)**: submitting the `/assistant` "Ask a
        question" form always fails with HTTP 403 `"CSRF token is missing or
        invalid."` from `POST /api/v1/ai/ask`. Root cause confirmed by
        reading `shared/api/ai.ts`: its `askAI`/`explainNumber`/
        `parseDecisionIntent` functions call `apiPost(path, payload)`
        without the third `{ headers: csrfHeaders() }` argument that every
        other mutating API module in the app (`migrationBoard.ts`, etc.)
        passes on every `apiPost`/`apiPatch`/`apiDelete` call, per the
        backend's global CSRF middleware
        (`apps/api/app/bootstrap/app_factory.py`). This means the AI
        Assistant feature has likely never worked end-to-end regardless of
        locale or of any stage in this task — pure pre-existing backend/
        frontend wiring gap, nothing to do with hardcoded text. Not fixed
        here; a background task was spawned to fix `shared/api/ai.ts`
        separately from this i18n branch.
      - This is the last content stage — every string budget in the
        original ~154-file survey (`## Scope survey` above) is now
        accounted for across Stages 1-10.

## Final verification (after all stages land)

- [+] Full typecheck/lint/format (`ui` + `web`) — ran
      `python dev_tools_scripts_runner.py full-check --profile full`
      (the interactive default prompt needs a real TTY, so invoked the
      `full-check` script directly with `--profile full` instead of relying
      on the bare no-arg default). Static gate all green: `ruff check`,
      `mypy` (706 source files, 0 issues), `ruff format --check` (708 files
      already formatted), `i18n key parity` (1023/1023 at that point, before
      this pass's own fixes added 2 more keys), design-token contrast audit
      (every text token passes on every background token), `sqlfluff lint`,
      `pytest` (both the main suite and `utils/synthetic_data`),
      `pnpm contracts:generate`, `pnpm quality` (typecheck+lint+format
      across `web`/`ui`), `go vet`. Two real failures surfaced by this same
      run, both investigated and resolved below (`go test`, Playwright
      E2E) — everything else in the 79 OK / 4 WARN (stale local cache dirs,
      harmless) / 1 SKIP (proto codegen, deliberately opt-in) / 2 FAIL
      summary passed.
      - `go test` **FAIL is a known, pre-existing, documented environment
        limitation, not a regression**: `go: -race requires cgo; enable
        cgo by setting CGO_ENABLED=1`. `.ai/project/11-commands.md` already
        documents this exact failure mode for a Windows machine without a
        mingw/gcc toolchain — "the CI job is the actual `-race` gate."
        Nothing in this task touches `apps/notifier` (Go), so there is no
        code change to attribute this to; `go vet` (the part of the Go
        gate that doesn't need cgo) passed clean.
- [+] `next build` clean (45 routes, unchanged), JS-budget script passes:
      `python dev_tools_scripts_runner.py js-budgets` → "JS budget OK: 45
      routes checked, worst is `/[locale]/countries/[slug]` at 298.0 kB
      (ceiling 330 kB)." No default-route-measurement issue in practice —
      the script checks every route uniformly regardless of which locale
      is default.
- [+] Full Vitest: `web` 86/86 (14 files), `ui` 8/8 (3 files) — both clean.
      Storybook (`packages/ui`): `build-storybook` succeeded in 1.18 min,
      output written to `packages/ui/storybook-static` (the two >500 kB
      chunk-size warnings are Storybook's own doc-renderer/MDX bundles, not
      story code, and pre-date this task).
- [+] Full Playwright E2E suite + visual regression — **found and fixed 3
      real, in-scope bugs**, all now resolved and reverified:
      1. **`shared/ui/ErrorBoundary.tsx` double-fault on `/internal/**`**
         (the first bug actually found, via a genuine crash while manually
         re-checking `/internal/data-quality` in the browser, not from the
         E2E run itself — the E2E run's 24 initial failures were the first
         *signal* something was wrong). Stage 3a's Stage-3a-era change made
         `ErrorBoundary`'s fallback call `useTranslations("errorBoundary")`
         unconditionally. `/internal/**` sits outside `[locale]/layout.tsx`'s
         `NextIntlClientProvider` by explicit design (stays untranslated,
         confirmed still out of scope) — so any client-side error inside
         `/internal/**` (this session found `ChunkLoadError: Loading chunk
         app/[locale]/page failed`, itself likely a separate, pre-existing
         Next-dev-mode quirk, not investigated further since it's outside
         this task's remit) triggered `ErrorBoundary`, whose own fallback
         then threw *again* ("Failed to call `useTranslations` because the
         context from `NextIntlClientProvider` was not found"), cascading
         past the custom boundary to the root `app/error.tsx` (which
         already has a documented, deliberate hardcoded-text workaround for
         exactly this scenario) — losing the real recoverable error UI and
         the `insufficient-rights` notices several internal admin pages
         depend on. First attempted a prop-threading fix on `ErrorBoundary`
         itself (optional `labels` prop, `AppShell` passing real translated
         values, `InternalShell` getting a hardcoded default) — reverted it
         after finding the *exact same* crash in `shared/ui/LoadingState.tsx`
         too, proving the prop-threading approach would need repeating for
         every shared component that calls `useTranslations()` and is ever
         reached by `/internal/**` (`LoadingState`, `EmptyState`,
         `DisclaimerNotice`, `ErrorState`, `LastVerifiedAt`, `EvidenceCard`
         are all candidates). Replaced with a single, much smaller fix:
         wrapped `app/internal/layout.tsx`'s `InternalShell` in a
         `NextIntlClientProvider` seeded with the existing `ru.json`
         catalog — `/internal/**`'s own pre-migration language, so nothing
         there needs translating, it just needs *a* working intl context
         for whichever shared component reaches for one. Fixes the whole
         class of bug in one place; confirmed via a clean `.next` rebuild
         and a fresh browser tab that `/internal/data-quality`,
         `/internal/translation-jobs`, `/internal/users` all now render
         their correct (Russian) "insufficient rights" notices instead of
         the generic root-level crash text. Resolved 11 of the 24 E2E
         failures (all `web-mvp-internal-admin.spec.ts` tests, plus
         `web-mvp-auth-rbac.spec.ts`'s data-quality-nav-link test,
         `web-mvp-community-intelligence.spec.ts`'s moderation test, and
         `web-mvp-migration-board.spec.ts`'s moderation test — every one of
         these renders an internal admin page as an anonymous/unauthorized
         user, which is exactly the crash path). Committed as `c8cc2ae`.
      2. **12 E2E tests hardcoded Russian regex/text assertions against
         pages now correctly rendering English** — expected test-fixture
         drift from Stage 1's `DEFAULT_LOCALE` flip (`ru`→`en`), exactly as
         this checklist predicted for the visual suite but not called out
         for the main E2E suite. Two distinct sources: (a) tests explicitly
         requesting `locale: "en"` via `e2eRoutes` helpers but still
         asserting the old Russian heading/button/link text
         (`web-mvp-analytical-pages.spec.ts` ×7 across legal-signals/
         sources/accessibility, `web-mvp-locale.spec.ts` ×1,
         `web-mvp-pages.spec.ts` ×1, `web-mvp-watchlist.spec.ts` ×2); (b)
         bare-URL tests (`/countries`, `/decision`) that now redirect to
         the new default `/en/...` instead of the old default `/ru/...`.
         Fixed by swapping each assertion to the real English string, read
         directly from `en.json`/component source rather than guessed
         (`"Legal signals feed"`, `"Evidence sources"`, `"Country card:
         {name}"`, `"Country: {name}"`, `"Open dossier"`, `"Scenario"`,
         `"Country of origin"`, `"Run the decision engine"`, `"Run a
         country decision"`, `"Save to watchlist"` / `"In watchlist"`) —
         left every genuinely `ru`-scoped assertion untouched, including
         `tests/e2e/helpers/routes.ts`'s own `e2eRoutes.*` helpers (which
         still hardcode `DEFAULT_LOCALE = "ru"` for routes that don't pass
         an explicit locale, by the helper's own design comment, so most of
         the suite was never affected). Verified via an isolated rerun of
         the 4 touched spec files (41/41 passed) before rerunning the whole
         suite. Committed as `4f21d04`.
      3. **Visual regression**: `pnpm web:mvp:visual` — 4/5 passed
         immediately; the 5th (`country dossier`) failed with the page
         17px taller than the baseline (1280×12280 vs the recorded
         1280×12263). Reviewed the diff image: the changed region sits
         right before the footer, exactly where Stage 9 inserted the new
         Community section — already independently confirmed rendering
         correctly via live browser testing earlier in this session, so
         this is the "real, reviewed baseline change" the checklist
         anticipated, not a regression. Ran `web:mvp:visual:update`,
         reran `web:mvp:visual` clean (5/5). Committed as `6bb3a1f`.
      - Final full-suite state: `pnpm exec playwright test` (main E2E) —
        325+ passed, the only failures across two full-suite runs were 3
        tests that also showed up as "flaky" on Playwright's own retry and
        were confirmed passing in a clean isolated rerun (parallel-worker
        resource contention on this local machine, not a code issue, and
        none of the 3 overlap with anything this task touched:
        `web-mvp-argentina-cii.spec.ts` responsive/compare test,
        `web-mvp-argentina-legal-timeline.spec.ts` timeline test, and one
        already-fixed `web-mvp-analytical-pages.spec.ts` test that passed
        cleanly both before and after in isolation). `web:mvp:visual` — 5/5
        clean after the one reviewed baseline update.
      - **Real, pre-existing, out-of-scope bug found and flagged
        separately, not fixed here**: `shared/api/ai.ts`'s `askAI`/
        `explainNumber`/`parseDecisionIntent` never pass
        `{ headers: csrfHeaders() }` to `apiPost`, unlike every other
        mutating API module in the app — the AI Assistant's "Ask a
        question" form always 403s with `"CSRF token is missing or
        invalid."` regardless of locale or session. Confirmed live in the
        browser and via the backend's own CSRF middleware
        (`apps/api/app/bootstrap/app_factory.py`). Purely a missing-header
        wiring bug, nothing to do with hardcoded text or i18n — flagged as
        a separate background task rather than folded into this branch's
        diff, per the project's scope-control rule.
- [+] Contrast + i18n-parity audits: contrast audit passed as part of the
      full gate above. `i18n_parity_check.py` run standalone one final time
      after all fixes: **1023/1023 keys match across `en.json`, `ru.json`,
      `es.json`** (692 after Stage 8 → 950 after Stage 9 → 1023 after
      Stage 10; this session's own bug-fix pass added the `railCommunity`/
      `titleCommunity` pair, +2 keys, already included in the 1023 total —
      no parity drift anywhere across all 10 stages plus this pass's own
      fixes).
- [+] Browser walkthrough of all 3 locales across every migrated area —
      done across two passes this session: (1) closing Stage 9's and Stage
      10's own flagged real-interactive-walkthrough gap (both of those
      stages' agent sessions lacked Browser-pane tools) — registered a
      real throwaway account, filled and submitted a real migration-board
      post through the actual form UI (all selects read back correctly),
      confirmed it in `/account/migration-board` with translated status/
      action labels, walked `/migration-board`, `/migration-board/new`,
      `/account/author-metrics`, `/account/country-proposals`, the
      `CommunityCountryBlock` on a real country page, `/methodology`,
      `/glossary`, `/assistant` (submitted a real question — this is what
      surfaced the CSRF bug above), `/search` (live query + result-type
      filter) across `/en`/`/ru`/`/es`; found and fixed the `ru.json`
      untranslated-string bugs and the `CountryDossier.tsx` hardcoded-
      "Community" bug documented in Stage 9's entry above. (2) A final
      consolidated pass across areas from earlier stages not otherwise
      re-touched this session: `/es/countries/argentina` full dossier
      (CII, platform intelligence, trust, scores, routes, migration board
      block, what-changed, legal signals, sources, evidence, user stories,
      community — all sections, all 3 locales spot-checked), `/es/compare`
      (chrome translated, scenario/country content correctly untranslated
      per the content-vs-chrome boundary, confirming Stage 3b's locale-cast
      bug fix still holds), `/es/routes/monotributo` (not-found error state
      fully translated), `/en/trips`, `/ru/subscriptions`, `/es/account`
      (profile, Telegram link, active sessions, all fully translated). No
      new translation bugs found in this second pass. Two pre-existing,
      out-of-scope oddities re-confirmed as backend content data, not
      frontend bugs: the CII/scenario methodology disclaimer text
      (`database/fixtures/demo_countries/country_scores.json`) and mixed
      English/Russian scenario names in dropdowns (`/api/v1/scenarios`
      response itself already mixes languages at the data layer, per
      `MigrationBoard`/`UserStories`/`Trips` scenario pickers) — both
      confirmed via source/API inspection, not just visual guessing.
- [+] Updated `docs/_arch_/08_Открытые_вопросов.md`'s Р-12: struck through
      the superseded "ru-only interface" decision, dated the new one
      2026-07-19, summarized the full 10-stage migration (154-file scope,
      90→1023 catalog keys, the `toApiLocale` content-vs-chrome boundary),
      and pointed to `task-checklist.md` as the detailed record rather than
      duplicating it in the architecture doc.
- [+] Known non-blocking gaps, confirmed still accurate and not silently
      fixed mid-verification: the pre-existing `Негативное`/`Отрицательное`
      Russian wording inconsistency (Stage 7, not introduced by this task);
      backend *content* staying in its original language regardless of
      interface locale (explicit scope boundary, not a bug — re-confirmed
      twice more this session via the CII-disclaimer and scenario-name
      findings above); `packages/ui`'s `Breadcrumbs` `ariaLabel` default
      still hardcoded Russian on all 4 call sites (Stage 9, screen-reader-
      only); **new this session**: the CSRF-header bug in `shared/api/ai.ts`
      (flagged as a separate background task, not this branch's diff).

## Completion

- [ ] Checklist filled (`+`/`-`) — stages 1–8 above are already `[+]`
      with full writeups; only Stage 9, Stage 10, Final verification, and
      this Completion section remain `[ ]`.
- [ ] Incremental commits on this branch, one per stage (9 of 10 done;
      commits so far: `6554d7f` Stage 1, `47fc596` Stage 2, `425c199`
      Stage 3a, `8747a19` Stage 4, `1461d77` Stage 5, `58781f0` Stage 6,
      `e538e6f` Stage 7, `71ff01f` Stage 8, `2a64476`/`74cc747` Stage 9,
      `37472d8` Stage 9 browser-walkthrough fixups).
- [ ] Final report — summarize what shipped, total namespaces/keys added
      across all 10 stages, any deferred tech debt (the two items in the
      Final-verification gaps list above), and confirm the branch's
      relationship to `main` (currently pushed to `origin` only, per
      owner's 2026-07-19 decision to defer the `main` merge until this
      checklist and the full quality gate are both green).
