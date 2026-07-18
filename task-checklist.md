# Task: Frontend redesign — Этап 5 (Закрепление / consolidation)

Owner-provided plan, §"Этап 5 — Закрепление". Unlike Stages 0-3 (which
landed directly on `main` by owner instruction for that work), this task
runs on a dedicated branch (`feat/frontend-redesign-stage-5-consolidation`)
per explicit owner instruction this session: incremental commits, no
merge to `main`, no push to `origin/main` — only a push of this branch to
`origin` at the end.

Scope for this branch, per the owner's "доделай оставшиеся задачи" request
and the audit from the previous conversation turn:

- Этап 5's five sub-items (component tests, Storybook stories/play-tests,
  JS budget CI gate, a11y hardening, i18n content-strategy decision).
- Two small previously-flagged tech-debt items:
  `.claude/launch.json` missing `APP_ENV=local` on `web-prod`, and dead
  code `apps/web/src/shared/api/watchlists.ts`.

Explicitly OUT of scope for this branch (confirmed again before starting,
not silently dropped):

- Catalog (Stage 1.2) CII ring / drift trend arrow — blocked on a backend
  contract gap (`cii_score`/`country_drift` not on the catalog list
  endpoint's response schema); a schema + repository + service change,
  not a "consolidation" task. Left as backend follow-up per Stage 1.2's
  own documented decision.
- Catalog sticky filter/sort panel — blocked on there being no filter/sort
  UI on the catalog page at all yet; building one from scratch is a
  materially larger, different task than "make it sticky". Left as its
  own follow-up per Stage 1.2's own documented decision.

## Pre-flight (verified, not assumed)

- [+] `apps/web` has Vitest + jsdom, but **no** `@testing-library/react`
      anywhere in the repo (checked root/`apps/web`/`packages/ui`
      `package.json`s) and only one existing `.test.tsx` file
      (`shared/ui/semantic-labels.test.tsx`), which is a plain
      function-level test despite the extension — no actual component
      render exists yet. `packages/ui` has `msw`/`msw-storybook-addon`
      for Storybook only, no vitest-level MSW handler setup anywhere.
      Adding `@testing-library/react` (+ `@testing-library/jest-dom`,
      `@testing-library/user-event`) to `apps/web` is therefore a new,
      justified dependency: it's what the owner's own plan asks for by
      name, actively maintained, industry-standard, and doesn't duplicate
      anything already installed.
- [+] `CountryDossier` receives `card` as an already-resolved prop (no
      internal fetch) and imports its 17 sections' heavy feature blocks
      (`CommunityCountryBlock`, `TrustSurfaceBlock`, etc.) as named
      imports — mockable via `vi.mock` so the component test can target
      tab-switching/URL-sync/`DossierRail` behavior without needing MSW
      handlers for 17 unrelated domains. `useFeatureEnabled` reads a
      plain React Context (no TanStack Query) — mocked directly via
      `vi.mock` on `FeatureProvider`, simpler than wrapping a real
      provider and mocking its underlying fetch.
- [+] `HomeDeck` also receives all panel data as already-resolved props
      (no internal fetch) and imports its 5 panel components by name —
      same `vi.mock` strategy. Its only runtime dependencies needing a
      jsdom shim are `useMediaQuery`/`useReducedMotion`, both thin
      `window.matchMedia` wrappers.
- [+] `DecisionRunForm` is the one case needing real MSW: it calls
      `allCountriesQuery`/`scenariosQuery` (2 real endpoints) to populate
      its two `<select>`s. A real MSW-backed test is worth it here since
      the actual multi-step interaction (RHF + step navigation) is what
      needs covering, not something to mock away.
- [+] Stage 13 stream 3 already wired `@next/bundle-analyzer` behind
      `ANALYZE=true` for **manual, local-only** audits — confirmed via
      `git show b9d924d`, no CI gate exists today. `full_check.py`'s
      local profiles (`quick`/`backend`/`frontend`/`docker`/`full`/`ci`)
      **do not run `next build` at all** in any profile (checked
      `should_run_phase`'s `profile_phases` dict) — only
      `.github/workflows/quality.yml`'s dedicated `frontend` job runs
      `pnpm build`. Wiring a JS-budget check into `full_check.py` would
      mean adding a new phase that runs a real Next build locally on
      every quick/full run — a materially bigger, riskier change to a
      heavily-relied-on script than this task needs. Chose instead: one
      new standalone script (invokable on its own, runs its own
      `next build` and parses the result) plus one new CI step in the
      existing `frontend` job, right after `Build` — surgical, no changes
      to `full_check.py`.
- [+] Current worst First Load JS (fresh `next build`, this branch):
      recorded in the script's own docstring/constant once measured.
- [+] `next-intl`'s message catalog (`en.json`/`ru.json`, 90 keys) covers
      only app chrome (nav, auth forms, footer, search palette,
      error/not-found) — zero keys for any feature/page content. Country
      data is localized separately via the backend's
      `overlay_localized_fields` service. Every UI label added across
      Stages 0-3 of this redesign (dossier tab names, wizard step names,
      catalog labels, filter-chip option labels) is a hardcoded Russian
      string, unaffected by the `/en/` vs `/ru/` URL locale — confirmed
      by reading `TAB_LABELS`/`STEP_LABELS`/`FilterChipGroup` option
      arrays directly, not assumed. This matches the project's own
      existing hard rule (`.ai/project/12-domain-rules.md`: no AI
      translation without an explicit owner ask) and the whole redesign's
      de facto pattern to date — documenting it as the accepted decision
      rather than opening a large, invasive full-migration effort nobody
      asked for.

## 5.1 — Component tests for the three new layouts (done)

- [+] Added `@testing-library/react`, `@testing-library/jest-dom`,
      `@testing-library/user-event`, `msw` to `apps/web`'s devDependencies;
      wired `@testing-library/jest-dom/vitest` into a new
      `apps/web/vitest.setup.ts`, registered via `vitest.config.ts`'s
      `test.setupFiles`.
- [+] New shared `apps/web/src/test-utils/render.tsx`
      (`renderWithProviders`): fresh `QueryClient` per render (retries
      off), `nuqs/adapters/testing`'s real `withNuqsTestingAdapter`
      (`hasMemory: true`, not a hand-rolled nuqs mock), wrapped in
      `NextIntlClientProvider` — needed because `CountryDossier.tsx`
      itself and `CountryEvidenceSummary` both use `<Link>` from
      `i18n/navigation`, which throws without an intl context even for
      components not under test directly.
- [+] Explicit `afterEach(() => cleanup())` added to `vitest.setup.ts` —
      discovered Testing Library's automatic per-test DOM cleanup never
      registers without `test.globals: true` (which this project
      deliberately doesn't set), so unmounted components were piling up
      and causing "found multiple elements" failures across tests in the
      same file until this was added.
- [+] `IntersectionObserver` and `ResizeObserver` jsdom polyfills added to
      `vitest.setup.ts` — `DossierRail`'s scrollspy and
      `HorizontalPager`'s container-width measurement both construct one
      unconditionally on mount; jsdom has neither.
- [+] `CountryDossier.test.tsx`: mocks the 8 heavy sibling feature blocks
      (community/country-drift/data-journal/migration-board/
      platform-intelligence/routes/trust-surface/what-changed) and
      `useFeatureEnabled` (forced tabbed layout); the `./index`-local
      section components (CII, evidence, scores, sources, etc.) render
      for real from a minimal `card` fixture. 3 tests: default tab +
      all 5 triggers present, switching tabs shows only that tab's
      panel/rail sections (Radix keeps inactive `TabsContent` in the DOM
      with `hidden`, doesn't unmount — asserted via `.not.toBeVisible()`,
      not `.not.toBeInTheDocument()`, after the first attempt proved that
      wrong), community tab renders its own mocked blocks.
- [+] `DecisionRunForm.test.tsx`: real MSW handlers for
      `/api/v1/countries`, `/api/v1/scenarios`, `/api/v1/personas`; mocks
      `useAppLocale`/`useAnalyticsEvent` and the non-wizard-step sibling
      components (`DecisionWizard`, `AIDecisionIntentHelper`,
      `DecisionPassportActions`, `DecisionCiiComparison`,
      `DecisionRiskContext`, `DecisionResults`). 5 tests covering the
      actual behavior (step navigation has no validation gate — only the
      final run button's `disabled` state reacts to candidate/scenario
      state — corrected from this checklist's original "validation
      blocking advance" wording, which didn't match the real
      implementation once read closely): all 4 labels render with step 1
      active, "Далее" advances through all 4 panels, direct step-nav
      jump works, "Назад" disabled only on step 1, run button disables
      once every candidate is unchecked.
- [+] `HomeDeck.test.tsx`: mocks the 5 panel components; a local
      `mockMatchMedia(matchingQueries)` helper drives `useMediaQuery`/
      `useReducedMotion` directly. 3 tests: desktop pager mode (off-screen
      slides `inert`, clicking `pager-next` flips which slide is inert),
      reduced-motion flat fallback (no pager controls at all), narrow
      viewport uses `MobileStack` instead.
- [+] Verify: 77/77 Vitest tests green across all 14 files (11 pre-existing
      + 3 new) in `apps/web`; typecheck/lint clean; `pnpm format:check`
      clean after an auto-fix pass.

## 5.2 — Storybook stories + play-tests for new primitives

- [ ] Confirm/add a story for `Tabs` (packages/ui primitive) using the
      dossier's tab pattern (5 triggers, controlled value) if no story
      exists yet for a multi-tab configuration.
- [ ] Confirm/add a story for `HorizontalPager` (the deck) with a
      play-test exercising next/prev navigation and asserting `inert` on
      off-screen slides.
- [ ] `BoardGrid` already has a story from Stage 3.3 — no action needed,
      noted for completeness.
- [ ] Verify: Storybook builds clean, play-tests pass.

## 5.3 — First Load JS budget gate

- [ ] New script `scripts/dev_tools/check_js_budgets.py`: runs
      `next build` for `apps/web` (or accepts already-captured output),
      parses the route table for each route's First Load JS, fails
      (exit 1) listing every route over a fixed ceiling.
- [ ] Ceiling = current worst measured route, rounded, +10% margin, per
      the plan's literal instruction ("текущее +10% как потолок,
      снижать волнами").
- [ ] Register in `utils/dev_tools_scripts_runner/config/scripts.json`
      for discoverability (`--doctor`/listing), but note it is **not**
      wired into any local `full_check.py` profile (see pre-flight) —
      it's CI + on-demand only.
- [ ] New step in `.github/workflows/quality.yml`'s `frontend` job, right
      after `Build`.
- [ ] Verify: script correctly fails on an artificially lowered ceiling,
      passes on the real one.

## 5.4 — Accessibility hardening

- [ ] `HorizontalPager`'s dot/arrow navigation: proper focus management
      (confirm whether existing dot buttons need roving tabindex, or
      whether disabled/enabled arrow buttons already give adequate
      keyboard reachability — read the component before assuming a gap).
- [ ] `DecisionResults` recompute: `aria-live="polite"` region announcing
      when results update after a weight/persona change.
- [ ] Keyboard-only walkthrough of the wizard (Tab/Enter/Arrow) via a
      live browser check, not assumed from reading code alone.
- [ ] Verify: no regression in existing a11y-relevant e2e assertions;
      manual keyboard walkthrough recorded in the final report.

## 5.5 — i18n content-strategy decision

- [ ] Add a new accepted-decision entry (Р-12) to
      `docs/_arch_/08_Открытые_вопросы.md`: ru-only feature/page-content
      labels are the accepted pattern; `next-intl` stays scoped to app
      chrome; full string migration is an explicit "not now", revisitable
      if the owner asks for true EN-locale parity later.

## Tech debt cleanup

- [ ] `.claude/launch.json`: add `"env": {"APP_ENV": "local"}` to the
      `web-prod` entry, matching the `api` entry's existing pattern, so a
      manually-started preview server behaves like Playwright's own
      managed one (root cause of the `/internal/*` 404s hit during Stage
      3's final verification).
- [ ] Remove dead `apps/web/src/shared/api/watchlists.ts` after confirming
      zero remaining references (grep first, don't assume).

## Final verification

- [ ] Full typecheck/lint (`ui`+`web`), `pnpm format:check`.
- [ ] `next build` clean, JS-budget script passes against the real
      ceiling.
- [ ] New Vitest component tests green; existing Vitest suite unaffected.
- [ ] Storybook builds clean, new play-tests pass.
- [ ] Full Playwright e2e suite green (or isolated-passing flakes only,
      confirmed by re-running the specific spec alone) — a fresh
      `next start` server, not a reused one with stale env, per the
      Stage 3 lesson.
- [ ] Visual regression suite green (only if any covered page's markup
      changed — check before re-shooting).
- [ ] Contrast + i18n-parity audits still green.
- [ ] Browser walkthrough of anything visually touched (pager focus
      changes, aria-live region).

## Completion

- [ ] Fill this checklist (`+`/`-`).
- [ ] Incremental commits on this branch only, one per sub-item group,
      no merge to `main`.
- [ ] Push `feat/frontend-redesign-stage-5-consolidation` to `origin`
      (not `main`).
- [ ] Final report.
