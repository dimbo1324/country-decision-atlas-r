# Task: Frontend redesign Stage 3 (registries and cabinet)

Owner-approved plan, continuing directly on `main` (established pattern for
this whole redesign initiative — stages 0-2 landed there too). Sub-staged
like stages 1-2, each its own commit, full verification before moving on.

Scope correction from the original plan, based on a read-only survey before
starting any edits:
- Trips and watchlist are **already card grids**, not plain lists — the
  "card-board" work narrows to (a) extracting the duplicated grid classes
  into one shared primitive, (b) converting **subscriptions**, the one
  genuinely plain list, to match.
- All five domains touched here (legal-signals, sources, trips, watchlist,
  subscriptions) are **already migrated** to the `entities/*` queryOptions
  pattern — the plan's "Этап 4 (слой данных)" has no remaining work for
  this wave.
- `apps/web/src/shared/api/watchlists.ts` looks like dead code superseded
  by `entities/watchlist/api.ts`'s own client — flagged as a separate
  tech-debt item, not fixed in this wave (unrelated to the redesign).

## Stage 3.1 — Legal signals: fold timeline into a tab

- [ ] Merge `LegalSignalsTimelineView` (year-group feed) and
      `LegalSignalsChartView` (chart) into one `LegalSignalsRegistryView`
      on `/legal-signals`, tabbed (`Лента` / `Таймлайн`, Radix `Tabs`
      matching `CountryDossier`'s convention), tab state via nuqs `?tab=`.
- [ ] Hoist the 5 filter query-states (`country_slug`, `signal_type`,
      `impact_direction`, `impact_level`, `year`) up one level so both
      tabs share one filter bar instead of each duplicating it.
- [ ] Delete `apps/web/src/app/[locale]/legal-signals/timeline/page.tsx`;
      old URL redirects to `/legal-signals?tab=timeline`.
- [ ] Fold `features/legal-signals-chart/` into `features/legal-signals-timeline/`
      (move `adaptTimelineEvents.ts`, delete the now-empty chart feature dir).
- [ ] Rewrite the 3 pinned tests in `web-mvp-knowledge-transparency.spec.ts`
      (new URL shape, new testids) plus anything in
      `web-mvp-legal-signals-timeline.spec.ts` that assumes the old split.
- [ ] Verify: typecheck/lint, targeted e2e re-run, browser walkthrough
      (both tabs, filters persist across tab switch, old timeline URL
      redirects).

## Stage 3.2 — Legal signals + sources: chip filters

- [ ] New `packages/ui` primitive: `FilterChipGroup` (single-select toggle
      row, button-based, `aria-checked` + accessible name — not a native
      `<select>`), Storybook story.
- [ ] Convert `TimelineFilters` (5 fields) and `SourcesFilters` (3 fields)
      from `<select>` dropdowns to `FilterChipGroup`.
- [ ] Update e2e assertions that currently read `.toHaveValue()` on
      `#timeline-country`/`#src-country` to chip-based assertions
      (`aria-checked` / accessible name) — touches
      `web-mvp-analytical-pages.spec.ts`,
      `web-mvp-legal-signals-timeline.spec.ts`.
- [ ] Verify: typecheck/lint, targeted e2e, visual check (filter bar at
      mobile width).

## Stage 3.3 — Cabinet: shared board grid, subscriptions card conversion

- [ ] New `packages/ui` primitive: `BoardGrid` (the
      `grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3` pattern
      duplicated in `TripListView.tsx` and `WatchlistView.tsx`).
- [ ] Adopt `BoardGrid` in `TripListView.tsx` and `WatchlistView.tsx`
      (behavior-neutral refactor — same markup, shared primitive).
- [ ] Convert `SubscriptionsView.tsx`'s plain `border-b` row list to
      `BoardGrid` cards.
- [ ] Update `web-mvp-subscriptions.spec.ts` testids/structure as needed
      (keep `subscriptions-list`/`subscription-item`/
      `subscription-remove-button` contracts where possible).
- [ ] Verify: typecheck/lint, targeted e2e, visual check.

## Final verification (after 3.1-3.3 all land)

- [ ] Full Playwright suite green (or isolated-passing flakes only,
      confirmed by re-running the specific spec alone).
- [ ] Visual regression suite green (re-shoot baselines once at the end
      of the whole wave, not per commit).
- [ ] `packages/ui`/`apps/web` typecheck/lint/build clean.
- [ ] Contrast + i18n-parity audits still green.
- [ ] Browser walkthrough of all Stage 3 surfaces.

## Completion

- [ ] Fill this checklist (`+`/`-`).
- [ ] Commit(s) directly on `main`, each sub-stage its own commit.
- [ ] Final report.
