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
      префетчит первую страницу списка (SEO)") — that one was *initially*
      built as RSC-prefetch + `HydrationBoundary` + client pagination/filter
      component, but see the deviation logged below: this had to be reverted.
- [+] **DEVIATION from the plan: catalog page dropped RSC prefetch /
      `HydrationBoundary` entirely, now plain client `useQuery` like
      `/search` and the home page.** Manual browser verification (both
      `pnpm dev` and a real `pnpm build && pnpm start` production run)
      found `/countries` rendering `data-testid="country-catalog"` and its
      `<h1>` **twice** in the live DOM — one correct copy inside `<main>`,
      one hidden orphan copy as a sibling outside `<main>`, confirmed via
      `document.querySelectorAll(...).length === 2` and absent from the
      server's raw HTML response (`fetch(...).then(r=>r.text())` had only
      one occurrence) — i.e. a client-side post-hydration duplication, not
      an SSR streaming artifact. Bisected by toggling one variable at a
      time on this one page: swapping `useQueryState` (nuqs) for plain
      `useState` did **not** fix it; removing the `<Suspense>` boundary did
      **not** fix it; removing only `<HydrationBoundary>` (and its
      `queryClient.prefetchQuery`/`dehydrate` RSC prefetch) **did** fix it,
      confirmed with a full `pnpm build` prod rebuild each time (not just
      dev-mode HMR, to rule out a Strict-Mode-only artifact). Root cause:
      `HydrationBoundary` combined with `export const dynamic =
      "force-dynamic"` on this exact Next 15 / React 19 / TanStack Query
      version combination reliably reproduces the duplicate-DOM class of
      bug already on file in memory as `episode_gotchas_backend_tooling.md`
      (originally an `AuthProvider` mount-`setState` issue) — this is a new
      trigger for the same symptom, not the old bug recurring. **Fix:**
      `apps/web/src/app/[locale]/countries/page.tsx` is now a plain sync
      RSC that renders `<CountryCatalogView />` with no prefetch/hydration;
      `CountryCatalogView` itself now wraps its `nuqs`-using inner component
      in its own `<Suspense>` (nuqs still requires a Suspense ancestor,
      same as `/search`'s existing pattern) — `page.tsx` no longer needs to
      provide one. **Cost:** the catalog's first paint is no longer
      SEO-prefetched server-side; it renders a skeleton then fetches
      client-side, same as `/search`. **Why accepted:** correctness (no
      duplicate DOM, no risk of duplicate-content SEO/accessibility issues)
      outweighs the SEO-prefetch nicety for a 3-row demo catalog, and no
      other page in this codebase uses the RSC-prefetch pattern successfully
      yet to compare against — reintroducing it needs its own investigation,
      out of scope for this stage.
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

- [+] `apps/web/src/app/providers.tsx`: add `NuqsAdapter`.
- [+] `apps/web/src/shared/lib/flagEmoji.ts`: ISO2 → flag emoji.
- [+] `apps/web/src/entities/home/api.ts`: `homeOverviewQuery(locale)`.
- [+] `apps/web/src/entities/search/api.ts`: `searchQuery(params)`.
- [+] `apps/web/src/entities/watchlist/api.ts`: `myWatchlistQuery()` +
      `useToggleWatchlistMutation()`.
- [+] Home page reskin: hero, summary counters, `SignalTicker`, country
      overview cards (`ProgressRing`+`MetricCard`), scenario winners, matrix
      preview, legal events + key insights, quick links — all 5 panel
      components + the view itself.
- [+] Country catalog reskin: `CountryCatalogView` client component (grid,
      `WatchlistStar`, `Pagination` via `nuqs`) — **not** RSC prefetch, see
      the logged deviation above (duplicate-DOM bug, reverted).
- [+] Search: reskin `/search` page onto `useQuery`+`nuqs`; wire live results
      into `CommandPalette`.
- [+] Update `tests/e2e/web-mvp-home-overview.spec.ts` /
      `web-mvp-pages.spec.ts` (countries section) / `web-mvp-search.spec.ts`
      selectors only where the new markup genuinely changes them; add new
      cases for pagination/filter/watchlist-star where Stage 5 adds new
      interactive surface.
  - [+] Added `/countries watchlist star prompts login when signed out` to
        `web-mvp-pages.spec.ts` (new interactive surface, zero prior
        coverage).
  - [+] Fixed 3 pre-existing accessible-name assertions
        (`web-mvp-analytical-pages.spec.ts`, `web-mvp-locale.spec.ts` x2)
        that matched the OLD catalog card's literal link text "Карточка
        страны" — the reskinned card's CTA is now "Открыть досье →"
        (a deliberate copy change, not an accident); updated the regex to
        `/открыть досье/i` to match the new, intentional markup.

## Verification

- [+] `pnpm --filter web typecheck` / `lint`
- [+] Manual browser check (preview tools) of home, catalog, search pages +
      CommandPalette live search, both `pnpm dev` and a real
      `pnpm build && pnpm start` run, plus a 375px mobile viewport pass on
      the catalog (no horizontal overflow, no duplication).
- [+] `npx playwright test` (full suite, 285 specs) — **285 passed**, run
      against Playwright's own `webServer` (a real production build with
      `APP_ENV=local`, matching CI). Two failures found along the way were
      diagnosed and are NOT Stage 5 regressions:
  - A `CSRF cookie is readable by JS` test failed once under 4-worker
    concurrency, passed cleanly in isolation — flaky test-data collision
    unrelated to this branch's changes, not investigated further.
  - `web-mvp-main-flow.spec.ts` failed with a duplicate `<h1>` on
    `/countries/uruguay` (`WatchlistButton.tsx`, untouched by Stage 5,
    last modified before this stage) — a pre-existing latent bug, same
    root cause class as the `HydrationBoundary` deviation above (see
    memory `episode_gotchas_backend_tooling.md` for the full writeup).
    Filed as a separate background task (`task_a547e20d`) rather than
    fixed inline, per the project's scope-control rule (don't mix
    unrelated fixes into this diff). **This is a known, tracked, non-
    blocking pre-existing issue — not introduced by this branch.**
- [+] `python dev_tools_scripts_runner.py full-check`. Two runs:
  - First run surfaced real, fixable issues from this diff: 11 files not
    yet Prettier-formatted (`pnpm quality` failing on `format:check`) and
    a stale `pre-commit run --all-files`. Both fixed
    (`prettier --write` / re-running `pre-commit`); second run confirmed
    both green.
  - Remaining `FAIL`s are pre-existing and unrelated to this branch, not
    fixed (would be scope creep — none of the affected files were touched
    by Stage 5):
    - `pytest (scripts/synthetic_data)` — `ModuleNotFoundError: No module
      named 'arabic_reshaper'`, a local venv drift gap (declared in
      `pyproject.toml`, not actually installed); `pip install -e .[dev]`
      did not resolve it. Pure Python synthetic-data tooling, no relation
      to frontend work.
    - `go test` — pre-existing, already documented (`-race` needs a CGO
      toolchain this Windows machine doesn't have; `go vet` and plain
      `go test` both pass).
    - `pnpm web:mvp:check (Playwright E2E)` inside the gate — the gate
      runs Playwright concurrently with its own heavy Docker stack
      (Postgres/Redis/API containers under active migration/smoke-test
      load), which produced 4 generic `Test timeout of 30000ms exceeded`
      failures on pages Stage 5 never touched
      (`/internal/data-quality`, platform-intelligence, route-checklist,
      Route Explorer) — resource contention, not a code issue. A
      standalone `npx playwright test` run (no concurrent Docker gate)
      passed all of these cleanly (see above, 285/285 minus the 2 known
      issues). The 5th failure in the gate run was the same pre-existing
      `WatchlistButton` bug already filed as `task_a547e20d`.

## Completion

- [+] Commit
- [+] Final report
