# Architecture Invariants Registry

> Decisions that must never be violated by any future task. Breaking any entry here blocks a merge regardless of a green quality gate. The registry itself may only be changed by a dedicated documentation task on the owner's decision.

## 1. Core and data

1. **PostgreSQL is the single source of truth.** Go/Kafka/Mongo carry only asynchronous delivery and rebuildable derived state.
2. **Core math is immutable**: the CII formula, scenario weights, and the decision-engine scoring are never edited. Everything new is a layer on top (Persona, Drift, Trust, weight profiles, author layers).
3. **Derived metrics** (LVI, SSRS, Contradiction, Trust, reputations) are computed from their own data and **never mixed** into the aggregated CII.
4. **Platform methodology changes only via a new version** (`methodology_parameters.version`, `formula_version`): no silent value edits; every scored output and passport carries its version.
5. **Source-backed everything**: a public claim with no source/attribution is never published; data-quality gates are never weakened or bypassed with fake data.
6. **Content lifecycle**: `draft → review → published → archived` (+ `rejected`); every transition carries an audit event.
7. **Migrations**: sequential, idempotent, sqlfluff-clean; applied files are never renamed or edited (checksum-tracked via `schema_migrations`). Content seeds (including RU translations and demo data) baked into early migrations 002-025 are an accepted architectural constraint: any later structural schema change must stay compatible with those already-committed INSERTs; new countries and content flow through the product pipeline (Episode 5), not through new seed migrations (audit finding P3-10).
8. **The demo country set is never deleted** (decision D-1): after conservation (Episode 5) the demo data is hidden from public surfaces but kept in fixtures and idempotently restorable via a dev tool.

## 2. Asynchronous surface

9. **Outbox discipline**: events flow only through `domain_events`; `event_key` guarantees idempotency; the publish event fires on the transition to `published`; seed/historical data is `notifiable = FALSE` (no notification storm).
10. **Notifier**: a channel abstraction plus a DLQ; Mongo is eventually-consistent derived state, rebuildable from the Kafka log.

## 3. External systems

11. **Provider seams, fake-by-default**: the AI provider, Telegram, and the future payment provider are all wired through an abstraction with a fake implementation by default; switching is a setting (`*_MODE=fake|real`), never a code rewrite.
12. **AI is a tool on a leash**: it answers only from published content with citations; with no context, it refuses; AI-authored content reaches users only after human review; AI never ranks human answers.
13. **Autonomous development mode** (decision D-10, in effect until the integration tranche): no external service is switched to real mode; every episode must be fully implementable and testable offline. If a real connection would require writing new logic, the seam was designed wrong — that's a defect in the episode, not a reason to skip the seam.

## 4. Rights, privacy, security

14. **Deny by default; authorization checks live only on the server**; every privileged action lands in audit_events with a reason.
15. **Flags ≠ rights**: feature flags control functionality rollout, grants/roles control user admission.
16. **Reputation is not a right**: derived reputation informs but never auto-grants a capability; granting one is always an explicit governance action.
17. **Never stored**: travel documents, bookings, document scans; raw share tokens (hash+prefix only); IP/user-agent in analytics.
18. **Private-first**: personal objects are created private; publishing is an explicit action; public projections pass a PII filter.
19. **k-anonymity for people-level aggregates**: groups smaller than the threshold (parameter `flows.k_anonymity`, starting value 20) are never exposed through any API parameter combination.
20. **Moderator access to private data** — only in the context of a filed report and only to its subject matter; every such access is audited.
21. **"Not legal advice"** plus a last-reviewed date appear on all public, author-generated, and delivered content.

## 5. Author and user-generated content

22. **Layer separation**: author metrics/methodologies are never blended with platform ones into a single number — only shown side by side, with explicit "author, version, updated" attribution.
23. **A methodology is mandatory**: an author metric with no "how it's computed" description is never published; every value carries a source OR an explicit "author's personal experience" mark.
24. **A fork carries lineage** (`forked_from`); contribution attribution is preserved.
25. **Country contribution** happens only through the onboarding gate (an automated readiness standard) and an editor curator; publishing a country with no curator is impossible.
26. **Synthetic content** is always marked and gets displaced by real content as coverage grows.
27. **Contribution licenses** (decision D-4): country data carries a non-exclusive, perpetual license to the platform; author methodologies get the author's choice at publish time (platform license | CC BY-SA), stored with the metric definition.

## 6. Monetization (safeguards ahead of implementation)

28. **Money never buys** rights, reputation, ranking position, or passing moderation.
29. Payment integration happens only through the provider seam (item 11) and only in the integration tranche; payment data is never stored on the platform. Operating jurisdiction is Uruguay (decision D-3).

## 7. Stack

30. **The core is FastAPI + PostgreSQL**; "Postgres until the trigger fires": heavy computation moves out of Python only on a proven bottleneck, replacing one isolated module behind a seam.
