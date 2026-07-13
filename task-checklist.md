# Task: Frontend Stage 4 (data visualization library)

Source plan: `docs/_arch_/FRONTEND_IMPLEMENTATION_PLAN.md`, §7 Этап 4.
Branch: `feat/frontend-visualization-library` (fresh off `main` — the Stage
1+2/3 branch was already merged and deleted; no continuation possible).

Scope note: `docs/_ideas_and_concepts_/` is never read per the project's hard
rule, even though the plan doc recommends the design-system reference under
it — everything needed (palette, motion, perf rules) is already excerpted in
the plan doc itself (§3, §5), and the actual components to port live in
`apps/web-prototype` (unrestricted).

## Preparation

- [ ] Explored `apps/web-prototype`'s 9 chart components + `chartColors.ts`,
      `DriftBoard`, `PassportCard`, `data/generator.ts` type defs.
- [ ] Confirmed current `packages/ui` state (from Stage 1+2, not done by me):
      `hooks/useCanvasLoop` + `useReducedMotion` already ported verbatim;
      `primitives/ChartFrame` + `Counter` already ported; no `charts/` folder
      yet; no `d3-scale`/`d3-shape` anywhere in the repo; no Vitest config
      anywhere (out of scope for this stage — not a Stage 4 criterion).
- [ ] Confirmed `apps/web` has zero chart usage today — nothing to replace,
      pure net-new addition via `packages/ui`.

## Design decisions (recorded before writing code)

- [ ] `packages/ui/src/charts/` — new folder for all 9 base charts + 2 new
      visualizations + `DriftBoard`/`PassportCard` composites + shared
      `types.ts` + the visibility registry.
- [ ] Color prop unification: prototype charts take a raw `colorVar: string`
      (e.g. `"--color-gold"`); Stage 4's data contract asks for `accent?`
      (semantic) — ported charts take `accent: Accent = "gold"` and resolve
      `--color-${accent}` internally (same template `MetricCard` already
      uses), not a literal copy of the raw-string prop.
- [ ] `live`/`static` mode is new work (grepped prototype — no chart has it
      today, only a slide-visibility `active` boolean). Canvas-breathing
      charts (Radar/Sparkline/Heatmap/RankFlow): gate the periodic
      `target` re-randomization behind `mode === "live"`; static mode lerps
      once to the real value and holds. Plain-CSS breathing charts
      (DivergingMeter/BarColumns): gate their `setInterval` jitter the same
      way. Single-value SVG entrance charts (ProgressRing/GaugeArc/
      DonutChart) had no continuous breathing before — add an optional
      subtle live-mode oscillation for consistency, default stays a single
      entrance animation. `PassportCard`'s `GlidingNumber` glides between
      real toggled values already (not decorative) — no `mode` prop added,
      noted as a deliberate no-op rather than forced.
- [ ] Visibility registry: `ChartVisibilityProvider` (context holding one
      `IntersectionObserver`) + `useChartVisible(ref)` hook, defaulting to
      `visible=true` with no provider present (Storybook / standalone usage
      keeps working unchanged). Each canvas chart combines
      `active && isVisible` before calling `useCanvasLoop`.
- [ ] Tab-hidden pause is a *different* mechanism from the IntersectionObserver
      registry (Page Visibility API, not scroll-visibility) — added directly
      inside the shared `useCanvasLoop` hook so every chart gets it for free:
      `visibilitychange` listener stops/resumes the rAF loop.
- [ ] `ChartFrame` extended with optional `verifiedAt?`/`confidence?` props,
      rendered via the existing generic `Badge` primitive — not a new
      dependency on `apps/web`'s `ConfidenceBadge`/`FreshnessBadge` (wrong
      direction: `packages/ui` cannot depend on the consuming app).

## Implementation

- [ ] `packages/ui/src/charts/types.ts`: `ChartDatum`, `ChartMode`, plus the
      per-chart data shapes ported from prototype's `data/generator.ts`
      (`DonutSegment`, `HeatmapData`, `RankFlowSeries`, `DriftBoardRow`,
      `PassportData`), `accent` instead of `colorVar` where applicable.
- [ ] `packages/ui/src/charts/useChartVisibility.tsx`: provider + hook.
- [ ] `useCanvasLoop`: add tab-visibility pause/resume.
- [ ] Port charts (each with a `.stories.tsx`: live, static, reduced-motion
      variants): `RadarChart`, `SparklineChart`, `DivergingMeter`,
      `ProgressRing`, `GaugeArc`, `DonutChart`, `Heatmap`, `RankFlow`,
      `BarColumns`.
- [ ] Port composites: `DriftBoard` (row sparklines + Drawer dossier),
      `PassportCard` (toggles + gliding recompute).
- [ ] New: `LegalSignalTimeline` (SVG + `d3-scale` for the time axis; no
      `d3-shape` needed — event markers are plain circles/paths, not curve
      geometry) with its own `.stories.tsx`.
- [ ] New: `CriteriaWeightBars` (horizontal contribution bars, no library)
      with its own `.stories.tsx`.
- [ ] `ChartFrame.tsx`: add `verifiedAt`/`confidence` props + badge render.
- [ ] Add `d3-scale`, `d3-shape`, `@types/d3-scale`, `@types/d3-shape` to
      `packages/ui/package.json`; `pnpm install`.
- [ ] `packages/ui/src/index.ts`: export everything new.
- [ ] One Storybook story demonstrating the visibility registry with a long
      scrollable list of many charts (stands in for "6+ charts on one page"
      since `apps/web` has no chart-consuming page yet — those land in
      Stages 5+).

## Verification

- [ ] `packages/ui` typecheck (`tsc --noEmit`) and lint (`eslint .`) clean.
- [ ] `packages/ui` Storybook builds (`build-storybook`) with every new
      story, including reduced-motion variants.
- [ ] Manual Storybook walkthrough: live vs static modes visibly differ;
      `prefers-reduced-motion` degrades every chart to static/no-motion;
      DriftBoard drawer opens/closes; PassportCard toggles recompute the
      score with a glide; the visibility-registry story only animates
      charts scrolled into view.
- [ ] Root `pnpm quality` (still scoped to `apps/web` — confirm it stays
      green since `apps/web` doesn't import `packages/ui/charts` yet).
- [ ] Full Playwright e2e suite green (regression check — Stage 4 doesn't
      touch `apps/web` routes, so this should be a no-op confirmation).

## Completion

- [ ] Fill this checklist (`+`/`-`).
- [ ] Final report: what shipped, what's deferred (Vitest setup, real
      `apps/web` page usage — both land in later stages), any risks.
