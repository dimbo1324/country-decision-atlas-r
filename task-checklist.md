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
- [-] `packages/ui/src/charts/PassportCard.tsx` — evaluated, NOT reused (see
      Design decisions below: prop shape mismatch with real read-only data).
- [+] `packages/ui/src/shell/AnalysisOverlay.tsx` already built (Stage 6,
      reuses `ProgressRing`) — reused as-is.
- [+] `packages/ui/src/lib/scoreLabel.ts` (`scoreLabelStyle`) already built
      (Stage 6, for the dossier's `CountryScores`) — reused for
      `compare-matrix`'s `MatrixCell` instead of a second hand-maintained
      5-band mapping.
- [+] Contract shapes confirmed: `DecisionRunResponse`,
      `DecisionPersonalizationResponse`, `CompareMatrixResponse`,
      `CiiCountryComparisonResponse`, `Scenario`, `Persona`,
      `PersonaWeightProfile`, `DecisionPassportCreateResponse`,
      `DecisionPassportResponse` (doubles as the public token-read shape).

## Design decisions

- [+] All 6 feature domains migrated their raw `useEffect`+fetch to
      TanStack Query `useQuery`/`useMutation`, matching Stage 5/6's
      established pattern — one `entities/*/api.ts` module per domain.
- [+] `AnalysisOverlay` shown during the `decision/run` mutation.
- [-] URL-persisted wizard/weight state via `nuqs` — NOT implemented this
      stage. Deferred: not required for correctness, existing local state
      already worked, and adding it risked scope creep beyond the
      TanStack Query migration that was the actual bulk of the plan. Noted
      as follow-up if the owner wants shareable decision links.
- [-] Radix `Slider` for weight sliders — tried, then explicitly REVERTED
      to native `<input type="range">`. ~10 existing E2E assertions across
      3 spec files use Playwright `.fill(exactValue)` on the slider testid
      to drive real computed-result checks; Radix's ARIA `div[role=slider]`
      does not support `.fill()`. Kept native input with `accent-gold`
      Tailwind styling instead of rewriting the assertions to synthesize
      keyboard/pointer sequences.
- [-] Debounced live recompute on weight change — NOT implemented. Not
      present in the original plan's blocking requirements once the
      Slider decision above was reverted (native range input's own
      `onChange` already batches fine); left as-is to avoid scope creep.
- [~] `CiiCompareSpiderChart.tsx` replaced with `packages/ui`'s
      `RadarChart` — done, clean fit (N metrics as axes, one series per
      country).
      `CiiMetricCompareBars.tsx` NOT replaced with `CriteriaWeightBars` —
      real shape mismatch found: that primitive is signed single-value
      diverging bars, doesn't fit 2-country side-by-side grouped bars.
      Kept hand-rolled, reskinned visually only.
- [+] `compare-matrix`'s `MatrixCell` 5-band colour logic replaced by the
      shared `scoreLabelStyle` helper.
- [-] `PassportCard` reuse for the public token page — evaluated and
      REJECTED. Its prop shape is an interactive tax-treaty/nomad-mode
      toggle demo card that live-recomputes a score; no such recompute
      endpoint exists for the real `DecisionPassportResponse` (read-only).
      Faking that interactivity would misrepresent real data. Kept the
      existing `DecisionResults` + methodology `<dl>` structure, reskinned
      visually instead.
- [+] `/decision/passports/[token]/page.tsx` stayed a plain RSC `await`.
- [+] `force-dynamic` scrutiny applied: removed the redundant
      `export const dynamic = "force-dynamic"` from `compare/page.tsx`
      after confirming via `pnpm build` output (`ƒ (Dynamic)`, auto-detected
      due to `await getLocale()`) and a duplicate-`<h1>` Playwright check
      that it wasn't load-bearing. Kept on the passport token page (real
      per-token RSC `await`, no reason to touch it).
- [+] Preserved every existing `data-testid`; where markup genuinely
      changed (RadioCards instead of native `<select>`, retired CSS-class
      selectors), updated the corresponding test files instead of the
      component (same rule as Stage 6).

## Implementation

- [+] `entities/decision/api.ts`: `allCountriesQuery`, `scenariosQuery`,
      `personasQuery`, `useRunDecisionMutation`, `useResolveWizardMutation`,
      `compareCiiQuery`, `matrixQuery`.
- [+] `entities/decision-passports/api.ts`: `useCreateDecisionPassportMutation`,
      `getPublicPassport` (plain async fn for the RSC page).
- [+] Reskinned `decision-wizard/*`: `RadioCards` steps (added a per-option
      `data-testid` to the shared `RadioCards` primitive), `useMutation`
      for resolve.
- [+] Reskinned `decision-personalization/*`: native range sliders (see
      deviation above), `Card`/`Badge`/`Button`.
- [+] Reskinned `decision-run/*`: `AnalysisOverlay` during run,
      `Card`/`Field`/`FieldLabel`/`Badge`, `DataTable` for
      `DecisionBreakdown`, `DecisionCountryTrustBadge` migrated onto the
      Stage-6-built `countryTrustQuery`.
- [+] Reskinned `decision-visual-comparison/*`: `RadarChart` for the spider
      chart, hand-rolled bars kept (see deviation above).
- [+] Reskinned `compare-matrix/*` onto `scoreLabelStyle` + `DataTable`-style
      table, migrated to `matrixQuery`.
- [+] Reskinned `decision-passports/*` (`DecisionPassportActions`) onto
      `useCreateDecisionPassportMutation` + `Button`; reskinned the public
      token page (see deviation above, no `PassportCard`).
- [+] Reskinned `app/[locale]/decision/page.tsx` and
      `app/[locale]/compare/page.tsx` shells (Kicker/heading pattern).

## Verification

- [+] `pnpm --filter web typecheck` / `lint` — clean.
- [+] `pnpm build` — compiles clean; duplicate-`<h1>` check done for
      `/compare` after removing `force-dynamic`.
- [+] Manual browser + full Playwright coverage across wizard → run →
      result → compare → matrix → passport → public passport link (via
      the existing E2E suite, not a separate manual pass).
- [+] `npx playwright test` (full suite, 285 specs) — 285/285 passing at
      `--workers=2` (the reliable baseline; default worker count produces
      resource-contention flakiness under this Docker+build load,
      documented repeatedly since Stage 5).
- [+] `python dev_tools_scripts_runner.py full-check` — clean except two
      known pre-existing, unrelated failures: `pytest (scripts/synthetic_data)`
      (missing `arabic_reshaper` in that venv) and `go test -race` (no CGO
      toolchain on this Windows machine; the `-race` gate is enforced in
      CI's `ubuntu-latest`, not locally). A transient `pnpm quality` /
      `pre-commit` Prettier formatting gap on 8 already-edited files was
      found and fixed (`prettier --write`); re-run confirmed clean.

## Completion

- [+] Commits: 7 total on the feature branch (query-migration slices per
      domain + a bug-fix/testid-parity commit + a formatting-fix commit).
- [+] Merge to `main` (fast-forward), push to `origin/main`.
- [+] Final report.
- Deferred/out-of-scope, documented above rather than silently dropped:
  nuqs URL state for wizard/weights, debounced live recompute, Radix
  Slider, `CriteriaWeightBars` for the 2-country comparison,
  `PassportCard` reuse on the token page.
