# Task: Frontend redesign — Этап 1 (Волна «Навигация и обзор»)

Source: owner-provided plan (pasted in chat), §1. Follows Этап 0
(`c622288`, merged). Branch: `feat/frontend-navigation-overview-v1`, fresh
off `main`.

Three sub-waves: 1.1 dossier tabs (main work), 1.2 catalog card redesign,
1.3 home page horizontal deck.

## 1.1 — Country dossier: tabs behind `web_dossier_v2`

### Current state (verified, not assumed — see Stage 0's exploration)

- `apps/web/src/app/[locale]/countries/[slug]/page.tsx`: Server Component,
  RSC-fetches `card` via `countriesApi.getCountryCard(slug, locale)`, then
  renders **17** sections as a flat vertical stack, each wrapped in a
  `DossierSection` helper (`id` + `scroll-mt-24` + `Card`), plus an existing
  `<DossierRail sections={RAIL_SECTIONS} />` (scrollspy nav, already
  working, already used a second place — the country-proposal wizard).
- `DossierRail` (`packages/ui/src/shell/DossierRail.tsx`) takes a flat
  `{id,label}[]` and needs no changes — feeding it a filtered subset per
  active tab is enough.
- `Tabs`/`TabsList`/`TabsTrigger`/`TabsContent`
  (`packages/ui/src/primitives/Tabs.tsx`) are thin Radix wrappers with the
  full controlled `value`/`onValueChange` API already available — no
  primitive changes needed.
- `useFeatureEnabled(key)` (`apps/web/src/shared/features/FeatureProvider.tsx`)
  is the proven gating pattern (one real precedent:
  `CountryDataJournalBlock.tsx`) — returns `false` while `/platform/features`
  is still loading, which is exactly the safe default (old layout) with no
  extra code needed.

### Tab grouping (my own reasoned mapping — the plan's grouping didn't
account for 2 of the 17 real sections, `profile` and `locale-status`,
since it was written against an outdated "13 sections" premise)

- **Обзор**: `overview` (exec summary), `cii`, `evidence`, `what-changed`,
  `profile` (general country-profile text — fits as extended overview
  content), `locale-status` (meta/translation status — not really
  "content", grouped with overview as the closest fit)
- **Оценки**: `scores`, `platform-intelligence`, `drift`
- **Доверие**: `trust`, `sources`, `data-journal`
- **Сигналы**: `legal-signals`, `routes`
- **Сообщество**: `user-stories`, `community`, `migration-board`

### Implementation

- [ ] `database/migrations/056_web_dossier_v2_flag.sql`: seed
      `web_dossier_v2` into `feature_flags` (disabled/internal by default),
      matching migration 030's `INSERT ... ON CONFLICT (key) DO NOTHING`
      pattern exactly.
- [ ] Apply migration locally, confirm idempotent (apply twice).
- [ ] Extract the 17 sections' JSX into one place both the old (flat) and
      new (tabbed) layouts render from — no duplicated markup, so there is
      no way for the two layouts to drift out of sync with each other.
      Every existing `data-testid` preserved exactly.
- [ ] New client component (`CountryDossierTabs` or similar, in
      `features/country-card/`): Radix `Tabs`, `value` synced via
      `useQueryState("tab", ...)` (nuqs — proven pattern, copy
      `CountryCatalogView.tsx`'s usage), 5 `TabsTrigger`s, each
      `TabsContent` a `grid lg:grid-cols-2` (heavy/wide blocks —
      community, migration-board, sources, legal-signals — span
      `lg:col-span-2`), `DossierRail` fed only the active tab's sections.
- [ ] `CountryPage` (Server Component): unchanged data-fetch; the
      section-rendering portion moves into one client wrapper that reads
      `useFeatureEnabled("web_dossier_v2")` and picks old-vertical vs.
      new-tabbed — flag check stays entirely client-side, matching the one
      proven precedent, no attempt to thread it through SSR.
- [ ] Update `tests/e2e/web-mvp-*` dossier-touching specs to add "open tab
      X" steps where a test now needs a non-default tab active
      (`argentina-core-country`, `country-drift`, `trust-transparency`,
      `platform-intelligence`, `community-intelligence`, `what-changed`,
      `routes` — the plan's own flagged "largest test tail"). Old-layout
      assertions keep working unchanged since the flag defaults off.
- [ ] New E2E coverage specifically for the flag: enabling
      `web_dossier_v2` renders tabs, disabled (default) renders the
      existing flat layout — both against the same page.

## 1.2 — Catalog card redesign

- [ ] `CountryCatalogCard.tsx`: add `ProgressRing` (CII, size~56) — confirm
      CII score is already present on the list-item shape from
      `countryListQuery`'s response before adding.
- [ ] Trend arrow from drift value (sage=positive/terra=negative) — same
      data-availability check first.
- [ ] `WatchlistStar` — check its current implementation before assuming a
      new `variant="icon"` prop is needed; it may already be icon-only.
- [ ] Sticky filter/sort panel in `CountryCatalogView.tsx`.
- [ ] Grid density: confirm current breakpoints before changing (plan
      assumes `sm:grid-cols-2 lg:grid-cols-3`, adds `xl:grid-cols-3`).

## 1.3 — Home page horizontal deck

- [ ] Port `HorizontalPager` + `MobileStack` from
      `apps/web-prototype/src/components/shell/` into
      `packages/ui/src/shell/` (genuinely new — neither exists there yet,
      confirmed in Stage 0's exploration pass).
- [ ] Wrap `CountryOverviewCards`/`ScenarioWinnersPanel`/
      `HomeMatrixPreview`/`LatestLegalEventsPanel`+`KeyInsightsPanel` in the
      deck. Hero/CTA untouched (per the plan).
- [ ] Mobile: scroll-snap degradation; `prefers-reduced-motion`: vertical
      column (design-system §6.3: three zones, no scroll-offset caching,
      debounced resize).

## Verification (per wave, before merge)

- [ ] `packages/ui`/`apps/web` typecheck/lint/build clean.
- [ ] Full Playwright suite (flag off = default: old layout everywhere,
      zero visible change to existing behavior; flag on: new layout works).
- [ ] Manual check: dossier page with flag on and off, catalog page,
      home page — in a real browser.
- [ ] Visual baselines re-shot once at the end of the whole wave (per the
      plan's own rule — not per commit).

## Completion

- [ ] Fill this checklist (`+`/`-`).
- [ ] Final report.
