# Task: Frontend redesign — Этап 2 (Волна «Сценарий решения»)

Source: owner-provided plan (pasted in chat). Follows Этап 1 (`2584a5f`,
merged to main). Branch: `feat/frontend-decision-scenario-v1`, fresh off
`main`.

Three sub-items: 2.1 decision wizard restructuring, 2.2 result card deck,
2.3 passport visual polish.

## Pre-implementation investigation (verified, not assumed)

- `DecisionRunForm.tsx` is currently ONE flat form (`grid lg:grid-cols-2`)
  with an existing collapsible `DecisionWizard` (8-question guided quiz,
  `features/decision-wizard/`, separate concept from "4 steps" — it
  pre-fills the flat form's fields via `onApply`, stays untouched and
  always-visible above the new stepper) plus `AIDecisionIntentHelper`
  (same treatment), then manual fields: origin-select, candidate
  checkboxes, scenario-select (native `<select>`), persona-select
  (native `<select>`), `DecisionWeightSliders` (already a `<details>`
  accordion, closed by default — the plan's "свернуто по умолчанию" for
  Приоритеты is already satisfied by this existing component, no new
  work needed there), run button.
- `decision-scenario-select` is currently a native `<select>`.
  `DecisionWizardStep` (the existing quiz's own option picker) already
  uses `RadioCards` with testid pattern `${name}-option-${value}` — same
  primitive/pattern the plan asks for in step 1, proven and reusable.
  Switching the flat form's scenario field to RadioCards breaks every
  test using `.selectOption()`/`.locator("option")` on
  `decision-scenario-select` — confirmed via a full e2e catalog (see
  below), not assumed.
- Full e2e catalog (via Explore subagent, cross-checked against source):
  `origin-select`, `decision-scenario-select`, `persona-selector`,
  `decision-run-button` are all currently visible/interactable with
  **zero prior clicks** in most decision specs (fill fields → click run,
  no step navigation). `decision-weights-panel`/`decision-weight-slider-*`
  already require an explicit `<details>` open first — existing
  precedent for "click to reveal" in this exact form. Files touching
  these testids: `web-mvp-decision-personalization`,
  `web-mvp-decision-wizard`, `web-mvp-decision-ready-scenarios`,
  `web-mvp-scenario-specific-cii`, `web-mvp-origin-aware-decision`,
  `web-mvp-personas`, `web-mvp-decision-passport`,
  `web-mvp-platform-foundations`, plus incidental checks in
  `web-mvp-main-flow`, `web-mvp-ai-invariants`, `web-mvp-locale`,
  `web-mvp-localization-badges`, `web-mvp-pages`.
- **Hard constraints for 2.2** (must stay visible with zero clicks after
  restructuring, confirmed via the same e2e catalog): `result-card`
  (main-flow.spec.ts), `persona-adjusted-score` (personas.spec.ts),
  `ai-explain-number-button` nested inside `decision-winner-block`
  (ai-invariants.spec.ts). `origin-pair-context`/`origin-pair-context-empty`
  have **zero** e2e coverage — free to move behind an accordion.
  `decision-winner-block` itself needs no restructuring — the plan's own
  text says it "уже есть" (already exists) as the big-winner-on-top
  treatment.
- `/compare` currently has no query-param pre-fill mechanism at all
  (`CompareMatrixView` always renders the full matrix) — building the
  "compare top-2/3" pre-fill is new, contained work (client-side filter
  of an already-fetched dataset), not wiring up an existing feature.
- Real passport page (`decision/passports/[token]/page.tsx`) currently
  reuses plain `Card`/`Badge` primitives, not `PassportCard`.
  `PassportCard` (packages/ui/src/charts/PassportCard.tsx) is the
  web-prototype's mockup component with **live recompute toggles** —
  the plan explicitly says port only decorative fragments (perforated
  edge, stamp), not the component, and explicitly not the toggles, since
  the real passport is an immutable snapshot (matches invariant #4 in
  `02_Реестр_инвариантов.md`: methodology/results carry a version, no
  silent recompute).

## Design decisions (reasoned, not silently assumed)

- Step navigation: a horizontal stepper header (4 clickable step
  buttons, direct non-linear jump allowed — not strictly sequential)
  plus Prev/Next buttons. No global keyboard arrow-key hijacking (same
  reasoning as Stage 1.3's HorizontalPager — the steps contain real
  form controls, e.g. `<select>`, that already use arrow keys
  themselves; hijacking them globally would actively break those
  controls, worse than the home-page case). Native buttons are
  sufficiently keyboard-accessible on their own.
- Step content is simple conditional rendering (no transform/slide
  animation) — this is a controlled form wizard, not a content carousel;
  animating it adds risk with no clear UX benefit the plan asked for.
- Step state: `useQueryState("step", parseAsInteger.withDefault(1))`
  (nuqs), matching the plan's `?step=2` and the established pattern from
  `CountryCatalogView`'s pagination.
- `decision-scenario-select` RadioCards wrapped in a
  `data-testid="decision-scenario-select"` container div (RadioCards
  itself has no container testid, only per-option) so existing
  `.toBeVisible()` checks on that testid keep working; individual
  options get `decision-scenario-select-option-<slug>` for free via
  RadioCards' own naming.

## 2.1 — Decision wizard: 4 horizontal steps

- [ ] New step-wizard structure in `DecisionRunForm.tsx`: stepper header
      (Цель / Откуда / Приоритеты / Запуск), step content conditionally
      rendered, Prev/Next + direct step-jump.
- [ ] Step 1 «Цель»: scenario picker converted to `RadioCards`.
- [ ] Step 2 «Откуда»: origin-select + candidate checkboxes (unchanged
      elements, just relocated).
- [ ] Step 3 «Приоритеты»: persona-select + existing
      `DecisionWeightSliders` (unchanged, already collapsed by default).
- [ ] Step 4 «Запуск»: summary of current selections (scenario, origin,
      candidates, persona, weights-touched) + run button.
- [ ] `DecisionWizard` (guided quiz) + `AIDecisionIntentHelper` stay
      always-visible above the stepper, fully untouched.
- [ ] typecheck/lint/prettier clean.

## 2.1 — e2e updates for step navigation

- [ ] `web-mvp-decision-ready-scenarios.spec.ts`: option-text reads via
      RadioCards, run-button tests get a step-4 jump.
- [ ] `web-mvp-decision-personalization.spec.ts`: weight-slider tests
      get a step-3 jump before the existing `<details>` open.
- [ ] `web-mvp-decision-wizard.spec.ts`: post-apply assertions on
      scenario/persona read RadioCards state instead of `<select>` value
      where applicable.
- [ ] `web-mvp-scenario-specific-cii.spec.ts`, `web-mvp-origin-aware-decision.spec.ts`,
      `web-mvp-personas.spec.ts`, `web-mvp-decision-passport.spec.ts`,
      `web-mvp-platform-foundations.spec.ts`: step jumps added where fields
      moved.
- [ ] Spot-check `web-mvp-main-flow.spec.ts`, `web-mvp-ai-invariants.spec.ts`,
      `web-mvp-locale.spec.ts`, `web-mvp-localization-badges.spec.ts`,
      `web-mvp-pages.spec.ts` for incidental breakage.

## 2.2 — Result card deck

- [ ] `DecisionResultCard.tsx`: compact always-visible header (rank,
      country, score, confidence, top strength line) under `result-card`;
      `persona-adjusted-score` stays visible (test constraint); rest
      (weaknesses, risks, route context, breakdown, sources, country-card
      link) moves into an `Accordion`.
- [ ] Compare top-2/3 link: `/compare?countries=slug1,slug2` pre-fill.
- [ ] `CompareMatrixView`/`CountryScenarioMatrix`: read `countries` query
      param, filter matrix client-side when present.
- [ ] typecheck/lint/prettier clean.
- [ ] Verify `result-card`, `persona-adjusted-score`,
      `ai-explain-number-button`-inside-`decision-winner-block` all still
      visible with zero clicks.

## 2.3 — Passport visual polish

- [ ] Perforated-edge top border + circular stamp/seal ported as
      decorative markup into the passport page header (not the
      PassportCard component).
- [ ] Mono-formatted REF/date/status metadata.
- [ ] No live toggles, no recompute — page stays a pure server-rendered
      snapshot.

## Verification (before merge)

- [ ] `packages/ui`/`apps/web` typecheck/lint/build clean.
- [ ] Full Playwright suite green (or honestly documented flakes only).
- [ ] Visual baselines re-shot once at the end of the whole wave.
- [ ] Manual browser check: full decision flow start to finish, passport
      page.

## Completion

- [ ] Fill this checklist (`+`/`-`).
- [ ] Commit on `feat/frontend-decision-scenario-v1`.
- [ ] **STOP before merge/push** — ask the user explicitly, given the
      Stage 1 finding that push authorization doesn't automatically
      carry over between waves.
- [ ] Final report.
