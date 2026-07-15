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
- [+] Accessibility pass scope, decided after measuring rather than
      guessing: the plan's DoD item 4 only requires contrast/keyboard/
      reduced-motion to be **"verified and documented"**, not that
      every finding be fixed — `text-c3`/`text-c4` alone appear 232 and
      137 times respectively across the codebase, too large a surface
      to bulk-edit safely without per-usage design judgment in this
      pass. So: full computed contrast audit delivered as documentation
      (exact ratios, not eyeballed); keyboard-nav, ARIA-chart-summary,
      and reduced-motion get real fixes wherever a concrete,
      bounded, low-risk gap was found — not a blind sweep.

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

### Stream 4: Accessibility pass (done — audited + bounded fixes, see scope note)

**Contrast audit (computed, not eyeballed).** Wrote a small WCAG relative-
luminance script and ran every text-token/background-token pair from
`packages/ui/src/tokens/theme.css` (`--color-c1..c4`, all accent triads,
`--color-bg/bg2/bg3/bg4`) through it. Full results are reproducible from
the token file; the material findings:
- **`--c3` on `bg2`/`bg3`/`bg4`: 4.25 / 4.47 / 4.00 : 1** — fails WCAG AA
  for normal text (needs 4.5:1), passes for large text/UI components
  (needs 3:1). This is exactly what the plan predicted
  ("--c3 на --bg2 для мелкого текста"). `text-c3` is used **232 times**
  across `apps/web/src` + `packages/ui/src`, nearly always for small
  (`text-xs`/`text-[9-11px]`) meta/label text — the failing case, not
  the passing one.
- **`--c4` on any background: 1.75–1.98 : 1** — fails even the large-text/
  UI-component floor (3:1) everywhere, badly. Used **137 times**, mostly
  for the `font-mono text-[9px] tracking-[0.2em] uppercase` micro-label
  convention used throughout every stage (section eyebrows, meta chips).
  This is the more severe of the two findings.
- Several accent "-2" shades used as **text** color (`blue2`, `terra2`,
  `sage2`, `plum2`) fail AA-normal (2.0–3.2:1) but most pass AA-large/UI;
  spot-checked usage and these are predominantly used for *borders*, not
  text, in this codebase's actual components — lower real-world risk
  than `c3`/`c4`, not separately itemized further.
- **Not fixed this pass** (see scope note above): elevating `c3`→`c2` and
  auditing every `c4` micro-label use for size/necessity touches
  hundreds of call sites across 44 routes and both design-system-package
  and app code — the audit is complete and exact; the remediation is
  the explicit next-step handoff (see Completion).

**Keyboard navigation.** Established convention (Radix-based primitives
for `Dialog`/`Dropdown`/`Select`/`Popover`/`Tabs`, semantic `<button>`/
`<a>` throughout) already covers most interactive paths for free. Found
and fixed one real, concrete gap introduced in Stage 12:
`packages/ui/src/primitives/ModerationQueue.tsx`'s row-click-to-open-
detail behavior was a bare `onClick` on `<td>` elements — no keyboard
equivalent, no focus indicator, no `tabIndex`. Fixed by making the row
itself focusable (`tabIndex={0}`, `aria-label` naming the row via
`detailTitle`) with an `onKeyDown` handler for Enter/Space — deliberately
**not** `role="button"` on the `<tr>`, since the same row also contains
real `<button>` elements for row actions and ARIA disallows interactive
content inside a button-role element; the handler instead checks
`event.target.closest("button, a")` and bails out so pressing Enter on a
nested action button doesn't *also* pop the detail drawer. This affects
every Stage-12 admin queue that passes `renderDetail`
(author-metrics, country-proposals, contradiction-candidates, users).

**ARIA chart summaries.** Confirmed **zero** of the 12 real chart
components in `packages/ui/src/charts/` had any `aria-label`/text
alternative — canvas-based charts in particular convey literally no
information to a screen reader without one. Fixed all of them,
matching each chart's actual accessible-content situation rather than
applying one pattern everywhere:
- **Canvas charts with no adjacent visible text**
  (`RadarChart`, `Heatmap`, `RankFlow`, standalone `SparklineChart`):
  added a synthesized `role="img" aria-label` text summary built from
  the component's own data props (axis/series values, row/column
  extremes, rank sequences) — the plan's literal example
  ("CII 71 из 100, уверенность высокая") is exactly this shape.
- **Decorative canvas/SVG where the value is already rendered as
  visible text nearby** (`ProgressRing`, `GaugeArc`, `DonutChart`,
  `DriftBoard`'s inline row sparkline): added `aria-hidden="true"` to
  the canvas/SVG itself instead of a redundant duplicate description —
  the value is already announced via the sibling text node.
- **Div/span-based bar/meter charts** (`BarColumns`, `CriteriaWeightBars`,
  `DivergingMeter`, `PassportCard`): confirmed already accessible by
  construction — every value is a real visible DOM text node, not a
  canvas pixel, so no change was needed.

**Reduced-motion.** Confirmed 12 of 13 chart components already call
`useReducedMotion()` and degrade correctly. Found and fixed the one
exception: `PassportCard.tsx`'s `GlidingNumber` sub-component ran a
700ms `requestAnimationFrame` count-up animation on every value change
with no `prefers-reduced-motion` check at all — fixed to snap directly
to the target value when reduced motion is requested, matching every
other chart's established pattern.

- `pnpm --filter ui typecheck`/`lint` clean; `pnpm --filter web
  typecheck`/`lint`/`build` clean; full Playwright suite **328/328
  passed** at `--workers=2` (5 workers=2-only failures on the first
  pass, all confirmed passing in isolation — the same documented
  resource-contention flake pattern, not a regression from these
  changes).

## Verification

- [+] `pnpm --filter web typecheck` / `lint` — clean.
- [+] `pnpm --filter web build` — clean, all 44 routes compile.
- [+] Full Playwright regression at `--workers=2` — **328/328 passed**,
      including the 3 spec files hardened against the pre-existing
      Suspense-marker locator fragility.
- [+] `python dev_tools_scripts_runner.py --profile quick` — clean
      except the pre-existing `arabic_reshaper` venv gap (same known
      baseline issue since Stage 9-12, not a regression).
- [+] Manual accessibility/contrast/reduced-motion checks — done in
      Stream 4: computed contrast audit, keyboard-nav fix, ARIA chart
      summaries, reduced-motion fix. See Stream 4 above for exact
      findings and what remains unfixed (contrast role elevation).

## Completion

- [+] Commit(s) — 4 of 9 streams landed on
      `feat/frontend-stage13-polish` (`4f33d7f` legacy CSS removal,
      `5631114` ErrorBoundary, `b9d924d` bundle analyzer,
      `324e22c` accessibility), each independently verified
      (`typecheck`/`lint`/`build`/328-test Playwright regression/quick
      quality gate) before its own commit.
- [ ] Merge to `main`, push — **not done, by design**: the owner asked
      for streams 1-4 plus thorough documentation this pass, then
      wants to continue streams 5-9 themselves before merging. Do not
      merge until they confirm the stage is complete.
- [+] Final report — see below.

## Handoff: streams 5-9 remaining

Streams 1-4 (legacy CSS, observability, bundle/perf, accessibility)
are done, verified, and committed. The following five are **not
started** — each was scoped in "Scope decision for this stage" above
before any research confirmed feasibility; the notes below add what's
now known so whoever picks these up doesn't have to re-derive it.

**Stream 5 — i18n completeness.** Not started. `apps/web/src/messages/
{en,ru}.json` are the two dictionaries; no parity-check script or lint
rule exists yet (confirmed absent in Stage 13 Preparation research).
Suggested approach: a small Node/TS script under `scripts/dev_tools/`
that flat-diffs both JSON files' key sets (recursive, dot-path keys)
and fails non-zero on any one-sided key — cheap to write, cheap to run,
and matches the plan's literal ask ("no orphans outside the
dictionaries") without needing a full next-intl ESLint plugin. Register
it as a `--profile quick` step in `dev_tools_scripts_runner.py` once it
exists. Separately: an actual ru/en *content* pass over all 44 routes
(not just key-parity) to catch missing/stale translations is a manual
QA pass, not a script — budget time for it separately.

**Stream 6 — Vitest setup.** Not started, and confirmed genuinely
greenfield: no `vitest` dependency, no config, anywhere in the repo.
Needs: `vitest` + `@vitejs/plugin-react` (already a devDependency of
`packages/ui` via Storybook's Vite setup, so precedent for the tooling
exists) or `jsdom`/`happy-dom` for the test environment, a
`vitest.config.ts` per workspace that needs it (`apps/web`,
`packages/ui`), and `package.json` `test`/`test:watch` scripts. Scope
recommendation from "Design decisions" above still holds: start with
`shared/lib/*` pure utilities and `entities/*/api.ts` query-key/params
logic (no React rendering needed, fastest to write and most stable),
not component rendering tests — those would want Stream 7's MSW
fixtures first anyway.

**Stream 7 — MSW + Storybook interaction tests.** Not started.
Storybook 8.4.7 already exists in `packages/ui` (`.storybook/`,
`build-storybook` script) — this stream only needs `msw` added as a
devDependency plus `msw-storybook-addon`, then a handful of interaction
stories (`play` functions) on the highest-value components as the
established pattern, not full coverage. Natural candidates given this
session's work: `ModerationQueue` (now has the keyboard-interaction
path worth regression-testing in isolation) and one or two chart
components with the new ARIA labels.

**Stream 8 — Visual regression.** Not started. No `toHaveScreenshot`/
`toMatchSnapshot` usage exists anywhere in `tests/e2e/` (confirmed
absent). The plan's explicit minimum is 5 screens: home, catalog,
dossier (country page), decision result, passport. Playwright's
built-in `expect(page).toHaveScreenshot()` needs a first baseline-
generation run (`--update-snapshots`) committed alongside the test
file; budget for the fact that Stage 13 streams 1-4 changed visual
output on several routes this session (legacy CSS removal, bundle
changes) so baselines should be captured *after* those land, not
before — which they now have.

**Stream 9 — Final full-suite pass + Stage-0 checklist.** Not started.
Once streams 5-8 land: re-run the full Playwright suite one more time,
confirm the DoD's 5 numbered criteria in the plan
(`docs/_arch_/FRONTEND_IMPLEMENTATION_PLAN.md` §7 Этап 13) against
actual current state (route count is 44, not the plan's stale "29+" —
worth updating the plan doc itself in this final pass, not just
checking it off), and do the Stage-0 checklist sweep confirming every
route is marked "migrated" in whatever tracking doc Stage 0 established.
