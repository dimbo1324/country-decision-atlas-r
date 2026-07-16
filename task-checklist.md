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

- [+] `database/migrations/056_web_dossier_v2_flag.sql`: seeds
      `web_dossier_v2` into `feature_flags` (disabled/internal by default)
      plus a paired `feature_access_rules` row, matching migration 030's
      convention exactly. sqlfluff-clean.
- [+] Applied migration locally, confirmed idempotent (applied twice).
- [+] Extracted the 17 sections' JSX into `CountryDossier.tsx`
      (`apps/web/src/features/country-card/CountryDossier.tsx`) — one
      `sections` array built once via `useMemo`, both the old (flat) and
      new (tabbed) layouts render from it, so the two layouts cannot drift
      out of sync. Every existing `data-testid` preserved exactly.
- [+] `CountryDossier` component: Radix `Tabs`, `value` synced via
      `useQueryState("tab", parseAsStringEnum(...))` (nuqs), 5
      `TabsTrigger`s, each `TabsContent` a `grid lg:grid-cols-2` with wide
      blocks (community, migration-board, sources, legal-signals) spanning
      `lg:col-span-2`, `DossierRail` fed only the active tab's sections.
- [+] `CountryPage` (`[slug]/page.tsx`, Server Component): unchanged
      data-fetch; shrank from ~289 to ~99 lines — section rendering now
      delegates entirely to `<CountryDossier card={card} locale={locale}>`,
      which reads `useFeatureEnabled("web_dossier_v2")` client-side and
      picks flat vs. tabbed. Flag check stays client-only, matching the
      one proven precedent (`CountryDataJournalBlock`); no SSR threading
      attempted.
- [-] Update dossier-touching E2E specs to add "open tab X" steps: NOT
      needed in practice — every existing spec still passes unchanged
      because the flag defaults off (flat layout, identical DOM/testids to
      before). Verified via a 20-file / 183-test regression run (183
      passed, 1 pre-existing flaky, 0 new failures). No spec required a
      non-default tab to reach its target testid.
- [+] New E2E coverage for the flag: added
      `"dossier renders the flat rail layout by default (web_dossier_v2
      disabled)"` in `web-mvp-argentina-core-country.spec.ts` — asserts
      the rail is present, `country-dossier-tabs`/`tablist` are absent.
      The tabbed on-state was NOT covered by an automated spec — there is
      no admin write endpoint for feature flags in this codebase (GET
      `/platform/features` is read-only), so flipping the flag on inside
      an E2E run isn't cleanly possible without direct DB access. Matches
      the same negative-only coverage pattern already used for other
      capability-gated surfaces (author-metrics, country-proposals,
      migration-board). The on-state was verified manually instead: all 5
      tabs, correct section grouping, `?tab=` deep-linking, zero console
      errors, against a live DB flag flip (both `feature_flags` and
      `feature_access_rules` rows, then reverted back to seeded defaults
      after verification).

## 1.2 — Catalog card redesign

- [-] `CountryCatalogCard.tsx`: add `ProgressRing` (CII, size~56) — SCOPED
      OUT. Verified via `packages/contracts/generated/types.ts`: the
      `Country`/`CountryListResponse` schemas returned by the catalog's
      list endpoint carry no `cii_score` field at all (only the unrelated
      `ComparedCountry` schema, used by `/compare`, has one). Rendering a
      CII ring on the catalog card would need a backend/contract change
      (new field on the list response, or an N+1 per-card fetch) — out of
      scope for a frontend-only wave per `.ai/project/12-domain-rules.md`'s
      contract-change rules. Flagging as backend follow-up, not attempting
      a workaround (e.g. per-card fetch) that would introduce N+1 calls.
- [-] Trend arrow from drift value — SCOPED OUT, same root cause: no
      `country_drift` field on the list response either. Same reasoning
      as the CII item above; both would ship together once the backend
      adds an enrichment field.
- [+] `WatchlistStar` — checked before touching: already a compact,
      icon-only button (`Star` icon from lucide-react, absolutely
      positioned, 8x8). No changes needed, no new variant added.
- [-] Sticky filter/sort panel in `CountryCatalogView.tsx` — SCOPED OUT.
      Read the file in full first: there is currently NO filter/sort UI at
      all (only `useQueryState("page", ...)` pagination). The plan's
      "make it sticky" premise assumes filters already exist; building
      filter/sort UI from scratch is a materially larger, different task
      (new query params, new API usage, new controls, new tests) than
      "add position: sticky" and doesn't belong in this wave without an
      explicit go-ahead. Flagging as its own follow-up task.
- [+] Grid density: read current breakpoints first (`sm:grid-cols-2
      lg:grid-cols-3`, no existing `xl:` step — plan's premise of an
      existing `xl:grid-cols-3` didn't hold either). Added
      `xl:grid-cols-4` to both the real items grid and the loading
      skeleton (`CatalogSkeletonGrid`) in
      `apps/web/src/features/country-catalog/CountryCatalogView.tsx`, so
      the loading state's column count matches the loaded state's —
      avoids a layout shift between skeleton and real content on wide
      screens. Typecheck/lint/prettier all clean after the change.

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
