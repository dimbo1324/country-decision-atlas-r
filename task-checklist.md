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

- [+] Explored `apps/web-prototype`'s 9 chart components + `chartColors.ts`,
      `DriftBoard`, `PassportCard`, `data/generator.ts` type defs.
- [+] Confirmed current `packages/ui` state (from Stage 1+2, not done by me):
      `hooks/useCanvasLoop` + `useReducedMotion` already ported verbatim;
      `primitives/ChartFrame` + `Counter` already ported; no `charts/` folder
      yet; no `d3-scale`/`d3-shape` anywhere in the repo; no Vitest config
      anywhere (out of scope for this stage — not a Stage 4 criterion).
- [+] Confirmed `apps/web` has zero chart usage today — nothing to replace,
      pure net-new addition via `packages/ui`.

## Design decisions (recorded before writing code)

- [+] `packages/ui/src/charts/` — new folder for all 9 base charts + 2 new
      visualizations + `DriftBoard`/`PassportCard` composites + shared
      `types.ts` + the visibility registry.
- [+] Color prop unification: prototype charts take a raw `colorVar: string`
      (e.g. `"--color-gold"`); Stage 4's data contract asks for `accent?`
      (semantic) — ported charts take `accent: Accent = "gold"` and resolve
      `--color-${accent}` internally (same template `MetricCard` already
      uses), not a literal copy of the raw-string prop.
- [+] `live`/`static` mode is new work (grepped prototype — no chart has it
      today, only a slide-visibility `active` boolean). Canvas-breathing
      charts (Radar/Sparkline/Heatmap/RankFlow): gate the periodic
      `target` re-randomization behind `mode === "live"`; static mode lerps
      once to the real value and holds. Plain-CSS breathing charts
      (DivergingMeter/BarColumns): gate their `setInterval` jitter the same
      way. Single-value SVG entrance charts (ProgressRing/GaugeArc/
      DonutChart) had no continuous breathing before — added an optional
      subtle live-mode oscillation of the *visual* fill only (ring/arc/donut
      geometry), while the text number always settles and never jitters.
      `PassportCard`'s `GlidingNumber` glides between real toggled values
      already (not decorative) — no `mode` prop added, deliberate no-op.
- [+] `Confidence` type extracted to `lib/confidence.ts` (not `charts/types.ts`)
      so `primitives/ChartFrame` doesn't have to depend on `charts/` —
      correct layering (primitives sit below charts).
- [+] Visibility registry: `ChartVisibilityProvider` (context holding one
      `IntersectionObserver`) + `useChartVisible(ref)` hook, defaulting to
      `visible=true` with no provider present (Storybook / standalone usage
      keeps working unchanged). Each canvas chart combines
      `active && isVisible` before calling `useCanvasLoop`.
- [+] `ChartFrame` extended with optional `verifiedAt?`/`confidence?` props,
      rendered via the existing generic `Badge` primitive — not a new
      dependency on `apps/web`'s `ConfidenceBadge`/`FreshnessBadge` (wrong
      direction: `packages/ui` cannot depend on the consuming app).
- [-] `d3-shape` — planned but not added. `LegalSignalTimeline` only needed
      `d3-scale` (plain circles/lines, no curve/arc path generation); adding
      an unused dependency would violate the project's own dependency rule
      ("no new dependency without justification"). Can be added later if a
      future chart genuinely needs path generation.

## Implementation

- [+] `packages/ui/src/charts/types.ts`: `ChartDatum`, `ChartMode`, plus the
      per-chart data shapes ported from prototype's `data/generator.ts`
      (`DonutSegment`, `HeatmapData`, `RankFlowSeries`, `DriftBoardRow`,
      `PassportData`), `accent` instead of `colorVar` where applicable.
- [+] `packages/ui/src/charts/useChartVisibility.tsx`: provider + hook.
- [+] `useCanvasLoop`: tab-visibility pause/resume, fixed after a real bug
      found in verification (see below).
- [+] Ported charts (each with a `.stories.tsx`: Live, Static, ReducedMotion):
      `RadarChart`, `SparklineChart`, `DivergingMeter`, `ProgressRing`,
      `GaugeArc`, `DonutChart`, `Heatmap`, `RankFlow`, `BarColumns`.
- [+] Ported composites: `DriftBoard` (row sparklines + Drawer dossier),
      `PassportCard` (toggles + gliding recompute).
- [+] New: `LegalSignalTimeline` (SVG + `d3-scale` for the time axis) with
      its own `.stories.tsx` (Default, ReducedMotion).
- [+] New: `CriteriaWeightBars` (horizontal signed-contribution bars, no
      library) with its own `.stories.tsx`.
- [+] `ChartFrame.tsx`: `verifiedAt`/`confidence` props + badge render;
      `ChartFrame.stories.tsx` gained a `WithTransparencyBadges` story.
- [+] Added `d3-scale` + `@types/d3-scale` to `packages/ui/package.json`;
      `pnpm install` run at repo root.
- [+] `packages/ui/src/index.ts`: exports everything new.
- [+] `ChartVisibilityDemo.stories.tsx`: a 10-chart scrollable list wrapped
      in one `ChartVisibilityProvider`, standing in for "6+ charts on one
      page" since `apps/web` has no chart-consuming page yet (lands in
      Stages 5+).
- [+] `.storybook/ForceReducedMotion.tsx`: story-only helper patching
      `matchMedia` so a dedicated "ReducedMotion" story exists per chart
      without needing a global Storybook toolbar toggle.
- [+] `.claude/launch.json`: added a `ui-storybook` preview target (port
      6006) — didn't exist before, needed it to actually verify this stage
      in a browser.

## Bugs found and fixed during verification (not present before this stage)

- [+] **Storybook never actually applied Tailwind/the design system.**
      `packages/ui/.storybook/main.ts` never registered the
      `@tailwindcss/vite` plugin (already a devDependency, just never wired
      into Storybook's Vite config via `viteFinal`) — confirmed via direct
      browser inspection: `getComputedStyle` showed `--color-c1` empty,
      body background transparent instead of the theme's dark navy, and
      Tailwind utility classes like `h-full`/`w-full` had zero effect (a
      canvas stayed at the browser's native 300×150 default regardless of
      its parent's size). This means every story shipped in Stage 1-3 has
      been rendering completely unstyled in Storybook this whole time — a
      pre-existing gap, not something this stage introduced, but it directly
      blocked verifying this stage's own charts, so fixed it: added
      `viteFinal` registering `tailwindcss()`, mirroring exactly how
      `apps/web-prototype/vite.config.ts` already does it for its own dev
      server. Re-verified after the fix: `--color-c1` resolves correctly,
      body background matches the theme, and canvas backing-store sizing
      now correctly tracks its CSS box.
- [+] **`useCanvasLoop`'s new tab-visibility pause gated the *initial* start
      on `document.visibilityState`, not just transitions.** Caught by
      testing in this session's own browser-automation environment, which
      reports `visibilityState: "hidden"` for any unfocused tab (confirmed
      directly via `document.visibilityState`/`document.hasFocus()`) — the
      same behavior a headless Playwright run or CI browser commonly has.
      Gating the first `start()` call on that would have silently stopped
      every canvas chart from ever drawing under E2E/CI, not just real
      backgrounded tabs. Fixed: the initial mount always calls `start()`
      unconditionally; only a *subsequent* `visibilitychange` event (an
      actual transition, which does fire reliably) pauses/resumes the loop
      going forward. Re-verified: canvas backing store now syncs to its CSS
      size correctly on mount regardless of the environment's focus state.

## Verification

- [+] `packages/ui` typecheck (`tsc --noEmit`) and lint (`eslint .`) clean.
- [+] `packages/ui` Storybook builds (`build-storybook`) with every new
      story, including reduced-motion variants — rebuilt again after both
      bug fixes above, still clean.
- [+] Browser walkthrough via the Storybook dev server (`.claude/launch.json`
      `ui-storybook` target): confirmed via DOM/JS inspection (screenshot
      capture itself was broken in this session for *any* page, including a
      static external site — an environment issue, not a code issue):
      `ProgressRing`'s ReducedMotion story shows the exact settled value
      ("71") instantly; `DriftBoard` row click opens the Drawer dossier with
      correct drift value/direction/copy; `PassportCard`'s nomad-mode toggle
      correctly flips `aria-checked` and recomputes the underlying score
      (the *visual* glide itself couldn't be observed frame-by-frame here —
      this automation environment's unfocused tab throttles
      `requestAnimationFrame` entirely, confirmed by instrumenting
      `window.requestAnimationFrame` directly and by the identical symptom
      recurring across two unrelated components); `LegalSignalTimeline`
      renders all 5 event markers in chronological order with correct
      dates/countries; `CriteriaWeightBars` renders all 5 signed
      contributions correctly; `ChartVisibilityDemo` renders 10 canvases
      with no console errors.
- [+] Root `pnpm quality` (format:check, lint, typecheck, build for
      `apps/web`) green — confirms `apps/web` is unaffected (it doesn't
      import `packages/ui/charts` yet).
- [-] Full Playwright e2e suite **not re-run**: `git status` confirms zero
      files under `apps/web/` changed this stage, so the suite (which only
      exercises `apps/web`) has nothing new to catch — would be pure
      overhead. Flagging honestly rather than silently skipping.
- [+] `prettier --check`/`--write` run directly against the new `.tsx` files
      (root `format:check`'s glob only covers `packages/**/*.{ts,json}`, not
      `.tsx` — a pre-existing scope gap, left as-is, out of scope for this
      stage).

## Completion

- [+] Fill this checklist (`+`/`-`).
- [+] Final report: what shipped, what's deferred (Vitest setup, real
      `apps/web` page usage — both land in later stages), any risks.
