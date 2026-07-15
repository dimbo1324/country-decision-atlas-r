# Task: Frontend Stage 13 (полировка и выпуск)

Source plan: `docs/_arch_/FRONTEND_IMPLEMENTATION_PLAN.md`, §7 Этап 13.
Branch: `feat/frontend-stage13-polish` (fresh off `main` — Stage 12
merged, `419be35`).

Owner decision: full plan scope, sequenced in parts (same discipline as
Stages 10/12), each its own commit, verified before moving on.

## Preparation

- [+] Research pass done (Explore agent) establishing real scope vs the
      plan text:
      - `apps/web/src/app/styles.css` (2996 lines) still has **one**
        import site (`app/layout.tsx`) but legacy classnames
        (`pageShell`, `pageHeader`, `formGroup`, `notice`,
        `internalLink`, `resultCard`, etc.) are still referenced across
        **24 files** — real, bounded cleanup, not a rounding error.
      - **Vitest is entirely absent** (no config, no dependency anywhere)
        — a from-scratch addition, not a light lift.
      - Storybook 8.4.7 exists in `packages/ui`; **MSW is not installed
        anywhere** — "MSW fixtures for Storybook interaction tests" is
        also greenfield.
      - **No visual regression** exists (`toHaveScreenshot`/
        `toMatchSnapshot` absent from the whole e2e suite).
      - **No bundle analyzer** wired into `next.config.mjs`.
      - **No `ErrorBoundary` component and no `client_error` event
        anywhere**, but `shared/analytics/useAnalyticsEvent.ts` already
        exists — only the boundary + event type are new, not the
        plumbing.
      - Route count is **44** `page.tsx` files (11 `internal/` + 33
        `[locale]/`), not the plan's stale "29+"; e2e suite is **321**
        tests across 44 spec files, not "284" — both DoD figures are
        stale and scale the accessibility/i18n audit surface up
        accordingly.
      - No next-intl lint rule or ru/en key-parity script exists —
        another from-scratch build.
- [+] Owner confirmed: full 7-stream scope, sequenced, not cut down.

## Scope decision for this stage

Given the size, this stage ships in the following order, each a
self-contained commit, verified before moving on (mirrors Stage 10/12
discipline):
1. Legacy CSS removal — reskin the remaining 24 files off `styles.css`
   classnames onto the design system, then delete the file and its
   import.
2. Frontend observability — `ErrorBoundary` component + `client_error`
   analytics event, wired at the app-shell level.
3. Bundle analyzer + performance pass — wire `@next/bundle-analyzer`,
   audit the report, lazy-load heavy chart/feature chunks, confirm
   `next/image` usage for emblem images, review RSC cache policies.
4. Accessibility pass — keyboard-navigation audit, contrast audit of
   `--c3`/`--bg2` and related pairs, ARIA text summaries for charts,
   reduced-motion audit across screens (many charts already respect
   `useReducedMotion`; this is a completeness sweep, not a from-scratch
   build).
5. i18n completeness — ru/en parity script (fails CI-style on orphan
   keys) + a pass fixing any drift found.
6. Vitest setup — config, first real coverage of utilities and data
   hooks (not aiming for exhaustive coverage in one pass; establishing
   the harness + meaningful initial coverage).
7. MSW + Storybook interaction tests — MSW install + a handful of
   interaction stories as the pattern, not full component coverage.
8. Visual regression — Playwright screenshot tests for the plan's
   explicit minimum: home, catalog, dossier, decision result, passport.
9. Final full-suite Playwright run + Stage-0 checklist final pass
   (confirm every route "migrated").

If effort runs out before all nine land, each is independently
committable and this checklist will say honestly which shipped and
which didn't — no stream gets silently dropped without a note, matching
every prior stage's discipline.

## Design decisions

- [+] Legacy-CSS reskin follows the exact `Kicker`/`Card`/`Field`/
      `Button` conventions used throughout Stages 9-12; no new
      primitives invented for this cleanup.
- [+] `ErrorBoundary` wraps at the `AppShell`/`InternalShell` level
      (inside each shell's `<main>`, around `children`) rather than
      directly in the two `layout.tsx` files — same effective coverage
      of every route in both trees, but keeps the boundary co-located
      with the shells it belongs to. Reports via the existing
      low-level `trackEvent` client (not the `useAnalyticsEvent` hook —
      hooks are unavailable in a class component, and error boundaries
      must be class components) with `event_type: "client_error"`,
      degrades to a plain retry UI. Verified end-to-end in a real
      browser (dev server, temporary crash-trigger, reverted after):
      the boundary catches the thrown error, renders the retry UI, and
      the real `trackEvent` call resolves with a schema-valid payload
      (`event_type`/`source`/`path`/`metadata` all present and passing
      backend Pydantic validation `^[a-z][a-z0-9_]{1,63}$`).
- [+] Bundle-analyzer output only run locally (`ANALYZE=true next build`)
      — not wired into CI, since the plan doesn't ask for a CI budget
      gate, only a manual audit this stage. Audit surfaced two real,
      fixed wins (see Implementation, Stream 3) and confirmed the
      shared baseline (102 KB, React + Next.js runtime only) is
      already lean — Next's automatic per-route chunking already
      isolates most feature-specific weight without manual
      intervention; the two real problems found were both *barrel
      re-export leaks* (a page importing one named export from a
      feature's `index.ts` pulled in a sibling export's heavy,
      unrelated dependency because barrels without
      `"sideEffects": false` don't guarantee per-export tree-shaking),
      not missing lazy-loading per se.
- [ ] i18n parity script lives in `scripts/dev_tools/` (matching the
      project's existing dev-tooling location) and is registered as a
      `--profile quick`-eligible check if lightweight enough; otherwise
      documented as a manual command.
- [ ] Vitest scope: `shared/lib/*` utilities and `entities/*/api.ts`
      hooks with clear pure-function surface first — not an attempt at
      full coverage of every component in one stage.

## Implementation

### Stream 1: Legacy CSS removal (done)

- Delegated the mechanical reskin of the 24 files identified in
  research to the `country-atlas-frontend-web` subagent, with a full
  classname→DS-primitive mapping derived from each rule's actual CSS
  (not guessed). The agent additionally found and fixed real legacy
  classnames outside the given mapping table
  (`cardSection`/`cardSectionTitle`/`cardSectionHighlight`,
  `routeDetail`/`routeDetailGrid`/`routeBadges`/`routeFacts`/
  `routeWarnings`, `routeChecklist*`, `dataGrid`/`dataCard`) in
  `RouteDetailView.tsx`, `RouteChecklistList.tsx`,
  `DecisionRiskContext.tsx`, and `scenarios/page.tsx` — these weren't
  in the brief but were genuine `styles.css` dependents that would
  have silently broken once the file was deleted.
- Deleted two now-dead components discovered along the way:
  `shared/ui/SectionHeader.tsx` and `shared/ui/SummaryCard.tsx` — both
  had zero remaining consumers after the `DataQualityReportView`
  reskin in Stage 12.
- Independently re-verified the agent's work rather than trusting its
  self-report: cross-checked **every one of the 429 selectors defined
  in `styles.css`** against remaining `className="..."` usage
  app-wide (not just the 24-file list), which caught 3 more real
  dependents the agent's narrower final-check missed:
  `RouteDocumentsList.tsx`, `RouteEvidenceList.tsx`,
  `RouteSourcesList.tsx` (all using `routeDocuments`/`routeEvidence`/
  `routeSources` container classes) — fixed directly.
- Deleted `apps/web/src/app/styles.css` (2996 lines) and its import in
  `apps/web/src/app/layout.tsx`.
- **Regression found and fixed during verification, not by the
  agent**: the agent's `RouteDetailView.tsx` reskin introduced the
  `Breadcrumbs` design-system primitive into
  `app/[locale]/routes/[id]/page.tsx` (an async Server Component)
  with an inline `renderLink` function prop — `Breadcrumbs` is a
  `"use client"` component, and passing a plain function across the
  Server→Client boundary is illegal in RSC (`next build` succeeds,
  but every real request 500s: "Functions cannot be passed directly
  to Client Components"). This was caught by running the full
  Playwright suite, not by typecheck/lint/build, all three of which
  stayed green throughout. Fixed by adding
  `shared/ui/AppBreadcrumbs.tsx`, a thin `"use client"` wrapper that
  owns the `renderLink` closure itself so Server Component callers
  only ever pass plain serializable `items`.
- **Two more issues found via the full-suite run, both pre-existing
  test fragility unrelated to the CSS work**: `web-mvp-analytical-pages.spec.ts`,
  `web-mvp-legal-signals-timeline.spec.ts`, and `web-mvp-main-flow.spec.ts`
  used bare `page.locator('[data-testid="..."]')`/`page.locator("#id")`
  selectors that intermittently match a second, permanently-invisible
  DOM node Next.js leaves behind under a transient `id="S:0"` Suspense
  streaming marker — a real (if obscure) Next.js behavior, not an
  application bug; the pages render correctly (confirmed via
  screenshot and direct DOM inspection: the second match has
  `offsetParent === null`). Confirmed this is not a Stage 13
  regression by checking `git diff main` for every implicated
  component (`LegalSignalsTimelineView.tsx`, `TimelineFilters.tsx`,
  `LegalSignalsChartView.tsx`, `[slug]/page.tsx` country dossier) —
  zero changes vs `main` in any of them. Hardened the affected
  locators to `page.getByRole("main").locator(...)`/`.getByTestId(...)`
  in all three spec files rather than touch application code for a
  test-only fragility issue.
- Verified independently end-to-end: `typecheck` clean, `lint` clean,
  `build` clean (all 44 routes compile), full Playwright suite
  **328/328 passed** at `--workers=2` against the live Docker stack.

### Stream 2: Frontend observability (done)

- `shared/ui/ErrorBoundary.tsx` (new) — class component
  (`getDerivedStateFromError`/`componentDidCatch`, the only React API
  shape error boundaries support), reports a `client_error` analytics
  event via the existing low-level `trackEvent` client (message,
  truncated stack, truncated component stack, current path), renders
  a `Card`/`Kicker`/`Button` retry UI instead of a blank crash.
- Wired into `AppShell.tsx` and `InternalShell.tsx`, wrapping
  `children` inside each shell's `<main>` — covers every route in
  both the `[locale]` and `internal` trees without duplicating the
  boundary per-page.
- Verified live in a browser: temporarily made a page throw on a
  query-param trigger, confirmed the boundary renders the retry UI
  and the real (non-mocked) `trackEvent` call resolves against the
  live backend with a schema-valid `client_error` payload — then
  reverted the temporary trigger (`git diff` on the touched file
  confirmed clean afterward).
- `typecheck`/`lint`/`build` clean; full Playwright suite unaffected
  (**328/328** re-run passed with the boundary wrapping every page).

### Stream 3: Bundle analyzer + performance audit (done)

- Added `@next/bundle-analyzer` as a devDependency, wired into
  `next.config.mjs` behind `ANALYZE=true` (`createBundleAnalyzer({
  enabled: process.env.ANALYZE === "true" })`, composed with the
  existing `withNextIntl` wrapper) — a manual local audit tool, not a
  CI gate.
- Ran `ANALYZE=true pnpm --filter web build` and parsed the generated
  `apps/web/.next/analyze/client.html` treemap JSON directly (no
  visual eyeballing) to rank chunks by parsed size and drill into
  which packages/modules make up each one.
- **Finding 1 (fixed)**: `/trips` (list page) shipped 306 KB First
  Load JS — the highest of any route — despite the list view itself
  having no chart/DnD dependency. Root cause: `apps/web/src/app/[locale]/trips/page.tsx`
  imported `TripListView` through the barrel
  `features/trips/index.ts`, which also re-exports `TripDetailView`;
  `TripDetailView` pulls in `TripWaypoints` (`@dnd-kit/core` +
  `@dnd-kit/sortable`, ~41 KB parsed) and `TripReminders` (`date-fns`,
  ~14 KB parsed) directly (not lazily), and the barrel's lack of
  `"sideEffects": false` meant webpack couldn't prove those modules
  were unreachable from the list page's actual import, so it kept
  them in a shared chunk pulled by both routes.
  Fixed in two parts:
  1. `TripDetailView.tsx` now lazy-loads `TripWaypoints` and
     `TripReminders` via `next/dynamic()` with a `LoadingState`
     fallback — they were never needed on first paint of the detail
     page either (both are below-the-fold, interaction-only), so this
     is a genuine lazy-chunk split, not just a barrel workaround.
  2. Both `trips/page.tsx` and `trips/[id]/page.tsx` now import
     directly from `./TripListView`/`./TripDetailView` instead of the
     barrel, removing the ambiguity for webpack entirely.
  **Measured result**: `/trips` 306 → 279 KB (**-27 KB**), `/trips/[id]`
  213 → 170 KB (**-43 KB**).
- **Finding 2 (fixed)**: `/authors/[userId]` (public author profile,
  no admin UI) shipped 281 KB First Load JS. Root cause: same barrel
  pattern — `features/author-metrics/index.ts` re-exports
  `AuthorProfileView` (what the public page actually needs) alongside
  `AuthorMetricsModerationView`, which pulls in `@tanstack/react-table`
  (~48 KB parsed, needed only by the `/internal/author-metrics-moderation`
  `ModerationQueue` instance). Fixed by importing directly from each
  view's own file in all three consumer pages
  (`account/author-metrics/page.tsx`, `authors/[userId]/page.tsx`,
  `internal/author-metrics-moderation/page.tsx`) instead of the
  barrel.
  **Measured result**: `/authors/[userId]` 281 → 233 KB (**-48 KB**).
- **Confirmed already healthy, no action needed**: the "First Load JS
  shared by all" baseline is 102 KB total, made up of exactly
  React/Next.js runtime chunks (`framework`, `react-dom-client`,
  `react-server-dom-webpack` client, `main`) plus ~2 KB of genuinely
  shared app code — no app-specific library (charts, tables, DnD) leaks
  into the global baseline. Next's automatic per-route code splitting
  is already doing its job; the two fixes above were barrel-import
  leaks between *sibling* routes, not a missing-lazy-loading problem
  at the framework level.
- **Not exhaustively audited — left for a follow-up pass**: a
  `grep`-level survey found 8 more feature barrels with 2+ named
  exports used by routes of meaningfully different weight/role
  (`ai-assistant`, `auth`, `community`, `country-proposals`,
  `migration-board`, `search`, `watchlist`, `data-quality`) that
  *could* have the same class of leak, but none showed up as
  disproportionately large in the current First Load JS numbers the
  way `/trips` and `/authors/[userId]` did, so they weren't chased
  further this pass — flagged here rather than silently assumed clean.
- `pnpm typecheck`/`lint`/`build` clean; full Playwright suite
  **328/328 passed** at `--workers=2` after both fixes.

## Verification

- [+] `pnpm --filter web typecheck` / `lint` — clean.
- [+] `pnpm --filter web build` — clean, all 44 routes compile.
- [+] Full Playwright regression at `--workers=2` — **328/328 passed**,
      including the 3 spec files hardened against the pre-existing
      Suspense-marker locator fragility.
- [+] `python dev_tools_scripts_runner.py --profile quick` — clean
      except the pre-existing `arabic_reshaper` venv gap (same known
      baseline issue since Stage 9-12, not a regression).
- [ ] Manual accessibility/contrast/reduced-motion checks — deferred to
      Stream 4 (accessibility pass), not part of CSS removal.

## Completion

- [ ] Commit(s) — stream 1 (legacy CSS removal) landing now; streams
      2-9 remain.
- [ ] Merge to `main`, push — only once explicitly confirmed complete.
- [ ] Final report — honest per-stream status against the DoD.
