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

- [+] New step-wizard structure in `DecisionRunForm.tsx`: stepper header
      (Цель / Откуда / Приоритеты / Запуск), step content conditionally
      rendered, Prev/Next + direct step-jump (non-linear — clicking any
      step button jumps straight there, not just sequential). Step state
      via `useQueryState("step", parseAsInteger.withDefault(1))`.
- [+] Step 1 «Цель»: scenario picker converted to `RadioCards`, wrapped in
      a `data-testid="decision-scenario-select"` container so the
      existing testid stays queryable; individual options get
      `decision-scenario-select-option-<slug>` for free via RadioCards'
      own naming.
- [+] Step 2 «Откуда»: origin-select + candidate checkboxes (unchanged
      elements, just relocated).
- [+] Step 3 «Приоритеты»: persona-select + existing
      `DecisionWeightSliders` (unchanged, already collapsed by default —
      the plan's "свернуто по умолчанию" was already satisfied, no new
      work needed).
- [+] Step 4 «Запуск»: summary `<dl>` of current selections (scenario,
      origin, candidate count, persona, weights-touched) + run button.
- [+] `DecisionWizard` (guided quiz) + `AIDecisionIntentHelper` stay
      always-visible above the stepper, fully untouched — verified via
      the existing `web-mvp-decision-wizard.spec.ts` suite.
- [+] typecheck/lint/prettier clean (packages/ui + apps/web).
- [+] **Accessibility fix found and fixed, not just tested around:**
      `RadioCards` had no way to associate a visible label with its
      `role="radiogroup"` — a pre-existing gap also present in the
      already-shipped `DecisionWizardStep`'s own RadioCards usage, not
      something this wave introduced but newly exposed by an accessibility
      test that specifically probes the flat form. Added an `ariaLabel`
      prop to `RadioCards` (`packages/ui/src/primitives/RadioCards.tsx`),
      applied as `aria-label` on the radiogroup div; `DecisionRunForm`
      now passes `ariaLabel="Сценарий"`.

## 2.1 — e2e updates for step navigation

- [+] Added `tests/e2e/helpers/decision.ts` (`goToDecisionStep(page, n)`)
      — one shared helper for the repeated "jump to step N" pattern,
      used across every file below instead of duplicating the click.
- [+] `web-mvp-decision-ready-scenarios.spec.ts`: option-text reads via
      `[role="radio"]` instead of `<option>`; run-button tests get a
      step-4 jump.
- [+] `web-mvp-decision-personalization.spec.ts`: all 9 tests get a
      step-3 jump before touching persona/weights; `runDecision` helper
      centralizes the step-4 jump for the 3 tests that also run.
- [+] `web-mvp-decision-wizard.spec.ts`: post-apply scenario assertion
      reads RadioCards `aria-checked` instead of `<select>` `.toHaveValue`;
      persona/weights checks get a step-3 jump; manual-override test
      clicks the RadioCards option directly instead of `.selectOption()`.
- [+] `web-mvp-scenario-specific-cii.spec.ts`: single shared `runDecision`
      helper fixed once, cascading to all 8 tests.
- [+] `web-mvp-origin-aware-decision.spec.ts`, `web-mvp-personas.spec.ts`,
      `web-mvp-decision-passport.spec.ts`,
      `web-mvp-platform-foundations.spec.ts`,
      `web-mvp-decision-visual-comparison.spec.ts` (6 tests, same shared
      pattern), `web-mvp-platform-intelligence.spec.ts`: step jumps added
      wherever origin/persona/weights/run fields moved.
- [+] Found beyond the original spot-check list (a broader grep for the
      run button's own accessible-name text, not just testids, surfaced
      these): `web-mvp-main-flow.spec.ts` (scenario check switched from a
      combobox-role lookup to the RadioCards testid, since RadioCards
      carries no combobox role), `web-mvp-pages.spec.ts` (2 tests),
      `web-mvp-locale.spec.ts` (1 test), `web-mvp-ai-invariants.spec.ts`
      (1 test) — all needed a step jump before their role-based run-button
      lookup.
- [+] `web-mvp-analytical-pages.spec.ts`'s "decision page form inputs have
      labels" accessibility test: scenario check switched from
      `getByLabel` (which doesn't apply to a `role="radiogroup"` without
      the new `aria-label`) to `getByRole("radiogroup", {name: ...})`,
      exercising the accessibility fix above rather than working around
      it.
- [+] Full verification: all 15 touched/spot-checked decision-related
      spec files run together against a clean production build — 102
      passed, 1 flake (confirmed transient via isolated re-run: 14/14
      passed in under 12s total). One test
      (`web-mvp-locale.spec.ts` "locale=ru is preserved...") reproduced a
      consistent 3/3 failure at one point during investigation — root
      caused to leaving a manually-started `next dev` preview server
      running, which Playwright's `reuseExistingServer` config silently
      reused instead of its own production build; dev-mode's slower
      client-side transition timing let `page.url()` observe a stale URL
      mid-navigation. Not a code bug — confirmed by a clean production
      rebuild + 3/3 pass. Documented here since it's the second time this
      exact dev/production `.next` mixing has caused confusing failures
      this session (first at the end of Stage 1.3) — worth remembering
      going forward: never leave a `preview_start` dev server running
      during an e2e verification pass.

## 2.2 — Result card deck

- [+] `DecisionResultCard.tsx`: compact always-visible header (rank,
      country, score, `score_label` badge, confidence, localization
      badge) + trust badge + summary + `persona-adjusted-score` (kept
      compact — hard test constraint) + one-line top strength, under
      `result-card`. Rest moves into an `Accordion`
      (`packages/ui/src/primitives/Accordion.tsx`, already existed,
      single-open-at-a-time): route context, remaining strengths,
      weaknesses, risks, breakdown, sources.
- [+] **Route context placement resolved a real conflict, not silently**:
      the plan names "контекст маршрута" as accordion content, but
      `web-mvp-origin-aware-decision.spec.ts` asserts `origin-aware-context`
      visible with zero clicks. `Accordion` opens item 0 by default, so
      making route context accordion item 0 satisfies both — the plan's
      structural intent and the existing test — with no compromise and no
      test rewrite needed for that specific assertion.
- [+] Country-card link kept in the compact area (not accordion) —
      reasoned deviation: it's a simple "view more" navigation link with
      no expand-state dependency, no reason to gate it behind a click.
- [+] Compare top-2/3 link: `DecisionResults.tsx` adds
      `data-testid="compare-top-results-link"`, linking to
      `/compare?countries=slug1,slug2[,slug3]` using the top
      `min(3, results.length)` ranked country slugs. Only shown when
      `results.length >= 2` (a single result has nothing to compare).
- [+] `CompareMatrixView.tsx`: reads a `countries` query param via
      `useSearchParams`, filters the already-fetched matrix dataset
      client-side (no new API call). Missing/empty param falls back to
      the original unfiltered behavior — verified manually: `/compare`
      alone still shows all 3 countries; `/compare?countries=uruguay,russia`
      shows exactly those 2.
- [+] typecheck/lint/prettier clean (packages/ui + apps/web).
- [+] Verified against a clean production build: `result-card`,
      `persona-adjusted-score` (personas.spec.ts, 1.2s),
      `ai-explain-number-button`-inside-`decision-winner-block`
      (ai-invariants.spec.ts) all confirmed visible with zero clicks.
      `decision-visual-comparison.spec.ts` (8 tests) +
      `scenario-specific-cii.spec.ts` (8 tests) +
      `compare-matrix.spec.ts` (12 tests) all pass — CII-comparison
      components and the compare page are unaffected by the result-card
      restructuring, as expected since they're separate components.

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
