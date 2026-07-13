# Task: Frontend Stage 7 (decision mechanics)

Source plan: `docs/_arch_/FRONTEND_IMPLEMENTATION_PLAN.md`, §7 Этап 7.
Branch: `feat/frontend-stage7-decision-mechanics` (fresh off `main` — Stage 6
merged, `58b9b62`).

Owner instruction: implement in a separate branch, push to `origin/main`
once done and tests pass.

## Preparation (carried over from Stage 6+7 planning, still valid)

- [+] Full file inventory already done via research agent during Stage 6
      planning: `features/decision-wizard`, `decision-run`,
      `decision-personalization`, `decision-passports`,
      `decision-visual-comparison`, `compare-matrix` + their route pages.
      100% raw `useEffect`+fetch, zero TanStack Query, confirmed.
- [+] `packages/ui/src/charts/PassportCard.tsx` already exists (ported
      Stage 4) — reuse as-is.
- [+] `packages/ui/src/shell/AnalysisOverlay.tsx` already built (Stage 6,
      reuses `ProgressRing`) — reuse as-is, no new work needed here.
- [+] `packages/ui/src/lib/scoreLabel.ts` (`scoreLabelStyle`) already built
      (Stage 6, for the dossier's `CountryScores`) — reuse for
      `compare-matrix`'s `MatrixCell` instead of the plan's separate
      `scoreLabelAccent` idea, one mapping for both surfaces.
- [+] Contract shapes confirmed: `DecisionRunResponse`,
      `DecisionPersonalizationResponse`, `CompareMatrixResponse`,
      `CiiCountryComparisonResponse`, `Scenario`, `Persona`,
      `PersonaWeightProfile`, `DecisionPassportCreateResponse`,
      `DecisionPassportResponse` (doubles as the public token-read shape).

## Design decisions

- [ ] All 6 feature domains migrate their raw `useEffect`+fetch to
      TanStack Query `useQuery`/`useMutation`, matching Stage 5/6's
      established pattern — one `entities/*/api.ts` module per domain.
- [ ] `AnalysisOverlay` (already built) shown during the `decision/run`
      mutation and the CII comparison fetch — the plan's explicit
      "фирменный момент продукта".
- [ ] Decision wizard step + weight-slider state goes into the URL via
      `nuqs`, per the plan's explicit "shareable по ссылке" requirement —
      genuinely new behavior, not present in the current wizard at all.
- [ ] Radix `Slider` (already in `packages/ui` since Stage 2) replaces the
      plain `<input type="range">` weight sliders.
- [ ] Debounced live recompute on weight change: a small local
      `useDebouncedValue`-style hook (matches how Stage 5 debounced the
      CommandPalette search), not a new dependency.
- [ ] `decision-visual-comparison`'s hand-rolled inline SVG spider
      (`CiiCompareSpiderChart.tsx`) and hand-rolled bars
      (`CiiMetricCompareBars.tsx`) replaced by `packages/ui`'s `RadarChart`/
      `CriteriaWeightBars` — same components as the dossier's CII section.
- [ ] `compare-matrix`'s `MatrixCell` 5-band colour logic replaced by the
      shared `scoreLabelStyle` helper (built in Stage 6) instead of a
      second hand-maintained mapping.
- [ ] `PassportCard` reused as-is from `packages/ui/src/charts/PassportCard.tsx`
      for both the create-passport action's preview and the public
      `/decision/passports/[token]` page.
- [ ] `/decision/passports/[token]/page.tsx` stays a plain RSC `await` (no
      `HydrationBoundary`) — a read-only public page, no reason to
      introduce the known-risky prefetch pattern here.
- [ ] Any new `force-dynamic` export added to a page in this stage gets
      the same scrutiny as Stage 6's finding: check if the page is
      already auto-detected as dynamic before adding it, given the
      established force-dynamic + client-mount-setState bug class.
- [ ] Preserve every existing `data-testid` — cross-check against the
      current source before considering each file done (same rule as
      Stage 6, where 2 real regressions were caught this way).

## Implementation

- [ ] `entities/decision/api.ts`: `scenariosQuery`, `personasQuery`,
      `runDecisionMutation`, `resolveWizardMutation`, `compareCiiQuery`,
      `matrixQuery`.
- [ ] `entities/decision-passports/api.ts`: `createPassportMutation`,
      `getPublicPassport` (plain async fn for the RSC page, not
      `queryOptions`).
- [ ] Reskin `decision-wizard/*` (`DecisionWizardPanel`, `DecisionWizardStep`,
      `DecisionWizardSummary`): RadioCards steps, nuqs step state,
      `useMutation` for resolve.
- [ ] Reskin `decision-personalization/*` (`DecisionWeightSlider(s)`,
      `DecisionWeightSummary`, `DecisionPersonalizationSummary`): Radix
      `Slider`, debounced live recompute, nuqs weight state.
- [ ] Reskin `decision-run/*` (`DecisionRunForm`, `DecisionResults`,
      `DecisionResultCard`, `DecisionBreakdown`, `DecisionCountryTrustBadge`,
      `DecisionSources`, `DecisionWarnings`): `AnalysisOverlay` during run,
      `GaugeArc`/`Badge`/`Card`/`CriteriaWeightBars`.
- [ ] Reskin `decision-visual-comparison/*` (`DecisionCiiComparison`,
      `CiiComparisonSummary`, `CiiMetricCompareBars` → `CriteriaWeightBars`,
      `CiiCompareSpiderChart` → `RadarChart`, `CiiMetricWinnerList`,
      `CiiComparisonEmptyState`).
- [ ] Reskin `compare-matrix/*` (`CompareMatrixView`, `CountryScenarioMatrix`,
      `MatrixCell`, `MatrixEmptyState`, `MatrixLegend`, `MatrixSummary`).
- [ ] Reskin `decision-passports/*` (`DecisionPassportActions`) +
      `app/[locale]/decision/passports/[token]/page.tsx` onto `PassportCard`.
- [ ] Update `app/[locale]/decision/page.tsx` and `app/[locale]/compare/page.tsx`
      wrappers if their shells need restyling (Kicker/heading pattern from
      Stage 5/6).

## Verification

- [ ] `pnpm --filter web typecheck` / `lint`
- [ ] `pnpm build` — check for the duplicate-DOM bug class on any touched
      force-dynamic page (fresh Playwright context check, not the manual
      browser tool per Stage 6's documented false-positive risk).
- [ ] Manual browser check: wizard → run → result → compare → matrix →
      passport → public passport link, both locales, mobile viewport.
- [ ] `npx playwright test` (full suite) — must stay green; update specs
      only where markup genuinely changed.
- [ ] `python dev_tools_scripts_runner.py full-check`

## Completion

- [ ] Commit(s)
- [ ] Merge to `main`, push
- [ ] Final report
