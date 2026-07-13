# Task: Frontend Stage 6 + 7 (country dossier, decision mechanics) + WatchlistButton bug fix

Source plan: `docs/_arch_/FRONTEND_IMPLEMENTATION_PLAN.md`, §7 Этап 6 и Этап 7.
Branch: `feat/frontend-stage6-7-dossier-decisions` (fresh off `main` — Stage 5
merged and deleted).

Owner decision: bundle both stages in one branch, plus fold in a small
pre-existing bug fix (`WatchlistButton.tsx` duplicate-DOM setState bug,
found during Stage 5 verification, originally filed as a separate
background task) rather than a separate branch.

## Preparation

- [+] Confirmed Stage 5 merged into `main` (`cc885fb`), branch is fresh off it.
- [+] Re-read `FRONTEND_IMPLEMENTATION_PLAN.md` in full for Р-1..Р-10 and the
      exact Этап 6 / Этап 7 task lists, component-source tables, and
      readiness criteria.
- [+] Surveyed via 2 parallel research agents:
  - Country dossier (`countries/[slug]/page.tsx` + `features/country-card`,
      `country-drift`, `trust-surface`, `data-journal`, `routes`,
      `platform-intelligence`, `what-changed`, `community`): full file
      inventory, data-testids, fetch patterns (100% raw `useEffect`+fetch,
      zero TanStack Query), contract shapes, old CSS classes to retire.
  - Decision mechanics (`features/decision-wizard`, `decision-run`,
      `decision-personalization`, `decision-passports`,
      `decision-visual-comparison`, `compare-matrix` + their route pages):
      same inventory. Confirmed `packages/ui/src/charts/PassportCard.tsx`
      already exists (ported in Stage 4) — reuse it, don't re-port from the
      prototype. `AnalysisOverlay` does NOT exist yet in `packages/ui` —
      needs porting fresh.
- [+] Fixed the WatchlistButton bug (see "Bug fix" section below) as the
      first commit-sized unit of work, verified independently before
      starting the two stages.

## Bug fix: WatchlistButton duplicate-DOM setState (folded in per owner decision)

- [+] `apps/web/src/features/watchlist/WatchlistButton.tsx`: initializer now
      reads `hasSessionHint()` — anonymous visitors start directly at
      `"login-required"` instead of `"loading"` → mount-effect transition.
      Mount effect itself also early-returns when there's no session hint,
      since even a same-value `setState` call is enough to trigger this bug
      class (confirmed empirically in Stage 5's investigation — swapping
      state values wasn't the trigger, the setState call itself was).
- [+] Verified: `npx playwright test tests/e2e/web-mvp-main-flow.spec.ts
      tests/e2e/web-mvp-watchlist.spec.ts` — 6/6 passed against a real
      `pnpm build && pnpm start` production server (this bug never
      reproduced in dev mode, so dev-mode passing would prove nothing).

## Design decisions (recorded before writing code)

- [ ] Every feature file touched in these two stages currently does raw
      `useEffect`+`useState` fetching via hand-written `shared/api/*`
      modules. Per Р-4, migrate to TanStack Query `queryOptions` factories
      (one module per domain under `entities/*/api.ts`, matching the
      Stage 3/5 pattern) rather than leaving the old pattern in place —
      the plan's own "Паттерн для разработчика (данные)" section requires
      this, and mixing old/new fetch patterns on the same rescinned page
      would be inconsistent.
- [ ] `country-card/*` components are pure presentational (props from one
      server-fetched `CountryReadModelResponse`) — stay server-rendered via
      RSC prefetch of `/countries/{slug}/card`, per the plan's "RSC-префетч
      карточки + ленивые клиентские подзапросы тяжёлых секций" pattern.
      Given the Stage 5 HydrationBoundary/force-dynamic duplicate-DOM bug,
      this RSC-prefetch layer will be tested specifically against that
      regression before being trusted (build + Playwright strict-mode h1
      check), not assumed safe by analogy.
- [ ] Heavy sections (`trust-surface`, `country-drift`, `platform-intelligence`,
      `data-journal`, `what-changed`, `community`, `routes`) become
      independent client components with their own `useQuery`, each
      `enabled: isNearViewport` via `IntersectionObserver`, per the plan's
      "Паттерн (ленивая загрузка секций)". A shared `useNearViewport(ref)`
      hook is added once in `apps/web/src/shared/lib/` rather than
      duplicated per section.
- [ ] Rail navigation for the dossier (`#rail` per the plan) is a new
      `DossierRail` component built from `packages/ui` primitives
      (sticky aside, active-section highlight via `IntersectionObserver`),
      not ported from anywhere (prototype has no exact equivalent).
- [ ] `CountryCiiBlock` gets the `RadarChart` (spider) + `CriteriaWeightBars`
      (component breakdown) from `packages/ui`, replacing the existing
      hand-rolled inline SVG in `country-card` (none currently — it's
      plain metric rows) — matches plan's explicit CII-section spec.
  - [ ] `TrustSurfaceBlock` gets `ProgressRing` (confidence) + `DonutChart`
        (source structure) + existing `FreshnessBadge`/`TrustBadge` rescinned
        onto `Badge`.
  - [ ] `CountryDriftBlock`/`CountryWhatChanged` get `DriftBoard` +
        `Drawer` for the change-detail dossier, per plan.
  - [ ] `PlatformIntelligenceBlock` gets `DataTable` + `SparklineChart` per
        row, per plan.
  - [ ] `CountryScores` gets `MetricCard` grid + `GaugeArc`, with
        score-label colour semantics (weak…excellent) already established
        by `compare-matrix`'s `MatrixCell` colour bands — reuse that exact
        band logic rather than inventing a second one.
- [ ] Decision-visual-comparison's hand-rolled inline SVG spider
      (`CiiCompareSpiderChart.tsx`) and hand-rolled bars
      (`CiiMetricCompareBars.tsx`) are replaced by `packages/ui`'s
      `RadarChart`/`CriteriaWeightBars` — same components as the dossier's
      CII section, for one visual source of truth between "view a
      country's CII" and "compare two countries' CII".
- [ ] `compare-matrix`'s `MatrixCell` colour-band logic (weak/limited/
      moderate/strong/excellent → 5 colours) becomes a small shared
      `scoreLabelAccent(label)` helper in `packages/ui` (or
      `apps/web/src/shared/lib/`) so the dossier's `CountryScores` and the
      matrix use the identical mapping instead of two hand-maintained
      copies.
- [ ] `AnalysisOverlay` ported fresh into `packages/ui/src/shell/` (not
      `charts/`, matching where `BackgroundTexture`/`BackgroundFX` live),
      reusing the existing `ProgressRing` chart instead of re-implementing
      the SVG ring by hand (prototype hand-rolls it; we don't need to).
- [ ] `PassportCard` reused as-is from `packages/ui/src/charts/PassportCard.tsx`
      (already ported in Stage 4) for the Decision Passport screens —
      no re-port from the prototype.
- [ ] Decision wizard/run/weights/passports stay client components (already
      are); migrated to `useQuery`/`useMutation` in place of raw fetch, URL
      state (`nuqs`) added for wizard step + weight sliders per plan's
      explicit "shareable по ссылке" requirement — this is new work, the
      current wizard has no URL persistence at all.
- [ ] `DecisionPassportPage` (`/decision/passports/[token]`) stays a plain
      RSC `await` (no HydrationBoundary) — it's a one-shot read-only public
      page, no client interactivity needed beyond what `PassportCard`
      itself provides, so there's no reason to introduce the
      HydrationBoundary pattern (and its known duplicate-DOM risk) here.
- [ ] Slider for decision weights: Radix `Slider` (already in `packages/ui`
      from Stage 2) styled per plan's "гравированная шкала", replacing the
      current plain `<input type="range">`.
- [ ] Debounced live recompute on weight change (400–500ms, per plan)
      implemented as a `useDebouncedCallback`-style local hook (no new
      dependency — a 10-line `useEffect`+`setTimeout` utility, matching how
      Stage 5 did the CommandPalette's search debounce).

## Implementation — Stage 6 (country dossier)

- [ ] `entities/country-card/api.ts` (or reuse `entities/country/api.ts`):
      `countryCardQuery(slug, locale)` for RSC prefetch.
- [ ] New `entities/*/api.ts` modules for the 6 heavy sections: drift,
      trust, platform-intelligence, data-journal, what-changed, routes,
      community — each a `queryOptions` factory.
- [ ] `shared/lib/useNearViewport.ts`: `IntersectionObserver`-based hook.
- [ ] `packages/ui`: `DossierRail` (sticky section nav), `scoreLabelAccent`
      helper.
- [ ] Reskin `countries/[slug]/page.tsx`: RSC prefetch of the card, rail
      nav, section wrappers using `ChartFrame`.
- [ ] Reskin all `country-card/*` components onto Card/Badge/MetricCard/
      RadarChart/CriteriaWeightBars/GaugeArc.
- [ ] Reskin `country-drift`, `trust-surface`, `data-journal`,
      `platform-intelligence`, `what-changed`, `routes`, `community` onto
      TanStack Query + `packages/ui` (DriftBoard, ProgressRing, DonutChart,
      DataTable, SparklineChart, TimelineList, Drawer).
- [ ] Preserve every existing `data-testid` (per the migration rule: no
      functionality lost) — cross-check against the survey's testid list
      before considering each file done.

## Implementation — Stage 7 (decision mechanics)

- [ ] `entities/decision/api.ts`: `runDecisionMutation`, `compareCiiQuery`,
      `matrixQuery`, `scenariosQuery`, `personasQuery`,
      `weightProfilesQuery` + mutations.
- [ ] `entities/decision-passports/api.ts`: create-passport mutation,
      public-passport query (for the token page's RSC `await`, reused as a
      plain async function, not necessarily `queryOptions`).
- [ ] `packages/ui/src/shell/AnalysisOverlay.tsx` + story.
- [ ] Reskin `decision-wizard/*`: RadioCards steps, nuqs step state,
      `useMutation` for resolve.
- [ ] Reskin `decision-personalization/*`: Radix `Slider`s, debounced live
      recompute, nuqs weight state.
- [ ] Reskin `decision-run/*`: `DecisionRunForm` main page, `DecisionResults`,
      `DecisionResultCard`, `DecisionBreakdown` (→ `CriteriaWeightBars`),
      `DecisionCountryTrustBadge`, `DecisionSources`, `DecisionWarnings` —
      `AnalysisOverlay` shown during the run mutation.
- [ ] Reskin `decision-visual-comparison/*` onto `RadarChart` +
      `CriteriaWeightBars` (replacing hand-rolled SVG/bars).
- [ ] Reskin `compare-matrix/*`: `CountryScenarioMatrix` table restyle,
      `MatrixCell` using the shared `scoreLabelAccent`, `RankFlow` as an
      alternate view per plan ("RankFlow как альтернативный вид").
- [ ] Reskin `decision-passports/*` (`DecisionPassportActions`) +
      `decision/passports/[token]/page.tsx` onto `PassportCard`.
- [ ] Preserve every existing data-testid (same rule as Stage 6).

## Verification

- [ ] `pnpm --filter web typecheck` / `lint`
- [ ] Manual browser check (preview tools): dossier page (all sections),
      decision wizard → run → result → compare → matrix → passport →
      public passport link, both locales, mobile viewport.
- [ ] Explicit duplicate-DOM regression check on every newly-added
      RSC-prefetch or force-dynamic + client-mount-effect combination
      (`document.querySelectorAll(testid).length === 1` in a real
      `pnpm build && pnpm start`), given this bug class has now recurred
      twice in this codebase.
- [ ] `npx playwright test` (full suite) — update/extend specs for markup
      that genuinely changed; must stay at parity or better than the
      285-spec baseline from Stage 5.
- [ ] `python dev_tools_scripts_runner.py full-check`

## Completion

- [ ] Commit(s)
- [ ] Final report
