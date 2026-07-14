# Task: Frontend Stage 9 (личный кабинет — безопасность, watchlist, лента, поездки)

Source plan: `docs/_arch_/FRONTEND_IMPLEMENTATION_PLAN.md`, §7 Этап 9.
Branch: `feat/frontend-stage9-account-trips` (fresh off `main` — Stage 8
merged, `e65de69`).

Owner instruction: verify Stage 8 first (owner implemented it locally
yesterday, outside this session), then implement Stage 9 in a separate
branch.

## Preparation

- [ ] Stage 8 independently verified in this session before starting (see
      the Stage 8 verification note below, not part of Stage 9's own
      checklist items).
- [+] Research pass done (Explore agent): `features/auth/AccountView.tsx`
      and `features/watchlist/WatchlistView.tsx` are raw `useEffect`+fetch,
      legacy CSS-module classes, no design-system primitives — reskin
      targets, not net-new. `WatchlistButton.tsx` already uses Pattern B
      (`entities/watchlist/api.ts`) — mostly reusable as-is.
      Subscriptions/feed and the entire trip planner (trips, waypoints,
      checklist+import, reminders, warnings, share, export, annotations,
      what-changed, public shared-trip page) are net-new frontend surface
      on top of already-complete backend contracts — zero existing
      `shared/api/subscriptions.ts` / `shared/api/feed.ts` /
      `shared/api/trips.ts`.
- [+] Contract shapes confirmed present in
      `packages/contracts/generated/types.ts`: `AuthSession`,
      `SecurityNotification`, `TelegramLinkStatusResponse`,
      `WatchlistItem`/`WatchlistResponse`, `SubscriptionResponse`/
      `SubscriptionListResponse`/`SubscriptionFeedResponse`, `TripSummary`/
      `TripDetail`/`TripDetailResponse`/`TripListResponse`/
      `TripCreateRequest`/`TripCreateFromPassportRequest`, `TripWaypoint`
      (+create/update/reorder requests), `TripChecklistItem` (+create/
      update/import requests — distinct from the pre-existing
      `RouteChecklistItem` used by Migration Board, do not conflate),
      `TripReminder`(+create), `TripWarning`/`TripWhatChangedResponse`,
      `TripAnnotation`(+create/update), `TripShareResponse`/
      `SharedTripResponse`(+waypoints/checklist).
- [+] `@dnd-kit/core` + `@dnd-kit/sortable` confirmed absent repo-wide —
      genuinely new dependency per the plan. `date-fns` also absent;
      needed for reminder-date formatting per the plan.
- [+] RHF+Zod+`Field` convention already established in
      `features/auth/LoginForm.tsx`/`RegisterForm.tsx` — the template to
      extend to Stage 9 forms (Telegram code, revoke-all password, trip
      create/edit, waypoint edit, reminder create). `AccountView.tsx`/
      `WatchlistView.tsx` predate this convention and don't use it yet.
- [+] Existing Playwright coverage inventoried: `web-mvp-session-security.spec.ts`
      (httpOnly cookie checks, revoke-all password-confirm flow, CSRF
      403 check), `web-mvp-watchlist.spec.ts` (unauthenticated/empty states,
      toggle button, notification-preference persistence),
      `web-mvp-auth-rbac.spec.ts` (shares `e2eRoutes.account`/`login`).
      No existing specs for Telegram linking specifically, subscriptions,
      feed, or trips — all net-new test surface.

## Design decisions

- [ ] `AccountView.tsx` reskinned in place onto design-system primitives
      (`Card`/`Field`/`Button`/`Badge`) + `DataTable` for the sessions
      list; revoke-all's current inline password toggle becomes a `Dialog`
      confirmation (plan explicitly calls for Dialog-confirmed terracotta
      destructive actions) — this changes the revoke-all DOM shape, so
      `web-mvp-session-security.spec.ts`'s `revoke-all-password-input`
      lookup needs updating to open the Dialog first; preserve the
      underlying CSRF/password-confirm behavior and testids where the
      element itself doesn't move.
- [ ] Migrate `AccountView.tsx`'s data fetching from raw
      `useEffect`+`Promise.all` to `entities/account/api.ts`
      (`queryOptions` + mutations for sessions/telegram/security
      notifications), matching Pattern B.
- [ ] `WatchlistView.tsx` reskinned onto the country-catalog card grid
      pattern (Stage 5 precedent) + drift summary block; migrated onto
      `entities/watchlist/api.ts`'s existing `myWatchlistQuery` (reuse, no
      new query needed for the list itself).
- [ ] New `entities/subscriptions/api.ts` + `shared/api/subscriptions.ts`
      wrapping `me/subscriptions` CRUD + `me/subscriptions/feed`;
      `features/subscriptions/*` (management UI) and `features/feed/*`
      (`TimelineList` grouped by day, type icons, dossier links) + new
      `/subscriptions` (or folded into `/account`) and no dedicated
      `/feed` route unless the plan's routing implies one — confirm during
      implementation which shell hosts the feed.
- [ ] New `entities/trips/api.ts` + `shared/api/trips.ts` covering the
      full surface: trips CRUD, waypoints CRUD + reorder, checklist CRUD +
      import, reminders CRUD, warnings (read), share enable/disable,
      export, annotations CRUD, what-changed.
- [ ] New `features/trips/*`: trip list (`/trips`) + detail (`/trips/[id]`)
      with waypoints (dnd-kit sortable, keyboard-accessible drag),
      checklist (optimistic toggle + Sonner rollback toast per the plan's
      optimistic-CRUD pattern), reminders (date-fns formatted list),
      warnings/what-changed (terracotta callouts per plan), share/export
      actions.
- [ ] New public `app/[locale]/trips/shared/[token]/page.tsx` — read-only,
      plain RSC `await`, same precedent as Stage 7's public passport page
      (no `HydrationBoundary`, no client mutations).
- [ ] `@dnd-kit/core` + `@dnd-kit/sortable` added to `apps/web/package.json`;
      `date-fns` added alongside. Both justified per the plan's explicit
      component/library table for this stage — no substitution found that
      avoids them without hand-rolling drag reordering or date formatting.
- [ ] Optimistic-CRUD pattern (checklist toggles, watchlist star, future
      subscription toggles): `onMutate` optimistic update + `onError`
      rollback + Sonner terracotta toast, matching the plan's explicit
      pattern note — apply consistently across watchlist/checklist/
      subscriptions, not just one surface.
- [ ] `routes.ts` (`apps/web/src/shared/lib/routes.ts`) and
      `tests/e2e/helpers/routes.ts` gain `trips`, `tripDetail(id)`,
      `tripSharedPublic(token)`, `subscriptions`/`feed` entries.
- [ ] Preserve every existing `data-testid` from `AccountView`/
      `WatchlistView`/`WatchlistButton`; where markup genuinely changes
      (Dialog-wrapped revoke-all, card-grid watchlist), update the
      corresponding spec file instead of forcing old markup to survive.

## Implementation

- [ ] `entities/account/api.ts`: sessions list/revoke/revoke-all query +
      mutations, Telegram link/unlink/status, security-notifications
      list/ack.
- [ ] `entities/subscriptions/api.ts`: list/create/delete subscriptions,
      feed query.
- [ ] `entities/trips/api.ts`: trips CRUD, waypoints CRUD+reorder,
      checklist CRUD+import, reminders CRUD, warnings, what-changed,
      share enable/disable, export, annotations CRUD.
- [ ] `shared/api/subscriptions.ts`, `shared/api/trips.ts` (typed wrappers,
      matching `shared/api/watchlists.ts`'s existing style).
- [ ] Reskin `features/auth/AccountView.tsx` onto Card/Field/DataTable/
      Dialog + `entities/account/api.ts`.
- [ ] Reskin `features/watchlist/WatchlistView.tsx` onto the catalog-card
      grid + drift summary + `entities/watchlist/api.ts`.
- [ ] New `features/subscriptions/*`, `features/feed/*`.
- [ ] New `features/trips/*` (list, detail, waypoints dnd-kit, checklist,
      reminders, warnings, share/export UI).
- [ ] New route pages: `app/[locale]/trips/page.tsx`,
      `app/[locale]/trips/[id]/page.tsx`,
      `app/[locale]/trips/shared/[token]/page.tsx`; wire `/subscriptions`
      and/or `/feed` per the design decision above.
- [ ] Update `routes.ts` and `tests/e2e/helpers/routes.ts`.
- [ ] Update `web-mvp-session-security.spec.ts` and
      `web-mvp-watchlist.spec.ts` for markup changes; add new spec
      file(s) for Telegram linking, subscriptions/feed, and trips
      (CRUD, waypoint reorder, checklist optimistic toggle + rollback,
      reminders, share link, public shared-trip page).

## Verification

- [ ] `pnpm --filter web typecheck` / `lint`
- [ ] `pnpm --filter ui typecheck` / `lint` (if `packages/ui` gains any
      new primitive along the way)
- [ ] `pnpm build` — check all new routes compile, no duplicate-DOM
      regressions on any `force-dynamic` page touched.
- [ ] Manual browser check: account (profile/telegram/sessions/revoke),
      watchlist, subscriptions/feed, trip CRUD + waypoint drag-reorder +
      checklist optimistic toggle + reminders + share link + public
      shared-trip page, both locales, mobile viewport (dnd-kit keyboard
      fallback check).
- [ ] Full Playwright suite (`npx playwright test --workers=2` — the
      established clean baseline for this environment) — must stay green;
      update specs only where markup genuinely changed.
- [ ] `python dev_tools_scripts_runner.py full-check`

## Completion

- [ ] Commit(s)
- [ ] Merge to `main`, push
- [ ] Final report
