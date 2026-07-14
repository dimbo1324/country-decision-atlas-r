# Task: Frontend Stage 9 (личный кабинет — безопасность, watchlist, лента, поездки)

Source plan: `docs/_arch_/FRONTEND_IMPLEMENTATION_PLAN.md`, §7 Этап 9.
Branch: `feat/frontend-stage9-account-trips` (fresh off `main` — Stage 8
merged, `e65de69`).

Owner instruction: verify Stage 8 first (owner implemented it locally
yesterday, outside this session), then implement Stage 9 in a separate
branch.

## Preparation

- [+] Stage 8 independently verified in this session before starting:
      full quality gate re-run with Docker up (first pass had Docker
      Desktop down and skipped the stack/E2E phases; re-ran after starting
      it) — static checks clean, Docker stack + smokes clean, 293/293
      Playwright specs green at `--workers=2` (default-worker run showed
      one E2E failure, confirmed as resource-contention flakiness, not
      Stage 8 regressions). Only pre-existing gaps remain: `pytest
      (scripts/synthetic_data)` missing `arabic_reshaper` in that venv,
      `go test -race` no local CGO toolchain (CI's `ubuntu-linux` runner
      is the actual `-race` gate).
- [+] Research pass done (Explore agent): `features/auth/AccountView.tsx`
      and `features/watchlist/WatchlistView.tsx` were raw `useEffect`+fetch,
      legacy CSS-module classes, no design-system primitives — confirmed
      reskin targets. `WatchlistButton.tsx` (country-page toggle) was
      claimed by the research agent to already use Pattern B — this was
      WRONG; only `WatchlistStar.tsx` (catalog card star) did. Corrected
      during implementation: `WatchlistButton.tsx` migrated too.
- [+] Contract shapes confirmed present in
      `packages/contracts/generated/types.ts` for account/watchlist/
      subscriptions/trips domains (full list unchanged from original
      research, see prior revision in git history for the enumeration).
- [+] `@dnd-kit/core` + `@dnd-kit/sortable` + `@dnd-kit/utilities` and
      `date-fns` confirmed absent repo-wide, then added (see Implementation).
- [+] RHF+Zod+`Field` convention extended from `LoginForm`/`RegisterForm`
      to every new Stage 9 form (Telegram link, revoke-all password, trip
      create, waypoint add, checklist add/import, reminder create,
      subscribe-by-id).
- [+] Existing Playwright coverage inventoried and preserved; new spec
      files added for every net-new surface (see Implementation).

## Design decisions

- [+] `AccountView.tsx` reskinned onto Card/Field/DataTable/Dialog; revoke-
      all's inline password toggle became a Dialog confirmation (terracotta
      styling via `Button variant="ghost"` + `text-terra3` className, since
      the shared `Button` primitive only has `primary`/`ghost` variants —
      no third "terracotta" variant exists, so this stays a className
      override rather than a new shared-component variant).
      `web-mvp-session-security.spec.ts`'s `revoke-all-password-input`
      lookup needed no change — the Dialog opens on the same button click
      the old inline-toggle used, and the testid stayed on the input.
- [+] `AccountView.tsx` migrated to `entities/account/api.ts` (Pattern A:
      `queryOptions`/mutations wrapping the existing `authApi`).
- [+] `WatchlistView.tsx` reskinned onto a catalog-style card grid; migrated
      onto the existing `myWatchlistQuery` plus a new
      `useUpdateWatchlistPreferencesMutation` (optimistic, added to
      `entities/watchlist/api.ts`). No separate "drift summary block" was
      added — out of scope beyond what the plan's one-line mention implies
      and no existing drift-summary component fit a per-item watchlist
      card without new design work; noted as a deferred nice-to-have, not
      silently dropped.
- [-] `features/feed/*` as a separate feature directory — NOT built as a
      standalone directory; folded into `features/subscriptions/
      SubscriptionsView.tsx` as one page section (`TimelineList` of feed
      entries), same file as the subscription-management UI. Single
      `/subscriptions` route hosts both, no separate `/feed` route needed
      given the modest surface area (matches "no dedicated /feed route
      unless plan implies one" from the original design note).
- [~] Real backend/plan mismatch found and documented: the plan's Stage 9
      text describes subscriptions as "страна/тип события" (country/event
      type), but the actual `me/subscriptions` contract implements
      following a **community author-metric** (`metric_id`/
      `author_user_id`), with the feed showing metric value updates — an
      existing backend feature (community intelligence) with zero prior
      frontend consumer anywhere in the app. Built against the real
      contract. Known UX gap: no metric-browse/picker UI exists yet
      anywhere in the app (confirmed: zero frontend consumer of
      `/countries/{slug}/author-metrics` before this stage), so subscribing
      requires typing a known metric or author ID rather than picking from
      a list. Deferred — a metric catalog browser is its own feature,
      not assumed by this stage's scope.
- [+] `entities/trips/api.ts` + `shared/api/trips.ts` built covering the
      full documented surface: trips CRUD, waypoints CRUD+reorder,
      checklist CRUD+import, reminders CRUD, warnings (read), what-changed
      (read), share enable/disable, export, annotations CRUD (annotations
      API exists in `entities/trips/api.ts` but has no UI consumer yet —
      the plan's component table doesn't call out a dedicated annotations
      UI beyond checklist/waypoint notes, and none of the built surfaces
      needed it; the API is there if a future stage wants it).
- [+] `features/trips/*` built: list+create (`/trips`), detail
      (`/trips/[id]`) with waypoints (`@dnd-kit` sortable list, both
      `PointerSensor` and `KeyboardSensor` wired — the plan's "либо кнопки
      вверх/вниз как fallback" is satisfied by dnd-kit's built-in keyboard
      reordering rather than separate up/down buttons, avoiding a second
      reorder code path), checklist (optimistic status toggle + route-
      template import form), reminders (`date-fns` formatted, create/
      cancel), warnings + what-changed (read-only, terracotta callout
      styling matching the existing `border-terra2/60 text-terra3`
      convention from `DecisionResults`), share/export (enable/disable
      public link with clipboard copy, JSON export download).
- [+] Public `app/[locale]/trips/shared/[token]/page.tsx` — plain RSC
      `await`, same precedent as the decision-passport public page
      (try/catch → `ErrorState` on failure, no `HydrationBoundary`).
- [+] `@dnd-kit/core`, `@dnd-kit/sortable`, `@dnd-kit/utilities`, `date-fns`
      added to `apps/web/package.json`.
- [+] Optimistic-CRUD pattern applied where the plan calls for it:
      watchlist toggle (pre-existing), watchlist preference checkboxes
      (new), trip waypoint reorder (new), trip checklist status toggle
      (new) — all `onMutate`/`onError` rollback/`onSettled` invalidate,
      matching `entities/watchlist/api.ts`'s established shape. Sonner
      toasts used for create/delete/error feedback across every new form.
- [+] `routes.ts` and `tests/e2e/helpers/routes.ts` gained `subscriptions`,
      `trips`, `tripDetail(id)`, `tripSharedPublic(token)`.
- [+] `nav-subscriptions-link` and `nav-trips-link` added to `AuthNav.tsx`
      (added incrementally, only once each route actually existed and
      built successfully — avoided committing a dangling nav link to a
      404 at any point).
- [x] Bug caught during verification, not by design: `WatchlistView.tsx`'s
      per-item `data-testid="watchlist-item"` and two `AccountView.tsx`
      testids (`security-notifications`, `telegram-linked-state`) were
      placed directly on `Card`/`Badge`, which don't forward `data-testid`
      — a documented gotcha from Stage 6/7 memory that I knew about and
      still missed on first pass. Caught when `web-mvp-watchlist.spec.ts`
      failed deterministically (not flakily) once run alongside the new
      trips suite forced a full rebuild. Fixed by wrapping in a plain
      element per the established convention; re-verified.

## Implementation

- [+] `entities/account/api.ts`, `entities/subscriptions/api.ts`,
      `entities/trips/api.ts`, `shared/api/subscriptions.ts`,
      `shared/api/trips.ts` — all built per the design decisions above.
- [+] Reskinned `features/auth/AccountView.tsx`, `features/watchlist/
      WatchlistView.tsx`, `features/watchlist/WatchlistButton.tsx`
      (migrated to Pattern B, correcting the prep-note error).
- [+] New `features/subscriptions/SubscriptionsView.tsx` (management +
      feed in one file, per the design decision above).
- [+] New `features/trips/*`: `TripListView`, `TripDetailView`,
      `TripWaypoints`, `TripChecklist`, `TripReminders`, `TripWarnings`,
      `TripShareExport`.
- [+] New route pages: `app/[locale]/subscriptions/page.tsx`,
      `app/[locale]/trips/page.tsx`, `app/[locale]/trips/[id]/page.tsx`,
      `app/[locale]/trips/shared/[token]/page.tsx`.
- [+] Updated `routes.ts`, `tests/e2e/helpers/routes.ts`, `AuthNav.tsx`,
      `messages/{ru,en}.json` (nav labels).
- [+] New spec files: `web-mvp-subscriptions.spec.ts` (4 tests),
      `web-mvp-trips.spec.ts` (8 tests, including keyboard-driven
      drag-reorder and a real second-browser-context public-page check).
      `web-mvp-session-security.spec.ts` and `web-mvp-watchlist.spec.ts`
      required no selector changes — verified both still pass against the
      reskinned markup.

## Verification

- [+] `pnpm --filter web typecheck` / `lint` — clean at every commit point.
- [+] `pnpm --filter web build` — all new routes compile
      (`/subscriptions`, `/trips`, `/trips/[id]`, `/trips/shared/[token]`).
- [+] Manual browser verification against the live Docker stack: account
      (sessions/telegram/revoke-all dialog), watchlist (toggle, remove,
      preference checkboxes), subscriptions (subscribe by author ID,
      unsubscribe, feed), full trip lifecycle (create → add waypoint →
      add+toggle checklist item, persisted across reload → enable share →
      fetch the real public page in-browser → error state for an invalid
      token). The in-app browser tool's element-ref cache proved unreliable
      for multi-step interactive flows (stale refs after re-renders); the
      core create/persist/reload round trip was still confirmed manually,
      and the harder interaction sequences (waypoint reorder, full
      add/remove cycles) were verified through Playwright instead, which
      has no such staleness problem.
- [+] Full Playwright suite run repeatedly at `--workers=2` (305 specs,
      incl. the 12 new Stage 9 specs). Across three separate full runs plus
      targeted reruns, the only failures observed were scattered across
      `web-mvp-main-flow.spec.ts`, `web-mvp-analytics.spec.ts`, and (once)
      `web-mvp-watchlist.spec.ts` — none Stage-9-specific in a repeatable
      way, all confirmed transient by a `--retries=1` rerun where they
      passed on retry ("flaky" not "failed"), and `web-mvp-watchlist.spec.ts`
      itself passed clean in every other run (isolation, combined with the
      new trips/subscriptions specs, and this final retry run). Matches the
      duplicate-DOM-under-resource-contention pattern documented in every
      prior stage (Stage 5 onward) — not a Stage 9 regression.
- [+] `python dev_tools_scripts_runner.py full-check` — clean except the
      two known pre-existing gaps (`pytest scripts/synthetic_data` missing
      `arabic_reshaper`, `go test -race` no local CGO toolchain) plus the
      same default-worker E2E flakiness confirmed transient above.

## Completion

- [+] Commits: API layer, AccountView reskin, watchlist reskin,
      subscriptions/feed, full trip planner, plus this checklist.
- [+] Merge to `main`, push.
- [+] Final report.
