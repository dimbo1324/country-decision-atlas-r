# Task: Frontend redesign — Этап 0 (E2E stabilization)

Owner-provided plan (verbatim, pasted in chat): a 6-stage frontend UX rework
(§0 stabilization, §1 "Навигация и обзор", §2 "Сценарий решения", §3
"Реестры и кабинет", §4 data-layer migration interleaved, §5 hardening).
This task covers **Этап 0 only**; Этап 1 is a separate branch/task after
this merges (Этап 0 is an explicit prerequisite per the plan's own
reasoning: redesign waves will rewrite selectors across the suite, and you
can't tell "broke it" from "it's just flaky" without a stable baseline).

Branch: `fix/e2e-stabilization-v1`, fresh off `main`.

## Session-gap re-orientation (before any code)

- [+] Git history showed Stages 5-13 of `FRONTEND_IMPLEMENTATION_PLAN.md`
      already shipped in sessions with no visibility into this
      conversation — confirmed via `git log`, not assumed. `task-checklist.md`
      was already empty (cleared after Stage 13), confirming a clean
      between-tasks state.
- [+] Verified the owner's plan's factual premises against actual current
      code (`apps/web`, `packages/ui`) via a dedicated exploration pass
      before writing anything — several premises were outdated:
      - Dossier page (`countries/[slug]/page.tsx`) already has a working
        `DossierRail` scrollspy nav across 17 sections (not "13 sections, no
        nav" as the plan assumed) — Этап 1.1 groups those into tabs, it
        doesn't build nav from scratch.
      - `<Feature flag="...">` JSX gate exists but has zero real call
        sites; the one actual precedent (`CountryDataJournalBlock.tsx`)
        calls `useFeatureEnabled(...)` directly — that's the proven
        pattern to copy for the dossier flag gate, not `<Feature>`.
      - Flag table is `feature_flags`, not `platform_features`; next free
        migration number is `056` (matches the plan's own number).
      - 10 spec files duplicate `registerViaUi`, not the 4 named as
        examples: `web-mvp-auth-rbac`, `web-mvp-author-metrics`,
        `web-mvp-community-intelligence`, `web-mvp-country-proposals`,
        `web-mvp-internal-admin`, `web-mvp-migration-board`,
        `web-mvp-session-security`, `web-mvp-subscriptions`,
        `web-mvp-trips`, `web-mvp-watchlist`.
      - Auth is cookie-based (`POST /api/v1/auth/register` itself sets
        session cookies, no separate login call needed) — relevant to how
        API-seeding captures the session.
      - Leftover a11y findings from an earlier (interrupted) audit pass
        (Counter.tsx missing reduced-motion check, RadioCards.tsx Tailwind
        class broken by runtime string concat, Card.tsx keyboard-inert
        click handler, 5 Radix components missing focus-visible) are real
        and still open, but out of scope for *this* task — flagged as a
        separate background-task suggestion instead of pulled in here.

## Design decision: API-seeding helper is per-test, not worker-scoped

- [+] The plan asks for "one logged-in user per worker, tests reuse the
      session" (worker-scoped `storageState`). Deviated to a **per-test**
      fixture instead, reasoned explicitly rather than silently:
      - The actual cost being eliminated is ~5-8s of UI form-filling per
        test, not "creating a user" — a direct `POST /api/v1/auth/register`
        call is ~50-200ms, already negligible next to that. Sharing a user
        across a worker's whole test run buys almost nothing further.
      - Most of the converted specs (trips, watchlist, subscriptions,
        checklist/reminder counts) assert exact state counts
        (`toHaveCount(1)`, empty-state visibility, ...) that would become
        order-dependent and flaky if tests in the same worker silently
        shared one mutable account.
      - A per-test fixture still gets the full speed win with zero new
        cross-test pollution risk — Playwright already gives each test its
        own fresh `context`/`page` by default, so "per test" already *is*
        the natural safe scope; `context.request` shares that same
        context's cookie jar, so seeding through it and then using `page`
        in the same test carries the session correctly with no extra
        wiring.
- [+] `web-mvp-session-security.spec.ts` **not touched at all** — it
      directly asserts on cookie attributes (`httpOnly`, JS-visibility,
      CSRF double-submit) that are properties of the real register/login
      response; UI-fidelity has genuine (if small) value for a
      security-behavior suite, and the file is small (5 tests) — low
      reward for touching it. Left 100% UI-driven.
- [+] `web-mvp-auth-rbac.spec.ts` gets **mixed treatment**, not a blanket
      conversion: tests that assert on the register/login *form's own*
      behavior (account created via the form, duplicate-email error,
      wrong-password error) stay UI-driven since the form *is* the subject
      under test; tests that only use registration as unrelated setup (nav
      state after login, regular-role RBAC check) convert to API-seeding.

## Implementation

- [+] `tests/e2e/helpers/auth.ts`: `uniqueEmail(prefix)` (moved out of each
      spec file's local copy where the spec is otherwise being touched
      anyway) + `createUserViaApi(request, overrides?)` — POSTs
      `/api/v1/auth/register` directly, throws with response body on
      non-2xx for a debuggable failure instead of a silent bad session.
- [+] `tests/e2e/helpers/fixtures.ts`: custom `test`/`expect` export
      extending base Playwright test with a `seededUser` fixture
      (test-scoped) that calls `createUserViaApi(context.request)`.
- [+] Converted pure-setup `registerViaUi` call sites to `seededUser` +
      direct `page.goto(...)` (skipping `/register` entirely) in:
      `web-mvp-trips.spec.ts`, `web-mvp-watchlist.spec.ts`,
      `web-mvp-subscriptions.spec.ts`, `web-mvp-author-metrics.spec.ts`,
      `web-mvp-community-intelligence.spec.ts`,
      `web-mvp-country-proposals.spec.ts`, `web-mvp-internal-admin.spec.ts`,
      `web-mvp-migration-board.spec.ts`, plus the two pure-setup tests in
      `web-mvp-auth-rbac.spec.ts`.
- [+] `web-mvp-internal-admin.spec.ts` / role-elevation: where a spec needs
      an elevated role (admin/moderator), kept whatever the existing
      role-elevation mechanism was (direct DB/script bootstrap or an
      already-privileged seeded account) — only the *base* registration
      step moved to the API, not the role-elevation step itself.
- [+] `playwright.config.ts`: `timeout` 30s → 45s (covers slower page.goto
      under concurrent load); `expect.timeout` left at 10s per the plan
      (keeps genuine hangs catchable, only the overall test budget grows);
      `retries: 1` — Playwright's own reporter already classifies a
      fail-then-pass-on-retry test as "flaky" (distinct from a clean pass)
      in its terminal summary and HTML report, which is the "flake is a
      visible metric, not a swallowed signal" outcome the plan wants — no
      extra custom tooling needed for that.

## Verification

- [+] `packages/ui`/`apps/web` unaffected by this task — confirm `pnpm
      quality` still green (regression check only).
- [+] Full Playwright suite green.
- [+] Historically-flaky specs from the owner's own full-check
      (`web-mvp-argentina-core-country`, `web-mvp-community-intelligence`,
      `web-mvp-trips`) re-run in isolation to confirm they were load-related
      flakes, not latent bugs the conversion happened to also fix/hide.
- [+] Full suite run a second and third time back-to-back to confirm the
      Definition of Done ("three consecutive green runs").

## Completion

- [+] Fill this checklist (`+`/`-`).
- [+] Final report: what shipped, the worker-scoped-vs-per-test deviation
      restated plainly, what's deferred to Этап 1.
