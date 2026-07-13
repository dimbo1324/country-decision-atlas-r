# Task: Frontend Stage 8 (knowledge & transparency)

Source plan: `docs/_arch_/FRONTEND_IMPLEMENTATION_PLAN.md`, §7 Этап 8.
Branch: `feat/frontend-stage8-knowledge-transparency` (fresh off `main` —
Stage 7 merged, `f06eab1`).

Owner instruction: implement Stage 8 (legal signals, sources, methodology,
glossary) in a separate branch; push to `origin/main` once done and tests
pass.

## Preparation

- [ ] Research pass done (Explore agent + direct reads): confirmed all four
      MVP surfaces exist and are pre-reskin (raw `useEffect`+fetch or plain
      RSC `await`, legacy CSS-module classes, no design-system primitives
      except badges). No dedicated glossary page/feature exists yet — new
      build, not a reskin. `LegalSignalTimeline` SVG chart already exists in
      `packages/ui` (Stage 4) but has zero consumers. `@tanstack/react-virtual`
      confirmed as a genuinely new dependency.
- [ ] Contract shapes confirmed: `LegalSignalDetailListResponse`,
      `LegalSignalTimelineResponse`/`LegalSignalTimelineEvent`,
      `SourceListResponse`, `EvidenceItemListResponse`/`EvidenceListResponse`,
      `MethodologyListResponse`/`MethodologySection`,
      `MethodologyParametersResponse`/`MethodologyParameter` (no existing FE
      consumer), `GlossaryListResponse`/`GlossaryTerm`.
- [ ] Existing Playwright coverage inventoried across 5 spec files
      (`web-mvp-legal-signals-timeline`, `web-mvp-argentina-legal-timeline`,
      `web-mvp-analytical-pages`, `web-mvp-trust-transparency`,
      `web-mvp-pages`) — selectors/testids/heading text catalogued so the
      reskin preserves or deliberately migrates each one.

## Design decisions

- [ ] `/legal-signals` keeps its current role as the filterable feed
      (heading "Лента правовых сигналов" preserved, year-grouped via the
      `timeline` endpoint) — migrated onto TanStack Query + nuqs + design
      system, NOT restructured into a separate flat/grouped split. A new
      `/legal-signals/timeline` route is ADDED for the dedicated
      `LegalSignalTimeline` SVG chart view (plan's "таймлайн-режим"),
      sharing filters via nuqs. Rationale: minimizes restructuring of a
      route ~15 existing e2e assertions depend on; the plan's wording
      ("реестр + таймлайн-режим (legal-signals/timeline)") is satisfied by
      treating the existing grouped feed as the registry and adding the
      chart as the distinct new mode, rather than rebuilding the feed as a
      flat table.
- [ ] Country/type/impact/year filter `<select>`s stay native HTML
      `<select>` elements (styled with design tokens), not Radix `Select`.
      Rationale: same precedent as Stage 7's Slider reversion — ~6 existing
      e2e assertions use `#timeline-country`/`#src-country` id lookups and
      `.toHaveValue(...)`, which native selects support and Radix's
      non-native listbox does not.
- [ ] Sources page evidence detail moves from inline per-card expand to a
      `Drawer` (design-system pattern used everywhere since Stage 6) — no
      existing e2e asserts the old inline-expand behavior/testid, so this
      is a safe upgrade, not a deviation requiring a testid migration.
- [ ] Legal signal detail (evidence + affected countries) also uses `Drawer`
      per the plan's explicit wording for this domain.
- [ ] `@tanstack/react-virtual` added to `packages/ui` (new `VirtualList`
      primitive) and used by the sources registry list. Applied with a
      generous overscan and un-capped natural height (no internal
      scroll-clipping) so the small synthetic-data item counts this repo
      ships with always render in full — virtualization exists and is
      real for scale, but is verified not to hide any row that existing or
      new e2e depends on.
- [ ] Glossary gets its own full page (`/glossary`, new) per the plan,
      but the existing `data-testid="glossary-section"` teaser stays on
      `/methodology` (e2e locks its visibility there) as a compact
      cross-link into the full page, not a duplicate full listing.
- [ ] `GlossaryTerm` popover component: new `GlossaryProvider` (client,
      per-locale fetch of the full glossary list — no pagination in the
      contract, so one fetch covers it) mounted in `[locale]/layout.tsx`;
      `GlossaryTerm` consumes it by slug and degrades to plain text if the
      slug isn't found. Wired into methodology's related-terms list and
      into the country dossier's CII section label (minimum 2 surfaces per
      the plan's acceptance criterion).
- [ ] `routes.ts` gains `methodology`, `methodologyParameters`, `glossary`,
      `legalSignalsTimeline` entries (previously missing).

## Implementation

- [ ] `entities/legal-signals/api.ts`, `entities/sources/api.ts`,
      `entities/methodology/api.ts`, `entities/glossary/api.ts` —
      `queryOptions` factories wrapping the existing typed `shared/api/*`
      modules (Pattern B, matching `entities/decision/api.ts`).
- [ ] `shared/api/methodology.ts` gains `listMethodologyParameters` (new
      frontend consumer for an endpoint that had zero callers).
- [ ] Reskin `features/legal-signals-timeline/*` onto Card/Badge/nuqs/Query;
      add `features/legal-signals-chart/` for the new `/legal-signals/timeline`
      SVG-chart route; evidence Drawer.
- [ ] Reskin `features/sources/*` onto Card/Badge/nuqs/Query + VirtualList +
      Drawer.
- [ ] Reskin `/methodology` page onto `Accordion` + Playfair/Crimson/IM Fell
      typography; add `/methodology/parameters` (DataTable).
- [ ] New `/glossary` page + `features/glossary/*`.
- [ ] `GlossaryProvider` + `GlossaryTerm` component; wire into methodology
      and country dossier CII section.
- [ ] Update `routes.ts` and `tests/e2e/helpers/routes.ts`.
- [ ] Update the 5 affected Playwright spec files for new testids/selectors
      while preserving all existing text/heading assertions; add a new
      spec file for `/glossary` and `/methodology/parameters` smoke coverage.

## Verification

- [ ] `pnpm --filter web typecheck` / `lint` — clean.
- [ ] `pnpm --filter ui typecheck` / `lint` — clean.
- [ ] `pnpm build` — compiles clean.
- [ ] `npx playwright test` — affected specs green, no regressions.
- [ ] `python dev_tools_scripts_runner.py` (full gate) or documented
      pre-existing exceptions only.

## Completion

- [ ] Commits: logical slices (entities/data layer, legal-signals reskin,
      sources reskin, methodology + parameters, glossary + popover, e2e
      parity fixes).
- [ ] Merge to `main` (fast-forward), push to `origin/main`.
- [ ] Final report.
