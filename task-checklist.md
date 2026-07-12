# Task: Frontend Stage 1 + Stage 2 (design-system foundation + primitives)

Source plan: `docs/_arch_/FRONTEND_IMPLEMENTATION_PLAN.md`, §7 Этап 1 и Этап 2.
Scope: `packages/ui` foundation + primitive component library, wired into
`apps/web` (Next.js). No page-by-page migration (that is Stage 5+), no
charts library (Stage 4), no data/auth layer changes (Stage 3). Single
branch for the whole task per owner instruction — no sub-branches.

## Preparation

- [ ] Read prototype source for every component being ported (tokens,
      Card, Button, Kicker, Icon, Counter, ChartFrame, DataTable, Drawer,
      Accordion, Toggle, TimelineList, SignalTicker, MetricCard,
      BackgroundTexture, BackgroundFX, useCanvasLoop, useReducedMotion).
- [ ] Inspect current `apps/web` state: no Tailwind installed yet, legacy
      `styles.css` (3001 lines), existing badges/EmptyState/ErrorState/
      LoadingState/Skeleton in `shared/ui`.

## Stage 1 — `packages/ui` foundation

- [ ] Create `packages/ui` workspace package (tokens, lib, hooks, shell).
- [ ] Port design tokens (`@theme` palette/fonts/easing) from prototype's
      `index.css` into `packages/ui/src/tokens/theme.css`.
- [ ] Port `BackgroundTexture`, `BackgroundFX`, `useCanvasLoop`,
      `useReducedMotion`, `cn`, `ACCENTS`.
- [ ] Add Tailwind v4 to `apps/web` (previously absent) + PostCSS config;
      `transpilePackages` for `@country-decision-atlas/ui`.
- [ ] Wire fonts via `next/font/google` (Playfair Display, Crimson Text,
      IM Fell English) as CSS variables consumed by the theme.
- [ ] Render background layers once in the root layout with
      `prefers-reduced-motion` degradation.
- [ ] Storybook in `packages/ui` with the dark theme wrapper + fonts.

## Stage 2 — primitive component library

- [ ] Port prototype primitives as-is (Card, Button, Kicker, Icon, Counter,
      MetricCard, ChartFrame, DataTable, Drawer, Accordion, Toggle,
      TimelineList, SignalTicker).
- [ ] Build Radix-based primitives: Dialog, Popover, Tooltip, Tabs, Select,
      DropdownMenu, Slider — styled with tokens, CVA variants.
- [ ] Toast via Sonner (styled wrapper).
- [ ] Field form wrapper (label/error/hint) for React Hook Form + Zod.
- [ ] RadioCards, Pagination, Breadcrumbs (built from scratch on tokens).
- [ ] Reskin `apps/web`'s existing badges (Confidence/Freshness/Trust/
      Impact/Status/Localization) and states (Empty/Error/Loading/
      Skeleton) to render through the new primitives — same props/exports,
      so all existing call sites pick up the new skin unchanged.
- [ ] Story per primitive in Storybook.

## Verification

- [ ] `packages/ui` typecheck/lint/build.
- [ ] `apps/web` typecheck/lint/build.
- [ ] Storybook builds/runs.
- [ ] Browser check: home page renders on the warm background with new
      fonts, no console errors; a page using badges/empty/error/loading
      states shows the new skin; reduced-motion stops the canvas layers.
- [ ] Full project quality gate (`python dev_tools_scripts_runner.py
      full-check`) if time allows; otherwise targeted frontend checks only,
      called out honestly in the final report.

## Completion

- [ ] Fill this checklist (`+`/`-`).
- [ ] Final report: what shipped, what's deferred to Stage 3+, any risks.
