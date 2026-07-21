# Current System State

> A technical snapshot of the implemented system, grounded in code facts (41 routers, 136 service modules/packages, 100 repositories, 56 migrations, 188 backend test files / 2306 tests; frontend — 45 `apps/web` pages, 94 unit tests (Vitest, web+ui), 44 E2E specs (Playwright), 5 visual-regression baselines; Go notifier — 16 packages, 16 test files; plus an autonomous synthetic-data pipeline with ~300 tests of its own). Everything described here exists, works, and is covered by tests.
>
> The baseline for the current development line was fixed on **2026-07-04**; this document was last refreshed on **2026-07-21**. Since the baseline, episodes 1–5 and 7 shipped, along with the hardening audit episodes, the synthetic-data pipeline, a full `apps/web` redesign onto the `packages/ui` design system (14 stages), a three-language interface migration (en/ru/es), frontend testing infrastructure (Vitest, MSW, visual regression), and a 10-layer whole-project audit with all findings resolved — summarized in §7. Episode 6 (migration flows and statistics) has not been implemented yet.

---

## 1. Overall architecture

```
                    ┌─────────────────────────────────────────────────┐
                    │                CLIENTS                          │
                    │   Next.js 15 (apps/web)      Telegram bot       │
                    └───────────┬─────────────────────────▲───────────┘
                                │ REST /api/v1 (OpenAPI)  │ notifications
                    ┌───────────▼─────────────────────────┼───────────┐
                    │   FastAPI (apps/api) — modular monolith         │
                    │   routers → services → repositories             │
                    │   Redis cache (mode: null|redis)                │
                    └───────┬──────────────────────┬──────────────────┘
                            │ SQL (psycopg)        │ INSERT domain_events
                    ┌───────▼───────┐      ┌───────▼────────┐
                    │  PostgreSQL   │      │ outbox:        │
                    │  source of    │      │ domain_events  │
                    │  truth        │      └───────┬────────┘
                    └───────────────┘              │ scripts/outbox_relay.py
                                                   ▼ (batched, idempotent by
                                            ┌────────────┐  event_key, NOTIFY_AFTER
                                            │ Kafka      │  cutoff, fake|kafka)
                                            │ (Redpanda) │
                                            └─────┬──────┘
                                                  ▼
                    ┌─────────────────────────────────────────────────┐
                    │  Go notifier (apps/notifier)                    │
                    │  Kafka consumer → channels (abstraction) →      │
                    │  Telegram; Mongo — derived state (delivery log),│
                    │  DLQ, metrics, health,                          │
                    │  gRPC subscriptions server (Telegram↔web link)  │
                    └─────────────────────────────────────────────────┘
```

`docker-compose`: postgres, redis, api, redpanda, mongo, notifier.

A detailed breakdown of layers, application boundaries, and who is allowed to
call whom lives in [layers-and-boundaries.md](layers-and-boundaries.md). API
conventions (versioning, error format, authentication) are in
[../api/overview.md](../api/overview.md).

## 2. Code layers and conventions

| Layer | Where | Rule |
|---|---|---|
| Routers | `apps/api/app/api/v1/*.py` | Thin: parsing, dependencies (auth/RBAC/connection), one service call |
| Services | `apps/api/app/services/` | All business logic; large domains become packages (`migration_board/`, `decision_engine/`, `data_quality/`) that re-export their public surface via `__init__.py` |
| Repositories | `apps/api/app/repositories/` | SQL only (enforced by the "repository is SQL-only" tests) |
| Schemas | `apps/api/app/schemas/` | Pydantic v2; OpenAPI contract → generated TS types (`pnpm contracts:generate`) |
| Core | `apps/api/app/core/` | Settings; database helpers; `api_error` → the single error envelope `{detail:{error:{code,message,details}}}`; CurrentUser; require_roles |

Conventions (full detail in the root `CLAUDE.md`):

- **Localization is an overlay applied on read**: `overlay_localized_fields(...)` layers translations on top of the read model's strings; the client gets a `source|translated|fallback|missing` status per field. Legacy `*_ru/*_en` columns are kept in place.
- **Package decomposition**: files over 800 lines are split into a package; cross-cutting private helpers live in one `helpers.py`, accessed via qualified module access — otherwise `monkeypatch` in tests silently stops intercepting calls.
- **Feature flags**: `ensure_feature_enabled(connection, key, message)` → 403 `feature_disabled`; statuses enabled/disabled/internal/deprecated, access tiers public/beta/internal/admin, tier-scoped rules.
- **Tests**: MagicMock connection, monkeypatch on the repository module, `_assert_error` for error codes; migration tests read raw SQL; every test file carries a one-line docstring stating what it checks.

## 3. Domain map

### 3.1 Content core (reference data, publication lifecycle, audit)

| Domain | Key tables | API | Notes |
|---|---|---|---|
| Countries and cards | countries, country_profiles, country_cards | `/countries`, `/countries/{slug}`, `…/card` | **Demo set: RU/UY/AR** (`countries.is_demo`, Episode 5) — preserved (`is_active=TRUE`) but hidden from every public surface; fixtures + an idempotent restore script; RU/EN; draft→review→published lifecycle |
| Sources and evidence | sources, evidence_items | `/sources`, `…/evidence` | Type/language/confidence; only `published` is exposed |
| Legal signals | legal_signals, legal_signal_events | `/legal-signals`, timeline | legal_status, impact direction/level, year-by-year timeline |
| Routes | routes (+documents/sources/evidence), route_checklist_items | `/routes/*` | Checklist step: documents, cost, timeline, official requirements — each with sources |
| Country pairs | country_pair_compatibility (+sources/evidence) | `/country-pairs/*` | origin→destination: visas/taxes/banking/flights/language/restrictions |
| Reference | glossary, methodology_sections, data journal | `/glossary`, `/methodology`, `/data-journal` | |

### 3.2 Decisions

| Capability | Mechanics |
|---|---|
| `/decision/run` | 5 scenarios × 7 criteria; stored breakdowns; ranking `(-score, -confidence, slug)`; strengths ≥70 / weaknesses ≤50; risk warnings; everything carries source_ids |
| Custom weights | per-request; completeness/range/sum validation; recomputed at request time, not persisted |
| Persona | Layer: metric modifiers (−0.5…+0.5) → adjusted weights (sum = 1) → persona-adjusted ranking |
| Origin-aware | pair context in results when an origin country is supplied |
| Comparison | winner/tie: delta <3 — tie/low, <10 — medium, else high |
| Passports | Snapshot of the request and result; a public token (hash+prefix in the DB), TTL, 410 once expired |
| Wizard | Goal → scenario; sliders → weights |

### 3.3 Computed layers (derived, versioned)

| Layer | Storage | Recompute |
|---|---|---|
| CII | cii_metric_definitions (polarity, source, active), country_metric_values, scenario_metric_weights (**versioned**), country_cii_scores (formula_version, geometric) | seed + admin recompute |
| Platform metrics (LVI, SSRS, Contradiction) | country_platform_metrics (methodology_version) | script, idempotent, dry-run |
| Trust Score | country_trust_scores (label, confidence, components, expires_at) | script; from counts/freshness/contradiction |
| Drift | country_drift_snapshots (period, label, confidence) | from legal_signal_events; downgraded when data is sparse |

### 3.4 Platform and user

- **Auth/RBAC**: PBKDF2-SHA256 (260k iterations); session — httpOnly+Secure(prod)+SameSite=Lax cookie with CSRF double-submit (plus an `Authorization` header as an alternate path for API clients); the session token rotates every `auth_session_rotation_interval_minutes` with a grace period on the previous one; session/device visibility (`GET /auth/sessions` with a device label and masked IP) and new-device sign-in notifications (`GET/POST /auth/security-notifications`); `revoke-all` requires step-up re-authentication with the password; roles user/editor/moderator/owner; promotion to owner is owner-only; registration is behind a flag; Telegram linking goes through gRPC to the notifier.
- **Watchlists** (flagged), **What changed** (window/`since` per country), **Search** (search_documents + GIN, upsert/remove in the same transaction on publish transitions plus a separate full rebuild script, locales kept separate), **Analytics** (session hashing, metadata sanitization, forbidden keys), **Feature flags API**, **Cache** (Redis backend — a per-process singleton).
- **Retention**: `scripts/cleanup_retention.py` (idempotent, dry-run) deletes `analytics_events`/`ai_interaction_logs` older than `retention.analytics_days`, `domain_events(status='relayed')` older than `retention.domain_events_days`, and `auth_sessions` (expired/revoked) older than `retention.sessions_days` — the windows are methodology parameters, not hardcoded.

### 3.5 Community

- **Q&A**: pending→published (moderated); consensus computed by a transparent formula (weighting + a source-backed bonus + a "contested" detector based on spread).
- **User stories**: structured, with a verification status, synthetic marking; ratings across 6 axes; data-error reports.
- **Migration board**: posts with a lifecycle and moderation (approve/reject/hide), public/members_only/private visibility, a PII detector on public text (email/phone/@handle/URL), mutual-consent contact requests (20/day limit), blocks, reports (20/day, deduplicated), companion matching with match reasons, a public projection with no PII.
- **Contact threads** (Episode 7, an extension of the board): a 1:1 conversation is auto-created when a contact request is accepted, statuses `open|closed|frozen`, delivery by polling, a message-per-day limit (parameter `board.max_thread_messages_per_day`), closable by either side, frozen when the counterpart is blocked, a thread report reuses the contact request's report; moderator access to the conversation is gated strictly to `report_id` matching the thread's contact request, plus a conflict-of-interest check and an audit entry on every access (not just the first); the PII filter does not apply to message bodies (a private channel, not a public projection).
- **Author metrics** (grant `author.metrics`, behind the `author_metrics_enabled` flag): metric definitions with a draft→review→published→archived(+rejected) lifecycle, premoderated through the `moderator.metrics` scope (publication requires a methodology description above a minimum length and coverage of at least N countries), per-country values (a source OR an explicit "personal experience" mark, scale validation), forks with lineage (`forked_from_id`), subscriptions to a metric/author plus a feed, derived reputation (coverage/freshness/sourcing, recomputed by script). The author layer is a read-only overlay on dedicated endpoints (`/countries/{slug}/author-metrics`, `/authors/{user_id}/metrics`) — the platform's CII/decision/compare code never imports or reads `services/author_metrics`.
- **Country contribution** (grant `contributor.countries`, behind the `country_contribution_enabled` flag, Episode 5): proposing a country (`country_proposals`, draft→review→published→archived(+rejected) lifecycle) creates a hidden (`is_active=FALSE`) `countries` row; the contributor fills in the card/sources/evidence/legal signals/timeline/CII values through ownership-gated `/me/country-proposals/{id}/...` endpoints (wrappers over the existing editorial services, status always `draft`); an editor curator is assigned (`curator_user_id`), runs the onboarding gate (`evaluate_country_onboarding`, reused as the contribution gate), enters the scenario scores themselves (`country_scores`/`country_score_breakdowns`, 7 weighted criteria with sources), and publishes — publication without a curator or with a failing gate is impossible (an invariant). Contributor attribution is preserved publicly.

### 3.6 AI surface (a tool, not a source of truth)

Provider seam (fake-by-default); context is limited to published content and stored metrics; `/ai/ask` (cited, refuses without context), `/ai/explain-number`, `/ai/decision-intent`; drafts go to needs_review; contradiction candidates go to review; interaction logs have restricted metadata.

### 3.7 Editorial and operations

Admin CRUD with a lifecycle and audit_events; **data quality** — a valid/invalid report, 60+ checks batched by domain; translation jobs plus a worker foundation; outbox relay (batching, max attempts, metrics); rate limits.

## 4. Operational surface

- **Migrations**: `database/migrations/NNN_name.sql`; `schema_migrations(version=filename, checksum)` — applied files are immutable.
- **Quality gate**: `python dev_tools_scripts_runner.py [--profile …] [--doctor] [--fix]` → `scripts/dev_tools/full_check.py`: environment diagnostics, toolchain, dependencies, static checks (ruff/mypy/sqlfluff), pytest, Go vet/test, the Docker stack + migrations + runtime smokes + E2E, pre-commit; reports land in `full-check-reports/`.
- **CI**: `.github/workflows/quality.yml`.
- **Recurring jobs** (currently run manually / via `dev_tools_scripts_runner.py`, not yet wired to cron/systemd/CronJob — the deployment target hasn't been chosen yet):
  - `scripts/outbox_relay.py` — `domain_events` → Kafka, idempotent by `event_key`, batched.
  - `scripts/dispatch_trip_reminders.py` (alias `dispatch-trip-reminders` in the orchestrator) — moves due `trip_reminders` into `domain_events` (`event_type=trip_reminder_due`), transactionally, `SKIP LOCKED`, idempotent. Run manually until a real deployment exists; schedule it on a recurring cadence in production.
  - `apps/worker` (`python apps/worker/main.py translation-jobs [--target-locale …] [--limit …] [--worker-id …] [--dry-run]`) — processes a batch of pending `translation_jobs` (the same logic as `/admin/translation-jobs/process-batch` in the API). Not yet registered in `dev_tools_scripts_runner.py` or mentioned in CI — run manually, directly. Covered by tests (`tests/test_translation_jobs_worker.py`).

## 5. Hardcoded-value inventory (Episode 1 entry point, status after Episode 1 — done)

A snapshot at the start of Episode 1 versus the current (after-the-fact) state:

| Parameter | Before (Episode 1 entry) | Current state | Where now |
|---|---|---|---|
| Score-label thresholds | 30/50/70/85, hardcoded | **In the DB, versioned** (`methodology_parameters`) | `services/score_labels.py` takes `ScoreLabelThresholds` from `methodology_config.py` |
| Strengths/weaknesses | ≥70 / ≤50, hardcoded | **In the DB, versioned** | `decision_engine/decision_runner.py` via `get_active_methodology_config` |
| Confidence bounds | ≥2.5 high, ≥1.7 medium, hardcoded | **In the DB, versioned** | `decision_engine/helpers.py` via `get_active_methodology_config` |
| Compare deltas | <3 tie, <10 medium, hardcoded | **In the DB, versioned** | `decision_engine/decision_runner._recommend` via `methodology.decision` |
| Custom weights | per-request, not persisted | **Persistable user profiles** | `user_weight_profiles`, `services/weight_profiles.py` |
| Board limits | 5 posts; 20 contacts/day; 20 reports/day, hardcoded | **In the DB, versioned** | `migration_board/helpers.py` via `get_active_methodology_config` |
| k-anonymity threshold | — (no people-level aggregates yet) | A methodology parameter, k=20 (used from Episode 6 onward) | `methodology_parameters` |
| CII weights/metrics | v1.0 | In the DB, versioned (unchanged since the baseline) | Opened to authors — Episodes 3–4 |
| Persona modifiers | −0.5…0.5 | In the DB (unchanged since the baseline) | — |

## 6. Reusable building blocks for the new line

Existing mechanisms the plan relies on (reuse, not reinvention):

| Building block | Where implemented | Who needs it |
|---|---|---|
| Publication lifecycle + audit | admin/editorial surface | Author metrics, country contribution |
| Methodology versioning | scenario_metric_weights.version, formula_version | Episode 1 |
| User weight validation | decision_personalization | Weight profiles (Episode 1) |
| Sourced checklist steps | route_checklist_items | Trip planner (Episode 2) |
| Country-pair compatibility | country_pair_compatibility | Trip-planner warnings |
| Token sharing (hash+prefix) | decision_passports | Sharing plans |
| Telegram delivery | outbox → relay → Kafka → notifier | Trip-planner reminders |
| PII detection on public text | migration_board/helpers | Every new public text field |
| PII-free public projection | the board's `_public_post` | Shared plan projections |
| Derived reputation | trust_score (a reference calculation) | Author reputation |
| Country onboarding standard | the country_onboarding_standard test + dq checks | Country contribution (Episode 5) |
| Recompute scripts (idempotent, dry-run) | platform_metrics, trust, drift | Migration flows (Episode 6), reputation |

## 7. Changes since the baseline (2026-07-04 → 2026-07-12)

A summary of what landed on top of the baseline; §1–§6 above already describe the system with these changes folded in.

### 7.1 Product-line episodes

Implemented and on `main`: **Episode 1** (flexible methodology, migration 046), **2** (trip planner, 047), **3** (rights and roles v2, 048), **4** (author metrics, 049), **5** (country contribution + demo-set conservation, 050), **7** (contact threads, 051). **Episode 6** (migration flows and statistics) has not started — episode status is tracked in [../product/roadmap.md](../product/roadmap.md).

### 7.2 Hardening audit episodes

A separate code-audit line (security, resources, concurrency, database, observability, resilience, testing/CI) is closed; its plan and full report (`audit_result.txt`, `09_audit_remediation_plan.md`) were removed from the documentation once done. Schema-affecting changes landed as migrations **052–055**:

| Migration | What it added |
|---|---|
| 052 `session_security_hardening` | Session token rotation, device visibility, new-device sign-in notification (`auth_sessions`) |
| 053 `domain_events_in_flight` | An in-flight status on `domain_events`: the relay releases row locks before the blocking publish to Kafka |
| 054 `retention_config` | Retention windows as methodology parameters (analytics, `domain_events`, sessions) — not hardcoded |
| 055 `recompute_requested_event` | A `recompute_requested` event type for async admin recompute via the outbox |

Changes without migrations: fail-fast on default production secrets and the production `docker-compose` overlay, a configurable DB pool; observability — request-id tracing, JSON logs, a `/metrics` endpoint (request counters, latency, DB pool gauges); keyset pagination for deep public listings; idempotency on content-create endpoints; a single source of truth for PII patterns and lifecycle statuses; fetch timeouts in the `apps/web` API client; repository integration tests and `-race` for Go in CI.

### 7.3 The synthetic-data pipeline (`scripts/synthetic_data.py` + `utils/synthetic_data`)

An autonomous dev tool that generates a fully **fictional** world (countries, users, metrics, documents) for development and testing without a real database and without real countries. Deterministic by seed; 15 Unicode locales; profiles and archetypes; document rendering (PDF/DOCX/XLSX/TXT), SQL fixtures with dataset-isolated loading by `dataset_id`, an HTML dashboard, sha256 package sidecars, dataset diffing, a mock HTTP server that mimics `apps/api`'s endpoints. Entry point is the thin `scripts/synthetic_data.py` shim; the full implementation and input configs live under `utils/synthetic_data/` (moved from `scripts/synthetic_data`/`docs/synthetic_data`, see [../operations/synthetic-data-plan.md](../operations/synthetic-data-plan.md), Stage 0). Stage 1 added a Synthetic Web Environment (`utils/synthetic_data/web/`): a browsable, deterministic web of fictional sites (one site per country, source/article/notice pages, cross-site links, deliberately broken pages — 404/500/redirect/duplicate/empty/huge/broken-encoding), served by a local FastAPI server (`generate --formats web`, `render-web`, `serve` in the CLI). Full documentation lives in `utils/synthetic_data/README.md`. Its own test suite (341 tests) is wired into the quality gate as a separate pytest step. Switching product E2E/smoke tests onto this dataset is a separate, still-open task (Episode 8; see D-11 in [../decisions/open-questions.md](../decisions/open-questions.md)).

### 7.4 The dev-tools orchestrator

`dev_tools_scripts_runner.py` was reworked from a flat list into a categorized, two-level menu with bilingual (RU/EN) descriptions and a man-page-style built-in help; non-interactive invocation and `--help`/`help <script>` are both supported. It remains the main entry point for the quality gate and dev scripts.

### 7.5 The `apps/web` redesign onto the `packages/ui` design system

A full migration of the product frontend from its original markup onto a shared design system, "warm intelligence archive" (style donor: `apps/web-prototype`, ported over in redesign waves and then removed). Completed in 14 stages, including: reskinning every product section (home, catalog, country dossier, decision run, passports, comparison, legal signals, sources, methodology, glossary, trip planner, migration board, stories, community, watchlist, subscriptions, account, AI assistant — stage 11); the internal `/internal/**` surface as its own admin console (stage 12) with a reusable `ModerationQueue` primitive and eight moderation queues; stage 13, "polish and ship" — removing legacy CSS, an `ErrorBoundary` with client-error analytics, a bundle audit and size reduction (`@next/bundle-analyzer`, direct imports instead of barrel re-exports, `next/dynamic` for heavy blocks), an accessibility audit (WCAG token contrast, `prefers-reduced-motion`, aria markup on canvases/charts, keyboard navigation for composite rows). The country dossier got a tabbed layout behind the `web_dossier_v2` flag (migration 056, `disabled` by default, `internal` tier) — sections (Overview/Scores/Trust/Signals/Community) instead of one long vertical stack.

### 7.6 The three-language interface migration (en/ru/es)

The interface (not the backend's content data) moved from Russian-only to three locales — English (the new default, previously Russian), Russian, Spanish. 10 stages, end to end across every public-surface page (`apps/web/src/app/[locale]/**`); the `next-intl` message catalog grew from 90 to 1046 keys per locale, and parity between `en.json`/`ru.json`/`es.json` is enforced by `scripts/dev_tools/i18n_parity_check.py` (fails on any mismatch, wired into the quick gate). The backend's content data (country/scenario names, source text, legal-signal bodies, methodology) stays in its original language regardless of interface locale; for `es` it is requested from the backend with a fallback to `en` via `toApiLocale()` — the backend's `LocaleCode` contract is still only `en`\|`ru`; Spanish is not planned at the data layer. `/internal/**` (the admin console) is deliberately out of scope — it runs Russian-only through its own `NextIntlClientProvider` pinned to `locale="ru"` (recorded in [../decisions/open-questions.md](../decisions/open-questions.md), D-12). `apps/notifier`'s Telegram bot and event-notification templates are also localized to three languages — by the `language_code` from Telegram updates, independent of the web-interface migration.

### 7.7 Frontend testing infrastructure

Added from scratch (none of it existed in the repository before): **Vitest** for `apps/web` and `packages/ui` (94 tests — pure functions in `shared/lib/*`, `packages/ui/src/lib/*`, query-key logic in `entities/*/api.ts`); **MSW + `msw-storybook-addon`** in the `packages/ui` Storybook, with play functions for key components (`Dialog`, `Select`, `Tabs`, `ModerationQueue` — the last also doubles as a keyboard-accessibility regression test); **visual regression** — a separate `playwright.visual.config.ts`/`tests/visual/` with 5 baseline screenshots (home, catalog, country dossier, decision result, passport), run via `pnpm web:mvp:visual`, **deliberately not wired** into the main quality gate: screenshot pixel-diffing depends on OS/font rendering, the baseline was captured on Windows and would be falsely flaky on a Linux CI runner. Vitest is also not yet wired into `pnpm quality`/`web:mvp:check` — an open technical debt item, not a blocker (run manually: `pnpm --filter web test`/`pnpm --filter ui test`); it doesn't have its own entry in [../decisions/open-questions.md](../decisions/open-questions.md) since it doesn't need an owner decision — it's a purely technical gate improvement.

### 7.8 Whole-project audit (2026-07-20 — 2026-07-21)

A 10-layer audit (backend, frontend, notifier, database, worker + infrastructure, `packages/ui`, the OpenAPI contract, `scripts`/`utils`, tests, documentation drift), followed by fixing every finding. Key findings and fixes:

- **Frontend/SSR**: a hydration mismatch in the header (`NextIntlClientProvider` without an explicit `locale` — `<Link>` built links in the default locale); React error #418 on `/glossary`, `/sources`, `/legal-signals*` (a client-fetch view inside `<Suspense>` without a `<ClientOnly>` wrapper, reproducible in a production build); wide tables clipping on mobile (`DataTable` missing `overflow-x-auto`); un-cancelled `requestAnimationFrame` loops in `Counter`/`DonutChart`/`GaugeArc`; 14 form fields with no accessible name and 8 `FieldLabel`s missing `htmlFor` (a new `FieldGroupLabel` primitive was added for group headings); silent rollback of optimistic mutations with no user feedback; no localized 404 inside `[locale]` (needed a catch-all `[locale]/[...rest]/page.tsx` — a nested `not-found.tsx` is unreachable without an explicit `notFound()` call from within that segment's tree).
- **Infrastructure**: the `apps/notifier` container ran as root (fixed, non-root `USER app`, matching `apps/api`); dev-infrastructure ports (`postgres`, `redis`, `redpanda`×2, `mongo`, `notifier`×2) were published on `0.0.0.0` with no auth on `redis`/`mongo` — rebound to `127.0.0.1`; `api` was deliberately left untouched (it has real application-level authorization behind it).
- **Worker**: a fragile `sys.path` hack with a fixed `os.path.dirname` depth was replaced with a repo-root search by marker file (`pyproject.toml`).
- **Notifier**: the Telegram bot and notifications were localized (see §7.6).
- **Backend, database, the OpenAPI contract, `scripts`/`utils`** — checked in a full sweep across risk dimensions (authorization, SQL injection, transactions, migration idempotency, contract sync); no bugs found.

The full report (`AUDIT_2026-07-20.md`, per-finding status) was removed from the documentation once the task closed, the same as the earlier hardening-audit line (§7.2) — the history of decisions lives in git history and task final reports, not in a standalone file.
