# Task: Frontend Stage 1 + Stage 2 (design-system foundation + primitives)

Source plan: `docs/_arch_/FRONTEND_IMPLEMENTATION_PLAN.md`, §7 Этап 1 и Этап 2.
Scope: `packages/ui` foundation + primitive component library, wired into
`apps/web` (Next.js). No page-by-page migration (that is Stage 5+), no
charts library (Stage 4), no data/auth layer changes (Stage 3). Single
branch for the whole task per owner instruction — no sub-branches.

## Preparation

- [+] Read prototype source for every component being ported (tokens,
      Card, Button, Kicker, Icon, Counter, ChartFrame, DataTable, Drawer,
      Accordion, Toggle, TimelineList, SignalTicker, MetricCard,
      BackgroundTexture, BackgroundFX, useCanvasLoop, useReducedMotion).
- [+] Inspect current `apps/web` state: no Tailwind installed yet, legacy
      `styles.css` (3001 lines), existing badges/EmptyState/ErrorState/
      LoadingState/Skeleton in `shared/ui`.

## Stage 1 — `packages/ui` foundation

- [+] Create `packages/ui` workspace package (tokens, lib, hooks, shell).
- [+] Port design tokens (`@theme` palette/fonts/easing) from prototype's
      `index.css` into `packages/ui/src/tokens/theme.css`. Font-family
      values route through a `--ui-font-*` indirection so the same file
      works unchanged in both apps/web (next/font) and apps/web-prototype
      (Google Fonts `<link>`, unchanged).
- [+] Port `BackgroundTexture`, `BackgroundFX`, `useCanvasLoop`,
      `useReducedMotion`, `cn` (now clsx+tailwind-merge per plan Р-3),
      `ACCENTS`.
- [+] Add Tailwind v4 to `apps/web` (previously absent) + PostCSS config;
      `transpilePackages` for `@country-decision-atlas/ui`. Also required
      an explicit `@source` directive in theme.css — Tailwind v4's
      automatic content detection does not walk out of the consuming app
      into a sibling workspace package by default; found this live via
      browser verification (utility classes were being silently dropped).
- [+] Wire fonts via `next/font/google` (Playfair Display, Crimson Text,
      IM Fell English) as CSS variables consumed by the theme.
- [+] Render background layers once in the root layout with
      `prefers-reduced-motion` degradation (code path unchanged from the
      already-verified prototype implementation; not re-emulated live —
      browser tool has no reduced-motion emulation control).
- [+] Storybook in `packages/ui` with the dark theme wrapper + fonts
      (`build-storybook` verified green).

## Stage 2 — primitive component library

- [+] Port prototype primitives as-is (Card, Button, Kicker, Icon, Counter,
      MetricCard, ChartFrame, DataTable, Drawer, Accordion, Toggle,
      TimelineList, SignalTicker). `TimelineList`'s event type is now a
      standalone `TimelineEvent` (was importing the prototype's synthetic
      data generator type).
- [+] Build Radix-based primitives: Dialog, Popover, Tooltip, Tabs, Select,
      DropdownMenu, Slider — styled with tokens. CVA/enter-exit animation
      classes were dropped where no matching Tailwind plugin exists
      (avoided dead/misleading classNames); Motion-based presence
      transitions are Stage 6+ per the plan's own animation-levels rule.
- [+] Toast via Sonner (styled wrapper + `Toaster`, mounted once in
      apps/web's root layout).
- [+] Field form wrapper (label/error/hint) — framework-agnostic
      (pairs with RHF's `register`/`Controller` at the call site rather
      than hard-depending on react-hook-form/zod inside the shared
      package).
- [+] RadioCards, Pagination, Breadcrumbs (built from scratch on tokens).
- [+] Reskin `apps/web`'s existing badges (Confidence/Freshness/Trust/
      Impact/Status/Localization) and states (Empty/Error/Loading/
      Skeleton) to render through the new primitives — same props/exports,
      so all existing call sites (55 occurrences across 35 files) pick up
      the new skin unchanged. Feature-local ad-hoc badge/empty markup
      (`CountryDriftBadge`, `CommunityCountryBlock`, `RouteEmptyState`,
      `HomeOverviewEmptyState`) intentionally left untouched — that is
      per-page migration territory (Stage 6/9/10), not the shared library.
- [+] Story per primitive in Storybook (30 story files, one per primitive
      plus a Shell/Background story for the texture+FX layers).

## Verification

- [+] `packages/ui` typecheck/lint/build (`build-storybook`) — all clean.
- [+] `apps/web` typecheck/lint/`next build` — all clean (24 routes).
- [+] Storybook builds/runs.
- [+] Browser check: home page renders on the warm background with new
      fonts (Crimson Text body, Playfair Display headings, confirmed via
      computed styles), 2 background canvases present, zero console
      errors; `/countries` (no backend running) renders the reskinned
      `ErrorState` with correct tokens (bg-bg3, terra border, Playfair
      title, mono terra code) after the `@source` fix. Reduced-motion not
      live-emulated (tool limitation) — verified by code inspection only.
- [+] `tests/e2e/web-mvp-localization-badges.spec.ts` (6/6 passed) against
      the reskinned badges.
- [-] Full project quality gate (`python dev_tools_scripts_runner.py
      full-check`) — NOT run. This task only touched frontend
      (packages/ui, apps/web); ran the full Playwright e2e suite instead
      (see final report for result) as a lighter-weight substitute. Python/
      Go/Docker/migration checks are unaffected by this diff and were
      skipped to keep the verification pass proportionate to the change.

## Completion

- [+] Fill this checklist (`+`/`-`).
- [+] Final report: what shipped, what's deferred to Stage 3+, any risks.
