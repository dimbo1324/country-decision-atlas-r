# Implementation Roadmap

> The executive plan for the current development line. The implemented system ([../architecture/overview.md](../architecture/overview.md)) is the baseline; episode numbering restarts at 1. Every episode follows the working standard ([../operations/working-standard.md](../operations/working-standard.md)): its own `feat/<slug>-v1` branch, migrations continuing the existing sequence (046+), new surfaces behind feature flags (off until acceptance), a data-quality package from day one, a full quality gate before merging.
>
> Owner decisions locked into the plan (2026-07-04, the full log is in [../decisions/open-questions.md](../decisions/open-questions.md)): the k-anonymity threshold = 20; the owner does not act as "author #1" (the cold start is covered in the Episode 4 section); synthetic stories are displaced by real ones; monetization is future donations (Uruguay jurisdiction), for now only the foundation; the moderator institution follows the model in [../architecture/rights-and-roles.md](../architecture/rights-and-roles.md); methodology premoderation lasts until ~50 authors (switching to postmoderation once the rejection rate stays under 10%); contribution licenses use option "c"; test countries are never deleted — they're conserved as a demo set (Episode 5).
>
> **Autonomous development mode (decision D-10):** until the integration tranche, no episode connects a real external service — the entire 1–7 line is built and tested offline through fake seams. Episode acceptance criteria are written accordingly (e.g., reminder delivery is verified against the fake mode's delivery log).

---

## 1. Line summary

| # | Episode | Branch | Gist | Depends on |
|---|---|---|---|---|
| 1 | Flexible methodology | `feat/flexible-methodology-v1` | Thresholds/limits move from code → versioned configuration; savable weight profiles | — |
| 2 | Trip planner | `feat/trip-planner-v1` | A personal surface: a plan, checklists, rule-based warnings, Telegram reminders, export, sharing | 1 (parameters) |
| 3 | Rights and roles v2 | `feat/rights-capabilities-v1` | Capability grants, a moderator institution, governance surfaces, auto-sanctions | 1 (thresholds) |
| 4 | Author metrics | `feat/author-metrics-v1` | Creation/moderation/publication/subscriptions/forks; author reputation | 3 |
| 5 | Country contribution | `feat/country-contribution-v1` | A community country-proposal and population pipeline; the fate of the test countries | 3, 4 (patterns) |
| 6 | Migration flows and statistics | `feat/migration-flows-v1` | Destination aggregates (k=20), confidence tiers, a "relocation journal," displacing synthetic data | 2 |
| 7 | Contact threads | `feat/community-threads-v1` | Lightweight mutual-consent conversation + a Telegram deep link | 3 |
| — | Visual tranche | a separate line | The showcase: infographics, drift/flows, a map (Leaflet/OSM), evocative metric names | after 1–2 at minimum |
| — | Integration tranche | a separate line | Real connections: Telegram real mode, an LLM provider, payments (Uruguay), email, OAuth, hosting | after the owner's relocation |

Dependency map:

```
1 (parameters/profiles) ──→ used by everything (thresholds, limits, k)
2 (planner) ─────────────→ 6 (flows feed off plans)
3 (rights v2) ────────────→ 4 (authors) ──→ 5 (country contribution)
                        └─→ 7 (threads: sanctions/moderation)
```

Recommended order: **1 → 2 → 3 → 4 → 5 → 6 → 7**. Episode 2 is deliberately placed before 3–4: daily-return value gets built before the author surface needs an audience.

---

## 2. Episodes

### Episode 1 — `feat/flexible-methodology-v1`: flexible methodology

**Status.** Implemented (migration 046, `services/methodology_config.py`, `services/weight_profiles.py`). The hardcoded-value inventory from the baseline's §5 was moved into `methodology_parameters`; the table in [../architecture/overview.md](../architecture/overview.md) was updated.

**Goal.** Move interpretation thresholds and product limits out of code and into versioned configuration; give users savable weight profiles. Zero default-behavior change.

**Data model (migration 046).**

```sql
CREATE TABLE methodology_parameters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version TEXT NOT NULL DEFAULT 'v1.0',
    param_key TEXT NOT NULL,          -- 'score_label.weak_below', 'strength.min_score',
                                      -- 'board.max_active_posts', 'flows.k_anonymity', ...
    value_numeric NUMERIC,
    value_json JSONB,
    description TEXT NOT NULL,
    effective_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_methodology_param UNIQUE (version, param_key)
);
-- seed: the hardcoded-value inventory from overview.md §5,
-- values = the existing constants; flows.k_anonymity = 20

CREATE TABLE user_weight_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    scenario_slug TEXT,               -- NULL = applies to any scenario
    weights JSONB NOT NULL,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_profile_name UNIQUE (user_id, name)
);
```

**Service layer.** A new `services/methodology_config.py`: typed reads of the active version with caching; a missing key is a hard error (no silent second source of truth). Consumers (`score_labels`, `decision_engine`, `_recommend`, board limits) move onto the configuration; pure functions receive parameters as arguments. A new `services/weight_profiles.py`: CRUD; validation reuses `decision_personalization.validate_custom_weights`.

**API.** `GET/POST/PATCH/DELETE /me/weight-profiles`; `decision/run` accepts a `weight_profile_id` (mutually exclusive with inline weights); every decision response and passport carries `methodology_version`; a passport snapshots the weights that were applied (by value — for reproducibility). `GET /methodology/parameters` — a public read of the active version (transparency).

**Tests/acceptance.** A bit-for-bit regression: the existing test suite passes with no expectation changes. dq: the active version exists and is complete, values are within range. Acceptance: a profile saves, applies, and a passport reproduces the calculation after the profile changes. **Not doing:** user-set thresholds that affect other people's views; UI editing of platform parameters.

**Scope.** 1 migration, 2 services, edits to 4–5 consumers, ~25–35 tests.

---

### Episode 2 — `feat/trip-planner-v1`: trip planner

**Status.** Implemented (migration 047, the `services/trip_planner/` package, `scripts/dispatch_trip_reminders.py`, registered in `dev_tools_scripts_runner.py`).

**Goal.** A personal, daily-use surface: a plan → waypoints → a checklist → rule-based warnings → Telegram reminders → export/sharing. No map UI (that's the visual tranche).

**Data model (migration 047).**

```sql
CREATE TABLE trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    scenario_slug TEXT,
    origin_country_id UUID REFERENCES countries(id),
    status TEXT NOT NULL DEFAULT 'draft',            -- draft|active|completed|abandoned
    confidence_tier TEXT NOT NULL DEFAULT 'declared',-- declared|active|confirmed (for Episode 6)
    visibility TEXT NOT NULL DEFAULT 'private',      -- private|link
    share_token_hash TEXT UNIQUE,
    share_token_prefix TEXT,
    created_at/updated_at/completed_at TIMESTAMPTZ
);

CREATE TABLE trip_waypoints (
    id UUID PK, trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    position INT NOT NULL,
    country_id UUID NOT NULL REFERENCES countries(id),
    city TEXT,
    kind TEXT NOT NULL DEFAULT 'destination',        -- transit|destination|stopover
    planned_from DATE, planned_to DATE,
    notes TEXT,
    CONSTRAINT uq_trip_position UNIQUE (trip_id, position)
);

CREATE TABLE trip_checklist_items (
    id UUID PK, trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    waypoint_id UUID REFERENCES trip_waypoints(id) ON DELETE SET NULL,
    title TEXT NOT NULL, description TEXT,
    due_date DATE,
    status TEXT NOT NULL DEFAULT 'todo',             -- todo|in_progress|done|skipped
    origin_kind TEXT NOT NULL DEFAULT 'manual',      -- manual|route_template|author_template
    origin_ref UUID,
    position INT NOT NULL,
    created_at/updated_at TIMESTAMPTZ
);

CREATE TABLE trip_reminders (
    id UUID PK, trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    checklist_item_id UUID REFERENCES trip_checklist_items(id) ON DELETE CASCADE,
    remind_at TIMESTAMPTZ NOT NULL,
    channel TEXT NOT NULL DEFAULT 'telegram',
    status TEXT NOT NULL DEFAULT 'scheduled',        -- scheduled|sent|cancelled
    sent_at TIMESTAMPTZ
);

CREATE TABLE trip_annotations (                      -- user notes
    id UUID PK, trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    waypoint_id UUID REFERENCES trip_waypoints(id) ON DELETE CASCADE,
    kind TEXT NOT NULL,                              -- note|item_to_bring|warning_ack
    body TEXT NOT NULL,
    position INT
);
```

**Service layer — the `services/trip_planner/` package:** `trips.py` (CRUD, status transitions, an "I relocated" hook into Episode 6), `checklist.py` (CRUD; importing steps from published `route_checklist_items`), `warnings.py` (a rules engine: plan segments → `country_pair_compatibility` + `legal_signals` → `{code, severity, message, source_ids}` warnings; severity comes from Episode 1 parameters; **no AI**), `reminders.py`, `sharing.py` (a token pattern matching passports; a PII-safe projection matching `_public_post`), `exports.py` (full JSON; ICS by deadline — a stdlib generator; GeoJSON waypoints), `helpers.py`.

**Reminders — through the existing surface.** The `scripts/dispatch_trip_reminders.py` script (modeled on the recompute scripts): a due-item query → `domain_events(event_type='trip_reminder_due', event_key='trip_reminder:{id}', notifiable=TRUE)` → relay → Kafka → the notifier: a new event type + render → Telegram (no linking — logged to the DLQ without crashing).

**API (behind the `trip_planner_enabled` flag).** `GET/POST /me/trips`; `GET/PATCH/DELETE /me/trips/{id}`; waypoint CRUD + reorder; `GET …/warnings`; checklist CRUD + `POST …/checklist/import {route_id}`; reminder POST/DELETE; share POST/DELETE + `GET /trips/shared/{token}`; `GET …/export?format=json|ics|geojson`.

**Integrations.** Watchlist: a plan's countries are added idempotently (drift/signal alerts then work for the plan). `GET …/what-changed` — a proxy to the existing mechanism, scoped to the plan's countries. "Create a plan from a decision passport." AI buttons ("explain this warning," "draft a checklist") are separate endpoints through the existing seam, marked, optional.

**Tests/acceptance.** Unit tests for the warnings engine (a matrix: a pair with a note / no pair / a high-impact signal); a PII-filter invariant test on the shared projection's field list; ICS validity; reminder → event payload. Acceptance: the full cycle — "created a plan → a sourced warning → imported steps → a reminder (fake mode: a delivery-log entry) → marked done → exported ICS" — with no AI. **Not doing:** a map UI, collaborative editing, OAuth calendars, a public plan catalog.

**Scope.** 1 migration (5 tables), a package of ~7 modules, 1 script, +1 event type in the notifier, ~50–70 tests.

---

### Episode 3 — `feat/rights-capabilities-v1`: rights and roles v2

**Status.** Implemented (migration 048, `services/capabilities.py`, `require_capability`/`require_capability_or_roles` in `core/rbac.py`, `/admin/capabilities`, `/admin/moderation/actions`). The board and Q&A queues moved onto scoped capabilities with no change to existing role behavior; a conflict-of-interest check was added to board moderation actions, plus a level-1 auto-sanction (auto-hiding a post once it hits N confirmed reports, parameter `board.auto_hide_report_threshold`).

**Goal.** Introduce capability grants and a moderator institution, following the model in [../architecture/rights-and-roles.md](../architecture/rights-and-roles.md), without changing existing role behavior.

**Data model (migration 048).** `user_capabilities` (see the rights model document, §3.2).

**Service layer.** `services/capabilities.py`: `has_capability` (a role bundle OR an active grant), a `require_capability(cap)` dependency modeled on `require_roles`; grant/revoke with an audit record; a conflict-of-interest check for moderate actions (a moderator can't be a party to the object). A level-1 auto-sanction: auto-hiding an object once it hits N confirmed reports (N is an Episode 1 parameter), queued for post-review.

**API.** Governance (owner): `GET/POST/DELETE /admin/capabilities` (grant/revoke, with a reason); `GET /admin/moderation/actions` — a moderator action feed (filters, anomalies). Moderation queues already exist (the board, Q&A) — they move off `require_moderator` onto scoped capabilities with no behavior change (`moderator` covers every scope).

**Tests/acceptance.** A parameterized "action × role/grant → status" matrix (from §4 of the rights document); a deny-by-default test on every privileged router; conflict of interest; revoking a grant takes effect immediately. Acceptance: a user with the `moderator.board` grant can work the board queue and has no access to other scopes' queues; every one of their actions shows up in the governance feed. **Not doing:** moderator applications (phase 2), auto-granting rights from reputation (forbidden by an invariant).

**Scope.** 1 migration, 1 service + router-dependency edits, 2 admin surfaces, ~30–40 tests.

---

### Episode 4 — `feat/author-metrics-v1`: author metrics

**Status.** Implemented (migration 049 — 4 tables + the `author_metrics_enabled` flag +
`author_metrics.min_methodology_length`/`author_metrics.min_country_coverage`
thresholds; the `repositories/author_metrics/` and `services/author_metrics/`
packages (`definitions.py`, `values.py`, `subscriptions.py`, `reputation.py`, `overlay.py`,
`forks.py`, `helpers.py`); a public + `/me` router `api/v1/author_metrics.py` and
`api/v1/admin_author_metrics.py`; `scripts/recompute_author_reputation.py`
registered in `dev_tools_scripts_runner.py`; DQ checks wired into
`services/data_quality/report.py`; the contract and
`packages/contracts/generated/types.ts` updated; ~85 tests, including an
invariant snapshot test of CII/decision against `services/author_metrics`). The
frontend (an author-metrics showcase on the country page) is not part of this
episode — following the precedent of episodes 1–3, the visual layer belongs to
the separate visual tranche after episode 7.

**Goal.** Open the metric system to the community: creation, premoderation, publication, subscriptions, forks, derived author reputation. The platform CII stays untouchable.

**Data model (migration 049).**

```sql
CREATE TABLE author_metric_definitions (
    id UUID PK,
    author_user_id UUID NOT NULL REFERENCES users(id),
    slug TEXT NOT NULL,
    name_en/name_ru TEXT NOT NULL,
    methodology_en/methodology_ru TEXT NOT NULL,     -- mandatory before publish
    polarity TEXT NOT NULL,                          -- positive|negative
    scale_min NUMERIC NOT NULL DEFAULT 0,
    scale_max NUMERIC NOT NULL DEFAULT 100,
    license TEXT NOT NULL DEFAULT 'platform',        -- platform|cc_by_sa (the
                                                     -- author's choice at
                                                     -- publish time; decision D-4)
    status TEXT NOT NULL DEFAULT 'draft',            -- the existing lifecycle
    visibility TEXT NOT NULL DEFAULT 'public',
    forked_from_id UUID REFERENCES author_metric_definitions(id),
    version INT NOT NULL DEFAULT 1,
    created_at/updated_at/published_at TIMESTAMPTZ,
    CONSTRAINT uq_author_metric UNIQUE (author_user_id, slug)
);

CREATE TABLE author_metric_values (
    id UUID PK,
    metric_id UUID NOT NULL REFERENCES author_metric_definitions(id) ON DELETE CASCADE,
    country_id UUID NOT NULL REFERENCES countries(id),
    value NUMERIC NOT NULL,
    source_url TEXT,
    is_personal_experience BOOLEAN NOT NULL DEFAULT FALSE,
    note TEXT,
    valid_as_of DATE NOT NULL,
    updated_at TIMESTAMPTZ,
    CONSTRAINT uq_metric_country UNIQUE (metric_id, country_id),
    CONSTRAINT chk_provenance CHECK (source_url IS NOT NULL OR is_personal_experience)
);

CREATE TABLE author_subscriptions (
    id UUID PK, user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    metric_id UUID REFERENCES author_metric_definitions(id) ON DELETE CASCADE,
    author_user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ,
    CONSTRAINT chk_target CHECK (metric_id IS NOT NULL OR author_user_id IS NOT NULL)
);

CREATE TABLE author_reputation (                     -- derived, recomputed
    author_user_id UUID PRIMARY KEY REFERENCES users(id),
    coverage_score/freshness_score/sourcing_score NUMERIC,
    subscriber_count INT, published_metric_count INT,
    computed_at TIMESTAMPTZ, methodology_version TEXT
);
```

**Service layer — the `services/author_metrics/` package:** `definitions.py` (CRUD + a submit→review→publish lifecycle; text PII scanning; a publish threshold: a methodology no shorter than a minimum length, coverage ≥ N countries — Episode 1 parameters), `values.py` (bulk upsert, scale validation), `subscriptions.py`, `reputation.py` (a recompute script modeled on trust), `overlay.py` (author layers for the country page/comparison — **separate endpoints**, never mixed into CII), `forks.py` (a fork copies a definition and its methodology with `forked_from_id`; the author fills in their own values), `helpers.py`.

**Rights.** Creating one requires the `author.metrics` grant; premoderation runs through the `moderator.metrics` scope (until the institution matures — the owner). Issuing the first grants is invite-only (see the cold start).

**The cold start (the owner isn't "author #1").** (1) Platform methodologies (CII, Trust, Drift) are shown in the same showcase format, "methodology + version + last updated" — a genre example exists from day one; (2) templates from route checklists — author content with no authors; (3) invite-only grants to active participants with high derived reputation; (4) open submissions — after moderation is tested.

**Key invariants (enforced by tests).** No platform CII/decision/compare endpoint changes its response because author data exists (a before/after seed snapshot test); publishing with no methodology is impossible; every value carries a source OR an explicit "personal experience" mark; a fork carries its lineage.

**API (behind the `author_metrics_enabled` flag).** `GET/POST/PATCH /me/author-metrics` (+submit/archive); `PUT /me/author-metrics/{id}/values` (bulk); `POST /author-metrics/{id}/fork`; `GET /authors/{user_id}/metrics`; `GET /countries/{slug}/author-metrics`; subscriptions `POST/DELETE /me/subscriptions` + `GET /me/subscriptions/feed`; an admin queue `GET /admin/author-metrics?status=review`.

**Donation foundation (no implementation).** No payment tables at all; `author_user_id` + subscriptions are enough. Invariant: money never affects reputation/rights/grants (see the registry). The concrete model comes after the open questions are answered.

**Acceptance.** The full draft→review→published path; a subscriber-facing layer on the country page with "author, version, updated"; the core invariant snapshot test stays green. **Not doing:** monetization, "top authors," comments on metrics, blending into CII.

**Scope.** 1 migration (4 tables), a package of ~7 modules, 1 recompute script, an admin router, ~60–80 tests.

---

### Episode 5 — `feat/country-contribution-v1`: community country contribution

**Status.** Implemented (migration 050 — `country_proposals` +
`countries.is_demo` + `country_contribution_enabled`; the
`repositories/country_contribution/` and `services/country_contribution/`
packages (`proposals.py`, `content.py`, `curation.py`, `scores.py`, `helpers.py`);
a contributor router `api/v1/country_contribution.py` (`/me/country-
proposals/...`) and a curator/editor router `api/v1/admin_country_contribution.py`
(`/admin/country-proposals/...`); DQ checks in
`services/data_quality/country_contribution_checks.py` wired into the report;
the demo set (RU/UY/AR) preserved (`is_active=TRUE`, `is_demo=TRUE`) and hidden
from public surfaces (listings/details, `/decision/run`, the CII/compare
matrix, drift, platform metrics, trust, search, country-pairs, the legal-signal
timeline) via targeted read-repository edits, without touching the recompute
scripts; fixtures exported by `scripts/dev_tools/
export_demo_countries.py` into `database/fixtures/demo_countries/*.json` and
restored idempotently by `scripts/dev_tools/restore_demo_countries.py`
(registered in `dev_tools_scripts_runner.py`); the contract and
`packages/contracts/generated/types.ts` updated.
Owner decisions recorded during implementation: country scenario scores
(`country_scores`/`country_score_breakdowns`) are entered only by the editor
curator (a new editor-gated `PUT .../scenario-scores` endpoint), not by the
contributor; CII metric values (`country_metric_values`) are entered by the
contributor. Contributor content (the card/sources/evidence/legal
signals/timeline) flows through dedicated `/me/country-proposals/{id}/...`
endpoints (ownership-gated wrappers over `services/admin_content`), not through
the existing `/admin/*` endpoints — editor behavior is unchanged. The
frontend is not part of this episode — following the precedent of episodes
1–4, the visual layer belongs to the separate visual tranche.

**Goal.** Open the content core: users with a grant propose countries and maintain their population under editorial curation, following a formal standard. Resolve the fate of the test countries.

**Foundation.** A country onboarding standard is already formalized in code: the `build_country_onboarding_dq_results` dq checks and the onboarding-standard tests describe what a country must have (a card, sources, signals, CII metrics, evidence). That standard becomes the **automatic contribution gate** — a programmatic readiness checklist.

**Data model (migration 050).**

```sql
CREATE TABLE country_proposals (
    id UUID PK,
    proposer_user_id UUID NOT NULL REFERENCES users(id),
    slug TEXT NOT NULL UNIQUE,
    name_en/name_ru TEXT NOT NULL,
    justification TEXT NOT NULL,                 -- why the platform needs this country
    status TEXT NOT NULL DEFAULT 'draft',        -- the existing lifecycle
    curator_user_id UUID REFERENCES users(id),   -- the assigned editor
    readiness_snapshot JSONB,                    -- the latest onboarding-gate run
    created_at/updated_at/published_at TIMESTAMPTZ
);
```

A country proposal creates a hidden (unlisted) `countries` row in draft status; population (the card, sources, signals, metric values) uses the existing editorial mechanisms, but a contributor's edits are scoped to their own country (the `contributor.countries` grant + ownership of the proposal). Transitioning to review/published is editor-curator-only, after a passing onboarding gate.

**Demo-set conservation (decision D-1: test countries are never deleted).** In this episode, the current RU/UY/AR set: (a) is run through the onboarding gate as the pipeline's first "patients"; (b) gets a `countries.is_demo` flag — demo countries are hidden from all public surfaces (listings, search, decisions) but remain in the DB; (c) a full linked dump of the demo set (countries, cards, sources, signals, metrics, routes) is exported to JSON fixtures under `database/fixtures/demo_countries/`; (d) a dev tool, `scripts/dev_tools/restore_demo_countries.py`, is created — an idempotent, one-command restore of the demo set from fixtures (registered in the `dev_tools_scripts_runner.py` orchestrator as a single `ScriptInfo` entry). A developer can get a working local dataset at any time.

**Rights.** `contributor.countries` is an invite-only grant; curation is editor-only; publishing is editor/owner. Contributor attribution is preserved publicly (the country page: "data contributed by …").

**Tests/acceptance.** The gate: a country missing a required piece never reaches review (automatically); a contributor can't edit someone else's country or the core; a curator is mandatory for publishing; demo countries appear on no public surface; `restore_demo_countries.py` restores the set idempotently, and the restored set passes the onboarding gate. Acceptance: a fully populated candidate country goes through proposal→population→gate→review→published and shows up on every surface (decisions, comparison, search) with no manual code changes. **Not doing:** open submission with no grant; auto-publishing with no curator; bulk country import; deleting demo data.

**Scope.** 1 migration, the `country_contribution/` service package, admin/curator surfaces, export fixtures + a restore script, ~45–60 tests.

---

### Episode 6 — `feat/migration-flows-v1`: migration flows and statistics

**Status.** Not implemented (the next episode up). The migration number in the sketch below (051, then 056) has gone stale twice: 051 was taken by Episode 7 (`community_threads`), 052–055 by the hardening audit episodes, and 056 by the seed for the frontend flag `web_dossier_v2` (see [../architecture/overview.md](../architecture/overview.md) §7.5). When Episode 6 starts, it takes **the next free number — 057**.

**Goal.** An aggregated picture of migration directions — "who's moving where" — with hard anonymization (k=20); confidence tiers for undocumented plans; a "relocation journal"; displacing synthetic data.

**Data model (migration 057).**

```sql
CREATE TABLE migration_flow_aggregates (      -- materialized by a job
    id UUID PK,
    origin_country_id UUID NOT NULL REFERENCES countries(id),
    destination_country_id UUID NOT NULL REFERENCES countries(id),
    period TEXT NOT NULL,                     -- '2026-Q3'
    trip_count INT NOT NULL,                  -- a row is never written if < k
    weighted_count NUMERIC NOT NULL,          -- weighted by confidence
    computed_at TIMESTAMPTZ, methodology_version TEXT,
    CONSTRAINT uq_flow UNIQUE (origin_country_id, destination_country_id, period)
);
```

**Confidence tiers** (`trips.confidence_tier`, no documents involved — an invariant): `declared` (created) → `active` (a heuristic: ≥X completed steps + account age; Episode 1 parameters) → `confirmed` (the user marked "I relocated").

**The "relocation journal."** Marking "I relocated" turns a plan into a draft structured user story in one action (route, timeline, steps pre-filled) → the standard story moderation. The loop: a plan → a relocation → a story → data for the next person. As real stories grow, a **synthetic-data displacement policy** applies (an owner decision): synthetic stories are pulled from public surfaces as their scenarios/countries get covered by real ones (marking and dq control already exist).

**Service and script.** `services/migration_flows.py` (a pure aggregator: active/confirmed trips + published board posts → pairs × quarters; groups under k are dropped; weighted by tier) + `scripts/recompute_migration_flows.py` (idempotent, dry-run, a summary).

**API.** `GET /migration-flows?origin=&destination=&period=`; `GET /me/trips/{id}/flow-context` — "in your direction this quarter: ≥N plans" + a link to the board's fellow-traveler section.

**Privacy invariants (tests are mandatory).** No API parameter combination ever returns a group smaller than 20 (the value is the `flows.k_anonymity` parameter); only country→country × quarter — no cities, no dates, no IDs; the recompute job never logs group membership.

**Acceptance.** Aggregates match the seed; a group of k−1 is invisible; tiers advance per the rules; the "journal" creates a story draft from a completed plan. **Not doing:** lists of who's going where; realtime counters; storing documents (ever).

**Scope.** 1 migration, 1 service + a script, ~25–35 tests.

---

### Episode 7 — `feat/community-threads-v1`: contact threads

**Goal.** Lightweight messaging strictly between mutually consenting parties (an accepted contact request) + a Telegram deep link. Not a messenger.

**Data model (migration 052).**

```sql
CREATE TABLE contact_threads (
    id UUID PK,
    contact_request_id UUID NOT NULL UNIQUE REFERENCES migration_board_contact_requests(id),
    status TEXT NOT NULL DEFAULT 'open',      -- open|closed_by_a|closed_by_b|frozen
    created_at TIMESTAMPTZ
);
CREATE TABLE thread_messages (
    id UUID PK, thread_id UUID NOT NULL REFERENCES contact_threads(id) ON DELETE CASCADE,
    sender_user_id UUID NOT NULL REFERENCES users(id),
    body TEXT NOT NULL,
    created_at TIMESTAMPTZ
);
```

**Rules.** A thread exists only on an `accepted` contact; a message-per-day limit (a parameter); either side can close it; a block freezes it; a thread report reuses the contact-report flow → a moderator sees the conversation **only via the report**, and it's audited (a privacy policy + an access audit). Delivery is polling (`GET …/messages?after=`), no WebSocket in v1. The deep link: once Telegram is mutually linked, contact exchange happens via explicit two-step mutual consent.

**Acceptance.** Messaging only works within an accepted contact; closing/blocking/reporting all work; limits are enforced; moderator access to a conversation leaves an audit trail. **Not doing:** attachments, group chats, realtime, message search.

**Scope.** 1 migration, an extension of the migration_board package, ~20–30 tests.

**Status.** Implemented and on `main` (migration `051_community_threads_v1.sql`).
Deviations from the sketch above, recorded as deliberate decisions:
the migration number is **051, not 052** (Episode 6 hadn't been implemented yet
by this point, and 051 turned out to be free; the following migrations took
052–056 (hardening audit + the `web_dossier_v2` frontend flag), so Episode 6
takes **057** when it starts (see its status above) — no need to renumber 051);
thread statuses were simplified to `open|closed|frozen` instead of
`open|closed_by_a|closed_by_b|frozen` (who closed it is a separate
`closed_by_user_id` + `closed_at` column); the Telegram deep link for
exchanging contacts was dropped from v1 (there was no explicit requirement for
it, outside the minimal acceptance criteria).
Key modules: `database/migrations/051_community_threads_v1.sql`;
`repositories/migration_board/threads.py`; `services/migration_board/threads.py`
(list/send/close/report-gated moderator access with an audit trail); hooks in
`services/migration_board/contacts.py` (auto-creating a thread in
`accept_contact_request`, freezing it in `block_user`); the endpoints
`GET /me/threads`, `GET|POST /me/threads/{id}/messages`,
`POST /me/threads/{id}/close`, `GET /admin/migration-board/threads/{id}/messages?report_id=`;
DQ checks for a thread open with no accepted contact and messages sent
after closing/blocking. 38 new tests, the full `pytest tests/` suite green.

---

### The visual tranche (a separate line after the backend episodes)

The minimum starting condition (episodes 1–2 closed) is met; the tranche is
**partially complete** — the design system and the product reskin onto it are
done (see below), the map/infographics/naming revision remain open.

**Done.** (1) An isolated visual prototype, `apps/web-prototype`
(Vite + React + Tailwind v4) — a showcase for the "warm intelligence archive"
design system with "breathing" canvas charts and a component library —
served as the style/element donor; the material was fully ported into
`packages/ui` in redesign waves, after which the prototype was removed. (2) The
`packages/ui` design system and the full migration of the product's
`apps/web` onto it, 14 stages (reskinning every product section + the internal
`/internal/**` admin surface + polish/bundle/accessibility) — detail and scope
in [../architecture/overview.md](../architecture/overview.md) §7.5. The
original step-by-step port plan (`FRONTEND_IMPLEMENTATION_PLAN.md`) was
removed from the documentation once the port finished, the same as other
one-off execution plans (their history lives in git). (3) **Locale-in-URL is
implemented** (decision D-8, closed): `localePrefix: "always"` in
`apps/web/src/i18n/routing.ts`, a `/en|ru|es/...` path segment for every public
page; this also drove the full three-language interface migration
(overview.md §7.5/§7.6) — not a separate owner decision, but a natural
consequence of finalizing locale-in-URL.

**Still open** (not started): the planner map (Leaflet + OpenStreetMap);
flow and drift infographics (the underlying data has been computed since
Episode 6, but there's no showcase for it); a metric naming revision
(LVI/SSRS/CII → evocative names, decision D-7); progressive disclosure of
complexity as a distinct UX practice (not evaluated in depth).

**Render strategy (audit finding P2-12, recorded by hardening audit episode
9 — `fix/frontend-resilience-v1`).** Current state: all 22 pages under
`apps/web/src/app/**/page.tsx` are `force-dynamic` + `cache: "no-store"` on
every fetch (`shared/api/http.ts`); the country page mounts ~10 independent
client blocks (`CountryDriftBlock`, `TrustSurfaceBlock`,
`PlatformIntelligenceBlock`, `CountryRoutesBlock`, `CountryDataJournalBlock`,
`CommunityCountryBlock`, `CountryWhatChanged`, `CountryMigrationBoardBlock`,
and others), each with its own request — an HTTP "N+1." The tranche's concrete
technical steps: (1) rarely changing public pages (methodology, the glossary,
the country list) move to `export const revalidate = N` (ISR) instead of
`force-dynamic`; (2) the country page gets a single aggregate server fetch
(the backend can already serve a `country_read_model` aggregate, or a
`Promise.all` across 2–3 endpoints) passing data into the blocks as props —
client requests remain only for genuinely interactive blocks (watchlist,
community actions); (3) ISR invalidation on publish events, through the
existing `apps/api/app/services/cache_invalidation.py` hooks (add a
`revalidateTag` call on publish transitions, or a short TTL), symmetric with
the already-working Redis cache invalidation. P2-11 (fetch timeouts) is closed
separately, in code, in the same episode, before this tranche starts.

### The integration tranche (after the owner's relocation, targeted ~3–4 months from 2026-07)

Every real external connection is collected into a separate line (decision
D-10); until then, all development is offline through fake seams that already
exist or are being laid down episode by episode. Scope: Telegram real mode
(the seam is ready: `TELEGRAM_MODE`, the notifier's channel abstraction); a
real LLM provider (the seam is ready: `ai_providers.py`); a payment provider
for the Uruguay jurisdiction (candidates: dLocal, Mercado Pago, PayPal — the
seam gets built when monetization starts, not before); an email channel (a
backlog item, decision D-6); OAuth integrations (Google Calendar/Maps — after
the ICS/GeoJSON export); production hosting (open question Q-2). The tranche's
principle: every connection is configuration and keys, not development; if a
connection needs new logic written for it, the seam was designed wrong, and
that's a defect in the corresponding episode.

---

## 3. Cross-cutting engineering themes

### 3.1 Privacy as a program

- **Private-first**: everything personal is created private; publishing is an explicit action with a preview of the public projection.
- **Never stored** (invariants): travel documents/bookings/scans; raw share tokens (hash+prefix only); IP/user-agent in analytics.
- **k-anonymity** on every people-level aggregate (k=20, a parameter).
- **User rights**: exporting all of one's own data (JSON) and cascading account deletion — implemented in Episode 2 (once the first "heavy" personal data appears), not deferred.
- Interaction-log and analytics retention — a methodology parameter.

### 3.2 Performance and the compute stack

Rule: **Postgres until the trigger fires.** Every calculation sits behind a pure functional seam (examples: the CII aggregator, trust, drift). The trigger for reconsidering: an aggregate query stably takes >1s under real load, or a batch doesn't fit its window → a targeted replacement of one module (a NumPy job/a Rust binary behind a CLI), the contract doesn't change. PyTorch is off the table (there's no ML work by architectural stance).

### 3.3 New-domain checklist

1. A `feat/<slug>-v1` branch; the next migration number + a header comment.
2. A service package following house style (`helpers.py`, qualified access, re-exported via `__init__.py`).
3. A feature flag (off) + `ensure_feature_enabled` on every surface; rights via `require_roles`/`require_capability`.
4. Events only through the outbox (`event_key` idempotency).
5. A dq module (`_append_<domain>_checks`) wired into the report.
6. Tests: unit, API (a mock repo), a schema migration test, privacy/rights invariants.
7. A full quality gate before merge; push to main per the standard.

### 3.4 Observability

Every new domain emits analytics events following the existing pattern (hashed sessions, safe metadata): created/updated/shared for plans; published/subscribed/forked for metrics; proposal events for countries; reminder_sent from the relay's metrics. Recompute counters land in the recompute scripts' summaries.

### 3.5 Main risks

| Risk | Mitigation |
|---|---|
| UGC moderation load falling on one person | The autonomy pyramid (levels 0–1 ahead of humans); invite-only authors/contributors; premoderation until the moderator institution matures; parameterized limits |
| A cold start for the creative surface with no "author #1" | Platform methodologies as a showcase; templates from existing checklists; invite-only early authors |
| Trust erosion from author content | A hard "platform vs. author" separation; a mandatory methodology; core invariant tests |
| Gaming the flow statistics | Confidence tiers + k=20 + weighting; analytics anomaly detection |
| Legal risk from UGC advice | A "not legal advice" stance on every author/user surface |
| Solo-project scope creep | Episode discipline; rejected directions locked in vision.md §5; changes only by an explicit revisit |
| Growing outbox traffic (reminders) | Relay batching; a dedicated event_type; a separate topic if needed, via configuration |
