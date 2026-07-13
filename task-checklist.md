# Task: Frontend Stage 8 (knowledge & transparency)

Source plan: `docs/_arch_/FRONTEND_IMPLEMENTATION_PLAN.md`, §7 Этап 8.
Branch: `feat/frontend-stage8-knowledge-transparency` (fresh off `main` —
Stage 7 merged, `f06eab1`).

Owner instruction: implement Stage 8 (legal signals, sources, methodology,
glossary) in a separate branch; push to `origin/main` once done and tests
pass.

## Preparation

- [+] Research pass done (Explore agent + direct reads): confirmed all four
      MVP surfaces exist and are pre-reskin (raw `useEffect`+fetch or plain
      RSC `await`, legacy CSS-module classes, no design-system primitives
      except badges). No dedicated glossary page/feature exists yet — new
      build, not a reskin. `LegalSignalTimeline` SVG chart already exists in
      `packages/ui` (Stage 4) but has zero consumers. `@tanstack/react-virtual`
      confirmed as a genuinely new dependency.
- [+] Contract shapes confirmed: `LegalSignalDetailListResponse`,
      `LegalSignalTimelineResponse`/`LegalSignalTimelineEvent`,
      `SourceListResponse`, `EvidenceItemListResponse`/`EvidenceListResponse`,
      `MethodologyListResponse`/`MethodologySection`,
      `MethodologyParametersResponse`/`MethodologyParameter` (no existing FE
      consumer), `GlossaryListResponse`/`GlossaryTerm`.
- [+] Existing Playwright coverage inventoried across 5 spec files
      (`web-mvp-legal-signals-timeline`, `web-mvp-argentina-legal-timeline`,
      `web-mvp-analytical-pages`, `web-mvp-trust-transparency`,
      `web-mvp-pages`) — selectors/testids/heading text catalogued so the
      reskin preserves or deliberately migrates each one.

## Design decisions

- [+] `/legal-signals` keeps its current role as the filterable feed
      (heading "Лента правовых сигналов" preserved, year-grouped via the
      `timeline` endpoint) — migrated onto TanStack Query + nuqs + design
      system, NOT restructured into a separate flat/grouped split. A new
      `/legal-signals/timeline` route is ADDED for the dedicated
      `LegalSignalTimeline` SVG chart view (plan's "таймлайн-режим"),
      sharing filters via nuqs.
- [+] Country/type/impact/year filter `<select>`s stay native HTML
      `<select>` elements (styled with design tokens), not Radix `Select`.
      Same precedent as Stage 7's Slider reversion — existing e2e assertions
      use `#timeline-country`/`#src-country` id lookups and
      `.toHaveValue(...)`, which native selects support and Radix's
      non-native listbox does not.
- [+] Sources page evidence detail moves from inline per-card expand to a
      `Drawer` — no existing e2e asserted the old inline-expand
      testid/behavior, so this was a safe upgrade.
- [+] Legal signal detail (evidence + affected countries) also uses `Drawer`.
- [+] `@tanstack/react-virtual` added to `packages/ui` (new `VirtualList`
      primitive) and used by the sources registry list. Verified in the
      browser that all 20 demo source rows render (no hidden rows).
- [+] Glossary gets its own full page (`/glossary`, new) per the plan; the
      existing `data-testid="glossary-section"` teaser stays on
      `/methodology` (e2e locks its visibility there) as a compact
      cross-link into the full page, not a duplicate full listing.
- [~] `GlossaryTerm` popover component: `GlossaryProvider` (client,
      per-locale fetch of the full glossary list) mounted in
      `[locale]/layout.tsx`; `GlossaryTerm` consumes it by slug and degrades
      to plain text if the slug isn't found. Ended up wired into **three**
      surfaces, not the two originally planned: the methodology page's
      compact term-chip teaser, the full `/glossary` page's related-terms
      cross-links, and the country dossier's CII block (glossary slug
      `cii` — corrected from the originally-guessed `what_is_cii`, which is
      actually a *methodology section* slug, a different namespace).
- [+] `routes.ts` gains `methodology`, `methodologyParameters`, `glossary`,
      `legalSignalsTimeline` entries (previously missing).

## Implementation

- [+] `entities/legal-signals/api.ts`, `entities/sources/api.ts`,
      `entities/methodology/api.ts`, `entities/glossary/api.ts` —
      `queryOptions` factories wrapping the existing typed `shared/api/*`
      modules (Pattern B, matching `entities/decision/api.ts`).
- [+] `shared/api/methodology.ts` gains `listMethodologyParameters` (new
      frontend consumer for an endpoint that had zero callers).
- [+] Reskin `features/legal-signals-timeline/*` onto Card/Badge/nuqs/Query;
      added `features/legal-signals-chart/` for the new `/legal-signals/timeline`
      SVG-chart route; evidence Drawer.
- [+] Reskin `features/sources/*` onto Card/Badge/nuqs/Query + VirtualList +
      Drawer.
- [+] Reskin `/methodology` page onto `Accordion` + Playfair/Crimson/IM Fell
      typography; added `/methodology/parameters` (DataTable, 24 rows).
- [+] New `/glossary` page + `features/glossary/*` (19 terms, alphabetical
      grouping, q/category nuqs filters).
- [+] `GlossaryProvider` + `GlossaryTerm` component; wired into methodology,
      the full glossary page, and the country dossier CII section.
- [+] Updated `routes.ts` and `tests/e2e/helpers/routes.ts`.
- [+] Updated the affected Playwright spec files for new testids/selectors
      while preserving all existing text/heading assertions; added
      `web-mvp-knowledge-transparency.spec.ts` for `/glossary`,
      `/methodology/parameters`, `/legal-signals/timeline`, and the term
      popover.
- [+] Unplanned fix found during manual verification (not by any failing
      test — Next.js was silently swallowing it on background prefetch
      requests): `packages/ui`'s shared `Drawer` primitive called
      `createPortal(..., document.body)` unconditionally on every render,
      including the server-rendered pass client components still get for
      initial HTML, where `document` doesn't exist. No page rendered
      `Drawer` before Stage 8's two new evidence drawers, so this never
      surfaced previously. Fixed with an SSR guard (`typeof document ===
      "undefined"` → render nothing); this is a `packages/ui` primitive fix,
      not scope creep, since my own new code was the first real consumer to
      trigger it.

## Verification

- [+] `pnpm --filter web typecheck` / `lint` — clean.
- [+] `pnpm --filter ui typecheck` / `lint` — clean.
- [+] `pnpm build` — compiles clean, all new routes present.
- [+] Manual browser verification of every new/changed surface
      (`/legal-signals`, `/legal-signals/timeline`, `/sources`,
      `/methodology`, `/methodology/parameters`, `/glossary`, country
      dossier CII block, evidence Drawer open/close, glossary popover) —
      no console errors, correct data counts (26 legal-signal events, 20
      sources, 12 methodology sections, 19 glossary terms).
- [+] Targeted Playwright run (78 tests across the 6 touched/new spec
      files) — 78/78 passed.
- [+] Full Playwright suite, clean Docker/DB environment (via
      `dev_tools_scripts_runner.py full-check`) — 293/293 passed. (An
      earlier ad-hoc full-suite run against an already-mutated dev database
      showed 5-6 unrelated flaky failures in decision-passport/locale/
      migration-board/route-checklist/session-security/watchlist specs —
      none in Stage 8 domains; confirmed as test-data pollution from
      repeated runs, not a regression, once the clean-environment run came
      back 293/293 green.)
- [+] `python dev_tools_scripts_runner.py full-check` — full gate: 78 OK,
      1 SKIP (proto codegen, intentionally skipped per script design), 1
      FAIL. The FAIL is `go test -race`: `-race requires cgo; enable cgo by
      setting CGO_ENABLED=1` — this Windows machine has no CGO toolchain.
      Confirmed pre-existing and environment-only, not a regression: `go
      test ./...` (no `-race`) passes 100% clean, and zero Go files changed
      in this branch. Identical documented exception as Stage 7's checklist
      (`task-checklist.md` history); the actual `-race` gate is enforced in
      CI's `ubuntu-latest`, per `.ai/project/11-commands.md`.

## Completion

- [+] Commits: 9 logical slices (task checklist, entities + VirtualList,
      glossary provider/component, legal-signals reskin + new timeline
      route, sources reskin, methodology + parameters, glossary page +
      dossier wiring, e2e selector/spec updates, Drawer SSR fix).
- [+] Merge to `main` (fast-forward), push to `origin/main`.
- [+] Final report.
