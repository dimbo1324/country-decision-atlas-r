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

## Stage 3.1 — Legal signals: fold timeline into a tab (done)

- [+] Merged `LegalSignalsTimelineView` (year-group feed) and
      `LegalSignalsChartView` (chart) into one `LegalSignalsRegistryView`
      on `/legal-signals`, tabbed (`Лента` / `Таймлайн`, Radix `Tabs`
      matching `CountryDossier`'s convention), tab state via nuqs `?tab=`
      (`feed` default, `timeline`).
- [+] Hoisted the 5 filter query-states (`country_slug`, `signal_type`,
      `impact_direction`, `impact_level`, `year`) to the merged view so
      both tabs share one filter bar and one data fetch instead of each
      duplicating both.
- [+] `apps/web/src/app/[locale]/legal-signals/timeline/page.tsx` is now a
      redirect (`i18n/navigation`'s locale-aware `redirect()`) to
      `/legal-signals?tab=timeline`, forwarding any filter query params
      from the old URL so saved filtered links keep their meaning.
- [+] Folded `features/legal-signals-chart/` into
      `features/legal-signals-timeline/` (`adaptTimelineEvents.ts` moved
      via `git mv`, `LegalSignalsChartView.tsx` deleted — its logic lives
      in the merged view now; the chart primitive itself is unaffected,
      it lives in `packages/ui`). Removed the now-dead
      `routes.legalSignalsTimeline` constant from `shared/lib/routes.ts`
      (nothing in the app links to it anymore — the merged page handles
      both views via the tab).
- [+] Rewrote the 3 pinned tests in `web-mvp-knowledge-transparency.spec.ts`
      for the new URL shape (`?tab=timeline`) and new testids
      (`legal-signals-view-panel-timeline`); `web-mvp-legal-signals-timeline.spec.ts`
      and the legal-signals section of `web-mvp-analytical-pages.spec.ts`
      needed no changes — both already exercised the default `feed` tab
      through `e2eRoutes.legalSignals(...)`, unaffected by the merge.
- [+] Verify: typecheck/lint clean; targeted e2e (27 tests across the 3
      affected + adjacent spec files) — all green; browser walkthrough —
      both tabs render, filter selection (country) persists across a tab
      switch via a real click (not raw DOM `.click()`, which silently
      no-ops on Radix's Tabs — same raw-DOM-simulation pitfall documented
      earlier in this project for native `<select>`), old
      `/legal-signals/timeline?country_slug=uruguay` URL redirects to
      `/legal-signals?tab=timeline&country_slug=uruguay` with the filter
      preserved, console clean.

## Stage 3.2 — Legal signals + sources: chip filters (done)

- [+] New `packages/ui` primitive: `FilterChipGroup` (single-select toggle
      row, real `role="radio"` buttons — the visible label text is the
      accessible name, not a styled `<select>`), Storybook story.
- [+] Converted `TimelineFilters` (5 fields: country/signal-type/
      impact-direction/impact-level/year) and `SourcesFilters` (3 fields:
      country/type/confidence) from `<select>` dropdowns to
      `FilterChipGroup`. Bonus fix found while converting: source-type
      chips (`government`/`news`/`academic`/…) and confidence chips
      previously showed raw English/lowercase values in the `<select>`
      options (unlike `TimelineFilters`, which already had Russian
      labels) — added a `SOURCE_TYPE_LABELS` map and reused the existing
      `confidenceLabelRu()` export so both filter bars are consistently
      Russian.
- [+] Updated e2e assertions that read `.toHaveValue()` on
      `#timeline-country`/`#src-country` to chip-based assertions
      (`getByTestId("<name>-chip-<value>")` +
      `toHaveAttribute("aria-checked", "true")`) — touched
      `web-mvp-analytical-pages.spec.ts` (2 assertions),
      `web-mvp-legal-signals-timeline.spec.ts` (1),
      `web-mvp-knowledge-transparency.spec.ts` (1, already rewritten in
      3.1, needed a second pass here for the chip change).
- [+] Verify: typecheck/lint clean (web+ui); 27 targeted e2e green after
      diagnosing a false alarm — the first run showed 25/27 failing
      including completely unrelated pages (glossary, methodology,
      data-quality), traced to a stale `next start` process still bound
      to port 3000 from Stage 3.1's browser walkthrough serving
      mismatched chunks against the just-rebuilt `.next` output, not a
      code regression; killing that process and re-running gave a clean
      27/27. Browser walkthrough: chips render with correct Russian
      labels, a real click (via the `computer` tool, not raw JS
      `.click()`) flips `aria-checked` and updates the URL query param,
      no horizontal overflow or wrapping issues at 375px, console clean
      on both `/sources` and `/legal-signals`.

## Stage 3.3 — Cabinet: shared board grid, subscriptions card conversion (done)

- [+] New `packages/ui` primitive: `BoardGrid` (the
      `grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3` pattern
      duplicated in `TripListView.tsx` and `WatchlistView.tsx`), forwards
      `data-testid` and the rest of `<div>`'s props so each caller keeps its
      own grid testid. Exported from `packages/ui/src/index.ts`, Storybook
      story added.
- [+] Adopted `BoardGrid` in `TripListView.tsx` and `WatchlistView.tsx`
      (behavior-neutral refactor — same markup/testids, just routed through
      the shared primitive instead of each duplicating the raw grid
      className).
- [+] Converted `SubscriptionsView.tsx`'s plain `border-b` row list to
      `BoardGrid` cards, matching the visual language of the trips/watchlist
      cards (title, metric-slug badge, "Отписаться" button); the separate
      `feedItems`/`TimelineList` feed section was left untouched, as scoped.
- [+] `web-mvp-subscriptions.spec.ts` needed no changes — it only asserts on
      `subscriptions-list`/`subscription-item`/`subscription-remove-button`
      testids, all of which the card conversion preserved; verified this by
      reading the spec before making any edits.
- [+] Verify: typecheck/lint clean (`ui`+`web`), `pnpm format:check` clean;
      `next build` clean; 17 targeted e2e green
      (`web-mvp-trips.spec.ts`/`web-mvp-watchlist.spec.ts`/
      `web-mvp-subscriptions.spec.ts`) after stopping a stale `web-prod`
      preview server left over from an earlier stage (same
      port-3000-reuse pitfall as Stage 3.2, caught before it could cause a
      false-alarm run this time); browser walkthrough — created a trip and
      a watchlist entry and a subscription through real UI actions, each
      landed in a `BoardGrid` with the correct grid className and
      testid/child count, deleted the subscription and confirmed the empty
      state returns, no horizontal overflow at 375px, console clean.

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
