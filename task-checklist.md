# Task: Frontend Stage 5 (home, country catalog, search)

Source plan: `docs/_arch_/FRONTEND_IMPLEMENTATION_PLAN.md`, §7 Этап 5.
Branch: `feat/frontend-stage5-home-catalog-search` (fresh off `main` — Stages
1-4 already merged and their branches deleted).

## Preparation

- [+] Confirmed Stages 1-4 are merged into `main` (git log, `pre-frontend-milestone`
      tag context) — this branch builds directly on top.
- [+] Read `FRONTEND_IMPLEMENTATION_PLAN.md` in full (all 13 stages, not just
      §5) for architectural decisions (Р-1..Р-10) that constrain this stage.
- [+] Surveyed via 3 parallel research agents: prototype hero/deck components
      (`HeroSlide`, `HorizontalPager`/`MobileStack`/`SlideSection`, no
      dedicated country-card component exists — closest analog is inline in
      `CommunitySlide.tsx`), current `apps/web` state of home/countries/search
      pages (all three still on old `styles.css` classes + `useEffect`/
      `useState` fetch pattern, `CommandPalette` already Stage-3-styled but
      static-only), `packages/ui` full export surface post-Stage-4 and the
      Stage-3 "one module per domain" query pattern (`entities/country/api.ts`
      exists but has zero consumers yet).
- [+] Read exact prop signatures directly (not just the agent summaries) for
      `Card`, `Button`, `Kicker`, `Icon`/`IconFrame`, `Badge`, `MetricCard`,
      `ProgressRing`, `EmptyState`, `ErrorState`, `Skeleton` — all in
      `packages/ui/src/primitives/*` and `charts/ProgressRing.tsx`.
- [+] Read `AppShell.tsx` — `<main>` already provides
      `mx-auto max-w-[1400px] px-6 py-8`; page components must not add their
      own outer page-shell wrapper.
- [+] Confirmed exact contract shapes: `Country` (list item — **no CII/score
      field**, just metadata: slug/iso2/iso3/name/region/subregion/capital),
      `HomeOverviewResponse.countries_summary` (**does** have
      `average_score`/`confidence`/best-worst scenario), `SearchResponse`/
      `SearchResultItem`, `WatchlistResponse`/`WatchlistItem` (bulk list
      endpoint exists: `GET /me/watchlist`).
- [+] Read all 5 home-overview panel components + `SearchView`/`SearchFilters`/
      `SearchResultCard` + `WatchlistButton` (detail-page only, not reused
      for the catalog — see design decisions) to know every `data-testid` and
      prop shape that must survive the reskin.
- [+] Read `tests/e2e/web-mvp-home-overview.spec.ts` and the `/countries`
      section of `web-mvp-pages.spec.ts` in full to know exactly which
      `data-testid`s and text assertions must keep passing.

## Design decisions (recorded before writing code)

- [+] **Catalog cards do not get a CII `ProgressRing`.** The plan's own
      component table asks for one, but `GET /countries` (the catalog's only
      data source) returns plain metadata — no score, no confidence. Faking a
      number instead of fetching per-card (N+1) would violate the project's
      own guardrail (every number needs a real source/confidence). Catalog
      cards show name/flag/region/iso2 + watchlist star; the CII `ProgressRing`
      pattern instead goes on the **home page's** "Country overview" cards,
      which are already backed by `home/overview`'s `countries_summary`
      (real `average_score`/`confidence`).
- [+] **Watchlist star is a new component, not `WatchlistButton` reused.**
      `WatchlistButton` (country detail page) fetches per-mount status via
      one `GET .../watchlist-status` call per country — fine for one card,
      an N+1 problem across a whole catalog grid. New `WatchlistStar` instead
      reads from a single `GET /me/watchlist` (`myWatchlistQuery`, one fetch
      for the whole grid) and does an optimistic toggle mutation invalidating
      `['me','watchlist']`, exactly the pattern the plan asks for. Detail-page
      `WatchlistButton` is untouched (out of scope — Stage 6).
- [+] **No flag-emoji library.** ISO2 → Unicode regional-indicator flag emoji
      is a 2-line pure function (offset each letter into the regional
      indicator symbol block) — a new dependency for this would be
      unjustified per the project's dependency rule.
- [+] **HorizontalPager revolver-deck promo section: skipped.** The plan
      explicitly allows this ("если сроки жмут — deck откладывается без
      ущерба, обычные секции достаточны"). Home page uses ordinary
      scroll-reveal sections built from ported primitives instead — no new
      component risk, no wheel/touch/keyboard pager logic to re-verify.
- [+] **Home page stays a client component (`useQuery`, not RSC prefetch).**
      It was already fully client-side pre-Stage-5 (`useEffect`/`useState`);
      swapping to `useQuery(homeOverviewQuery(locale))` satisfies the plan's
      TanStack Query requirement with much less risk than also restructuring
      it into RSC+`HydrationBoundary` in the same change. The plan only
      explicitly asks for RSC prefetch on the **catalog** ("RSC-страница
      префетчит первую страницу списка (SEO)") — that one *is* built as
      RSC-prefetch + `HydrationBoundary` + client pagination/filter component.
- [+] **Catalog pagination is offset-based, not keyset**, matching the actual
      backend contract (`Pagination{limit,offset,total}`) — the plan's
      "keyset с бэкенда" phrasing doesn't match the real endpoint; the
      `Pagination` primitive built in Stage 2 is already page-index-based, a
      natural fit for offset math (`offset = (page-1) * limit`).
  - [+] **⌘K palette**: replaced the static section list with live results
      once a query is typed (debounced 280ms), keeping the static
      sections/actions when the input is empty (so the palette is still
      useful for pure navigation) — additive, not a rewrite of Stage 3's
      shell.
- [+] **`/search` page**: reskinned onto the new design system and migrated
      from raw `useEffect`+`useState` to `useQuery`, keeping every existing
      `data-testid` and the exact filter/URL-sync behavior (types + country
      checkbox/select, `q` param) — `nuqs` replaces the hand-rolled
      `URLSearchParams` push logic.
- [+] **`NuqsAdapter` wiring**: added to `app/providers.tsx` — no prior stage
      did this despite `nuqs` being a dependency since Stage 3.

## Implementation

- [ ] `apps/web/src/app/providers.tsx`: add `NuqsAdapter`.
- [ ] `apps/web/src/shared/lib/flagEmoji.ts`: ISO2 → flag emoji.
- [ ] `apps/web/src/entities/home/api.ts`: `homeOverviewQuery(locale)`.
- [ ] `apps/web/src/entities/search/api.ts`: `searchQuery(params)`.
- [ ] `apps/web/src/entities/watchlist/api.ts`: `myWatchlistQuery()` +
      `useToggleWatchlistMutation()`.
- [ ] Home page reskin: hero, summary counters, `SignalTicker`, country
      overview cards (`ProgressRing`+`MetricCard`), scenario winners, matrix
      preview, legal events + key insights, quick links — all 5 panel
      components + the view itself.
- [ ] Country catalog reskin: RSC prefetch + `CountryCatalogView` client
      component (grid, `WatchlistStar`, `Pagination`, region filter via
      `nuqs`).
- [ ] Search: reskin `/search` page onto `useQuery`+`nuqs`; wire live results
      into `CommandPalette`.
- [ ] Update `tests/e2e/web-mvp-home-overview.spec.ts` /
      `web-mvp-pages.spec.ts` (countries section) / `web-mvp-search.spec.ts`
      selectors only where the new markup genuinely changes them; add new
      cases for pagination/filter/watchlist-star where Stage 5 adds new
      interactive surface.

## Verification

- [ ] `pnpm --filter web typecheck` / `lint`
- [ ] Manual browser check (preview tools) of all three pages, both locales
- [ ] `pnpm web:mvp:check` (Playwright E2E)
- [ ] `python dev_tools_scripts_runner.py --profile full`

## Completion

- [ ] Commit
- [ ] Final report
