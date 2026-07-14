# Task: Frontend Stage 10 (сообщество — истории, Q&A, борд, авторские метрики, заявки стран)

Source plan: `docs/_arch_/FRONTEND_IMPLEMENTATION_PLAN.md`, §7 Этап 10.
Branch: `feat/frontend-stage10-community` (fresh off `main` — Stage 9
merged, `b8888e3`).

This is the largest stage in the plan ("самый широкий по числу экранов
этап") — 4-5 UGC subsystems at very different levels of existing
completeness. Given the size, implementation is sequenced from most-
contained to most-complex; each subsystem gets its own commit(s) and is
verified before moving to the next, matching the pattern from Stage 9.

## Preparation

- [+] Research pass done (Explore agent) inventorying all five
      subsystems. Key findings:
      - `features/migration-board/*` (9 files) fully exists but is 100%
        legacy: raw `useEffect`/`useState`, no TanStack Query, no
        `entities/migration-board/api.ts`, plain global CSS classes
        (`pageShell`, `runButton`, `cardGrid`, etc.), zero
        `@country-decision-atlas/ui` imports. Biggest reskin lift.
      - `features/community/CommunityCountryBlock.tsx` is already modern
        (TanStack Query + DS primitives) but only a single embedded
        country-page block, not a standalone page; its "6-axis" rating is
        actually one collapsed slider, not 6 real axes; no admin
        moderation UI for questions/answers/reports.
      - User stories: only a list-only `shared/api/user-stories.ts`
        (43 lines) — no entity, no components, no create/rating UI despite
        `UserStoryCreate`/`UserStoryRatingCreate`/etc. existing in
        contracts.
      - Author metrics: nothing exists (no entity, no shared/api, no
        feature, no route) — contracts fully define definitions/values/
        submit/archive/fork/moderate/reputation.
      - Country proposals: nothing exists — contracts fully define the
        6-section wizard sub-resources (sources/evidence/signals/
        timeline-events/metric-values) + admin curator/readiness/publish
        workflow. Genuinely the largest single build in this stage
        ("мастер-страница" per the plan) — see the scope note below.
- [+] Contract schemas confirmed present for all five subsystems (full
      enumeration in the research agent's report, condensed): UserStory*,
      Community{Question,Answer}*+ConsensusSummary, DataErrorReport*,
      MigrationBoard{Post,Report,ContactRequest,BlockedUser,Match}* (no
      dedicated message-thread schema — contact-request accept/decline
      IS the thread primitive, no separate chat-messages endpoint exists,
      contradicting the plan's mention of `me/threads/{id}/messages`;
      built against the real contract instead, see design decisions),
      AuthorMetric{Definition,Value,Reputation}*, CountryProposal*
      (+ sources/evidence-items/legal-signals/timeline-events/
      metric-values sub-collections, `/card/{locale}` preview endpoint).
- [+] Existing Playwright coverage inventoried:
      `web-mvp-community-intelligence.spec.ts` (one test, country-page
      embedded block selectors), `web-mvp-migration-board.spec.ts` (two
      tests, list/filter/new-post/account/moderation-guard selectors).
      Both preserved; no e2e exists yet for user-stories, author-metrics,
      or country-proposals standalone (all net-new test surface).
- [+] Design-system fit-check: `DossierRail` (sticky IntersectionObserver
      side-nav) is the right primitive for the country-proposal wizard's
      step rail. `RadarChart` (not `DivergingMeter`) is the right fit for
      the 6-axis story rating — one axis per rating dimension, not a
      paired comparison. `ProgressRing` for author reputation. No chat/
      thread-list primitive exists — composed ad-hoc from Card/Badge for
      migration-board contact requests.

## Scope decision for this stage

Given the size, this stage ships in the following order, each a
self-contained commit, verified before moving on:
1. `features/migration-board/*` full reskin onto TanStack Query + DS
   (biggest existing-code lift, clearest precedent from Stage 5-9).
2. `features/community/*` extension: standalone Q&A, real 6-axis
   `RadarChart` rating, admin moderation queries/UI.
3. User stories: full build-out (entity, shared/api CRUD, feed page,
   submission form, rating display).
4. Author-metrics studio: CRUD definitions, values entry, submit/fork,
   public author profile with `ProgressRing` reputation.
5. Country proposals wizard: the "мастер-страница" — sources → evidence
   → signals → metrics → timeline → locale preview → submit, with
   `DossierRail` step navigation and a readiness `ProgressRing`.

If effort runs out before all five land, each subsystem is independently
committable and the checklist below will say honestly which shipped and
which didn't — no subsystem gets silently dropped without a note.

## Design decisions

- [+] Migration Board's "message thread" is modeled on the real contract
      (contact-request accept/decline + the request itself as the unit),
      NOT a separate `me/threads/{id}/messages` polling chat as the plan
      text describes — that schema doesn't exist. No realtime/polling
      chat UI is built; this is a scope correction, not a deferral of
      planned work that's actually possible.
- [+] `entities/migration-board/api.ts` created wrapping the already-
      thorough `shared/api/migrationBoard.ts` (Pattern A, matching
      `entities/decision/api.ts`'s style) — the shared/api layer itself
      didn't need rebuilding except for a real bug: the exported
      `migrationBoardApi` bundle object was missing 7 already-defined
      admin functions (`listAdminBoardPosts`, `approveAdminBoardPost`,
      `rejectAdminBoardPost`, `hideAdminBoardPost`,
      `listAdminBoardReports`, `resolveAdminBoardReport`,
      `dismissAdminBoardReport`) — added them to the bundle.
- [+] Community's single-value "review gate" rating becomes a real 6-axis
      `RadarChart` input — confirmed the backend rating payload accepts 6
      distinct fields (`official_expectation_score`,
      `real_experience_score`, `bureaucracy_score`, `cost_surprise_score`,
      `banking_difficulty_score`, `safety_feeling_score`); the old UI was
      sending one collapsed value into all 6, fixed with 6 independent
      sliders + a live `RadarChart` preview.
- [+] Every new UGC form gets the plan's explicit PII soft-warning
      ("не публикуйте контакты в открытом тексте") as inline `FieldHint`
      text — backend validates, frontend only warns.
- [+] Country-proposal wizard: `DossierRail` step navigation +
      `ProgressRing` readiness indicator (hardcoded `value={0}` — the
      contract has no readiness/progress field on `CountryProposal`, so
      this is a visual placeholder, not a computed metric; noted as tech
      debt below), one form-section per sub-resource matching the plan's
      explicit UI-pattern note.

## Implementation

1. **Migration Board reskin** (commit `82ccff6`) — `entities/migration-board/api.ts`
   added; `MigrationBoardListView`, `MigrationBoardDetailView`,
   `MigrationBoardFormView`, `AccountMigrationBoardView`,
   `MigrationBoardModerationView`, `CountryMigrationBoardBlock`,
   `RouteMigrationBoardBlock`, all 4 route shells reskinned onto
   Kicker+h1+DS primitives. Bug found and fixed: `migrationBoardApi`
   bundle missing 7 admin functions (see Design decisions).
2. **Community extension** (commit `c00cc6d`) — real 6-axis
   `RadarChart` rating form; `CommunityModerationView` (new) covering
   questions/answers/reports/ratings moderation queues; new route
   `/internal/community-moderation`; 8 new admin API functions +
   entity wrappers + 4 status-update mutations.
3. **User stories** (commit `c9651b5`) — `entities/user-stories/api.ts`
   (new), `UserStoriesView` (feed + submission form, country + scenario
   `<select>`), new route `/user-stories`, nav entry. Bug found and
   fixed: default synthetic `notes` text didn't satisfy the DB check
   constraint `user_stories_synthetic_quality_check` (500 error) —
   fixed the notes string; free-text scenario input replaced with a
   `<select>` after `422 user_story_scenario_invalid` errors.
4. **Author-metrics studio** (commit `52bc06c`) — `apiPut` added to
   `shared/api/http.ts` (only GET/POST/PATCH/DELETE existed);
   `shared/api/author-metrics.ts` + entity wrappers (full CRUD, bulk
   values, submit/archive/fork, public reputation); `AuthorMetricsStudioView`
   (own-metrics CRUD, auth-guarded) and `AuthorProfileView` (public,
   made resilient to `author_reputation_not_found` 404 instead of a
   full-page error); routes `/account/author-metrics`, `/authors/[userId]`.
   **Confirmed limitation**: `author.metrics` is capability-gated
   (`require_capability`, no role bypass, `apps/api/app/core/rbac.py`),
   grantable only via `POST /api/v1/admin/capabilities` (owner-only) — no
   path exists to grant it through the public UI, so the positive
   create-metric flow cannot be exercised end-to-end via public
   registration.
5. **Country proposals wizard** (this commit) —
   `shared/api/country-proposals.ts` + `entities/country-proposals/api.ts`
   (full CRUD + all 5 sub-resource creators + card upsert);
   `CountryProposalListView` (create form + own-proposals grid) and
   `CountryProposalWizardView` (7 `DossierRail`-linked sections:
   sources, evidence, legal signals, timeline, metrics, card preview,
   submit); routes `/account/country-proposals`,
   `/account/country-proposals/[id]`.
   **Confirmed limitation**: none of the 5 sub-resource endpoints
   (sources, evidence-items, legal-signals, timeline-events,
   metric-values) has a GET/list endpoint — only POST/PATCH exist
   (confirmed against `packages/contracts/generated/types.ts`). Rows
   persist server-side but can't be re-read by this page; each section
   tracks "added this session" locally for UI feedback only, and a page
   reload loses that local list even though the underlying data is
   safe. Documented in-code and here — not routed around.
   **Confirmed limitation**: `contributor.countries` is capability-gated
   the same way as `author.metrics` (same `require_capability` pattern,
   `apps/api/app/api/v1/country_contribution.py`) — not grantable via
   public UI.

## Verification

- [+] `pnpm --filter web typecheck` — clean, no errors.
- [+] `pnpm --filter web lint` — clean, no errors.
- [+] `pnpm --filter web build` — clean; both new routes
      (`/account/country-proposals`, `/account/country-proposals/[id]`)
      compile and appear in the route manifest.
- [+] Manual verification against the live Docker stack (`docker compose
      up --build -d api redis` + migrations/seed) for all 5 subsystems,
      via Playwright rather than the in-app browser tool (which proved
      unreliable for multi-step flows this session).
- [+] Full Stage-10 Playwright regression at `--workers=2` across all 5
      subsystem specs (`web-mvp-migration-board`,
      `web-mvp-community-intelligence`, `web-mvp-user-stories`,
      `web-mvp-author-metrics`, `web-mvp-country-proposals`): **15/15
      passed**.
- [ ] `python dev_tools_scripts_runner.py full-check` — not yet run this
      session; the two previously-known baseline gaps (arabic_reshaper
      venv gap, `go test -race` requiring a local CGO toolchain) are
      expected to remain and are not regressions from this work.

## Completion

- [+] Commit(s) — 5 subsystem commits on `feat/frontend-stage10-community`
      (`82ccff6`, `c00cc6d`, `c9651b5`, `52bc06c`, plus this one for
      country-proposals + checklist finalization), on top of the
      checklist-init commit `df0333d`.
- [ ] Merge to `main`, push — pending explicit owner go-ahead per this
      task's instruction ("push only once you tell me the stage is
      finished").
- [+] Final report — given in the chat response accompanying this
      checklist update.
