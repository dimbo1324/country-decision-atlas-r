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

- [ ] Migration Board's "message thread" is modeled on the real contract
      (contact-request accept/decline + the request itself as the unit),
      NOT a separate `me/threads/{id}/messages` polling chat as the plan
      text describes — that schema doesn't exist. No realtime/polling
      chat UI is built; this is a scope correction, not a deferral of
      planned work that's actually possible.
- [ ] `entities/migration-board/api.ts` created wrapping the already-
      thorough `shared/api/migrationBoard.ts` (Pattern A, matching
      `entities/decision/api.ts`'s style) — the shared/api layer itself
      doesn't need rebuilding, only a Query wrapper + component reskin.
- [ ] Community's single-value "review gate" rating becomes a real 6-axis
      `RadarChart` input if the backend rating creation payload supports
      6 distinct fields (verify `UserStoryRatingCreate`/community rating
      schema field-by-field before committing to this — if the backend
      only accepts one scalar, the UI stays single-value and this
      decision is corrected in place, not implemented against a
      nonexistent multi-field API).
- [ ] Every new UGC form gets the plan's explicit PII soft-warning
      ("не публikуйте контакты в открытом тексте") as inline `FieldHint`
      text — backend validates, frontend only warns.
- [ ] Country-proposal wizard: `DossierRail` step navigation +
      `ProgressRing` readiness indicator, one form-table per section,
      matching the plan's explicit UI-pattern note.

## Implementation

(Filled in per subsystem as each lands — see Scope decision above.)

## Verification

- [ ] `pnpm --filter web typecheck` / `lint`
- [ ] `pnpm --filter web build`
- [ ] Manual browser check per subsystem against the live Docker stack.
- [ ] Full Playwright suite at `--workers=2` — must stay green; existing
      `web-mvp-community-intelligence.spec.ts` and
      `web-mvp-migration-board.spec.ts` preserved, new specs added per
      subsystem.
- [ ] `python dev_tools_scripts_runner.py full-check`

## Completion

- [ ] Commit(s)
- [ ] Merge to `main`, push
- [ ] Final report
