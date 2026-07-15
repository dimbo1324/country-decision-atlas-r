# Task: Frontend Stage 13 (полировка и выпуск)

Source plan: `docs/_arch_/FRONTEND_IMPLEMENTATION_PLAN.md`, §7 Этап 13.
Branch: `feat/frontend-stage13-polish` (fresh off `main` — Stage 12
merged, `419be35`).

Owner decision: full plan scope, sequenced in parts (same discipline as
Stages 10/12), each its own commit, verified before moving on.

## Preparation

- [+] Research pass done (Explore agent) establishing real scope vs the
      plan text:
      - `apps/web/src/app/styles.css` (2996 lines) still has **one**
        import site (`app/layout.tsx`) but legacy classnames
        (`pageShell`, `pageHeader`, `formGroup`, `notice`,
        `internalLink`, `resultCard`, etc.) are still referenced across
        **24 files** — real, bounded cleanup, not a rounding error.
      - **Vitest is entirely absent** (no config, no dependency anywhere)
        — a from-scratch addition, not a light lift.
      - Storybook 8.4.7 exists in `packages/ui`; **MSW is not installed
        anywhere** — "MSW fixtures for Storybook interaction tests" is
        also greenfield.
      - **No visual regression** exists (`toHaveScreenshot`/
        `toMatchSnapshot` absent from the whole e2e suite).
      - **No bundle analyzer** wired into `next.config.mjs`.
      - **No `ErrorBoundary` component and no `client_error` event
        anywhere**, but `shared/analytics/useAnalyticsEvent.ts` already
        exists — only the boundary + event type are new, not the
        plumbing.
      - Route count is **44** `page.tsx` files (11 `internal/` + 33
        `[locale]/`), not the plan's stale "29+"; e2e suite is **321**
        tests across 44 spec files, not "284" — both DoD figures are
        stale and scale the accessibility/i18n audit surface up
        accordingly.
      - No next-intl lint rule or ru/en key-parity script exists —
        another from-scratch build.
- [+] Owner confirmed: full 7-stream scope, sequenced, not cut down.

## Scope decision for this stage

Given the size, this stage ships in the following order, each a
self-contained commit, verified before moving on (mirrors Stage 10/12
discipline):
1. Legacy CSS removal — reskin the remaining 24 files off `styles.css`
   classnames onto the design system, then delete the file and its
   import.
2. Frontend observability — `ErrorBoundary` component + `client_error`
   analytics event, wired at the app-shell level.
3. Bundle analyzer + performance pass — wire `@next/bundle-analyzer`,
   audit the report, lazy-load heavy chart/feature chunks, confirm
   `next/image` usage for emblem images, review RSC cache policies.
4. Accessibility pass — keyboard-navigation audit, contrast audit of
   `--c3`/`--bg2` and related pairs, ARIA text summaries for charts,
   reduced-motion audit across screens (many charts already respect
   `useReducedMotion`; this is a completeness sweep, not a from-scratch
   build).
5. i18n completeness — ru/en parity script (fails CI-style on orphan
   keys) + a pass fixing any drift found.
6. Vitest setup — config, first real coverage of utilities and data
   hooks (not aiming for exhaustive coverage in one pass; establishing
   the harness + meaningful initial coverage).
7. MSW + Storybook interaction tests — MSW install + a handful of
   interaction stories as the pattern, not full component coverage.
8. Visual regression — Playwright screenshot tests for the plan's
   explicit minimum: home, catalog, dossier, decision result, passport.
9. Final full-suite Playwright run + Stage-0 checklist final pass
   (confirm every route "migrated").

If effort runs out before all nine land, each is independently
committable and this checklist will say honestly which shipped and
which didn't — no stream gets silently dropped without a note, matching
every prior stage's discipline.

## Design decisions

- [ ] Legacy-CSS reskin follows the exact `Kicker`/`Card`/`Field`/
      `Button` conventions used throughout Stages 9-12; no new
      primitives invented for this cleanup.
- [ ] `ErrorBoundary` wraps at the `app/[locale]/layout.tsx` and
      `app/internal/layout.tsx` boundaries (both root shells), reports
      via the existing `trackEvent`/analytics client with
      `type: "client_error"`, degrades to a plain retry UI — no crash
      loop risk from the boundary itself.
- [ ] Bundle-analyzer output only run locally (`ANALYZE=true next build`)
      — not wired into CI, since the plan doesn't ask for a CI budget
      gate, only a manual audit this stage.
- [ ] i18n parity script lives in `scripts/dev_tools/` (matching the
      project's existing dev-tooling location) and is registered as a
      `--profile quick`-eligible check if lightweight enough; otherwise
      documented as a manual command.
- [ ] Vitest scope: `shared/lib/*` utilities and `entities/*/api.ts`
      hooks with clear pure-function surface first — not an attempt at
      full coverage of every component in one stage.

## Implementation

(Filled in per stream as each lands.)

## Verification

- [ ] `pnpm --filter web typecheck` / `lint` after every stream.
- [ ] `pnpm --filter web build` clean after CSS removal and bundle work.
- [ ] Full Playwright regression at `--workers=2` after every stream
      that touches shared shells (CSS removal, error boundary).
- [ ] `python dev_tools_scripts_runner.py --profile quick` before final
      commit of each stream.
- [ ] Manual accessibility/contrast/reduced-motion checks documented
      with findings, not just "looked fine."

## Completion

- [ ] Commit(s)
- [ ] Merge to `main`, push — only once explicitly confirmed complete.
- [ ] Final report — honest per-stream status against the DoD.
