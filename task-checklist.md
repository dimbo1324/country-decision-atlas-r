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

- [ ] Knowledge + AI Assistant + Search (14 files + 4 pages) — not yet
      surveyed this session. Before starting: glob
      `apps/web/src/features/{methodology,glossary,scenarios,assistant,search}/**/*.tsx`
      (or whatever the actual folder names turn out to be — methodology,
      glossary, and scenarios pages already exist per the route list seen
      in every `next build` output this session:
      `/methodology`, `/methodology/parameters`, `/glossary`, `/scenarios`,
      `/assistant`, `/search`) and cross-check each file's importers
      against `app/internal/**` the same way Stage 9 does, in case any of
      these also have an internal-only sibling. This is the last content
      stage — after it lands, every string budget in the original ~154-file
      survey (`## Scope survey` above) should be accounted for; if the
      actual file count comes in noticeably different from the "14 files"
      estimate, that's expected (every stage this session did) — just
      record the real number.

## Final verification (after all stages land)

- [ ] Full typecheck/lint/format (`ui` + `web`) — run
      `python dev_tools_scripts_runner.py` (default full profile) rather
      than the piecemeal per-stage commands used mid-task; it also covers
      Python/Go/Docker/pre-commit that individual stages didn't need to
      touch.
- [ ] `next build` clean, JS-budget script passes (the budget script is
      part of the full quality gate; check its output specifically since
      English becoming the default locale changes which bundle is
      measured as the "default" route).
- [ ] Full Vitest, Storybook build (`packages/ui` — not touched since
      Stage 2, should still be clean, but confirm).
- [ ] Full Playwright e2e suite + visual regression — **expect real,
      reviewed baseline changes**: English is now the default locale for
      every "no explicit locale" screenshot, so `pnpm web:mvp:visual`
      baselines from before this task will show diffs on purpose, not by
      regression. Review each diff before running
      `web:mvp:visual:update` — a diff that isn't just
      Russian-text-becoming-English-text is a real bug.
- [ ] Contrast + i18n-parity audits (parity now covers 3 locales — rerun
      `i18n_parity_check.py` one final time across the fully-merged
      namespace set from all 10 stages, not just the last stage's delta).
- [ ] Browser walkthrough of all 3 locales across every migrated area —
      not just Stage 9/10's new areas; a final end-to-end pass of the
      whole `[locale]` tree (nav, footer, home, catalog, compare, country
      dossier, decision flow, legal signals, sources, routes, trips,
      watchlist, subscriptions, account, migration board, stories, author
      metrics, country proposals, methodology, glossary, scenarios,
      assistant, search) in `/en`, `/ru`, `/es`. **Must include a real
      interactive click-through of Stage 9's areas specifically** (create a
      migration board post through the actual form UI, submit an author
      metric, step through the country-proposal wizard, post a community
      question/answer/report/rating) — Stage 9 itself only had HTTP-level
      tool access (no Browser-pane tools that session) and substituted
      `curl`-driven checks against a real running stack, which is not
      equivalent to a real click-through; see Stage 9's own entry above for
      exactly what was and wasn't covered that way.
- [ ] Update `docs/_arch_/08_Открытые_вопросов.md`'s Р-12 (documented
      "ru-only interface, next-intl scoped to chrome" as the accepted
      state) — supersede with the new decision and date: English default,
      Russian and Spanish as full peers, `es` falls back to `en` for
      backend *data* (not chrome) per the Stage 1 `toApiLocale` design.
- [ ] Known non-blocking gaps to note in the final report, not silently
      fix mid-verification (each already flagged in its stage's checklist
      entry, listed here for one place to check they're either accepted
      or filed separately): the pre-existing `Негативное`/`Отрицательное`
      Russian wording inconsistency for the same "negative" impact-
      direction enum value across two different label sources (flagged in
      Stage 7's browser walkthrough, not introduced by this task); backend
      *content* (country names, scenario names, source excerpts, event
      summaries) staying in its original language regardless of interface
      locale — this is the explicit, owner-confirmed scope boundary for
      this whole task, not a bug; `packages/ui`'s `Breadcrumbs` component's
      `ariaLabel` prop still defaults to the hardcoded Russian
      `"Хлебные крошки"` regardless of interface locale on all 4
      `AppBreadcrumbs` call sites app-wide (`routes/[id]`,
      `trips/[id]`, `decision/passports/[token]`, and Stage 9's own
      `migration-board/[id]`) — a Stage 2 default nobody has wired to a
      translated value yet, screen-reader-only (flagged, not fixed, in
      Stage 9's entry above since fixing it touches pages from 3 different
      already-shipped stages).

## Completion

- [ ] Checklist filled (`+`/`-`) — stages 1–8 above are already `[+]`
      with full writeups; only Stage 9, Stage 10, Final verification, and
      this Completion section remain `[ ]`.
- [ ] Incremental commits on this branch, one per stage (9 of 10 done;
      commits so far: `6554d7f` Stage 1, `47fc596` Stage 2, `425c199`
      Stage 3a, `8747a19` Stage 4, `1461d77` Stage 5, `58781f0` Stage 6,
      `e538e6f` Stage 7, `71ff01f` Stage 8, `2a64476` Stage 9).
- [ ] Final report — summarize what shipped, total namespaces/keys added
      across all 10 stages, any deferred tech debt (the two items in the
      Final-verification gaps list above), and confirm the branch's
      relationship to `main` (currently pushed to `origin` only, per
      owner's 2026-07-19 decision to defer the `main` merge until this
      checklist and the full quality gate are both green).
