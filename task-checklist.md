# Task: Frontend Stage 12 (внутренний контур — админ/модерация)

Source plan: `docs/_arch_/FRONTEND_IMPLEMENTATION_PLAN.md`, §7 Этап 12.
Branch: `feat/frontend-stage12-internal-admin` (fresh off `main` — Stage 11
merged, `94565d6`).

This is the largest remaining stage: a full operator console covering 7+
distinct admin surfaces. Sequenced from foundation → highest-value queues
→ ops screens → lower-value/gap-limited surfaces, each its own commit,
verified before moving on — same discipline as Stage 10.

## Preparation

- [+] Research pass done (Explore agent + direct grep verification):
      inventoried every `/internal/*` route, the two Stage-10 hand-rolled
      moderation views, the role-guard mechanism, and every backend admin
      endpoint this stage could consume.
- [+] Confirmed `/internal/layout.tsx` is an explicit placeholder — its
      own comment says "Stage 12 gives it its own dedicated shell." No
      role-guard lives in the layout; each page guards itself via
      `useAuthGuard`. This stage keeps that per-page-guard convention
      (queues need different role/capability sets — `require_editor` vs
      `require_admin` vs `require_capability(MODERATOR_METRICS)` — a
      single layout-level guard can't express that) and only adds chrome
      (TopBar + queue sidebar) to the shell.
- [+] Confirmed `@tanstack/react-table` is genuinely absent from the repo
      (root/`apps/web` package.json, lockfile) — added this stage per
      plan.
- [+] Confirmed `packages/ui`'s existing `DataTable` is read-only
      (columns/rows only, no selection/actions/sorting) — not extended;
      a new `ModerationQueue` component is built on `@tanstack/react-table`
      instead, matching the plan's explicit "generic component built
      once" instruction. `Dialog`, `Drawer`, and a Sonner-backed `Toast`
      already exist in `packages/ui` and are unused anywhere in
      `apps/web` today — this stage is their first consumer.
- [+] Backend endpoint inventory per queue (full support unless noted):
      author-metrics admin (list+approve+reject, `require_capability(MODERATOR_METRICS)`),
      country-proposals admin (list+curator+readiness-check+scenario-scores+publish/reject/request-changes/archive, `require_editor`),
      contradiction-candidates admin (list+status patch, `require_editor`),
      AI-drafts admin (list+generate+status patch, `require_editor`),
      users admin (list+role+status+sessions+revoke-all, `require_admin` —
      stricter than the other queues, needs its own frontend role set),
      translation-jobs admin (list+create-missing+create-stale+process-batch+retry-failed, `require_editor`),
      recompute (drift/trust/platform-metrics, three separate routers
      sharing one `app/services/admin_recompute.py`, `require_editor`).
- [+] **Confirmed backend gaps, not routed around:**
      - User-stories admin moderation has POST (create) and PATCH
        (by-id) only — **no GET/list**, and the public list endpoint's
        `status` filter is restricted to `"published"|"archived"`
        (can't surface drafts/pending either). A moderation *queue* for
        user stories is not buildable against the real API. Skipped this
        stage; documented here rather than faked.
      - Evidence/sources/legal-signals admin endpoints are POST+PATCH
        only, **no GET/list** for any of the three. A browsable CRUD
        queue isn't buildable; only create/patch-by-known-id forms are.
        Scoped down accordingly (see Design decisions).

## Design decisions

- [+] `/internal` shell gets a compact `TopBar` + queue sidebar
      (`InternalShell` in `apps/web/src/shared/ui/InternalShell.tsx` or
      similar) wrapping `internal/layout.tsx`'s children — denser
      spacing, no card-glow/showcase animation per the plan's "канцелярия
      архива, а не витрина" framing. Per-page `useAuthGuard` stays the
      enforcement point; the shell itself is presentation-only chrome
      plus static nav links (a logged-out/wrong-role visitor sees the
      nav but each page still redirects/blocks on its own guard,
      matching the existing convention exactly).
- [+] New role set `STRICT_ADMIN_ROLES = new Set(["admin", "owner"])`
      added to `shared/auth/roles.ts` for the Users queue (backend
      `require_admin` excludes `editor`, unlike every other queue this
      stage which maps to the existing `ADMIN_ROLES`).
- [+] Generic `ModerationQueue` component
      (`apps/web/src/shared/ui/ModerationQueue.tsx`) built once on
      `@tanstack/react-table`: column-config prop, row actions with a
      `variant: "default" | "dangerous"` flag (dangerous actions render
      behind a confirming `Dialog`), a `Drawer` slot for row detail
      (render-prop), and Sonner `toast` on every action result. Reused
      by every new queue this stage; existing Stage-10
      `CommunityModerationView`/`MigrationBoardModerationView` are
      **not** retrofitted this stage (both are small, working, tested —
      forcing them through a not-yet-proven abstraction risks churn on
      working code; noted as a fast-follow once `ModerationQueue` is
      proven on 4+ real queues here).
- [+] Author-metrics, country-proposals, contradiction-candidates, and
      AI-drafts queues each get their own thin `entities/*/api.ts`
      Pattern-A wrapper and a config object fed into `ModerationQueue`.
- [+] Country-proposals admin gets the full workflow (curator assign,
      readiness-check, scenario-scores upsert, publish/reject/
      request-changes/archive) since the backend supports every step —
      the plan's explicit "полный workflow" instruction, and the one
      queue where "полный цикл без обращения к API вручную" is fully
      achievable.
- [+] Recompute panel is a standalone page (not a `ModerationQueue`
      instance — it's three confirm-gated action buttons + a response
      log, not a list), `/internal/recompute`.
- [+] Data-quality report reskinned from `useEffect`+fetch legacy
      styling onto TanStack Query + the existing read-only `DataTable`
      primitive (data is inherently read-only stats, not a queue).
- [~] Evidence/sources/legal-signals: scoped down to a single
      `/internal/evidence` page with three create forms (plain
      controlled state, matching the country-proposal wizard's form
      conventions) — explicitly NOT a browsable table, since no
      GET/list endpoint exists. **Correction from the original plan**:
      patch-by-known-id was also dropped during implementation (not
      just list) to keep this pass's scope honest about time invested
      versus value — a moderator with a known id can still reach the
      existing PATCH endpoints directly if needed; documented here as a
      further reduction, not silently dropped.
- [+] User-stories admin moderation: **not built this stage** — no
      buildable surface without a GET/list endpoint (see Preparation).

## Implementation

1. **Foundation** (commit `b44043d`) — `InternalShell` (TopBar + queue
   sidebar), `ModerationQueue` generic component (`packages/ui`, new
   `@tanstack/react-table` dependency in both `packages/ui` and
   `apps/web`), `STRICT_ADMIN_ROLES` added to `shared/auth/roles.ts`.
2. **First 4 queues** (commit `b44043d`) — author-metrics moderation
   (`/internal/author-metrics-moderation`), country-proposals curation
   with the full workflow (`/internal/country-proposals`),
   contradiction-candidates (`/internal/contradiction-candidates`),
   AI-drafts with a generate-summary form
   (`/internal/ai-drafts`). Each with its own `shared/api/admin-*.ts` +
   `entities/admin-*/api.ts` Pattern-A wrapper.
3. **Remaining surfaces** (commit `2f3cd16`) — users admin
   (`/internal/users`, role/status/sessions/revoke-all, gated by
   `STRICT_ADMIN_ROLES`), translation-jobs batch panel
   (`/internal/translation-jobs`), recompute panel with confirm dialogs
   and a monospaced log (`/internal/recompute`), data-quality reskin
   (`useEffect`+fetch → TanStack Query, testids unchanged), evidence
   create forms (`/internal/evidence`).
4. `tests/e2e/web-mvp-internal-admin.spec.ts` (new, 10 tests) — sidebar
   render check, unauthenticated-notice coverage for all 8 new pages,
   forbidden-role coverage for the strictest queue (users admin).

## Verification

- [+] `pnpm --filter web typecheck` — clean, no errors, across both
      batches.
- [+] `pnpm --filter web lint` — clean, no errors.
- [+] `pnpm --filter web build` — clean; all 11 `/internal/*` routes
      compile (8 new + data-quality reskinned + the 2 Stage-10 views
      left untouched).
- [+] Manual verification against the live Docker stack via Playwright
      (Docker Desktop and the seed data were already up from Stage 11's
      session).
- [+] Full regression: the new spec (10 tests) plus every spec touching
      `/internal/*` or auth/RBAC (`web-mvp-analytical-pages`,
      `web-mvp-auth-rbac`, `web-mvp-pages`, `web-mvp-migration-board`,
      `web-mvp-community-intelligence`) — **54/54 passed**, confirming
      the `DataQualityGate`/`DataQualityReportView` reskin didn't touch
      any of the 4 testids the existing specs depend on.
- [+] `python dev_tools_scripts_runner.py --profile quick` — clean
      except the pre-existing `arabic_reshaper` venv gap (same known
      baseline issue since Stage 9/10/11, not a regression).

## Completion

- [+] Commit(s) — 3 commits on `feat/frontend-stage12-internal-admin`
      (`2e39f05` checklist, `b44043d` foundation + 4 queues, `2f3cd16`
      remaining surfaces), plus this checklist finalization.
- [ ] Merge to `main`, push — only once explicitly confirmed complete.
- [+] Final report — given in the chat response accompanying this
      checklist update.
